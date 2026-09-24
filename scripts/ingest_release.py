#!/usr/bin/env python3
"""Verify a product's release candidate and promote a channel to it.

The source repository builds the candidate; this repository only accepts it
when every identity in it agrees (docs/DISTRIBUTION.md, "Ingest"). The checks
that need the network or a Mac (the source tag, attestations, notarization)
run in .github/workflows/ingest-release.yml, which hands their results here.

    ingest_release.py verify <candidate dir> --product ID --run RUN.json --tag-commit SHA
    ingest_release.py notes <candidate dir>
    ingest_release.py promote --product ID --channel stable|beta --manifest FILE --release-url URL
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = "release-manifest.json"
CHECKSUMS = "SHA256SUMS"
DOWNLOADS_START = "<!-- downloads:start -->"
DOWNLOADS_END = "<!-- downloads:end -->"


class Rejected(Exception):
    """A candidate that must not be published."""


def load_json(path: Path) -> dict:
    """Read a JSON object, rejecting any other top-level value."""
    with path.open(encoding="utf-8") as source:
        value = json.load(source)
    if not isinstance(value, dict):
        raise Rejected(f"{path.name} must be a JSON object")
    return value


def catalog_entry(product_id: str) -> dict:
    """Return the registered product, or reject an id the catalog does not list."""
    catalog = load_json(ROOT / "products/catalog.json")
    for product in catalog.get("products", []):
        if product.get("id") == product_id:
            return product
    raise Rejected(f"{product_id!r} is not a registered product")


def sha256(path: Path) -> str:
    """Hex SHA-256 of a file, read in blocks so installers need not fit in memory."""
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_schema(manifest: dict) -> None:
    """Reject a manifest that does not match schemas/release-manifest.schema.json."""
    import jsonschema

    schema = load_json(ROOT / "schemas/release-manifest.schema.json")
    validator = jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())
    errors = sorted(validator.iter_errors(manifest), key=lambda error: list(error.path))
    if errors:
        details = "; ".join(f"{'/'.join(map(str, e.path)) or '<root>'}: {e.message}" for e in errors[:5])
        raise Rejected(f"{MANIFEST} does not match the release-manifest schema: {details}")


def verify(candidate: Path, product_id: str, run: dict, tag_commit: str) -> dict:
    """Return the manifest when the candidate is publishable; raise Rejected otherwise."""
    product = catalog_entry(product_id)
    manifest = load_json(candidate / MANIFEST)
    validate_schema(manifest)

    source = manifest["source"]
    expected = {
        "product": product_id,
        "display_name": product["display_name"],
        "distribution_tag": f"{product['distribution_tag_prefix']}{manifest['version']}",
        "source repository": product["source_repository"],
    }
    actual = {
        "product": manifest["product"],
        "display_name": manifest["display_name"],
        "distribution_tag": manifest["distribution_tag"],
        "source repository": source["repository"],
    }
    for field, value in expected.items():
        if actual[field] != value:
            raise Rejected(f"{field} is {actual[field]!r}; the catalog requires {value!r}")

    prerelease = "-" in manifest["version"].split("+", 1)[0]
    if manifest["channel"] != ("beta" if prerelease else "stable"):
        raise Rejected(f"version {manifest['version']} cannot be a {manifest['channel']} release")
    if manifest["channel"] not in product.get("channels", []):
        raise Rejected(f"{product_id} has no {manifest['channel']} channel")

    if tag_commit != source["commit"]:
        raise Rejected(f"source tag {source['tag']} resolves to {tag_commit}, not {source['commit']}")

    # The build that produced these bytes, as GitHub reports it.
    repository = run.get("repository", {}).get("full_name")
    checks = {
        "run repository": (repository, source["repository"]),
        "run id": (str(run.get("id")), str(manifest["build"]["run_id"])),
        "run workflow": (run.get("path"), manifest["build"]["workflow"]),
        "run commit": (run.get("head_sha"), source["commit"]),
        "run branch": (run.get("head_branch"), "main"),
        "run conclusion": (run.get("conclusion"), "success"),
    }
    for field, (got, want) in checks.items():
        if got != want:
            raise Rejected(f"{field} is {got!r}, expected {want!r}")

    files = {path.name: path for path in candidate.iterdir() if path.is_file()}
    listed: dict[str, str] = {}
    for line in (candidate / CHECKSUMS).read_text(encoding="utf-8").splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  (\S.*)", line)
        if not match:
            raise Rejected(f"{CHECKSUMS} has a malformed line: {line!r}")
        listed[match.group(2)] = match.group(1)
    unlisted = sorted(set(files) - set(listed) - {MANIFEST, CHECKSUMS})
    if unlisted:
        raise Rejected(f"files outside {CHECKSUMS}: {unlisted}")
    for name, digest in listed.items():
        if name not in files:
            raise Rejected(f"{CHECKSUMS} lists {name}, which is missing")
        if sha256(files[name]) != digest:
            raise Rejected(f"{name} does not match {CHECKSUMS}")

    evidence = [manifest["checksums"], manifest["sbom"], manifest["provenance"], *manifest.get("attestations", [])]
    for item in [*manifest["artifacts"], *evidence]:
        name = item.get("name") or item.get("path")
        if name not in files:
            raise Rejected(f"{MANIFEST} references {name}, which is missing")
        if sha256(files[name]) != item["sha256"]:
            raise Rejected(f"{name} does not match its digest in {MANIFEST}")
        if "size" in item and files[name].stat().st_size != item["size"]:
            raise Rejected(f"{name} does not match its size in {MANIFEST}")

    sbom = load_json(files[manifest["sbom"]["path"]])
    if sbom.get("bomFormat") != "CycloneDX" or not isinstance(sbom.get("components"), list) or not sbom["components"]:
        raise Rejected(f"{manifest['sbom']['path']} is not a CycloneDX SBOM with components")

    installers = [item for item in manifest["artifacts"] if item["kind"] == "installer"]
    if not installers:
        raise Rejected("the candidate has no installer")
    for item in installers:
        if item["platform"] in {"macos", "windows"} and not item.get("native_signature"):
            raise Rejected(f"{item['name']} carries no native signing evidence")
    return manifest


def release_notes(candidate: Path) -> str:
    """Markdown release notes: installers with digests, source, build and evidence."""
    manifest = load_json(candidate / MANIFEST)
    source = manifest["source"]
    lines = [
        f"{manifest['display_name']} {manifest['version']}",
        "",
        "| Platform | File | SHA-256 |",
        "| --- | --- | --- |",
    ]
    for item in manifest["artifacts"]:
        label = {"arm64": "Apple silicon", "x64": "Intel"}.get(item["arch"], item["arch"])
        lines.append(f"| {item['platform']} ({label}) | `{item['name']}` | `{item['sha256']}` |")
    lines += [
        "",
        f"Source: [{source['repository']}@{source['tag']}](https://github.com/{source['repository']}/tree/{source['commit']}) "
        f"(`{source['commit']}`)",
        f"Build: [run {manifest['build']['run_id']}](https://github.com/{source['repository']}/actions/runs/{manifest['build']['run_id']})",
        "",
        f"Evidence: `{MANIFEST}`, `{CHECKSUMS}`, CycloneDX SBOM `{manifest['sbom']['path']}`, "
        f"provenance `{manifest['provenance']['path']}`. Verify an installer with:",
        "",
        "```",
        f"gh attestation verify <file> --repo {source['repository']}",
        "```",
    ]
    return "\n".join(lines) + "\n"


def promote(product_id: str, channel: str, manifest_path: Path, release_url: str) -> None:
    """Point a channel at a published release; stable also rewrites the product page downloads."""
    product = catalog_entry(product_id)
    manifest = load_json(manifest_path)
    if manifest.get("product") != product_id:
        raise Rejected(f"{manifest_path.name} is for {manifest.get('product')!r}, not {product_id!r}")
    if channel not in product.get("channels", []):
        raise Rejected(f"{product_id} has no {channel} channel")
    if channel == "stable" and manifest["channel"] != "stable":
        raise Rejected(f"a {manifest['channel']} release cannot be promoted to stable")

    tag = manifest["distribution_tag"]
    channel_path = ROOT / product[f"{channel}_channel"]
    pointer = {
        "schema_version": 1,
        "product": product_id,
        "channel": channel,
        "state": "promoted",
        "version": manifest["version"],
        "distribution_tag": tag,
        "release_url": release_url,
        "manifest_url": f"{release_url.replace('/releases/tag/', '/releases/download/')}/{MANIFEST}",
        "manifest_sha256": sha256(manifest_path),
        "promoted_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    channel_path.write_text(json.dumps(pointer, indent=2) + "\n", encoding="utf-8")

    if channel == "stable":
        page = ROOT / product["product_page"]
        text = page.read_text(encoding="utf-8")
        if DOWNLOADS_START not in text or DOWNLOADS_END not in text:
            raise Rejected(f"{page.relative_to(ROOT)} has no downloads markers")
        download = pointer["manifest_url"].rsplit("/", 1)[0]
        rows = [
            f"Current stable release: **{manifest['version']}** ([release notes and evidence]({release_url}))",
            "",
            "| Platform | Download |",
            "| --- | --- |",
        ]
        for item in manifest["artifacts"]:
            if item["kind"] != "installer":
                continue
            label = {"arm64": "Apple silicon (M1 and later)", "x64": "Intel"}.get(item["arch"], item["arch"])
            rows.append(f"| {item['platform'].replace('macos', 'macOS')}, {label} | [{item['name']}]({download}/{item['name']}) |")
        block = "\n".join([DOWNLOADS_START, *rows, DOWNLOADS_END])
        start = text.index(DOWNLOADS_START)
        end = text.index(DOWNLOADS_END) + len(DOWNLOADS_END)
        page.write_text(text[:start] + block + text[end:], encoding="utf-8")
    print(f"{product_id} {channel} -> {tag}")


def main() -> int:
    """Command-line entry point; a rejected candidate exits 1 with the reason."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    check = commands.add_parser("verify")
    check.add_argument("candidate", type=Path)
    check.add_argument("--product", required=True)
    check.add_argument("--run", type=Path, required=True)
    check.add_argument("--tag-commit", required=True)
    notes = commands.add_parser("notes")
    notes.add_argument("candidate", type=Path)
    move = commands.add_parser("promote")
    move.add_argument("--product", required=True)
    move.add_argument("--channel", choices=("stable", "beta"), required=True)
    move.add_argument("--manifest", type=Path, required=True)
    move.add_argument("--release-url", required=True)
    args = parser.parse_args()

    try:
        if args.command == "verify":
            manifest = verify(args.candidate, args.product, load_json(args.run), args.tag_commit)
            print(f"candidate accepted: {manifest['distribution_tag']} ({len(manifest['artifacts'])} artifacts)")
        elif args.command == "notes":
            sys.stdout.write(release_notes(args.candidate))
        else:
            promote(args.product, args.channel, args.manifest, args.release_url)
    except Rejected as rejection:
        print(f"rejected: {rejection}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

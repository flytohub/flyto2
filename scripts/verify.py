#!/usr/bin/env python3
"""Verify the Flyto2 distribution-hub contract."""

from __future__ import annotations

import gzip
import json
import re
import tarfile
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LOCAL_LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
REQUIRED_FILES = (
    "README.md",
    "SECURITY.md",
    "PROJECT.md",
    "ARCHITECTURE.md",
    "STATE.md",
    "DECISIONS.md",
    "docs/README.md",
    "docs/DISTRIBUTION.md",
    "docs/SUPPLY_CHAIN.md",
    "docs/LEGACY_ROUTING.md",
    "products/catalog.json",
    "products/README.md",
    "release-policy.json",
    "schemas/release-manifest.schema.json",
)
FORBIDDEN_PRODUCT_ROOTS = (
    "go.mod",
    "package.json",
    "pyproject.toml",
    "src",
    "src-tauri",
)
EXPECTED_PRODUCTS = {
    "flow": ("flytohub/flyto-flow", "flow/v"),
    "runtime": ("flytohub/flyto-runtime", "runtime/v"),
    "agent-firewall": ("flytohub/flyto-engine", "agent-firewall/v"),
}
PRODUCT_FILES = ("README.md", "product.json", "stable.json", "beta.json")
REQUIRED_EVIDENCE = {
    "release_manifest",
    "source_repository",
    "source_commit",
    "source_tag",
    "build_workflow",
    "build_run",
    "sha256_checksums",
    "cyclonedx_sbom",
    "provenance",
}


def load_json(path: str) -> dict:
    with (ROOT / path).open(encoding="utf-8") as source:
        value = json.load(source)
    if not isinstance(value, dict):
        raise RuntimeError(f"{path} must contain a JSON object")
    return value


def markdown_files() -> list[Path]:
    """Return maintained Markdown without caches or generated output."""
    skipped = {".flyto-index", ".git", "out"}
    return sorted(
        path
        for path in ROOT.rglob("*.md")
        if not any(part in skipped for part in path.parts)
    )


def verify_registry() -> None:
    catalog = load_json("products/catalog.json")
    products = catalog.get("products")
    if not isinstance(products, list):
        raise RuntimeError("products/catalog.json: products must be a list")

    seen_ids: set[str] = set()
    seen_prefixes: set[str] = set()
    resolved: dict[str, tuple[str, str]] = {}

    for product in products:
        if not isinstance(product, dict):
            raise RuntimeError("products/catalog.json: every product must be an object")
        product_id = product.get("id")
        source = product.get("source_repository")
        prefix = product.get("distribution_tag_prefix")
        channels = product.get("channels")
        product_page = product.get("product_page")
        stable_channel = product.get("stable_channel")
        beta_channel = product.get("beta_channel")
        if not all(
            isinstance(value, str) and value
            for value in (product_id, source, prefix, product_page, stable_channel, beta_channel)
        ):
            raise RuntimeError(
                "products/catalog.json: product id/source/prefix/page/channel paths must be non-empty strings"
            )
        if product_id in seen_ids:
            raise RuntimeError(f"duplicate product id: {product_id}")
        if prefix in seen_prefixes:
            raise RuntimeError(f"duplicate distribution tag prefix: {prefix}")
        if channels != ["stable", "beta"]:
            raise RuntimeError(f"{product_id}: channels must be ['stable', 'beta']")
        product_dir = ROOT / "products" / product_id
        missing_product_files = [
            name for name in PRODUCT_FILES if not (product_dir / name).is_file()
        ]
        if missing_product_files:
            raise RuntimeError(
                f"{product_id}: missing product distribution files: {missing_product_files}"
            )

        expected_paths = {
            "product_page": f"products/{product_id}/README.md",
            "stable_channel": f"products/{product_id}/stable.json",
            "beta_channel": f"products/{product_id}/beta.json",
        }
        actual_paths = {
            "product_page": product_page,
            "stable_channel": stable_channel,
            "beta_channel": beta_channel,
        }
        if actual_paths != expected_paths:
            raise RuntimeError(f"{product_id}: product page/channel paths mismatch: {actual_paths!r}")

        product_meta = load_json(f"products/{product_id}/product.json")
        if (
            product_meta.get("id") != product_id
            or product_meta.get("display_name") != product.get("display_name")
            or product_meta.get("source_repository") != source
            or product_meta.get("distribution_tag_prefix") != prefix
        ):
            raise RuntimeError(f"{product_id}: product.json does not match catalog identity")

        for channel in ("stable", "beta"):
            channel_data = load_json(f"products/{product_id}/{channel}.json")
            if channel_data.get("product") != product_id or channel_data.get("channel") != channel:
                raise RuntimeError(f"{product_id}: {channel}.json identity mismatch")
            if channel_data.get("state") not in {"legacy", "unpromoted", "promoted"}:
                raise RuntimeError(f"{product_id}: unsupported {channel} channel state")
            if channel_data.get("state") == "promoted":
                if not all(
                    isinstance(channel_data.get(name), str) and channel_data.get(name)
                    for name in ("version", "distribution_tag", "release_url")
                ):
                    raise RuntimeError(f"{product_id}: promoted {channel} channel is incomplete")

        seen_ids.add(product_id)
        seen_prefixes.add(prefix)
        resolved[product_id] = (source, prefix)

    if resolved != EXPECTED_PRODUCTS:
        raise RuntimeError(f"product registry mismatch: {resolved!r}")


def verify_release_policy() -> None:
    policy = load_json("release-policy.json")
    if policy.get("schema_version") != 1:
        raise RuntimeError("release-policy.json: unsupported schema_version")

    evidence = policy.get("required_evidence")
    if not isinstance(evidence, list) or not REQUIRED_EVIDENCE.issubset(set(evidence)):
        raise RuntimeError("release-policy.json: required release evidence is incomplete")

    signing = policy.get("signing")
    if not isinstance(signing, dict) or signing.get("artifact_attestation_required") is not True:
        raise RuntimeError("release-policy.json: artifact attestation must be required")

    storage = policy.get("storage")
    if not isinstance(storage, dict) or storage.get("commit_binary_installers_to_git") is not False:
        raise RuntimeError("release-policy.json: binary installers must stay out of Git history")


def verify_manifest_schema() -> None:
    schema = load_json("schemas/release-manifest.schema.json")
    required = set(schema.get("required", []))
    expected = {
        "schema_version",
        "product",
        "display_name",
        "version",
        "channel",
        "distribution_tag",
        "source",
        "build",
        "artifacts",
        "checksums",
        "sbom",
        "provenance",
    }
    if not expected.issubset(required):
        raise RuntimeError("release-manifest schema is missing required release identity/evidence fields")

    properties = schema.get("properties")
    if not isinstance(properties, dict):
        raise RuntimeError("release-manifest schema: properties must be an object")
    sbom = properties.get("sbom")
    provenance = properties.get("provenance")
    if not isinstance(sbom, dict) or not isinstance(provenance, dict):
        raise RuntimeError("release-manifest schema must define SBOM and provenance")


def verify_contract() -> None:
    """Reject missing distribution contracts, product source, and broken links."""
    missing = [path for path in REQUIRED_FILES if not (ROOT / path).is_file()]
    if missing:
        raise RuntimeError(f"missing required files: {missing}")

    product_roots = [path for path in FORBIDDEN_PRODUCT_ROOTS if (ROOT / path).exists()]
    if product_roots:
        raise RuntimeError(f"distribution hub contains product source/package roots: {product_roots}")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    security = (ROOT / "SECURITY.md").read_text(encoding="utf-8")
    required_readme = (
        "Flyto2 Distribution Hub",
        "Flyto2 Flow",
        "https://github.com/flytohub/flyto-flow",
        "https://github.com/flytohub/flyto-runtime",
        "https://github.com/flytohub/flyto-engine",
        "CycloneDX",
        "products/flow/README.md",
        "products/runtime/README.md",
        "products/agent-firewall/README.md",
        "https://flyto2.com",
    )
    absent = [value for value in required_readme if value not in readme]
    if absent:
        raise RuntimeError(f"README is missing distribution contract text: {absent}")
    if "security@flyto2.com" not in security:
        raise RuntimeError("SECURITY.md is missing the canonical contact")

    verify_registry()
    verify_release_policy()
    verify_manifest_schema()

    broken: list[str] = []
    links = 0
    for source in markdown_files():
        for raw in LOCAL_LINK.findall(source.read_text(encoding="utf-8")):
            target = raw.strip().split(maxsplit=1)[0].strip("<>")
            if target.startswith(("#", "http://", "https://", "mailto:")):
                continue
            relative = target.split("#", 1)[0]
            if not relative:
                continue
            links += 1
            if not (source.parent / relative).resolve().exists():
                broken.append(f"{source.relative_to(ROOT)}: {raw}")
    if broken:
        raise RuntimeError("broken local links:\n" + "\n".join(broken))

    print(
        "distribution contract passed: "
        f"{len(REQUIRED_FILES)} files, {len(EXPECTED_PRODUCTS)} products, {links} local links"
    )


def verify_bundle() -> None:
    """Build and reopen a deterministic distribution-contract bundle."""
    roots = [
        *ROOT.glob("*.md"),
        ROOT / "docs",
        ROOT / "products",
        ROOT / "schemas",
        ROOT / "workflows",
        ROOT / "handoffs",
        ROOT / "release-policy.json",
    ]
    files: list[Path] = []
    for entry in roots:
        files.extend(entry.rglob("*") if entry.is_dir() else [entry])
    files = sorted(path for path in files if path.is_file())

    with tempfile.TemporaryDirectory(prefix="flyto2-distribution-") as temp:
        archive = Path(temp) / "flyto2-distribution-contract.tar.gz"
        with archive.open("wb") as raw:
            with gzip.GzipFile(fileobj=raw, mode="wb", mtime=0) as compressed:
                with tarfile.open(fileobj=compressed, mode="w") as bundle:
                    for path in files:
                        info = bundle.gettarinfo(str(path), path.relative_to(ROOT).as_posix())
                        info.uid = info.gid = info.mtime = 0
                        info.uname = info.gname = ""
                        with path.open("rb") as source:
                            bundle.addfile(info, source)
        with tarfile.open(archive, "r:gz") as bundle:
            names = set(bundle.getnames())
        expected = {
            "README.md",
            "SECURITY.md",
            "products/catalog.json",
            "release-policy.json",
            "schemas/release-manifest.schema.json",
        }
        if not expected.issubset(names):
            raise RuntimeError(f"distribution contract bundle is incomplete: {sorted(expected - names)}")
    print(f"distribution contract bundle passed: {len(files)} files")


def verify_ingest() -> None:
    """Accept a well-formed candidate, refuse tampered ones, and promote a copy."""
    import importlib.util
    import shutil

    spec = importlib.util.spec_from_file_location("ingest_release", ROOT / "scripts/ingest_release.py")
    ingest = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ingest)

    commit = "a" * 40
    with tempfile.TemporaryDirectory(prefix="flyto2-ingest-") as temp:
        candidate = Path(temp) / "candidate"
        candidate.mkdir()
        files = {
            "Flyto2-Runtime-1.2.3-macos-arm64.dmg": b"arm64 installer",
            "Flyto2-Runtime-1.2.3-macos-x64.dmg": b"x64 installer",
            "flyto2-runtime-1.2.3.cdx.json": json.dumps(
                {"bomFormat": "CycloneDX", "specVersion": "1.6", "components": [{"type": "library", "name": "x"}]}
            ).encode(),
            "provenance.intoto.jsonl": b"{}\n",
        }
        for name, content in files.items():
            (candidate / name).write_bytes(content)
        digest = lambda name: ingest.sha256(candidate / name)
        (candidate / "SHA256SUMS").write_text("".join(f"{digest(n)}  {n}\n" for n in sorted(files)))
        manifest = {
            "schema_version": 1,
            "product": "runtime",
            "display_name": "Flyto2 Runtime",
            "version": "1.2.3",
            "channel": "stable",
            "distribution_tag": "runtime/v1.2.3",
            "source": {"repository": "flytohub/flyto-runtime", "commit": commit, "tag": "v1.2.3"},
            "build": {"workflow": ".github/workflows/macos-app.yml", "run_id": 42},
            "artifacts": [
                {"name": n, "platform": "macos", "arch": a, "kind": "installer", "sha256": digest(n),
                 "size": len(files[n]), "native_signature": "apple-developer-id-notarized"}
                for n, a in (("Flyto2-Runtime-1.2.3-macos-arm64.dmg", "arm64"), ("Flyto2-Runtime-1.2.3-macos-x64.dmg", "x64"))
            ],
            "checksums": {"path": "SHA256SUMS", "sha256": digest("SHA256SUMS")},
            "sbom": {"path": "flyto2-runtime-1.2.3.cdx.json", "sha256": digest("flyto2-runtime-1.2.3.cdx.json"), "format": "CycloneDX"},
            "provenance": {"path": "provenance.intoto.jsonl", "sha256": digest("provenance.intoto.jsonl"),
                           "type": "github-artifact-attestation"},
        }
        (candidate / "release-manifest.json").write_text(json.dumps(manifest))
        run = {"id": 42, "repository": {"full_name": "flytohub/flyto-runtime"}, "path": ".github/workflows/macos-app.yml",
               "head_sha": commit, "head_branch": "main", "conclusion": "success"}

        ingest.verify(candidate, "runtime", run, commit)
        refusals = {
            "tag on another commit": lambda: ingest.verify(candidate, "runtime", run, "b" * 40),
            "failed build": lambda: ingest.verify(candidate, "runtime", {**run, "conclusion": "failure"}, commit),
            "build from a branch": lambda: ingest.verify(candidate, "runtime", {**run, "head_branch": "dev"}, commit),
            "wrong product": lambda: ingest.verify(candidate, "flow", run, commit),
        }
        (candidate / "Flyto2-Runtime-1.2.3-macos-x64.dmg").write_bytes(b"swapped installer")
        refusals["swapped installer"] = lambda: ingest.verify(candidate, "runtime", run, commit)
        for label, attempt in refusals.items():
            try:
                attempt()
            except ingest.Rejected:
                continue
            raise RuntimeError(f"ingest accepted a candidate with a {label}")
        (candidate / "Flyto2-Runtime-1.2.3-macos-x64.dmg").write_bytes(files["Flyto2-Runtime-1.2.3-macos-x64.dmg"])

        copy = Path(temp) / "hub"
        shutil.copytree(ROOT / "products", copy / "products")
        ingest.ROOT = copy
        try:
            url = "https://github.com/flytohub/flyto2/releases/tag/runtime/v1.2.3"
            ingest.promote("runtime", "stable", candidate / "release-manifest.json", url)
            pointer = json.loads((copy / "products/runtime/stable.json").read_text())
            page = (copy / "products/runtime/README.md").read_text()
        finally:
            ingest.ROOT = ROOT
        if pointer.get("state") != "promoted" or pointer.get("distribution_tag") != "runtime/v1.2.3":
            raise RuntimeError(f"promotion wrote an unexpected channel pointer: {pointer!r}")
        if "releases/download/runtime/v1.2.3/Flyto2-Runtime-1.2.3-macos-arm64.dmg" not in page:
            raise RuntimeError("promotion did not link the installers from the product page")
    print(f"ingest contract passed: 1 accepted candidate, {len(refusals)} refused")


if __name__ == "__main__":
    verify_contract()
    verify_bundle()
    verify_ingest()

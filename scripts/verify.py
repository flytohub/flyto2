#!/usr/bin/env python3
"""Verify the deprecated Flyto2 routing and documentation-only contract."""

from __future__ import annotations

import gzip
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
    "docs/LEGACY_ROUTING.md",
)
FORBIDDEN_RUNTIME_ROOTS = (
    "go.mod",
    "package.json",
    "pyproject.toml",
    "src",
)


def markdown_files() -> list[Path]:
    """Return maintained Markdown without tool caches or generated output."""
    skipped = {".flyto-index", ".git", "out"}
    return sorted(
        path
        for path in ROOT.rglob("*.md")
        if not any(part in skipped for part in path.parts)
    )


def verify_contract() -> None:
    """Reject missing routes, accidental runtime authority, and broken links."""
    missing = [path for path in REQUIRED_FILES if not (ROOT / path).is_file()]
    if missing:
        raise RuntimeError(f"missing required files: {missing}")

    runtime = [path for path in FORBIDDEN_RUNTIME_ROOTS if (ROOT / path).exists()]
    if runtime:
        raise RuntimeError(f"legacy shell contains runtime surfaces: {runtime}")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    security = (ROOT / "SECURITY.md").read_text(encoding="utf-8")
    required_readme = (
        "Deprecated legacy distribution shell",
        "https://github.com/flytohub/flyto-core",
        "https://docs.flyto2.com",
    )
    absent = [value for value in required_readme if value not in readme]
    if absent:
        raise RuntimeError(f"README is missing legacy routes: {absent}")
    if "security@flyto2.com" not in security:
        raise RuntimeError("SECURITY.md is missing the canonical contact")

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
    print(f"legacy routing contract passed: {len(REQUIRED_FILES)} files, {links} links")


def verify_bundle() -> None:
    """Build and reopen the same deterministic documentation bundle as CI."""
    roots = [*ROOT.glob("*.md"), ROOT / "docs", ROOT / "workflows", ROOT / "handoffs"]
    files: list[Path] = []
    for entry in roots:
        files.extend(entry.rglob("*") if entry.is_dir() else [entry])
    files = sorted(path for path in files if path.is_file())

    with tempfile.TemporaryDirectory(prefix="flyto2-legacy-") as temp:
        archive = Path(temp) / "flyto2-legacy-docs.tar.gz"
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
            names = bundle.getnames()
        if "README.md" not in names or "SECURITY.md" not in names:
            raise RuntimeError("documentation bundle is incomplete")
    print(f"legacy documentation bundle passed: {len(files)} files")


if __name__ == "__main__":
    verify_contract()
    verify_bundle()

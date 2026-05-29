#!/usr/bin/env python3
"""Fetch the full ABCDE dataset from a GitHub Release and verify checksums.

Downloads every asset of the latest release (or ``--tag <tag>``) of
BEACNpool/ABCDE into ``data/release/`` (gitignored), then verifies each asset
against the ``artifacts.sha256`` manifest that ships in the same release.

Requires the GitHub CLI (`gh`) to be installed and authenticated.

Usage:
  python scripts/fetch_db.py                 # latest release
  python scripts/fetch_db.py --tag v2.0.0    # specific tag
"""
from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEST = REPO / "data" / "release"
SLUG = "BEACNpool/ABCDE"
MANIFEST_NAME = "artifacts.sha256"


def gh_download(tag: str | None) -> None:
    DEST.mkdir(parents=True, exist_ok=True)
    cmd = ["gh", "release", "download"]
    if tag:
        cmd.append(tag)
    cmd += ["--repo", SLUG, "--dir", str(DEST), "--clobber", "--pattern", "*"]
    print(f"$ {' '.join(cmd)}")
    subprocess.run(cmd, check=True)


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_manifest(manifest: Path) -> dict[str, str]:
    """Parse a `sha256  filename` manifest into {filename: digest}."""
    wanted: dict[str, str] = {}
    for line in manifest.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 2:
            continue
        digest = parts[0]
        # filename may contain a leading '*' (binary marker) and/or path
        name = " ".join(parts[1:]).lstrip("*")
        wanted[Path(name).name] = digest.lower()
    return wanted


def verify() -> int:
    manifest = DEST / MANIFEST_NAME
    if not manifest.exists():
        print(f"WARNING: no {MANIFEST_NAME} in release; skipping verification.")
        return 0
    wanted = parse_manifest(manifest)
    if not wanted:
        print(f"WARNING: {MANIFEST_NAME} is empty; nothing to verify.")
        return 0
    failures = 0
    for name, expected in sorted(wanted.items()):
        asset = DEST / name
        if not asset.exists():
            print(f"  MISSING  {name}")
            failures += 1
            continue
        actual = sha256_of(asset)
        if actual == expected:
            print(f"  OK       {name}")
        else:
            print(f"  MISMATCH {name}\n           expected {expected}\n           actual   {actual}")
            failures += 1
    return failures


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tag", help="release tag to download (default: latest)")
    args = parser.parse_args()

    gh_download(args.tag)
    print(f"\nDownloaded assets to {DEST.relative_to(REPO)}")
    print("Verifying checksums against artifacts.sha256 ...")
    failures = verify()
    if failures:
        sys.exit(f"\n{failures} asset(s) failed verification.")
    print("\nAll assets verified.")


if __name__ == "__main__":
    main()

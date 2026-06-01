#!/usr/bin/env python3
"""Verify committed public artifact hashes against the public manifest."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "manifests" / "public-artifacts-manifest.json"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", default=str(MANIFEST))
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    if not manifest_path.is_absolute():
        manifest_path = ROOT / manifest_path
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))

    failures = 0
    files = payload.get("files", [])
    for item in files:
        rel = item["path"]
        path = ROOT / rel
        if not path.exists():
            print(f"FAIL missing {rel}")
            failures += 1
            continue
        size = path.stat().st_size
        digest = sha256_file(path)
        if size != int(item["bytes"]) or digest != item["sha256"]:
            print(f"FAIL {rel}: bytes={size} sha256={digest}")
            print(f"  expected bytes={item['bytes']} sha256={item['sha256']}")
            failures += 1

    expected_count = int(payload.get("file_count", len(files)))
    if expected_count != len(files):
        print(f"FAIL manifest file_count={expected_count} but files has {len(files)} entries")
        failures += 1

    if failures:
        raise SystemExit(f"{failures} public artifact manifest failure(s)")
    print(f"Public artifact manifest OK: {len(files)} files")


if __name__ == "__main__":
    main()

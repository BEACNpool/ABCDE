#!/usr/bin/env python3
"""Fetch the full NIGHT spend-flow graph (release-tier) and verify it.

The full graph is ~630 MB — too large to belong in every clone. It is hosted on
a **custom git ref** (`refs/night-full/data`) rather than a branch, so a normal
`git clone` never downloads it, yet anyone can pull it on demand over plain
HTTPS (no auth, no PAT). This fetches just that ref's Parquet parts into
data/release/night_full_bundle/ and verifies every part's SHA-256 against the
committed manifest.

Usage:
  python scripts/fetch_night_full.py
  python scripts/fetch_night_full.py --remote https://github.com/BEACNpool/ABCDE.git

Then query with DuckDB, e.g.:
  SELECT count(*) FROM parquet_scan('data/release/night_full_bundle/utxo_nodes/*.parquet');
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "data/release/night_full_bundle"
MANIFEST = ROOT / "data/manifests/night-full-bundle-manifest.json"
REF = "refs/night-full/data"
DEFAULT_REMOTE = "https://github.com/BEACNpool/ABCDE.git"


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def git(*args: str) -> None:
    subprocess.run(["git", *args], check=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--remote", default=DEFAULT_REMOTE)
    ap.add_argument("--keep-tmp", action="store_true")
    args = ap.parse_args()
    if not MANIFEST.exists():
        sys.exit(f"missing {MANIFEST} — update your clone")
    manifest = json.loads(MANIFEST.read_text())

    tmp = Path(tempfile.mkdtemp(prefix="night-full-"))
    print(f"fetching {REF} (~{manifest.get('total_mb','?')} MB) from {args.remote} …")
    git("init", "-q", str(tmp))
    git("-C", str(tmp), "remote", "add", "origin", args.remote)
    git("-C", str(tmp), "fetch", "-q", "--depth", "1", "origin", REF)
    git("-C", str(tmp), "checkout", "-q", "FETCH_HEAD")

    DEST.mkdir(parents=True, exist_ok=True)
    ok = bad = 0
    for table, meta in manifest["tables"].items():
        for fmeta in meta["files"]:
            src = tmp / fmeta["path"]
            dst = DEST / fmeta["path"]
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            if sha256(dst) == fmeta["sha256"]:
                ok += 1
            else:
                bad += 1
                print(f"  SHA MISMATCH: {fmeta['path']}")
    if not args.keep_tmp:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"verified {ok} parts, {bad} bad -> {DEST.relative_to(ROOT)}")
    if bad:
        sys.exit(1)
    print("done. query with: "
          "parquet_scan('data/release/night_full_bundle/<table>/*.parquet')")


if __name__ == "__main__":
    main()

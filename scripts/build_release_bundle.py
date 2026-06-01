#!/usr/bin/env python3
"""Build public release assets with checksums."""
from __future__ import annotations

import hashlib
import json
import shutil
import tarfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist" / "release"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def add_tree(tar: tarfile.TarFile, path: Path) -> None:
    if not path.exists():
        return
    for item in sorted(path.rglob("*")):
        if item.is_file():
            tar.add(item, arcname=item.relative_to(ROOT))


def make_tar(name: str, paths: list[Path]) -> Path:
    out = DIST / name
    with tarfile.open(out, "w:gz") as tar:
        for path in paths:
            if path.is_dir():
                add_tree(tar, path)
            elif path.exists():
                tar.add(path, arcname=path.relative_to(ROOT))
    return out


def main() -> None:
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)

    assets: list[Path] = []
    db_src = ROOT / "data" / "abcde_genesis.duckdb"
    db_dst = DIST / "abcde_genesis.duckdb"
    shutil.copy2(db_src, db_dst)
    assets.append(db_dst)

    assets.append(make_tar("abcde_public_receipts.tar.gz", [
        ROOT / "data" / "small",
        ROOT / "data" / "manifests",
        ROOT / "data" / "manifest.json",
        ROOT / "data" / "schema_catalog.json",
        ROOT / "docs",
        ROOT / "findings",
        ROOT / "reports",
        ROOT / "claims",
        ROOT / "prompts",
    ]))

    reproducibility = DIST / "REPRODUCIBILITY.md"
    reproducibility.write_text(
        "# ABCDE Public Data Release\n\n"
        f"Generated UTC: {datetime.now(timezone.utc).isoformat(timespec='seconds')}\n\n"
        "This release contains the compact public DuckDB database plus committed\n"
        "CSV receipts, manifests, docs, findings, reports, claim receipt SQL, and\n"
        "AI reviewer prompts.\n\n"
        "Verify after download:\n\n"
        "```bash\n"
        "sha256sum -c artifacts.sha256\n"
        "python scripts/verify_claim_receipts.py\n"
        "python scripts/selftest.py\n"
        "```\n\n"
        "Limits: this public cut supports committed clone-and-query figures. Any\n"
        "claim requiring deeper private db-sync extraction must be labeled as such\n"
        "until a larger release asset is published.\n",
        encoding="utf-8",
    )
    assets.append(reproducibility)

    manifest = {
        "schema_version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "assets": [
            {
                "name": path.name,
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
            for path in assets
        ],
    }
    manifest_path = DIST / "MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    assets.append(manifest_path)

    checksum_path = DIST / "artifacts.sha256"
    checksum_path.write_text(
        "".join(f"{sha256_file(path)}  {path.name}\n" for path in assets),
        encoding="utf-8",
    )

    print(f"wrote {DIST.relative_to(ROOT)}")
    for path in sorted(DIST.iterdir()):
        print(f"{path.name}\t{path.stat().st_size}\t{sha256_file(path)}")


if __name__ == "__main__":
    main()

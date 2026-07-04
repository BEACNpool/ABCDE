#!/usr/bin/env python3
"""Package the full NIGHT spend-flow graph as a git-pushable release bundle.

The raw CSV export is ~2 GB and several files exceed GitHub's 100 MB per-file
push limit. This converts the graph to Parquet+ZSTD and splits each large table
into parts under ~45 MB (below GitHub's 50 MB warning), so the whole bundle can
be pushed to a dedicated data branch over an SSH deploy key — no PAT, no
Releases API, no Git LFS quota. DuckDB reads the parts back with a glob.

Source: NIGHT_SRC (default data/release/night_full/). Output: OUT_DIR staging
dir (default data/release/night_bundle/) with:
  <table>/<table>.part-NN.parquet     the split Parquet parts
  manifest.json                        files, rows, sha256, part counts
  README.md                            how to query the bundle

Deterministic: ntile ordered by a stable key. Idempotent (overwrites OUT_DIR).
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
SRC = Path(os.environ.get("NIGHT_SRC", ROOT / "data/release/night_full"))
OUT = Path(os.environ.get("NIGHT_BUNDLE", ROOT / "data/release/night_bundle"))
TARGET_PART_MB = 40  # aim; hard ceiling well under GitHub's 100 MB limit

# table -> (source csv, stable order key for deterministic splitting)
TABLES = {
    "mint_events": ("35_night_mint_events_abcde.csv", "tx_hash"),
    "root_utxo": ("36_night_root_utxo_abcde.csv", "utxo_node_id"),
    "utxo_nodes": ("37_night_reachable_utxo_nodes_abcde.csv", "utxo_node_id"),
    "tx_nodes": ("38_night_reachable_tx_nodes_abcde.csv", "tx_node_id"),
    "edges_utxo_to_tx": ("39_night_edges_utxo_to_tx_abcde.csv", "source_node_id"),
    "edges_tx_to_utxo": ("40_night_edges_tx_to_utxo_abcde.csv", "source_node_id"),
    "current_leaves": ("41_night_current_leaves_abcde.csv", "utxo_node_id"),
    "flow_summary": ("43_night_flow_summary_abcde.csv", "metric"),
}


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def main() -> None:
    con = duckdb.connect()
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    manifest = {"policy": "0691b2fecca1ac4f53cb6dfb00b7013e561d1f34403b957cbb5af1fa",
                "asset": "NIGHT", "target_part_mb": TARGET_PART_MB, "tables": {}}

    for table, (csv_name, key) in TABLES.items():
        csv = SRC / csv_name
        if not csv.exists():
            raise SystemExit(f"missing {csv} — set NIGHT_SRC to the unzipped export")
        # estimate parquet size from a single-file write to pick a part count
        probe = OUT / f"_probe_{table}.parquet"
        con.execute(f"COPY (SELECT * FROM read_csv_auto('{csv}')) TO '{probe}' "
                    f"(FORMAT PARQUET, COMPRESSION ZSTD)")
        mb = probe.stat().st_size / 1e6
        parts = max(1, -(-int(mb) // TARGET_PART_MB))  # ceil
        probe.unlink()

        tdir = OUT / table
        tdir.mkdir()
        if parts == 1:
            out = tdir / f"{table}.part-00.parquet"
            con.execute(f"COPY (SELECT * FROM read_csv_auto('{csv}')) TO '{out}' "
                        f"(FORMAT PARQUET, COMPRESSION ZSTD)")
        else:
            stage = OUT / f"_stage_{table}"
            con.execute(
                f"COPY (SELECT *, ntile({parts}) OVER (ORDER BY {key}) AS _part "
                f"FROM read_csv_auto('{csv}')) TO '{stage}' "
                f"(FORMAT PARQUET, PARTITION_BY (_part), COMPRESSION ZSTD, OVERWRITE_OR_IGNORE)")
            for pdir in sorted(stage.glob("_part=*")):
                n = int(pdir.name.split("=")[1])
                src_pq = next(pdir.glob("*.parquet"))
                src_pq.rename(tdir / f"{table}.part-{n:02d}.parquet")
            shutil.rmtree(stage)

        files = sorted(tdir.glob("*.parquet"))
        rows = con.execute(
            f"SELECT count(*) FROM parquet_scan('{tdir}/*.parquet')").fetchone()[0]
        manifest["tables"][table] = {
            "rows": rows, "parts": len(files),
            "max_part_bytes": max(p.stat().st_size for p in files),
            "files": [{"path": f"{table}/{p.name}", "bytes": p.stat().st_size,
                       "sha256": sha256(p)} for p in files],
        }
        big = manifest["tables"][table]["max_part_bytes"] / 1e6
        print(f"  {table:18} {rows:>9,} rows -> {len(files)} part(s), max {big:.1f} MB")

    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2))
    total = sum(p.stat().st_size for p in OUT.rglob("*.parquet"))
    over = [t for t, m in manifest["tables"].items() if m["max_part_bytes"] > 95 * 1e6]
    print(f"bundle: {total/1e6:.1f} MB across {sum(m['parts'] for m in manifest['tables'].values())} parquet parts")
    if over:
        raise SystemExit(f"parts still over 95 MB (lower TARGET_PART_MB): {over}")
    (OUT / "README.md").write_text(
        "# NIGHT full spend-flow graph (release bundle)\n\n"
        "Parquet+ZSTD, split into <45 MB parts so it fits GitHub's per-file push limit.\n"
        "Fetch with `python scripts/fetch_night_full.py`; query with DuckDB, e.g.\n\n"
        "```sql\nSELECT count(*) FROM parquet_scan('utxo_nodes/*.parquet');\n```\n")
    print("done. manifest.json + README.md written.")


if __name__ == "__main__":
    main()

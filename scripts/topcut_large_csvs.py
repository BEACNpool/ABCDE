#!/usr/bin/env python3
"""Enforce the compact-cut size policy on oversized committed CSVs.

Some warehouse extracts (notably the depth-14 IOG per-UTxO drilldown) are large
enough to push the committed DuckDB over GitHub's 50 MiB warning / the repo's
hard gate. The repo's documented pattern (docs/22) is "release asset + committed
top-cut": keep the highest-value rows in the compact clone so clone-and-ask
still answers the common questions, and move the full table to the gitignored
release tier (published as a GitHub Release asset).

This script makes that automatic and idempotent. For each configured table it:
  - if data/small/<name>.csv exceeds max_rows, copies the FULL file to
    data/release/<name>_full.csv (gitignored) and rewrites data/small/<name>.csv
    to the top max_rows by the value column (ties broken deterministically);
  - writes a sidecar data/small/<name>.coverage.json recording full row count,
    kept rows, and % of value retained, so the cut is transparent and auditable.

Run before build_genesis_db.py. Safe to run repeatedly: an already-cut file
(row count <= max_rows) is left untouched.
"""
from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SMALL = ROOT / "data" / "small"
RELEASE = ROOT / "data" / "release"

# table stem -> (value column, rows kept in the compact cut)
CONFIG = {
    "iog_current_bag_depth14_current_utxos": ("current_ada", 15000),
}


def topcut(stem: str, value_col: str, max_rows: int) -> None:
    src = SMALL / f"{stem}.csv"
    if not src.exists():
        return
    with src.open() as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fields = reader.fieldnames or []
    if len(rows) <= max_rows:
        return  # already within budget (or already cut)

    RELEASE.mkdir(parents=True, exist_ok=True)
    full_dst = RELEASE / f"{stem}_full.csv"
    shutil.copy2(src, full_dst)

    def sort_key(r: dict[str, str]):
        try:
            v = float(r.get(value_col) or 0)
        except ValueError:
            v = 0.0
        # deterministic tie-break on the remaining columns
        return (-v, tuple(r.get(c, "") for c in fields if c != value_col))

    rows.sort(key=sort_key)
    kept = rows[:max_rows]

    total_val = sum(_num(r.get(value_col)) for r in rows)
    kept_val = sum(_num(r.get(value_col)) for r in kept)

    with src.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(kept)

    coverage = {
        "table": stem,
        "value_column": value_col,
        "full_rows": len(rows),
        "kept_rows": len(kept),
        "value_retained_pct": round(100 * kept_val / total_val, 4) if total_val else None,
        "full_release_asset": f"data/release/{stem}_full.csv",
        "note": (
            "Compact cut = top rows by value. Full table is a release-tier "
            "artifact (gitignored); regenerate with the maintainer extract "
            "script or pull from a GitHub Release."
        ),
    }
    (SMALL / f"{stem}.coverage.json").write_text(json.dumps(coverage, indent=2) + "\n")
    print(f"  top-cut {stem}: kept {len(kept)}/{len(rows)} rows "
          f"({coverage['value_retained_pct']}% of value); full -> {full_dst.relative_to(ROOT)}")


def _num(v) -> float:
    try:
        return float(v or 0)
    except (TypeError, ValueError):
        return 0.0


def main() -> None:
    for stem, (col, n) in CONFIG.items():
        topcut(stem, col, n)


if __name__ == "__main__":
    main()

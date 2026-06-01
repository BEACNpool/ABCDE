#!/usr/bin/env python3
"""Verify public claim receipt SQL against the committed DuckDB database."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = ROOT / "data" / "abcde_genesis.duckdb"
CLAIMS = ROOT / "claims" / "manifest.json"


def render_tsv(columns: list[str], rows: list[tuple[Any, ...]]) -> str:
    out: list[str] = []
    out.append("\t".join(columns))
    for row in rows:
        out.append("\t".join("" if v is None else str(v) for v in row))
    return "\n".join(out) + "\n"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", default=str(DEFAULT_DB), help="DuckDB file to query")
    parser.add_argument("--write-outputs", action="store_true", help="Write receipt TSV outputs to claims/outputs/")
    args = parser.parse_args()

    import duckdb  # type: ignore

    manifest = json.loads(CLAIMS.read_text(encoding="utf-8"))
    output_dir = ROOT / "claims" / "outputs"
    if args.write_outputs:
        output_dir.mkdir(parents=True, exist_ok=True)

    con = duckdb.connect(args.db, read_only=True)
    failures = 0
    try:
        for claim in manifest["claims"]:
            sql_path = ROOT / claim["sql"]
            sql = sql_path.read_text(encoding="utf-8")
            result = con.execute(sql)
            columns = [d[0] for d in result.description or []]
            rows = result.fetchall()
            text = render_tsv(columns, rows)
            digest = sha256_text(text)

            expected_rows = int(claim["expected_rows"])
            expected_digest = claim["output_sha256"]
            ok = len(rows) == expected_rows and digest == expected_digest
            status = "PASS" if ok else "FAIL"
            print(f"{status} {claim['id']}: rows={len(rows)} sha256={digest}")
            if args.write_outputs:
                (output_dir / f"{claim['id']}.tsv").write_text(text, encoding="utf-8")
            if not ok:
                print(f"  expected rows={expected_rows} sha256={expected_digest}")
                failures += 1
    finally:
        con.close()

    if failures:
        raise SystemExit(f"{failures} claim receipt(s) failed")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Run a SQL file against the local ABCDE DuckDB artifact."""
from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('sql_file')
    parser.add_argument('--db', default='data/abcde_genesis.duckdb')
    args = parser.parse_args()

    import duckdb  # type: ignore

    sql_path = ROOT / args.sql_file
    db_path = ROOT / args.db
    sql = sql_path.read_text()
    con = duckdb.connect(str(db_path), read_only=True)
    try:
        result = con.execute(sql)
        rows = result.fetchall()
        columns = [d[0] for d in result.description or []]
        if columns:
            print(','.join(columns))
        for row in rows:
            print(','.join('' if v is None else str(v) for v in row))
    finally:
        con.close()


if __name__ == "__main__":
    main()

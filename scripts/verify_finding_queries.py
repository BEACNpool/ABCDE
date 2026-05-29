#!/usr/bin/env python3
"""Execute every sql/10_findings/*.duckdb.sql query against the local DuckDB cut."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / 'data/abcde_genesis_seed_registry.duckdb'
SQL_DIR = ROOT / 'sql/10_findings'


def main() -> None:
    import duckdb  # type: ignore

    if not DB.exists():
        raise SystemExit(f'missing {DB.relative_to(ROOT)}')
    sql_files = sorted(SQL_DIR.glob('*.duckdb.sql'))
    if not sql_files:
        raise SystemExit('no finding SQL files found')

    con = duckdb.connect(str(DB), read_only=True)
    try:
        for sql_file in sql_files:
            sql = sql_file.read_text()
            rows = con.execute(sql).fetchall()
            if len(rows) == 0:
                raise SystemExit(f'{sql_file.relative_to(ROOT)} returned zero rows')
            print(f'OK {sql_file.relative_to(ROOT)} rows={len(rows)}')
    finally:
        con.close()


if __name__ == '__main__':
    main()

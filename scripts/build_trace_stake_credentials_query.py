#!/usr/bin/env python3
"""Emit db-sync SQL to extract stake credentials visible in a bounded trace cut.

For now this uses the committed bounded trace CSV as input on the local side only for its addresses.
The remote query resolves stake credentials from db-sync for those addresses where possible.
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRACE_CSV = ROOT / 'data/small/bounded_trace_depth3_db.csv'


def quote(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def main() -> None:
    rows = list(csv.DictReader(TRACE_CSV.open(newline='')))
    addresses = sorted({r['address'] for r in rows if r.get('address')})
    if not addresses:
        raise SystemExit('no addresses in bounded trace CSV')
    print('WITH addresses(address) AS (VALUES')
    print(',\n'.join(f'  ({quote(a)})' for a in addresses))
    print(')')
    print(r"""
SELECT DISTINCT
  txo.address,
  sa.id AS stake_address_id,
  sa.view AS stake_address
FROM addresses a
JOIN public.tx_out txo ON txo.address = a.address
LEFT JOIN public.stake_address sa ON sa.id = txo.stake_address_id
ORDER BY stake_address NULLS LAST, address;
""")


if __name__ == '__main__':
    main()

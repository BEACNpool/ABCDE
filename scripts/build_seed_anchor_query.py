#!/usr/bin/env python3
"""Emit the read-only db-sync SQL used to verify seed anchors."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'lib'))

from chain_toolkit.anchors import load_anchors


def quote(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def main() -> None:
    print('WITH seeds(seed_id,label,tx_hash_hex,amount_lovelace) AS (VALUES')
    parts = []
    for a in load_anchors(ROOT / 'anchors.yaml'):
        parts.append(
            f"  ({quote(a.seed_id)}, {quote(a.label)}, {quote(a.tx_hash)}, {a.amount_ada * 1_000_000})"
        )
    print(',\n'.join(parts))
    print(')')
    print(r"""
SELECT
  s.seed_id,
  s.label,
  CASE WHEN tx.id IS NULL THEN 'MISSING' ELSE 'FOUND' END AS status,
  tx.id AS tx_id,
  b.epoch_no,
  b.block_no,
  b.time AS block_time_utc,
  (SELECT count(*) FROM public.tx_out txo WHERE txo.tx_id = tx.id) AS output_count,
  (SELECT coalesce(sum(value),0) FROM public.tx_out txo WHERE txo.tx_id = tx.id) AS tx_output_lovelace
FROM seeds s
LEFT JOIN public.tx tx ON tx.hash = decode(s.tx_hash_hex, 'hex')
LEFT JOIN public.block b ON b.id = tx.block_id
ORDER BY s.seed_id;
""")


if __name__ == '__main__':
    main()

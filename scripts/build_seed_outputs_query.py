#!/usr/bin/env python3
"""Emit read-only db-sync SQL to materialize seed redemption outputs."""
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
  encode(tx.hash, 'hex') AS tx_hash,
  tx.id AS tx_id,
  txo.index AS tx_out_index,
  txo.value AS value_lovelace,
  txo.address,
  sa.view AS stake_address,
  b.epoch_no,
  b.block_no,
  b.time AS block_time_utc
FROM seeds s
JOIN public.tx tx ON tx.hash = decode(s.tx_hash_hex, 'hex')
JOIN public.tx_out txo ON txo.tx_id = tx.id
LEFT JOIN public.stake_address sa ON sa.id = txo.stake_address_id
JOIN public.block b ON b.id = tx.block_id
ORDER BY s.seed_id, txo.index;
""")


if __name__ == '__main__':
    main()

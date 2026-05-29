#!/usr/bin/env python3
"""Emit read-only db-sync SQL for bounded seed UTxO traces."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'lib'))

from chain_toolkit.anchors import load_anchors

MAX_DEPTH = int(__import__('os').environ.get('TRACE_DEPTH', '3'))


def quote(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def main() -> None:
    print('WITH RECURSIVE seeds(seed_id,label,tx_hash_hex,amount_lovelace) AS (VALUES')
    parts = []
    for a in load_anchors(ROOT / 'anchors.yaml'):
        parts.append(f"  ({quote(a.seed_id)}, {quote(a.label)}, {quote(a.tx_hash)}, {a.amount_ada * 1_000_000})")
    print(',\n'.join(parts))
    print('), trace AS (')
    print(rf"""
  SELECT
    s.seed_id,
    s.label,
    0 AS depth,
    tx.id AS tx_id,
    encode(tx.hash, 'hex') AS tx_hash,
    txo.index AS tx_out_index,
    txo.value AS value_lovelace,
    txo.address,
    sa.view AS stake_address,
    b.epoch_no,
    b.block_no,
    b.time AS block_time_utc,
    NULL::bigint AS spent_by_tx_id,
    NULL::text AS spent_by_tx_hash,
    ARRAY[encode(tx.hash, 'hex') || '#' || txo.index::text]::text[] AS path
  FROM seeds s
  JOIN public.tx tx ON tx.hash = decode(s.tx_hash_hex, 'hex')
  JOIN public.tx_out txo ON txo.tx_id = tx.id
  LEFT JOIN public.stake_address sa ON sa.id = txo.stake_address_id
  JOIN public.block b ON b.id = tx.block_id

  UNION ALL

  SELECT
    tr.seed_id,
    tr.label,
    tr.depth + 1 AS depth,
    child_tx.id AS tx_id,
    encode(child_tx.hash, 'hex') AS tx_hash,
    child_out.index AS tx_out_index,
    child_out.value AS value_lovelace,
    child_out.address,
    child_sa.view AS stake_address,
    child_block.epoch_no,
    child_block.block_no,
    child_block.time AS block_time_utc,
    child_tx.id AS spent_by_tx_id,
    encode(child_tx.hash, 'hex') AS spent_by_tx_hash,
    tr.path || (encode(child_tx.hash, 'hex') || '#' || child_out.index::text)
  FROM trace tr
  JOIN public.tx_in spend
    ON spend.tx_out_id = tr.tx_id
   AND spend.tx_out_index = tr.tx_out_index
  JOIN public.tx child_tx
    ON child_tx.id = spend.tx_in_id
  JOIN public.tx_out child_out
    ON child_out.tx_id = child_tx.id
  LEFT JOIN public.stake_address child_sa ON child_sa.id = child_out.stake_address_id
  JOIN public.block child_block ON child_block.id = child_tx.block_id
  WHERE tr.depth < {MAX_DEPTH}
)
SELECT
  seed_id,
  label,
  depth,
  tx_hash,
  tx_id,
  tx_out_index,
  value_lovelace,
  address,
  stake_address,
  epoch_no,
  block_no,
  block_time_utc,
  array_to_string(path, ' > ') AS path
FROM trace
ORDER BY seed_id, depth, tx_hash, tx_out_index;
""")


if __name__ == '__main__':
    main()

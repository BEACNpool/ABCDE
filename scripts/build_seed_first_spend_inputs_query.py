#!/usr/bin/env python3
"""Emit read-only db-sync SQL for input composition of seed first-spend txs."""
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
        parts.append(f"  ({quote(a.seed_id)}, {quote(a.label)}, {quote(a.tx_hash)}, {a.amount_ada * 1_000_000})")
    print(',\n'.join(parts))
    print('), seed_outputs AS (')
    print(r"""
  SELECT
    s.seed_id,
    s.label,
    tx.id AS seed_tx_id,
    encode(tx.hash, 'hex') AS seed_tx_hash,
    txo.index AS seed_tx_out_index,
    txo.value AS seed_value_lovelace,
    b.time AS seed_time_utc
  FROM seeds s
  JOIN public.tx tx ON tx.hash = decode(s.tx_hash_hex, 'hex')
  JOIN public.tx_out txo ON txo.tx_id = tx.id
  JOIN public.block b ON b.id = tx.block_id
), first_spends AS (
  SELECT
    so.*,
    spend_tx.id AS first_spend_tx_id,
    encode(spend_tx.hash, 'hex') AS first_spend_tx_hash,
    spend_block.time AS first_spend_time_utc
  FROM seed_outputs so
  JOIN public.tx_in seed_spend
    ON seed_spend.tx_out_id = so.seed_tx_id
   AND seed_spend.tx_out_index = so.seed_tx_out_index
  JOIN public.tx spend_tx
    ON spend_tx.id = seed_spend.tx_in_id
  JOIN public.block spend_block
    ON spend_block.id = spend_tx.block_id
), input_rows AS (
  SELECT
    fs.seed_id AS first_spend_seed_id,
    fs.label AS first_spend_seed_label,
    fs.first_spend_tx_hash,
    fs.first_spend_tx_id,
    src_tx.id AS input_source_tx_id,
    encode(src_tx.hash, 'hex') AS input_source_tx_hash,
    txi.tx_out_index AS input_source_tx_out_index,
    src_out.value AS input_value_lovelace,
    src_out.address AS input_address,
    sa.view AS input_stake_address,
    src_block.epoch_no AS input_source_epoch,
    src_block.block_no AS input_source_block_no,
    src_block.time AS input_source_time_utc,
    matched_seed.seed_id AS matched_seed_id
  FROM first_spends fs
  JOIN public.tx_in txi
    ON txi.tx_in_id = fs.first_spend_tx_id
  JOIN public.tx src_tx
    ON src_tx.id = txi.tx_out_id
  JOIN public.tx_out src_out
    ON src_out.tx_id = src_tx.id
   AND src_out.index = txi.tx_out_index
  JOIN public.block src_block
    ON src_block.id = src_tx.block_id
  LEFT JOIN public.stake_address sa
    ON sa.id = src_out.stake_address_id
  LEFT JOIN seeds matched_seed
    ON src_tx.hash = decode(matched_seed.tx_hash_hex, 'hex')
)
SELECT *
FROM input_rows
ORDER BY first_spend_seed_id, input_value_lovelace DESC, input_source_tx_hash, input_source_tx_out_index;
""")


if __name__ == '__main__':
    main()

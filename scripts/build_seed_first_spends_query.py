#!/usr/bin/env python3
"""Emit read-only db-sync SQL for first spends of seed redemption outputs.

Uses the correct db-sync relation:
  tx_in.tx_out_id = producing_tx.id
  tx_in.tx_out_index = produced_output.index
"""
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
)
SELECT
  so.seed_id,
  so.label,
  so.seed_tx_hash,
  so.seed_tx_id,
  so.seed_tx_out_index,
  so.seed_value_lovelace,
  so.seed_time_utc,
  encode(spend_tx.hash, 'hex') AS first_spend_tx_hash,
  spend_tx.id AS first_spend_tx_id,
  spend_block.epoch_no AS first_spend_epoch,
  spend_block.block_no AS first_spend_block_no,
  spend_block.time AS first_spend_time_utc,
  extract(epoch from (spend_block.time - so.seed_time_utc)) / 3600.0 AS dormant_hours,
  (SELECT count(*) FROM public.tx_in ti WHERE ti.tx_in_id = spend_tx.id) AS spend_input_count,
  (SELECT count(*) FROM public.tx_out txo WHERE txo.tx_id = spend_tx.id) AS spend_output_count,
  (SELECT coalesce(sum(txo.value),0) FROM public.tx_out txo WHERE txo.tx_id = spend_tx.id) AS spend_output_lovelace
FROM seed_outputs so
LEFT JOIN public.tx_in seed_spend
  ON seed_spend.tx_out_id = so.seed_tx_id
 AND seed_spend.tx_out_index = so.seed_tx_out_index
LEFT JOIN public.tx spend_tx
  ON spend_tx.id = seed_spend.tx_in_id
LEFT JOIN public.block spend_block
  ON spend_block.id = spend_tx.block_id
ORDER BY so.seed_id;
""")


if __name__ == '__main__':
    main()

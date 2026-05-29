#!/usr/bin/env python3
"""Emit SQL files to enrich governance delegation targets with pool/DRep metadata."""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPO_CSV = ROOT / 'data/small/governance_spo_delegation_targets.csv'
DREP_CSV = ROOT / 'data/small/governance_drep_delegation_targets.csv'


def quote(v: str) -> str:
    return "'" + v.replace("'", "''") + "'"


def pool_sql() -> str:
    rows = list(csv.DictReader(SPO_CSV.open(newline='')))
    pools = sorted({r['pool_id_bech32'] for r in rows if r['pool_id_bech32']})
    values = ',\n'.join(f'  ({quote(p)})' for p in pools)
    return f"""WITH wanted(pool_id_bech32) AS (VALUES
{values}
), latest_meta AS (
  SELECT DISTINCT ON (ph.view)
    ph.view AS pool_id_bech32,
    ocpd.ticker_name,
    ocpd.json ->> 'name' AS pool_name,
    ocpd.json ->> 'homepage' AS homepage,
    ocpd.json ->> 'description' AS description,
    pmr.url AS metadata_url,
    encode(pmr.hash, 'hex') AS metadata_hash_hex,
    pu.active_epoch_no
  FROM wanted w
  JOIN public.pool_hash ph ON ph.view = w.pool_id_bech32
  LEFT JOIN public.pool_update pu ON pu.hash_id = ph.id
  LEFT JOIN public.pool_metadata_ref pmr ON pmr.id = pu.meta_id
  LEFT JOIN public.off_chain_pool_data ocpd ON ocpd.pmr_id = pmr.id
  ORDER BY ph.view, pu.active_epoch_no DESC NULLS LAST, pu.id DESC NULLS LAST
)
SELECT * FROM latest_meta ORDER BY pool_id_bech32;
"""


def drep_sql() -> str:
    rows = list(csv.DictReader(DREP_CSV.open(newline='')))
    dreps = sorted({r['drep_id_bech32'] for r in rows if r['drep_id_bech32'].startswith('drep1')})
    values = ',\n'.join(f'  ({quote(d)})' for d in dreps)
    return f"""WITH wanted(drep_id_bech32) AS (VALUES
{values}
), latest_reg AS (
  SELECT DISTINCT ON (dh.view)
    dh.view AS drep_id_bech32,
    dr.deposit,
    va.url AS voting_anchor_url,
    encode(va.data_hash, 'hex') AS voting_anchor_data_hash_hex,
    encode(tx.hash, 'hex') AS registration_tx_hash,
    b.epoch_no,
    b.time AS block_time_utc
  FROM wanted w
  JOIN public.drep_hash dh ON dh.view = w.drep_id_bech32
  LEFT JOIN public.drep_registration dr ON dr.drep_hash_id = dh.id
  LEFT JOIN public.voting_anchor va ON va.id = dr.voting_anchor_id
  LEFT JOIN public.tx tx ON tx.id = dr.tx_id
  LEFT JOIN public.block b ON b.id = tx.block_id
  ORDER BY dh.view, b.time DESC NULLS LAST, dr.id DESC NULLS LAST
)
SELECT * FROM latest_reg ORDER BY drep_id_bech32;
"""


def main() -> None:
    print('-- POOL_METADATA_SQL_START')
    print(pool_sql())
    print('-- DREP_METADATA_SQL_START')
    print(drep_sql())


if __name__ == '__main__':
    main()

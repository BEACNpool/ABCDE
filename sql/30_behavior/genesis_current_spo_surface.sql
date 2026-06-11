-- Export Genesis trace -> current SPO (stake pool) delegation surface.
--
-- One row per (root_seed_id, current live traced UTxO). Carries the latest
-- observed pool delegation AND latest observed DRep vote delegation for the
-- UTxO's stake credential, so pool/DRep cross-tabs can be built locally.
--
-- psql variables:
--   stage_schema: staged trace schema where build_genesis_governance_surface_tables.sql ran
--
-- Evidence boundary: latest delegation targets are on-chain observations.
-- They are not custody, ownership, identity, or intent claims.
WITH traced_creds AS (
  SELECT DISTINCT stake_address_id
  FROM :"stage_schema".current_live_utxos
  WHERE stake_address_id IS NOT NULL
),
latest_pool AS (
  SELECT DISTINCT ON (d.addr_id)
    d.addr_id,
    d.pool_hash_id,
    d.active_epoch_no AS pool_active_epoch_no,
    d.tx_id AS pool_delegation_tx_id
  FROM public.delegation d
  JOIN traced_creds t ON t.stake_address_id = d.addr_id
  ORDER BY d.addr_id, d.tx_id DESC, d.cert_index DESC
)
SELECT
  to_char(now() AT TIME ZONE 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS"Z"') AS snapshot_utc,
  :'stage_schema' AS trace_schema,
  u.root_seed_id,
  u.tx_id,
  u.tx_hash,
  u.tx_out_index,
  u.min_depth,
  u.value_lovelace,
  u.stake_address_id,
  u.stake_address,
  u.epoch_no AS output_epoch_no,
  u.block_no AS output_block_no,
  u.block_time_utc AS output_block_time_utc,
  ph.view AS latest_pool_id_bech32,
  lp.pool_active_epoch_no,
  encode(ptx.hash, 'hex') AS pool_delegation_tx_hash,
  lv.drep_id_bech32 AS latest_drep_id_bech32,
  lv.latest_vote_epoch
FROM :"stage_schema".current_live_utxos u
LEFT JOIN latest_pool lp ON lp.addr_id = u.stake_address_id
LEFT JOIN public.pool_hash ph ON ph.id = lp.pool_hash_id
LEFT JOIN public.tx ptx ON ptx.id = lp.pool_delegation_tx_id
LEFT JOIN :"stage_schema".current_latest_vote lv ON lv.addr_id = u.stake_address_id
ORDER BY u.root_seed_id, u.min_depth, u.tx_id, u.tx_out_index;

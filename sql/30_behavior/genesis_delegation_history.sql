-- Full delegation certificate history (SPO + DRep) for every stake credential
-- ever reached by a Genesis trace. One row per certificate observation.
-- Large export: release asset, not committed to git.
--
-- psql variables:
--   stage_schema: staged trace schema (uses all-time trace_utxos membership)
--
-- Evidence boundary: certificates are on-chain observations about delegation
-- targets over time. They are not custody, ownership, identity, or intent
-- claims.
WITH traced_creds AS (
  SELECT
    stake_address_id,
    min(min_depth) AS min_trace_depth,
    string_agg(DISTINCT root_seed_id, '+' ORDER BY root_seed_id) AS root_combo
  FROM :"stage_schema".trace_utxos
  WHERE stake_address_id IS NOT NULL
  GROUP BY stake_address_id
)
SELECT
  to_char(now() AT TIME ZONE 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS"Z"') AS snapshot_utc,
  :'stage_schema' AS trace_schema,
  'spo_delegation' AS cert_type,
  sa.view AS stake_address,
  tc.min_trace_depth,
  tc.root_combo,
  ph.view AS target_id_bech32,
  d.active_epoch_no AS active_or_cert_epoch,
  encode(tx.hash, 'hex') AS cert_tx_hash,
  b.time AS cert_block_time_utc
FROM public.delegation d
JOIN traced_creds tc ON tc.stake_address_id = d.addr_id
JOIN public.stake_address sa ON sa.id = d.addr_id
JOIN public.pool_hash ph ON ph.id = d.pool_hash_id
JOIN public.tx ON tx.id = d.tx_id
JOIN public.block b ON b.id = tx.block_id
UNION ALL
SELECT
  to_char(now() AT TIME ZONE 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS"Z"') AS snapshot_utc,
  :'stage_schema' AS trace_schema,
  'drep_vote_delegation' AS cert_type,
  sa.view AS stake_address,
  tc.min_trace_depth,
  tc.root_combo,
  coalesce(dh.view, 'drep_raw_' || encode(dh.raw, 'hex')) AS target_id_bech32,
  b.epoch_no AS active_or_cert_epoch,
  encode(tx.hash, 'hex') AS cert_tx_hash,
  b.time AS cert_block_time_utc
FROM public.delegation_vote dv
JOIN traced_creds tc ON tc.stake_address_id = dv.addr_id
JOIN public.stake_address sa ON sa.id = dv.addr_id
JOIN public.drep_hash dh ON dh.id = dv.drep_hash_id
JOIN public.tx ON tx.id = dv.tx_id
JOIN public.block b ON b.id = tx.block_id
ORDER BY stake_address, cert_block_time_utc, cert_type;

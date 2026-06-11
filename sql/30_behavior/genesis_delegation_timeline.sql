-- Committed rollup: delegation certificate activity per epoch, root combo,
-- and certificate type for trace-reached stake credentials. Answers "when did
-- traced credentials (re)delegate, and toward how many distinct targets" as a
-- small receipt; per-certificate detail lives in the release-asset history.
--
-- psql variables:
--   stage_schema: staged trace schema (uses all-time trace_utxos membership)
WITH traced_creds AS (
  SELECT
    stake_address_id,
    string_agg(DISTINCT root_seed_id, '+' ORDER BY root_seed_id) AS root_combo
  FROM :"stage_schema".trace_utxos
  WHERE stake_address_id IS NOT NULL
  GROUP BY stake_address_id
),
certs AS (
  SELECT
    'spo_delegation' AS cert_type,
    tc.root_combo,
    b.epoch_no,
    d.addr_id,
    d.pool_hash_id::text AS target_key
  FROM public.delegation d
  JOIN traced_creds tc ON tc.stake_address_id = d.addr_id
  JOIN public.tx ON tx.id = d.tx_id
  JOIN public.block b ON b.id = tx.block_id
  UNION ALL
  SELECT
    'drep_vote_delegation' AS cert_type,
    tc.root_combo,
    b.epoch_no,
    dv.addr_id,
    dv.drep_hash_id::text AS target_key
  FROM public.delegation_vote dv
  JOIN traced_creds tc ON tc.stake_address_id = dv.addr_id
  JOIN public.tx ON tx.id = dv.tx_id
  JOIN public.block b ON b.id = tx.block_id
)
SELECT
  to_char(now() AT TIME ZONE 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS"Z"') AS snapshot_utc,
  :'stage_schema' AS trace_schema,
  cert_type,
  root_combo,
  epoch_no,
  count(*) AS cert_count,
  count(DISTINCT addr_id) AS distinct_stake_addresses,
  count(DISTINCT target_key) AS distinct_targets
FROM certs
GROUP BY cert_type, root_combo, epoch_no
ORDER BY cert_type, root_combo, epoch_no;

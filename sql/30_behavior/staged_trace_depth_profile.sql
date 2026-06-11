-- Per-root depth profile for a staged trace schema: rows, value, credential
-- counts, and live-unspent rows per (root_seed_id, min_depth). Small receipt
-- that documents how far each root's trace actually reaches and how value
-- dilutes with depth.
--
-- psql variables:
--   stage_schema: staged trace schema built by build_staged_trace_sql.py
WITH live AS (
  SELECT u.root_seed_id, u.min_depth, count(*) AS live_rows,
         sum(u.value_lovelace) AS live_lovelace
  FROM :"stage_schema".trace_utxos u
  LEFT JOIN public.tx_in spend
    ON spend.tx_out_id = u.tx_id
   AND spend.tx_out_index = u.tx_out_index
  WHERE spend.tx_in_id IS NULL
  GROUP BY u.root_seed_id, u.min_depth
)
SELECT
  to_char(now() AT TIME ZONE 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS"Z"') AS snapshot_utc,
  :'stage_schema' AS trace_schema,
  u.root_seed_id,
  u.min_depth,
  count(*) AS utxo_rows,
  sum(u.value_lovelace) AS total_lovelace,
  count(DISTINCT u.stake_address_id) AS distinct_stake_addresses,
  coalesce(max(l.live_rows), 0) AS live_unspent_rows,
  coalesce(max(l.live_lovelace), 0) AS live_unspent_lovelace
FROM :"stage_schema".trace_utxos u
LEFT JOIN live l
  ON l.root_seed_id = u.root_seed_id AND l.min_depth = u.min_depth
GROUP BY u.root_seed_id, u.min_depth
ORDER BY u.root_seed_id, u.min_depth;

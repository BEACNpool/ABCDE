-- ADA Handle resolved owner footprint report backing query
-- Usage:
--   psql -d cexplorer_replica -v handle='bob' -At -F $'\t' -f queries/ada_handle_owner_footprint.sql
--
-- Scope:
-- - Counts are keyed to the resolved owner identity as observed in the owner tx output:
--   payment credential + stake identity shape.
-- - This is still strictly on-chain, but avoids an unindexed address-string scan.

\if :{?handle}
\else
\echo 'ERROR: pass -v handle=<name> (without leading $)'
\quit 1
\endif

WITH resolved AS (
  SELECT
    h.handle,
    h.handle_display,
    h.current_owner_address,
    h.current_owner_stake,
    h.tx_hash,
    h.block_no,
    h.slot_no,
    h.epoch_no,
    h.observed_at,
    t.id AS tx_id
  FROM explorer.handle_search h
  JOIN public.tx t
    ON t.hash = decode(h.tx_hash, 'hex')
  WHERE lower(h.handle) = lower(:'handle')
), owner_identity AS (
  SELECT
    r.handle,
    r.handle_display,
    r.current_owner_address,
    COALESCE(r.current_owner_stake, '-') AS current_owner_stake,
    r.tx_hash,
    r.block_no,
    r.slot_no,
    r.epoch_no,
    r.observed_at,
    txo.payment_cred,
    txo.stake_address_id
  FROM resolved r
  JOIN public.tx_out txo
    ON txo.tx_id = r.tx_id
   AND txo.address = r.current_owner_address
  ORDER BY txo.id
  LIMIT 1
), matched_outputs AS (
  SELECT
    oi.handle,
    oi.handle_display,
    oi.current_owner_address,
    oi.current_owner_stake,
    oi.tx_hash,
    oi.block_no,
    oi.slot_no,
    oi.epoch_no,
    oi.observed_at,
    txo.id AS tx_out_row_id,
    txo.tx_id,
    txo.index,
    txo.value,
    txo.consumed_by_tx_id,
    b.block_no AS matched_block_no,
    b.time AS matched_block_time
  FROM owner_identity oi
  JOIN public.tx_out txo
    ON txo.payment_cred = oi.payment_cred
   AND txo.stake_address_id IS NOT DISTINCT FROM oi.stake_address_id
  JOIN public.tx t
    ON t.id = txo.tx_id
  JOIN public.block b
    ON b.id = t.block_id
), counts AS (
  SELECT
    COUNT(*)::text AS tx_out_rows,
    COUNT(DISTINCT tx_id)::text AS distinct_output_txs,
    COUNT(DISTINCT consumed_by_tx_id)::text AS distinct_consuming_txs,
    COUNT(*) FILTER (WHERE consumed_by_tx_id IS NOT NULL)::text AS tx_in_rows,
    COALESCE(SUM(value), 0)::text AS total_received_lovelace,
    COALESCE(MIN(matched_block_no), 0)::text AS earliest_block_no,
    COALESCE(MAX(matched_block_no), 0)::text AS latest_block_no
  FROM matched_outputs
), recent AS (
  SELECT
    matched_block_no::text AS matched_block_no,
    encode(t.hash::bytea, 'hex') AS matched_tx_hash,
    mo.index::text AS tx_out_index,
    mo.value::text AS lovelace,
    COALESCE(mo.consumed_by_tx_id::text, '-') AS consumed_by_tx_id
  FROM matched_outputs mo
  JOIN public.tx t
    ON t.id = mo.tx_id
  ORDER BY mo.matched_block_no DESC, matched_tx_hash, mo.index
  LIMIT 5
)
SELECT
  'owner' AS section,
  oi.handle,
  oi.handle_display,
  oi.current_owner_address,
  oi.current_owner_stake,
  oi.tx_hash,
  oi.block_no::text,
  oi.slot_no::text,
  oi.epoch_no::text,
  oi.observed_at::text
FROM owner_identity oi
UNION ALL
SELECT
  'counts' AS section,
  c.tx_out_rows,
  c.distinct_output_txs,
  c.distinct_consuming_txs,
  c.tx_in_rows,
  c.total_received_lovelace,
  c.earliest_block_no,
  c.latest_block_no,
  NULL::text,
  NULL::text
FROM counts c
UNION ALL
SELECT
  'recent' AS section,
  r.matched_block_no,
  r.matched_tx_hash,
  r.tx_out_index,
  r.lovelace,
  r.consumed_by_tx_id,
  NULL::text,
  NULL::text,
  NULL::text,
  NULL::text
FROM recent r;

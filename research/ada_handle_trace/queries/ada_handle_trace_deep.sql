-- ADA Handle resolution + bounded backward hop trace helper for ABCDE
--
-- Usage:
--   psql -d cexplorer_replica -v handle='bob' -v max_depth='3' -f queries/ada_handle_trace_deep.sql
--
-- Notes:
-- - Input handle should be WITHOUT the leading '$'.
-- - This stays strictly on-chain and starts from explorer.handle_search.
-- - This version is intentionally bounded (default max_depth=3, hard cap=5).
--   Full recursive expansion was too expensive/unpredictable on the live replica.
-- - Expansion follows tx inputs backward through source outputs.

\if :{?handle}
\else
\echo 'ERROR: pass -v handle=<name> (without leading $)'
\quit 1
\endif

\if :{?max_depth}
\else
\set max_depth 3
\endif

WITH params AS (
  SELECT LEAST(GREATEST(CAST(:'max_depth' AS integer), 1), 5) AS max_depth
), resolved AS (
  SELECT
    h.handle,
    h.handle_display,
    h.current_owner_address,
    h.current_owner_stake,
    h.tx_hash,
    h.block_no,
    h.slot_no,
    h.epoch_no,
    h.observed_at
  FROM explorer.handle_search h
  WHERE lower(h.handle) = lower(:'handle')
), owner_tx AS (
  SELECT
    r.*,
    t.id AS tx_id
  FROM resolved r
  JOIN public.tx t
    ON t.hash = decode(r.tx_hash, 'hex')
), depth1 AS (
  SELECT
    1 AS depth,
    ot.handle,
    ot.handle_display,
    ot.current_owner_address,
    ot.current_owner_stake,
    ot.tx_id AS target_tx_id,
    encode(t_target.hash::bytea, 'hex') AS target_tx_hash,
    txo_prev.tx_id AS source_tx_id,
    encode(t_prev.hash::bytea, 'hex') AS source_tx_hash,
    txo_prev.index AS source_tx_out_index,
    txo_prev.address AS source_address,
    sa_prev.view AS source_stake,
    txo_prev.value::text AS source_lovelace,
    b_prev.block_no AS source_block_no,
    b_prev.time AS source_block_time
  FROM owner_tx ot
  JOIN public.tx t_target
    ON t_target.id = ot.tx_id
  JOIN public.tx_in ti
    ON ti.tx_in_id = ot.tx_id
  JOIN public.tx_out txo_prev
    ON txo_prev.tx_id = ti.tx_out_id
   AND txo_prev.index = ti.tx_out_index
  JOIN public.tx t_prev
    ON t_prev.id = txo_prev.tx_id
  JOIN public.block b_prev
    ON b_prev.id = t_prev.block_id
  LEFT JOIN public.stake_address sa_prev
    ON sa_prev.id = txo_prev.stake_address_id
), depth2 AS (
  SELECT
    2 AS depth,
    d1.handle,
    d1.handle_display,
    d1.current_owner_address,
    d1.current_owner_stake,
    d1.source_tx_id AS target_tx_id,
    d1.source_tx_hash AS target_tx_hash,
    txo_prev.tx_id AS source_tx_id,
    encode(t_prev.hash::bytea, 'hex') AS source_tx_hash,
    txo_prev.index AS source_tx_out_index,
    txo_prev.address AS source_address,
    sa_prev.view AS source_stake,
    txo_prev.value::text AS source_lovelace,
    b_prev.block_no AS source_block_no,
    b_prev.time AS source_block_time
  FROM params p
  JOIN depth1 d1 ON p.max_depth >= 2
  JOIN public.tx_in ti
    ON ti.tx_in_id = d1.source_tx_id
  JOIN public.tx_out txo_prev
    ON txo_prev.tx_id = ti.tx_out_id
   AND txo_prev.index = ti.tx_out_index
  JOIN public.tx t_prev
    ON t_prev.id = txo_prev.tx_id
  JOIN public.block b_prev
    ON b_prev.id = t_prev.block_id
  LEFT JOIN public.stake_address sa_prev
    ON sa_prev.id = txo_prev.stake_address_id
), depth3 AS (
  SELECT
    3 AS depth,
    d2.handle,
    d2.handle_display,
    d2.current_owner_address,
    d2.current_owner_stake,
    d2.source_tx_id AS target_tx_id,
    d2.source_tx_hash AS target_tx_hash,
    txo_prev.tx_id AS source_tx_id,
    encode(t_prev.hash::bytea, 'hex') AS source_tx_hash,
    txo_prev.index AS source_tx_out_index,
    txo_prev.address AS source_address,
    sa_prev.view AS source_stake,
    txo_prev.value::text AS source_lovelace,
    b_prev.block_no AS source_block_no,
    b_prev.time AS source_block_time
  FROM params p
  JOIN depth2 d2 ON p.max_depth >= 3
  JOIN public.tx_in ti
    ON ti.tx_in_id = d2.source_tx_id
  JOIN public.tx_out txo_prev
    ON txo_prev.tx_id = ti.tx_out_id
   AND txo_prev.index = ti.tx_out_index
  JOIN public.tx t_prev
    ON t_prev.id = txo_prev.tx_id
  JOIN public.block b_prev
    ON b_prev.id = t_prev.block_id
  LEFT JOIN public.stake_address sa_prev
    ON sa_prev.id = txo_prev.stake_address_id
), depth4 AS (
  SELECT
    4 AS depth,
    d3.handle,
    d3.handle_display,
    d3.current_owner_address,
    d3.current_owner_stake,
    d3.source_tx_id AS target_tx_id,
    d3.source_tx_hash AS target_tx_hash,
    txo_prev.tx_id AS source_tx_id,
    encode(t_prev.hash::bytea, 'hex') AS source_tx_hash,
    txo_prev.index AS source_tx_out_index,
    txo_prev.address AS source_address,
    sa_prev.view AS source_stake,
    txo_prev.value::text AS source_lovelace,
    b_prev.block_no AS source_block_no,
    b_prev.time AS source_block_time
  FROM params p
  JOIN depth3 d3 ON p.max_depth >= 4
  JOIN public.tx_in ti
    ON ti.tx_in_id = d3.source_tx_id
  JOIN public.tx_out txo_prev
    ON txo_prev.tx_id = ti.tx_out_id
   AND txo_prev.index = ti.tx_out_index
  JOIN public.tx t_prev
    ON t_prev.id = txo_prev.tx_id
  JOIN public.block b_prev
    ON b_prev.id = t_prev.block_id
  LEFT JOIN public.stake_address sa_prev
    ON sa_prev.id = txo_prev.stake_address_id
), depth5 AS (
  SELECT
    5 AS depth,
    d4.handle,
    d4.handle_display,
    d4.current_owner_address,
    d4.current_owner_stake,
    d4.source_tx_id AS target_tx_id,
    d4.source_tx_hash AS target_tx_hash,
    txo_prev.tx_id AS source_tx_id,
    encode(t_prev.hash::bytea, 'hex') AS source_tx_hash,
    txo_prev.index AS source_tx_out_index,
    txo_prev.address AS source_address,
    sa_prev.view AS source_stake,
    txo_prev.value::text AS source_lovelace,
    b_prev.block_no AS source_block_no,
    b_prev.time AS source_block_time
  FROM params p
  JOIN depth4 d4 ON p.max_depth >= 5
  JOIN public.tx_in ti
    ON ti.tx_in_id = d4.source_tx_id
  JOIN public.tx_out txo_prev
    ON txo_prev.tx_id = ti.tx_out_id
   AND txo_prev.index = ti.tx_out_index
  JOIN public.tx t_prev
    ON t_prev.id = txo_prev.tx_id
  JOIN public.block b_prev
    ON b_prev.id = t_prev.block_id
  LEFT JOIN public.stake_address sa_prev
    ON sa_prev.id = txo_prev.stake_address_id
), all_depths AS (
  SELECT * FROM depth1
  UNION ALL SELECT * FROM depth2
  UNION ALL SELECT * FROM depth3
  UNION ALL SELECT * FROM depth4
  UNION ALL SELECT * FROM depth5
)
SELECT
  ad.depth,
  ad.handle,
  ad.handle_display,
  ad.current_owner_address,
  ad.current_owner_stake,
  ad.target_tx_hash,
  ad.source_tx_hash,
  ad.source_tx_out_index,
  ad.source_address,
  ad.source_stake,
  ad.source_lovelace,
  ad.source_block_no,
  ad.source_block_time
FROM all_depths ad
ORDER BY ad.depth, ad.source_block_no DESC, ad.source_tx_hash;

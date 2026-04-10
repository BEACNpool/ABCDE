-- Bridge-Input Creator Transaction Table
-- Step 1 of the amended next-step sequence (cross_entity_summary_amended_2026-04-06.md)
--
-- Purpose:
--   For each of the 381 UTxOs from the bridge/aggregator address
--   (Ae2tdPwUPEZHiXixpj6Xdju5jti25cY7QhjHZ3WiZypCsfEJoJx5fGujAKn)
--   that are direct inputs to clean three-way merge transaction 571f776c...,
--   identify the creator transaction, its time, its own feeder inputs,
--   and a preliminary value-type classification.
--
-- Outputs two result sets:
--   Result A: one row per bridge UTxO — creator tx metadata and value classification
--   Result B: one row per (bridge UTxO, feeder input) — full feeder address list
--
-- Seed-trace tagging (IOG/EMURGO/CF) is done in a subsequent local join step
--   against the published trace-edge CSVs, not here.
--
-- Connection: psql -h ${DB_HOST} -p 5432 -U codex_audit -d cexplorer_replica
-- Run:        \o outputs/cross_entity_evidence/bridge_input_creator_table_2026-04-08.csv
--             \copy (...) TO 'path' WITH CSV HEADER

-- ============================================================================
-- Result A: Bridge UTxO inventory with creator tx metadata
-- ============================================================================
\echo '--- RESULT A: bridge UTxO inventory ---'

WITH
target AS (
  SELECT tx.id AS tx_id
  FROM public.tx
  WHERE tx.hash = decode('571f776c0698c576ddecae145f97e7f284b82ebea70fbc924fa4e2a4a6258020', 'hex')
),
-- All inputs to 571f776c that come from the bridge address
bridge_consumed AS (
  SELECT
    ti.tx_out_id     AS creator_tx_id,
    ti.tx_out_index  AS creator_out_index,
    src.id           AS bridge_utxo_id,
    src.value        AS bridge_utxo_lovelace
  FROM target
  JOIN public.tx_in ti
    ON ti.tx_in_id = target.tx_id
  JOIN public.tx_out src
    ON src.tx_id = ti.tx_out_id
   AND src.index  = ti.tx_out_index
  WHERE src.address = 'Ae2tdPwUPEZHiXixpj6Xdju5jti25cY7QhjHZ3WiZypCsfEJoJx5fGujAKn'
)
SELECT
  bc.bridge_utxo_id,
  bc.creator_out_index,
  bc.bridge_utxo_lovelace,
  ROUND(bc.bridge_utxo_lovelace::numeric / 1000000, 6)  AS bridge_utxo_ada,
  CASE
    WHEN bc.bridge_utxo_lovelace % 1000000 = 0                            THEN 'round_ada'
    WHEN bc.bridge_utxo_lovelace % 100000  = 0                            THEN 'round_100k_lovelace'
    WHEN bc.bridge_utxo_lovelace > 1000000000000                          THEN 'large_bespoke'
    ELSE                                                                        'bespoke'
  END                                                    AS value_type,
  encode(ctx.hash, 'hex')                                AS creator_tx_hash,
  b.epoch_no                                             AS creator_epoch,
  b.time                                                 AS creator_time_utc,
  -- How many of the 381 bridge inputs share this same creator tx?
  COUNT(*) OVER (PARTITION BY bc.creator_tx_id)          AS bridge_outputs_from_same_creator
FROM bridge_consumed bc
JOIN public.tx    ctx ON ctx.id   = bc.creator_tx_id
JOIN public.block b   ON b.id     = ctx.block_id
ORDER BY b.epoch_no, ctx.id, bc.creator_out_index;

-- ============================================================================
-- Result B: Feeder inputs of each creator transaction
-- ============================================================================
\echo '--- RESULT B: feeder inputs of creator transactions ---'

WITH
target AS (
  SELECT tx.id AS tx_id
  FROM public.tx
  WHERE tx.hash = decode('571f776c0698c576ddecae145f97e7f284b82ebea70fbc924fa4e2a4a6258020', 'hex')
),
bridge_consumed AS (
  SELECT DISTINCT
    ti.tx_out_id     AS creator_tx_id,
    src.id           AS bridge_utxo_id
  FROM target
  JOIN public.tx_in ti
    ON ti.tx_in_id = target.tx_id
  JOIN public.tx_out src
    ON src.tx_id = ti.tx_out_id
   AND src.index  = ti.tx_out_index
  WHERE src.address = 'Ae2tdPwUPEZHiXixpj6Xdju5jti25cY7QhjHZ3WiZypCsfEJoJx5fGujAKn'
),
-- Deduplicated set of creator tx ids (a single creator tx may have produced
-- multiple of the 381 bridge outputs — only query its feeders once)
distinct_creators AS (
  SELECT DISTINCT creator_tx_id
  FROM bridge_consumed
)
SELECT
  encode(ctx.hash, 'hex')          AS creator_tx_hash,
  b.epoch_no                        AS creator_epoch,
  b.time                            AS creator_time_utc,
  encode(feed_tx.hash, 'hex')      AS feeder_tx_hash,
  feed_out.index                    AS feeder_out_index,
  feed_out.id                       AS feeder_tx_out_id,
  feed_out.address                  AS feeder_address,
  feed_out.value                    AS feeder_lovelace,
  ROUND(feed_out.value::numeric / 1000000, 6) AS feeder_ada,
  -- Flag if this feeder output came from the splitter address
  CASE
    WHEN feed_out.address = 'Ae2tdPwUPEZ6xYrxCgRDM2NQFM5oajHEoJN3i9ZVV2AbsbvxoJBjVu3yP7W' THEN 'splitter'
    WHEN feed_out.address = 'DdzFFzCqrhstmqBkaU98vdHu6PdqjqotmgudToWYEeRmQKDrn4cAgGv9EZKtu1DevLrMA1pdVazufUCK4zhFkUcQZ5Gm88mVHnrwmXvT' THEN 'sink'
    WHEN feed_out.address = 'Ae2tdPwUPEZHiXixpj6Xdju5jti25cY7QhjHZ3WiZypCsfEJoJx5fGujAKn' THEN 'bridge_self'
    ELSE 'other'
  END                               AS feeder_role_hint
FROM distinct_creators dc
JOIN public.tx ctx ON ctx.id = dc.creator_tx_id
JOIN public.block b ON b.id  = ctx.block_id
JOIN public.tx_in ti
  ON ti.tx_in_id = dc.creator_tx_id
JOIN public.tx feed_tx
  ON feed_tx.id  = ti.tx_out_id
JOIN public.tx_out feed_out
  ON feed_out.tx_id = ti.tx_out_id
 AND feed_out.index = ti.tx_out_index
ORDER BY b.epoch_no, ctx.id, feed_out.id;

-- ============================================================================
-- Result C: Creator transaction summary — distinct creator txs and their
--           aggregate input/output breakdown (sanity check)
-- ============================================================================
\echo '--- RESULT C: creator tx summary ---'

WITH
target AS (
  SELECT tx.id AS tx_id
  FROM public.tx
  WHERE tx.hash = decode('571f776c0698c576ddecae145f97e7f284b82ebea70fbc924fa4e2a4a6258020', 'hex')
),
bridge_consumed AS (
  SELECT DISTINCT
    ti.tx_out_id AS creator_tx_id
  FROM target
  JOIN public.tx_in ti ON ti.tx_in_id = target.tx_id
  JOIN public.tx_out src
    ON src.tx_id = ti.tx_out_id
   AND src.index  = ti.tx_out_index
  WHERE src.address = 'Ae2tdPwUPEZHiXixpj6Xdju5jti25cY7QhjHZ3WiZypCsfEJoJx5fGujAKn'
)
SELECT
  encode(ctx.hash, 'hex')                                            AS creator_tx_hash,
  b.epoch_no                                                          AS creator_epoch,
  b.time                                                              AS creator_time_utc,
  -- How many outputs did this creator tx send to the bridge address?
  COUNT(DISTINCT bridge_out.id)                                       AS bridge_outputs_created,
  SUM(bridge_out.value)                                               AS total_to_bridge_lovelace,
  ROUND(SUM(bridge_out.value)::numeric / 1000000, 6)                  AS total_to_bridge_ada,
  -- Total outputs of the creator tx (across all destinations)
  (SELECT COUNT(*) FROM public.tx_out WHERE tx_id = ctx.id)           AS creator_total_outputs,
  -- Total input value fed into this creator tx
  (SELECT SUM(feed_out.value)
   FROM public.tx_in ti2
   JOIN public.tx_out feed_out
     ON feed_out.tx_id = ti2.tx_out_id
    AND feed_out.index = ti2.tx_out_index
   WHERE ti2.tx_in_id = ctx.id)                                        AS creator_total_input_lovelace
FROM bridge_consumed bc
JOIN public.tx ctx ON ctx.id = bc.creator_tx_id
JOIN public.block b ON b.id  = ctx.block_id
JOIN public.tx_out bridge_out
  ON bridge_out.tx_id  = ctx.id
 AND bridge_out.address = 'Ae2tdPwUPEZHiXixpj6Xdju5jti25cY7QhjHZ3WiZypCsfEJoJx5fGujAKn'
GROUP BY ctx.id, ctx.hash, b.epoch_no, b.time
ORDER BY b.epoch_no, ctx.id;

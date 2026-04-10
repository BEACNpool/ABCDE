#!/usr/bin/env bash
# run_bridge_creator_step1.sh
#
# Executes bridge_input_creator_table_step1.sql against db-sync and saves
# the three result sets as separate CSVs ready for the local tagging step.
#
# Usage (from repo root):
#   bash scripts/run_bridge_creator_step1.sh
#
# Requires: psql in PATH, db-sync accessible at 192.168.86.118:5432

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT_DIR="$REPO_ROOT/outputs/cross_entity_evidence"
DB_HOST="192.168.86.118"
DB_PORT="5432"
DB_NAME="cexplorer_replica"
DB_USER="${PGUSER:-codex_audit}"
DATE="2026-04-08"

mkdir -p "$OUT_DIR"

echo "=== Step 1A: bridge UTxO inventory (Result A) ==="
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
  --no-psqlrc -A -F',' --pset=footer=off \
  -c "
WITH
target AS (
  SELECT tx.id AS tx_id
  FROM public.tx
  WHERE tx.hash = decode('571f776c0698c576ddecae145f97e7f284b82ebea70fbc924fa4e2a4a6258020', 'hex')
),
bridge_consumed AS (
  SELECT
    ti.tx_out_id     AS creator_tx_id,
    ti.tx_out_index  AS creator_out_index,
    src.id           AS bridge_utxo_id,
    src.value        AS bridge_utxo_lovelace
  FROM target
  JOIN public.tx_in ti    ON ti.tx_in_id = target.tx_id
  JOIN public.tx_out src  ON src.tx_id = ti.tx_out_id AND src.index = ti.tx_out_index
  WHERE src.address = 'Ae2tdPwUPEZHiXixpj6Xdju5jti25cY7QhjHZ3WiZypCsfEJoJx5fGujAKn'
)
SELECT
  bc.bridge_utxo_id,
  bc.creator_out_index,
  bc.bridge_utxo_lovelace,
  ROUND(bc.bridge_utxo_lovelace::numeric / 1000000, 6)  AS bridge_utxo_ada,
  CASE
    WHEN bc.bridge_utxo_lovelace % 1000000 = 0 THEN 'round_ada'
    WHEN bc.bridge_utxo_lovelace % 100000  = 0 THEN 'round_100k_lovelace'
    WHEN bc.bridge_utxo_lovelace > 1000000000000 THEN 'large_bespoke'
    ELSE 'bespoke'
  END                                                    AS value_type,
  encode(ctx.hash, 'hex')                                AS creator_tx_hash,
  b.epoch_no                                             AS creator_epoch,
  b.time                                                 AS creator_time_utc,
  COUNT(*) OVER (PARTITION BY bc.creator_tx_id)          AS bridge_outputs_from_same_creator
FROM bridge_consumed bc
JOIN public.tx    ctx ON ctx.id = bc.creator_tx_id
JOIN public.block b   ON b.id   = ctx.block_id
ORDER BY b.epoch_no, ctx.id, bc.creator_out_index;
" \
  > "$OUT_DIR/bridge_creator_inventory_result_a_${DATE}.csv"

echo "  Written: bridge_creator_inventory_result_a_${DATE}.csv"

echo "=== Step 1B: feeder inputs of creator transactions (Result B) ==="
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
  --no-psqlrc -A -F',' --pset=footer=off \
  -c "
WITH
target AS (
  SELECT tx.id AS tx_id
  FROM public.tx
  WHERE tx.hash = decode('571f776c0698c576ddecae145f97e7f284b82ebea70fbc924fa4e2a4a6258020', 'hex')
),
bridge_consumed AS (
  SELECT DISTINCT ti.tx_out_id AS creator_tx_id
  FROM target
  JOIN public.tx_in ti ON ti.tx_in_id = target.tx_id
  JOIN public.tx_out src ON src.tx_id = ti.tx_out_id AND src.index = ti.tx_out_index
  WHERE src.address = 'Ae2tdPwUPEZHiXixpj6Xdju5jti25cY7QhjHZ3WiZypCsfEJoJx5fGujAKn'
)
SELECT
  encode(ctx.hash, 'hex')                                AS creator_tx_hash,
  b.epoch_no                                             AS creator_epoch,
  b.time                                                 AS creator_time_utc,
  encode(feed_tx.hash, 'hex')                            AS feeder_tx_hash,
  feed_out.index                                         AS feeder_out_index,
  feed_out.id                                            AS feeder_tx_out_id,
  feed_out.address                                       AS feeder_address,
  feed_out.value                                         AS feeder_lovelace,
  ROUND(feed_out.value::numeric / 1000000, 6)            AS feeder_ada,
  CASE
    WHEN feed_out.address = 'Ae2tdPwUPEZ6xYrxCgRDM2NQFM5oajHEoJN3i9ZVV2AbsbvxoJBjVu3yP7W' THEN 'splitter'
    WHEN feed_out.address = 'DdzFFzCqrhstmqBkaU98vdHu6PdqjqotmgudToWYEeRmQKDrn4cAgGv9EZKtu1DevLrMA1pdVazufUCK4zhFkUcQZ5Gm88mVHnrwmXvT' THEN 'sink'
    WHEN feed_out.address = 'Ae2tdPwUPEZHiXixpj6Xdju5jti25cY7QhjHZ3WiZypCsfEJoJx5fGujAKn' THEN 'bridge_self'
    ELSE 'other'
  END                                                    AS feeder_role_hint
FROM bridge_consumed bc
JOIN public.tx ctx ON ctx.id = bc.creator_tx_id
JOIN public.block b ON b.id  = ctx.block_id
JOIN public.tx_in ti ON ti.tx_in_id = bc.creator_tx_id
JOIN public.tx feed_tx ON feed_tx.id = ti.tx_out_id
JOIN public.tx_out feed_out ON feed_out.tx_id = ti.tx_out_id AND feed_out.index = ti.tx_out_index
ORDER BY b.epoch_no, ctx.id, feed_out.id;
" \
  > "$OUT_DIR/bridge_creator_feeders_result_b_${DATE}.csv"

echo "  Written: bridge_creator_feeders_result_b_${DATE}.csv"

echo "=== Step 1C: creator transaction summary (Result C) ==="
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
  --no-psqlrc -A -F',' --pset=footer=off \
  -c "
WITH
target AS (
  SELECT tx.id AS tx_id
  FROM public.tx
  WHERE tx.hash = decode('571f776c0698c576ddecae145f97e7f284b82ebea70fbc924fa4e2a4a6258020', 'hex')
),
bridge_consumed AS (
  SELECT DISTINCT ti.tx_out_id AS creator_tx_id
  FROM target
  JOIN public.tx_in ti ON ti.tx_in_id = target.tx_id
  JOIN public.tx_out src ON src.tx_id = ti.tx_out_id AND src.index = ti.tx_out_index
  WHERE src.address = 'Ae2tdPwUPEZHiXixpj6Xdju5jti25cY7QhjHZ3WiZypCsfEJoJx5fGujAKn'
)
SELECT
  encode(ctx.hash, 'hex')                                              AS creator_tx_hash,
  b.epoch_no                                                            AS creator_epoch,
  b.time                                                                AS creator_time_utc,
  COUNT(DISTINCT bridge_out.id)                                         AS bridge_outputs_created,
  SUM(bridge_out.value)                                                 AS total_to_bridge_lovelace,
  ROUND(SUM(bridge_out.value)::numeric / 1000000, 6)                    AS total_to_bridge_ada,
  (SELECT COUNT(*) FROM public.tx_out WHERE tx_id = ctx.id)             AS creator_total_outputs,
  (SELECT SUM(feed_out2.value)
   FROM public.tx_in ti2
   JOIN public.tx_out feed_out2 ON feed_out2.tx_id = ti2.tx_out_id AND feed_out2.index = ti2.tx_out_index
   WHERE ti2.tx_in_id = ctx.id)                                         AS creator_total_input_lovelace
FROM bridge_consumed bc
JOIN public.tx ctx ON ctx.id = bc.creator_tx_id
JOIN public.block b ON b.id  = ctx.block_id
JOIN public.tx_out bridge_out
  ON bridge_out.tx_id   = ctx.id
 AND bridge_out.address = 'Ae2tdPwUPEZHiXixpj6Xdju5jti25cY7QhjHZ3WiZypCsfEJoJx5fGujAKn'
GROUP BY ctx.id, ctx.hash, b.epoch_no, b.time
ORDER BY b.epoch_no, ctx.id;
" \
  > "$OUT_DIR/bridge_creator_summary_result_c_${DATE}.csv"

echo "  Written: bridge_creator_summary_result_c_${DATE}.csv"
echo ""
echo "=== All three result sets done. ==="
echo ""
echo "Next: run seed-trace tagging against Result B:"
echo "  cd $REPO_ROOT"
echo "  python scripts/tag_creator_feeders_with_seed_traces.py"

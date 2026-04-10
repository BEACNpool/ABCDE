#!/usr/bin/env bash
# run_step5_triply_shared_dossiers.sh
#
# Step 5: Full transaction dossiers for the three triply-shared transactions:
#   197f9d27e49345cc085c9a2951d96c77f57f1cd82a71c095b7b7a3b36e74855d  (epoch 196)
#   34147ef46fd105ed39e3be63ac194e79622fb1bf9ea6e50313a0c3e0e6fd20c3  (epoch 239)
#   571f776c0698c576ddecae145f97e7f284b82ebea70fbc924fa4e2a4a6258020  (epoch 250)
#
# For each: full input table, full output table, per-address role hints.

set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT_DIR="$REPO_ROOT/outputs/cross_entity_evidence"
DB_HOST="192.168.86.118"
DB_PORT="5432"
DB_NAME="cexplorer_replica"
DB_USER="${PGUSER:-codex_audit}"
DATE="2026-04-08"

QUERY_METADATA="
WITH hashes AS (
  SELECT decode('197f9d27e49345cc085c9a2951d96c77f57f1cd82a71c095b7b7a3b36e74855d','hex') AS h
  UNION ALL SELECT decode('34147ef46fd105ed39e3be63ac194e79622fb1bf9ea6e50313a0c3e0e6fd20c3','hex')
  UNION ALL SELECT decode('571f776c0698c576ddecae145f97e7f284b82ebea70fbc924fa4e2a4a6258020','hex')
)
SELECT
  encode(tx.hash,'hex')          AS tx_hash,
  b.epoch_no,
  b.slot_no,
  b.time                         AS block_time_utc,
  tx.fee,
  tx.size                        AS tx_size_bytes,
  (SELECT COUNT(*) FROM public.tx_in WHERE tx_in_id = tx.id)   AS input_count,
  (SELECT COUNT(*) FROM public.tx_out WHERE tx_id   = tx.id)   AS output_count,
  (SELECT SUM(src.value) FROM public.tx_in ti JOIN public.tx_out src ON src.tx_id=ti.tx_out_id AND src.index=ti.tx_out_index WHERE ti.tx_in_id=tx.id) AS total_input_lovelace,
  (SELECT SUM(value)     FROM public.tx_out WHERE tx_id = tx.id) AS total_output_lovelace
FROM public.tx
JOIN public.block b ON b.id = tx.block_id
JOIN hashes ON hashes.h = tx.hash
ORDER BY b.epoch_no;"

QUERY_INPUTS="
WITH hashes AS (
  SELECT decode('197f9d27e49345cc085c9a2951d96c77f57f1cd82a71c095b7b7a3b36e74855d','hex') AS h
  UNION ALL SELECT decode('34147ef46fd105ed39e3be63ac194e79622fb1bf9ea6e50313a0c3e0e6fd20c3','hex')
  UNION ALL SELECT decode('571f776c0698c576ddecae145f97e7f284b82ebea70fbc924fa4e2a4a6258020','hex')
),
targets AS (
  SELECT tx.id, encode(tx.hash,'hex') AS tx_hash, b.epoch_no
  FROM public.tx JOIN public.block b ON b.id=tx.block_id JOIN hashes ON hashes.h=tx.hash
)
SELECT
  t.tx_hash,
  t.epoch_no,
  src.id                             AS input_tx_out_id,
  encode(src_tx.hash,'hex')          AS input_created_in_tx,
  src.index                          AS input_out_index,
  src.value                          AS lovelace,
  ROUND(src.value::numeric/1000000,6) AS ada,
  COALESCE(sa.view,'')               AS stake_address,
  src.address,
  CASE
    WHEN src.address='Ae2tdPwUPEZ6xYrxCgRDM2NQFM5oajHEoJN3i9ZVV2AbsbvxoJBjVu3yP7W' THEN 'splitter'
    WHEN src.address='Ae2tdPwUPEZHiXixpj6Xdju5jti25cY7QhjHZ3WiZypCsfEJoJx5fGujAKn' THEN 'bridge'
    WHEN src.address='DdzFFzCqrhstmqBkaU98vdHu6PdqjqotmgudToWYEeRmQKDrn4cAgGv9EZKtu1DevLrMA1pdVazufUCK4zhFkUcQZ5Gm88mVHnrwmXvT' THEN 'sink'
    ELSE 'other'
  END AS address_role
FROM targets t
JOIN public.tx_in ti ON ti.tx_in_id = t.id
JOIN public.tx src_tx ON src_tx.id = ti.tx_out_id
JOIN public.tx_out src ON src.tx_id=ti.tx_out_id AND src.index=ti.tx_out_index
LEFT JOIN public.stake_address sa ON sa.id = src.stake_address_id
ORDER BY t.epoch_no, src.id;"

QUERY_OUTPUTS="
WITH hashes AS (
  SELECT decode('197f9d27e49345cc085c9a2951d96c77f57f1cd82a71c095b7b7a3b36e74855d','hex') AS h
  UNION ALL SELECT decode('34147ef46fd105ed39e3be63ac194e79622fb1bf9ea6e50313a0c3e0e6fd20c3','hex')
  UNION ALL SELECT decode('571f776c0698c576ddecae145f97e7f284b82ebea70fbc924fa4e2a4a6258020','hex')
),
targets AS (
  SELECT tx.id, encode(tx.hash,'hex') AS tx_hash, b.epoch_no
  FROM public.tx JOIN public.block b ON b.id=tx.block_id JOIN hashes ON hashes.h=tx.hash
)
SELECT
  t.tx_hash,
  t.epoch_no,
  out.id                              AS output_tx_out_id,
  out.index                           AS output_index,
  out.value                           AS lovelace,
  ROUND(out.value::numeric/1000000,6) AS ada,
  COALESCE(sa.view,'')                AS stake_address,
  out.address,
  CASE WHEN ti2.tx_in_id IS NOT NULL THEN encode(next_tx.hash,'hex') ELSE 'UNSPENT' END AS spent_in_tx,
  CASE WHEN ti2.tx_in_id IS NOT NULL THEN nb.epoch_no ELSE NULL END AS spent_epoch
FROM targets t
JOIN public.tx_out out ON out.tx_id = t.id
LEFT JOIN public.stake_address sa ON sa.id = out.stake_address_id
LEFT JOIN public.tx_in ti2 ON ti2.tx_out_id=out.tx_id AND ti2.tx_out_index=out.index
LEFT JOIN public.tx next_tx ON next_tx.id = ti2.tx_in_id
LEFT JOIN public.block nb ON nb.id = next_tx.block_id
ORDER BY t.epoch_no, out.index;"

echo "=== Step 5A: Transaction metadata ==="
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
  --no-psqlrc -A -F',' --pset=footer=off \
  -c "$QUERY_METADATA" > "$OUT_DIR/triply_shared_tx_metadata_${DATE}.csv"
echo "  Written: triply_shared_tx_metadata_${DATE}.csv"

echo "=== Step 5B: Full input tables ==="
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
  --no-psqlrc -A -F',' --pset=footer=off \
  -c "$QUERY_INPUTS" > "$OUT_DIR/triply_shared_tx_inputs_${DATE}.csv"
echo "  Written: triply_shared_tx_inputs_${DATE}.csv"

echo "=== Step 5C: Full output tables ==="
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
  --no-psqlrc -A -F',' --pset=footer=off \
  -c "$QUERY_OUTPUTS" > "$OUT_DIR/triply_shared_tx_outputs_${DATE}.csv"
echo "  Written: triply_shared_tx_outputs_${DATE}.csv"
echo "=== Step 5 complete ==="

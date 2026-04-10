#!/usr/bin/env bash
# run_step3_splitter_bridge_expansion.sh
#
# Step 3: Expand the four verified splitter->bridge transactions into a
# full descendant graph. For each of the 4 bridge outputs that were
# created by those transactions, follow every spending transaction one
# additional hop and record all outputs with their destinations.
#
# Inputs (from splitter_to_bridge_forward_trace_2026-04-06.csv):
#   bridge_tx_out_ids: 5497972, 5550334, 5678309, 7061516
#   consuming txs:
#     963c761a2e798bfe2e35bf7d3bb888c1c178fb8407b9e431b93bcddbd7fe83d0
#     024ae3eaedfd98e5fa61b2650eab0ef1f40190da600a5cd8b2184a60856e8737
#     26174c832f6261944ac9074817b0dbe8ef7f81d55f193723672cfd0065d0bc04
#     988b65ca092d5d4254ce4313d593aafdd0bab57a59ac9059332e74087ea08858

set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT_DIR="$REPO_ROOT/outputs/cross_entity_evidence"
DB_HOST="${DB_HOST}"
DB_PORT="5432"
DB_NAME="cexplorer_replica"
DB_USER="${PGUSER:-codex_audit}"
DATE="2026-04-08"

echo "=== Step 3: Splitter->Bridge spending transactions — full output expansion ==="
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
  --no-psqlrc -A -F',' --pset=footer=off \
  -c "
WITH
-- The 4 transactions that spent the splitter->bridge outputs
consuming_hashes AS (
  SELECT decode('963c761a2e798bfe2e35bf7d3bb888c1c178fb8407b9e431b93bcddbd7fe83d0','hex') AS hash, 5497972::bigint AS origin_tx_out_id
  UNION ALL
  SELECT decode('024ae3eaedfd98e5fa61b2650eab0ef1f40190da600a5cd8b2184a60856e8737','hex'), 5550334
  UNION ALL
  SELECT decode('26174c832f6261944ac9074817b0dbe8ef7f81d55f193723672cfd0065d0bc04','hex'), 5678309
  UNION ALL
  SELECT decode('988b65ca092d5d4254ce4313d593aafdd0bab57a59ac9059332e74087ea08858','hex'), 7061516
),
targets AS (
  SELECT tx.id AS tx_id, encode(tx.hash,'hex') AS tx_hash, ch.origin_tx_out_id,
         b.epoch_no, b.time AS block_time
  FROM consuming_hashes ch
  JOIN public.tx ON tx.hash = ch.hash
  JOIN public.block b ON b.id = tx.block_id
)
-- All outputs produced by these 4 transactions
SELECT
  t.tx_hash                                              AS consuming_tx_hash,
  t.origin_tx_out_id                                     AS bridge_input_tx_out_id,
  t.epoch_no,
  t.block_time,
  out.id                                                 AS output_tx_out_id,
  out.index                                              AS output_index,
  out.value                                              AS lovelace,
  ROUND(out.value::numeric/1000000,6)                    AS ada,
  out.address,
  COALESCE(sa.view,'')                                   AS stake_address,
  -- Has this output been spent?
  CASE WHEN ti2.tx_in_id IS NOT NULL THEN encode(next_tx.hash,'hex') ELSE NULL END
                                                         AS spent_in_tx_hash,
  CASE WHEN ti2.tx_in_id IS NOT NULL THEN nb.epoch_no    ELSE NULL END
                                                         AS spent_epoch,
  CASE
    WHEN out.address = 'Ae2tdPwUPEZ6xYrxCgRDM2NQFM5oajHEoJN3i9ZVV2AbsbvxoJBjVu3yP7W' THEN 'splitter'
    WHEN out.address = 'Ae2tdPwUPEZHiXixpj6Xdju5jti25cY7QhjHZ3WiZypCsfEJoJx5fGujAKn' THEN 'bridge'
    WHEN out.address = 'DdzFFzCqrhstmqBkaU98vdHu6PdqjqotmgudToWYEeRmQKDrn4cAgGv9EZKtu1DevLrMA1pdVazufUCK4zhFkUcQZ5Gm88mVHnrwmXvT' THEN 'sink'
    ELSE 'other'
  END                                                    AS address_role
FROM targets t
JOIN public.tx_out out ON out.tx_id = t.tx_id
LEFT JOIN public.stake_address sa ON sa.id = out.stake_address_id
LEFT JOIN public.tx_in ti2 ON ti2.tx_out_id = out.tx_id AND ti2.tx_out_index = out.index
LEFT JOIN public.tx next_tx ON next_tx.id = ti2.tx_in_id
LEFT JOIN public.block nb ON nb.id = next_tx.block_id
ORDER BY t.origin_tx_out_id, out.index;
" > "$OUT_DIR/splitter_bridge_spending_expansion_${DATE}.csv"

echo "  Written: splitter_bridge_spending_expansion_${DATE}.csv"

echo "=== Step 3B: Full input context for the 4 consuming transactions ==="
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
  --no-psqlrc -A -F',' --pset=footer=off \
  -c "
WITH consuming_hashes AS (
  SELECT decode('963c761a2e798bfe2e35bf7d3bb888c1c178fb8407b9e431b93bcddbd7fe83d0','hex') AS hash
  UNION ALL SELECT decode('024ae3eaedfd98e5fa61b2650eab0ef1f40190da600a5cd8b2184a60856e8737','hex')
  UNION ALL SELECT decode('26174c832f6261944ac9074817b0dbe8ef7f81d55f193723672cfd0065d0bc04','hex')
  UNION ALL SELECT decode('988b65ca092d5d4254ce4313d593aafdd0bab57a59ac9059332e74087ea08858','hex')
),
targets AS (
  SELECT tx.id AS tx_id, encode(tx.hash,'hex') AS tx_hash
  FROM consuming_hashes ch JOIN public.tx ON tx.hash = ch.hash
)
SELECT
  t.tx_hash                                     AS consuming_tx_hash,
  src.id                                        AS input_tx_out_id,
  encode(src_tx.hash,'hex')                     AS input_created_in_tx,
  src.index                                     AS input_out_index,
  src.value                                     AS input_lovelace,
  ROUND(src.value::numeric/1000000,6)           AS input_ada,
  src.address                                   AS input_address,
  CASE
    WHEN src.address = 'Ae2tdPwUPEZ6xYrxCgRDM2NQFM5oajHEoJN3i9ZVV2AbsbvxoJBjVu3yP7W' THEN 'splitter'
    WHEN src.address = 'Ae2tdPwUPEZHiXixpj6Xdju5jti25cY7QhjHZ3WiZypCsfEJoJx5fGujAKn' THEN 'bridge'
    WHEN src.address = 'DdzFFzCqrhstmqBkaU98vdHu6PdqjqotmgudToWYEeRmQKDrn4cAgGv9EZKtu1DevLrMA1pdVazufUCK4zhFkUcQZ5Gm88mVHnrwmXvT' THEN 'sink'
    ELSE 'other'
  END                                           AS address_role
FROM targets t
JOIN public.tx_in ti ON ti.tx_in_id = t.tx_id
JOIN public.tx src_tx ON src_tx.id = ti.tx_out_id
JOIN public.tx_out src ON src.tx_id = ti.tx_out_id AND src.index = ti.tx_out_index
ORDER BY t.tx_hash, src.id;
" > "$OUT_DIR/splitter_bridge_consuming_inputs_${DATE}.csv"

echo "  Written: splitter_bridge_consuming_inputs_${DATE}.csv"
echo "=== Step 3 complete ==="

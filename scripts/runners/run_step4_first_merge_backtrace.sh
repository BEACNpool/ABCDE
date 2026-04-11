#!/usr/bin/env bash
# run_step4_first_merge_backtrace.sh
#
# Step 4: For the 521 cross-seed consuming transactions (cross_seed_consuming_transactions_2026-04-06.csv),
# identify the first convergence point for each pair and classify:
#   - clean merge (fresh inputs from both/all founders, no prior overlap)
#   - inherited overlap (converged because a shared ancestor was already in both traces)
#
# This script focuses on:
#   A) The top-value pairwise IOG+EMURGO consuming transactions (first-hop backtrace)
#   B) The top-value EMURGO+CF consuming transactions
#   C) Full input breakdown for all three clean two-way first merges
#      IOG+EMURGO: a71578ec... (epoch 95, 2019-01-15)
#      IOG+CF:     f9951db3... (epoch 193, 2020-05-18)
#      EMURGO+CF:  11c0765f... (epoch 195, 2020-05-27)

set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT_DIR="$REPO_ROOT/outputs/cross_entity_evidence"
DB_HOST="${DB_HOST}"
DB_PORT="5432"
DB_NAME="cexplorer_replica"
DB_USER="${PGUSER:-codex_audit}"
PSQL_BIN="${PSQL_BIN:-}"
DATE="2026-04-08"

mkdir -p "$OUT_DIR"

if [[ -z "$PSQL_BIN" ]]; then
  if command -v psql >/dev/null 2>&1; then
    PSQL_BIN="$(command -v psql)"
  elif command -v psql.exe >/dev/null 2>&1; then
    PSQL_BIN="$(command -v psql.exe)"
  elif [[ -x /mnt/c/Users/david/Apps/PostgreSQL/18/bin/psql.exe ]]; then
    PSQL_BIN="/mnt/c/Users/david/Apps/PostgreSQL/18/bin/psql.exe"
  else
    PSQL_BIN="psql"
  fi
fi

echo "=== Step 4A: First clean pairwise merge dossiers ==="
"$PSQL_BIN" -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
  --no-psqlrc -A -F',' --pset=footer=off \
  -c "
WITH first_merges AS (
  SELECT decode('a71578ec01f6cf39dbcf31351631159e3dd6fb99dd475783effbc65b90b8f0f9','hex') AS h, 'IOG+EMURGO_first_clean' AS label
  UNION ALL
  SELECT decode('f9951db326893e5c6cd94407e3d75be4928442aaf5809e435ca3e82c1983949d','hex'), 'IOG+CF_first_clean'
  UNION ALL
  SELECT decode('11c0765f430ecfffbdd1fb400d34bcd61d13af4c2e9332ce215f33de7e48d394','hex'), 'EMURGO+CF_first_clean'
)
SELECT
  fm.label,
  encode(tx.hash,'hex')  AS tx_hash,
  b.epoch_no,
  b.time                 AS block_time_utc,
  tx.fee,
  (SELECT COUNT(*) FROM public.tx_in  WHERE tx_in_id=tx.id) AS input_count,
  (SELECT COUNT(*) FROM public.tx_out WHERE tx_id=tx.id)    AS output_count,
  (SELECT SUM(src.value) FROM public.tx_in ti JOIN public.tx_out src ON src.tx_id=ti.tx_out_id AND src.index=ti.tx_out_index WHERE ti.tx_in_id=tx.id) AS total_input_lovelace
FROM first_merges fm
JOIN public.tx ON tx.hash = fm.h
JOIN public.block b ON b.id = tx.block_id
ORDER BY b.epoch_no;
" > "$OUT_DIR/first_clean_merges_metadata_${DATE}.csv"
echo "  Written: first_clean_merges_metadata_${DATE}.csv"

echo "=== Step 4B: Full input breakdown for first clean pairwise merges ==="
"$PSQL_BIN" -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
  --no-psqlrc -A -F',' --pset=footer=off \
  -c "
WITH first_merges AS (
  SELECT decode('a71578ec01f6cf39dbcf31351631159e3dd6fb99dd475783effbc65b90b8f0f9','hex') AS h, 'IOG+EMURGO_first_clean' AS label
  UNION ALL
  SELECT decode('f9951db326893e5c6cd94407e3d75be4928442aaf5809e435ca3e82c1983949d','hex'), 'IOG+CF_first_clean'
  UNION ALL
  SELECT decode('11c0765f430ecfffbdd1fb400d34bcd61d13af4c2e9332ce215f33de7e48d394','hex'), 'EMURGO+CF_first_clean'
),
targets AS (
  SELECT tx.id, fm.label, encode(tx.hash,'hex') AS tx_hash, b.epoch_no
  FROM first_merges fm JOIN public.tx ON tx.hash=fm.h JOIN public.block b ON b.id=tx.block_id
)
SELECT
  t.label,
  t.tx_hash,
  t.epoch_no,
  src.id                              AS input_tx_out_id,
  encode(src_tx.hash,'hex')           AS input_created_in_tx,
  src.index                           AS input_out_index,
  src.value                           AS lovelace,
  ROUND(src.value::numeric/1000000,6) AS ada,
  src.address
FROM targets t
JOIN public.tx_in ti ON ti.tx_in_id = t.id
JOIN public.tx src_tx ON src_tx.id = ti.tx_out_id
JOIN public.tx_out src ON src.tx_id=ti.tx_out_id AND src.index=ti.tx_out_index
ORDER BY t.epoch_no, src.id;
" > "$OUT_DIR/first_clean_merges_inputs_${DATE}.csv"
echo "  Written: first_clean_merges_inputs_${DATE}.csv"

echo "=== Step 4C: Cross-seed consuming transactions — top 50 by ADA value with input address breakdown ==="
# Load the annotated cross-seed CSV, rank the transactions by db-sync output value,
# and then get the full input breakdown for the top 50.
export REPO_ROOT OUT_DIR DATE DB_HOST DB_PORT DB_NAME DB_USER PSQL_BIN
python3 - <<'PYEOF'
import csv
import os
import subprocess
import sys
from pathlib import Path

root = Path(os.environ["REPO_ROOT"])
outdir = Path(os.environ["OUT_DIR"])
date = os.environ["DATE"]
db_host = os.environ["DB_HOST"]
db_port = os.environ["DB_PORT"]
db_name = os.environ["DB_NAME"]
db_user = os.environ["DB_USER"]
psql_bin = os.environ["PSQL_BIN"]

src = outdir / f"cross_seed_consuming_transactions_annotated_{date}.csv"
if not src.exists():
    print(f"[WARN] not found: {src}", file=sys.stderr)
    sys.exit(0)

hashes = []
with src.open(newline="", encoding="utf-8") as fh:
    for row in csv.DictReader(fh):
        h = row.get("dest_tx_hash", "").strip()
        if h:
            hashes.append(h)

hashes = sorted(set(hashes))
if not hashes:
    print("[WARN] no tx hashes found in annotated CSV", file=sys.stderr)
    sys.exit(0)

values_sql = ",\n  ".join(f"('{h}')" for h in hashes)
ranking_sql = outdir / f"_tmp_top50_cross_seed_value_{date}.sql"
ranking_csv = outdir / f"top50_cross_seed_tx_by_value_{date}.csv"
inputs_sql = outdir / f"_tmp_top50_cross_seed_inputs_{date}.sql"
inputs_csv = outdir / f"top50_cross_seed_tx_inputs_{date}.csv"

ranking_sql.write_text(
    f"""WITH target_hashes(hash_hex) AS (
  VALUES
  {values_sql}
),
target_txs AS (
  SELECT
    tx.id,
    encode(tx.hash,'hex') AS tx_hash,
    b.epoch_no,
    (SELECT SUM(value) FROM public.tx_out WHERE tx_id=tx.id) AS total_output_lovelace,
    ROUND((SELECT SUM(value) FROM public.tx_out WHERE tx_id=tx.id)::numeric/1000000,3) AS total_output_ada,
    (SELECT COUNT(*) FROM public.tx_in WHERE tx_in_id=tx.id) AS input_count,
    (SELECT COUNT(*) FROM public.tx_out WHERE tx_id=tx.id) AS output_count
  FROM public.tx
  JOIN public.block b ON b.id = tx.block_id
  JOIN target_hashes th ON tx.hash = decode(th.hash_hex,'hex')
)
SELECT
  tx_hash,
  epoch_no,
  total_output_lovelace,
  total_output_ada,
  input_count,
  output_count
FROM target_txs
ORDER BY total_output_lovelace DESC
LIMIT 50;
""",
    encoding="utf-8",
)

with ranking_csv.open("w", encoding="utf-8", newline="") as outfh:
    result = subprocess.run(
        [
            psql_bin,
            "-h", db_host,
            "-p", db_port,
            "-U", db_user,
            "-d", db_name,
            "--no-psqlrc",
            "-A",
            "-F,",
            "--pset=footer=off",
            "-f", str(ranking_sql),
        ],
        stdout=outfh,
        stderr=subprocess.PIPE,
        text=True,
        env=os.environ.copy(),
    )
if result.returncode != 0:
    print(f"[ERROR] ranking psql failed:\n{result.stderr}", file=sys.stderr)
    sys.exit(result.returncode)

top50_hashes = []
with ranking_csv.open(newline="", encoding="utf-8") as fh:
    for row in csv.DictReader(fh):
        if row.get("tx_hash"):
            top50_hashes.append(row["tx_hash"])

if not top50_hashes:
    print(f"[WARN] ranking output was empty: {ranking_csv}", file=sys.stderr)
    sys.exit(0)

top50_values_sql = ",\n  ".join(f"('{h}')" for h in top50_hashes)
inputs_sql.write_text(
    f"""WITH target_hashes(hash_hex) AS (
  VALUES
  {top50_values_sql}
),
targets AS (
  SELECT tx.id, encode(tx.hash,'hex') AS tx_hash, b.epoch_no, b.time AS block_time
  FROM public.tx
  JOIN public.block b ON b.id = tx.block_id
  JOIN target_hashes th ON tx.hash = decode(th.hash_hex,'hex')
)
SELECT
  t.tx_hash,
  t.epoch_no,
  t.block_time,
  src.id                              AS input_tx_out_id,
  encode(src_tx.hash,'hex')           AS input_created_in_tx,
  src.index                           AS input_out_index,
  src.value                           AS lovelace,
  ROUND(src.value::numeric/1000000,6) AS ada,
  src.address
FROM targets t
JOIN public.tx_in ti ON ti.tx_in_id = t.id
JOIN public.tx src_tx ON src_tx.id = ti.tx_out_id
JOIN public.tx_out src ON src.tx_id = ti.tx_out_id AND src.index = ti.tx_out_index
ORDER BY t.epoch_no, t.tx_hash, src.id;
""",
    encoding="utf-8",
)

with inputs_csv.open("w", encoding="utf-8", newline="") as outfh:
    result = subprocess.run(
        [
            psql_bin,
            "-h", db_host,
            "-p", db_port,
            "-U", db_user,
            "-d", db_name,
            "--no-psqlrc",
            "-A",
            "-F,",
            "--pset=footer=off",
            "-f", str(inputs_sql),
        ],
        stdout=outfh,
        stderr=subprocess.PIPE,
        text=True,
        env=os.environ.copy(),
    )
if result.returncode != 0:
    print(f"[ERROR] input breakdown psql failed:\n{result.stderr}", file=sys.stderr)
    sys.exit(result.returncode)

print(f"Written: {ranking_csv}", file=sys.stderr)
print(f"Written: {inputs_csv}", file=sys.stderr)
PYEOF

echo "=== Step 4 complete ==="

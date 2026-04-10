#!/usr/bin/env bash
# run_emurgo2_analysis.sh
#
# Gather on-chain evidence for the EMURGO_2 convergence and classification question.
# EMURGO_2 anchor: 5ec95a53fa3bb7dc56864bb6e75f369f00aa20e8d8cdc3b66b2fb88ec1b225ef
# Genesis ADA: 781,381,495
# First redemption destination: DdzFFzCqrhspiThx6UaeJASmHTbwbXp2FtdCkF9AU9QXPF9D8sUC7Fqrv9bmYkxradBbqMrSxukTTsqCPNPwRh5PHazdiwWTuJYVMMaf
# 100% stake-address overlap with main EMURGO trace (6,216 / 6,216 addresses)

set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT_DIR="$REPO_ROOT/outputs/cross_entity_evidence"
DB_HOST="192.168.86.118"
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

ANCHOR="5ec95a53fa3bb7dc56864bb6e75f369f00aa20e8d8cdc3b66b2fb88ec1b225ef"
EMURGO_ANCHOR="242608fc18552a4ac83adabcef7155f3b909e83d469ce89735db8f11d3637e38"

echo "=== EMURGO_2: Anchor transaction metadata ==="
"$PSQL_BIN" -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
  --no-psqlrc -A -F',' --pset=footer=off \
  -c "
SELECT
  encode(tx.hash,'hex') AS tx_hash,
  b.epoch_no,
  b.slot_no,
  b.time               AS block_time_utc,
  tx.fee,
  tx.size              AS tx_size_bytes,
  (SELECT COUNT(*)     FROM public.tx_in  WHERE tx_in_id = tx.id) AS input_count,
  (SELECT COUNT(*)     FROM public.tx_out WHERE tx_id    = tx.id) AS output_count,
  (SELECT SUM(value)   FROM public.tx_out WHERE tx_id    = tx.id) AS total_output_lovelace,
  ROUND((SELECT SUM(value) FROM public.tx_out WHERE tx_id=tx.id)::numeric/1000000,6) AS total_output_ada
FROM public.tx
JOIN public.block b ON b.id = tx.block_id
WHERE tx.hash = decode('$ANCHOR','hex');
" > "$OUT_DIR/emurgo2_anchor_metadata_${DATE}.csv"
echo "  Written: emurgo2_anchor_metadata_${DATE}.csv"

echo "=== EMURGO_2: Anchor transaction outputs ==="
"$PSQL_BIN" -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
  --no-psqlrc -A -F',' --pset=footer=off \
  -c "
WITH anchor AS (
  SELECT tx.id FROM public.tx WHERE tx.hash = decode('$ANCHOR','hex')
)
SELECT
  out.id      AS tx_out_id,
  out.index,
  out.value   AS lovelace,
  ROUND(out.value::numeric/1000000,6) AS ada,
  out.address,
  CASE WHEN ti.tx_in_id IS NOT NULL THEN encode(next_tx.hash,'hex') ELSE 'UNSPENT' END AS spent_in_tx,
  CASE WHEN ti.tx_in_id IS NOT NULL THEN nb.epoch_no ELSE NULL END AS spent_epoch
FROM anchor
JOIN public.tx_out out ON out.tx_id = anchor.id
LEFT JOIN public.tx_in ti ON ti.tx_out_id=out.tx_id AND ti.tx_out_index=out.index
LEFT JOIN public.tx next_tx ON next_tx.id = ti.tx_in_id
LEFT JOIN public.block nb ON nb.id = next_tx.block_id
ORDER BY out.index;
" > "$OUT_DIR/emurgo2_anchor_outputs_${DATE}.csv"
echo "  Written: emurgo2_anchor_outputs_${DATE}.csv"

echo "=== EMURGO_2 vs EMURGO: Compare anchor transaction structure ==="
"$PSQL_BIN" -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
  --no-psqlrc -A -F',' --pset=footer=off \
  -c "
WITH anchors AS (
  SELECT decode('$ANCHOR','hex')        AS h, 'EMURGO_2' AS entity
  UNION ALL
  SELECT decode('$EMURGO_ANCHOR','hex'),     'EMURGO'
)
SELECT
  a.entity,
  encode(tx.hash,'hex')    AS tx_hash,
  b.epoch_no,
  b.time                   AS block_time_utc,
  tx.fee,
  (SELECT COUNT(*) FROM public.tx_in  WHERE tx_in_id = tx.id)  AS input_count,
  (SELECT COUNT(*) FROM public.tx_out WHERE tx_id    = tx.id)  AS output_count,
  (SELECT SUM(value) FROM public.tx_out WHERE tx_id  = tx.id)  AS total_output_lovelace,
  ROUND((SELECT SUM(value) FROM public.tx_out WHERE tx_id=tx.id)::numeric/1000000,6) AS total_output_ada
FROM anchors a
JOIN public.tx ON tx.hash = a.h
JOIN public.block b ON b.id = tx.block_id
ORDER BY b.epoch_no;
" > "$OUT_DIR/emurgo2_vs_emurgo_anchor_comparison_${DATE}.csv"
echo "  Written: emurgo2_vs_emurgo_anchor_comparison_${DATE}.csv"

echo "=== EMURGO_2: First downstream spend transaction ==="
"$PSQL_BIN" -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
  --no-psqlrc -A -F',' --pset=footer=off \
  -c "
WITH anchor AS (
  SELECT tx.id AS tx_id FROM public.tx WHERE tx.hash = decode('$ANCHOR','hex')
),
anchor_outputs AS (
  SELECT out.id, out.index, out.value, out.address
  FROM anchor JOIN public.tx_out out ON out.tx_id = anchor.tx_id
),
first_spend AS (
  SELECT
    ao.id AS anchor_out_id,
    ao.value AS anchor_value,
    ao.address AS anchor_dest_address,
    ti.tx_in_id AS spend_tx_id
  FROM anchor_outputs ao
  JOIN public.tx_in ti ON ti.tx_out_id=(SELECT tx_id FROM anchor) AND ti.tx_out_index=ao.index
)
SELECT
  fs.anchor_out_id,
  fs.anchor_value AS lovelace,
  ROUND(fs.anchor_value::numeric/1000000,6) AS ada,
  fs.anchor_dest_address,
  encode(sp_tx.hash,'hex') AS first_spend_tx_hash,
  sp_b.epoch_no            AS first_spend_epoch,
  sp_b.time                AS first_spend_time_utc,
  (SELECT COUNT(*) FROM public.tx_in  WHERE tx_in_id = sp_tx.id) AS spend_tx_inputs,
  (SELECT COUNT(*) FROM public.tx_out WHERE tx_id    = sp_tx.id) AS spend_tx_outputs
FROM first_spend fs
JOIN public.tx sp_tx ON sp_tx.id = fs.spend_tx_id
JOIN public.block sp_b ON sp_b.id = sp_tx.block_id
ORDER BY fs.anchor_out_id;
" > "$OUT_DIR/emurgo2_first_spend_${DATE}.csv"
echo "  Written: emurgo2_first_spend_${DATE}.csv"

echo "=== EMURGO_2: Cross-entity overlap with main EMURGO trace (shared dest_tx_out_ids) ==="
# Count shared UTxO IDs between EMURGO_2 current_unspent and main EMURGO/IOG/CF current_unspent
export REPO_ROOT OUT_DIR DATE
python3 - <<'PYEOF'
import csv, os, sys

ROOT = os.environ["REPO_ROOT"]
OUTDIR = os.environ["OUT_DIR"]
DATE = os.environ["DATE"]

def load_ids(path):
    ids = set()
    if not os.path.exists(path):
        print(f"  [WARN] not found: {path}", file=sys.stderr)
        return ids
    with open(path) as f:
        for row in csv.DictReader(f):
            try: ids.add(int(row['dest_tx_out_id']))
            except: pass
    return ids

paths = {
    'IOG':      os.path.join(ROOT, 'datasets/genesis-founders/iog/current_unspent.csv'),
    'EMURGO':   os.path.join(ROOT, 'datasets/genesis-founders/emurgo/current_unspent.csv'),
    'CF':       os.path.join(ROOT, 'datasets/genesis-founders/cf/current_unspent.csv'),
    'EMURGO_2': os.path.join(ROOT, 'datasets/genesis-founders/emurgo2/current_unspent.csv'),
}

sets = {k: load_ids(v) for k, v in paths.items()}
for k, s in sets.items():
    print(f"  {k}: {len(s):,} dest_tx_out_ids", file=sys.stderr)

out_path = os.path.join(OUTDIR, f'emurgo2_frontier_overlap_{DATE}.csv')
rows = []
for a in ['IOG','EMURGO','CF']:
    overlap = sets['EMURGO_2'] & sets[a]
    rows.append({'pair': f'EMURGO_2 ∩ {a}', 'shared_dest_tx_out_id_count': len(overlap)})
    if overlap:
        # sample top 10 shared IDs
        sample = sorted(overlap)[:10]
        rows.append({'pair': f'  sample_ids', 'shared_dest_tx_out_id_count': str(sample)})

# all four
all4 = sets['EMURGO_2'] & sets['IOG'] & sets['EMURGO'] & sets['CF']
rows.append({'pair': 'EMURGO_2 ∩ IOG ∩ EMURGO ∩ CF', 'shared_dest_tx_out_id_count': len(all4)})

with open(out_path, 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['pair','shared_dest_tx_out_id_count'])
    w.writeheader()
    w.writerows(rows)
print(f"  Written: {out_path}", file=sys.stderr)
PYEOF

echo "=== EMURGO_2 analysis complete ==="

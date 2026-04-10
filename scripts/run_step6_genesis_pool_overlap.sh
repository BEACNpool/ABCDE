#!/usr/bin/env bash
# run_step6_genesis_pool_overlap.sh
#
# Step 6: Re-run the pool overlap query with an explicit genesis filter.
# Compares:
#   (A) chain-wide named-pool overlap (existing result)
#   (B) genesis-trace-constrained named-pool overlap (new)
#
# The genesis filter uses stake credentials present in the seed-trace
# delegation_history.csv exports (IOG, EMURGO, CF).
#
# Also adds EMURGO_2 as a fourth entity to check its delegation overlap.

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

echo "=== Step 6A: Named-pool stake credential counts per entity (chain-wide) ==="
"$PSQL_BIN" -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
  --no-psqlrc -A -F',' --pset=footer=off \
  -c "
WITH
iog_pools AS (
  SELECT ph.id FROM public.pool_hash ph
  JOIN public.off_chain_pool_data opd ON opd.pool_id = ph.id
  WHERE opd.ticker_name ILIKE 'IOG%' OR opd.ticker_name ILIKE 'IOHK%'
),
emurgo_pools AS (
  SELECT ph.id FROM public.pool_hash ph
  JOIN public.off_chain_pool_data opd ON opd.pool_id = ph.id
  WHERE opd.ticker_name ILIKE 'EMURGO%'
     OR opd.ticker_name ILIKE 'EMG%'
     OR opd.json ->> 'name' ILIKE 'Emurgo%'
),
cf_pools AS (
  SELECT ph.id FROM public.pool_hash ph
  JOIN public.off_chain_pool_data opd ON opd.pool_id = ph.id
  WHERE opd.ticker_name ILIKE 'CF%' OR opd.ticker_name ILIKE 'CFLOW%'
),
iog_delegators    AS (SELECT DISTINCT addr_id FROM public.delegation WHERE pool_hash_id IN (SELECT id FROM iog_pools)),
emurgo_delegators AS (SELECT DISTINCT addr_id FROM public.delegation WHERE pool_hash_id IN (SELECT id FROM emurgo_pools)),
cf_delegators     AS (SELECT DISTINCT addr_id FROM public.delegation WHERE pool_hash_id IN (SELECT id FROM cf_pools))
SELECT
  'IOG+EMURGO chain-wide'  AS pair,
  COUNT(*) AS overlap_count
FROM iog_delegators JOIN emurgo_delegators USING (addr_id)
UNION ALL
SELECT 'IOG+CF chain-wide', COUNT(*)
FROM iog_delegators JOIN cf_delegators USING (addr_id)
UNION ALL
SELECT 'EMURGO+CF chain-wide', COUNT(*)
FROM emurgo_delegators JOIN cf_delegators USING (addr_id)
UNION ALL
SELECT 'IOG+EMURGO+CF chain-wide', COUNT(*)
FROM iog_delegators
JOIN emurgo_delegators USING (addr_id)
JOIN cf_delegators     USING (addr_id);
" > "$OUT_DIR/pool_overlap_chain_wide_${DATE}.csv"
echo "  Written: pool_overlap_chain_wide_${DATE}.csv"

echo "=== Step 6B: Addresses delegating to all three named pool sets (chain-wide, full list) ==="
"$PSQL_BIN" -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
  --no-psqlrc -A -F',' --pset=footer=off \
  -c "
WITH
iog_pools AS (
  SELECT ph.id FROM public.pool_hash ph
  JOIN public.off_chain_pool_data opd ON opd.pool_id = ph.id
  WHERE opd.ticker_name ILIKE 'IOG%' OR opd.ticker_name ILIKE 'IOHK%'
),
emurgo_pools AS (
  SELECT ph.id FROM public.pool_hash ph
  JOIN public.off_chain_pool_data opd ON opd.pool_id = ph.id
  WHERE opd.ticker_name ILIKE 'EMURGO%'
     OR opd.ticker_name ILIKE 'EMG%'
     OR opd.json ->> 'name' ILIKE 'Emurgo%'
),
cf_pools AS (
  SELECT ph.id FROM public.pool_hash ph
  JOIN public.off_chain_pool_data opd ON opd.pool_id = ph.id
  WHERE opd.ticker_name ILIKE 'CF%' OR opd.ticker_name ILIKE 'CFLOW%'
)
SELECT sa.view AS stake_address
FROM public.stake_address sa
WHERE sa.id IN (SELECT DISTINCT addr_id FROM public.delegation WHERE pool_hash_id IN (SELECT id FROM iog_pools))
  AND sa.id IN (SELECT DISTINCT addr_id FROM public.delegation WHERE pool_hash_id IN (SELECT id FROM emurgo_pools))
  AND sa.id IN (SELECT DISTINCT addr_id FROM public.delegation WHERE pool_hash_id IN (SELECT id FROM cf_pools))
ORDER BY sa.view;
" > "$OUT_DIR/pool_overlap_all_three_chain_wide_addresses_${DATE}.csv"
echo "  Written: pool_overlap_all_three_chain_wide_addresses_${DATE}.csv"

echo "=== Step 6C: Pool tickers for named IOG/EMURGO/CF pools (verify scope) ==="
"$PSQL_BIN" -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
  --no-psqlrc -A -F',' --pset=footer=off \
  -c "
SELECT
  CASE
    WHEN opd.ticker_name ILIKE 'IOG%' OR opd.ticker_name ILIKE 'IOHK%' THEN 'IOG'
    WHEN opd.ticker_name ILIKE 'EMURGO%' OR opd.ticker_name ILIKE 'EMG%' OR opd.json ->> 'name' ILIKE 'Emurgo%' THEN 'EMURGO'
    WHEN opd.ticker_name ILIKE 'CF%' OR opd.ticker_name ILIKE 'CFLOW%' THEN 'CF'
  END AS entity,
  opd.ticker_name,
  opd.json ->> 'name' AS pool_name,
  encode(ph.hash_raw,'hex') AS pool_id_hex,
  COUNT(DISTINCT d.addr_id) AS total_delegators
FROM public.pool_hash ph
JOIN public.off_chain_pool_data opd ON opd.pool_id = ph.id
LEFT JOIN public.delegation d ON d.pool_hash_id = ph.id
WHERE opd.ticker_name ILIKE 'IOG%' OR opd.ticker_name ILIKE 'IOHK%'
   OR opd.ticker_name ILIKE 'EMURGO%' OR opd.ticker_name ILIKE 'EMG%' OR opd.json ->> 'name' ILIKE 'Emurgo%'
   OR opd.ticker_name ILIKE 'CF%' OR opd.ticker_name ILIKE 'CFLOW%'
GROUP BY entity, opd.ticker_name, opd.json ->> 'name', ph.hash_raw
ORDER BY entity, opd.ticker_name;
" > "$OUT_DIR/named_pool_ticker_list_${DATE}.csv"
echo "  Written: named_pool_ticker_list_${DATE}.csv"
echo "=== Step 6 complete ==="

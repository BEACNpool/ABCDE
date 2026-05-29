#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ABCDE_SSH="${ABCDE_SSH:-abcde@192.168.86.118}"
DB_NAME="${DB_NAME:-cexplorer_replica}"
SCHEMA="${TRACE_STAGE_SCHEMA:-abcde_forensics_stage_founders_depth14}"
OUT_DIR="${1:-$REPO_ROOT/data/small}"
mkdir -p "$OUT_DIR"
case "$SCHEMA" in
  *[!a-zA-Z0-9_]*|'') echo "unsafe TRACE_STAGE_SCHEMA: $SCHEMA" >&2; exit 2 ;;
esac

run_sql() {
  local out="$1"
  ssh "$ABCDE_SSH" "sudo -n -u postgres psql -q -v ON_ERROR_STOP=1 -d '$DB_NAME' --csv -f -" > "$out"
}

cat <<SQL | run_sql "$OUT_DIR/iog_current_bag_depth14_summary.csv"
WITH iog AS (
  SELECT root_seed_id, min_depth, tx_id, tx_out_index, value_lovelace, address, stake_address
  FROM "$SCHEMA".trace_utxos
  WHERE root_seed_id='iog'
), current_iog AS (
  SELECT i.*
  FROM iog i
  LEFT JOIN tx_in spent ON spent.tx_out_id=i.tx_id AND spent.tx_out_index=i.tx_out_index
  WHERE spent.tx_in_id IS NULL
)
SELECT
  count(*) AS current_utxo_rows,
  sum(value_lovelace)/1000000.0 AS current_ada,
  min(min_depth) AS min_depth,
  max(min_depth) AS max_depth,
  count(DISTINCT stake_address) FILTER (WHERE stake_address IS NOT NULL) AS distinct_stake_addresses,
  count(*) FILTER (WHERE stake_address IS NULL) AS byron_or_no_stake_utxos,
  sum(value_lovelace) FILTER (WHERE stake_address IS NULL)/1000000.0 AS byron_or_no_stake_ada,
  sum(value_lovelace) FILTER (WHERE stake_address IS NOT NULL)/1000000.0 AS shelley_staked_ada
FROM current_iog;
SQL

cat <<SQL | run_sql "$OUT_DIR/iog_current_bag_depth14_by_depth.csv"
WITH iog AS (
  SELECT min_depth, tx_id, tx_out_index, value_lovelace
  FROM "$SCHEMA".trace_utxos
  WHERE root_seed_id='iog'
), current_iog AS (
  SELECT i.*
  FROM iog i
  LEFT JOIN tx_in spent ON spent.tx_out_id=i.tx_id AND spent.tx_out_index=i.tx_out_index
  WHERE spent.tx_in_id IS NULL
)
SELECT min_depth, count(*) AS current_utxos, sum(value_lovelace)/1000000.0 AS current_ada
FROM current_iog
GROUP BY min_depth
ORDER BY min_depth;
SQL

cat <<SQL | run_sql "$OUT_DIR/iog_current_bag_depth14_top_stake.csv"
WITH iog AS (
  SELECT min_depth, tx_id, tx_out_index, value_lovelace, stake_address
  FROM "$SCHEMA".trace_utxos
  WHERE root_seed_id='iog'
), current_iog AS (
  SELECT i.*
  FROM iog i
  LEFT JOIN tx_in spent ON spent.tx_out_id=i.tx_id AND spent.tx_out_index=i.tx_out_index
  WHERE spent.tx_in_id IS NULL
)
SELECT stake_address, count(*) AS current_utxos, sum(value_lovelace)/1000000.0 AS current_ada, min(min_depth) AS min_depth, max(min_depth) AS max_depth
FROM current_iog
WHERE stake_address IS NOT NULL
GROUP BY stake_address
ORDER BY sum(value_lovelace) DESC
LIMIT 50;
SQL

cat <<'SQL' | run_sql "$OUT_DIR/iog_pool_state_validation.csv"
WITH pools(pool_view, label) AS (VALUES
 ('pool1mxqjlrfskhd5kql9kak06fpdh8xjwc76gec76p3taqy2qmfzs5z','IOG1'),
 ('pool10dwjth7esfw5gc036vu6l6csnvn6elqax0d3kh8t65rxyewk2g3','IOG2')
), tip AS (
 SELECT epoch_no, block_no, time FROM block ORDER BY id DESC LIMIT 1
), ph AS (
 SELECT p.label, h.id AS pool_hash_id, h.view AS pool_view, encode(h.hash_raw,'hex') AS pool_hash_hex
 FROM pools p JOIN pool_hash h ON h.view=p.pool_view
), latest_update AS (
 SELECT DISTINCT ON (pu.hash_id)
   pu.hash_id, pu.active_epoch_no, pu.pledge, pu.margin, pu.fixed_cost,
   encode(tx.hash,'hex') AS update_tx_hash, b.time AS update_time,
   pmr.url AS metadata_url, encode(pmr.hash,'hex') AS metadata_hash_hex, ocpd.ticker_name
 FROM pool_update pu
 JOIN tx ON tx.id=pu.registered_tx_id
 JOIN block b ON b.id=tx.block_id
 LEFT JOIN pool_metadata_ref pmr ON pmr.id=pu.meta_id
 LEFT JOIN off_chain_pool_data ocpd ON ocpd.pmr_id=pmr.id
 ORDER BY pu.hash_id, pu.active_epoch_no DESC, pu.id DESC
), latest_retire AS (
 SELECT DISTINCT ON (pr.hash_id)
   pr.hash_id, pr.retiring_epoch, encode(tx.hash,'hex') AS retire_tx_hash, b.time AS retire_time
 FROM pool_retire pr
 JOIN tx ON tx.id=pr.announced_tx_id
 JOIN block b ON b.id=tx.block_id
 ORDER BY pr.hash_id, pr.retiring_epoch DESC, pr.id DESC
), latest_epoch_stake AS (
 SELECT es.pool_id, es.epoch_no, sum(es.amount) AS active_stake_lovelace, count(DISTINCT es.addr_id) AS stake_credentials
 FROM epoch_stake es
 JOIN (SELECT max(epoch_no) AS epoch_no FROM epoch_stake) me ON me.epoch_no=es.epoch_no
 GROUP BY es.pool_id, es.epoch_no
)
SELECT
 ph.label,
 ph.pool_view,
 tip.epoch_no AS tip_epoch,
 tip.block_no AS tip_block,
 tip.time AS tip_time_utc,
 lu.active_epoch_no AS latest_update_active_epoch,
 lu.ticker_name,
 lu.metadata_url,
 lu.pledge/1000000.0 AS pledge_ada,
 lu.margin,
 lr.retiring_epoch,
 lr.retire_time AS retire_announced_time,
 CASE WHEN lr.retiring_epoch IS NOT NULL AND lr.retiring_epoch <= tip.epoch_no THEN true ELSE false END AS is_retired_at_tip,
 les.epoch_no AS latest_epoch_stake_epoch,
 les.active_stake_lovelace/1000000.0 AS latest_epoch_active_stake_ada,
 les.stake_credentials AS latest_epoch_stake_credentials
FROM ph
CROSS JOIN tip
LEFT JOIN latest_update lu ON lu.hash_id=ph.pool_hash_id
LEFT JOIN latest_retire lr ON lr.hash_id=ph.pool_hash_id
LEFT JOIN latest_epoch_stake les ON les.pool_id=ph.pool_hash_id
ORDER BY ph.label;
SQL

echo "wrote ${OUT_DIR#$REPO_ROOT/}/iog_current_bag_depth14_summary.csv"
echo "wrote ${OUT_DIR#$REPO_ROOT/}/iog_current_bag_depth14_by_depth.csv"
echo "wrote ${OUT_DIR#$REPO_ROOT/}/iog_current_bag_depth14_top_stake.csv"
echo "wrote ${OUT_DIR#$REPO_ROOT/}/iog_pool_state_validation.csv"

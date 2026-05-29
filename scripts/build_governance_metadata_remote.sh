#!/usr/bin/env bash
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ABCDE_SSH="${ABCDE_SSH:-abcde@192.168.86.118}"
DB_NAME="${DB_NAME:-cexplorer_replica}"
POOL_OUT="$REPO_ROOT/data/small/governance_pool_metadata.csv"
DREP_OUT="$REPO_ROOT/data/small/governance_drep_metadata.csv"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT
python3 "$REPO_ROOT/scripts/build_governance_metadata_queries.py" > "$TMP_DIR/all.sql"
awk '/-- POOL_METADATA_SQL_START/{flag=1;next}/-- DREP_METADATA_SQL_START/{flag=0}flag' "$TMP_DIR/all.sql" > "$TMP_DIR/pool.sql"
awk '/-- DREP_METADATA_SQL_START/{flag=1;next}flag' "$TMP_DIR/all.sql" > "$TMP_DIR/drep.sql"
ssh "$ABCDE_SSH" "sudo -n -u postgres psql -v ON_ERROR_STOP=1 -d '$DB_NAME' --csv -f -" < "$TMP_DIR/pool.sql" > "$POOL_OUT"
ssh "$ABCDE_SSH" "sudo -n -u postgres psql -v ON_ERROR_STOP=1 -d '$DB_NAME' --csv -f -" < "$TMP_DIR/drep.sql" > "$DREP_OUT"
echo "wrote ${POOL_OUT#$REPO_ROOT/}"
echo "wrote ${DREP_OUT#$REPO_ROOT/}"

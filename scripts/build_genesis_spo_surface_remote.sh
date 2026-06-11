#!/usr/bin/env bash
# Build the Genesis-to-SPO delegation surface, pool operator linkage, and
# governance actions catalog from the ABCDE warehouse.
#
# Outputs:
#   data/release/genesis_current_spo_surface.csv   (full surface; release asset)
#   data/small/governance_genesis_pool_operator_links.csv
#   data/small/governance_actions_catalog.csv
# Then run scripts/build_genesis_spo_rollups.py for the committed rollups.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ -z "${ABCDE_SSH:-}" ]]; then
  echo "Set ABCDE_SSH to the SSH target for the db-sync warehouse host." >&2
  exit 2
fi
DB_NAME="${DB_NAME:-cexplorer_replica}"
SCHEMA="${TRACE_STAGE_SCHEMA:-abcde_forensics_stage_founders_depth14}"
SMALL_DIR="${SMALL_DIR:-$REPO_ROOT/data/small}"
RELEASE_DIR="${RELEASE_DIR:-$REPO_ROOT/data/release}"

case "$SCHEMA" in
  *[!a-zA-Z0-9_]*|'') echo "unsafe TRACE_STAGE_SCHEMA: $SCHEMA" >&2; exit 2 ;;
esac

mkdir -p "$SMALL_DIR" "$RELEASE_DIR"

run_query() {
  local sql_path="$1"
  local out_path="$2"
  ssh "$ABCDE_SSH" "sudo -n -u postgres psql -q -v ON_ERROR_STOP=1 -v stage_schema='$SCHEMA' -d '$DB_NAME' --csv -f -" \
    < "$REPO_ROOT/$sql_path" > "$out_path"
  echo "wrote ${out_path#$REPO_ROOT/}"
}

run_query "sql/30_behavior/genesis_current_spo_surface.sql" "$RELEASE_DIR/genesis_current_spo_surface.csv"
run_query "sql/30_behavior/genesis_pool_operator_links.sql" "$SMALL_DIR/governance_genesis_pool_operator_links.csv"
run_query "sql/30_behavior/governance_actions_catalog.sql" "$SMALL_DIR/governance_actions_catalog.csv"
run_query "sql/30_behavior/genesis_delegation_history.sql" "$RELEASE_DIR/genesis_delegation_history.csv"
run_query "sql/30_behavior/genesis_delegation_timeline.sql" "$SMALL_DIR/governance_genesis_delegation_timeline.csv"

python3 "$REPO_ROOT/scripts/build_genesis_spo_rollups.py"

#!/usr/bin/env bash
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

ssh "$ABCDE_SSH" "sudo -n -u postgres psql -q -v ON_ERROR_STOP=1 -v stage_schema='$SCHEMA' -d '$DB_NAME' -f -" \
  < "$REPO_ROOT/sql/30_behavior/build_genesis_governance_surface_tables.sql"

run_query "sql/30_behavior/genesis_current_governance_surface.sql" "$RELEASE_DIR/genesis_current_governance_surface.csv"
run_query "sql/30_behavior/drep_proposal_votes.sql" "$RELEASE_DIR/governance_drep_votes.csv"

python3 "$REPO_ROOT/scripts/build_genesis_drep_behavior_rollups.py"
python3 "$REPO_ROOT/scripts/build_public_artifact_manifest.py"

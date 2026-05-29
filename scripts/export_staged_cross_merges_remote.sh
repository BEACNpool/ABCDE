#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ABCDE_SSH="${ABCDE_SSH:-abcde@192.168.86.118}"
DB_NAME="${DB_NAME:-cexplorer_replica}"
SCHEMA="${TRACE_STAGE_SCHEMA:-abcde_forensics_stage}"
OUT="${1:-$REPO_ROOT/data/small/staged_cross_entity_merges.csv}"
mkdir -p "$(dirname "$OUT")"
case "$SCHEMA" in
  *[!a-zA-Z0-9_]*|'') echo "unsafe TRACE_STAGE_SCHEMA: $SCHEMA" >&2; exit 2 ;;
esac
ssh "$ABCDE_SSH" "sudo -n -u postgres psql -q -v ON_ERROR_STOP=1 -d '$DB_NAME' --csv -c \"SELECT merge_tx_hash, epoch_no, block_no, block_time_utc, root_combo, root_count, traced_input_rows, traced_input_lovelace, min_input_depth, max_input_depth FROM \\\"$SCHEMA\\\".cross_entity_merges ORDER BY epoch_no, block_no, merge_tx_hash;\"" > "$OUT"
echo "wrote ${OUT#$REPO_ROOT/}"

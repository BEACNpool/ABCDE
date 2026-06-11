#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ -z "${ABCDE_SSH:-}" ]]; then
  echo "Set ABCDE_SSH to the SSH target for the db-sync warehouse host." >&2
  exit 2
fi
DB_NAME="${DB_NAME:-cexplorer_replica}"
SCHEMA="${TRACE_STAGE_SCHEMA:-abcde_forensics_stage}"
DEPTH="${TRACE_MAX_DEPTH:-10}"
FOUNDERS_ONLY="${FOUNDERS_ONLY:-0}"
OUT="${1:-$REPO_ROOT/data/small/staged_trace_depth${DEPTH}_summary.csv}"
mkdir -p "$(dirname "$OUT")"
args=(--schema "$SCHEMA" --max-depth "$DEPTH")
if [[ "$FOUNDERS_ONLY" == "1" || "$FOUNDERS_ONLY" == "true" ]]; then
  args+=(--founders-only)
fi
python3 "$REPO_ROOT/scripts/build_staged_trace_sql.py" "${args[@]}" |
  ssh "$ABCDE_SSH" "sudo -n -u postgres psql -q -v ON_ERROR_STOP=1 -d '$DB_NAME' --csv -f -" > "$OUT"
echo "wrote ${OUT#$REPO_ROOT/}"

#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ -z "${ABCDE_SSH:-}" ]]; then
  echo "Set ABCDE_SSH to the SSH target for the db-sync warehouse host." >&2
  exit 2
fi
DB_NAME="${DB_NAME:-cexplorer_replica}"
DEPTH="${TRACE_DEPTH:-3}"
OUT="${1:-$REPO_ROOT/data/small/bounded_trace_depth${DEPTH}_db.csv}"
mkdir -p "$(dirname "$OUT")"
TRACE_DEPTH="$DEPTH" python3 "$REPO_ROOT/scripts/build_bounded_trace_query.py" |
  ssh "$ABCDE_SSH" "sudo -n -u postgres psql -v ON_ERROR_STOP=1 -d '$DB_NAME' --csv -f -" > "$OUT"
echo "wrote ${OUT#$REPO_ROOT/}"

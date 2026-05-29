#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ABCDE_SSH="${ABCDE_SSH:-abcde@192.168.86.118}"
DB_NAME="${DB_NAME:-cexplorer_replica}"
DEPTH="${TRACE_DEPTH:-3}"
OUT="${1:-$REPO_ROOT/data/small/bounded_trace_depth${DEPTH}_db.csv}"
mkdir -p "$(dirname "$OUT")"
TRACE_DEPTH="$DEPTH" python3 "$REPO_ROOT/scripts/build_bounded_trace_query.py" |
  ssh "$ABCDE_SSH" "sudo -n -u postgres psql -v ON_ERROR_STOP=1 -d '$DB_NAME' --csv -f -" > "$OUT"
echo "wrote ${OUT#$REPO_ROOT/}"

#!/usr/bin/env bash
# Build seed output CSV receipt from ABCDE/db-sync.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ABCDE_SSH="${ABCDE_SSH:-abcde@192.168.86.118}"
DB_NAME="${DB_NAME:-cexplorer_replica}"
OUT="${1:-$REPO_ROOT/data/small/seed_outputs_db.csv}"
mkdir -p "$(dirname "$OUT")"
python3 "$REPO_ROOT/scripts/build_seed_outputs_query.py" |
  ssh "$ABCDE_SSH" "sudo -n -u postgres psql -v ON_ERROR_STOP=1 -d '$DB_NAME' --csv -f -" > "$OUT"
echo "wrote ${OUT#$REPO_ROOT/}"

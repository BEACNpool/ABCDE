#!/usr/bin/env bash
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ -z "${ABCDE_SSH:-}" ]]; then
  echo "Set ABCDE_SSH to the SSH target for the db-sync warehouse host." >&2
  exit 2
fi
DB_NAME="${DB_NAME:-cexplorer_replica}"
OUT="${1:-$REPO_ROOT/data/small/trace_stake_credentials_db.csv}"
mkdir -p "$(dirname "$OUT")"
python3 "$REPO_ROOT/scripts/build_trace_stake_credentials_query.py" |
  ssh "$ABCDE_SSH" "sudo -n -u postgres psql -v ON_ERROR_STOP=1 -d '$DB_NAME' --csv -f -" > "$OUT"
echo "wrote ${OUT#$REPO_ROOT/}"

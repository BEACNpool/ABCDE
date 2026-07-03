#!/usr/bin/env bash
# Extract live-tip genesis control indicators + shared-cert cohorts from the
# ABCDE warehouse, then run the deterministic local classifier.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ -z "${ABCDE_SSH:-}" ]]; then
  echo "Set ABCDE_SSH to the SSH target for the db-sync warehouse host." >&2
  exit 2
fi
DB_NAME="${DB_NAME:-cexplorer_replica}"
PSQL="sudo -n -u postgres psql -v ON_ERROR_STOP=1 -d '$DB_NAME' --csv -f -"

python3 "$REPO_ROOT/scripts/build_genesis_control_indicators_query.py" |
  ssh "$ABCDE_SSH" "$PSQL" > "$REPO_ROOT/data/small/genesis_control_indicators_raw.csv"
echo "wrote data/small/genesis_control_indicators_raw.csv"

python3 "$REPO_ROOT/scripts/build_genesis_control_indicators_query.py" --cohorts |
  ssh "$ABCDE_SSH" "$PSQL" > "$REPO_ROOT/data/small/genesis_control_cert_cohorts.csv"
echo "wrote data/small/genesis_control_cert_cohorts.csv"

python3 "$REPO_ROOT/scripts/build_genesis_control_classification.py"

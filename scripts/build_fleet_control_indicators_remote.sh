#!/usr/bin/env bash
# Classify the F13 operator fleet (the 81 non-cohort stake keys that share
# withdrawal transactions with the F11 cohort) through the SAME control-
# indicator SQL and classifier as the genesis set, but written to a separate
# fleet_control_* output so the two surfaces can be compared.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
: "${ABCDE_SSH:?Set ABCDE_SSH to the warehouse SSH target}"
DB_NAME="${DB_NAME:-cexplorer_replica}"
PSQL="sudo -n -u postgres psql -v ON_ERROR_STOP=1 -d '$DB_NAME' --csv -f -"

export ABCDE_CONTROL_ROOTS="data/small/f11_downstream_fleet.csv:stake_address"
export ABCDE_CONTROL_PREFIX="fleet_control"

python3 "$REPO_ROOT/scripts/build_genesis_control_indicators_query.py" |
  ssh "$ABCDE_SSH" "$PSQL" > "$REPO_ROOT/data/small/fleet_control_indicators_raw.csv"
echo "wrote data/small/fleet_control_indicators_raw.csv"

python3 "$REPO_ROOT/scripts/build_genesis_control_indicators_query.py" --cohorts |
  ssh "$ABCDE_SSH" "$PSQL" > "$REPO_ROOT/data/small/fleet_control_cert_cohorts.csv"
echo "wrote data/small/fleet_control_cert_cohorts.csv"

python3 "$REPO_ROOT/scripts/build_genesis_control_classification.py"

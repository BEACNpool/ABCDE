#!/usr/bin/env bash
# F15: discover the full forward-reachable co-plumbing component from the 8 F11
# cohort keys (BFS to fixpoint), then classify every component key through the
# same control-indicator pipeline (component_control_* output).
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
: "${ABCDE_SSH:?Set ABCDE_SSH to the warehouse SSH target}"
DB_NAME="${DB_NAME:-cexplorer_replica}"
SMALL="$REPO_ROOT/data/small"

# 1. Component discovery. stderr carries the round-by-round NOTICE growth log;
#    keep it on the terminal but strip it out of the CSV, then slice after the
#    @@COMPONENT sentinel.
raw="$(ssh "$ABCDE_SSH" \
  "sudo -n -u postgres psql -q -v ON_ERROR_STOP=1 -d '$DB_NAME' -f -" \
  < "$REPO_ROOT/sql/10_findings/f15_cowithdrawal_component.sql" 2> >(grep -i round >&2))"
printf '%s\n' "$raw" | awk '/@@COMPONENT/{f=1;next} f' \
  > "$SMALL/f15_cowithdrawal_component.csv"
echo "wrote data/small/f15_cowithdrawal_component.csv ($(($(wc -l < "$SMALL/f15_cowithdrawal_component.csv") - 1)) keys)"

# 2. Classify the component through the shared pipeline.
export ABCDE_CONTROL_ROOTS="data/small/f15_cowithdrawal_component.csv:stake_address"
export ABCDE_CONTROL_PREFIX="component_control"
PSQL="sudo -n -u postgres psql -v ON_ERROR_STOP=1 -d '$DB_NAME' --csv -f -"

python3 "$REPO_ROOT/scripts/build_genesis_control_indicators_query.py" |
  ssh "$ABCDE_SSH" "$PSQL" > "$SMALL/component_control_indicators_raw.csv"
echo "wrote data/small/component_control_indicators_raw.csv"

python3 "$REPO_ROOT/scripts/build_genesis_control_indicators_query.py" --cohorts |
  ssh "$ABCDE_SSH" "$PSQL" > "$SMALL/component_control_cert_cohorts.csv"
echo "wrote data/small/component_control_cert_cohorts.csv"

python3 "$REPO_ROOT/scripts/build_genesis_control_classification.py"

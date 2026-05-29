#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ABCDE_SSH="${ABCDE_SSH:-abcde@192.168.86.118}"
DB_NAME="${DB_NAME:-cexplorer_replica}"

run_query() {
  local sql_path="$1"
  local out_path="$2"
  ssh "$ABCDE_SSH" "sudo -n -u postgres psql -v ON_ERROR_STOP=1 -d '$DB_NAME' --csv -f -" \
    < "$REPO_ROOT/$sql_path" > "$REPO_ROOT/$out_path"
  echo "wrote $out_path"
}

run_query sql/20_profiles/top_drep_profiles_current.sql data/small/governance_top_drep_profiles_current.csv
run_query sql/20_profiles/top_drep_stake_buckets.sql data/small/governance_top_drep_stake_buckets.csv
run_query sql/20_profiles/top_drep_delegation_age_buckets.sql data/small/governance_top_drep_delegation_age_buckets.csv
run_query sql/20_profiles/top_drep_pool_affiliations.sql data/small/governance_top_drep_pool_affiliations.csv

python3 "$REPO_ROOT/scripts/build_top_drep_koios_crosscheck.py"
python3 "$REPO_ROOT/scripts/build_top_drep_profiles_report.py"

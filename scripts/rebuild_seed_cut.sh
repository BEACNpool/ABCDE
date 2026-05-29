#!/usr/bin/env bash
# Rebuild the current v2 seed cut end-to-end.
# Requires SSH access to ABCDE for db-sync receipts and Python deps installed locally.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

if ! python3 - <<'PY' >/dev/null 2>&1
import duckdb
PY
then
  cat >&2 <<'MSG'
Missing Python package: duckdb
Run:
  python3 -m venv .venv
  . .venv/bin/activate
  pip install -r requirements/base.txt
MSG
  exit 1
fi

bash scripts/verify_seed_anchors_remote.sh
bash scripts/build_seed_outputs_remote.sh
bash scripts/build_seed_first_spends_remote.sh
bash scripts/build_seed_first_spend_inputs_remote.sh
bash scripts/build_fourth_entry_direct_cospend_remote.sh
bash scripts/build_bounded_trace_remote.sh
python3 scripts/build_sale_ticket_signal.py
python3 scripts/build_governance_rollups.py
bash scripts/build_governance_metadata_remote.sh
python3 scripts/build_governance_value_rollups.py
bash scripts/build_top_drep_profiles_remote.sh
python3 scripts/build_seed_artifacts.py
python3 scripts/verify_seed_artifacts.py
python3 scripts/verify_governance_rollups.py
python3 scripts/verify_governance_value_rollups.py
python3 scripts/verify_finding_queries.py
python3 scripts/build_community_report.py
python3 scripts/build_public_artifact_manifest.py

#!/usr/bin/env python3
import argparse
from pathlib import Path
import sys

REQUIRED = [
    'README.md', 'anchors.yaml', 'AUDIT_BACKLOG.md', 'Justfile', '.env.example',
    'profiles/dreps/README.md', 'docs/18_DREP_PROFILE_PACK.md', 'docs/19_QUERY_COOKBOOK.md',
    'docs/01_METHOD.md', 'docs/02_GRADING.md', 'docs/04_REPRODUCING_LOCALLY.md',
    'sql/01_extract/001_seed_registry.sql', 'sql/10_findings/F01_named_founder_allocations.duckdb.sql',
    'data/manifest.json', 'docs/09_LEGACY_MIGRATION_MAP.md', 'scripts/build_seed_artifacts.py', 'scripts/build_public_artifact_manifest.py', 'data/manifests/public-artifacts-manifest.json', 'scripts/build_community_report.py', 'reports/genesis_forensics_community_summary.md', 'scripts/verify_seed_artifacts.py', 'scripts/build_governance_rollups.py', 'scripts/build_governance_value_rollups.py', 'scripts/verify_governance_value_rollups.py', 'data/small/governance_spo_latest_value_targets.csv', 'data/small/governance_drep_latest_value_targets.csv', 'data/manifests/governance-value-rollups-manifest.json', 'scripts/verify_governance_rollups.py', 'data/small/governance_spo_delegation_targets.csv', 'data/small/governance_drep_delegation_targets.csv', 'data/small/governance_pool_metadata.csv', 'data/small/governance_drep_metadata.csv', 'scripts/build_governance_metadata_queries.py', 'scripts/build_governance_metadata_remote.sh', 'data/manifests/governance-rollups-manifest.json', 'scripts/verify_finding_queries.py', 'scripts/query_duckdb.py', 'docs/13_CROSS_MERGE_MILESTONE.md', 'docs/14_TRACE_EXPANSION_PROBE.md', 'data/small/bounded_trace_growth_probe.csv', 'data/small/cross_merge_depth10_probe.csv', 'data/small/seed_registry.csv', 'data/small/seed_anchor_db_verification.csv', 'data/small/seed_outputs_db.csv', 'data/small/seed_first_spends_db.csv', 'data/small/fourth_entry_direct_cospend_db.csv', 'data/small/fourth_entry_sale_ticket_signal.csv', 'data/small/bounded_trace_depth3_db.csv', 'data/small/seed_first_spend_inputs_db.csv', 'scripts/build_bounded_trace_query.py', 'scripts/build_bounded_trace_remote.sh', 'scripts/build_seed_anchor_query.py', 'scripts/build_seed_first_spend_inputs_query.py', 'scripts/build_seed_first_spend_inputs_remote.sh', 'scripts/build_fourth_entry_direct_cospend_query.py', 'scripts/build_fourth_entry_direct_cospend_remote.sh', 'scripts/build_seed_first_spends_query.py', 'scripts/build_seed_first_spends_remote.sh', 'scripts/build_seed_outputs_query.py', 'scripts/build_seed_outputs_remote.sh', 'scripts/verify_seed_anchors_remote.sh'
]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--structure-only', action='store_true')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / 'lib'))
    missing = [p for p in REQUIRED if not (root / p).exists()]
    if missing:
        print('Missing required paths:')
        for p in missing:
            print(f'  - {p}')
        raise SystemExit(1)
    from chain_toolkit.anchors import load_anchors
    anchors = load_anchors(root / 'anchors.yaml')
    if len(anchors) < 4:
        raise SystemExit('Expected at least 4 seed anchors')
    print(f'Structure check OK ({len(anchors)} anchors)')
    if not args.structure_only:
        print('Data-bundle verification is not implemented yet.')

if __name__ == '__main__':
    main()

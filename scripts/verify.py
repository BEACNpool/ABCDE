#!/usr/bin/env python3
import argparse
from pathlib import Path
import sys

REQUIRED = [
    'README.md', 'anchors.yaml', 'AUDIT_BACKLOG.md', 'Justfile', '.env.example',
    'claims/manifest.json', 'claims/README.md', 'prompts/README.md',
    'scripts/verify_claim_receipts.py', 'scripts/verify_public_artifacts.py',
    'scripts/build_release_bundle.py',
    'scripts/build_genesis_trail_case_remote.sh',
    'scripts/verify_genesis_trail_case.py',
    'reports/genesis_trail_case.md',
    'findings/F10_genesis_trail_monthly_stream.md',
    'claims/sql/genesis_trail_monthly_stream.sql',
    '.github/workflows/release.yml',
    'profiles/dreps/README.md', 'docs/18_DREP_PROFILE_PACK.md', 'docs/19_QUERY_COOKBOOK.md',
    'docs/21_GENESIS_DREP_BEHAVIOR_ANALYSIS.md', 'reports/genesis_ada_confidence_analysis.md',
    'findings/findings.json', 'scripts/build_findings_json.py', 'scripts/check_file_sizes.py',
    'data/small/db_tip_receipt.csv', 'data/manifests/genesis-drep-behavior-manifest.json',
    'data/small/governance_genesis_behavior_signals_top.csv',
    'data/small/governance_genesis_behavior_by_drep.csv',
    'data/small/governance_genesis_behavior_by_root_drep.csv',
    'data/small/governance_genesis_behavior_clusters.csv',
    'data/small/governance_genesis_behavior_by_proposal.csv',
    'scripts/build_genesis_drep_behavior_surface_remote.sh',
    'scripts/build_genesis_drep_behavior_rollups.py',
    'scripts/build_genesis_confidence_report.py',
    'sql/30_behavior/build_genesis_governance_surface_tables.sql',
    'sql/30_behavior/genesis_current_governance_surface.sql',
    'sql/30_behavior/drep_proposal_votes.sql',
    'sql/30_behavior/genesis_current_spo_surface.sql',
    'sql/30_behavior/genesis_pool_operator_links.sql',
    'sql/30_behavior/governance_actions_catalog.sql',
    'sql/30_behavior/genesis_delegation_history.sql',
    'sql/30_behavior/genesis_delegation_timeline.sql',
    'sql/30_behavior/staged_trace_depth_profile.sql',
    'scripts/build_genesis_spo_surface_remote.sh', 'scripts/build_genesis_spo_rollups.py',
    'data/small/governance_genesis_spo_by_pool.csv',
    'data/small/governance_genesis_pool_drep_matrix.csv',
    'data/small/governance_genesis_pool_operator_links.csv',
    'data/small/governance_actions_catalog.csv',
    'data/small/governance_genesis_delegation_timeline.csv',
    'data/small/staged_trace_depth16_summary.csv',
    'data/small/staged_trace_depth16_profile.csv',
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

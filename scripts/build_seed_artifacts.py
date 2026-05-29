#!/usr/bin/env python3
"""Build the first public seed artifacts from anchors.yaml.

This is intentionally local-only: it does not require db-sync. It creates:
- data/small/seed_registry.csv
- data/abcde_genesis_seed_registry.duckdb when the Python duckdb package is installed
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'lib'))

from chain_toolkit.anchors import load_anchors

COLUMNS = ['seed_id', 'label', 'tx_hash', 'amount_ada', 'amount_lovelace', 'source_type', 'evidence_grade', 'notes']
SEED_OUTPUTS_CSV = ROOT / 'data/small/seed_outputs_db.csv'
SEED_FIRST_SPENDS_CSV = ROOT / 'data/small/seed_first_spends_db.csv'
SEED_FIRST_SPEND_INPUTS_CSV = ROOT / 'data/small/seed_first_spend_inputs_db.csv'
FOURTH_DIRECT_COSPEND_CSV = ROOT / 'data/small/fourth_entry_direct_cospend_db.csv'
FOURTH_SALE_TICKET_SIGNAL_CSV = ROOT / 'data/small/fourth_entry_sale_ticket_signal.csv'
BOUNDED_TRACE_DEPTH3_CSV = ROOT / 'data/small/bounded_trace_depth3_db.csv'
GOV_SPO_TARGETS_CSV = ROOT / 'data/small/governance_spo_delegation_targets.csv'
GOV_DREP_TARGETS_CSV = ROOT / 'data/small/governance_drep_delegation_targets.csv'
GOV_SPO_LATEST_CSV = ROOT / 'data/small/governance_spo_latest_targets.csv'
GOV_DREP_LATEST_CSV = ROOT / 'data/small/governance_drep_latest_targets.csv'
GOV_SPO_VALUE_CSV = ROOT / 'data/small/governance_spo_latest_value_targets.csv'
GOV_DREP_VALUE_CSV = ROOT / 'data/small/governance_drep_latest_value_targets.csv'
GOV_POOL_METADATA_CSV = ROOT / 'data/small/governance_pool_metadata.csv'
GOV_DREP_METADATA_CSV = ROOT / 'data/small/governance_drep_metadata.csv'
STAGED_TRACE_DEPTH3_SUMMARY_CSV = ROOT / 'data/small/staged_trace_depth3_summary.csv'
STAGED_TRACE_DEPTH10_SUMMARY_CSV = ROOT / 'data/small/staged_trace_depth10_summary.csv'
STAGED_TRACE_FOUNDERS_DEPTH10_SUMMARY_CSV = ROOT / 'data/small/staged_trace_founders_depth10_summary.csv'
STAGED_TRACE_FOUNDERS_DEPTH12_SUMMARY_CSV = ROOT / 'data/small/staged_trace_founders_depth12_summary.csv'
STAGED_TRACE_FOUNDERS_DEPTH13_SUMMARY_CSV = ROOT / 'data/small/staged_trace_founders_depth13_summary.csv'
STAGED_TRACE_FOUNDERS_DEPTH14_SUMMARY_CSV = ROOT / 'data/small/staged_trace_founders_depth14_summary.csv'
STAGED_CROSS_MERGE_COMPARISON_CSV = ROOT / 'data/small/staged_cross_merge_comparison.csv'
STAGED_CROSS_MERGES_DEPTH10_CSV = ROOT / 'data/small/staged_cross_entity_merges_depth10.csv'
STAGED_CROSS_MERGES_FOUNDERS_DEPTH10_CSV = ROOT / 'data/small/staged_cross_entity_merges_founders_depth10.csv'
IOG_CURRENT_BAG_SUMMARY_CSV = ROOT / 'data/small/iog_current_bag_depth14_summary.csv'
IOG_CURRENT_BAG_BY_DEPTH_CSV = ROOT / 'data/small/iog_current_bag_depth14_by_depth.csv'
IOG_CURRENT_BAG_TOP_STAKE_CSV = ROOT / 'data/small/iog_current_bag_depth14_top_stake.csv'
IOG_POOL_STATE_VALIDATION_CSV = ROOT / 'data/small/iog_pool_state_validation.csv'
IOG_CLUSTER_PROFILE_TOP200_CSV = ROOT / 'data/small/iog_current_bag_depth14_cluster_profile_top200.csv'
IOG_CLUSTER_CLASSIFICATION_TOP200_CSV = ROOT / 'data/small/iog_current_bag_depth14_cluster_classification_top200.csv'
IOG_HEURISTIC_CLASS_SUMMARY_CSV = ROOT / 'data/small/iog_current_bag_depth14_heuristic_class_summary.csv'
IOG_COORDINATED_ABSTAIN_CSV = ROOT / 'data/small/iog_current_bag_depth14_coordinated_abstain_e329_clusters.csv'
IOG_CONFIDENCE_BANDS_CSV = ROOT / 'data/small/iog_current_bag_depth14_confidence_bands.csv'


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def write_csv(path: Path) -> None:
    anchors = load_anchors(ROOT / 'anchors.yaml')
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        for a in anchors:
            writer.writerow({
                'seed_id': a.seed_id,
                'label': a.label,
                'tx_hash': a.tx_hash,
                'amount_ada': a.amount_ada,
                'amount_lovelace': a.amount_ada * 1_000_000,
                'source_type': a.source_type,
                'evidence_grade': a.evidence_grade,
                'notes': a.notes or '',
            })


def write_duckdb(db_path: Path, csv_path: Path) -> bool:
    try:
        import duckdb  # type: ignore
    except Exception as exc:
        print(f'warning: duckdb Python package unavailable; skipped {db_path}: {exc}')
        return False
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()
    con = duckdb.connect(str(db_path))
    try:
        con.execute('CREATE SCHEMA IF NOT EXISTS genesis')
        con.execute(f"""
            CREATE TABLE seed_registry AS
            SELECT * FROM read_csv_auto('{csv_path.as_posix()}', header=true)
        """)
        con.execute('CREATE VIEW genesis.seed_registry AS SELECT * FROM seed_registry')

        optional_tables = [
            (SEED_OUTPUTS_CSV, 'seed_outputs'),
            (SEED_FIRST_SPENDS_CSV, 'seed_first_spends'),
            (SEED_FIRST_SPEND_INPUTS_CSV, 'seed_first_spend_inputs'),
            (FOURTH_DIRECT_COSPEND_CSV, 'fourth_entry_direct_cospend'),
            (FOURTH_SALE_TICKET_SIGNAL_CSV, 'fourth_entry_sale_ticket_signal'),
            (BOUNDED_TRACE_DEPTH3_CSV, 'bounded_trace_depth3'),
            (GOV_SPO_TARGETS_CSV, 'governance_spo_delegation_targets'),
            (GOV_DREP_TARGETS_CSV, 'governance_drep_delegation_targets'),
            (GOV_SPO_LATEST_CSV, 'governance_spo_latest_targets'),
            (GOV_DREP_LATEST_CSV, 'governance_drep_latest_targets'),
            (GOV_SPO_VALUE_CSV, 'governance_spo_latest_value_targets'),
            (GOV_DREP_VALUE_CSV, 'governance_drep_latest_value_targets'),
            (GOV_POOL_METADATA_CSV, 'governance_pool_metadata'),
            (GOV_DREP_METADATA_CSV, 'governance_drep_metadata'),
            (STAGED_TRACE_DEPTH3_SUMMARY_CSV, 'staged_trace_depth3_summary'),
            (STAGED_TRACE_DEPTH10_SUMMARY_CSV, 'staged_trace_depth10_summary'),
            (STAGED_TRACE_FOUNDERS_DEPTH10_SUMMARY_CSV, 'staged_trace_founders_depth10_summary'),
            (STAGED_TRACE_FOUNDERS_DEPTH12_SUMMARY_CSV, 'staged_trace_founders_depth12_summary'),
            (STAGED_TRACE_FOUNDERS_DEPTH13_SUMMARY_CSV, 'staged_trace_founders_depth13_summary'),
            (STAGED_TRACE_FOUNDERS_DEPTH14_SUMMARY_CSV, 'staged_trace_founders_depth14_summary'),
            (STAGED_CROSS_MERGE_COMPARISON_CSV, 'staged_cross_merge_comparison'),
            (STAGED_CROSS_MERGES_DEPTH10_CSV, 'staged_cross_entity_merges_depth10'),
            (STAGED_CROSS_MERGES_FOUNDERS_DEPTH10_CSV, 'staged_cross_entity_merges_founders_depth10'),
            (IOG_CURRENT_BAG_SUMMARY_CSV, 'iog_current_bag_depth14_summary'),
            (IOG_CURRENT_BAG_BY_DEPTH_CSV, 'iog_current_bag_depth14_by_depth'),
            (IOG_CURRENT_BAG_TOP_STAKE_CSV, 'iog_current_bag_depth14_top_stake'),
            (IOG_POOL_STATE_VALIDATION_CSV, 'iog_pool_state_validation'),
            (IOG_CLUSTER_PROFILE_TOP200_CSV, 'iog_current_bag_depth14_cluster_profile_top200'),
            (IOG_CLUSTER_CLASSIFICATION_TOP200_CSV, 'iog_current_bag_depth14_cluster_classification_top200'),
            (IOG_HEURISTIC_CLASS_SUMMARY_CSV, 'iog_current_bag_depth14_heuristic_class_summary'),
            (IOG_COORDINATED_ABSTAIN_CSV, 'iog_current_bag_depth14_coordinated_abstain_e329_clusters'),
            (IOG_CONFIDENCE_BANDS_CSV, 'iog_current_bag_depth14_confidence_bands'),
        ]
        for source_csv, table_name in optional_tables:
            if source_csv.exists():
                con.execute(f"""
                    CREATE TABLE {table_name} AS
                    SELECT * FROM read_csv_auto('{source_csv.as_posix()}', header=true)
                """)
                con.execute(f'CREATE VIEW genesis.{table_name} AS SELECT * FROM {table_name}')

        con.execute('CREATE TABLE artifact_manifest (key VARCHAR, value VARCHAR)')
        con.executemany('INSERT INTO artifact_manifest VALUES (?, ?)', [
            ('schema_version', '1'),
            ('artifact_kind', 'seed_registry'),
            ('source_file', 'anchors.yaml'),
            ('source_sha256', sha256_file(ROOT / 'anchors.yaml')),
            ('seed_registry_csv_sha256', sha256_file(csv_path)),
        ])
    finally:
        con.close()
    return True


def update_manifest(csv_path: Path, db_path: Path | None) -> None:
    manifest_path = ROOT / 'data' / 'manifest.json'
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {'schema_version': 1}
    manifest.update({
        'status': 'seed_registry_built',
        'seed_registry_csv': csv_path.relative_to(ROOT).as_posix(),
        'seed_registry_csv_sha256': sha256_file(csv_path),
        'anchors_yaml_sha256': sha256_file(ROOT / 'anchors.yaml'),
    })
    if db_path and db_path.exists():
        manifest['seed_registry_duckdb'] = db_path.relative_to(ROOT).as_posix()
    db_receipt = ROOT / 'data/small/seed_anchor_db_verification.csv'
    if db_receipt.exists():
        manifest['seed_anchor_db_verification_csv'] = db_receipt.relative_to(ROOT).as_posix()
        manifest['seed_anchor_db_verification_csv_sha256'] = sha256_file(db_receipt)
    if SEED_OUTPUTS_CSV.exists():
        manifest['seed_outputs_db_csv'] = SEED_OUTPUTS_CSV.relative_to(ROOT).as_posix()
        manifest['seed_outputs_db_csv_sha256'] = sha256_file(SEED_OUTPUTS_CSV)
    if SEED_FIRST_SPENDS_CSV.exists():
        manifest['seed_first_spends_db_csv'] = SEED_FIRST_SPENDS_CSV.relative_to(ROOT).as_posix()
        manifest['seed_first_spends_db_csv_sha256'] = sha256_file(SEED_FIRST_SPENDS_CSV)
    if SEED_FIRST_SPEND_INPUTS_CSV.exists():
        manifest['seed_first_spend_inputs_db_csv'] = SEED_FIRST_SPEND_INPUTS_CSV.relative_to(ROOT).as_posix()
        manifest['seed_first_spend_inputs_db_csv_sha256'] = sha256_file(SEED_FIRST_SPEND_INPUTS_CSV)
    if FOURTH_DIRECT_COSPEND_CSV.exists():
        manifest['fourth_entry_direct_cospend_db_csv'] = FOURTH_DIRECT_COSPEND_CSV.relative_to(ROOT).as_posix()
        manifest['fourth_entry_direct_cospend_db_csv_sha256'] = sha256_file(FOURTH_DIRECT_COSPEND_CSV)
    if FOURTH_SALE_TICKET_SIGNAL_CSV.exists():
        manifest['fourth_entry_sale_ticket_signal_csv'] = FOURTH_SALE_TICKET_SIGNAL_CSV.relative_to(ROOT).as_posix()
        manifest['fourth_entry_sale_ticket_signal_csv_sha256'] = sha256_file(FOURTH_SALE_TICKET_SIGNAL_CSV)
    if BOUNDED_TRACE_DEPTH3_CSV.exists():
        manifest['bounded_trace_depth3_csv'] = BOUNDED_TRACE_DEPTH3_CSV.relative_to(ROOT).as_posix()
        manifest['bounded_trace_depth3_csv_sha256'] = sha256_file(BOUNDED_TRACE_DEPTH3_CSV)
    if GOV_SPO_TARGETS_CSV.exists():
        manifest['governance_spo_delegation_targets_csv'] = GOV_SPO_TARGETS_CSV.relative_to(ROOT).as_posix()
        manifest['governance_spo_delegation_targets_csv_sha256'] = sha256_file(GOV_SPO_TARGETS_CSV)
    if GOV_DREP_TARGETS_CSV.exists():
        manifest['governance_drep_delegation_targets_csv'] = GOV_DREP_TARGETS_CSV.relative_to(ROOT).as_posix()
        manifest['governance_drep_delegation_targets_csv_sha256'] = sha256_file(GOV_DREP_TARGETS_CSV)
    if GOV_SPO_LATEST_CSV.exists():
        manifest['governance_spo_latest_targets_csv'] = GOV_SPO_LATEST_CSV.relative_to(ROOT).as_posix()
        manifest['governance_spo_latest_targets_csv_sha256'] = sha256_file(GOV_SPO_LATEST_CSV)
    if GOV_DREP_LATEST_CSV.exists():
        manifest['governance_drep_latest_targets_csv'] = GOV_DREP_LATEST_CSV.relative_to(ROOT).as_posix()
        manifest['governance_drep_latest_targets_csv_sha256'] = sha256_file(GOV_DREP_LATEST_CSV)
    if GOV_SPO_VALUE_CSV.exists():
        manifest['governance_spo_latest_value_targets_csv'] = GOV_SPO_VALUE_CSV.relative_to(ROOT).as_posix()
        manifest['governance_spo_latest_value_targets_csv_sha256'] = sha256_file(GOV_SPO_VALUE_CSV)
    if GOV_DREP_VALUE_CSV.exists():
        manifest['governance_drep_latest_value_targets_csv'] = GOV_DREP_VALUE_CSV.relative_to(ROOT).as_posix()
        manifest['governance_drep_latest_value_targets_csv_sha256'] = sha256_file(GOV_DREP_VALUE_CSV)
    if GOV_POOL_METADATA_CSV.exists():
        manifest['governance_pool_metadata_csv'] = GOV_POOL_METADATA_CSV.relative_to(ROOT).as_posix()
        manifest['governance_pool_metadata_csv_sha256'] = sha256_file(GOV_POOL_METADATA_CSV)
    if GOV_DREP_METADATA_CSV.exists():
        manifest['governance_drep_metadata_csv'] = GOV_DREP_METADATA_CSV.relative_to(ROOT).as_posix()
        manifest['governance_drep_metadata_csv_sha256'] = sha256_file(GOV_DREP_METADATA_CSV)
    staged_artifacts = {
        'staged_trace_depth3_summary_csv': STAGED_TRACE_DEPTH3_SUMMARY_CSV,
        'staged_trace_depth10_summary_csv': STAGED_TRACE_DEPTH10_SUMMARY_CSV,
        'staged_trace_founders_depth10_summary_csv': STAGED_TRACE_FOUNDERS_DEPTH10_SUMMARY_CSV,
        'staged_trace_founders_depth12_summary_csv': STAGED_TRACE_FOUNDERS_DEPTH12_SUMMARY_CSV,
        'staged_trace_founders_depth13_summary_csv': STAGED_TRACE_FOUNDERS_DEPTH13_SUMMARY_CSV,
        'staged_trace_founders_depth14_summary_csv': STAGED_TRACE_FOUNDERS_DEPTH14_SUMMARY_CSV,
        'staged_cross_merge_comparison_csv': STAGED_CROSS_MERGE_COMPARISON_CSV,
        'staged_cross_entity_merges_depth10_csv': STAGED_CROSS_MERGES_DEPTH10_CSV,
        'staged_cross_entity_merges_founders_depth10_csv': STAGED_CROSS_MERGES_FOUNDERS_DEPTH10_CSV,
        'iog_current_bag_depth14_summary_csv': IOG_CURRENT_BAG_SUMMARY_CSV,
        'iog_current_bag_depth14_by_depth_csv': IOG_CURRENT_BAG_BY_DEPTH_CSV,
        'iog_current_bag_depth14_top_stake_csv': IOG_CURRENT_BAG_TOP_STAKE_CSV,
        'iog_pool_state_validation_csv': IOG_POOL_STATE_VALIDATION_CSV,
        'iog_current_bag_depth14_cluster_profile_top200_csv': IOG_CLUSTER_PROFILE_TOP200_CSV,
        'iog_current_bag_depth14_cluster_classification_top200_csv': IOG_CLUSTER_CLASSIFICATION_TOP200_CSV,
        'iog_current_bag_depth14_heuristic_class_summary_csv': IOG_HEURISTIC_CLASS_SUMMARY_CSV,
        'iog_current_bag_depth14_coordinated_abstain_e329_clusters_csv': IOG_COORDINATED_ABSTAIN_CSV,
        'iog_current_bag_depth14_confidence_bands_csv': IOG_CONFIDENCE_BANDS_CSV,
    }
    for key, path in staged_artifacts.items():
        if path.exists():
            manifest[key] = path.relative_to(ROOT).as_posix()
            manifest[f'{key}_sha256'] = sha256_file(path)
    manifest_path.write_text(json.dumps(manifest, indent=2) + '\n')


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--csv', default='data/small/seed_registry.csv')
    parser.add_argument('--duckdb', default='data/abcde_genesis_seed_registry.duckdb')
    args = parser.parse_args()
    csv_path = ROOT / args.csv
    db_path = ROOT / args.duckdb
    write_csv(csv_path)
    wrote_db = write_duckdb(db_path, csv_path)
    update_manifest(csv_path, db_path if wrote_db else None)
    print(f'wrote {csv_path.relative_to(ROOT)} sha256={sha256_file(csv_path)}')
    if wrote_db:
        print(f'wrote {db_path.relative_to(ROOT)} sha256={sha256_file(db_path)}')


if __name__ == '__main__':
    main()

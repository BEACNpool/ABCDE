#!/usr/bin/env python3
"""Build SPO/DRep delegation rollups from preserved trace delegation receipts."""
from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEGACY = ROOT / 'legacy/2026-05-20-pre-v2-import/data/raw'
OUT_DIR = ROOT / 'data/small'
MANIFEST = ROOT / 'data/manifests/governance-rollups-manifest.json'

SEED_MAP = {
    'iog': 'iog',
    'emurgo': 'emurgo',
    'emurgo2': 'fourth_entry_781m',
    'cf': 'cf',
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline='') as f:
        return list(csv.DictReader(f))


def rollup_pool() -> list[dict[str, object]]:
    grouped: dict[tuple[str, str], dict[str, object]] = {}
    for legacy_seed, root_seed_id in SEED_MAP.items():
        path = LEGACY / legacy_seed / 'delegation_history.csv'
        for row in read_csv(path):
            pool = row['pool_id_bech32']
            key = (root_seed_id, pool)
            g = grouped.setdefault(key, {
                'root_seed_id': root_seed_id,
                'pool_id_bech32': pool,
                'delegation_cert_count': 0,
                'stake_addresses': set(),
                'first_active_epoch': None,
                'last_active_epoch': None,
                'first_observed_block_time': None,
                'last_observed_block_time': None,
                'source_files': set(),
            })
            epoch = int(row['active_epoch_no']) if row['active_epoch_no'] else None
            g['delegation_cert_count'] = int(g['delegation_cert_count']) + 1
            g['stake_addresses'].add(row['stake_address'])  # type: ignore[union-attr]
            g['source_files'].add(str(path.relative_to(ROOT)))  # type: ignore[union-attr]
            if epoch is not None:
                g['first_active_epoch'] = epoch if g['first_active_epoch'] is None else min(int(g['first_active_epoch']), epoch)
                g['last_active_epoch'] = epoch if g['last_active_epoch'] is None else max(int(g['last_active_epoch']), epoch)
            bt = row.get('block_time') or ''
            if bt:
                g['first_observed_block_time'] = bt if g['first_observed_block_time'] is None else min(str(g['first_observed_block_time']), bt)
                g['last_observed_block_time'] = bt if g['last_observed_block_time'] is None else max(str(g['last_observed_block_time']), bt)
    out = []
    for g in grouped.values():
        out.append({
            'root_seed_id': g['root_seed_id'],
            'pool_id_bech32': g['pool_id_bech32'],
            'distinct_stake_addresses': len(g['stake_addresses']),
            'delegation_cert_count': g['delegation_cert_count'],
            'first_active_epoch': g['first_active_epoch'],
            'last_active_epoch': g['last_active_epoch'],
            'first_observed_block_time': g['first_observed_block_time'],
            'last_observed_block_time': g['last_observed_block_time'],
            'source_files': ';'.join(sorted(g['source_files'])),
        })
    return sorted(out, key=lambda r: (str(r['root_seed_id']), -int(r['distinct_stake_addresses']), str(r['pool_id_bech32'])))


def rollup_drep() -> list[dict[str, object]]:
    grouped: dict[tuple[str, str], dict[str, object]] = {}
    for legacy_seed, root_seed_id in SEED_MAP.items():
        path = LEGACY / legacy_seed / 'drep_delegation.csv'
        for row in read_csv(path):
            drep = row['drep_id_bech32'] or 'ABSTAIN_OR_NO_CONFIDENCE_OR_UNKNOWN'
            key = (root_seed_id, drep)
            g = grouped.setdefault(key, {
                'root_seed_id': root_seed_id,
                'drep_id_bech32': drep,
                'delegation_cert_count': 0,
                'stake_addresses': set(),
                'first_epoch': None,
                'last_epoch': None,
                'first_observed_block_time': None,
                'last_observed_block_time': None,
                'source_files': set(),
            })
            epoch = int(row['epoch_no']) if row['epoch_no'] else None
            g['delegation_cert_count'] = int(g['delegation_cert_count']) + 1
            g['stake_addresses'].add(row['stake_address'])  # type: ignore[union-attr]
            g['source_files'].add(str(path.relative_to(ROOT)))  # type: ignore[union-attr]
            if epoch is not None:
                g['first_epoch'] = epoch if g['first_epoch'] is None else min(int(g['first_epoch']), epoch)
                g['last_epoch'] = epoch if g['last_epoch'] is None else max(int(g['last_epoch']), epoch)
            bt = row.get('block_time') or ''
            if bt:
                g['first_observed_block_time'] = bt if g['first_observed_block_time'] is None else min(str(g['first_observed_block_time']), bt)
                g['last_observed_block_time'] = bt if g['last_observed_block_time'] is None else max(str(g['last_observed_block_time']), bt)
    out = []
    for g in grouped.values():
        out.append({
            'root_seed_id': g['root_seed_id'],
            'drep_id_bech32': g['drep_id_bech32'],
            'distinct_stake_addresses': len(g['stake_addresses']),
            'delegation_cert_count': g['delegation_cert_count'],
            'first_epoch': g['first_epoch'],
            'last_epoch': g['last_epoch'],
            'first_observed_block_time': g['first_observed_block_time'],
            'last_observed_block_time': g['last_observed_block_time'],
            'source_files': ';'.join(sorted(g['source_files'])),
        })
    return sorted(out, key=lambda r: (str(r['root_seed_id']), -int(r['distinct_stake_addresses']), str(r['drep_id_bech32'])))



def latest_pool_snapshots() -> list[dict[str, object]]:
    latest: dict[tuple[str, str], dict[str, str]] = {}
    for legacy_seed, root_seed_id in SEED_MAP.items():
        path = LEGACY / legacy_seed / 'delegation_history.csv'
        for row in read_csv(path):
            key = (root_seed_id, row['stake_address'])
            prev = latest.get(key)
            row_key = (int(row['active_epoch_no'] or 0), row.get('block_time') or '', row.get('tx_hash') or '')
            prev_key = (int(prev['active_epoch_no'] or 0), prev.get('block_time') or '', prev.get('tx_hash') or '') if prev else None
            if prev is None or row_key > prev_key:
                latest[key] = row | {'root_seed_id': root_seed_id, 'source_file': str(path.relative_to(ROOT))}
    grouped: dict[tuple[str, str], dict[str, object]] = {}
    for row in latest.values():
        key = (row['root_seed_id'], row['pool_id_bech32'])
        g = grouped.setdefault(key, {
            'root_seed_id': row['root_seed_id'],
            'pool_id_bech32': row['pool_id_bech32'],
            'latest_distinct_stake_addresses': 0,
            'latest_active_epoch_min': None,
            'latest_active_epoch_max': None,
            'latest_observed_block_time_min': None,
            'latest_observed_block_time_max': None,
        })
        g['latest_distinct_stake_addresses'] = int(g['latest_distinct_stake_addresses']) + 1
        epoch = int(row['active_epoch_no'])
        g['latest_active_epoch_min'] = epoch if g['latest_active_epoch_min'] is None else min(int(g['latest_active_epoch_min']), epoch)
        g['latest_active_epoch_max'] = epoch if g['latest_active_epoch_max'] is None else max(int(g['latest_active_epoch_max']), epoch)
        bt = row.get('block_time') or ''
        g['latest_observed_block_time_min'] = bt if g['latest_observed_block_time_min'] is None else min(str(g['latest_observed_block_time_min']), bt)
        g['latest_observed_block_time_max'] = bt if g['latest_observed_block_time_max'] is None else max(str(g['latest_observed_block_time_max']), bt)
    return sorted(grouped.values(), key=lambda r: (str(r['root_seed_id']), -int(r['latest_distinct_stake_addresses']), str(r['pool_id_bech32'])))


def latest_drep_snapshots() -> list[dict[str, object]]:
    latest: dict[tuple[str, str], dict[str, str]] = {}
    for legacy_seed, root_seed_id in SEED_MAP.items():
        path = LEGACY / legacy_seed / 'drep_delegation.csv'
        for row in read_csv(path):
            key = (root_seed_id, row['stake_address'])
            prev = latest.get(key)
            row_key = (int(row['epoch_no'] or 0), row.get('block_time') or '', row.get('tx_hash') or '')
            prev_key = (int(prev['epoch_no'] or 0), prev.get('block_time') or '', prev.get('tx_hash') or '') if prev else None
            if prev is None or row_key > prev_key:
                latest[key] = row | {'root_seed_id': root_seed_id, 'source_file': str(path.relative_to(ROOT))}
    grouped: dict[tuple[str, str], dict[str, object]] = {}
    for row in latest.values():
        drep = row['drep_id_bech32'] or 'ABSTAIN_OR_NO_CONFIDENCE_OR_UNKNOWN'
        key = (row['root_seed_id'], drep)
        g = grouped.setdefault(key, {
            'root_seed_id': row['root_seed_id'],
            'drep_id_bech32': drep,
            'latest_distinct_stake_addresses': 0,
            'latest_epoch_min': None,
            'latest_epoch_max': None,
            'latest_observed_block_time_min': None,
            'latest_observed_block_time_max': None,
        })
        g['latest_distinct_stake_addresses'] = int(g['latest_distinct_stake_addresses']) + 1
        epoch = int(row['epoch_no'])
        g['latest_epoch_min'] = epoch if g['latest_epoch_min'] is None else min(int(g['latest_epoch_min']), epoch)
        g['latest_epoch_max'] = epoch if g['latest_epoch_max'] is None else max(int(g['latest_epoch_max']), epoch)
        bt = row.get('block_time') or ''
        g['latest_observed_block_time_min'] = bt if g['latest_observed_block_time_min'] is None else min(str(g['latest_observed_block_time_min']), bt)
        g['latest_observed_block_time_max'] = bt if g['latest_observed_block_time_max'] is None else max(str(g['latest_observed_block_time_max']), bt)
    return sorted(grouped.values(), key=lambda r: (str(r['root_seed_id']), -int(r['latest_distinct_stake_addresses']), str(r['drep_id_bech32'])))

def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise SystemExit(f'no rows for {path}')
    with path.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    pool_rows = rollup_pool()
    drep_rows = rollup_drep()
    latest_pool_rows = latest_pool_snapshots()
    latest_drep_rows = latest_drep_snapshots()
    pool_path = OUT_DIR / 'governance_spo_delegation_targets.csv'
    drep_path = OUT_DIR / 'governance_drep_delegation_targets.csv'
    latest_pool_path = OUT_DIR / 'governance_spo_latest_targets.csv'
    latest_drep_path = OUT_DIR / 'governance_drep_latest_targets.csv'
    write_csv(pool_path, pool_rows)
    write_csv(drep_path, drep_rows)
    write_csv(latest_pool_path, latest_pool_rows)
    write_csv(latest_drep_path, latest_drep_rows)
    manifest = {
        'schema_version': 1,
        'inputs': [str((LEGACY / seed).relative_to(ROOT)) for seed in sorted(SEED_MAP)],
        'outputs': {
            str(pool_path.relative_to(ROOT)): {'rows': len(pool_rows), 'sha256': sha256_file(pool_path)},
            str(drep_path.relative_to(ROOT)): {'rows': len(drep_rows), 'sha256': sha256_file(drep_path)},
            str(latest_pool_path.relative_to(ROOT)): {'rows': len(latest_pool_rows), 'sha256': sha256_file(latest_pool_path)},
            str(latest_drep_path.relative_to(ROOT)): {'rows': len(latest_drep_rows), 'sha256': sha256_file(latest_drep_path)},
        },
        'notes': 'Rollups derived from preserved legacy trace delegation receipts; root_seed_id emurgo2 is normalized to fourth_entry_781m.',
    }
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(manifest, indent=2) + '\n')
    print(f'wrote {pool_path.relative_to(ROOT)} rows={len(pool_rows)}')
    print(f'wrote {drep_path.relative_to(ROOT)} rows={len(drep_rows)}')
    print(f'wrote {latest_pool_path.relative_to(ROOT)} rows={len(latest_pool_rows)}')
    print(f'wrote {latest_drep_path.relative_to(ROOT)} rows={len(latest_drep_rows)}')


if __name__ == '__main__':
    main()

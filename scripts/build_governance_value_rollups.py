#!/usr/bin/env python3
"""Build value-weighted latest SPO/DRep rollups from current_unspent + latest delegation receipts."""
from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEGACY = ROOT / 'legacy/2026-05-20-pre-v2-import/data/raw'
OUT_DIR = ROOT / 'data/small'
MANIFEST = ROOT / 'data/manifests/governance-value-rollups-manifest.json'

SEED_MAP = {
    'iog': 'iog',
    'emurgo': 'emurgo',
    'emurgo2': 'fourth_entry_781m',
    'cf': 'cf',
}


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists(): return []
    with path.open(newline='') as f: return list(csv.DictReader(f))


def sha256_file(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024), b''): h.update(chunk)
    return h.hexdigest()


def current_value_by_stake() -> dict[tuple[str,str], int]:
    totals: dict[tuple[str,str], int] = defaultdict(int)
    for legacy_seed, root_seed in SEED_MAP.items():
        for row in read_csv(LEGACY / legacy_seed / 'current_unspent.csv'):
            stake = row.get('dest_stake_address') or ''
            if not stake: continue
            totals[(root_seed, stake)] += int(row['lovelace'])
    return totals


def latest_map(kind: str) -> dict[tuple[str,str], str]:
    # kind: pool or drep
    latest: dict[tuple[str,str], tuple[tuple[int,str,str], str]] = {}
    fname = 'delegation_history.csv' if kind == 'pool' else 'drep_delegation.csv'
    target_col = 'pool_id_bech32' if kind == 'pool' else 'drep_id_bech32'
    epoch_col = 'active_epoch_no' if kind == 'pool' else 'epoch_no'
    for legacy_seed, root_seed in SEED_MAP.items():
        for row in read_csv(LEGACY / legacy_seed / fname):
            stake = row['stake_address']
            target = row.get(target_col) or 'ABSTAIN_OR_NO_CONFIDENCE_OR_UNKNOWN'
            key = (root_seed, stake)
            sort_key = (int(row.get(epoch_col) or 0), row.get('block_time') or '', row.get('tx_hash') or '')
            if key not in latest or sort_key > latest[key][0]:
                latest[key] = (sort_key, target)
    return {k:v for k,(_,v) in latest.items()}


def write_value_rollup(path: Path, target_name: str, latest: dict[tuple[str,str], str], values: dict[tuple[str,str], int]) -> list[dict[str, object]]:
    grouped: dict[tuple[str,str], dict[str, object]] = {}
    for key, lovelace in values.items():
        target = latest.get(key)
        if not target: continue
        root_seed, _stake = key
        g = grouped.setdefault((root_seed, target), {
            'root_seed_id': root_seed,
            target_name: target,
            'latest_distinct_stake_addresses_with_current_value': 0,
            'current_lovelace': 0,
            'current_ada': '0',
        })
        g['latest_distinct_stake_addresses_with_current_value'] = int(g['latest_distinct_stake_addresses_with_current_value']) + 1
        g['current_lovelace'] = int(g['current_lovelace']) + lovelace
    rows=[]
    for g in grouped.values():
        lovelace=int(g['current_lovelace'])
        g['current_ada'] = f'{lovelace/1_000_000:.6f}'
        rows.append(g)
    rows.sort(key=lambda r:(str(r['root_seed_id']), -int(r['current_lovelace']), str(r[target_name])))
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='') as f:
        writer=csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader(); writer.writerows(rows)
    return rows


def main() -> None:
    values = current_value_by_stake()
    pool_latest = latest_map('pool')
    drep_latest = latest_map('drep')
    pool_path = OUT_DIR / 'governance_spo_latest_value_targets.csv'
    drep_path = OUT_DIR / 'governance_drep_latest_value_targets.csv'
    pool_rows = write_value_rollup(pool_path, 'pool_id_bech32', pool_latest, values)
    drep_rows = write_value_rollup(drep_path, 'drep_id_bech32', drep_latest, values)
    manifest = {
        'schema_version': 1,
        'notes': 'Value-weighted latest delegation rollups. Value source is preserved current_unspent trace receipts grouped by dest_stake_address.',
        'outputs': {
            str(pool_path.relative_to(ROOT)): {'rows': len(pool_rows), 'sha256': sha256_file(pool_path)},
            str(drep_path.relative_to(ROOT)): {'rows': len(drep_rows), 'sha256': sha256_file(drep_path)},
        },
    }
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(manifest, indent=2)+'\n')
    print(f'wrote {pool_path.relative_to(ROOT)} rows={len(pool_rows)}')
    print(f'wrote {drep_path.relative_to(ROOT)} rows={len(drep_rows)}')

if __name__ == '__main__': main()

#!/usr/bin/env python3
"""Verify governance SPO/DRep rollup artifacts."""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPO = ROOT / 'data/small/governance_spo_delegation_targets.csv'
DREP = ROOT / 'data/small/governance_drep_delegation_targets.csv'
SPO_LATEST = ROOT / 'data/small/governance_spo_latest_targets.csv'
DREP_LATEST = ROOT / 'data/small/governance_drep_latest_targets.csv'
MANIFEST = ROOT / 'data/manifests/governance-rollups-manifest.json'
POOL_META = ROOT / 'data/small/governance_pool_metadata.csv'
DREP_META = ROOT / 'data/small/governance_drep_metadata.csv'


def fail(msg: str) -> None:
    raise SystemExit(f'ERROR: {msg}')


def main() -> None:
    spo_rows = list(csv.DictReader(SPO.open(newline='')))
    drep_rows = list(csv.DictReader(DREP.open(newline='')))
    if len(spo_rows) != 5175:
        fail(f'SPO row count {len(spo_rows)} != 5175')
    if len(drep_rows) != 390:
        fail(f'DRep row count {len(drep_rows)} != 390')
    spo_latest_rows = list(csv.DictReader(SPO_LATEST.open(newline='')))
    drep_latest_rows = list(csv.DictReader(DREP_LATEST.open(newline='')))
    if len(spo_latest_rows) != 2868:
        fail(f'SPO latest row count {len(spo_latest_rows)} != 2868')
    if len(drep_latest_rows) != 337:
        fail(f'DRep latest row count {len(drep_latest_rows)} != 337')
    seeds = {r['root_seed_id'] for r in spo_rows + drep_rows}
    expected = {'iog', 'emurgo', 'fourth_entry_781m', 'cf'}
    if seeds != expected:
        fail(f'seed set mismatch: {seeds}')
    if not any(r['drep_id_bech32'] == 'drep_always_abstain' for r in drep_rows):
        fail('missing drep_always_abstain')
    pool_meta_rows = list(csv.DictReader(POOL_META.open(newline=''))) if POOL_META.exists() else []
    drep_meta_rows = list(csv.DictReader(DREP_META.open(newline=''))) if DREP_META.exists() else []
    if pool_meta_rows and len(pool_meta_rows) != 1857:
        fail(f'pool metadata row count {len(pool_meta_rows)} != 1857')
    if drep_meta_rows and len(drep_meta_rows) != 184:
        fail(f'DRep metadata row count {len(drep_meta_rows)} != 184')
    manifest = json.loads(MANIFEST.read_text())
    if manifest['outputs']['data/small/governance_spo_delegation_targets.csv']['rows'] != len(spo_rows):
        fail('manifest SPO row mismatch')
    if manifest['outputs']['data/small/governance_drep_delegation_targets.csv']['rows'] != len(drep_rows):
        fail('manifest DRep row mismatch')
    print(f'Governance rollups OK: SPO targets={len(spo_rows)} DRep targets={len(drep_rows)} latest_SPO={len(spo_latest_rows)} latest_DRep={len(drep_latest_rows)}')


if __name__ == '__main__':
    main()

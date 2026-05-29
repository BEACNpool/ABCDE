#!/usr/bin/env python3
from __future__ import annotations
import csv, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SPO=ROOT/'data/small/governance_spo_latest_value_targets.csv'
DREP=ROOT/'data/small/governance_drep_latest_value_targets.csv'
MANIFEST=ROOT/'data/manifests/governance-value-rollups-manifest.json'

def fail(m): raise SystemExit(f'ERROR: {m}')
def main():
    spo=list(csv.DictReader(SPO.open(newline='')))
    drep=list(csv.DictReader(DREP.open(newline='')))
    if len(spo)!=2852: fail(f'SPO value rows {len(spo)} != 2852')
    if len(drep)!=335: fail(f'DRep value rows {len(drep)} != 335')
    if sum(int(r['current_lovelace']) for r in spo) <= 0: fail('SPO value total empty')
    if sum(int(r['current_lovelace']) for r in drep) <= 0: fail('DRep value total empty')
    m=json.loads(MANIFEST.read_text())
    if m['outputs']['data/small/governance_spo_latest_value_targets.csv']['rows'] != len(spo): fail('manifest SPO mismatch')
    if m['outputs']['data/small/governance_drep_latest_value_targets.csv']['rows'] != len(drep): fail('manifest DRep mismatch')
    print(f'Governance value rollups OK: SPO={len(spo)} DRep={len(drep)}')
if __name__=='__main__': main()

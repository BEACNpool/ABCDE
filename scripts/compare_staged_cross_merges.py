#!/usr/bin/env python3
"""Compare staged cross-entity merge exports against the legacy 521-row baseline."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEGACY = ROOT / 'legacy/2026-05-20-pre-v2-import/evidence/csv/cross_seed_consuming_transactions_2026-04-06.csv'


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline='') as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise SystemExit(f'no rows for {path}')
    with path.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def compare(staged_path: Path) -> dict[str, object]:
    legacy = read_csv(LEGACY)
    staged = read_csv(staged_path)
    legacy_hashes = {r['dest_tx_hash'] for r in legacy}
    staged_hashes = {r['merge_tx_hash'] for r in staged}
    overlap = legacy_hashes & staged_hashes
    missing = legacy_hashes - staged_hashes
    extra = staged_hashes - legacy_hashes
    return {
        'staged_path': staged_path.relative_to(ROOT).as_posix(),
        'staged_sha256': sha256_file(staged_path),
        'staged_rows': len(staged),
        'staged_distinct_txs': len(staged_hashes),
        'legacy_rows': len(legacy),
        'legacy_distinct_txs': len(legacy_hashes),
        'overlap_txs': len(overlap),
        'legacy_missing_txs': len(missing),
        'staged_extra_txs': len(extra),
        'overlap_by_legacy_combo': dict(sorted(Counter(r['seed_combo'] for r in legacy if r['dest_tx_hash'] in overlap).items())),
        'missing_by_legacy_combo': dict(sorted(Counter(r['seed_combo'] for r in legacy if r['dest_tx_hash'] in missing).items())),
        'extra_by_staged_combo': dict(sorted(Counter(r['root_combo'] for r in staged if r['merge_tx_hash'] in extra).items())),
        'first_missing_legacy': [
            {'epoch_no': r['epoch_no'], 'dest_tx_hash': r['dest_tx_hash'], 'seed_combo': r['seed_combo']}
            for r in sorted((r for r in legacy if r['dest_tx_hash'] in missing), key=lambda x: (int(x['epoch_no']), x['dest_tx_hash']))[:20]
        ],
        'first_extra_staged': [
            {'epoch_no': r['epoch_no'], 'merge_tx_hash': r['merge_tx_hash'], 'root_combo': r['root_combo']}
            for r in sorted((r for r in staged if r['merge_tx_hash'] in extra), key=lambda x: (int(x['epoch_no']), x['merge_tx_hash']))[:20]
        ],
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('staged_csv', nargs='+')
    ap.add_argument('--out-json', default='data/manifests/staged-cross-merge-comparison.json')
    ap.add_argument('--out-csv', default='data/small/staged_cross_merge_comparison.csv')
    args = ap.parse_args()
    comparisons = [compare((ROOT / p).resolve() if not Path(p).is_absolute() else Path(p)) for p in args.staged_csv]
    payload = {
        'schema_version': 1,
        'legacy_source': LEGACY.relative_to(ROOT).as_posix(),
        'legacy_sha256': sha256_file(LEGACY),
        'comparisons': comparisons,
        'notes': 'Overlap compares staged merge transaction hashes to the legacy 521-row named-founder cross-seed baseline. Staged extras are candidates, not claims.',
    }
    out_json = ROOT / args.out_json
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(payload, indent=2) + '\n')
    rows = []
    for c in comparisons:
        rows.append({
            'staged_path': c['staged_path'],
            'staged_rows': c['staged_rows'],
            'legacy_distinct_txs': c['legacy_distinct_txs'],
            'overlap_txs': c['overlap_txs'],
            'legacy_missing_txs': c['legacy_missing_txs'],
            'staged_extra_txs': c['staged_extra_txs'],
        })
    write_csv(ROOT / args.out_csv, rows)
    print(f'wrote {out_json.relative_to(ROOT)}')
    print(f'wrote {args.out_csv}')


if __name__ == '__main__':
    main()

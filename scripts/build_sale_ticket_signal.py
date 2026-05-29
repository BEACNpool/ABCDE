#!/usr/bin/env python3
"""Derive the fourth-entry sale-ticket signal from archived ada-sale stats JSON."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
SOURCE_URL = 'https://raw.githubusercontent.com/cardano-foundation/cardano-org/master/static/archive/static.iohk.io/adasale/js/stats/main2.json'
SOURCE_PATH = ROOT / 'data/sources/adasale_main2.json'
OUT_PATH = ROOT / 'data/small/fourth_entry_sale_ticket_signal.csv'
TARGET_AMOUNT = 781_381_495

TARGET_SLICES = {
    ('Tickets', 'Tranche', 'Tranche 4'),
    ('Tickets', 'Region', 'Japan'),
    ('Tickets', 'User type', 'Company'),
    ('Tickets', 'Currency', 'BTC'),
    ('Tickets', 'All', 'All'),
    ('Buyers', 'User type', 'Company'),
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def ensure_source() -> None:
    SOURCE_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not SOURCE_PATH.exists():
        with urlopen(SOURCE_URL, timeout=30) as r:
            SOURCE_PATH.write_bytes(r.read())


def field(entry: dict, name: str) -> str:
    return entry.get(f'gsx${name}', {}).get('$t', '')


def main() -> None:
    ensure_source()
    data = json.loads(SOURCE_PATH.read_text())
    rows = []
    for entry in data['feed']['entry']:
        subject = field(entry, 'subject')
        by = field(entry, 'by')
        view = field(entry, 'view')
        key = (subject, by, view)
        if key not in TARGET_SLICES:
            continue
        amount = int(field(entry, 'adamax'))
        rows.append({
            'subject': subject,
            'by': by,
            'view': view,
            'slice': f'{subject} / {by} / {view}',
            'metric': 'adamax',
            'amount_ada': amount,
            'matches_fourth_entry_amount': str(amount == TARGET_AMOUNT).lower(),
            'source_url': SOURCE_URL,
            'source_sha256': sha256_file(SOURCE_PATH),
            'source_updated': data['feed']['updated']['$t'],
        })
    rows.sort(key=lambda r: r['slice'])
    if len(rows) != len(TARGET_SLICES):
        raise SystemExit(f'expected {len(TARGET_SLICES)} target rows, got {len(rows)}')
    if any(r['amount_ada'] != TARGET_AMOUNT for r in rows):
        raise SystemExit('not all target rows match fourth-entry amount')
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f'wrote {OUT_PATH.relative_to(ROOT)}')
    print(f'source_sha256={sha256_file(SOURCE_PATH)}')


if __name__ == '__main__':
    main()

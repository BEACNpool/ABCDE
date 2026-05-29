#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'lib'))

from chain_toolkit.anchors import load_anchors


def sql_quote(value: str | None) -> str:
    if value is None:
        return 'NULL'
    return "'" + value.replace("'", "''") + "'"


def main():
    anchors = load_anchors(ROOT / 'anchors.yaml')
    print('BEGIN;')
    print('CREATE SCHEMA IF NOT EXISTS genesis;')
    print('TRUNCATE genesis.seed_registry;')
    for a in anchors:
        print(
            'INSERT INTO genesis.seed_registry '
            '(seed_id, label, tx_hash_hex, amount_lovelace, source_type, evidence_grade, notes) VALUES '
            f"({sql_quote(a.seed_id)}, {sql_quote(a.label)}, {sql_quote(a.tx_hash)}, {a.amount_ada * 1_000_000}, "
            f"{sql_quote(a.source_type)}, {sql_quote(a.evidence_grade)}, {sql_quote(a.notes)});"
        )
    print('COMMIT;')

if __name__ == '__main__':
    main()

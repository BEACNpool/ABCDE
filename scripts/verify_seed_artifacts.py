#!/usr/bin/env python3
"""Verify generated seed registry CSV/DuckDB artifacts against anchors.yaml."""
from __future__ import annotations

import csv
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'lib'))

from chain_toolkit.anchors import load_anchors

CSV_PATH = ROOT / 'data/small/seed_registry.csv'
DUCKDB_PATH = ROOT / 'data/abcde_genesis_seed_registry.duckdb'
DB_VERIFY_CSV_PATH = ROOT / 'data/small/seed_anchor_db_verification.csv'
SEED_OUTPUTS_CSV_PATH = ROOT / 'data/small/seed_outputs_db.csv'
SEED_FIRST_SPENDS_CSV_PATH = ROOT / 'data/small/seed_first_spends_db.csv'
FOURTH_DIRECT_COSPEND_CSV_PATH = ROOT / 'data/small/fourth_entry_direct_cospend_db.csv'
FOURTH_SALE_TICKET_SIGNAL_CSV_PATH = ROOT / 'data/small/fourth_entry_sale_ticket_signal.csv'
BOUNDED_TRACE_DEPTH3_CSV_PATH = ROOT / 'data/small/bounded_trace_depth3_db.csv'
GOV_SPO_TARGETS_CSV_PATH = ROOT / 'data/small/governance_spo_delegation_targets.csv'
GOV_DREP_TARGETS_CSV_PATH = ROOT / 'data/small/governance_drep_delegation_targets.csv'
EXPECTED_TOTAL_LOVELACE = 5_966_795_602_000_000


def fail(msg: str) -> None:
    raise SystemExit(f'ERROR: {msg}')


def verify_csv() -> None:
    anchors = {a.seed_id: a for a in load_anchors(ROOT / 'anchors.yaml')}
    if not CSV_PATH.exists():
        fail(f'missing {CSV_PATH.relative_to(ROOT)}')
    with CSV_PATH.open(newline='') as f:
        rows = list(csv.DictReader(f))
    if len(rows) != len(anchors):
        fail(f'CSV row count {len(rows)} != anchors {len(anchors)}')
    total = 0
    for row in rows:
        seed_id = row['seed_id']
        if seed_id not in anchors:
            fail(f'unexpected seed_id {seed_id}')
        anchor = anchors[seed_id]
        if row['tx_hash'] != anchor.tx_hash:
            fail(f'tx_hash mismatch for {seed_id}')
        if int(row['amount_ada']) != anchor.amount_ada:
            fail(f'amount_ada mismatch for {seed_id}')
        lovelace = int(row['amount_lovelace'])
        if lovelace != anchor.amount_ada * 1_000_000:
            fail(f'lovelace conversion mismatch for {seed_id}')
        total += lovelace
    if total != EXPECTED_TOTAL_LOVELACE:
        fail(f'total lovelace {total} != {EXPECTED_TOTAL_LOVELACE}')
    print(f'CSV OK: {len(rows)} seeds, total={total}')


def verify_duckdb() -> None:
    if not DUCKDB_PATH.exists():
        print(f'DuckDB not present, skipped: {DUCKDB_PATH.relative_to(ROOT)}')
        return
    try:
        import duckdb  # type: ignore
    except Exception as exc:
        print(f'DuckDB Python package unavailable, skipped DB verification: {exc}')
        return
    con = duckdb.connect(str(DUCKDB_PATH), read_only=True)
    try:
        count, total = con.execute('SELECT count(*), sum(amount_lovelace) FROM seed_registry').fetchone()
        if count != 4:
            fail(f'DuckDB seed count {count} != 4')
        if total != EXPECTED_TOTAL_LOVELACE:
            fail(f'DuckDB total {total} != {EXPECTED_TOTAL_LOVELACE}')
        grades = dict(con.execute('SELECT seed_id, evidence_grade FROM seed_registry').fetchall())
        if grades.get('fourth_entry_781m') != 'STRONG_INFERENCE':
            fail('fourth_entry_781m grade mismatch')
        for seed_id in ['iog', 'cf', 'emurgo']:
            if grades.get(seed_id) != 'FACT':
                fail(f'{seed_id} grade mismatch')
        if SEED_OUTPUTS_CSV_PATH.exists():
            out_count, out_total = con.execute('SELECT count(*), sum(value_lovelace) FROM seed_outputs').fetchone()
            if out_count != 4 or out_total != EXPECTED_TOTAL_LOVELACE:
                fail(f'DuckDB seed_outputs mismatch count={out_count} total={out_total}')
        if SEED_FIRST_SPENDS_CSV_PATH.exists():
            spend_count = con.execute('SELECT count(*) FROM seed_first_spends').fetchone()[0]
            if spend_count != 4:
                fail(f'DuckDB seed_first_spends mismatch count={spend_count}')
        if FOURTH_DIRECT_COSPEND_CSV_PATH.exists():
            cospend_count = con.execute('SELECT count(*) FROM fourth_entry_direct_cospend').fetchone()[0]
            if cospend_count != 2:
                fail(f'DuckDB fourth_entry_direct_cospend mismatch count={cospend_count}')
        if FOURTH_SALE_TICKET_SIGNAL_CSV_PATH.exists():
            signal_count = con.execute('SELECT count(*) FROM fourth_entry_sale_ticket_signal').fetchone()[0]
            if signal_count != 6:
                fail(f'DuckDB fourth_entry_sale_ticket_signal mismatch count={signal_count}')
        if BOUNDED_TRACE_DEPTH3_CSV_PATH.exists():
            trace_count = con.execute('SELECT count(*) FROM bounded_trace_depth3').fetchone()[0]
            if trace_count != 53:
                fail(f'DuckDB bounded_trace_depth3 mismatch count={trace_count}')
        if GOV_SPO_TARGETS_CSV_PATH.exists():
            spo_count = con.execute('SELECT count(*) FROM governance_spo_delegation_targets').fetchone()[0]
            if spo_count != 5175:
                fail(f'DuckDB SPO rollup mismatch count={spo_count}')
        if GOV_DREP_TARGETS_CSV_PATH.exists():
            drep_count = con.execute('SELECT count(*) FROM governance_drep_delegation_targets').fetchone()[0]
            if drep_count != 390:
                fail(f'DuckDB DRep rollup mismatch count={drep_count}')
        print(f'DuckDB OK: {count} seeds, total={total}')
    finally:
        con.close()



def verify_db_receipt() -> None:
    if not DB_VERIFY_CSV_PATH.exists():
        print(f'DB receipt not present, skipped: {DB_VERIFY_CSV_PATH.relative_to(ROOT)}')
        return
    with DB_VERIFY_CSV_PATH.open(newline='') as f:
        rows = list(csv.DictReader(f))
    if len(rows) != 4:
        fail(f'DB receipt row count {len(rows)} != 4')
    for row in rows:
        if row['status'] != 'FOUND':
            fail(f"DB receipt missing seed {row['seed_id']}")
        if int(row['output_count']) != 1:
            fail(f"DB receipt output_count mismatch for {row['seed_id']}")
        anchor = {a.seed_id: a for a in load_anchors(ROOT / 'anchors.yaml')}[row['seed_id']]
        if int(row['tx_output_lovelace']) != anchor.amount_ada * 1_000_000:
            fail(f"DB receipt value mismatch for {row['seed_id']}")
    print(f'DB receipt OK: {len(rows)} seeds found')


def verify_seed_outputs_receipt() -> None:
    if not SEED_OUTPUTS_CSV_PATH.exists():
        print(f'Seed outputs receipt not present, skipped: {SEED_OUTPUTS_CSV_PATH.relative_to(ROOT)}')
        return
    anchors = {a.seed_id: a for a in load_anchors(ROOT / 'anchors.yaml')}
    with SEED_OUTPUTS_CSV_PATH.open(newline='') as f:
        rows = list(csv.DictReader(f))
    if len(rows) != len(anchors):
        fail(f'seed outputs row count {len(rows)} != anchors {len(anchors)}')
    for row in rows:
        seed_id = row['seed_id']
        if seed_id not in anchors:
            fail(f'unexpected seed output seed_id {seed_id}')
        if int(row['tx_out_index']) != 0:
            fail(f'expected output index 0 for {seed_id}')
        if int(row['value_lovelace']) != anchors[seed_id].amount_ada * 1_000_000:
            fail(f'seed output value mismatch for {seed_id}')
        if not row['address'].startswith('DdzFF'):
            fail(f'unexpected non-Byron-looking seed address for {seed_id}')
    print(f'Seed outputs receipt OK: {len(rows)} outputs')


def verify_seed_first_spends_receipt() -> None:
    if not SEED_FIRST_SPENDS_CSV_PATH.exists():
        print(f'Seed first-spends receipt not present, skipped: {SEED_FIRST_SPENDS_CSV_PATH.relative_to(ROOT)}')
        return
    with SEED_FIRST_SPENDS_CSV_PATH.open(newline='') as f:
        rows = list(csv.DictReader(f))
    if len(rows) != 4:
        fail(f'first-spends row count {len(rows)} != 4')
    by_seed = {row['seed_id']: row for row in rows}
    for seed_id, row in by_seed.items():
        if not row['first_spend_tx_hash']:
            fail(f'missing first spend for {seed_id}')
        if int(row['seed_tx_out_index']) != 0:
            fail(f'first-spend source output index mismatch for {seed_id}')
    if int(by_seed['fourth_entry_781m']['spend_input_count']) < 2:
        fail('fourth entry first spend should have at least 2 inputs for convergence test')
    emurgo_hours = float(by_seed['emurgo']['dormant_hours'])
    fourth_hours = float(by_seed['fourth_entry_781m']['dormant_hours'])
    if abs(emurgo_hours - fourth_hours) > 0.1:
        fail('EMURGO and fourth-entry dormancy delta unexpectedly large')
    print(f'Seed first-spends receipt OK: {len(rows)} spends')


def verify_fourth_direct_cospend_receipt() -> None:
    if not FOURTH_DIRECT_COSPEND_CSV_PATH.exists():
        print(f'Fourth-entry direct-cospend receipt not present, skipped: {FOURTH_DIRECT_COSPEND_CSV_PATH.relative_to(ROOT)}')
        return
    with FOURTH_DIRECT_COSPEND_CSV_PATH.open(newline='') as f:
        rows = list(csv.DictReader(f))
    if len(rows) != 2:
        fail(f'fourth direct-cospend row count {len(rows)} != 2')
    emurgo_rows = [r for r in rows if r['descendant_of_seed_id'] == 'emurgo']
    if len(emurgo_rows) != 1:
        fail('expected exactly one EMURGO-descended co-spent input')
    if int(emurgo_rows[0]['emurgo_trace_depth']) != 2:
        fail('expected EMURGO co-spent input at trace depth 2')
    if not emurgo_rows[0]['emurgo_path'].startswith('242608fc'):
        fail('unexpected EMURGO path')
    print('Fourth-entry direct-cospend receipt OK')


def verify_fourth_sale_ticket_signal() -> None:
    if not FOURTH_SALE_TICKET_SIGNAL_CSV_PATH.exists():
        print(f'Fourth-entry sale-ticket signal not present, skipped: {FOURTH_SALE_TICKET_SIGNAL_CSV_PATH.relative_to(ROOT)}')
        return
    with FOURTH_SALE_TICKET_SIGNAL_CSV_PATH.open(newline='') as f:
        rows = list(csv.DictReader(f))
    if len(rows) != 6:
        fail(f'sale-ticket signal row count {len(rows)} != 6')
    if any(int(r['amount_ada']) != 781_381_495 for r in rows):
        fail('sale-ticket signal amount mismatch')
    print('Fourth-entry sale-ticket signal OK')


def verify_bounded_trace_depth3() -> None:
    if not BOUNDED_TRACE_DEPTH3_CSV_PATH.exists():
        print(f'Bounded trace not present, skipped: {BOUNDED_TRACE_DEPTH3_CSV_PATH.relative_to(ROOT)}')
        return
    with BOUNDED_TRACE_DEPTH3_CSV_PATH.open(newline='') as f:
        rows = list(csv.DictReader(f))
    if len(rows) != 53:
        fail(f'bounded trace row count {len(rows)} != 53')
    max_depth = max(int(r['depth']) for r in rows)
    if max_depth != 3:
        fail(f'bounded trace max depth {max_depth} != 3')
    print('Bounded trace depth-3 OK')

def main() -> None:
    verify_csv()
    verify_duckdb()
    verify_db_receipt()
    verify_seed_outputs_receipt()
    verify_seed_first_spends_receipt()
    verify_fourth_direct_cospend_receipt()
    verify_fourth_sale_ticket_signal()
    verify_bounded_trace_depth3()


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Generate a community-facing Markdown report from the local DuckDB artifact."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / 'data/abcde_genesis_seed_registry.duckdb'
OUT = ROOT / 'reports/genesis_forensics_community_summary.md'


def md_table(headers, rows):
    out = ['| ' + ' | '.join(headers) + ' |', '| ' + ' | '.join(['---'] * len(headers)) + ' |']
    for row in rows:
        out.append('| ' + ' | '.join('' if v is None else str(v) for v in row) + ' |')
    return '\n'.join(out)


def table_exists(con, table_name: str) -> bool:
    return bool(con.execute("""
        SELECT count(*) FROM information_schema.tables
        WHERE table_schema = 'main' AND table_name = ?
    """, [table_name]).fetchone()[0])


def main() -> None:
    import duckdb  # type: ignore
    con = duckdb.connect(str(DB), read_only=True)
    try:
        seed_rows = con.execute("""
            SELECT seed_id, label, amount_ada, source_type, evidence_grade
            FROM seed_registry ORDER BY amount_ada DESC
        """).fetchall()
        first_spends = con.execute("""
            SELECT seed_id, first_spend_tx_hash, round(dormant_hours, 3), spend_input_count
            FROM seed_first_spends ORDER BY seed_id
        """).fetchall()
        cospend = con.execute("""
            SELECT input_source_tx_hash, input_value_lovelace, descendant_of_seed_id, emurgo_trace_depth
            FROM fourth_entry_direct_cospend ORDER BY input_value_lovelace DESC
        """).fetchall()
        spo_summary = con.execute("""
            SELECT root_seed_id, count(*) AS pool_targets
            FROM governance_spo_delegation_targets GROUP BY root_seed_id ORDER BY root_seed_id
        """).fetchall()
        drep_summary = con.execute("""
            SELECT root_seed_id, count(*) AS drep_targets
            FROM governance_drep_delegation_targets GROUP BY root_seed_id ORDER BY root_seed_id
        """).fetchall()
        top_spo = con.execute("""
            SELECT root_seed_id, coalesce(ticker_name, ''), coalesce(pool_name, ''), pool_id_bech32, latest_distinct_stake_addresses
            FROM (
              SELECT t.*, m.ticker_name, m.pool_name
              FROM governance_spo_latest_targets t
              LEFT JOIN governance_pool_metadata m USING (pool_id_bech32)
            )
            ORDER BY latest_distinct_stake_addresses DESC, root_seed_id
            LIMIT 15
        """).fetchall()
        top_drep = con.execute("""
            SELECT root_seed_id, drep_id_bech32, coalesce(voting_anchor_url, ''), latest_distinct_stake_addresses
            FROM governance_drep_latest_targets t
            LEFT JOIN governance_drep_metadata m USING (drep_id_bech32)
            ORDER BY latest_distinct_stake_addresses DESC, root_seed_id
            LIMIT 15
        """).fetchall()
        top_spo_value = con.execute("""
            SELECT root_seed_id, coalesce(ticker_name, ''), coalesce(pool_name, ''), pool_id_bech32, current_ada
            FROM governance_spo_latest_value_targets t
            LEFT JOIN governance_pool_metadata m USING (pool_id_bech32)
            ORDER BY current_lovelace DESC, root_seed_id
            LIMIT 15
        """).fetchall()
        top_drep_value = con.execute("""
            SELECT root_seed_id, drep_id_bech32, coalesce(voting_anchor_url, ''), current_ada
            FROM governance_drep_latest_value_targets t
            LEFT JOIN governance_drep_metadata m USING (drep_id_bech32)
            ORDER BY current_lovelace DESC, root_seed_id
            LIMIT 15
        """).fetchall()
        staged_depth10 = con.execute("""
            SELECT artifact, bucket, rows
            FROM staged_trace_depth10_summary
            ORDER BY artifact, try_cast(bucket AS integer) NULLS LAST, bucket
        """).fetchall() if table_exists(con, 'staged_trace_depth10_summary') else []
        staged_founders_depth10 = con.execute("""
            SELECT artifact, bucket, rows
            FROM staged_trace_founders_depth10_summary
            ORDER BY artifact, try_cast(bucket AS integer) NULLS LAST, bucket
        """).fetchall() if table_exists(con, 'staged_trace_founders_depth10_summary') else []
        staged_merges = con.execute("""
            SELECT merge_tx_hash, epoch_no, root_combo, traced_input_rows, min_input_depth, max_input_depth
            FROM staged_cross_entity_merges_depth10
            ORDER BY epoch_no, merge_tx_hash
            LIMIT 12
        """).fetchall() if table_exists(con, 'staged_cross_entity_merges_depth10') else []
        staged_comparison = con.execute("""
            SELECT staged_path, staged_rows, legacy_distinct_txs, overlap_txs, legacy_missing_txs, staged_extra_txs
            FROM staged_cross_merge_comparison
            ORDER BY staged_path
        """).fetchall() if table_exists(con, 'staged_cross_merge_comparison') else []
        iog_bag_summary = con.execute("""
            SELECT current_utxo_rows, current_ada, min_depth, max_depth, distinct_stake_addresses, byron_or_no_stake_ada, shelley_staked_ada
            FROM iog_current_bag_depth14_summary
        """).fetchall() if table_exists(con, 'iog_current_bag_depth14_summary') else []
        iog_pool_validation = con.execute("""
            SELECT label, ticker_name, is_retired_at_tip, retiring_epoch, latest_epoch_stake_epoch, latest_epoch_active_stake_ada
            FROM iog_pool_state_validation
            ORDER BY label
        """).fetchall() if table_exists(con, 'iog_pool_state_validation') else []
        iog_confidence_bands = con.execute("""
            SELECT band, ada, confidence, interpretation
            FROM iog_current_bag_depth14_confidence_bands
        """).fetchall() if table_exists(con, 'iog_current_bag_depth14_confidence_bands') else []
        iog_class_summary = con.execute("""
            SELECT heuristic_class, clusters, utxos, ada
            FROM iog_current_bag_depth14_heuristic_class_summary
            ORDER BY ada DESC
        """).fetchall() if table_exists(con, 'iog_current_bag_depth14_heuristic_class_summary') else []
    finally:
        con.close()

    content = f"""# Cardano Genesis Forensics — Community Summary

This report is generated from the v2 ABCDE DuckDB artifact. It is designed for community review, not attribution theater.

## Core caveat

This project maps on-chain flows and delegation behavior. It does **not** prove legal ownership, intent, misconduct, or who controlled a wallet off-chain.

## Seed registry

{md_table(['seed_id', 'label', 'amount_ada', 'source_type', 'grade'], seed_rows)}

## First-spend behavior

{md_table(['seed_id', 'first_spend_tx_hash', 'dormant_hours', 'input_count'], first_spends)}

## Fourth-entry direct co-spend receipt

The fourth-entry first spend directly co-spends with an EMURGO-descended UTxO.

{md_table(['input_source_tx_hash', 'input_value_lovelace', 'descendant_of_seed_id', 'emurgo_trace_depth'], cospend)}

## Governance delegation surface

Lifetime target counts by root seed:

### SPO pool targets

{md_table(['root_seed_id', 'distinct_pool_targets'], spo_summary)}

### DRep targets

{md_table(['root_seed_id', 'distinct_drep_targets'], drep_summary)}

## Top latest SPO targets by traced stake credential count

{md_table(['root_seed_id', 'ticker', 'pool_name', 'pool_id', 'latest_stake_addresses'], top_spo)}

## Top latest DRep targets by traced stake credential count

{md_table(['root_seed_id', 'drep_id', 'anchor_url', 'latest_stake_addresses'], top_drep)}

## Trace-derived latest SPO target rollup by preserved current value

This is **not live pool stake**. It joins preserved trace current-unspent receipts to the latest observed delegation target per traced stake credential. Use `iog_pool_state_validation.csv` for live IOG1/IOG2 pool-state claims.

{md_table(['root_seed_id', 'ticker', 'pool_name', 'pool_id', 'trace_value_ada'], top_spo_value)}

## Trace-derived latest DRep target rollup by preserved current value

{md_table(['root_seed_id', 'drep_id', 'anchor_url', 'trace_value_ada'], top_drep_value)}

## Staged trace audit cuts

The repo includes server-side staged extraction so deeper traces can be materialized one frontier at a time with minimum-depth dedupe. Depth 10 is an `AUDIT_REVIEW_CUT`, not the final full-founder inventory.

### Depth-10 all-root staged summary

{md_table(['artifact', 'bucket', 'rows'], staged_depth10)}

### Depth-10 named-founder-only staged summary

{md_table(['artifact', 'bucket', 'rows'], staged_founders_depth10)}

### First staged depth-10 cross-entity merge rows

{md_table(['merge_tx_hash', 'epoch_no', 'root_combo', 'traced_input_rows', 'min_depth', 'max_depth'], staged_merges)}

### Founder-only staged comparison against preserved 521-row baseline

{md_table(['staged_path', 'staged_rows', 'legacy_txs', 'overlap_txs', 'legacy_missing_txs', 'staged_extra_txs'], staged_comparison)}

Interpretation: depth 14 recovers most baseline hashes but also produces many additional candidates. Those extras are an `AUDIT_CANDIDATE_SET`, not claims.

## IOG current bag audit cut

Depth-14 staged trace membership, filtered to live-unspent UTxOs at ABCDE/db-sync tip, currently resolves to the following IOG-descended balance. This is trace membership, not proof of current beneficial ownership.

{md_table(['current_utxos', 'current_ada', 'min_depth', 'max_depth', 'stake_addresses', 'byron_or_no_stake_ada', 'shelley_staked_ada'], iog_bag_summary)}

### IOG confidence bands

{md_table(['band', 'ada', 'confidence', 'interpretation'], iog_confidence_bands)}

### IOG heuristic class summary

{md_table(['heuristic_class', 'clusters', 'utxos', 'ada'], iog_class_summary)}

### IOG pool-state validation

This corrects the old shortcut: trace-derived latest-delegation rollups are not live pool stake.

{md_table(['label', 'ticker', 'retired_at_tip', 'retiring_epoch', 'stake_epoch', 'active_stake_ada'], iog_pool_validation)}

## Reproduce

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements/base.txt
bash scripts/rebuild_seed_cut.sh
python3 scripts/verify_finding_queries.py
python3 scripts/build_community_report.py
```

## Source files

- generated locally: `data/abcde_genesis_seed_registry.duckdb`
- `data/small/*.csv`
- `data/manifests/*.json`
- `findings/*.md`
"""
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(content)
    print(f'wrote {OUT.relative_to(ROOT)}')


if __name__ == '__main__':
    main()

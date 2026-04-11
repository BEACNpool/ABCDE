# Genesis Founders Dataset

**Published:** 2026-03-31  
**Data source:** Cardano db-sync (block 13,215,210, 2026-03-28 00:27:10 UTC)  
**Coverage:** Transaction lineage from Genesis (2017-09-23) to sync tip

---

## Contents

### IOG (Input Output Hong Kong)
- Genesis anchor: `fa2d2a70c0b5fd45cb6c3989f02813061f9d27f15f30ecddd38780c59f413c62`
- Genesis allocation: 2,463,071,701 ADA
- Trace depth: 11 hops
- Total edges: 102,502
- Current unspent outputs: 55,041
- Unique Shelley stake addresses: 11,873

### EMURGO
- Genesis anchor: `242608fc18552a4ac83adabcef7155f3b909e83d469ce89735db8f11d3637e38`
- Genesis allocation: 2,074,165,643 ADA
- Trace depth: 13 hops
- Total edges: 101,756
- Current unspent outputs: 49,089
- Unique Shelley stake addresses: 6,216

### EMURGO_2
- Genesis anchor: `5ec95a53fa3bb7dc56864bb6e75f369f00aa20e8d8cdc3b66b2fb88ec1b225ef`
- Genesis allocation: 781,381,495 ADA
- Trace depth: 13 hops
- Total edges: 85,980
- Current unspent outputs: 49,089
- Unique Shelley stake addresses: 6,216
- **Note:** 100% stake address overlap with EMURGO (see deoverlap_analysis.csv)

### CF (Cardano Foundation)
- Genesis anchor: `208c7d54c1c24059c9314ddbe866edc80adcb8894539b27b6a1430d5c078b998`
- Genesis allocation: 648,176,763 ADA
- Trace depth: 15 hops
- Total edges: 115,315
- Current unspent outputs: 23,005
- Unique Shelley stake addresses: 2,174

---

## File Descriptions

### Cross-Seed Analysis

**exchange-analysis/**
- Combined classification layer across the current frontier UTxOs from IOG, EMURGO, and CF
- Includes aggregate summaries and categorized `current_unspent` exports
- Files: `summary_aggregate.csv`, `summary_by_seed.csv`, categorized frontier CSVs, pipeline status log

### Per-Seed Files

**trace_summary.json**
- Aggregate statistics for the trace
- Fields: run_id, seed, anchor_tx, genesis_allocation_ada, max_hop_traced, total_edges, unique_shelley_stake_addresses, first_shelley_hop, frontier_unspent_outputs, delegation_records, drep_records, earliest_tx, latest_tx

**trace_edges_part1.csv / trace_edges_part2.csv**
- Complete lineage of all traced transaction outputs
- Fields: source_tx_out_id, spending_tx_id, descendant_tx_out_id, descendant_address, descendant_value (lovelace), stake_address_id, hop_depth, block_time, epoch_no

**current_unspent.csv**
- All currently unspent outputs at trace frontier
- Fields: dest_tx_out_id, dest_address, dest_stake_address, lovelace, ada, block_time, epoch_no, dest_tx_hash, last_traced_hop, era

**delegation_history.csv**
- Pool delegation events for all Shelley stake addresses found in trace
- Fields: addr_id, stake_address, pool_id_bech32, active_epoch_no, tx_hash, block_time, epoch_no

**drep_delegation.csv**
- DRep delegation events for all Shelley stake addresses found in trace
- Fields: stake_address, addr_id, drep_id_bech32, epoch_no, tx_hash, block_time

**deoverlap_analysis.csv** (EMURGO_2 only)
- Analysis of stake address overlap between EMURGO and EMURGO_2
- Fields: stake_address, overlap_type, emurgo_outputs, emurgo2_outputs, emurgo_ada, emurgo2_ada

---

## Data Collection Method

1. Start with Genesis anchor transaction hash
2. Find all spending transactions via `tx_in` table
3. Extract all descendant outputs via `tx_out` table
4. Record lineage edges with values, addresses, stake identities
5. Continue hop-by-hop until all branches reach: Shelley era, current unspent state, or dust threshold
6. Extract pool delegation history from `delegation` table for all Shelley stake addresses
7. Extract DRep delegation history from `delegation_vote` table
8. Export all results to CSV/JSON

See [METHODOLOGY.md](./METHODOLOGY.md) for SQL queries and reproducibility instructions.

---

## Verification

All transaction hashes and stake addresses in this dataset can be independently verified using:
- [Cardanoscan](https://cardanoscan.io)
- [Cardano Explorer](https://explorer.cardano.org)
- [Koios API](https://koios.rest)
- Direct db-sync queries

---

## Row Counts

| File | IOG | EMURGO | EMURGO_2 | CF |
|------|-----|--------|----------|-----|
| trace_edges (total) | 102,502 | 101,756 | 85,980 | 115,315 |
| current_unspent | 55,041 | 49,089 | 49,089 | 23,005 |
| delegation_history | 24,149 | 14,761 | 14,761 | 6,519 |
| drep_delegation | 1,994 | 1,089 | 1,089 | 511 |
| deoverlap_analysis | N/A | N/A | 6,216 | N/A |

**Cross-seed publication note:** `exchange-analysis/` is a combined frontier layer for **IOG + EMURGO + CF**. `EMURGO_2` is not yet included in that directory.

---

## Interpretation Guardrails

When reading this dataset, keep these quantities separate:
- **Genesis allocation** — original ADA assigned at genesis
- **Current traced frontier value** — descendant-state value in currently traced frontier outputs
- **Exchange-classified frontier value** — frontier value falling into the published exchange heuristic bucket
- **Provable sold amount** — realized sale volume directly proven from on-chain evidence

These values are **not interchangeable**.

Claim-strength note:
- frontier totals and row counts are published as direct receipts / deterministic transforms
- exchange buckets are heuristic classifications
- ownership, sale execution, intent, and coordination claims require additional evidence beyond the frontier tables alone

## Data Integrity

All files:
- Contain only db-sync-derived facts
- Include transaction hashes for verification
- Use standard bech32 address encoding
- Report values in lovelace (1 ADA = 1,000,000 lovelace)

No interpretation, analysis, or claims are made in the data files themselves.

## Exchange Analysis Layer

A combined classification layer is published at [`exchange-analysis/`](./exchange-analysis/).

This layer currently classifies the frontier UTxOs from **IOG + EMURGO + CF** into:
- `EXCHANGE`
- `ACTIVE_ECOSYSTEM`
- `DORMANT_STAKED`
- `BYRON_DORMANT`

`EMURGO_2` is not yet included in that combined classification directory.

# Exchange Analysis Layer

**Published:** 2026-03-31  
**Source dataset:** `datasets/genesis-founders/`  
**Input scope:** Combined current frontier UTxOs from IOG, EMURGO, and CF  
**Total frontier analyzed:** 127,135 UTxOs  
**Total ADA analyzed:** 54,352,889,291.73 ADA

---

## Purpose

This directory contains a classification layer applied to the current frontier UTxOs in the genesis founders dataset.

Categories assigned:
- `EXCHANGE`
- `ACTIVE_ECOSYSTEM`
- `DORMANT_STAKED`
- `BYRON_DORMANT`

These outputs are derived from db-sync state plus deterministic classification rules applied to the frontier snapshot.

---

## Files

- `summary_aggregate.csv` — aggregate category totals across the combined frontier
- `summary_by_seed.csv` — per-seed category totals
- `iog_current_unspent_categorized.csv` — IOG current frontier with category columns added
- `emurgo_current_unspent_categorized.csv` — EMURGO current frontier with category columns added
- `cf_current_unspent_categorized.csv` — CF current frontier with category columns added
- `PIPELINE_STATUS.txt` — execution checkpoint log from the classification run
- `FINAL_REPORT.txt` — generated run summary

---

## Aggregate Results

| Category | UTxOs | ADA | Percent |
|---|---:|---:|---:|
| BYRON_DORMANT | 84,543 | 30,549,323,428.28204000 | 56.21 |
| EXCHANGE | 13,570 | 16,544,973,055.88839200 | 30.44 |
| DORMANT_STAKED | 28,872 | 7,181,068,760.94875000 | 13.21 |
| ACTIVE_ECOSYSTEM | 150 | 77,524,046.60796000 | 0.14 |

---

## Method Notes

The run was completed end-to-end and validated against the combined frontier row count and ADA totals.

Validation receipts:
- frontier rows: `127,135`
- classified rows: `127,135`
- ADA total match: `54,352,889,291.73`
- NULL categories: `0`

Operational note:
- the initial Step 6 export join was corrected during the run
- final categorized exports join on `dest_tx_out_id`, which is the proper unique frontier key for export reconstruction

---

## Scope Note

This layer currently covers the combined frontier run built from:
- IOG
- EMURGO
- CF

`EMURGO_2` is not yet included in this classification directory.

# F05 — Bounded Depth-3 Merge Inventory Review Cut

## Claim

The v2 merge-classification logic can derive a cross-seed consuming transaction from trace membership. On the current bounded depth-3 artifact, it identifies the known EMURGO/fourth-entry convergence transaction.

## Audit labels

- **Finding status:** REVIEW_CUT
- **Claim grade:** FACT within bounded depth-3 scope
- **Artifact class:** AUDIT_REVIEW_CUT

This is not the full named-founder cross-seed inventory yet.

## Evidence

- `data/small/bounded_trace_depth3_db.csv`
- `data/small/seed_first_spend_inputs_db.csv`
- `data/abcde_genesis_seed_registry.duckdb`

## Reproduce

```sql
.read sql/10_findings/bounded_trace_depth3_merge_inventory.duckdb.sql
```

Expected current result: one row for a pairwise EMURGO + fourth-entry merge candidate.

## Why this matters

This proves the audit inventory should be generated from trace membership rather than copied from archived cross-merge CSVs. The next step is scaling `bounded_trace_depth3` into a full deduplicated trace membership table and comparing against the baseline in `docs/archive/13_CROSS_MERGE_MILESTONE.md`.

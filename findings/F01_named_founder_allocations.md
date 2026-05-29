# F01 — Named Founder Allocations

## Claim

The canonical named-founder and fourth-entry seed transactions are listed in `anchors.yaml` and can be verified against db-sync or the published DuckDB cut.

## Grade

FACT for named-founder anchor transactions. STRONG_INFERENCE for the fourth-entry sale-ticket classification.

## Reproduce

```sql
SELECT seed_id, label, tx_hash, amount_ada, source_type, evidence_grade
FROM seed_registry
ORDER BY amount_ada DESC;
```

## Legacy source

`legacy/2026-05-20-pre-v2-import/findings/F01_named_founder_allocations.md`

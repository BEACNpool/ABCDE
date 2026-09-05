# F04 — Bounded Depth-3 Trace Overlap Review Cut

## Claim

The v2 bounded depth-3 review-cut trace finds UTxOs reachable from both the EMURGO seed and the fourth-entry seed, confirming that the review-cut extractor can surface the known convergence pattern from generic trace output.

## Audit labels

- **Finding status:** REVIEW_CUT
- **Claim grade:** FACT within bounded depth-3 scope
- **Artifact class:** AUDIT_REVIEW_CUT

This is a bounded audit cut, not a full Genesis-wide overlap inventory.

## Evidence

- `data/small/bounded_trace_depth3_db.csv`
- `data/abcde_genesis_seed_registry.duckdb`

## Reproduce

```sql
SELECT
  tx_hash,
  tx_out_index,
  count(DISTINCT seed_id) AS seed_count,
  string_agg(DISTINCT seed_id, ', ' ORDER BY seed_id) AS seed_ids,
  max(value_lovelace) AS value_lovelace,
  min(depth) AS min_depth,
  max(depth) AS max_depth
FROM bounded_trace_depth3_db
GROUP BY tx_hash, tx_out_index
HAVING count(DISTINCT seed_id) > 1
ORDER BY seed_count DESC, value_lovelace DESC;
```

## Limitation

Because the trace is capped at depth 3, absence from this table does not imply no later overlap.

-- Runs against data/abcde_genesis_seed_registry.duckdb.
-- UTxOs reachable from more than one seed within the bounded depth-3 pilot trace.
SELECT
  tx_hash,
  tx_out_index,
  count(DISTINCT seed_id) AS seed_count,
  string_agg(DISTINCT seed_id, ', ' ORDER BY seed_id) AS seed_ids,
  max(value_lovelace) AS value_lovelace,
  min(depth) AS min_depth,
  max(depth) AS max_depth
FROM bounded_trace_depth3
GROUP BY tx_hash, tx_out_index
HAVING count(DISTINCT seed_id) > 1
ORDER BY seed_count DESC, value_lovelace DESC;

-- Runs against data/abcde_genesis.duckdb.
SELECT
  seed_id,
  depth,
  count(*) AS utxo_rows,
  sum(value_lovelace) AS value_lovelace
FROM bounded_trace_depth3_db
GROUP BY seed_id, depth
ORDER BY seed_id, depth;

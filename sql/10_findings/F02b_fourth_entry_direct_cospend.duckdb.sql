-- Runs against data/abcde_genesis_seed_registry.duckdb.
SELECT
  fourth_first_spend_tx_hash,
  input_source_tx_hash,
  input_value_lovelace,
  descendant_of_seed_id,
  emurgo_trace_depth,
  emurgo_path
FROM fourth_entry_direct_cospend
ORDER BY input_value_lovelace DESC;

-- Runs against generated data/abcde_genesis_seed_registry.duckdb.
SELECT
  t.root_seed_id,
  t.pool_id_bech32,
  m.ticker_name,
  m.pool_name,
  t.latest_distinct_stake_addresses_with_current_value,
  t.current_ada
FROM governance_spo_latest_value_targets t
LEFT JOIN governance_pool_metadata m USING (pool_id_bech32)
ORDER BY t.current_lovelace DESC, t.root_seed_id
LIMIT 100;

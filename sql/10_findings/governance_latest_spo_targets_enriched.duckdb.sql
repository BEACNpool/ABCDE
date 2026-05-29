-- Runs against data/abcde_genesis_seed_registry.duckdb.
SELECT
  t.root_seed_id,
  t.pool_id_bech32,
  m.ticker_name,
  m.pool_name,
  t.latest_distinct_stake_addresses,
  t.latest_active_epoch_min,
  t.latest_active_epoch_max
FROM governance_spo_latest_targets t
LEFT JOIN governance_pool_metadata m USING (pool_id_bech32)
ORDER BY t.latest_distinct_stake_addresses DESC, t.root_seed_id
LIMIT 100;

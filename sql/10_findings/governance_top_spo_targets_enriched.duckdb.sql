-- Runs against data/abcde_genesis_seed_registry.duckdb.
SELECT
  t.root_seed_id,
  t.pool_id_bech32,
  m.ticker_name,
  m.pool_name,
  m.homepage,
  t.distinct_stake_addresses,
  t.delegation_cert_count,
  t.first_active_epoch,
  t.last_active_epoch
FROM governance_spo_delegation_targets t
LEFT JOIN governance_pool_metadata m USING (pool_id_bech32)
ORDER BY t.distinct_stake_addresses DESC, t.delegation_cert_count DESC, t.root_seed_id
LIMIT 50;

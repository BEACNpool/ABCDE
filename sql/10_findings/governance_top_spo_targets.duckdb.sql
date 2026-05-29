-- Runs against data/abcde_genesis_seed_registry.duckdb.
SELECT
  root_seed_id,
  pool_id_bech32,
  distinct_stake_addresses,
  delegation_cert_count,
  first_active_epoch,
  last_active_epoch
FROM governance_spo_delegation_targets
ORDER BY distinct_stake_addresses DESC, delegation_cert_count DESC, root_seed_id
LIMIT 50;

-- Runs against data/abcde_genesis_seed_registry.duckdb.
SELECT
  root_seed_id,
  count(*) AS distinct_pool_targets,
  sum(distinct_stake_addresses) AS summed_distinct_stake_addresses_per_pool,
  min(first_active_epoch) AS first_active_epoch,
  max(last_active_epoch) AS last_active_epoch
FROM governance_spo_delegation_targets
GROUP BY root_seed_id
ORDER BY root_seed_id;

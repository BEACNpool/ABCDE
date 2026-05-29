-- Runs against data/abcde_genesis_seed_registry.duckdb.
SELECT
  root_seed_id,
  count(*) AS distinct_drep_targets,
  sum(distinct_stake_addresses) AS summed_distinct_stake_addresses_per_drep,
  min(first_epoch) AS first_epoch,
  max(last_epoch) AS last_epoch
FROM governance_drep_delegation_targets
GROUP BY root_seed_id
ORDER BY root_seed_id;

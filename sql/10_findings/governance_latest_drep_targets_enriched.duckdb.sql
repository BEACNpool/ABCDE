-- Runs against data/abcde_genesis_seed_registry.duckdb.
SELECT
  t.root_seed_id,
  t.drep_id_bech32,
  m.voting_anchor_url,
  t.latest_distinct_stake_addresses,
  t.latest_epoch_min,
  t.latest_epoch_max
FROM governance_drep_latest_targets t
LEFT JOIN governance_drep_metadata m USING (drep_id_bech32)
ORDER BY t.latest_distinct_stake_addresses DESC, t.root_seed_id
LIMIT 100;

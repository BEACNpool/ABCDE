-- Runs against generated data/abcde_genesis_seed_registry.duckdb.
SELECT
  t.root_seed_id,
  t.drep_id_bech32,
  m.voting_anchor_url,
  t.latest_distinct_stake_addresses_with_current_value,
  t.current_ada
FROM governance_drep_latest_value_targets t
LEFT JOIN governance_drep_metadata m USING (drep_id_bech32)
ORDER BY t.current_lovelace DESC, t.root_seed_id
LIMIT 100;

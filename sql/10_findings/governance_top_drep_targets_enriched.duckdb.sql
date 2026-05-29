-- Runs against data/abcde_genesis_seed_registry.duckdb.
SELECT
  t.root_seed_id,
  t.drep_id_bech32,
  m.voting_anchor_url,
  m.voting_anchor_data_hash_hex,
  t.distinct_stake_addresses,
  t.delegation_cert_count,
  t.first_epoch,
  t.last_epoch
FROM governance_drep_delegation_targets t
LEFT JOIN governance_drep_metadata m USING (drep_id_bech32)
ORDER BY t.distinct_stake_addresses DESC, t.delegation_cert_count DESC, t.root_seed_id
LIMIT 50;

SELECT
  rank_registered,
  drep_id_bech32,
  round(voting_power_ada, 6) AS voting_power_ada,
  current_delegator_count,
  round(latest_retention_ratio, 6) AS latest_retention_ratio,
  voting_anchor_url
FROM governance_top_drep_profiles_current
WHERE profile_class = 'registered'
ORDER BY rank_registered
LIMIT 10;

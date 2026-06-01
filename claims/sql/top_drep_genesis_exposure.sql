SELECT
  rank_overall,
  profile_class,
  drep_id_bech32,
  dedup_current_stake_credentials,
  round(dedup_current_ada, 6) AS dedup_current_ada,
  root_overlap_summary
FROM governance_top_drep_genesis_trace_exposure
ORDER BY dedup_current_ada DESC, rank_overall
LIMIT 10;

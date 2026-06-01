-- DRep genesis-trace exposure with delegation observation windows.
--
-- These are rollup windows, not per-UTXO chain positions. They are useful for
-- spotting common timing bands across roots before drilling into db-sync.
SELECT
  e.rank_overall,
  e.profile_class,
  e.drep_id_bech32,
  e.root_seed_id,
  e.current_ada,
  e.latest_stake_credentials_with_current_value,
  t.first_epoch,
  t.last_epoch,
  t.first_observed_block_time,
  t.last_observed_block_time,
  l.latest_epoch_min,
  l.latest_epoch_max,
  l.latest_observed_block_time_min,
  l.latest_observed_block_time_max
FROM governance_top_drep_genesis_trace_exposure_by_root e
LEFT JOIN governance_drep_delegation_targets t
  ON t.root_seed_id = e.root_seed_id
 AND t.drep_id_bech32 = e.drep_id_bech32
LEFT JOIN governance_drep_latest_targets l
  ON l.root_seed_id = e.root_seed_id
 AND l.drep_id_bech32 = e.drep_id_bech32
WHERE e.current_ada > 0
ORDER BY e.current_ada DESC, e.drep_id_bech32, e.root_seed_id;

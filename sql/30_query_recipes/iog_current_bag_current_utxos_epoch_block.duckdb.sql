-- IOG depth-14 current bag: per-current-UTXO chain position and delegation context.
--
-- This is the drilldown behind the confidence bands. It provides exact creation
-- epoch/block/time for each currently unspent traced UTxO, plus latest observed
-- SPO/DRep delegation context for the UTxO's stake credential where available.
SELECT
  root_seed_id,
  stake_address,
  tx_hash,
  tx_out_index,
  current_ada,
  min_depth,
  epoch_no,
  block_no,
  block_time_utc,
  latest_pool_id_bech32,
  latest_pool_active_epoch_no,
  latest_pool_delegation_epoch_no,
  latest_pool_delegation_block_no,
  latest_pool_delegation_time_utc,
  latest_drep_id_bech32,
  latest_drep_delegation_epoch_no,
  latest_drep_delegation_block_no,
  latest_drep_delegation_time_utc,
  active_stake_epoch,
  active_stake_ada
FROM iog_current_bag_depth14_current_utxos
ORDER BY current_ada DESC, min_depth, epoch_no, block_no, tx_hash, tx_out_index
LIMIT 500;

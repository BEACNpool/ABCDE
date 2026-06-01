-- IOG current-bag temporal coverage summary.
--
-- The current public cut now includes a per-current-UTXO table with exact
-- creation epoch/block/time. Confidence bands remain interpretation rollups;
-- temporal anomaly claims should cite the per-UTXO table below.
SELECT
  count(*) AS current_utxos,
  count(DISTINCT stake_address) FILTER (WHERE stake_address IS NOT NULL) AS stake_addresses,
  sum(current_lovelace) / 1000000.0 AS current_ada,
  min(min_depth) AS min_depth,
  max(min_depth) AS max_depth,
  min(epoch_no) AS earliest_utxo_epoch,
  max(epoch_no) AS latest_utxo_epoch,
  min(block_no) AS earliest_utxo_block,
  max(block_no) AS latest_utxo_block,
  min(block_time_utc) AS earliest_utxo_time_utc,
  max(block_time_utc) AS latest_utxo_time_utc,
  count(*) FILTER (WHERE latest_pool_id_bech32 IS NOT NULL) AS rows_with_latest_pool,
  count(*) FILTER (WHERE latest_drep_id_bech32 IS NOT NULL) AS rows_with_latest_drep,
  count(*) FILTER (WHERE active_stake_lovelace IS NOT NULL) AS rows_with_active_stake
FROM iog_current_bag_depth14_current_utxos;

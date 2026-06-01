-- IOG current-bag depth cut: what timing is and is not in the public artifact.
--
-- The current depth-14 bag exports are value/depth/classification rollups.
-- They do not contain per-UTXO epoch_no/block_no/block_time_utc. Use this query
-- to keep AI answers honest, then run a deeper db-sync extraction if a specific
-- anomaly needs exact chain-position receipts.
SELECT
  'summary' AS artifact,
  CAST(min_depth AS VARCHAR) AS depth_or_band,
  current_utxo_rows AS rows_or_utxos,
  current_ada,
  NULL::BIGINT AS epoch_no,
  NULL::BIGINT AS block_no,
  NULL::TIMESTAMP AS block_time_utc,
  'depth/value summary only; no per-UTXO chain position in this public table' AS timing_status
FROM iog_current_bag_depth14_summary
UNION ALL
SELECT
  'by_depth' AS artifact,
  CAST(min_depth AS VARCHAR) AS depth_or_band,
  current_utxos AS rows_or_utxos,
  current_ada,
  NULL::BIGINT AS epoch_no,
  NULL::BIGINT AS block_no,
  NULL::TIMESTAMP AS block_time_utc,
  'depth/value summary only; no per-UTXO chain position in this public table' AS timing_status
FROM iog_current_bag_depth14_by_depth
UNION ALL
SELECT
  'confidence_band' AS artifact,
  band AS depth_or_band,
  NULL::BIGINT AS rows_or_utxos,
  ada AS current_ada,
  NULL::BIGINT AS epoch_no,
  NULL::BIGINT AS block_no,
  NULL::TIMESTAMP AS block_time_utc,
  'confidence/value summary only; exact epoch/block requires db-sync drilldown' AS timing_status
FROM iog_current_bag_depth14_confidence_bands
ORDER BY artifact, depth_or_band;

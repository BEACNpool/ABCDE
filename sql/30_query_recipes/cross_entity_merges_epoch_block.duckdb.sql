-- Cross-entity merge candidates with exact chain position.
--
-- Depth says how far traced inputs were from their roots. The epoch/block
-- columns say when the merge transaction happened.
SELECT
  'all_roots_depth10' AS scope,
  merge_tx_hash,
  epoch_no,
  block_no,
  block_time_utc,
  root_combo,
  root_count,
  traced_input_rows,
  traced_input_lovelace / 1000000.0 AS traced_input_ada,
  min_input_depth,
  max_input_depth
FROM staged_cross_entity_merges_depth10
UNION ALL
SELECT
  'named_founders_depth10' AS scope,
  merge_tx_hash,
  epoch_no,
  block_no,
  block_time_utc,
  root_combo,
  root_count,
  traced_input_rows,
  traced_input_lovelace / 1000000.0 AS traced_input_ada,
  min_input_depth,
  max_input_depth
FROM staged_cross_entity_merges_founders_depth10
ORDER BY epoch_no, block_no, merge_tx_hash, scope;

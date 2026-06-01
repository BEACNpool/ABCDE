-- Trace hops with chain position.
--
-- Use this when checking whether a path is merely "N hops away" or whether
-- those hops cluster in the same epoch/block window.
SELECT
  seed_id,
  label,
  depth,
  epoch_no,
  block_no,
  block_time_utc,
  tx_hash,
  tx_out_index,
  value_lovelace / 1000000.0 AS value_ada,
  stake_address,
  path
FROM bounded_trace_depth3_db
ORDER BY seed_id, depth, epoch_no, block_no, tx_hash, tx_out_index;

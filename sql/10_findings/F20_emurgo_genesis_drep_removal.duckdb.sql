-- Runs against the published ABCDE Genesis DuckDB cut.
SELECT metric, value FROM (
  SELECT 'official_leftover_ada' AS metric, ada AS value
  FROM emurgo_genesis_leftover_by_drep_bucket
  WHERE bucket = 'EMURGO official'
  UNION ALL
  SELECT 'community7_removal_ada', abs(delta_ada)
  FROM emurgo_drep_epoch_deltas
  WHERE "window" = 'community7_removal' AND label = 'community7_total'
  UNION ALL
  SELECT 'official_drop_may2025_ada', abs(delta_ada)
  FROM emurgo_drep_epoch_deltas
  WHERE "window" = 'own_drep_genesis_removal'
)
ORDER BY metric;

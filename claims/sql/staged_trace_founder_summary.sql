SELECT
  artifact,
  bucket,
  rows
FROM staged_trace_founders_depth14_summary
ORDER BY artifact, bucket;

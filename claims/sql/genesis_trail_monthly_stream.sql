WITH terminal_traces AS (
  SELECT seed_label, hop_tx_hash
  FROM (
    SELECT
      seed_label,
      hop_tx_hash,
      row_number() OVER (PARTITION BY seed_label ORDER BY depth DESC) AS rank
    FROM genesis_trail_payment_dominant_traces
  )
  WHERE rank = 1
), metrics(metric, value_numeric, unit, evidence_grade) AS (
  SELECT
    'payment_sized_recipient_outputs',
    count(*)::BIGINT,
    'count',
    'FACT'
  FROM genesis_trail_recipient_outputs
  WHERE is_payment_sized

  UNION ALL

  SELECT
    'recipient_lifetime_received',
    sum(value_lovelace)::BIGINT,
    'lovelace',
    'FACT'
  FROM genesis_trail_recipient_outputs

  UNION ALL

  SELECT
    'recipient_forwarded_to_hub',
    sum(value_lovelace)::BIGINT,
    'lovelace',
    'FACT'
  FROM genesis_trail_recipient_forwarding

  UNION ALL

  SELECT
    'hub_gross_received',
    received_lovelace::BIGINT,
    'lovelace',
    'FACT'
  FROM genesis_trail_hub_summary

  UNION ALL

  SELECT
    stream_label,
    output_lovelace::BIGINT,
    'lovelace',
    'FACT'
  FROM genesis_trail_stream_bridges
  WHERE stream_label IN ('iogp_reward_to_burst', 'burst_to_hub')

  UNION ALL

  SELECT
    'payment_paths_to_iog_genesis',
    count(*)::BIGINT,
    'count',
    'FACT'
  FROM terminal_traces
  WHERE hop_tx_hash =
    '0ae3da29711600e94a33fb7441d2e76876a9a1e98b5ebdefbf2e3bc535617616'
)
SELECT metric, value_numeric, unit, evidence_grade
FROM metrics
ORDER BY metric;

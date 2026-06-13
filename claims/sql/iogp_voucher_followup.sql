WITH metrics(metric, value_lovelace, evidence_grade) AS (
  SELECT
    'iogp_declared_pledge',
    declared_pledge_lovelace,
    'FACT'
  FROM iogp_pool_registration

  UNION ALL

  SELECT
    'iogp_reward_epoch_250_active_stake',
    active_stake_lovelace,
    'FACT'
  FROM iogp_pool_epoch_stake
  WHERE epoch_no = 250 AND stake_role = 'reward_account'

  UNION ALL

  SELECT
    'voucher_stake_lifetime_received',
    stake_received_lovelace,
    'FACT'
  FROM voucher_wallet_profile

  UNION ALL

  SELECT
    'voucher_2023_10_05_funder_inflow',
    associated_lovelace,
    'FACT'
  FROM voucher_wallet_counterparty_summary
  WHERE direction = 'inbound'
    AND counterparty = 'stake1uy6yzwsxxc28lfms0qmpxvyz9a7y770rtcqx9y96m42cttqwvp4m5'

  UNION ALL

  SELECT
    'voucher_forward_endpoint_outflow',
    associated_lovelace,
    'FACT'
  FROM voucher_wallet_counterparty_summary
  WHERE direction = 'outbound'
    AND counterparty = 'addr1vymu4620q8vqf4xsstfrk6dy72787syvezet8ujsdj2k3jsfvlx47'

  UNION ALL

  SELECT
    'iogp_reward_to_burst',
    output_lovelace,
    'FACT'
  FROM iogp_reward_wallet_destinations
  WHERE destination = 'stake1uycla9q3glrugp48cq2r7awemjxepvj4lxs4emw5qmpsclc4tpe52'
)
SELECT
  metric,
  value_lovelace,
  round(value_lovelace / 1000000.0, 6) AS value_ada,
  evidence_grade
FROM metrics
ORDER BY metric;

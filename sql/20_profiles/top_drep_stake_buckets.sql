-- Current delegator stake-size buckets for the same top-10 DRep set.
WITH latest_dd AS (
  SELECT max(epoch_no) AS epoch_no FROM public.drep_distr
), latest_stake_epoch AS (
  SELECT max(epoch_no) AS epoch_no FROM public.epoch_stake
), current_dist AS (
  SELECT
    row_number() OVER (ORDER BY dd.amount DESC, dh.view) AS rank_overall,
    dh.id AS drep_hash_id,
    dh.view AS drep_id_bech32,
    dd.epoch_no AS drep_distribution_epoch,
    dd.amount AS voting_power_lovelace
  FROM public.drep_distr dd
  JOIN public.drep_hash dh ON dh.id = dd.hash_id
  JOIN latest_dd l ON l.epoch_no = dd.epoch_no
), top_dreps AS (
  SELECT *
  FROM current_dist
  ORDER BY voting_power_lovelace DESC, drep_id_bech32
  LIMIT 10
), latest_vote AS (
  SELECT DISTINCT ON (dv.addr_id)
    dv.addr_id,
    dv.drep_hash_id
  FROM public.delegation_vote dv
  JOIN public.tx tx ON tx.id = dv.tx_id
  JOIN public.block b ON b.id = tx.block_id
  ORDER BY dv.addr_id, b.time DESC, tx.id DESC, dv.cert_index DESC
), current_stake AS (
  SELECT
    lv.drep_hash_id,
    lv.addr_id,
    coalesce(es.amount, 0) AS active_stake_lovelace
  FROM latest_vote lv
  JOIN latest_stake_epoch se ON true
  LEFT JOIN public.epoch_stake es ON es.addr_id = lv.addr_id AND es.epoch_no = se.epoch_no
), bucketed AS (
  SELECT
    td.drep_distribution_epoch,
    (SELECT epoch_no FROM latest_stake_epoch) AS epoch_stake_epoch,
    td.rank_overall,
    CASE WHEN td.drep_id_bech32 LIKE 'drep_always_%' THEN 'system' ELSE 'registered' END AS profile_class,
    td.drep_id_bech32,
    CASE
      WHEN cs.active_stake_lovelace >= 50000000000000 THEN 1
      WHEN cs.active_stake_lovelace >= 10000000000000 THEN 2
      WHEN cs.active_stake_lovelace >= 1000000000000 THEN 3
      WHEN cs.active_stake_lovelace >= 100000000000 THEN 4
      WHEN cs.active_stake_lovelace >= 10000000000 THEN 5
      WHEN cs.active_stake_lovelace >= 1000000000 THEN 6
      WHEN cs.active_stake_lovelace > 0 THEN 7
      ELSE 8
    END AS bucket_order,
    CASE
      WHEN cs.active_stake_lovelace >= 50000000000000 THEN '>=50M'
      WHEN cs.active_stake_lovelace >= 10000000000000 THEN '10M-50M'
      WHEN cs.active_stake_lovelace >= 1000000000000 THEN '1M-10M'
      WHEN cs.active_stake_lovelace >= 100000000000 THEN '100k-1M'
      WHEN cs.active_stake_lovelace >= 10000000000 THEN '10k-100k'
      WHEN cs.active_stake_lovelace >= 1000000000 THEN '1k-10k'
      WHEN cs.active_stake_lovelace > 0 THEN '<1k'
      ELSE '0/no active stake'
    END AS active_stake_bucket,
    cs.active_stake_lovelace
  FROM top_dreps td
  JOIN current_stake cs ON cs.drep_hash_id = td.drep_hash_id
)
SELECT
  now() AT TIME ZONE 'UTC' AS query_timestamp_utc,
  drep_distribution_epoch,
  epoch_stake_epoch,
  rank_overall,
  profile_class,
  drep_id_bech32,
  bucket_order,
  active_stake_bucket,
  count(*) AS current_delegator_count,
  sum(active_stake_lovelace) AS active_stake_lovelace,
  round(sum(active_stake_lovelace) / 1000000.0, 6) AS active_stake_ada
FROM bucketed
GROUP BY
  drep_distribution_epoch,
  epoch_stake_epoch,
  rank_overall,
  profile_class,
  drep_id_bech32,
  bucket_order,
  active_stake_bucket
ORDER BY rank_overall, bucket_order;

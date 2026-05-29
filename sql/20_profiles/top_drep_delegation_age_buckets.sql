-- Current delegator latest-vote-delegation age buckets for the same top-10 DRep set.
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
    dv.drep_hash_id,
    b.epoch_no AS latest_vote_epoch
  FROM public.delegation_vote dv
  JOIN public.tx tx ON tx.id = dv.tx_id
  JOIN public.block b ON b.id = tx.block_id
  ORDER BY dv.addr_id, b.time DESC, tx.id DESC, dv.cert_index DESC
), current_stake AS (
  SELECT
    lv.drep_hash_id,
    lv.addr_id,
    lv.latest_vote_epoch,
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
      WHEN cs.latest_vote_epoch <= 520 THEN 1
      WHEN cs.latest_vote_epoch <= 540 THEN 2
      WHEN cs.latest_vote_epoch <= 560 THEN 3
      WHEN cs.latest_vote_epoch <= 580 THEN 4
      WHEN cs.latest_vote_epoch <= 600 THEN 5
      WHEN cs.latest_vote_epoch <= 620 THEN 6
      ELSE 7
    END AS age_bucket_order,
    CASE
      WHEN cs.latest_vote_epoch <= 520 THEN '<=520'
      WHEN cs.latest_vote_epoch <= 540 THEN '521-540'
      WHEN cs.latest_vote_epoch <= 560 THEN '541-560'
      WHEN cs.latest_vote_epoch <= 580 THEN '561-580'
      WHEN cs.latest_vote_epoch <= 600 THEN '581-600'
      WHEN cs.latest_vote_epoch <= 620 THEN '601-620'
      ELSE '621+'
    END AS latest_vote_epoch_bucket,
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
  age_bucket_order,
  latest_vote_epoch_bucket,
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
  age_bucket_order,
  latest_vote_epoch_bucket
ORDER BY rank_overall, age_bucket_order;

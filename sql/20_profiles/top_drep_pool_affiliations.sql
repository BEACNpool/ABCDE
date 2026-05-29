-- Top active SPO pool affiliations for current delegators of each top-10 DRep.
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
), active_pool AS (
  SELECT
    lv.drep_hash_id,
    es.addr_id,
    es.amount AS active_stake_lovelace,
    ph.view AS pool_id_bech32
  FROM latest_vote lv
  JOIN latest_stake_epoch se ON true
  JOIN public.epoch_stake es ON es.addr_id = lv.addr_id AND es.epoch_no = se.epoch_no
  JOIN public.pool_hash ph ON ph.id = es.pool_id
  WHERE es.amount > 0
), latest_pool_meta AS (
  SELECT DISTINCT ON (ph.view)
    ph.view AS pool_id_bech32,
    ocpd.ticker_name,
    ocpd.json ->> 'name' AS pool_name,
    ocpd.json ->> 'homepage' AS homepage
  FROM public.pool_hash ph
  LEFT JOIN public.pool_update pu ON pu.hash_id = ph.id
  LEFT JOIN public.pool_metadata_ref pmr ON pmr.id = pu.meta_id
  LEFT JOIN public.off_chain_pool_data ocpd ON ocpd.pmr_id = pmr.id
  ORDER BY ph.view, pu.active_epoch_no DESC NULLS LAST, pu.id DESC NULLS LAST
), ranked AS (
  SELECT
    td.drep_distribution_epoch,
    (SELECT epoch_no FROM latest_stake_epoch) AS epoch_stake_epoch,
    td.rank_overall,
    CASE WHEN td.drep_id_bech32 LIKE 'drep_always_%' THEN 'system' ELSE 'registered' END AS profile_class,
    td.drep_id_bech32,
    ap.pool_id_bech32,
    m.ticker_name,
    m.pool_name,
    m.homepage,
    count(*) AS current_delegator_count,
    sum(ap.active_stake_lovelace) AS active_stake_lovelace,
    round(sum(ap.active_stake_lovelace) / 1000000.0, 6) AS active_stake_ada,
    row_number() OVER (
      PARTITION BY td.drep_id_bech32
      ORDER BY sum(ap.active_stake_lovelace) DESC, count(*) DESC, ap.pool_id_bech32
    ) AS pool_rank_for_drep
  FROM top_dreps td
  JOIN active_pool ap ON ap.drep_hash_id = td.drep_hash_id
  LEFT JOIN latest_pool_meta m ON m.pool_id_bech32 = ap.pool_id_bech32
  GROUP BY
    td.drep_distribution_epoch,
    td.rank_overall,
    td.drep_id_bech32,
    ap.pool_id_bech32,
    m.ticker_name,
    m.pool_name,
    m.homepage
)
SELECT
  now() AT TIME ZONE 'UTC' AS query_timestamp_utc,
  drep_distribution_epoch,
  epoch_stake_epoch,
  rank_overall,
  profile_class,
  drep_id_bech32,
  pool_rank_for_drep,
  pool_id_bech32,
  ticker_name,
  pool_name,
  homepage,
  current_delegator_count,
  active_stake_lovelace,
  active_stake_ada
FROM ranked
WHERE pool_rank_for_drep <= 10
ORDER BY rank_overall, pool_rank_for_drep;

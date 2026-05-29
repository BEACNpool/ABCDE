-- Current top DRep profile snapshot from cardano-db-sync.
-- Produces one row per top DRep by latest drep_distr voting power.
WITH latest_dd AS (
  SELECT max(epoch_no) AS epoch_no FROM public.drep_distr
), latest_stake_epoch AS (
  SELECT max(epoch_no) AS epoch_no FROM public.epoch_stake
), tip AS (
  SELECT max(time) AS dbsync_tip_utc, max(epoch_no) AS dbsync_tip_epoch FROM public.block
), current_dist AS (
  SELECT
    row_number() OVER (ORDER BY dd.amount DESC, dh.view) AS rank_overall,
    CASE
      WHEN dh.view LIKE 'drep_always_%' THEN NULL
      ELSE sum(CASE WHEN dh.view NOT LIKE 'drep_always_%' THEN 1 ELSE 0 END)
        OVER (ORDER BY dd.amount DESC, dh.view ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
    END AS rank_registered,
    dd.epoch_no AS drep_distribution_epoch,
    dd.active_until,
    dh.id AS drep_hash_id,
    encode(dh.raw, 'hex') AS drep_hash_hex,
    dh.view AS drep_id_bech32,
    dh.has_script,
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
    b.epoch_no AS latest_vote_epoch,
    b.time AS latest_vote_time_utc,
    encode(tx.hash, 'hex') AS latest_vote_tx_hash
  FROM public.delegation_vote dv
  JOIN public.tx tx ON tx.id = dv.tx_id
  JOIN public.block b ON b.id = tx.block_id
  ORDER BY dv.addr_id, b.time DESC, tx.id DESC, dv.cert_index DESC
), current_delegators AS (
  SELECT
    drep_hash_id,
    count(*) AS current_delegator_count,
    min(latest_vote_epoch) AS earliest_current_vote_epoch,
    max(latest_vote_epoch) AS latest_current_vote_epoch
  FROM latest_vote
  GROUP BY drep_hash_id
), historical_delegators AS (
  SELECT
    drep_hash_id,
    count(DISTINCT addr_id) AS historical_delegator_count,
    count(*) AS historical_vote_cert_count
  FROM public.delegation_vote
  GROUP BY drep_hash_id
), current_stake AS (
  SELECT
    lv.drep_hash_id,
    count(es.addr_id) FILTER (WHERE es.amount > 0) AS current_active_stake_credentials,
    coalesce(sum(es.amount), 0) AS current_active_stake_lovelace
  FROM latest_vote lv
  JOIN latest_stake_epoch se ON true
  LEFT JOIN public.epoch_stake es ON es.addr_id = lv.addr_id AND es.epoch_no = se.epoch_no
  GROUP BY lv.drep_hash_id
), latest_reg AS (
  SELECT DISTINCT ON (dh.id)
    dh.id AS drep_hash_id,
    dr.deposit,
    va.url AS voting_anchor_url,
    encode(va.data_hash, 'hex') AS voting_anchor_data_hash_hex,
    encode(tx.hash, 'hex') AS registration_tx_hash,
    b.epoch_no AS registration_epoch,
    b.time AS registration_time_utc
  FROM public.drep_hash dh
  LEFT JOIN public.drep_registration dr ON dr.drep_hash_id = dh.id
  LEFT JOIN public.voting_anchor va ON va.id = dr.voting_anchor_id
  LEFT JOIN public.tx tx ON tx.id = dr.tx_id
  LEFT JOIN public.block b ON b.id = tx.block_id
  ORDER BY dh.id, b.time DESC NULLS LAST, dr.id DESC NULLS LAST
)
SELECT
  now() AT TIME ZONE 'UTC' AS query_timestamp_utc,
  tip.dbsync_tip_utc,
  tip.dbsync_tip_epoch,
  td.drep_distribution_epoch,
  (SELECT epoch_no FROM latest_stake_epoch) AS epoch_stake_epoch,
  td.rank_overall,
  td.rank_registered,
  CASE WHEN td.drep_id_bech32 LIKE 'drep_always_%' THEN 'system' ELSE 'registered' END AS profile_class,
  td.drep_id_bech32,
  td.drep_hash_hex,
  td.has_script,
  td.voting_power_lovelace,
  round(td.voting_power_lovelace / 1000000.0, 6) AS voting_power_ada,
  td.active_until,
  coalesce(cd.current_delegator_count, 0) AS current_delegator_count,
  coalesce(hd.historical_delegator_count, 0) AS historical_delegator_count,
  coalesce(hd.historical_vote_cert_count, 0) AS historical_vote_cert_count,
  CASE
    WHEN coalesce(hd.historical_delegator_count, 0) = 0 THEN NULL
    ELSE round(cd.current_delegator_count::numeric / hd.historical_delegator_count, 6)
  END AS latest_retention_ratio,
  coalesce(cs.current_active_stake_credentials, 0) AS current_active_stake_credentials,
  coalesce(cs.current_active_stake_lovelace, 0) AS current_active_stake_lovelace,
  round(coalesce(cs.current_active_stake_lovelace, 0) / 1000000.0, 6) AS current_active_stake_ada,
  cd.earliest_current_vote_epoch,
  cd.latest_current_vote_epoch,
  lr.voting_anchor_url,
  lr.voting_anchor_data_hash_hex,
  lr.registration_tx_hash,
  lr.registration_epoch,
  lr.registration_time_utc
FROM top_dreps td
CROSS JOIN tip
LEFT JOIN current_delegators cd ON cd.drep_hash_id = td.drep_hash_id
LEFT JOIN historical_delegators hd ON hd.drep_hash_id = td.drep_hash_id
LEFT JOIN current_stake cs ON cs.drep_hash_id = td.drep_hash_id
LEFT JOIN latest_reg lr ON lr.drep_hash_id = td.drep_hash_id
ORDER BY td.rank_overall;

-- FACT: current epoch stake and observed DRep certificates for a frozen
-- historical selector. Selection ancestry is not present-day ownership.
-- Epoch stake and the latest DRep certificate are different time concepts.
SELECT s.epoch_no, s.drep_id, count(*) AS selected_credentials,
       sum(CAST(s.amount_lovelace AS DECIMAL(38,0))) AS active_stake_lovelace,
       min(k.selection_snapshot_utc) AS selection_snapshot_first_utc,
       max(k.selection_snapshot_utc) AS selection_snapshot_last_utc,
       min(s.drep_cert_time) AS earliest_observed_latest_drep_certificate,
       max(s.drep_cert_time) AS latest_observed_latest_drep_certificate
FROM founding_cohort_stake s
JOIN founding_cohort_keys k ON k.stake_address = s.stake_address
GROUP BY s.epoch_no, s.drep_id
ORDER BY active_stake_lovelace DESC, s.drep_id;

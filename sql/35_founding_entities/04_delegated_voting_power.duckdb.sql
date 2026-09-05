-- FACT: epoch voting distribution, including stake delegated by other holders.
-- These amounts measure represented voting power, not assets owned by the DRep.
-- Historical distributions are included only for the named DReps; the latest
-- epoch includes all DReps. No percentage uses a partial historical denominator.
WITH latest_epoch AS (
  SELECT max(epoch_no) AS epoch_no FROM founding_drep_distribution
), named AS (
  SELECT d.epoch_no, i.entity, i.group_name, d.drep_id, d.drep_hash_id, d.has_script, d.active_until,
         CAST(d.amount_lovelace AS DECIMAL(38,0)) AS delegated_voting_lovelace
  FROM founding_drep_distribution d
  JOIN latest_epoch e ON e.epoch_no = d.epoch_no
  JOIN founding_drep_identity i ON i.drep_hash_id = d.drep_hash_id AND i.has_script = d.has_script
)
SELECT *,
       CAST(delegated_voting_lovelace * CAST(0.000001 AS DECIMAL(7,6))
            AS DECIMAL(38,6)) AS delegated_voting_ada,
       sum(delegated_voting_lovelace) OVER (PARTITION BY group_name)
            AS group_delegated_voting_lovelace
FROM named
ORDER BY group_name, entity;

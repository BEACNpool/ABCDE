-- Catalog of every on-chain governance action (Conway gov_action_proposal),
-- with lifecycle epochs and anchor URL. Small, committable reference table
-- that lets proposal-level rollups be joined to human-meaningful actions.
--
-- No stage schema needed; reads public.* only.
SELECT
  to_char(now() AT TIME ZONE 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS"Z"') AS snapshot_utc,
  gap.id AS gov_action_proposal_id,
  encode(tx.hash, 'hex') AS proposal_tx_hash,
  gap.index AS proposal_index,
  gap.type AS proposal_type,
  b.epoch_no AS proposed_epoch,
  gap.deposit AS deposit_lovelace,
  gap.expiration AS expiration_epoch,
  gap.ratified_epoch,
  gap.enacted_epoch,
  gap.dropped_epoch,
  gap.expired_epoch,
  va.url AS anchor_url,
  encode(va.data_hash, 'hex') AS anchor_data_hash_hex
FROM public.gov_action_proposal gap
JOIN public.tx tx ON tx.id = gap.tx_id
JOIN public.block b ON b.id = tx.block_id
LEFT JOIN public.voting_anchor va ON va.id = gap.voting_anchor_id
ORDER BY gap.id;

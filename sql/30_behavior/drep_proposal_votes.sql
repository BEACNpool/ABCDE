-- DRep votes on governance proposals for joining to the Genesis governance surface.
SELECT
  gap.id AS gov_action_proposal_id,
  encode(gap_tx.hash, 'hex') AS proposal_tx_hash,
  gap.index AS proposal_index,
  gap.type AS proposal_type,
  gap.expiration AS proposal_expiration_epoch,
  dh.id AS drep_hash_id,
  dh.view AS drep_id_bech32,
  vp.vote,
  vote_block.epoch_no AS vote_epoch,
  vote_block.time AS vote_time_utc,
  encode(vote_tx.hash, 'hex') AS vote_tx_hash
FROM public.voting_procedure vp
JOIN public.gov_action_proposal gap ON gap.id = vp.gov_action_proposal_id
JOIN public.tx gap_tx ON gap_tx.id = gap.tx_id
JOIN public.tx vote_tx ON vote_tx.id = vp.tx_id
JOIN public.block vote_block ON vote_block.id = vote_tx.block_id
JOIN public.drep_hash dh ON dh.id = vp.drep_voter
WHERE vp.voter_role = 'DRep'
  AND vp.drep_voter IS NOT NULL
ORDER BY vote_time_utc DESC, proposal_tx_hash, proposal_index, drep_id_bech32;

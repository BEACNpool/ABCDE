-- Counterevidence: inspect every difference among shared latest-valid ballots.
-- Follow both rationale URLs; matching choices alone cannot identify motives.
WITH ranked AS (
  SELECT *, row_number() OVER (
    PARTITION BY drep_hash_id, gov_action_tx_hash, gov_action_index
    ORDER BY ballot_tx_id DESC, ballot_index DESC
  ) AS ballot_rank
  FROM founding_votes
  WHERE invalid IS NULL
), latest AS (
  SELECT * FROM ranked WHERE ballot_rank = 1
)
SELECT a.gov_action_tx_hash, a.gov_action_index, a.gov_action_type,
       ai.entity AS entity_a, a.vote AS vote_a,
       a.ballot_tx_hash AS ballot_tx_a, a.rationale_url AS rationale_a,
       bi.entity AS entity_b, b.vote AS vote_b,
       b.ballot_tx_hash AS ballot_tx_b, b.rationale_url AS rationale_b
FROM latest a
JOIN latest b ON a.gov_action_tx_hash = b.gov_action_tx_hash
             AND a.gov_action_index = b.gov_action_index AND a.drep_id < b.drep_id
JOIN founding_drep_identity ai ON ai.drep_hash_id = a.drep_hash_id AND ai.has_script = a.has_script
JOIN founding_drep_identity bi ON bi.drep_hash_id = b.drep_hash_id AND bi.has_script = b.has_script
WHERE a.vote <> b.vote
ORDER BY a.gov_action_tx_hash, a.gov_action_index, entity_a, entity_b;

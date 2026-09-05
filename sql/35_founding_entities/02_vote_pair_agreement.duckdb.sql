-- FACT: latest valid ballot per DRep/action, ordered as db-sync records it.
-- Denominator is shared actions only. A missing vote is never an Abstain.
-- Agreement is behavior; it does not establish ownership, coordination or intent.
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
SELECT ai.entity AS entity_a, bi.entity AS entity_b,
       a.drep_id AS drep_a, b.drep_id AS drep_b,
       count(*) AS shared_actions,
       count(*) FILTER (WHERE a.vote = b.vote) AS same_votes,
       count(*) FILTER (WHERE a.vote <> b.vote) AS different_votes,
       count(*) FILTER (WHERE (a.vote = 'Yes' AND b.vote = 'No')
                           OR (a.vote = 'No' AND b.vote = 'Yes')) AS opposing_yes_no
FROM latest a
JOIN latest b ON a.gov_action_tx_hash = b.gov_action_tx_hash
             AND a.gov_action_index = b.gov_action_index AND a.drep_id < b.drep_id
JOIN founding_drep_identity ai ON ai.drep_hash_id = a.drep_hash_id AND ai.has_script = a.has_script
JOIN founding_drep_identity bi ON bi.drep_hash_id = b.drep_hash_id AND bi.has_script = b.has_script
GROUP BY ai.entity, bi.entity, a.drep_id, b.drep_id
ORDER BY entity_a, entity_b;

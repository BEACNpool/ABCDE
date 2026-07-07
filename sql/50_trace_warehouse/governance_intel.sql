-- governance_intel.sql — governance intelligence for the DRep mission.
-- Two matviews on the abcde warehouse (governance schema), exposed via the API:
--   * treasury_flow      — per-epoch treasury pot + true inflow/outflow (replaces
--                          Sundae GraphQL scraping; feeds the DRep treasury regime).
--   * proposal_vote_power — STAKE-WEIGHTED DRep vote tally per proposal (the
--                          drep_*_pct that Koios /proposal_voting_summary gives;
--                          completes the cardano-gov Koios cutover).
-- Read-only on public.*. Grading: pot balances and votes are FACT; stake weighting
-- uses the latest drep_distr snapshot (approximation of the enactment-epoch stake).
\set ON_ERROR_STOP on
SET work_mem = '512MB';
CREATE SCHEMA IF NOT EXISTS governance;

-- ---- treasury flow (true inflow = pot delta + enacted withdrawals) --------
DROP MATERIALIZED VIEW IF EXISTS governance.treasury_flow;
CREATE MATERIALIZED VIEW governance.treasury_flow AS
WITH pots AS (
  SELECT DISTINCT ON (epoch_no) epoch_no,
         treasury / 1e6 AS treasury_ada,
         reserves / 1e6 AS reserves_ada
  FROM public.ada_pots
  ORDER BY epoch_no, id DESC
),
wd AS (
  SELECT b.epoch_no, sum(tw.amount) / 1e6 AS withdrawn_ada
  FROM public.treasury_withdrawal tw
  JOIN public.gov_action_proposal gap ON gap.id = tw.gov_action_proposal_id
  JOIN public.tx t    ON t.id = gap.tx_id
  JOIN public.block b ON b.id = t.block_id
  GROUP BY b.epoch_no
)
SELECT p.epoch_no,
       p.treasury_ada,
       p.reserves_ada,
       p.treasury_ada - lag(p.treasury_ada) OVER (ORDER BY p.epoch_no) AS treasury_delta_ada,
       COALESCE(w.withdrawn_ada, 0)                                    AS withdrawn_ada,
       -- true inflow = balance change + what left via withdrawals
       (p.treasury_ada - lag(p.treasury_ada) OVER (ORDER BY p.epoch_no))
         + COALESCE(w.withdrawn_ada, 0)                               AS true_inflow_ada
FROM pots p
LEFT JOIN wd w ON w.epoch_no = p.epoch_no
ORDER BY p.epoch_no;
CREATE UNIQUE INDEX ON governance.treasury_flow (epoch_no);

-- ---- stake-weighted DRep vote power per proposal --------------------------
DROP MATERIALIZED VIEW IF EXISTS governance.proposal_vote_power;
CREATE MATERIALIZED VIEW governance.proposal_vote_power AS
WITH latest_stake AS (        -- most recent DRep stake snapshot
  SELECT hash_id, amount FROM public.drep_distr
  WHERE epoch_no = (SELECT max(epoch_no) FROM public.drep_distr)
),
drep_votes AS (               -- latest vote per (proposal, DRep)
  SELECT DISTINCT ON (vp.gov_action_proposal_id, vp.drep_voter)
         vp.gov_action_proposal_id, vp.drep_voter, vp.vote
  FROM public.voting_procedure vp
  WHERE vp.voter_role = 'DRep' AND vp.drep_voter IS NOT NULL
  ORDER BY vp.gov_action_proposal_id, vp.drep_voter, vp.tx_id DESC, vp.index DESC
)
SELECT encode(t.hash, 'hex')                                    AS proposal_tx_hash,
       ga.index                                                 AS proposal_index,
       ga.type                                                  AS proposal_type,
       count(*) FILTER (WHERE dv.vote = 'Yes')                  AS drep_yes_count,
       count(*) FILTER (WHERE dv.vote = 'No')                   AS drep_no_count,
       count(*) FILTER (WHERE dv.vote = 'Abstain')              AS drep_abstain_count,
       round(sum(ls.amount) FILTER (WHERE dv.vote = 'Yes')     / 1e6) AS drep_yes_ada,
       round(sum(ls.amount) FILTER (WHERE dv.vote = 'No')      / 1e6) AS drep_no_ada,
       round(sum(ls.amount) FILTER (WHERE dv.vote = 'Abstain') / 1e6) AS drep_abstain_ada
FROM drep_votes dv
JOIN public.gov_action_proposal ga ON ga.id = dv.gov_action_proposal_id
JOIN public.tx t    ON t.id = ga.tx_id
LEFT JOIN latest_stake ls ON ls.hash_id = dv.drep_voter
GROUP BY 1, 2, 3;
CREATE UNIQUE INDEX ON governance.proposal_vote_power (proposal_tx_hash, proposal_index);

GRANT SELECT ON governance.treasury_flow, governance.proposal_vote_power TO web_anon;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA governance GRANT SELECT ON TABLES TO web_anon;
NOTIFY pgrst, 'reload schema';

\echo === treasury flow (recent) ===
SELECT epoch_no, round(treasury_ada) treasury_ada, round(withdrawn_ada) withdrawn, round(true_inflow_ada) true_inflow
FROM governance.treasury_flow ORDER BY epoch_no DESC LIMIT 5;
\echo === most-contested proposals by DRep stake ===
SELECT proposal_type, drep_yes_ada, drep_no_ada FROM governance.proposal_vote_power
ORDER BY (COALESCE(drep_yes_ada,0)+COALESCE(drep_no_ada,0)) DESC LIMIT 5;

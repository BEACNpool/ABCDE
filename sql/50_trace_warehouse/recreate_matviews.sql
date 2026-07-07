-- Recreate the governance/explorer matviews dropped between 2026-03 and 2026-06.
-- Source: infra/ABCDE_BUILD_REFERENCE_V2.md, with three fixes for CONCURRENTLY
-- refresh: unique indexes on fee_revenue_trailing and treasury_withdrawals, and
-- DISTINCT ON in drep_registry (re-registrations would break its unique index).
\set ON_ERROR_STOP on
SET work_mem = '1GB';

CREATE SCHEMA IF NOT EXISTS explorer;
CREATE SCHEMA IF NOT EXISTS governance;

DROP MATERIALIZED VIEW IF EXISTS explorer.epoch_stats;
CREATE MATERIALIZED VIEW explorer.epoch_stats AS
SELECT
    b.epoch_no,
    COUNT(DISTINCT b.id)                AS block_count,
    COUNT(DISTINCT t.id)                AS tx_count,
    COALESCE(SUM(t.fee), 0) / 1e6      AS total_fees_ada,
    COALESCE(AVG(t.fee), 0) / 1e6      AS avg_fee_ada,
    COALESCE(MAX(t.fee), 0) / 1e6      AS max_fee_ada,
    MIN(b.time)                         AS epoch_start,
    MAX(b.time)                         AS epoch_end
FROM public.block b
LEFT JOIN public.tx t ON t.block_id = b.id
WHERE b.epoch_no IS NOT NULL
GROUP BY b.epoch_no
ORDER BY b.epoch_no;
CREATE UNIQUE INDEX ON explorer.epoch_stats (epoch_no);
COMMENT ON MATERIALIZED VIEW explorer.epoch_stats IS
  'Per-epoch block/tx/fee summary. Refresh every 6h. Requires tx sync complete.';

DROP MATERIALIZED VIEW IF EXISTS explorer.fee_revenue_trailing;
CREATE MATERIALIZED VIEW explorer.fee_revenue_trailing AS
SELECT
    DATE_TRUNC('month', b.time)     AS month,
    b.epoch_no,
    COUNT(DISTINCT t.id)            AS tx_count,
    SUM(t.fee) / 1e6                AS fees_ada,
    AVG(t.fee) / 1e6                AS avg_fee_ada
FROM public.block b
JOIN public.tx t ON t.block_id = b.id
WHERE b.time >= NOW() - INTERVAL '13 months'
GROUP BY DATE_TRUNC('month', b.time), b.epoch_no
ORDER BY month DESC, b.epoch_no DESC;
CREATE UNIQUE INDEX ON explorer.fee_revenue_trailing (month, epoch_no);
COMMENT ON MATERIALIZED VIEW explorer.fee_revenue_trailing IS
  'Monthly fee revenue trailing 13 months. Source of truth for fee revenue claims vs NCL debate.';

DROP MATERIALIZED VIEW IF EXISTS governance.treasury_withdrawals;
CREATE MATERIALIZED VIEW governance.treasury_withdrawals AS
SELECT
    tw.id,
    b.epoch_no                          AS epoch_no,
    b.time                              AS withdrawal_time,
    sa.view                             AS stake_address,
    tw.amount / 1e6                     AS amount_ada,
    encode(t.hash, 'hex')               AS proposal_tx_hash,
    gap.index                           AS proposal_index,
    gap.type                            AS proposal_type,
    b.block_no,
    b.slot_no
FROM public.treasury_withdrawal tw
JOIN public.gov_action_proposal gap ON gap.id = tw.gov_action_proposal_id
JOIN public.tx t                    ON t.id = gap.tx_id
JOIN public.block b                 ON b.id = t.block_id
JOIN public.stake_address sa        ON sa.id = tw.stake_address_id;
CREATE UNIQUE INDEX ON governance.treasury_withdrawals (id);
CREATE INDEX ON governance.treasury_withdrawals (epoch_no);
CREATE INDEX ON governance.treasury_withdrawals (stake_address);
CREATE INDEX ON governance.treasury_withdrawals (withdrawal_time);

DROP MATERIALIZED VIEW IF EXISTS governance.drep_registry;
CREATE MATERIALIZED VIEW governance.drep_registry AS
SELECT DISTINCT ON (dh.id)
    dh.id                               AS drep_hash_id,
    encode(dh.raw, 'hex')               AS drep_id_hex,
    dh.view                             AS drep_id_bech32,
    dr.deposit / 1e6                    AS deposit_ada,
    va.url                              AS anchor_url,
    encode(va.data_hash, 'hex')         AS anchor_hash,
    b.time                              AS registered_at,
    b.epoch_no                          AS registration_epoch
FROM public.drep_hash dh
JOIN public.drep_registration dr    ON dr.drep_hash_id = dh.id
JOIN public.tx t                    ON t.id = dr.tx_id
JOIN public.block b                 ON b.id = t.block_id
LEFT JOIN public.voting_anchor va   ON va.id = dr.voting_anchor_id
ORDER BY dh.id, b.time DESC;
CREATE UNIQUE INDEX ON governance.drep_registry (drep_hash_id);
CREATE INDEX ON governance.drep_registry (drep_id_bech32);
COMMENT ON MATERIALIZED VIEW governance.drep_registry IS
  'Latest registration per DRep (DISTINCT ON drep_hash_id, newest block wins).';

DROP MATERIALIZED VIEW IF EXISTS governance.drep_votes;
CREATE MATERIALIZED VIEW governance.drep_votes AS
SELECT
    encode(dh.raw, 'hex')               AS drep_id_hex,
    dh.view                             AS drep_id_bech32,
    vp.vote,
    encode(gap_tx.hash, 'hex')          AS proposal_tx_hash,
    ga.index                            AS proposal_index,
    ga.type                             AS proposal_type,
    encode(vp_tx.hash, 'hex')           AS vote_tx_hash,
    vp.index                            AS vote_index,
    b.time                              AS vote_time,
    b.epoch_no                          AS vote_epoch
FROM public.voting_procedure vp
JOIN public.drep_hash dh                ON dh.id = vp.drep_voter
JOIN public.gov_action_proposal ga      ON ga.id = vp.gov_action_proposal_id
JOIN public.tx gap_tx                   ON gap_tx.id = ga.tx_id
JOIN public.tx vp_tx                    ON vp_tx.id = vp.tx_id
JOIN public.block b                     ON b.id = vp_tx.block_id
ORDER BY b.time DESC;
CREATE INDEX ON governance.drep_votes (drep_id_bech32);
CREATE INDEX ON governance.drep_votes (vote_epoch);
CREATE INDEX ON governance.drep_votes (proposal_tx_hash);
CREATE INDEX ON governance.drep_votes (vote);
-- (vote_tx_hash, proposal, drep) is NOT unique on-chain: tx 4434102b8a… holds two
-- votes by the same DRep on the same proposal. (tx, vote index) is the true key.
CREATE UNIQUE INDEX ON governance.drep_votes (vote_tx_hash, vote_index);

DROP MATERIALIZED VIEW IF EXISTS governance.proposals;
CREATE MATERIALIZED VIEW governance.proposals AS
SELECT
    ga.id                               AS proposal_id,
    ga.type                             AS proposal_type,
    encode(t.hash, 'hex')               AS proposal_tx_hash,
    ga.index,
    ga.deposit / 1e6                    AS deposit_ada,
    b.time                              AS submitted_at,
    b.epoch_no                          AS submitted_epoch,
    ga.expiration                       AS expiration_epoch,
    ga.ratified_epoch, ga.enacted_epoch, ga.dropped_epoch, ga.expired_epoch,
    CASE WHEN ga.enacted_epoch  IS NOT NULL THEN 'enacted'
         WHEN ga.ratified_epoch IS NOT NULL THEN 'ratified'
         WHEN ga.dropped_epoch  IS NOT NULL OR ga.expired_epoch IS NOT NULL THEN 'expired'
         ELSE 'active' END              AS status,
    va.url                              AS anchor_url,
    encode(va.data_hash, 'hex')         AS anchor_hash,
    (SELECT COUNT(*) FROM public.voting_procedure vp
     WHERE vp.gov_action_proposal_id = ga.id AND vp.vote = 'Yes')     AS yes_votes,
    (SELECT COUNT(*) FROM public.voting_procedure vp
     WHERE vp.gov_action_proposal_id = ga.id AND vp.vote = 'No')      AS no_votes,
    (SELECT COUNT(*) FROM public.voting_procedure vp
     WHERE vp.gov_action_proposal_id = ga.id AND vp.vote = 'Abstain') AS abstain_votes
FROM public.gov_action_proposal ga
JOIN public.tx t                ON t.id = ga.tx_id
JOIN public.block b             ON b.id = t.block_id
LEFT JOIN public.voting_anchor va ON va.id = ga.voting_anchor_id
ORDER BY b.time DESC;
CREATE UNIQUE INDEX ON governance.proposals (proposal_id);
CREATE INDEX ON governance.proposals (proposal_type);
CREATE INDEX ON governance.proposals (submitted_epoch);
CREATE INDEX ON governance.proposals (status);

DROP MATERIALIZED VIEW IF EXISTS governance.drep_delegation_snapshot;
CREATE MATERIALIZED VIEW governance.drep_delegation_snapshot AS
WITH latest_epoch AS (
  SELECT MAX(epoch_no) AS epoch_no FROM public.drep_distr
)
SELECT
    encode(dh.raw, 'hex')          AS drep_id_hex,
    dh.view                        AS drep_id_bech32,
    dd.epoch_no,
    dd.amount / 1e6                AS total_stake_ada
FROM public.drep_distr dd
JOIN latest_epoch le ON le.epoch_no = dd.epoch_no
JOIN public.drep_hash dh ON dh.id = dd.hash_id
ORDER BY total_stake_ada DESC NULLS LAST;
CREATE UNIQUE INDEX ON governance.drep_delegation_snapshot (drep_id_hex);
CREATE INDEX ON governance.drep_delegation_snapshot (total_stake_ada DESC);

CREATE TABLE IF NOT EXISTS governance.genesis_address_tags (
    id                  SERIAL PRIMARY KEY,
    address             TEXT NOT NULL UNIQUE,
    tag                 TEXT NOT NULL,
    initial_balance_ada NUMERIC(20,6),
    notes               TEXT,
    confidence          TEXT CHECK (confidence IN ('FACT','STRONG_INFERENCE','UNKNOWN')),
    source_tx_hash      TEXT,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS genesis_address_tags_tag_idx ON governance.genesis_address_tags (tag);
CREATE INDEX IF NOT EXISTS genesis_address_tags_confidence_idx ON governance.genesis_address_tags (confidence);

\echo === matview row counts ===
SELECT 'epoch_stats' v, count(*) FROM explorer.epoch_stats
UNION ALL SELECT 'fee_revenue_trailing', count(*) FROM explorer.fee_revenue_trailing
UNION ALL SELECT 'treasury_withdrawals', count(*) FROM governance.treasury_withdrawals
UNION ALL SELECT 'drep_registry', count(*) FROM governance.drep_registry
UNION ALL SELECT 'drep_votes', count(*) FROM governance.drep_votes
UNION ALL SELECT 'proposals', count(*) FROM governance.proposals
UNION ALL SELECT 'drep_delegation_snapshot', count(*) FROM governance.drep_delegation_snapshot;

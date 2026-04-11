-- File: queries/drep_overlap_only_ada_weighted.sql
-- Run against: cexplorer_replica (host: ${DB_HOST}, port 5432)
-- Purpose: ADA-weighted DRep delegation breakdown for cross-entity overlap addresses only
--          (stake addresses appearing in 2+ founder trace frontiers simultaneously)
-- As-of: epoch 620 (2026-04-11)
-- SAFE: read-only, no writes
--
-- Prerequisites:
--   CREATE TEMP TABLE emurgo2_stake (stake_address text PRIMARY KEY);
--   \copy emurgo2_stake(stake_address) FROM 'data/raw/emurgo2/emurgo2_stake_addrs_import.csv' CSV
--   (EMURGO_2 is not in frontier_combined_persist; load from CSV)
--
-- Overlap tier definition:
--   entity_count=2 -> appears in exactly 2 of 4 founder frontiers
--   entity_count=3 -> appears in exactly 3 of 4 founder frontiers
--   entity_count=4 -> appears in all 4 founder frontiers
--
-- These addresses cannot result from independent retail purchases —
-- shared wallet infrastructure is required to appear in multiple founder traces.
--
-- EXCLUSION NOTE: The EMURGO|EMURGO_2-only tier (entity_count=2, entities='EMURGO|EMURGO_2')
-- is present in Result B for reference but is EXCLUDED from Result A summary totals.
-- Reason: the ABCDE investigation established 100% frontier identity between EMURGO and
-- EMURGO_2 (Section 2 — EMURGO_2 Genesis Entry). All EMURGO Shelley stake addresses appear
-- in EMURGO_2 and vice versa. This overlap therefore confirms the same finding already
-- established and does not constitute new cross-entity coordination evidence.
-- Including it in the cross-entity summary would inflate the shared-control metric
-- with same-entity overlap. Result A WHERE clause: entities <> 'EMURGO|EMURGO_2'.

WITH latest_epoch AS (
    SELECT MAX(no) AS epoch_no FROM public.epoch
),

-- One row per (stake_addr, entity) — de-duplicated UNION for EMURGO vs EMURGO_2
all_tagged AS (
    SELECT dest_stake_address AS stake_addr, seed AS entity
    FROM public.frontier_combined_persist
    WHERE dest_stake_address IS NOT NULL
    UNION
    SELECT stake_address, 'EMURGO_2'
    FROM emurgo2_stake
),

-- Overlap set: addresses in 2+ entity frontiers
overlap_set AS (
    SELECT
        stake_addr,
        COUNT(DISTINCT entity)                  AS entity_count,
        STRING_AGG(entity, '|' ORDER BY entity) AS entities
    FROM all_tagged
    GROUP BY stake_addr
    HAVING COUNT(DISTINCT entity) >= 2
),

-- Latest DRep delegation per stake address (highest tx_id wins)
current_drep AS (
    SELECT DISTINCT ON (dv.addr_id)
        dv.addr_id,
        dh.view AS drep_view
    FROM public.delegation_vote dv
    JOIN public.drep_hash dh ON dh.id = dv.drep_hash_id
    ORDER BY dv.addr_id, dv.tx_id DESC
),

-- Current ADA from epoch_stake (latest epoch)
stake_amounts AS (
    SELECT es.addr_id, SUM(es.amount) AS lovelace
    FROM public.epoch_stake es
    CROSS JOIN latest_epoch le
    WHERE es.epoch_no = le.epoch_no
    GROUP BY es.addr_id
),

-- Join everything together
overlap_with_drep AS (
    SELECT
        os.stake_addr,
        os.entity_count,
        os.entities,
        sa.id AS addr_id,
        CASE
            WHEN cd.drep_view = 'drep_always_abstain'       THEN 'ABSTAIN'
            WHEN cd.drep_view = 'drep_always_no_confidence' THEN 'NO_CONFIDENCE'
            WHEN cd.drep_view IS NOT NULL                    THEN 'NAMED_DREP'
            ELSE                                                  'NO_DELEGATION'
        END AS drep_category,
        COALESCE(sam.lovelace, 0) AS lovelace
    FROM overlap_set os
    JOIN public.stake_address sa ON sa.view = os.stake_addr
    LEFT JOIN current_drep cd ON cd.addr_id = sa.id
    LEFT JOIN stake_amounts sam ON sam.addr_id = sa.id
)

-- === RESULT A: Summary across cross-entity overlap addresses only ===
-- Excludes EMURGO|EMURGO_2-only tier (same-entity overlap — see EXCLUSION NOTE above)
SELECT
    'A_summary'                                     AS result_set,
    'CROSS_ENTITY'                                  AS overlap_tier,
    'ALL_CROSS_ENTITY'                              AS entities,
    drep_category,
    COUNT(*)                                        AS stake_addr_count,
    ROUND(SUM(lovelace) / 1000000.0, 0)            AS ada_amount,
    ROUND(
        SUM(lovelace) * 100.0 /
        NULLIF(SUM(SUM(lovelace)) OVER (), 0)
    , 2)                                            AS pct
FROM overlap_with_drep
WHERE entities <> 'EMURGO|EMURGO_2'   -- exclude same-entity EMURGO internal overlap
GROUP BY drep_category

UNION ALL

-- === RESULT B: Detail by overlap tier ===
SELECT
    'B_detail'                                      AS result_set,
    entity_count::text                              AS overlap_tier,
    entities,
    drep_category,
    COUNT(*)                                        AS stake_addr_count,
    ROUND(SUM(lovelace) / 1000000.0, 0)            AS ada_amount,
    ROUND(
        SUM(lovelace) * 100.0 /
        NULLIF(SUM(SUM(lovelace)) OVER (PARTITION BY entity_count, entities), 0)
    , 2)                                            AS pct
FROM overlap_with_drep
GROUP BY entity_count, entities, drep_category

ORDER BY result_set, overlap_tier, ada_amount DESC NULLS LAST;

-- build_kes_corotation.sql — operator fingerprinting by KES-rotation timing.
--
-- Runs ON the abcde warehouse (local `poolsync` schema; public.* stays read-only).
--
-- Premise: every Cardano block header carries the minting pool's operational
-- certificate (block.op_cert / op_cert_counter). When an operator rotates the KES
-- hot key, the new cert appears in that pool's next minted block — so rotation
-- TIMING is a public, unfakeable operational fingerprint. Pools that rotate in
-- lockstep, cycle after cycle, are administered by the same hands/automation.
--
-- This file builds the SQL-derived inputs; the pair-scoring + connected-component
-- clustering is done in scripts/kes_corotation_cluster.py (empirical-null Poisson
-- test — see that file). Round trip:
--   psql -f build_kes_corotation.sql
--   \copy poolsync.tight/pool_info/shared_* to CSV   (see README)
--   python scripts/kes_corotation_cluster.py         (writes poolsync.cluster)
--   psql -f build_kes_corotation_summary.sql          (enrichment, run after cluster load)
--
-- EVIDENCE GRADE: synchronized rotation is FACT and indicates shared OPERATIONAL
-- control (one admin / automation / managed host). It is NOT proof of shared
-- ownership — white-label infra providers (Kiln, Figment) run pools for many
-- clients and appear here identically. Per the repo wording rule, on-chain
-- co-behaviour is on-chain linkage, never real-world identity or control.

\set ON_ERROR_STOP on
SET work_mem = '512MB';
CREATE SCHEMA IF NOT EXISTS poolsync;
-- cluster_alert (built in build_kes_corotation_summary.sql) depends on several
-- tables below; drop it first so a re-run can rebuild them.
DROP VIEW IF EXISTS poolsync.cluster_alert;

-- ---- 1. rotation events: op-cert changes in block headers, per pool ---------
-- gap = time between the last block on the OLD cert and the first on the NEW one;
-- it bounds the rotation moment's uncertainty (a rarely-minting pool has a wide
-- gap). The clustering keeps events with gap <= 48h.
DROP TABLE IF EXISTS poolsync.rotation;
CREATE TABLE poolsync.rotation AS
WITH pb AS (
  SELECT sl.pool_hash_id, b.slot_no, b.time, b.op_cert, b.op_cert_counter,
         lag(b.op_cert) OVER w AS prev_cert,
         lag(b.time)    OVER w AS prev_time
  FROM public.block b
  JOIN public.slot_leader sl ON sl.id = b.slot_leader_id
  WHERE b.op_cert IS NOT NULL AND sl.pool_hash_id IS NOT NULL
  WINDOW w AS (PARTITION BY sl.pool_hash_id ORDER BY b.slot_no)
)
SELECT pool_hash_id, time AS first_seen, prev_time AS last_old_seen,
       op_cert_counter, (time - prev_time) AS gap
FROM pb
WHERE prev_cert IS NOT NULL AND prev_cert <> op_cert;
CREATE INDEX ON poolsync.rotation (first_seen);

-- events tight enough to time (<=48h uncertainty) -> the clustering input
DROP TABLE IF EXISTS poolsync.tight;
CREATE TABLE poolsync.tight AS
SELECT pool_hash_id, first_seen, gap FROM poolsync.rotation
WHERE gap <= interval '48 hours';
CREATE INDEX ON poolsync.tight (first_seen);

-- ---- 2. pool identity: ticker/name + current-epoch stake --------------------
-- pool_stat is empty on this db-sync build; stake is summed from epoch_stake.
DROP TABLE IF EXISTS poolsync.pool_info;
CREATE TABLE poolsync.pool_info AS
WITH meta AS (
  SELECT DISTINCT ON (pool_id) pool_id, ticker_name, json->>'name' AS pool_name
  FROM public.off_chain_pool_data ORDER BY pool_id, id DESC),
st AS (
  SELECT pool_id, sum(amount)::numeric/1e6 AS stake_ada, count(*) AS delegators
  FROM public.epoch_stake WHERE epoch_no = (SELECT max(epoch_no) FROM public.epoch_stake)
  GROUP BY 1)
SELECT ph.id AS pool_hash_id, ph.view AS pool_bech32,
       m.ticker_name, m.pool_name, st.stake_ada, st.delegators
FROM public.pool_hash ph
LEFT JOIN meta m ON m.pool_id = ph.id
LEFT JOIN st ON st.pool_id = ph.id;

-- ---- 3. corroboration: on-chain links independent of timing -----------------
-- pools co-registered in one tx / sharing a reward addr, owner key, or relay.
DROP TABLE IF EXISTS poolsync.same_tx;
CREATE TABLE poolsync.same_tx AS
SELECT registered_tx_id AS tx_id, array_agg(DISTINCT hash_id) AS pools, count(DISTINCT hash_id) AS n
FROM public.pool_update GROUP BY 1 HAVING count(DISTINCT hash_id) > 1;

DROP TABLE IF EXISTS poolsync.shared_reward;
CREATE TABLE poolsync.shared_reward AS
SELECT reward_addr_id, array_agg(DISTINCT hash_id) AS pools, count(DISTINCT hash_id) AS n
FROM public.pool_update GROUP BY 1 HAVING count(DISTINCT hash_id) > 1;

DROP TABLE IF EXISTS poolsync.shared_owner;
CREATE TABLE poolsync.shared_owner AS
SELECT po.addr_id, array_agg(DISTINCT pu.hash_id) AS pools, count(DISTINCT pu.hash_id) AS n
FROM public.pool_owner po JOIN public.pool_update pu ON pu.id = po.pool_update_id
GROUP BY 1 HAVING count(DISTINCT pu.hash_id) > 1;

DROP TABLE IF EXISTS poolsync.shared_relay;
CREATE TABLE poolsync.shared_relay AS
WITH latest AS (SELECT DISTINCT ON (hash_id) hash_id, id FROM public.pool_update ORDER BY hash_id, id DESC)
SELECT coalesce(pr.dns_name, pr.ipv4) AS endpoint,
       array_agg(DISTINCT l.hash_id) AS pools, count(DISTINCT l.hash_id) AS n
FROM public.pool_relay pr JOIN latest l ON l.id = pr.update_id
WHERE coalesce(pr.dns_name, pr.ipv4) IS NOT NULL
GROUP BY 1 HAVING count(DISTINCT l.hash_id) > 1;

\echo === rotation events / tight events / pools ===
SELECT (SELECT count(*) FROM poolsync.rotation) rotations,
       (SELECT count(*) FROM poolsync.tight)    tight_events,
       (SELECT count(DISTINCT pool_hash_id) FROM poolsync.rotation) pools;

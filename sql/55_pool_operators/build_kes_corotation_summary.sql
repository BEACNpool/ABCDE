-- build_kes_corotation_summary.sql — enrichment + alert view for the KES clusters.
-- Run AFTER scripts/kes_corotation_cluster.py has loaded poolsync.cluster
-- (cluster_id, pool_hash_id). Builds per-cluster stake / block-share / DRep
-- overlay / active-window, and a cluster_alert view (stable member-set
-- fingerprint + on-chain-links flag) that BEACN Monitor's pool_cluster_watch
-- reads. Grades as in build_kes_corotation.sql: KES sync = FACT of shared
-- OPERATIONAL control, never ownership.
\set ON_ERROR_STOP on
SET work_mem = '512MB';
-- rebuilt at the end; drop first so the tables it reads can be replaced.
DROP VIEW IF EXISTS poolsync.cluster_alert;

-- entity = cluster if clustered else the pool itself (for Nakamoto math)
DROP TABLE IF EXISTS poolsync.entity;
CREATE TABLE poolsync.entity AS
SELECT ph.id AS pool_hash_id, coalesce('C'||c.cluster_id, 'P'||ph.id) AS entity_id
FROM public.pool_hash ph LEFT JOIN poolsync.cluster c ON c.pool_hash_id=ph.id;

-- per-cluster active window (from tight rotation events)
DROP TABLE IF EXISTS poolsync.cluster_time;
CREATE TABLE poolsync.cluster_time AS
SELECT c.cluster_id, min(r.first_seen)::date first_sync, max(r.first_seen)::date last_sync, count(*) events
FROM poolsync.rotation r JOIN poolsync.cluster c ON c.pool_hash_id=r.pool_hash_id
WHERE r.gap <= interval '48 hours' GROUP BY 1;

-- per-cluster summary: stake (epoch tip), 30-epoch block share, DRep overlay
DROP TABLE IF EXISTS poolsync.cluster_summary;
CREATE TABLE poolsync.cluster_summary AS
WITH stake AS (
  SELECT c.cluster_id, sum(es.amount) stake, count(DISTINCT es.addr_id) delegators
  FROM public.epoch_stake es JOIN poolsync.cluster c ON c.pool_hash_id=es.pool_id
  WHERE es.epoch_no=(SELECT max(epoch_no) FROM public.epoch_stake) GROUP BY 1),
blocks AS (
  SELECT c.cluster_id, count(*) blks FROM public.block b
  JOIN public.slot_leader sl ON sl.id=b.slot_leader_id
  JOIN poolsync.cluster c ON c.pool_hash_id=sl.pool_hash_id
  WHERE b.epoch_no>=(SELECT max(epoch_no)-30 FROM public.block) GROUP BY 1),
totblk AS (SELECT count(*) t FROM public.block WHERE epoch_no>=(SELECT max(epoch_no)-30 FROM public.block)),
npools AS (SELECT cluster_id, count(*) np FROM poolsync.cluster GROUP BY 1),
votes AS (
  SELECT cd.cluster_id, dh.view drep, sum(cd.amount) amt
  FROM (SELECT c.cluster_id, es.addr_id, es.amount FROM public.epoch_stake es
        JOIN poolsync.cluster c ON c.pool_hash_id=es.pool_id
        WHERE es.epoch_no=(SELECT max(epoch_no) FROM public.epoch_stake)) cd
  LEFT JOIN (SELECT DISTINCT ON (addr_id) addr_id, drep_hash_id FROM public.delegation_vote ORDER BY addr_id, tx_id DESC) lv ON lv.addr_id=cd.addr_id
  LEFT JOIN public.drep_hash dh ON dh.id=lv.drep_hash_id GROUP BY 1,2),
abstain AS (SELECT cluster_id, amt FROM votes WHERE drep='drep_always_abstain'),
topdrep AS (SELECT DISTINCT ON (cluster_id) cluster_id, drep, amt FROM votes
            WHERE drep IS NOT NULL AND drep NOT LIKE 'drep_always%' ORDER BY cluster_id, amt DESC)
SELECT n.cluster_id, n.np pools, round(s.stake/1e6) stake_ada, s.delegators,
       coalesce(b.blks,0) blocks_30ep, round(100.0*coalesce(b.blks,0)/(SELECT t FROM totblk),2) block_pct,
       ct.first_sync, ct.last_sync,
       round(coalesce(a.amt,0)/1e6) abstain_ada, td.drep top_drep, round(coalesce(td.amt,0)/1e6) top_drep_ada
FROM npools n JOIN stake s ON s.cluster_id=n.cluster_id
LEFT JOIN blocks b ON b.cluster_id=n.cluster_id
LEFT JOIN poolsync.cluster_time ct ON ct.cluster_id=n.cluster_id
LEFT JOIN abstain a ON a.cluster_id=n.cluster_id
LEFT JOIN topdrep td ON td.cluster_id=n.cluster_id
ORDER BY s.stake DESC;

-- alert view: stable fingerprint (md5 of sorted member bech32) + on-chain flag
CREATE OR REPLACE VIEW poolsync.cluster_alert AS
WITH mem AS (
  SELECT cl.cluster_id, array_agg(ph.view ORDER BY ph.view) pool_bech32s, count(*) pools
  FROM poolsync.cluster cl JOIN public.pool_hash ph ON ph.id=cl.pool_hash_id GROUP BY 1),
onchain AS (
  SELECT DISTINCT c.cluster_id FROM poolsync.cluster c
  JOIN (SELECT pools FROM poolsync.shared_reward UNION ALL SELECT pools FROM poolsync.shared_owner
        UNION ALL SELECT pools FROM poolsync.shared_relay UNION ALL SELECT pools FROM poolsync.same_tx) s
    ON c.pool_hash_id = ANY(s.pools)
  GROUP BY c.cluster_id, s.pools HAVING count(*) >= 2),
tick AS (
  SELECT cl.cluster_id, string_agg(DISTINCT pi.ticker_name, ' ') FILTER (WHERE pi.ticker_name IS NOT NULL) ticks
  FROM poolsync.cluster cl LEFT JOIN poolsync.pool_info pi ON pi.pool_hash_id=cl.pool_hash_id GROUP BY 1)
SELECT m.cluster_id, md5(array_to_string(m.pool_bech32s, ',')) fingerprint, m.pools,
       cs.stake_ada, cs.block_pct, cs.delegators, cs.abstain_ada, cs.top_drep_ada,
       (o.cluster_id IS NOT NULL) has_onchain_links,
       coalesce(t.ticks,'(anonymous)') sample_tickers, cs.last_sync
FROM mem m
LEFT JOIN poolsync.cluster_summary cs ON cs.cluster_id=m.cluster_id
LEFT JOIN onchain o ON o.cluster_id=m.cluster_id
LEFT JOIN tick t ON t.cluster_id=m.cluster_id;

\echo === Nakamoto: naive per-pool vs per-operator (stake, current epoch) ===
WITH s AS (SELECT pool_id, sum(amount) amt FROM public.epoch_stake
           WHERE epoch_no=(SELECT max(epoch_no) FROM public.epoch_stake) GROUP BY 1),
r AS (SELECT amt, sum(amt) OVER (ORDER BY amt DESC) c, (SELECT sum(amt) FROM s) t,
             row_number() OVER (ORDER BY amt DESC) rn FROM s),
es AS (SELECT e.entity_id, sum(x.amt) amt FROM s x JOIN poolsync.entity e ON e.pool_hash_id=x.pool_id GROUP BY 1),
er AS (SELECT amt, sum(amt) OVER (ORDER BY amt DESC) c, (SELECT sum(amt) FROM es) t,
              row_number() OVER (ORDER BY amt DESC) rn FROM es)
SELECT 'naive_pool' k, (SELECT min(rn) FROM r WHERE c>=0.33*t) nak33, (SELECT min(rn) FROM r WHERE c>=0.5*t) nak50
UNION ALL
SELECT 'clustered_operator', (SELECT min(rn) FROM er WHERE c>=0.33*t), (SELECT min(rn) FROM er WHERE c>=0.5*t);

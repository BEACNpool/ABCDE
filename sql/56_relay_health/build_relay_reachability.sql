-- build_relay_reachability.sql — roll one probe sweep up into per-endpoint and
-- per-pool reachability. Run AFTER loading a sweep into relay.observation
-- (see scripts/relay_probe.py and the module README).
--
-- READ THIS BEFORE REPEATING ANY NUMBER FROM HERE
-- -----------------------------------------------
-- Reachability is an OBSERVATION, not a property of a pool. Every row here means
-- "this endpoint did / did not complete a Cardano handshake with OUR prober, at
-- that moment". It does not mean the relay is down. A firewall that drops our
-- prefix, an inbound connection limit, a rate limiter, a restart, or a transient
-- route all render as `unreachable`. We have measured the same endpoint answering
-- from one host and timing out from another minutes later.
--
-- Consequently: never publish a pool as "offline". Publish what was observed,
-- from where, and when -- and require repeated sweeps before anyone reads a trend.
\set ON_ERROR_STOP on

CREATE SCHEMA IF NOT EXISTS relay;

-- Append-only observation log. One row per (endpoint, resolved target, sweep).
CREATE TABLE IF NOT EXISTS relay.observation (
  id               bigserial PRIMARY KEY,
  endpoint         text NOT NULL,
  endpoint_kind    text NOT NULL,
  endpoint_host    text,
  registered_port  int,
  target_host      text,
  target_port      int,
  resolved_ip      text,
  handshake_ok     boolean NOT NULL,
  block_no         bigint,
  slot_no          bigint,
  rtt_ms           numeric,
  failure          text,
  error_detail     text,
  attempts         int  NOT NULL DEFAULT 1,   -- 2 = went through the confirmation pass
  checked_at       timestamptz NOT NULL
);
-- Idempotent upgrade path for warehouses built before these columns existed.
ALTER TABLE relay.observation ADD COLUMN IF NOT EXISTS error_detail text;
ALTER TABLE relay.observation ADD COLUMN IF NOT EXISTS attempts int NOT NULL DEFAULT 1;

CREATE INDEX IF NOT EXISTS observation_endpoint_time_idx
  ON relay.observation (endpoint, checked_at DESC);
CREATE INDEX IF NOT EXISTS observation_time_idx
  ON relay.observation (checked_at DESC);

-- Staging table the sweep CSV is \copy'd into, then folded in.
CREATE TABLE IF NOT EXISTS relay.observation_stage (LIKE relay.observation
  INCLUDING DEFAULTS EXCLUDING INDEXES EXCLUDING CONSTRAINTS);
ALTER TABLE relay.observation_stage DROP COLUMN IF EXISTS id;

-- ---------------------------------------------------------------------------
-- Latest sweep, per endpoint.
--   The tip reference is the HIGHEST block any peer reported during the sweep,
--   not our own db-sync tip -- our warehouse lags the network by design, and
--   grading other people's nodes against a lagging local clock would mark
--   healthy relays as behind.
-- ---------------------------------------------------------------------------
DROP VIEW IF EXISTS relay.endpoint_status CASCADE;
CREATE VIEW relay.endpoint_status AS
WITH sweep AS (
  SELECT max(checked_at) AS latest FROM relay.observation
),
recent AS (
  SELECT o.* FROM relay.observation o, sweep s
  WHERE o.checked_at > s.latest - interval '6 hours'
),
ref AS (
  SELECT max(block_no) AS tip_block, max(slot_no) AS tip_slot FROM recent
),
latest AS (
  SELECT DISTINCT ON (endpoint, target_host, target_port, coalesce(resolved_ip, ''))
         * FROM recent
  ORDER BY endpoint, target_host, target_port, coalesce(resolved_ip, ''), checked_at DESC
)
SELECT
  l.endpoint, l.endpoint_kind, l.target_host, l.target_port, l.resolved_ip,
  l.handshake_ok, l.failure, l.error_detail, l.rtt_ms, l.block_no, l.slot_no, l.checked_at,
  r.tip_slot - l.slot_no AS slots_behind_best,
  -- 180 slots is ~3 minutes of chain; anything inside that is at the tip for
  -- practical purposes and absorbs propagation plus our own sweep duration.
  (l.handshake_ok AND r.tip_slot - l.slot_no <= 180) AS at_tip
FROM latest l CROSS JOIN ref r;

-- ---------------------------------------------------------------------------
-- Per-pool reachability.
--   Counted over DISTINCT REACHABLE HOSTS (resolved IP where we have one),
--   never over registration entries. Two DNS names pointing at one box is one
--   relay, and registering the same machine twice is exactly the pattern this
--   dataset exists to make visible.
-- ---------------------------------------------------------------------------
DROP TABLE IF EXISTS relay.pool_health CASCADE;
CREATE TABLE relay.pool_health AS
WITH ep AS (
  SELECT DISTINCT e.pool_hash_id, e.endpoint FROM relay.endpoint e WHERE e.endpoint IS NOT NULL
),
per_pool AS (
  SELECT
    ep.pool_hash_id,
    count(DISTINCT es.endpoint)                                            AS endpoints_probed,
    count(DISTINCT coalesce(es.resolved_ip, es.target_host))
      FILTER (WHERE es.handshake_ok)                                       AS reachable_hosts,
    count(DISTINCT coalesce(es.resolved_ip, es.target_host))
      FILTER (WHERE es.at_tip)                                             AS at_tip_hosts,
    count(DISTINCT es.endpoint)
      FILTER (WHERE es.failure = 'no_ipv6_at_probe')                       AS endpoints_untested,
    min(es.rtt_ms) FILTER (WHERE es.handshake_ok)                          AS best_rtt_ms,
    max(es.slots_behind_best) FILTER (WHERE es.handshake_ok)               AS worst_slots_behind,
    max(es.checked_at)                                                     AS last_checked
  FROM ep JOIN relay.endpoint_status es ON es.endpoint = ep.endpoint
  GROUP BY ep.pool_hash_id
),
shared AS (
  SELECT DISTINCT e.pool_hash_id FROM relay.endpoint e
  JOIN relay.endpoint_shared s ON s.endpoint = e.endpoint
),
-- Whether a pool actually MINTS is the difference between a live operator and a
-- registration nobody ever retired. Without it the headline reachability numbers
-- are dominated by long-dead pools that hold no stake and produce no blocks, and
-- read as though the network is far sicker than it is.
minted AS (
  SELECT sl.pool_hash_id, count(*) AS blocks_30ep
  FROM public.block b
  JOIN public.slot_leader sl ON sl.id = b.slot_leader_id
  WHERE b.epoch_no >= (SELECT max(epoch_no) - 30 FROM public.block)
    AND sl.pool_hash_id IS NOT NULL
  GROUP BY sl.pool_hash_id
)
SELECT
  pr.pool_hash_id, pr.pool_bech32, pr.ticker, pr.stake_ada, pr.delegators,
  pr.relay_entries, pr.distinct_endpoints, pr.registration_class,
  coalesce(pp.endpoints_probed, 0)  AS endpoints_probed,
  coalesce(pp.reachable_hosts, 0)   AS reachable_hosts,
  coalesce(pp.at_tip_hosts, 0)      AS at_tip_hosts,
  coalesce(pp.endpoints_untested, 0) AS endpoints_untested,
  pp.best_rtt_ms, pp.worst_slots_behind, pp.last_checked,
  (sh.pool_hash_id IS NOT NULL)     AS shares_endpoint_with_other_pool,
  coalesce(mb.blocks_30ep, 0)       AS blocks_last_30_epochs,
  (mb.pool_hash_id IS NOT NULL)     AS minted_last_30_epochs,
  coalesce(fi.foreign_eps, 0)       AS endpoints_foreign_infra,
  (fi.pool_hash_id IS NOT NULL)     AS registers_foreign_infrastructure,
  coalesce(hi.relay_additions, 0)   AS relay_additions,
  coalesce(hi.relay_reductions, 0)  AS relay_reductions,
  coalesce(hi.ever_removed_all_relays, false) AS ever_removed_all_relays,
  hi.removed_all_on::date           AS removed_all_relays_on,
  CASE
    WHEN pr.relay_entries = 0             THEN 'NO_REGISTERED_RELAY'
    -- Every endpoint this pool registered is one we could not test at all
    -- (IPv6-only, and the prober has no IPv6 route). Reporting that as
    -- "nothing answered" would blame the pool for our own blind spot.
    WHEN coalesce(pp.reachable_hosts,0)=0
     AND coalesce(pp.endpoints_untested,0) >= pr.distinct_endpoints
                                          THEN 'NOT_TESTED_FROM_THIS_PROBE'
    WHEN coalesce(pp.reachable_hosts,0)=0 THEN 'NONE_REACHABLE'
    WHEN pp.reachable_hosts = 1           THEN 'ONE_REACHABLE_HOST'
    ELSE 'MULTI_REACHABLE_HOSTS'
  END AS reachability_class
FROM relay.pool_registration pr
LEFT JOIN per_pool pp ON pp.pool_hash_id = pr.pool_hash_id
LEFT JOIN shared sh   ON sh.pool_hash_id = pr.pool_hash_id
LEFT JOIN minted mb   ON mb.pool_hash_id = pr.pool_hash_id
LEFT JOIN relay.pool_relay_history hi ON hi.pool_hash_id = pr.pool_hash_id
-- Built by build_relay_foreign_infra.sql, which depends only on registration.
LEFT JOIN (
  SELECT pc2.pool_hash_id, max(f.endpoints_foreign) AS foreign_eps
  FROM relay.foreign_infrastructure f
  JOIN relay.pool_current pc2 ON pc2.pool_bech32 = f.pool_bech32
  GROUP BY pc2.pool_hash_id
) fi ON fi.pool_hash_id = pr.pool_hash_id;

ALTER TABLE relay.pool_health ADD PRIMARY KEY (pool_hash_id);
CREATE INDEX ON relay.pool_health (stake_ada DESC);

-- ---------------------------------------------------------------------------
-- Pools sharing a RESOLVED HOST, not a registered string.
--   Registering one hostname per pool defeats string matching completely --
--   this dataset contains a fleet whose pools each get their own numbered name
--   under one domain, so `endpoint_shared` sees them as unrelated. Resolution
--   collapses that: if two pools' relay names answer at the same IP, they are
--   on the same machine, whatever they registered.
--   Depends on a sweep having run; endpoints we could not resolve are absent,
--   so this is a FLOOR on sharing, never a ceiling.
-- ---------------------------------------------------------------------------
DROP TABLE IF EXISTS relay.shared_resolved_host CASCADE;
CREATE TABLE relay.shared_resolved_host AS
WITH per AS (
  SELECT es.resolved_ip, es.target_port, e.pool_hash_id, es.endpoint
  FROM relay.endpoint_status es
  JOIN relay.endpoint e ON e.endpoint = es.endpoint
  WHERE es.resolved_ip IS NOT NULL
),
-- Aggregate the pool set FIRST. A pool advertising five endpoints joins five
-- times, so counting rows here (rather than DISTINCT pools) multiplies both the
-- pool count and the stake by the number of endpoints -- it reported Everstake
-- as 75 pools / 3.16B ADA instead of 15 / 631M.
agg AS (
  SELECT resolved_ip, target_port,
         count(DISTINCT pool_hash_id) AS pools,
         count(DISTINCT endpoint)     AS distinct_registered_names
  FROM per GROUP BY 1, 2
  HAVING count(DISTINCT pool_hash_id) > 1
)
SELECT a.resolved_ip, a.target_port, a.pools, a.distinct_registered_names,
       s.stake_ada, s.delegators, s.tickers, s.pool_bech32s
FROM agg a
JOIN LATERAL (
  SELECT sum(pc.stake_ada)::bigint                       AS stake_ada,
         sum(pc.delegators)::bigint                      AS delegators,
         array_remove(array_agg(DISTINCT pc.ticker), NULL) AS tickers,
         array_agg(DISTINCT pc.pool_bech32)              AS pool_bech32s
  FROM (SELECT DISTINCT p.pool_hash_id FROM per p
        WHERE p.resolved_ip = a.resolved_ip AND p.target_port = a.target_port) d
  JOIN relay.pool_current pc ON pc.pool_hash_id = d.pool_hash_id
) s ON TRUE;

CREATE INDEX ON relay.shared_resolved_host (pools DESC);

-- ---------------------------------------------------------------------------
-- Pools sharing a registrable parent DOMAIN.
--   HEURISTIC: the last two labels of the registered name. It is wrong for
--   multi-part public suffixes (.co.uk, .com.br) and it deliberately groups
--   unrelated customers of one hosting domain. Use it to find fleets to look
--   at, never as a claim that the pools are related.
-- ---------------------------------------------------------------------------
DROP TABLE IF EXISTS relay.shared_domain CASCADE;
CREATE TABLE relay.shared_domain AS
WITH d AS (
  SELECT DISTINCT
         regexp_replace(e.endpoint_host, '^.*?([^.]+\.[^.]+)$', '\1') AS domain,
         e.pool_hash_id
  FROM relay.endpoint e
  WHERE e.endpoint_kind IN ('dns', 'srv') AND e.endpoint_host ~ '\.'
)
SELECT d.domain,
       count(*)                                          AS pools,
       sum(pc.stake_ada)::bigint                         AS stake_ada,
       sum(pc.delegators)::bigint                        AS delegators,
       array_remove(array_agg(DISTINCT pc.ticker), NULL) AS tickers
FROM d JOIN relay.pool_current pc ON pc.pool_hash_id = d.pool_hash_id
GROUP BY d.domain
HAVING count(*) > 1;

CREATE INDEX ON relay.shared_domain (pools DESC);

INSERT INTO relay.build_receipt (stage, tip_block_no, tip_epoch_no, tip_time, stake_epoch, rows_out, notes)
SELECT 'reachability',
       (SELECT max(block_no) FROM public.block),
       (SELECT max(epoch_no) FROM public.block),
       (SELECT max(time)     FROM public.block),
       (SELECT max(epoch_no) FROM public.epoch_stake),
       (SELECT count(*) FROM relay.pool_health),
       'single-vantage-point sweep; unreachable != offline';

-- schema.sql — peers: BEACN relay's peer-connection history + public
-- "who's connected" pool-map feed.
--
-- Runs ON abcde (isolated `peers` schema; public.* stays read-only). Fed by
-- the hourly ops/peer_map_collect.py cron on midnight, which SSHes relay for
-- a live `ss` snapshot and queries Security Onion's Zeek conn.log for
-- the relay's node port, inserts rows here, then builds the public
-- gh-pages/peers/peers.json feed from peers.recent_summary.
--
-- Identity join follows the same "latest pool_update per pool" + relay-IP
-- pattern already proven in sql/55_pool_operators/build_kes_corotation.sql
-- (poolsync.shared_relay) — deliberately not re-deriving that logic, just
-- the same shape, kept in its own schema since this feature is unrelated to
-- KES co-rotation and shouldn't couple to that table's build lifecycle.
--
-- Idempotent: safe to re-run. psql -d cexplorer_replica -f schema.sql

\set ON_ERROR_STOP on

CREATE SCHEMA IF NOT EXISTS peers;

CREATE TABLE IF NOT EXISTS peers.raw_observation (
  id            bigserial   PRIMARY KEY,
  observed_at   timestamptz NOT NULL DEFAULT now(),
  source        text        NOT NULL CHECK (source IN ('ss', 'zeek')),
  peer_ip       inet        NOT NULL,
  peer_port     integer     NOT NULL,
  direction     text,                     -- 'inbound' | 'outbound' | null (zeek: not always known)
  state         text,                     -- e.g. ESTAB (ss) / SF, S0... (zeek connection.state)
  bytes_client  bigint,
  bytes_server  bigint
);
CREATE INDEX IF NOT EXISTS raw_observation_observed_at_idx ON peers.raw_observation (observed_at);
CREATE INDEX IF NOT EXISTS raw_observation_peer_ip_idx     ON peers.raw_observation (peer_ip);

-- Which registered pool (if any) currently advertises a given relay IP.
-- No pool_retire filter, matching poolsync.shared_relay's existing convention —
-- a retired pool's relay simply stops appearing as a live peer on its own.
CREATE OR REPLACE VIEW peers.pool_by_ip AS
WITH latest AS (
  SELECT DISTINCT ON (hash_id) hash_id, id
  FROM public.pool_update
  ORDER BY hash_id, id DESC
),
meta AS (
  SELECT DISTINCT ON (pool_id) pool_id, ticker_name, json->>'name' AS pool_name
  FROM public.off_chain_pool_data
  ORDER BY pool_id, id DESC
)
SELECT
  coalesce(pr.ipv4, pr.ipv6) AS peer_ip,
  ph.id                      AS pool_hash_id,
  ph.view                    AS pool_bech32,
  m.ticker_name,
  m.pool_name
FROM public.pool_relay pr
JOIN latest l ON l.id = pr.update_id
JOIN public.pool_hash ph ON ph.id = l.hash_id
LEFT JOIN meta m ON m.pool_id = ph.id
WHERE coalesce(pr.ipv4, pr.ipv6) IS NOT NULL;

-- One row per peer IP seen in the last 48h, resolved against pool identity.
-- Queried directly by peer_map_collect.py's JSON-builder step — not
-- materialized, cheap at this row count (dozens to low hundreds of peers).
CREATE OR REPLACE VIEW peers.recent_summary AS
SELECT
  host(ro.peer_ip)              AS ip,
  min(ro.peer_port)              AS port,
  min(ro.observed_at)            AS first_seen,
  max(ro.observed_at)            AS last_seen,
  array_agg(DISTINCT ro.source)  AS sources,
  p.ticker_name,
  p.pool_name,
  p.pool_bech32
FROM peers.raw_observation ro
LEFT JOIN peers.pool_by_ip p ON p.peer_ip = host(ro.peer_ip)
WHERE ro.observed_at > now() - interval '48 hours'
GROUP BY host(ro.peer_ip), p.ticker_name, p.pool_name, p.pool_bech32;

\echo === peers schema ready ===
SELECT (SELECT count(*) FROM peers.raw_observation) AS raw_rows,
       (SELECT count(*) FROM peers.pool_by_ip)       AS pool_relay_ips;

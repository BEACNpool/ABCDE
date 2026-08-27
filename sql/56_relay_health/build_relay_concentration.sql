-- build_relay_concentration.sql — where the network's relays actually live, and
-- how much stake shares a single failure domain.
--
-- A pool with three relays is not redundant if all three sit in one datacenter.
-- Pool counts cannot see that; the announcing ASN can. Run AFTER a sweep, with
-- relay.ip_asn loaded from scripts/relay_asn_lookup.py.
--
-- GRADE. Which ASN announces an IP is FACT (BGP origin, via Team Cymru).
-- "These pools share a failure domain" is a STRONG_INFERENCE from it. An ASN is
-- NOT an operator and NOT ownership: Hetzner and DigitalOcean host a large share
-- of the hobbyist internet, and two pools in one datacenter are usually two
-- unrelated people who both picked the cheap option. That is precisely why it
-- matters -- uncoordinated concentration is still concentration.
\set ON_ERROR_STOP on

CREATE SCHEMA IF NOT EXISTS relay;

CREATE TABLE IF NOT EXISTS relay.ip_asn (
  resolved_ip text PRIMARY KEY,
  asn         text,
  as_name     text,
  prefix      text,
  country     text
);

-- ---------------------------------------------------------------------------
-- Per pool: the distinct ASNs its REACHABLE hosts sit in.
-- Unreachable endpoints contribute nothing -- we never resolved them, so we
-- cannot say where they are. Every count here is therefore a floor.
-- ---------------------------------------------------------------------------
DROP TABLE IF EXISTS relay.pool_asn CASCADE;
CREATE TABLE relay.pool_asn AS
SELECT DISTINCT e.pool_hash_id, ia.asn, ia.as_name, ia.country
FROM relay.endpoint e
JOIN relay.endpoint_status es ON es.endpoint = e.endpoint
JOIN relay.ip_asn ia          ON ia.resolved_ip = es.resolved_ip
WHERE es.handshake_ok AND ia.asn IS NOT NULL AND ia.asn <> '';

CREATE INDEX ON relay.pool_asn (pool_hash_id);
CREATE INDEX ON relay.pool_asn (asn);

-- ---------------------------------------------------------------------------
-- Per ASN: how much of the network it carries, and -- the number that matters --
-- how much of it would lose EVERY relay it has if that one ASN went dark.
-- ---------------------------------------------------------------------------
DROP TABLE IF EXISTS relay.asn_concentration CASCADE;
CREATE TABLE relay.asn_concentration AS
WITH spread AS (   -- how many distinct ASNs each pool is spread across
  SELECT pool_hash_id, count(DISTINCT asn) AS asn_count
  FROM relay.pool_asn GROUP BY pool_hash_id
)
SELECT
  pa.asn,
  min(pa.as_name)                                        AS as_name,
  min(pa.country)                                        AS country,
  count(DISTINCT pa.pool_hash_id)                        AS pools,
  sum(pc.stake_ada)::bigint                              AS stake_ada,
  sum(pc.delegators)::bigint                             AS delegators,
  count(DISTINCT pa.pool_hash_id) FILTER (WHERE s.asn_count = 1) AS pools_single_asn,
  coalesce(sum(pc.stake_ada) FILTER (WHERE s.asn_count = 1), 0)::bigint
                                                         AS stake_single_asn,
  coalesce(sum(pc.delegators) FILTER (WHERE s.asn_count = 1), 0)::bigint
                                                         AS delegators_single_asn
FROM relay.pool_asn pa
JOIN relay.pool_current pc ON pc.pool_hash_id = pa.pool_hash_id
JOIN spread s              ON s.pool_hash_id = pa.pool_hash_id
GROUP BY pa.asn;

CREATE INDEX ON relay.asn_concentration (stake_ada DESC);

INSERT INTO relay.build_receipt (stage, tip_block_no, tip_epoch_no, tip_time, stake_epoch, rows_out, notes)
SELECT 'concentration',
       (SELECT max(block_no) FROM public.block),
       (SELECT max(epoch_no) FROM public.block),
       (SELECT max(time)     FROM public.block),
       (SELECT max(epoch_no) FROM public.epoch_stake),
       (SELECT count(*) FROM relay.asn_concentration),
       'BGP origin per reachable relay IP; ASN is a failure domain, not an operator';

-- build_relay_defects.sql — relay registrations that cannot work, from the
-- string alone.
--
-- WHY THIS IS SAFE TO PUBLISH AND A GENERAL "ISSUE SCANNER" IS NOT.
-- Everything here is wrong by construction, not by opinion: no node on the
-- internet can reach 127.0.0.1 or an RFC1918 address, and the relay field takes
-- a bare hostname, so a value with a scheme and a slash is not a hostname. No
-- probe, no vantage point and no judgement call is involved -- run this against
-- any db-sync and you get the same rows.
--
-- These are almost certainly honest misconfigurations. That is exactly why they
-- are worth surfacing: this is the one category on the whole page that an
-- operator can read and simply fix. It is a service, not an accusation, and the
-- wording here should stay that way.
\set ON_ERROR_STOP on

CREATE SCHEMA IF NOT EXISTS relay;

DROP TABLE IF EXISTS relay.registration_defect CASCADE;
CREATE TABLE relay.registration_defect AS
WITH classified AS (
  SELECT
    e.pool_hash_id, e.pool_bech32, e.ticker, e.endpoint_kind, e.endpoint_host, e.port,
    CASE
      -- Reachable from nowhere but the operator's own network.
      WHEN e.endpoint_kind IN ('ipv4','ipv6') AND e.endpoint_host ~ '^127\.'        THEN 'loopback_address'
      WHEN e.endpoint_kind IN ('ipv4','ipv6') AND e.endpoint_host ~ '^(::1|0:0:0:0:0:0:0:1)$' THEN 'loopback_address'
      WHEN e.endpoint_kind IN ('ipv4','ipv6')
           AND e.endpoint_host ~ '^(10\.|192\.168\.|169\.254\.|172\.(1[6-9]|2[0-9]|3[01])\.)' THEN 'private_address'
      WHEN e.endpoint_kind IN ('ipv4','ipv6') AND e.endpoint_host ~ '^0\.'          THEN 'unroutable_address'
      -- The field takes a bare hostname. A scheme or a path is a config mistake.
      WHEN e.endpoint_host ~ '^[a-z]+://' OR e.endpoint_host ~ '/'                  THEN 'url_not_hostname'
      -- A DNS name with no dot cannot resolve publicly.
      WHEN e.endpoint_kind IN ('dns','srv') AND e.endpoint_host !~ '\.'             THEN 'hostname_not_qualified'
      WHEN e.endpoint_host ~ '(^localhost$|example\.(com|org|net)|changeme|your-|placeholder)' THEN 'placeholder_value'
      WHEN e.endpoint_host IS NULL OR btrim(e.endpoint_host) = ''                   THEN 'empty_host'
      WHEN e.port IS NOT NULL AND (e.port <= 0 OR e.port > 65535)                   THEN 'port_out_of_range'
    END AS defect
  FROM relay.endpoint e
)
SELECT
  c.pool_bech32, c.ticker, pc.stake_ada, pc.delegators,
  c.endpoint_kind, c.endpoint_host, c.port, c.defect,
  CASE c.defect
    WHEN 'loopback_address'       THEN 'a loopback address resolves to the machine doing the asking, so no other node can ever reach it'
    WHEN 'private_address'        THEN 'a private (RFC1918) address is only reachable inside the operator''s own network'
    WHEN 'unroutable_address'     THEN 'not a routable destination address'
    WHEN 'url_not_hostname'       THEN 'the relay field takes a bare hostname; a scheme or path will not resolve'
    WHEN 'hostname_not_qualified' THEN 'a name with no dot cannot resolve in public DNS'
    WHEN 'placeholder_value'      THEN 'looks like an unedited template or example value'
    WHEN 'empty_host'             THEN 'no host recorded on the relay entry'
    WHEN 'port_out_of_range'      THEN 'port is outside 1-65535'
  END AS why,
  (SELECT count(*) FROM public.block b JOIN public.slot_leader sl ON sl.id = b.slot_leader_id
   WHERE sl.pool_hash_id = c.pool_hash_id) AS blocks_all_time,
  (SELECT count(DISTINCT e2.endpoint) FROM relay.endpoint e2
   WHERE e2.pool_hash_id = c.pool_hash_id) AS endpoints_registered
FROM classified c
JOIN relay.pool_current pc ON pc.pool_hash_id = c.pool_hash_id
WHERE c.defect IS NOT NULL;

CREATE INDEX ON relay.registration_defect (defect);
CREATE INDEX ON relay.registration_defect (stake_ada DESC);

INSERT INTO relay.build_receipt (stage, tip_block_no, tip_epoch_no, tip_time, stake_epoch, rows_out, notes)
SELECT 'defects', (SELECT max(block_no) FROM public.block), (SELECT max(epoch_no) FROM public.block),
       (SELECT max(time) FROM public.block), (SELECT max(epoch_no) FROM public.epoch_stake),
       (SELECT count(*) FROM relay.registration_defect),
       'registrations that cannot work, detectable from the string alone';

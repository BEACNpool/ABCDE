-- build_relay_registration.sql — what every active pool has REGISTERED on-chain
-- as its relay set, plus which registered endpoints are shared between pools.
--
-- Grades (see findings/F21_relay_registration_and_reachability.md):
--   FACT        — the registration rows themselves. Anyone with db-sync gets these.
--   INFERENCE   — "these pools share infrastructure" from a shared endpoint string.
--                 A hosting provider or a white-label operator produces the same
--                 pattern as one operator running many pools.
--   NOT CLAIMED — ownership, identity, intent, or whether a relay is "down".
--                 Reachability lives in build_relay_reachability.sql and is an
--                 OBSERVATION from one vantage point, never a property of the pool.
--
-- Reads public.* read-only; writes only the `relay` schema.
\set ON_ERROR_STOP on
SET work_mem = '256MB';

CREATE SCHEMA IF NOT EXISTS relay;

-- ---------------------------------------------------------------------------
-- 1. Current pools.
--    A pool's live registration is its LATEST pool_update. A pool_retire cert
--    only counts if it was announced AFTER that update (a later re-registration
--    cancels a pending retirement) and its retiring_epoch has already arrived.
--    Getting this wrong is the classic db-sync pool-list bug: it either drops
--    pools that cancelled a retirement, or keeps pools that are long gone.
-- ---------------------------------------------------------------------------
DROP TABLE IF EXISTS relay.pool_current CASCADE;
CREATE TABLE relay.pool_current AS
WITH tip AS (
  SELECT max(epoch_no) AS epoch_no, max(block_no) AS block_no, max(time) AS block_time
  FROM public.block
),
latest_update AS (
  SELECT DISTINCT ON (pu.hash_id)
         pu.hash_id, pu.id AS update_id, pu.registered_tx_id,
         pu.active_epoch_no, pu.pledge, pu.margin, pu.fixed_cost
  FROM public.pool_update pu
  ORDER BY pu.hash_id, pu.registered_tx_id DESC, pu.cert_index DESC, pu.id DESC
),
retire AS (
  SELECT DISTINCT ON (pr.hash_id) pr.hash_id, pr.retiring_epoch, pr.announced_tx_id
  FROM public.pool_retire pr
  ORDER BY pr.hash_id, pr.announced_tx_id DESC, pr.cert_index DESC, pr.id DESC
),
live AS (
  SELECT lu.*,
         r.retiring_epoch,
         (r.hash_id IS NOT NULL AND r.announced_tx_id > lu.registered_tx_id) AS retire_pending
  FROM latest_update lu
  LEFT JOIN retire r ON r.hash_id = lu.hash_id
  CROSS JOIN tip t
  WHERE NOT (r.hash_id IS NOT NULL
             AND r.announced_tx_id > lu.registered_tx_id
             AND r.retiring_epoch <= t.epoch_no)
),
-- Active stake for the newest epoch present in epoch_stake. NOTE: epoch_stake is
-- keyed by the epoch the stake is ACTIVE FOR, so its max epoch is normally one
-- ahead of the tip block's epoch. pool_stat is EMPTY on db-sync 13.6.0.4 — do
-- not use it for stake or delegator counts.
stake AS (
  SELECT es.pool_id AS hash_id, sum(es.amount) AS stake_lovelace,
         count(DISTINCT es.addr_id) AS delegators
  FROM public.epoch_stake es
  WHERE es.epoch_no = (SELECT max(epoch_no) FROM public.epoch_stake)
  GROUP BY es.pool_id
),
ticker AS (
  SELECT DISTINCT ON (o.pool_id) o.pool_id AS hash_id, o.ticker_name
  FROM public.off_chain_pool_data o
  ORDER BY o.pool_id, o.pmr_id DESC, o.id DESC
)
SELECT
  l.hash_id                                   AS pool_hash_id,
  ph.view                                     AS pool_bech32,
  encode(ph.hash_raw, 'hex')                  AS pool_hash_hex,
  t.ticker_name                               AS ticker,
  round(coalesce(s.stake_lovelace, 0) / 1e6)::bigint AS stake_ada,
  coalesce(s.delegators, 0)                   AS delegators,
  l.update_id,
  l.active_epoch_no,
  round(l.pledge / 1e6)::bigint               AS pledge_ada,
  l.margin,
  round(l.fixed_cost / 1e6)::bigint           AS fixed_cost_ada,
  l.retire_pending,
  l.retiring_epoch,
  b.time                                      AS registered_at,
  encode(tx.hash, 'hex')                      AS registered_tx
FROM live l
JOIN public.pool_hash ph ON ph.id = l.hash_id
JOIN public.tx tx        ON tx.id = l.registered_tx_id
JOIN public.block b      ON b.id  = tx.block_id
LEFT JOIN stake s        ON s.hash_id = l.hash_id
LEFT JOIN ticker t       ON t.hash_id = l.hash_id;

ALTER TABLE relay.pool_current ADD PRIMARY KEY (pool_hash_id);
CREATE INDEX ON relay.pool_current (stake_ada DESC);

-- ---------------------------------------------------------------------------
-- 2. One row per registered relay entry, normalised to a probe target.
--    endpoint_kind is what the operator actually registered. Cardano supports
--    a multi-host DNS SRV record: ONE srv entry can stand for many real hosts
--    and carries its port in DNS, not in pool_relay.port. Counting entries and
--    calling an SRV pool "single relay" is wrong.
--    pool_relay.ipv4 is varchar, not inet — no host()/inet operators.
-- ---------------------------------------------------------------------------
DROP TABLE IF EXISTS relay.endpoint CASCADE;
CREATE TABLE relay.endpoint AS
SELECT
  pc.pool_hash_id,
  pc.pool_bech32,
  pc.ticker,
  pr.id AS pool_relay_id,
  CASE WHEN pr.dns_srv_name IS NOT NULL THEN 'srv'
       WHEN pr.dns_name     IS NOT NULL THEN 'dns'
       WHEN pr.ipv4         IS NOT NULL THEN 'ipv4'
       WHEN pr.ipv6         IS NOT NULL THEN 'ipv6'
       ELSE 'empty' END AS endpoint_kind,
  lower(trim(coalesce(pr.dns_srv_name, pr.dns_name, pr.ipv4, pr.ipv6))) AS endpoint_host,
  pr.port,
  CASE WHEN pr.dns_srv_name IS NOT NULL THEN 'srv:'  || lower(trim(pr.dns_srv_name))
       WHEN pr.dns_name     IS NOT NULL THEN 'dns:'  || lower(trim(pr.dns_name))
       WHEN pr.ipv4         IS NOT NULL THEN 'ipv4:' || trim(pr.ipv4)
       WHEN pr.ipv6         IS NOT NULL THEN 'ipv6:' || lower(trim(pr.ipv6))
       END AS endpoint
FROM relay.pool_current pc
JOIN public.pool_relay pr ON pr.update_id = pc.update_id;

CREATE INDEX ON relay.endpoint (pool_hash_id);
CREATE INDEX ON relay.endpoint (endpoint);

-- ---------------------------------------------------------------------------
-- 3. Per-pool registration shape + the community rubric applied to REGISTRATION
--    only. registration_class answers "what did they publish", never "is it up".
-- ---------------------------------------------------------------------------
DROP TABLE IF EXISTS relay.pool_registration CASCADE;
CREATE TABLE relay.pool_registration AS
SELECT
  pc.pool_hash_id, pc.pool_bech32, pc.ticker, pc.stake_ada, pc.delegators,
  pc.pledge_ada, pc.retire_pending, pc.registered_at,
  count(e.pool_relay_id)                                             AS relay_entries,
  count(e.pool_relay_id) FILTER (WHERE e.endpoint_kind = 'srv')      AS srv_entries,
  count(e.pool_relay_id) FILTER (WHERE e.endpoint_kind = 'dns')      AS dns_entries,
  count(e.pool_relay_id) FILTER (WHERE e.endpoint_kind = 'ipv4')     AS ipv4_entries,
  count(e.pool_relay_id) FILTER (WHERE e.endpoint_kind = 'ipv6')     AS ipv6_entries,
  count(DISTINCT e.endpoint)                                         AS distinct_endpoints,
  CASE
    WHEN count(e.pool_relay_id) = 0                             THEN 'NO_REGISTERED_RELAY'
    WHEN count(e.pool_relay_id) FILTER (WHERE e.endpoint_kind='srv') > 0
                                                                THEN 'SRV_MULTIHOST_POSSIBLE'
    WHEN count(DISTINCT e.endpoint) = 1                         THEN 'SINGLE_ENDPOINT'
    ELSE 'MULTIPLE_ENDPOINTS'
  END AS registration_class
FROM relay.pool_current pc
LEFT JOIN relay.endpoint e ON e.pool_hash_id = pc.pool_hash_id
GROUP BY pc.pool_hash_id, pc.pool_bech32, pc.ticker, pc.stake_ada, pc.delegators,
         pc.pledge_ada, pc.retire_pending, pc.registered_at;

ALTER TABLE relay.pool_registration ADD PRIMARY KEY (pool_hash_id);

-- ---------------------------------------------------------------------------
-- 4. Endpoints advertised by more than one CURRENT pool.
--    FACT: the same string appears in N pools' live registrations.
--    NOT a claim of shared ownership — read the finding before repeating this.
-- ---------------------------------------------------------------------------
DROP TABLE IF EXISTS relay.endpoint_shared CASCADE;
CREATE TABLE relay.endpoint_shared AS
WITH per_pool AS (
  SELECT DISTINCT e.endpoint, e.endpoint_kind, e.pool_hash_id
  FROM relay.endpoint e
  WHERE e.endpoint IS NOT NULL
)
SELECT
  p.endpoint,
  p.endpoint_kind,
  count(*)                                        AS pools,
  sum(pc.stake_ada)::bigint                       AS stake_ada,
  sum(pc.delegators)::bigint                      AS delegators,
  array_agg(pc.pool_bech32 ORDER BY pc.stake_ada DESC) AS pool_bech32s,
  array_remove(array_agg(pc.ticker ORDER BY pc.stake_ada DESC), NULL) AS tickers
FROM per_pool p
JOIN relay.pool_current pc ON pc.pool_hash_id = p.pool_hash_id
GROUP BY p.endpoint, p.endpoint_kind
HAVING count(*) > 1;

CREATE INDEX ON relay.endpoint_shared (pools DESC);

-- ---------------------------------------------------------------------------
-- 4b. Relay registration HISTORY.
--
--   `pool_update` is append-only: a pool can change what it advertises, but it
--   can never un-publish what it advertised before. So the one question a pool
--   cannot answer by editing its certificate is "what did you used to run?"
--
--   This matters because removing a relay from the certificate is a normal
--   transaction -- no new deposit, just the fee -- and it makes an unreachable
--   relay stop being unreachable by making it stop existing. That is the only
--   move in this dataset that *improves* a pool's standing by publishing less.
--   Here it does the opposite: removals are the thing being counted.
--
--   Read the direction honestly. Most relay-count changes are pools ADDING
--   capacity, and reducing a count is ordinary maintenance -- consolidating
--   hosts, retiring a box, moving provider. Dropping to ZERO is the case worth
--   looking at, and even that is permitted; operators who do it usually cite
--   DDoS surface. What it means factually is that the network can no longer
--   discover them from the chain.
-- ---------------------------------------------------------------------------
DROP TABLE IF EXISTS relay.registration_change CASCADE;
CREATE TABLE relay.registration_change AS
WITH upd AS (
  SELECT pu.hash_id, pu.id AS update_id, pu.registered_tx_id, pu.cert_index,
         row_number() OVER (PARTITION BY pu.hash_id
                            ORDER BY pu.registered_tx_id, pu.cert_index, pu.id) AS seq,
         (SELECT count(*) FROM public.pool_relay pr WHERE pr.update_id = pu.id) AS relays
  FROM public.pool_update pu
),
step AS (
  SELECT u.*, lag(u.relays) OVER (PARTITION BY u.hash_id ORDER BY u.seq) AS prev_relays
  FROM upd u
)
SELECT
  ph.view                       AS pool_bech32,
  t.ticker_name                 AS ticker,
  st.seq                        AS cert_number,
  b.time                        AS changed_at,
  encode(tx.hash, 'hex')        AS tx_hash,
  st.prev_relays                AS relays_before,
  st.relays                     AS relays_after,
  st.relays - st.prev_relays    AS delta,
  CASE WHEN st.relays > st.prev_relays THEN 'added'
       WHEN st.relays = 0            THEN 'removed_all'
       ELSE 'reduced' END       AS direction
FROM step st
JOIN public.pool_hash ph ON ph.id = st.hash_id
JOIN public.tx tx        ON tx.id = st.registered_tx_id
JOIN public.block b      ON b.id  = tx.block_id
LEFT JOIN LATERAL (
  SELECT o.ticker_name FROM public.off_chain_pool_data o
  WHERE o.pool_id = st.hash_id ORDER BY o.pmr_id DESC, o.id DESC LIMIT 1
) t ON TRUE
WHERE st.prev_relays IS NOT NULL AND st.relays <> st.prev_relays;

CREATE INDEX ON relay.registration_change (pool_bech32);
CREATE INDEX ON relay.registration_change (direction);

-- Per-pool rollup, joined into pool_health.
DROP TABLE IF EXISTS relay.pool_relay_history CASCADE;
CREATE TABLE relay.pool_relay_history AS
SELECT
  pc.pool_hash_id,
  count(*)                                                       AS relay_count_changes,
  count(*) FILTER (WHERE rc.direction = 'added')                 AS relay_additions,
  count(*) FILTER (WHERE rc.direction <> 'added')                AS relay_reductions,
  bool_or(rc.direction = 'removed_all')                          AS ever_removed_all_relays,
  max(rc.changed_at) FILTER (WHERE rc.direction = 'removed_all') AS removed_all_on
FROM relay.pool_current pc
JOIN relay.registration_change rc ON rc.pool_bech32 = pc.pool_bech32
GROUP BY pc.pool_hash_id;

ALTER TABLE relay.pool_relay_history ADD PRIMARY KEY (pool_hash_id);

-- ---------------------------------------------------------------------------
-- 5. Build receipt — every published number is pinned to a tip.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS relay.build_receipt (
  run_at        timestamptz NOT NULL DEFAULT now(),
  stage         text        NOT NULL,
  tip_block_no  bigint,
  tip_epoch_no  int,
  tip_time      timestamptz,
  stake_epoch   int,
  rows_out      bigint,
  notes         text
);

INSERT INTO relay.build_receipt (stage, tip_block_no, tip_epoch_no, tip_time, stake_epoch, rows_out, notes)
SELECT 'registration',
       (SELECT max(block_no) FROM public.block),
       (SELECT max(epoch_no) FROM public.block),
       (SELECT max(time)     FROM public.block),
       (SELECT max(epoch_no) FROM public.epoch_stake),
       (SELECT count(*) FROM relay.pool_current),
       'active pools + registered relay endpoints; pool_stat unused (empty on 13.6.0.4)';

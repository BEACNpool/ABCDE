-- build_relay_foreign_infra.sql — pools that registered somebody else's
-- infrastructure as their own relay set.
--
-- WHY THIS EXISTS. Reachability alone can be gamed, and this dataset was
-- rewarding the gaming. A pool that registers the founding entities' bootstrap
-- backbones scores MULTI_REACHABLE_HOSTS with a high reachable-host count,
-- because those endpoints genuinely answer -- they are IOG's, the Cardano
-- Foundation's and Emurgo's. It also evades every sharing check here: no other
-- pool registers the same strings, so endpoint_shared, shared_resolved_host and
-- shared_domain all see nothing. Credit to @HephyPool for spotting the pattern.
--
-- WHAT IS FLAGGED, AND WHY IT NEEDS NO JUDGEMENT CALL.
-- The `backbone.*` names below are the `bootstrapPeers` shipped in the stock
-- mainnet topology.json. They are the network's shared entry points, published
-- so that any node can find its first peers. They are not any pool's relays --
-- and notably the founding entities' OWN pools do not register them either
-- (IOG1 registers iog1-relays.cardano.iog.io; the CF pools register
-- cfNrN.mainnet.pool.cardanofoundation.org). So flagging a backbone
-- registration requires no allowlist of who is who: nobody legitimately
-- advertises these as their own relay.
--
-- GRADE. That a pool registered these strings is FACT, straight from
-- pool_relay. What it means is left to the reader: a misconfiguration and a
-- deliberate free-ride look identical on-chain, and this table does not
-- distinguish them. It does mean the pool publishes no way to reach ITS node,
-- and that its inbound load sits on infrastructure it does not run.
\set ON_ERROR_STOP on

CREATE SCHEMA IF NOT EXISTS relay;

DROP TABLE IF EXISTS relay.known_infrastructure CASCADE;
CREATE TABLE relay.known_infrastructure (
  host_pattern text PRIMARY KEY,
  operator     text NOT NULL,
  kind         text NOT NULL,
  note         text
);
INSERT INTO relay.known_infrastructure VALUES
 ('backbone.cardano.iog.io',                'IOG',                 'fe_bootstrap_backbone',
  'bootstrapPeers entry in the stock mainnet topology.json'),
 ('backbone.mainnet.cardanofoundation.org', 'Cardano Foundation',  'fe_bootstrap_backbone',
  'bootstrapPeers entry in the stock mainnet topology.json'),
 ('backbone.mainnet.emurgornd.com',         'Emurgo',              'fe_bootstrap_backbone',
  'bootstrapPeers entry in the stock mainnet topology.json'),
 ('relays-new.cardano-mainnet.iohk.io',     'IOG (retired)',       'fe_legacy_relay',
  'the old IOHK public relay; no longer resolves at all');

DROP TABLE IF EXISTS relay.foreign_infrastructure CASCADE;
CREATE TABLE relay.foreign_infrastructure AS
SELECT
  pc.pool_bech32, pc.ticker, pc.stake_ada, pc.delegators, pc.pledge_ada,
  ki.operator, ki.kind, e.endpoint_host, e.port,
  (SELECT count(*) FROM public.block b
   JOIN public.slot_leader sl ON sl.id = b.slot_leader_id
   WHERE sl.pool_hash_id = pc.pool_hash_id)          AS blocks_all_time,
  (SELECT count(DISTINCT e2.endpoint) FROM relay.endpoint e2
   WHERE e2.pool_hash_id = pc.pool_hash_id)          AS endpoints_registered,
  (SELECT count(DISTINCT e3.endpoint) FROM relay.endpoint e3
   JOIN relay.known_infrastructure k2 ON e3.endpoint_host = k2.host_pattern
   WHERE e3.pool_hash_id = pc.pool_hash_id)          AS endpoints_foreign
FROM relay.endpoint e
JOIN relay.known_infrastructure ki ON e.endpoint_host = ki.host_pattern
JOIN relay.pool_current pc ON pc.pool_hash_id = e.pool_hash_id;

CREATE INDEX ON relay.foreign_infrastructure (stake_ada DESC);

INSERT INTO relay.build_receipt (stage, tip_block_no, tip_epoch_no, tip_time, stake_epoch, rows_out, notes)
SELECT 'foreign_infrastructure',
       (SELECT max(block_no) FROM public.block), (SELECT max(epoch_no) FROM public.block),
       (SELECT max(time) FROM public.block), (SELECT max(epoch_no) FROM public.epoch_stake),
       (SELECT count(*) FROM relay.foreign_infrastructure),
       'pools registering founding-entity bootstrap backbones as their own relays';

-- build_night_reach.sql — materialize the COMPLETE NIGHT token flow graph.
--
-- Runs ON the abcde warehouse (local `night` schema; public.* stays read-only).
-- Unlike the genesis ADA trace (bounded taint reachability), a native token can
-- be traced EXACTLY: every NIGHT-carrying output descends from the single mint
-- tx through NIGHT-carrying inputs, so the full graph is just "all outputs that
-- ever carried NIGHT" (~1.8M rows) with spend links. depth = MINIMUM hop count
-- from the mint tx. No fan-out cap is needed — wide txs (airdrop/claim batches)
-- are real token flow, not taint noise; the API layer paginates them instead.
--
-- Invocation (see /usr/local/bin/build_night_trace.sh on abcde):
--   psql -d cexplorer_replica -f build_night_reach.sql
--
-- Builds into *_new staging tables, swaps at the end — readers never see a
-- partial build. Receipt row in night.build_receipt per run.

\set ON_ERROR_STOP on

SET work_mem = '1GB';

BEGIN;

CREATE SCHEMA IF NOT EXISTS night;

CREATE TABLE IF NOT EXISTS night.build_receipt (
  built_at timestamptz NOT NULL DEFAULT now(),
  tip_block bigint NOT NULL,
  tip_time timestamptz NOT NULL,
  n_outputs bigint NOT NULL,
  n_unspent bigint NOT NULL,
  n_orphan bigint NOT NULL,        -- depth IS NULL after BFS: should be 0
  max_depth int NOT NULL,
  total_supply numeric NOT NULL,   -- raw units on unspent outputs
  build_seconds numeric NOT NULL
);

DROP TABLE IF EXISTS night.flow_new;
CREATE TABLE night.flow_new (
  tx_id bigint NOT NULL,
  out_index smallint NOT NULL,
  depth int,                       -- min hops from the mint tx; NULL = orphan
  address varchar NOT NULL,
  stake_address varchar,
  qty numeric NOT NULL,            -- raw units (NIGHT has 6 decimals)
  block_no bigint,
  block_time timestamptz,
  spent_by_tx_id bigint,
  PRIMARY KEY (tx_id, out_index)
);

-- every output that ever carried NIGHT, with its spend link
INSERT INTO night.flow_new
  (tx_id, out_index, address, stake_address, qty, block_no, block_time, spent_by_tx_id)
SELECT o.tx_id, o.index, o.address, sa.view, mto.quantity, b.block_no, b.time, ti.tx_in_id
FROM public.multi_asset ma
JOIN public.ma_tx_out mto ON mto.ident = ma.id
JOIN public.tx_out o      ON o.id = mto.tx_out_id
JOIN public.tx t          ON t.id = o.tx_id
JOIN public.block b       ON b.id = t.block_id
LEFT JOIN public.stake_address sa ON sa.id = o.stake_address_id
LEFT JOIN public.tx_in ti ON ti.tx_out_id = o.tx_id AND ti.tx_out_index = o.index
WHERE ma.policy = '\x0691b2fecca1ac4f53cb6dfb00b7013e561d1f34403b957cbb5af1fa'
  AND ma.name   = '\x4e49474854';

CREATE INDEX ON night.flow_new (depth);

-- depth 0: outputs of the single mint tx
UPDATE night.flow_new f SET depth = 0
FROM (
  SELECT mtm.tx_id
  FROM public.ma_tx_mint mtm
  JOIN public.multi_asset ma ON ma.id = mtm.ident
  WHERE ma.policy = '\x0691b2fecca1ac4f53cb6dfb00b7013e561d1f34403b957cbb5af1fa'
    AND ma.name   = '\x4e49474854'
) m
WHERE f.tx_id = m.tx_id;

DO $$
DECLARE
  d int := 0;
  n bigint;
  t0 timestamptz := clock_timestamp();
BEGIN
  LOOP
    UPDATE night.flow_new c SET depth = d + 1
    FROM (
      SELECT DISTINCT spent_by_tx_id AS tx_id
      FROM night.flow_new WHERE depth = d AND spent_by_tx_id IS NOT NULL
    ) p
    WHERE c.tx_id = p.tx_id AND c.depth IS NULL;
    GET DIAGNOSTICS n = ROW_COUNT;
    RAISE NOTICE 'depth % -> % outputs (% elapsed)', d + 1, n, clock_timestamp() - t0;
    EXIT WHEN n = 0;
    d := d + 1;
    -- self-send chains can run deep, but not unbounded; hard stop = data bug
    IF d > 5000 THEN RAISE WARNING 'depth cap 5000 hit — investigate'; EXIT; END IF;
  END LOOP;
END $$;

CREATE INDEX ON night.flow_new (address);
CREATE INDEX ON night.flow_new (stake_address) WHERE stake_address IS NOT NULL;
CREATE INDEX ON night.flow_new (spent_by_tx_id) WHERE spent_by_tx_id IS NULL;

INSERT INTO night.build_receipt
  (tip_block, tip_time, n_outputs, n_unspent, n_orphan, max_depth, total_supply, build_seconds)
SELECT
  (SELECT max(block_no) FROM public.block),
  (SELECT max(time) FROM public.block),
  (SELECT count(*) FROM night.flow_new),
  (SELECT count(*) FROM night.flow_new WHERE spent_by_tx_id IS NULL),
  (SELECT count(*) FROM night.flow_new WHERE depth IS NULL),
  (SELECT coalesce(max(depth), 0) FROM night.flow_new),
  (SELECT coalesce(sum(qty), 0) FROM night.flow_new WHERE spent_by_tx_id IS NULL),
  extract(epoch FROM clock_timestamp() - now());

-- swap staging into place (view depends on the table — drop it first, recreated below)
DROP VIEW IF EXISTS night.current_holders;
DROP TABLE IF EXISTS night.flow;
ALTER TABLE night.flow_new RENAME TO flow;

-- where NIGHT sits NOW (FACT: unspent at tip). Address is on-chain linkage,
-- never a real-world identity claim.
CREATE OR REPLACE VIEW night.current_holders AS
SELECT address,
       max(stake_address) AS stake_address,
       sum(qty) / 1e6     AS night,
       count(*)           AS utxos,
       min(depth)         AS min_depth
FROM night.flow
WHERE spent_by_tx_id IS NULL
GROUP BY address;

-- PostgREST exposure (mirrors the trace-schema grant pattern)
GRANT USAGE ON SCHEMA night TO web_anon;
GRANT SELECT ON ALL TABLES IN SCHEMA night TO web_anon;
ALTER DEFAULT PRIVILEGES IN SCHEMA night GRANT SELECT ON TABLES TO web_anon;

COMMIT;

\echo === night build complete ===
SELECT * FROM night.build_receipt ORDER BY built_at DESC LIMIT 1;
SELECT depth, count(*) AS outputs, round(sum(qty) / 1e6) AS night,
       count(*) FILTER (WHERE spent_by_tx_id IS NULL) AS unspent
FROM night.flow GROUP BY depth ORDER BY depth LIMIT 25;

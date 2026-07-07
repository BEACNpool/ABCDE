-- build_genesis_reach.sql — materialize the genesis ADA reachability graph.
--
-- Runs ON the abcde warehouse (local `trace` schema; public.* stays read-only).
-- Semantics match the repo's bounded traces: REACHABILITY, not value attribution
-- — every output of a tx that spends a reached output is reached, EXCEPT that
-- txs with more than :cap outputs are recorded in trace.genesis_wide_tx and not
-- expanded (batch/exchange txs; expanding them turns taint into noise).
-- BFS depth-at-a-time, so `depth` is the MINIMUM hop count from any genesis seed.
--
-- Invocation (see /usr/local/bin/build_genesis_trace.sh on abcde):
--   psql -d cexplorer_replica -v depth=4 -v cap=50 -f build_genesis_reach.sql
--
-- Builds into *_new staging tables, swaps at the end — readers never see a
-- partial build. Receipt row in trace.build_receipt per run.

\set ON_ERROR_STOP on

SET work_mem = '1GB';

SELECT set_config('trace.max_depth', :'depth', false);
SELECT set_config('trace.fanout_cap', :'cap', false);

BEGIN;

CREATE SCHEMA IF NOT EXISTS trace;

CREATE TABLE IF NOT EXISTS trace.build_receipt (
  built_at timestamptz NOT NULL DEFAULT now(),
  tip_block bigint NOT NULL,
  tip_time timestamptz NOT NULL,
  max_depth int NOT NULL,
  fanout_cap int NOT NULL,
  n_seed bigint NOT NULL,
  n_reach bigint NOT NULL,
  n_wide bigint NOT NULL,
  build_seconds numeric NOT NULL
);

DROP TABLE IF EXISTS trace.genesis_reach_new;
CREATE TABLE trace.genesis_reach_new (
  tx_id bigint NOT NULL,
  out_index smallint NOT NULL,
  depth int NOT NULL,
  address varchar NOT NULL,
  value numeric NOT NULL,
  block_no bigint,             -- NULL for the genesis pseudo-block
  block_time timestamptz,
  spent_by_tx_id bigint,
  PRIMARY KEY (tx_id, out_index)
);

DROP TABLE IF EXISTS trace.genesis_wide_tx_new;
CREATE TABLE trace.genesis_wide_tx_new (
  tx_id bigint PRIMARY KEY,
  first_depth int NOT NULL,    -- depth the trace would have assigned its outputs
  n_outputs int NOT NULL
);

DROP TABLE IF EXISTS trace._frontier_spends;
CREATE TABLE trace._frontier_spends (spend_tx_id bigint PRIMARY KEY);

-- depth 0: every output of the 14,505 Byron genesis pseudo-txs (block id = 1)
INSERT INTO trace.genesis_reach_new
  (tx_id, out_index, depth, address, value, block_no, block_time)
SELECT o.tx_id, o.index, 0, o.address, o.value, b.block_no, b.time
FROM public.tx t
JOIN public.tx_out o ON o.tx_id = t.id
JOIN public.block b ON b.id = t.block_id
WHERE t.block_id = 1;

DO $$
DECLARE
  d int := 0;
  max_depth int := current_setting('trace.max_depth')::int;
  cap int := current_setting('trace.fanout_cap')::int;
  t0 timestamptz := clock_timestamp();
  n_new bigint;
BEGIN
  WHILE d < max_depth LOOP
    TRUNCATE trace._frontier_spends;

    INSERT INTO trace._frontier_spends (spend_tx_id)
    SELECT DISTINCT ti.tx_in_id
    FROM trace.genesis_reach_new r
    JOIN public.tx_in ti
      ON ti.tx_out_id = r.tx_id AND ti.tx_out_index = r.out_index
    WHERE r.depth = d;

    INSERT INTO trace.genesis_wide_tx_new (tx_id, first_depth, n_outputs)
    SELECT f.spend_tx_id, d + 1, c.n
    FROM trace._frontier_spends f
    JOIN LATERAL (
      SELECT count(*) AS n FROM public.tx_out o WHERE o.tx_id = f.spend_tx_id
    ) c ON true
    WHERE c.n > cap
    ON CONFLICT (tx_id) DO NOTHING;

    INSERT INTO trace.genesis_reach_new
      (tx_id, out_index, depth, address, value, block_no, block_time)
    SELECT o.tx_id, o.index, d + 1, o.address, o.value, b.block_no, b.time
    FROM trace._frontier_spends f
    JOIN public.tx_out o ON o.tx_id = f.spend_tx_id
    JOIN public.tx t ON t.id = o.tx_id
    JOIN public.block b ON b.id = t.block_id
    WHERE NOT EXISTS (
      SELECT 1 FROM trace.genesis_wide_tx_new w WHERE w.tx_id = f.spend_tx_id
    )
    ON CONFLICT (tx_id, out_index) DO NOTHING;

    GET DIAGNOSTICS n_new = ROW_COUNT;
    RAISE NOTICE 'depth % -> % new outputs (% elapsed)',
      d + 1, n_new, clock_timestamp() - t0;
    EXIT WHEN n_new = 0;
    d := d + 1;
  END LOOP;
END $$;

DROP TABLE trace._frontier_spends;

-- mark spent outputs (reachability tip: unspent rows = where traced value sits NOW)
UPDATE trace.genesis_reach_new r
SET spent_by_tx_id = ti.tx_in_id
FROM public.tx_in ti
WHERE ti.tx_out_id = r.tx_id AND ti.tx_out_index = r.out_index;

CREATE INDEX ON trace.genesis_reach_new (address);
CREATE INDEX ON trace.genesis_reach_new (depth);
CREATE INDEX ON trace.genesis_reach_new (spent_by_tx_id) WHERE spent_by_tx_id IS NULL;

INSERT INTO trace.build_receipt
  (tip_block, tip_time, max_depth, fanout_cap, n_seed, n_reach, n_wide, build_seconds)
SELECT
  (SELECT max(block_no) FROM public.block),
  (SELECT max(time) FROM public.block),
  current_setting('trace.max_depth')::int,
  current_setting('trace.fanout_cap')::int,
  (SELECT count(*) FROM trace.genesis_reach_new WHERE depth = 0),
  (SELECT count(*) FROM trace.genesis_reach_new),
  (SELECT count(*) FROM trace.genesis_wide_tx_new),
  extract(epoch FROM clock_timestamp() - now());

-- swap staging into place (view depends on the table — drop it first, recreated below)
DROP VIEW IF EXISTS trace.genesis_current;
DROP TABLE IF EXISTS trace.genesis_reach;
ALTER TABLE trace.genesis_reach_new RENAME TO genesis_reach;
DROP TABLE IF EXISTS trace.genesis_wide_tx;
ALTER TABLE trace.genesis_wide_tx_new RENAME TO genesis_wide_tx;

-- where genesis-derived value sits at the traced depth (FACT: unspent at tip,
-- at this bounded depth — NOT a claim that founders moved or hold anything)
CREATE OR REPLACE VIEW trace.genesis_current AS
SELECT g.*, t.hash AS tx_hash
FROM trace.genesis_reach g
JOIN public.tx t ON t.id = g.tx_id
WHERE g.spent_by_tx_id IS NULL;

COMMIT;

\echo === build complete ===
SELECT * FROM trace.build_receipt ORDER BY built_at DESC LIMIT 1;
SELECT depth, count(*) AS outputs,
       round(sum(value) / 1e6) AS total_ada,
       count(*) FILTER (WHERE spent_by_tx_id IS NULL) AS unspent
FROM trace.genesis_reach GROUP BY depth ORDER BY depth;

-- build_api_schema.sql — the `api` schema: PostgREST RPC functions that power
-- the warehouse desk UI (tools/warehouse-desk/). Beginner-facing search +
-- graph-expansion endpoints over trace.* (genesis ADA) and night.* (NIGHT).
--
-- Fully idempotent: drops and recreates the whole schema (functions only —
-- no data lives here). Run on abcde:
--   psql -d cexplorer_replica -f build_api_schema.sql
--
-- Exposure: add `api` to db-schemas in /usr/local/etc/postgrest.conf, then
-- NOTIFY pgrst. Endpoints are GET /rpc/<fn>?arg=... (functions are STABLE).
-- web_anon gets SELECT on the handful of public.* tables these need; the
-- public schema itself is NOT exposed through PostgREST.

\set ON_ERROR_STOP on

BEGIN;

DROP SCHEMA IF EXISTS api CASCADE;
CREATE SCHEMA api;

GRANT USAGE ON SCHEMA api TO web_anon;
ALTER DEFAULT PRIVILEGES IN SCHEMA api GRANT EXECUTE ON FUNCTIONS TO web_anon;

-- read grants the api functions need (run as invoker = web_anon)
GRANT SELECT ON public.tx, public.tx_out, public.tx_in, public.block,
                public.multi_asset, public.ma_tx_out, public.ma_tx_mint,
                public.stake_address, public.pool_hash
TO web_anon;

-- ---------------------------------------------------------------------------
-- $handle resolution (ADA Handle policy; CIP-68 user token preferred,
-- legacy fallback). Current holder = the unspent output carrying the asset.
-- ---------------------------------------------------------------------------
CREATE FUNCTION api.resolve_handle(h text)
RETURNS TABLE (handle text, kind text, address varchar, stake_address varchar)
LANGUAGE sql STABLE AS $fn$
  WITH want AS (SELECT lower(ltrim(trim(h), '$')) AS nm),
  asset AS (
    SELECT ma.id,
           CASE WHEN ma.name = ('\x000de140'::bytea || convert_to(w.nm, 'UTF8'))
                THEN 'cip68' ELSE 'legacy' END AS kind
    FROM public.multi_asset ma, want w
    WHERE ma.policy = '\xf0ff48bbb7bbe9d59a40f1ce90e9e9d0ff5002ec48f232b49ca0fb9a'
      AND (ma.name = convert_to(w.nm, 'UTF8')
           OR ma.name = '\x000de140'::bytea || convert_to(w.nm, 'UTF8'))
  )
  SELECT '$' || w.nm, a.kind, o.address, sa.view
  FROM want w, asset a
  JOIN public.ma_tx_out mto ON mto.ident = a.id
  JOIN public.tx_out o      ON o.id = mto.tx_out_id
  LEFT JOIN public.stake_address sa ON sa.id = o.stake_address_id
  LEFT JOIN public.tx_in ti ON ti.tx_out_id = o.tx_id AND ti.tx_out_index = o.index
  WHERE ti.id IS NULL
  ORDER BY a.kind = 'cip68' DESC
  LIMIT 1
$fn$;

-- ---------------------------------------------------------------------------
-- address summary: where it stands now + whether the trace graphs reach it
-- ---------------------------------------------------------------------------
CREATE FUNCTION api.address_summary(a text)
RETURNS jsonb
LANGUAGE sql STABLE AS $fn$
  SELECT jsonb_build_object(
    'address', a,
    'unspent', (
      SELECT jsonb_build_object('utxos', count(*), 'ada', round(coalesce(sum(o.value),0) / 1e6))
      FROM public.tx_out o
      LEFT JOIN public.tx_in ti ON ti.tx_out_id = o.tx_id AND ti.tx_out_index = o.index
      WHERE o.address = a AND ti.id IS NULL
    ),
    'activity', (
      SELECT jsonb_build_object('first_seen', min(b.time), 'last_seen', max(b.time), 'outputs_ever', count(*))
      FROM public.tx_out o
      JOIN public.tx t ON t.id = o.tx_id JOIN public.block b ON b.id = t.block_id
      WHERE o.address = a
    ),
    'genesis_trace', (
      SELECT jsonb_build_object('hits', count(*), 'min_depth', min(depth),
                                'ada', round(coalesce(sum(value),0) / 1e6),
                                'unspent_hits', count(*) FILTER (WHERE spent_by_tx_id IS NULL))
      FROM trace.genesis_reach WHERE address = a
    ),
    'night_trace', (
      SELECT jsonb_build_object('hits', count(*), 'min_depth', min(depth),
                                'night', round(coalesce(sum(qty),0) / 1e6),
                                'unspent_hits', count(*) FILTER (WHERE spent_by_tx_id IS NULL))
      FROM night.flow WHERE address = a
    ),
    'handles', (
      SELECT coalesce(jsonb_agg(DISTINCT '$' || convert_from(
               CASE WHEN substring(ma.name FROM 1 FOR 4) = '\x000de140'::bytea
                    THEN substring(ma.name FROM 5) ELSE ma.name END,
               'UTF8')), '[]'::jsonb)
      FROM public.tx_out o
      JOIN public.ma_tx_out mto ON mto.tx_out_id = o.id
      JOIN public.multi_asset ma ON ma.id = mto.ident
      LEFT JOIN public.tx_in ti ON ti.tx_out_id = o.tx_id AND ti.tx_out_index = o.index
      WHERE o.address = a AND ti.id IS NULL
        AND ma.policy = '\xf0ff48bbb7bbe9d59a40f1ce90e9e9d0ff5002ec48f232b49ca0fb9a'
        -- only names that are safe to render: CIP-68 user tokens or NUL-free legacy
        AND (substring(ma.name FROM 1 FOR 4) = '\x000de140'::bytea
             OR position('\x00'::bytea IN ma.name) = 0)
    )
  )
$fn$;

-- ---------------------------------------------------------------------------
-- tx summary: block context + ins/outs, with trace-graph flags per output
-- ---------------------------------------------------------------------------
CREATE FUNCTION api.tx_summary(h text)
RETURNS jsonb
LANGUAGE sql STABLE AS $fn$
  WITH t AS (
    SELECT tx.id, tx.hash, tx.fee, b.block_no, b.time
    FROM public.tx JOIN public.block b ON b.id = tx.block_id
    WHERE tx.hash = decode(lower(trim(h)), 'hex')
  )
  SELECT CASE WHEN NOT EXISTS (SELECT 1 FROM t) THEN
    jsonb_build_object('found', false)
  ELSE (
    SELECT jsonb_build_object(
      'found', true,
      'tx_hash', encode(t.hash, 'hex'),
      'block_no', t.block_no, 'time', t.time,
      'fee_ada', round(t.fee / 1e6, 2),
      'outputs', (
        SELECT coalesce(jsonb_agg(jsonb_build_object(
                 'index', o.index, 'address', o.address, 'ada', round(o.value / 1e6),
                 'genesis_depth', gr.depth, 'night_qty', round(coalesce(nf.qty,0) / 1e6),
                 'spent', (ti.id IS NOT NULL)) ORDER BY o.index), '[]'::jsonb)
        FROM public.tx_out o
        LEFT JOIN trace.genesis_reach gr ON gr.tx_id = o.tx_id AND gr.out_index = o.index
        LEFT JOIN night.flow nf ON nf.tx_id = o.tx_id AND nf.out_index = o.index
        LEFT JOIN public.tx_in ti ON ti.tx_out_id = o.tx_id AND ti.tx_out_index = o.index
        WHERE o.tx_id = t.id
      ),
      'inputs', (
        SELECT coalesce(jsonb_agg(jsonb_build_object(
                 'address', so.address, 'ada', round(so.value / 1e6),
                 'src_tx', encode(st.hash, 'hex'), 'src_index', ti.tx_out_index,
                 'genesis_depth', gr.depth) ORDER BY ti.id), '[]'::jsonb)
        FROM public.tx_in ti
        JOIN public.tx_out so ON so.tx_id = ti.tx_out_id AND so.index = ti.tx_out_index
        JOIN public.tx st ON st.id = ti.tx_out_id
        LEFT JOIN trace.genesis_reach gr ON gr.tx_id = so.tx_id AND gr.out_index = so.index
        WHERE ti.tx_in_id = t.id
      )
    ) FROM t
  ) END
$fn$;

-- ---------------------------------------------------------------------------
-- graph overviews (receipt + per-depth rollup)
-- ---------------------------------------------------------------------------
CREATE FUNCTION api.genesis_overview()
RETURNS jsonb
LANGUAGE sql STABLE AS $fn$
  SELECT jsonb_build_object(
    'receipt', (SELECT to_jsonb(r) FROM (
       SELECT built_at, tip_block, tip_time, max_depth, fanout_cap, n_seed, n_reach, n_wide
       FROM trace.build_receipt ORDER BY built_at DESC LIMIT 1) r),
    'depths', (SELECT coalesce(jsonb_agg(to_jsonb(d) ORDER BY d.depth), '[]'::jsonb) FROM (
       SELECT depth, count(*) AS outputs, round(sum(value) / 1e6) AS ada,
              count(*) FILTER (WHERE spent_by_tx_id IS NULL) AS unspent
       FROM trace.genesis_reach GROUP BY depth) d)
  )
$fn$;

CREATE FUNCTION api.night_overview()
RETURNS jsonb
LANGUAGE sql STABLE AS $fn$
  SELECT jsonb_build_object(
    'receipt', (SELECT to_jsonb(r) FROM (
       SELECT built_at, tip_block, tip_time, n_outputs, n_unspent, n_orphan, max_depth,
              round(total_supply / 1e6) AS supply_night
       FROM night.build_receipt ORDER BY built_at DESC LIMIT 1) r),
    'depths', (SELECT coalesce(jsonb_agg(to_jsonb(d) ORDER BY d.depth), '[]'::jsonb) FROM (
       SELECT depth, count(*) AS outputs, round(sum(qty) / 1e6) AS night,
              count(*) FILTER (WHERE spent_by_tx_id IS NULL) AS unspent
       FROM night.flow GROUP BY depth) d),
    'holders', (SELECT count(*) FROM night.current_holders)
  )
$fn$;

-- ---------------------------------------------------------------------------
-- graph roots: entry points for the fan-out visualization
-- ---------------------------------------------------------------------------
CREATE FUNCTION api.genesis_roots(p_limit int DEFAULT 50, p_offset int DEFAULT 0)
RETURNS TABLE (tx_id bigint, out_index smallint, tx_hash text, address varchar,
               ada numeric, spent boolean, n_children bigint)
LANGUAGE sql STABLE AS $fn$
  SELECT g.tx_id, g.out_index, encode(t.hash, 'hex'), g.address,
         round(g.value / 1e6), g.spent_by_tx_id IS NOT NULL,
         (SELECT count(*) FROM trace.genesis_reach c WHERE c.tx_id = g.spent_by_tx_id)
  FROM trace.genesis_reach g
  JOIN public.tx t ON t.id = g.tx_id
  WHERE g.depth = 0
  ORDER BY g.value DESC
  LIMIT least(p_limit, 500) OFFSET p_offset
$fn$;

CREATE FUNCTION api.night_roots()
RETURNS TABLE (tx_id bigint, out_index smallint, tx_hash text, address varchar,
               night numeric, spent boolean, n_children bigint)
LANGUAGE sql STABLE AS $fn$
  SELECT f.tx_id, f.out_index, encode(t.hash, 'hex'), f.address,
         round(f.qty / 1e6), f.spent_by_tx_id IS NOT NULL,
         (SELECT count(*) FROM night.flow c WHERE c.tx_id = f.spent_by_tx_id)
  FROM night.flow f
  JOIN public.tx t ON t.id = f.tx_id
  WHERE f.depth = 0
  ORDER BY f.qty DESC
$fn$;

-- ---------------------------------------------------------------------------
-- graph expansion: children (downstream) and parents (upstream) of a node.
-- A node is one output (tx_id, out_index). Children = the outputs of the tx
-- that SPENT this node; parents = graph outputs spent BY this node's tx.
-- ---------------------------------------------------------------------------
CREATE FUNCTION api.trace_children(p_tx_id bigint, p_out_index int,
                                   p_limit int DEFAULT 100, p_offset int DEFAULT 0)
RETURNS jsonb
LANGUAGE sql STABLE AS $fn$
  WITH node AS (
    SELECT g.*, (SELECT hash FROM public.tx WHERE id = g.spent_by_tx_id) AS spend_hash
    FROM trace.genesis_reach g
    WHERE g.tx_id = p_tx_id AND g.out_index = p_out_index
  )
  SELECT CASE
    WHEN NOT EXISTS (SELECT 1 FROM node) THEN jsonb_build_object('found', false)
    WHEN (SELECT spent_by_tx_id FROM node) IS NULL THEN
      jsonb_build_object('found', true, 'spent', false, 'children', '[]'::jsonb)
    WHEN EXISTS (SELECT 1 FROM trace.genesis_wide_tx w
                 WHERE w.tx_id = (SELECT spent_by_tx_id FROM node)) THEN
      jsonb_build_object('found', true, 'spent', true, 'wide', true,
        'spend_tx', (SELECT encode(spend_hash, 'hex') FROM node),
        'n_outputs', (SELECT n_outputs FROM trace.genesis_wide_tx
                      WHERE tx_id = (SELECT spent_by_tx_id FROM node)))
    ELSE jsonb_build_object('found', true, 'spent', true, 'wide', false,
      'spend_tx', (SELECT encode(spend_hash, 'hex') FROM node),
      'n_children', (SELECT count(*) FROM trace.genesis_reach c
                     WHERE c.tx_id = (SELECT spent_by_tx_id FROM node)),
      'children', (
        SELECT coalesce(jsonb_agg(jsonb_build_object(
                 'tx_id', c.tx_id, 'out_index', c.out_index, 'depth', c.depth,
                 'address', c.address, 'ada', round(c.value / 1e6),
                 'spent', c.spent_by_tx_id IS NOT NULL,
                 'n_children', (SELECT count(*) FROM trace.genesis_reach cc
                                WHERE cc.tx_id = c.spent_by_tx_id))
               ORDER BY c.value DESC), '[]'::jsonb)
        FROM (SELECT * FROM trace.genesis_reach c
              WHERE c.tx_id = (SELECT spent_by_tx_id FROM node)
              ORDER BY c.value DESC
              LIMIT least(p_limit, 200) OFFSET p_offset) c
      ))
  END
$fn$;

CREATE FUNCTION api.trace_parents(p_tx_id bigint)
RETURNS TABLE (tx_id bigint, out_index smallint, depth int, address varchar,
               ada numeric, tx_hash text)
LANGUAGE sql STABLE AS $fn$
  SELECT g.tx_id, g.out_index, g.depth, g.address, round(g.value / 1e6),
         encode(t.hash, 'hex')
  FROM trace.genesis_reach g
  JOIN public.tx t ON t.id = g.tx_id
  WHERE g.spent_by_tx_id = p_tx_id
  ORDER BY g.value DESC
  LIMIT 200
$fn$;

CREATE FUNCTION api.night_children(p_tx_id bigint, p_out_index int,
                                   p_limit int DEFAULT 100, p_offset int DEFAULT 0)
RETURNS jsonb
LANGUAGE sql STABLE AS $fn$
  WITH node AS (
    SELECT f.*, (SELECT hash FROM public.tx WHERE id = f.spent_by_tx_id) AS spend_hash
    FROM night.flow f
    WHERE f.tx_id = p_tx_id AND f.out_index = p_out_index
  )
  SELECT CASE
    WHEN NOT EXISTS (SELECT 1 FROM node) THEN jsonb_build_object('found', false)
    WHEN (SELECT spent_by_tx_id FROM node) IS NULL THEN
      jsonb_build_object('found', true, 'spent', false, 'children', '[]'::jsonb)
    ELSE jsonb_build_object('found', true, 'spent', true,
      'spend_tx', (SELECT encode(spend_hash, 'hex') FROM node),
      'n_children', (SELECT count(*) FROM night.flow c
                     WHERE c.tx_id = (SELECT spent_by_tx_id FROM node)),
      'children', (
        SELECT coalesce(jsonb_agg(jsonb_build_object(
                 'tx_id', c.tx_id, 'out_index', c.out_index, 'depth', c.depth,
                 'address', c.address, 'night', round(c.qty / 1e6),
                 'spent', c.spent_by_tx_id IS NOT NULL,
                 'n_children', (SELECT count(*) FROM night.flow cc
                                WHERE cc.tx_id = c.spent_by_tx_id))
               ORDER BY c.qty DESC), '[]'::jsonb)
        FROM (SELECT * FROM night.flow c
              WHERE c.tx_id = (SELECT spent_by_tx_id FROM node)
              ORDER BY c.qty DESC
              LIMIT least(p_limit, 200) OFFSET p_offset) c
      ))
  END
$fn$;

CREATE FUNCTION api.night_parents(p_tx_id bigint)
RETURNS TABLE (tx_id bigint, out_index smallint, depth int, address varchar,
               night numeric, tx_hash text)
LANGUAGE sql STABLE AS $fn$
  SELECT f.tx_id, f.out_index, f.depth, f.address, round(f.qty / 1e6),
         encode(t.hash, 'hex')
  FROM night.flow f
  JOIN public.tx t ON t.id = f.tx_id
  WHERE f.spent_by_tx_id = p_tx_id
  ORDER BY f.qty DESC
  LIMIT 200
$fn$;

-- ---------------------------------------------------------------------------
-- leaderboards: where traced value sits NOW
-- ---------------------------------------------------------------------------
CREATE FUNCTION api.genesis_top_current(p_limit int DEFAULT 50)
RETURNS TABLE (address varchar, ada numeric, utxos bigint, min_depth int)
LANGUAGE sql STABLE AS $fn$
  SELECT address, round(sum(value) / 1e6), count(*), min(depth)
  FROM trace.genesis_reach
  WHERE spent_by_tx_id IS NULL
  GROUP BY address
  ORDER BY sum(value) DESC
  LIMIT least(p_limit, 500)
$fn$;

CREATE FUNCTION api.night_top_holders(p_limit int DEFAULT 50)
RETURNS TABLE (address varchar, stake_address varchar, night numeric, utxos bigint, min_depth int)
LANGUAGE sql STABLE AS $fn$
  SELECT address, stake_address, round(night), utxos, min_depth
  FROM night.current_holders
  ORDER BY night DESC
  LIMIT least(p_limit, 500)
$fn$;

-- ---------------------------------------------------------------------------
-- universal search: classify the query and dispatch
-- ---------------------------------------------------------------------------
CREATE FUNCTION api.search(q text)
RETURNS jsonb
LANGUAGE plpgsql STABLE AS $fn$
DECLARE
  s text := trim(q);
  hrec record;
BEGIN
  IF s ~ '^\$' OR s ~ '^[a-z0-9_.-]{1,15}$' THEN
    SELECT * INTO hrec FROM api.resolve_handle(s);
    IF hrec.address IS NOT NULL THEN
      RETURN jsonb_build_object('query', s, 'type', 'handle', 'found', true,
        'handle', hrec.handle, 'kind', hrec.kind, 'address', hrec.address,
        'stake_address', hrec.stake_address,
        'summary', api.address_summary(hrec.address));
    ELSIF s ~ '^\$' THEN
      RETURN jsonb_build_object('query', s, 'type', 'handle', 'found', false);
    END IF;
  END IF;

  IF s ~ '^(addr1|Ae2|DdzFF)' THEN
    RETURN jsonb_build_object('query', s, 'type', 'address',
      'found', EXISTS (SELECT 1 FROM public.tx_out WHERE address = s LIMIT 1),
      'summary', api.address_summary(s));
  END IF;

  IF s ~ '^stake1' THEN
    RETURN jsonb_build_object('query', s, 'type', 'stake',
      'found', EXISTS (SELECT 1 FROM public.stake_address WHERE view = s),
      'night', (SELECT jsonb_build_object('night', round(coalesce(sum(night),0)),
                                          'addresses', count(*))
                FROM night.current_holders WHERE stake_address = s));
  END IF;

  IF s ~ '^pool1' THEN
    RETURN jsonb_build_object('query', s, 'type', 'pool',
      'found', EXISTS (SELECT 1 FROM public.pool_hash WHERE view = s));
  END IF;

  IF s ~ '^[0-9a-fA-F]{64}$' THEN
    RETURN jsonb_build_object('query', s, 'type', 'tx', 'summary', api.tx_summary(s));
  END IF;

  RETURN jsonb_build_object('query', s, 'type', 'unknown', 'found', false);
END
$fn$;

GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA api TO web_anon;

COMMIT;

NOTIFY pgrst, 'reload schema';

\echo === api schema built ===
SELECT proname FROM pg_proc p JOIN pg_namespace n ON n.oid = p.pronamespace
WHERE n.nspname = 'api' ORDER BY proname;

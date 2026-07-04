\timing on
\set ON_ERROR_STOP on

-- Iterative full NIGHT flow export.
-- Avoids one giant recursive CTE by expanding a visited/frontier set level-by-level.
-- Uses TEMP tables only.

DROP TABLE IF EXISTS night_mint_events;
DROP TABLE IF EXISTS night_root_utxo;
DROP TABLE IF EXISTS night_utxo_nodes_all;
DROP TABLE IF EXISTS night_tx_nodes_all;
DROP TABLE IF EXISTS night_flow_frontier;
DROP TABLE IF EXISTS night_flow_next_frontier;
DROP TABLE IF EXISTS night_flow_visited_utxos;
DROP TABLE IF EXISTS night_flow_visited_txs;
DROP TABLE IF EXISTS night_root_reachable_utxos;
DROP TABLE IF EXISTS night_root_reachable_txs;
DROP TABLE IF EXISTS night_edges_utxo_to_tx;
DROP TABLE IF EXISTS night_edges_tx_to_utxo;
DROP TABLE IF EXISTS night_current_leaves;
DROP TABLE IF EXISTS night_unreachable_current_leaves;
DROP TABLE IF EXISTS night_flow_summary;

CREATE TEMP TABLE night_mint_events AS
SELECT
  mtm.id AS ma_tx_mint_row_id,
  t.id AS tx_id_internal,
  encode(t.hash, 'hex') AS tx_hash,
  b.block_no,
  b.time AS block_time_utc,
  mtm.quantity::numeric AS quantity_raw,
  mtm.quantity::numeric / 1000000.0 AS quantity_night
FROM public.ma_tx_mint mtm
JOIN public.multi_asset ma ON ma.id = mtm.ident
JOIN public.tx t ON t.id = mtm.tx_id
JOIN public.block b ON b.id = t.block_id
WHERE encode(ma.policy, 'hex') = '0691b2fecca1ac4f53cb6dfb00b7013e561d1f34403b957cbb5af1fa'
  AND encode(ma.name, 'hex') = '4e49474854'
ORDER BY b.block_no, t.id, mtm.id;

CREATE TEMP TABLE night_root_utxo AS
SELECT
  txo.id AS utxo_row_id,
  t.id AS tx_id_internal,
  encode(t.hash, 'hex') || '#' || txo.index::text AS utxo_node_id,
  encode(t.hash, 'hex') AS tx_hash,
  txo.index AS tx_out_index,
  b.block_no,
  b.time AS block_time_utc,
  txo.address,
  txo.address_has_script,
  encode(txo.payment_cred, 'hex') AS payment_cred_hex,
  COALESCE(sa.view, 'NO_STAKE_CRED') AS stake_addr,
  encode(txo.data_hash, 'hex') AS datum_hash_hex,
  mto.quantity::numeric AS qty_raw,
  mto.quantity::numeric / 1000000.0 AS qty_night
FROM public.tx_out txo
JOIN public.tx t ON t.id = txo.tx_id
JOIN public.block b ON b.id = t.block_id
JOIN public.ma_tx_out mto ON mto.tx_out_id = txo.id
JOIN public.multi_asset ma ON ma.id = mto.ident
JOIN night_mint_events me ON me.tx_id_internal = t.id
LEFT JOIN public.stake_address sa ON sa.id = txo.stake_address_id
WHERE encode(ma.policy, 'hex') = '0691b2fecca1ac4f53cb6dfb00b7013e561d1f34403b957cbb5af1fa'
  AND encode(ma.name, 'hex') = '4e49474854'
  AND mto.quantity > 0;

CREATE TEMP TABLE night_utxo_nodes_all AS
SELECT
  txo.id AS utxo_row_id,
  t.id AS tx_id_internal,
  encode(t.hash, 'hex') || '#' || txo.index::text AS utxo_node_id,
  encode(t.hash, 'hex') AS tx_hash,
  txo.index AS tx_out_index,
  b.block_no,
  b.time AS block_time_utc,
  txo.address,
  txo.address_has_script,
  encode(txo.payment_cred, 'hex') AS payment_cred_hex,
  COALESCE(sa.view, 'NO_STAKE_CRED') AS stake_addr,
  encode(txo.data_hash, 'hex') AS datum_hash_hex,
  mto.quantity::numeric AS qty_raw,
  mto.quantity::numeric / 1000000.0 AS qty_night,
  (ru.utxo_row_id IS NOT NULL) AS is_root,
  (ti.tx_in_id IS NOT NULL) AS is_spent,
  ti.tx_in_id AS spend_tx_id_internal,
  encode(st.hash, 'hex') AS spend_tx_hash,
  sb.block_no AS spend_block_no,
  sb.time AS spend_time_utc
FROM public.tx_out txo
JOIN public.tx t ON t.id = txo.tx_id
JOIN public.block b ON b.id = t.block_id
JOIN public.ma_tx_out mto ON mto.tx_out_id = txo.id
JOIN public.multi_asset ma ON ma.id = mto.ident
LEFT JOIN public.stake_address sa ON sa.id = txo.stake_address_id
LEFT JOIN public.tx_in ti ON ti.tx_out_id = txo.tx_id AND ti.tx_out_index = txo.index
LEFT JOIN public.tx st ON st.id = ti.tx_in_id
LEFT JOIN public.block sb ON sb.id = st.block_id
LEFT JOIN night_root_utxo ru ON ru.utxo_row_id = txo.id
WHERE encode(ma.policy, 'hex') = '0691b2fecca1ac4f53cb6dfb00b7013e561d1f34403b957cbb5af1fa'
  AND encode(ma.name, 'hex') = '4e49474854';

CREATE INDEX ON night_utxo_nodes_all (utxo_row_id);
CREATE INDEX ON night_utxo_nodes_all (tx_id_internal);
CREATE INDEX ON night_utxo_nodes_all (spend_tx_id_internal);
CREATE INDEX ON night_utxo_nodes_all (is_spent);
CREATE INDEX ON night_utxo_nodes_all (is_root);

CREATE TEMP TABLE night_tx_nodes_all AS
WITH night_input AS (
  SELECT spend_tx_id_internal AS tx_id_internal, COUNT(*) AS night_input_utxo_count, SUM(qty_raw) AS night_input_qty_raw
  FROM night_utxo_nodes_all
  WHERE spend_tx_id_internal IS NOT NULL
  GROUP BY spend_tx_id_internal
), night_output AS (
  SELECT tx_id_internal, COUNT(*) AS night_output_utxo_count, SUM(qty_raw) AS night_output_qty_raw
  FROM night_utxo_nodes_all
  GROUP BY tx_id_internal
), tx_ids AS (
  SELECT tx_id_internal FROM night_input
  UNION
  SELECT tx_id_internal FROM night_output
)
SELECT
  x.tx_id_internal,
  'tx:' || encode(t.hash, 'hex') AS tx_node_id,
  encode(t.hash, 'hex') AS tx_hash,
  b.block_no,
  b.time AS block_time_utc,
  (ni.tx_id_internal IS NOT NULL) AS has_night_input,
  (no.tx_id_internal IS NOT NULL) AS has_night_output,
  COALESCE(ni.night_input_utxo_count, 0) AS night_input_utxo_count,
  COALESCE(ni.night_input_qty_raw, 0) AS night_input_qty_raw,
  COALESCE(ni.night_input_qty_raw, 0) / 1000000.0 AS night_input_qty_night,
  COALESCE(no.night_output_utxo_count, 0) AS night_output_utxo_count,
  COALESCE(no.night_output_qty_raw, 0) AS night_output_qty_raw,
  COALESCE(no.night_output_qty_raw, 0) / 1000000.0 AS night_output_qty_night
FROM tx_ids x
JOIN public.tx t ON t.id = x.tx_id_internal
JOIN public.block b ON b.id = t.block_id
LEFT JOIN night_input ni ON ni.tx_id_internal = x.tx_id_internal
LEFT JOIN night_output no ON no.tx_id_internal = x.tx_id_internal;

CREATE INDEX ON night_tx_nodes_all (tx_id_internal);

CREATE TEMP TABLE night_flow_visited_utxos (
  utxo_row_id bigint PRIMARY KEY,
  level_no integer NOT NULL
);

CREATE TEMP TABLE night_flow_visited_txs (
  tx_id_internal bigint PRIMARY KEY,
  first_level_no integer NOT NULL
);

CREATE TEMP TABLE night_flow_frontier (
  utxo_row_id bigint PRIMARY KEY,
  level_no integer NOT NULL
);

INSERT INTO night_flow_visited_utxos (utxo_row_id, level_no)
SELECT utxo_row_id, 0 FROM night_root_utxo;

INSERT INTO night_flow_frontier (utxo_row_id, level_no)
SELECT utxo_row_id, 0 FROM night_root_utxo;

DO $$
DECLARE
  frontier_count integer;
  next_count integer;
  curr_level integer := 0;
BEGIN
  LOOP
    SELECT COUNT(*) INTO frontier_count FROM night_flow_frontier;
    RAISE NOTICE 'night iterative frontier level %, frontier size %', curr_level, frontier_count;
    EXIT WHEN frontier_count = 0;

    INSERT INTO night_flow_visited_txs (tx_id_internal, first_level_no)
    SELECT DISTINCT parent.spend_tx_id_internal, curr_level + 1
    FROM night_flow_frontier f
    JOIN night_utxo_nodes_all parent ON parent.utxo_row_id = f.utxo_row_id
    WHERE parent.spend_tx_id_internal IS NOT NULL
    ON CONFLICT (tx_id_internal) DO NOTHING;

    CREATE TEMP TABLE night_flow_next_frontier ON COMMIT DROP AS
    SELECT DISTINCT child.utxo_row_id, curr_level + 1 AS level_no
    FROM night_flow_frontier f
    JOIN night_utxo_nodes_all parent ON parent.utxo_row_id = f.utxo_row_id
    JOIN night_utxo_nodes_all child ON child.tx_id_internal = parent.spend_tx_id_internal
    LEFT JOIN night_flow_visited_utxos seen ON seen.utxo_row_id = child.utxo_row_id
    WHERE parent.spend_tx_id_internal IS NOT NULL
      AND seen.utxo_row_id IS NULL;

    SELECT COUNT(*) INTO next_count FROM night_flow_next_frontier;
    RAISE NOTICE 'night iterative next frontier level %, size %', curr_level + 1, next_count;

    INSERT INTO night_flow_visited_utxos (utxo_row_id, level_no)
    SELECT utxo_row_id, level_no FROM night_flow_next_frontier
    ON CONFLICT (utxo_row_id) DO NOTHING;

    TRUNCATE night_flow_frontier;
    INSERT INTO night_flow_frontier (utxo_row_id, level_no)
    SELECT utxo_row_id, level_no FROM night_flow_next_frontier;

    DROP TABLE night_flow_next_frontier;
    curr_level := curr_level + 1;
  END LOOP;
END $$;

CREATE TEMP TABLE night_root_reachable_utxos AS
SELECT a.*, v.level_no AS flow_level
FROM night_utxo_nodes_all a
JOIN night_flow_visited_utxos v ON v.utxo_row_id = a.utxo_row_id;

CREATE INDEX ON night_root_reachable_utxos (utxo_row_id);
CREATE INDEX ON night_root_reachable_utxos (tx_id_internal);
CREATE INDEX ON night_root_reachable_utxos (spend_tx_id_internal);
CREATE INDEX ON night_root_reachable_utxos (is_spent);

CREATE TEMP TABLE night_root_reachable_txs AS
SELECT t.*, v.first_level_no AS flow_level
FROM night_tx_nodes_all t
JOIN night_flow_visited_txs v ON v.tx_id_internal = t.tx_id_internal;

CREATE TEMP TABLE night_edges_utxo_to_tx AS
SELECT
  'utxo:' || utxo_node_id AS source_node_id,
  'tx:' || spend_tx_hash AS target_node_id,
  utxo_node_id AS source_utxo_node_id,
  spend_tx_hash AS target_tx_hash,
  spend_block_no,
  spend_time_utc,
  qty_raw AS source_qty_raw,
  qty_night AS source_qty_night,
  address AS source_address,
  address_has_script AS source_has_script,
  flow_level
FROM night_root_reachable_utxos
WHERE spend_tx_id_internal IS NOT NULL;

CREATE TEMP TABLE night_edges_tx_to_utxo AS
SELECT
  'tx:' || tx_hash AS source_node_id,
  'utxo:' || utxo_node_id AS target_node_id,
  tx_hash AS source_tx_hash,
  utxo_node_id AS target_utxo_node_id,
  block_no AS output_block_no,
  block_time_utc AS output_time_utc,
  tx_out_index,
  qty_raw AS output_qty_raw,
  qty_night AS output_qty_night,
  address AS target_address,
  address_has_script AS target_has_script,
  flow_level
FROM night_root_reachable_utxos;

CREATE TEMP TABLE night_current_leaves AS
SELECT *
FROM night_root_reachable_utxos
WHERE is_spent = false
ORDER BY qty_raw DESC, block_no, tx_hash, tx_out_index;

CREATE TEMP TABLE night_unreachable_current_leaves AS
SELECT a.*
FROM night_utxo_nodes_all a
LEFT JOIN night_root_reachable_utxos r ON r.utxo_row_id = a.utxo_row_id
WHERE a.is_spent = false
  AND r.utxo_row_id IS NULL
ORDER BY a.qty_raw DESC, a.block_no, a.tx_hash, a.tx_out_index;

CREATE TEMP TABLE night_flow_summary AS
SELECT 'mint_event_rows' AS metric, COUNT(*)::text AS value FROM night_mint_events
UNION ALL SELECT 'net_minted_raw', COALESCE(SUM(quantity_raw), 0)::text FROM night_mint_events
UNION ALL SELECT 'net_minted_night', (COALESCE(SUM(quantity_raw), 0) / 1000000.0)::text FROM night_mint_events
UNION ALL SELECT 'root_utxo_rows', COUNT(*)::text FROM night_root_utxo
UNION ALL SELECT 'root_utxo_qty_night', (COALESCE(SUM(qty_raw), 0) / 1000000.0)::text FROM night_root_utxo
UNION ALL SELECT 'all_night_utxo_nodes', COUNT(*)::text FROM night_utxo_nodes_all
UNION ALL SELECT 'reachable_utxo_nodes', COUNT(*)::text FROM night_root_reachable_utxos
UNION ALL SELECT 'reachable_tx_nodes', COUNT(*)::text FROM night_root_reachable_txs
UNION ALL SELECT 'reachable_utxo_to_tx_edges', COUNT(*)::text FROM night_edges_utxo_to_tx
UNION ALL SELECT 'reachable_tx_to_utxo_edges', COUNT(*)::text FROM night_edges_tx_to_utxo
UNION ALL SELECT 'reachable_current_leaf_utxos', COUNT(*)::text FROM night_current_leaves
UNION ALL SELECT 'reachable_current_leaf_qty_night', (COALESCE(SUM(qty_raw), 0) / 1000000.0)::text FROM night_current_leaves
UNION ALL SELECT 'unreachable_current_leaf_utxos', COUNT(*)::text FROM night_unreachable_current_leaves
UNION ALL SELECT 'unreachable_current_leaf_qty_night', (COALESCE(SUM(qty_raw), 0) / 1000000.0)::text FROM night_unreachable_current_leaves
UNION ALL SELECT 'max_flow_level', COALESCE(MAX(flow_level),0)::text FROM night_root_reachable_utxos;

\copy (SELECT * FROM night_mint_events ORDER BY block_no, tx_hash) TO '/tmp/night_full_flow_export/35_night_mint_events_abcde.csv' CSV HEADER
\copy (SELECT * FROM night_root_utxo ORDER BY block_no, tx_hash, tx_out_index) TO '/tmp/night_full_flow_export/36_night_root_utxo_abcde.csv' CSV HEADER
\copy (SELECT * FROM night_root_reachable_utxos ORDER BY flow_level, block_no, tx_hash, tx_out_index) TO '/tmp/night_full_flow_export/37_night_reachable_utxo_nodes_abcde.csv' CSV HEADER
\copy (SELECT * FROM night_root_reachable_txs ORDER BY flow_level, block_no, tx_hash) TO '/tmp/night_full_flow_export/38_night_reachable_tx_nodes_abcde.csv' CSV HEADER
\copy (SELECT * FROM night_edges_utxo_to_tx ORDER BY flow_level, spend_block_no, target_tx_hash, source_utxo_node_id) TO '/tmp/night_full_flow_export/39_night_edges_utxo_to_tx_abcde.csv' CSV HEADER
\copy (SELECT * FROM night_edges_tx_to_utxo ORDER BY flow_level, output_block_no, source_tx_hash, target_utxo_node_id) TO '/tmp/night_full_flow_export/40_night_edges_tx_to_utxo_abcde.csv' CSV HEADER
\copy (SELECT * FROM night_current_leaves ORDER BY qty_raw DESC, block_no, tx_hash, tx_out_index) TO '/tmp/night_full_flow_export/41_night_current_leaves_abcde.csv' CSV HEADER
\copy (SELECT * FROM night_unreachable_current_leaves ORDER BY qty_raw DESC, block_no, tx_hash, tx_out_index) TO '/tmp/night_full_flow_export/42_night_unreachable_current_leaves_abcde.csv' CSV HEADER
\copy (SELECT * FROM night_flow_summary) TO '/tmp/night_full_flow_export/43_night_flow_summary_abcde.csv' CSV HEADER

\echo Wrote NIGHT iterative full flow CSV exports to NIGHT/data.

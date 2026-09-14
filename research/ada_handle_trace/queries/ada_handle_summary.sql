-- Human-oriented ADA Handle summary backing query
-- Usage:
--   psql -d cexplorer_replica -v handle='bob' -At -F $'\t' -f queries/ada_handle_summary.sql

\if :{?handle}
\else
\echo 'ERROR: pass -v handle=<name> (without leading $)'
\quit 1
\endif

WITH resolved AS (
  SELECT
    h.handle,
    h.handle_display,
    h.current_owner_address,
    h.current_owner_stake,
    h.tx_hash,
    h.block_no,
    h.slot_no,
    h.epoch_no,
    h.observed_at,
    t.id AS tx_id
  FROM explorer.handle_search h
  JOIN public.tx t
    ON t.hash = decode(h.tx_hash, 'hex')
  WHERE lower(h.handle) = lower(:'handle')
), first_hop AS (
  SELECT DISTINCT
    encode(t_prev.hash::bytea, 'hex') AS source_tx_hash,
    txo_prev.index AS source_tx_out_index,
    txo_prev.address AS source_address,
    COALESCE(sa_prev.view, '-') AS source_stake,
    txo_prev.value AS source_lovelace,
    b_prev.block_no AS source_block_no,
    b_prev.time AS source_block_time
  FROM resolved r
  JOIN public.tx_in ti
    ON ti.tx_in_id = r.tx_id
  JOIN public.tx_out txo_prev
    ON txo_prev.tx_id = ti.tx_out_id
   AND txo_prev.index = ti.tx_out_index
  JOIN public.tx t_prev
    ON t_prev.id = txo_prev.tx_id
  JOIN public.block b_prev
    ON b_prev.id = t_prev.block_id
  LEFT JOIN public.stake_address sa_prev
    ON sa_prev.id = txo_prev.stake_address_id
), stats AS (
  SELECT
    COUNT(*)::text AS first_hop_count,
    COALESCE(SUM(source_lovelace), 0)::text AS first_hop_total_lovelace,
    COUNT(DISTINCT source_address)::text AS distinct_source_addresses,
    COUNT(DISTINCT NULLIF(source_stake, '-'))::text AS distinct_source_stakes,
    COALESCE(MIN(source_block_no), 0)::text AS min_source_block_no,
    COALESCE(MAX(source_block_no), 0)::text AS max_source_block_no
  FROM first_hop
), sample AS (
  SELECT
    source_tx_hash,
    source_tx_out_index::text AS source_tx_out_index,
    source_lovelace::text AS source_lovelace,
    source_block_no::text AS source_block_no,
    source_address,
    source_stake
  FROM first_hop
  ORDER BY source_block_no DESC, source_tx_hash
  LIMIT 5
)
SELECT
  'stats' AS section,
  s.first_hop_count,
  s.first_hop_total_lovelace,
  s.distinct_source_addresses,
  s.distinct_source_stakes,
  s.min_source_block_no,
  s.max_source_block_no
FROM stats s
UNION ALL
SELECT
  'sample' AS section,
  sm.source_tx_hash,
  sm.source_tx_out_index,
  sm.source_lovelace,
  sm.source_block_no,
  sm.source_address,
  sm.source_stake
FROM sample sm;

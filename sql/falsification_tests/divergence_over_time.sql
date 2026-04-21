-- Hypothesis: If the 4th entry was only temporarily co-administered with EMURGO, its descendants may later diverge in spending behavior from EMURGO-tagged descendants.
-- Expected result: A persistently high co-spend fraction supports shared administration; meaningful declines or sustained non-overlap may support independent downstream control.
-- Interpretation: This query is a falsification aid, not a proof of ownership. Byron-era co-spend remains compatible with shared custody.
-- Parameters:
--   :window_blocks  integer block window for co-spend proximity (default 100)
-- Notes:
--   Read-only, SELECT-only. Targets replicated public.* plus local explorer.* overlays when available.

WITH params AS (
  SELECT COALESCE(NULLIF(:'window_blocks', '')::integer, 100) AS window_blocks
),
fourth_seed AS (
  SELECT tx.id AS anchor_tx_id
  FROM public.tx tx
  WHERE tx.hash = decode('5ec95a53fa3bb7dc56864bb6e75f369f00aa20e8d8cdc3b66b2fb88ec1b225ef', 'hex')
),
fourth_descendants AS (
  SELECT DISTINCT te.dest_tx_out_id
  FROM explorer.trace_edges te
  JOIN fourth_seed s ON te.root_tx_id = s.anchor_tx_id
),
emurgo_seed AS (
  SELECT tx.id AS anchor_tx_id
  FROM public.tx tx
  WHERE tx.hash = decode('242608fc18552a4ac83adabcef7155f3b909e83d469ce89735db8f11d3637e38', 'hex')
),
emurgo_descendants AS (
  SELECT DISTINCT te.dest_tx_out_id
  FROM explorer.trace_edges te
  JOIN emurgo_seed s ON te.root_tx_id = s.anchor_tx_id
),
fourth_spends AS (
  SELECT DISTINCT
    fd.dest_tx_out_id,
    tx.id AS spend_tx_id,
    b.epoch_no,
    b.block_no
  FROM fourth_descendants fd
  JOIN public.tx_in ti
    ON ti.tx_out_id = fd.dest_tx_out_id
  JOIN public.tx tx
    ON tx.id = ti.tx_in_id
  JOIN public.block b
    ON b.id = tx.block_id
),
emurgo_spends AS (
  SELECT DISTINCT
    ed.dest_tx_out_id,
    tx.id AS spend_tx_id,
    b.block_no
  FROM emurgo_descendants ed
  JOIN public.tx_in ti
    ON ti.tx_out_id = ed.dest_tx_out_id
  JOIN public.tx tx
    ON tx.id = ti.tx_in_id
  JOIN public.block b
    ON b.id = tx.block_id
),
co_spend_flags AS (
  SELECT
    fs.epoch_no,
    fs.dest_tx_out_id,
    EXISTS (
      SELECT 1
      FROM emurgo_spends es
      CROSS JOIN params p
      WHERE abs(es.block_no - fs.block_no) <= p.window_blocks
    ) AS near_emurgo_spend
  FROM fourth_spends fs
)
SELECT
  epoch_no,
  COUNT(*) AS fourth_entry_spends,
  COUNT(*) FILTER (WHERE near_emurgo_spend) AS near_emurgo_spends,
  ROUND(
    COUNT(*) FILTER (WHERE near_emurgo_spend)::numeric / NULLIF(COUNT(*), 0),
    6
  ) AS fraction_within_window
FROM co_spend_flags
GROUP BY epoch_no
ORDER BY epoch_no;

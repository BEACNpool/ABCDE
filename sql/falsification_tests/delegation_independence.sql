-- Hypothesis: If the 4th entry reflects an independent beneficial owner, its Shelley-era delegation history may include pools not seen in EMURGO delegation history.
-- Expected result: Non-overlapping pools are evidence of potentially independent decision-making and should be reviewed manually.
-- Interpretation: Pool overlap alone does not prove common ownership. Non-overlap is more diagnostic than overlap here.
-- Notes:
--   Read-only, SELECT-only. Uses explorer.* / governance.* derived schemas where available and falls back to replicated public.* delegation history.

WITH fourth_seed AS (
  SELECT tx.id AS anchor_tx_id
  FROM public.tx tx
  WHERE tx.hash = decode('5ec95a53fa3bb7dc56864bb6e75f369f00aa20e8d8cdc3b66b2fb88ec1b225ef', 'hex')
),
emurgo_seed AS (
  SELECT tx.id AS anchor_tx_id
  FROM public.tx tx
  WHERE tx.hash = decode('242608fc18552a4ac83adabcef7155f3b909e83d469ce89735db8f11d3637e38', 'hex')
),
fourth_stakes AS (
  SELECT DISTINCT cam.stake_address
  FROM explorer.trace_edges te
  JOIN fourth_seed s ON te.root_tx_id = s.anchor_tx_id
  JOIN explorer.credential_address_map cam
    ON cam.dest_tx_out_id = te.dest_tx_out_id
  WHERE cam.stake_address IS NOT NULL
),
emurgo_stakes AS (
  SELECT DISTINCT cam.stake_address
  FROM explorer.trace_edges te
  JOIN emurgo_seed s ON te.root_tx_id = s.anchor_tx_id
  JOIN explorer.credential_address_map cam
    ON cam.dest_tx_out_id = te.dest_tx_out_id
  WHERE cam.stake_address IS NOT NULL
),
all_delegations AS (
  SELECT
    sa.view AS stake_address,
    ph.view AS pool_view,
    ph.hash_raw AS pool_hash_raw,
    d.active_epoch_no
  FROM public.delegation d
  JOIN public.stake_address sa
    ON sa.id = d.addr_id
  JOIN public.pool_hash ph
    ON ph.id = d.pool_hash_id
),
fourth_pools AS (
  SELECT DISTINCT ad.pool_view, ad.pool_hash_raw
  FROM all_delegations ad
  JOIN fourth_stakes fs
    ON fs.stake_address = ad.stake_address
),
emurgo_pools AS (
  SELECT DISTINCT ad.pool_view, ad.pool_hash_raw
  FROM all_delegations ad
  JOIN emurgo_stakes es
    ON es.stake_address = ad.stake_address
),
combined AS (
  SELECT
    COALESCE(fp.pool_view, ep.pool_view) AS pool_view,
    COALESCE(fp.pool_hash_raw, ep.pool_hash_raw) AS pool_hash_raw,
    (fp.pool_view IS NOT NULL) AS seen_in_fourth_entry,
    (ep.pool_view IS NOT NULL) AS seen_in_emurgo
  FROM fourth_pools fp
  FULL OUTER JOIN emurgo_pools ep
    ON ep.pool_hash_raw = fp.pool_hash_raw
)
SELECT
  pool_view,
  encode(pool_hash_raw, 'hex') AS pool_hash_hex,
  seen_in_fourth_entry,
  seen_in_emurgo,
  CASE
    WHEN seen_in_fourth_entry AND seen_in_emurgo THEN 'overlap'
    WHEN seen_in_fourth_entry AND NOT seen_in_emurgo THEN 'fourth_only'
    WHEN NOT seen_in_fourth_entry AND seen_in_emurgo THEN 'emurgo_only'
    ELSE 'unknown'
  END AS interpretation_flag
FROM combined
ORDER BY interpretation_flag DESC, pool_view NULLS LAST;

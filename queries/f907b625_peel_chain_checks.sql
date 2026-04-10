-- ============================================================
-- f907b625... clean CF+EMURGO merge downstream peel chain
-- Generated: 2026-04-08
-- ============================================================

-- Root transaction metadata
SELECT
  encode(tx.hash,'hex') AS tx_hash,
  b.epoch_no,
  b.time AS block_time_utc,
  tx.fee,
  tx.size,
  (SELECT COUNT(*) FROM public.tx_in WHERE tx_in_id = tx.id) AS input_count,
  (SELECT COUNT(*) FROM public.tx_out WHERE tx_id = tx.id) AS output_count,
  ROUND((SELECT SUM(value) FROM public.tx_out WHERE tx_id = tx.id)::numeric / 1000000, 6) AS total_output_ada
FROM public.tx
JOIN public.block b ON b.id = tx.block_id
WHERE tx.hash = decode('f907b62584ca76c533f410867bf964c527b2a8251849d93c2b48a5b69e641816','hex');

-- Carry-chain recursion: follow the largest output forward
WITH RECURSIVE chain AS (
  SELECT
    0 AS hop,
    out.id AS carry_out_id,
    out.tx_id AS carry_tx_id,
    out.index AS carry_index,
    out.value::numeric AS carry_value,
    next_tx.id AS next_tx_id,
    encode(next_tx.hash,'hex') AS next_tx_hash
  FROM public.tx root
  JOIN public.tx_out out ON out.tx_id = root.id
  LEFT JOIN public.tx_in ti ON ti.tx_out_id = out.tx_id AND ti.tx_out_index = out.index
  LEFT JOIN public.tx next_tx ON next_tx.id = ti.tx_in_id
  WHERE root.hash = decode('f907b62584ca76c533f410867bf964c527b2a8251849d93c2b48a5b69e641816','hex')

  UNION ALL

  SELECT
    c.hop + 1,
    lo.id,
    lo.tx_id,
    lo.index,
    lo.value::numeric,
    next_tx.id,
    encode(next_tx.hash,'hex')
  FROM chain c
  JOIN LATERAL (
    SELECT o.id, o.tx_id, o.index, o.value
    FROM public.tx_out o
    WHERE o.tx_id = c.next_tx_id
    ORDER BY o.value DESC
    LIMIT 1
  ) lo ON true
  LEFT JOIN public.tx_in ti ON ti.tx_out_id = lo.tx_id AND ti.tx_out_index = lo.index
  LEFT JOIN public.tx next_tx ON next_tx.id = ti.tx_in_id
  WHERE c.next_tx_id IS NOT NULL
    AND c.hop < 12
)
SELECT
  hop,
  carry_out_id,
  carry_index,
  ROUND(carry_value / 1000000, 6) AS carry_ada,
  COALESCE(next_tx_hash, 'UNSPENT') AS spent_in_tx
FROM chain
ORDER BY hop;

-- Large outputs at each hop (captures the 200M / 150M peel pattern)
WITH RECURSIVE chain AS (
  SELECT
    0 AS hop,
    out.id AS carry_out_id,
    out.tx_id AS carry_tx_id,
    out.index AS carry_index,
    out.value::numeric AS carry_value,
    next_tx.id AS next_tx_id,
    encode(next_tx.hash,'hex') AS next_tx_hash
  FROM public.tx root
  JOIN public.tx_out out ON out.tx_id = root.id
  LEFT JOIN public.tx_in ti ON ti.tx_out_id = out.tx_id AND ti.tx_out_index = out.index
  LEFT JOIN public.tx next_tx ON next_tx.id = ti.tx_in_id
  WHERE root.hash = decode('f907b62584ca76c533f410867bf964c527b2a8251849d93c2b48a5b69e641816','hex')

  UNION ALL

  SELECT
    c.hop + 1,
    lo.id,
    lo.tx_id,
    lo.index,
    lo.value::numeric,
    next_tx.id,
    encode(next_tx.hash,'hex')
  FROM chain c
  JOIN LATERAL (
    SELECT o.id, o.tx_id, o.index, o.value
    FROM public.tx_out o
    WHERE o.tx_id = c.next_tx_id
    ORDER BY o.value DESC
    LIMIT 1
  ) lo ON true
  LEFT JOIN public.tx_in ti ON ti.tx_out_id = lo.tx_id AND ti.tx_out_index = lo.index
  LEFT JOIN public.tx next_tx ON next_tx.id = ti.tx_in_id
  WHERE c.next_tx_id IS NOT NULL
    AND c.hop < 12
)
SELECT
  c.hop,
  encode(tx.hash,'hex') AS tx_hash,
  o.id AS tx_out_id,
  o.index,
  ROUND(o.value::numeric / 1000000, 6) AS ada,
  COALESCE(sa.view,'') AS stake_address,
  o.address
FROM chain c
JOIN public.tx tx ON tx.id = c.next_tx_id
JOIN public.tx_out o ON o.tx_id = tx.id
LEFT JOIN public.stake_address sa ON sa.id = o.stake_address_id
WHERE o.value >= 100000000000000
ORDER BY c.hop, o.index;

-- Stake-profile summary for the high-value peel recipients and carry stakes
WITH RECURSIVE chain AS (
  SELECT
    0 AS hop,
    out.id AS carry_out_id,
    out.tx_id AS carry_tx_id,
    out.index AS carry_index,
    out.value::numeric AS carry_value,
    next_tx.id AS next_tx_id,
    encode(next_tx.hash,'hex') AS next_tx_hash
  FROM public.tx root
  JOIN public.tx_out out ON out.tx_id = root.id
  LEFT JOIN public.tx_in ti ON ti.tx_out_id = out.tx_id AND ti.tx_out_index = out.index
  LEFT JOIN public.tx next_tx ON next_tx.id = ti.tx_in_id
  WHERE root.hash = decode('f907b62584ca76c533f410867bf964c527b2a8251849d93c2b48a5b69e641816','hex')

  UNION ALL

  SELECT
    c.hop + 1,
    lo.id,
    lo.tx_id,
    lo.index,
    lo.value::numeric,
    next_tx.id,
    encode(next_tx.hash,'hex')
  FROM chain c
  JOIN LATERAL (
    SELECT o.id, o.tx_id, o.index, o.value
    FROM public.tx_out o
    WHERE o.tx_id = c.next_tx_id
    ORDER BY o.value DESC
    LIMIT 1
  ) lo ON true
  LEFT JOIN public.tx_in ti ON ti.tx_out_id = lo.tx_id AND ti.tx_out_index = lo.index
  LEFT JOIN public.tx next_tx ON next_tx.id = ti.tx_in_id
  WHERE c.next_tx_id IS NOT NULL
    AND c.hop < 12
), stakes AS (
  SELECT DISTINCT sa.id, sa.view
  FROM chain c
  JOIN public.tx tx ON tx.id = c.next_tx_id
  JOIN public.tx_out o ON o.tx_id = tx.id
  JOIN public.stake_address sa ON sa.id = o.stake_address_id
  WHERE o.value >= 100000000000000
)
SELECT
  s.view AS stake_address,
  (SELECT COUNT(*) FROM public.tx_out o WHERE o.stake_address_id = s.id) AS tx_out_count,
  ROUND((SELECT COALESCE(SUM(o.value),0) FROM public.tx_out o WHERE o.stake_address_id = s.id)::numeric / 1000000, 6) AS total_received_ada,
  ROUND((SELECT COALESCE(SUM(o.value),0) FROM public.tx_out o WHERE o.stake_address_id = s.id
         AND NOT EXISTS (
           SELECT 1 FROM public.tx_in i WHERE i.tx_out_id = o.tx_id AND i.tx_out_index = o.index
         ))::numeric / 1000000, 6) AS current_unspent_ada,
  (SELECT MAX(b.epoch_no)
   FROM public.tx_out o
   JOIN public.tx txo ON txo.id = o.tx_id
   JOIN public.block b ON b.id = txo.block_id
   WHERE o.stake_address_id = s.id) AS latest_output_epoch,
  (SELECT opd.ticker_name
   FROM public.delegation d
   JOIN public.tx txd ON txd.id = d.tx_id
   JOIN public.pool_hash ph ON ph.id = d.pool_hash_id
   LEFT JOIN public.off_chain_pool_data opd ON opd.pool_id = ph.id
   WHERE d.addr_id = s.id
   ORDER BY txd.id DESC, opd.id DESC
   LIMIT 1) AS latest_pool_ticker,
  (SELECT opd.json ->> 'name'
   FROM public.delegation d
   JOIN public.tx txd ON txd.id = d.tx_id
   JOIN public.pool_hash ph ON ph.id = d.pool_hash_id
   LEFT JOIN public.off_chain_pool_data opd ON opd.pool_id = ph.id
   WHERE d.addr_id = s.id
   ORDER BY txd.id DESC, opd.id DESC
   LIMIT 1) AS latest_pool_name,
  (SELECT COUNT(*) FROM public.delegation d WHERE d.addr_id = s.id) AS delegation_txs
FROM stakes s
ORDER BY s.view;

-- 200M branch re-funding: later paired top-ups from Hub 1 into the 200M branch and main carry stake
SELECT
  encode(t.hash,'hex') AS tx_hash,
  b.epoch_no,
  b.time AS block_time_utc,
  txo.index,
  ROUND(txo.value::numeric / 1000000, 6) AS ada,
  COALESCE(sa.view,'') AS stake_address,
  txo.address
FROM public.tx t
JOIN public.block b ON b.id = t.block_id
JOIN public.tx_out txo ON txo.tx_id = t.id
LEFT JOIN public.stake_address sa ON sa.id = txo.stake_address_id
WHERE encode(t.hash,'hex') IN (
  '1daba6274dbbe2f6a9cf3a031ee716597e14e7c43b1beec6ee2650ad6ee76b5a',
  '531150c6924b6054d9cc3801297477e9b7aeba0f5ee34f17241e8b97d579e3e0'
)
ORDER BY b.epoch_no, tx_hash, txo.index;

-- Force nested-loop plan here because the tx_in -> tx_out join on large fan-in txs
-- can otherwise devolve into a slow planner choice on this replica.
SET enable_hashjoin = off;
SET enable_mergejoin = off;

WITH target_txs AS (
  SELECT
    t.id,
    encode(t.hash,'hex') AS tx_hash
  FROM public.tx t
  WHERE encode(t.hash,'hex') IN (
    '1daba6274dbbe2f6a9cf3a031ee716597e14e7c43b1beec6ee2650ad6ee76b5a',
    '531150c6924b6054d9cc3801297477e9b7aeba0f5ee34f17241e8b97d579e3e0'
  )
)
SELECT
  tt.tx_hash,
  COUNT(*) AS input_count,
  ROUND(SUM(src.value)::numeric / 1000000, 6) AS total_input_ada,
  COALESCE(sa.view, src.address) AS input_source
FROM target_txs tt
JOIN public.tx_in ti ON ti.tx_in_id = tt.id
JOIN public.tx_out src ON src.tx_id = ti.tx_out_id AND src.index = ti.tx_out_index
LEFT JOIN public.stake_address sa ON sa.id = src.stake_address_id
GROUP BY tt.tx_hash, COALESCE(sa.view, src.address)
ORDER BY tt.tx_hash, total_input_ada DESC;

-- Sample side-branch contrast: later large side-branch txs that self-fund from the same
-- stake credential rather than receiving fresh Hub 1 fan-in.
WITH sample_txs(tx_hash, label) AS (
  VALUES
    ('aa1820467bbe382c73221502cb08e3b921664ec716dc8fda414e475d838621f9', 'u84_follow_on'),
    ('f7b1437de2730ad81df2713554a58a39a0949823a056511468f0b1d074866681', 'ux0_epoch237'),
    ('99791cba75b94932f19dbd8846828195394d1eb71e70da9312de35236fd6e0f5', 'uxz_epoch237')
), sample_ids AS (
  SELECT s.label, t.id, s.tx_hash
  FROM sample_txs s
  JOIN public.tx t ON encode(t.hash,'hex') = s.tx_hash
), sample_inputs AS (
  SELECT si.label, si.tx_hash, ti.tx_out_id, ti.tx_out_index
  FROM sample_ids si
  JOIN public.tx_in ti ON ti.tx_in_id = si.id
)
SELECT
  si.label,
  si.tx_hash,
  COUNT(*) AS input_count,
  ROUND(SUM(src.value)::numeric / 1000000, 6) AS total_input_ada,
  COUNT(DISTINCT COALESCE(sa.view, src.address)) AS distinct_input_sources,
  MIN(COALESCE(sa.view, src.address)) AS min_input_source,
  MAX(COALESCE(sa.view, src.address)) AS max_input_source
FROM sample_inputs si
JOIN public.tx_out src ON src.tx_id = si.tx_out_id AND src.index = si.tx_out_index
LEFT JOIN public.stake_address sa ON sa.id = src.stake_address_id
GROUP BY si.label, si.tx_hash
ORDER BY si.label;

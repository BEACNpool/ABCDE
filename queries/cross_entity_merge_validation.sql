-- Cross-Entity Merge Validation
--
-- Purpose:
--   Validate exemplar merge transactions identified in the local founder-allocation
--   trace exports against a live Cardano db-sync PostgreSQL replica.
--
-- Notes:
--   1. These queries are read-only.
--   2. The candidate transactions below are the three exemplar transactions already
--      identified from the published seed-trace CSVs.
--   3. Replace the hash list or the focal source UTxO list as investigation expands.

-- ============================================================================
-- Query 1: Candidate transaction metadata and input counts
-- ============================================================================
WITH candidate_hashes AS (
  SELECT decode('197f9d27e49345cc085c9a2951d96c77f57f1cd82a71c095b7b7a3b36e74855d', 'hex') AS hash
  UNION ALL
  SELECT decode('34147ef46fd105ed39e3be63ac194e79622fb1bf9ea6e50313a0c3e0e6fd20c3', 'hex')
  UNION ALL
  SELECT decode('571f776c0698c576ddecae145f97e7f284b82ebea70fbc924fa4e2a4a6258020', 'hex')
),
targets AS (
  SELECT tx.id, tx.hash, block.epoch_no, block.slot_no, block.time
  FROM public.tx
  JOIN public.block
    ON block.id = tx.block_id
  JOIN candidate_hashes
    ON candidate_hashes.hash = tx.hash
)
SELECT
  encode(targets.hash, 'hex') AS tx_hash,
  targets.id AS tx_id,
  targets.epoch_no,
  targets.slot_no,
  targets.time AS block_time_utc,
  COUNT(*) AS input_count,
  SUM(source_out.value) AS total_input_lovelace
FROM targets
JOIN public.tx_in
  ON tx_in.tx_in_id = targets.id
JOIN public.tx_out AS source_out
  ON source_out.tx_id = tx_in.tx_out_id
 AND source_out.index = tx_in.tx_out_index
GROUP BY targets.hash, targets.id, targets.epoch_no, targets.slot_no, targets.time
ORDER BY targets.epoch_no, targets.id;

-- ============================================================================
-- Query 2: Candidate transaction outputs
-- ============================================================================
WITH candidate_hashes AS (
  SELECT decode('197f9d27e49345cc085c9a2951d96c77f57f1cd82a71c095b7b7a3b36e74855d', 'hex') AS hash
  UNION ALL
  SELECT decode('34147ef46fd105ed39e3be63ac194e79622fb1bf9ea6e50313a0c3e0e6fd20c3', 'hex')
  UNION ALL
  SELECT decode('571f776c0698c576ddecae145f97e7f284b82ebea70fbc924fa4e2a4a6258020', 'hex')
),
targets AS (
  SELECT tx.id, tx.hash
  FROM public.tx
  JOIN candidate_hashes
    ON candidate_hashes.hash = tx.hash
)
SELECT
  encode(targets.hash, 'hex') AS tx_hash,
  tx_out.id AS dest_tx_out_id,
  tx_out.index AS dest_index,
  tx_out.value AS lovelace,
  COALESCE(sa.view, '') AS stake_address_view,
  tx_out.address
FROM targets
JOIN public.tx_out
  ON tx_out.tx_id = targets.id
LEFT JOIN public.stake_address sa
  ON sa.id = tx_out.stake_address_id
ORDER BY targets.id, tx_out.index;

-- ============================================================================
-- Query 3: Focal source UTxOs that feed the candidate merge transactions
-- ============================================================================
SELECT
  source_out.id AS source_tx_out_id,
  encode(source_tx.hash, 'hex') AS source_tx_hash,
  source_out.index AS source_index,
  source_out.value AS lovelace,
  COALESCE(sa.view, '') AS stake_address_view,
  source_out.address,
  encode(consuming_tx.hash, 'hex') AS consuming_tx_hash
FROM public.tx_out AS source_out
JOIN public.tx AS source_tx
  ON source_tx.id = source_out.tx_id
JOIN public.tx_in
  ON tx_in.tx_out_id = source_out.tx_id
 AND tx_in.tx_out_index = source_out.index
JOIN public.tx AS consuming_tx
  ON consuming_tx.id = tx_in.tx_in_id
LEFT JOIN public.stake_address sa
  ON sa.id = source_out.stake_address_id
WHERE source_out.id IN (
  5034850,
  5035023,
  6273746,
  6337983,
  6742421,
  8064253,
  8926255,
  9036401,
  10748217
)
ORDER BY source_out.id;

-- ============================================================================
-- Query 4: Full input dump for the candidate transactions
-- ============================================================================
WITH candidate_hashes AS (
  SELECT decode('197f9d27e49345cc085c9a2951d96c77f57f1cd82a71c095b7b7a3b36e74855d', 'hex') AS hash
  UNION ALL
  SELECT decode('34147ef46fd105ed39e3be63ac194e79622fb1bf9ea6e50313a0c3e0e6fd20c3', 'hex')
  UNION ALL
  SELECT decode('571f776c0698c576ddecae145f97e7f284b82ebea70fbc924fa4e2a4a6258020', 'hex')
),
targets AS (
  SELECT tx.id, tx.hash
  FROM public.tx
  JOIN candidate_hashes
    ON candidate_hashes.hash = tx.hash
)
SELECT
  encode(targets.hash, 'hex') AS target_tx_hash,
  source_out.id AS source_tx_out_id,
  encode(source_tx.hash, 'hex') AS source_tx_hash,
  source_out.index AS source_index,
  source_out.value AS lovelace,
  COALESCE(sa.view, '') AS stake_address_view,
  source_out.address
FROM targets
JOIN public.tx_in
  ON tx_in.tx_in_id = targets.id
JOIN public.tx AS source_tx
  ON source_tx.id = tx_in.tx_out_id
JOIN public.tx_out AS source_out
  ON source_out.tx_id = tx_in.tx_out_id
 AND source_out.index = tx_in.tx_out_index
LEFT JOIN public.stake_address sa
  ON sa.id = source_out.stake_address_id
ORDER BY targets.id, source_out.id;

-- ============================================================================
-- Query 5: Single-transaction template
-- Replace the hash literal and rerun for a new suspect transaction.
-- ============================================================================
WITH target AS (
  SELECT tx.id, tx.hash, block.epoch_no, block.slot_no, block.time
  FROM public.tx
  JOIN public.block
    ON block.id = tx.block_id
  WHERE tx.hash = decode('571f776c0698c576ddecae145f97e7f284b82ebea70fbc924fa4e2a4a6258020', 'hex')
)
SELECT
  encode(target.hash, 'hex') AS tx_hash,
  target.epoch_no,
  target.slot_no,
  target.time AS block_time_utc,
  source_out.id AS source_tx_out_id,
  encode(source_tx.hash, 'hex') AS source_tx_hash,
  source_out.index AS source_index,
  source_out.value AS input_lovelace,
  tx_out.id AS dest_tx_out_id,
  tx_out.index AS dest_index,
  tx_out.value AS output_lovelace
FROM target
JOIN public.tx_in
  ON tx_in.tx_in_id = target.id
JOIN public.tx AS source_tx
  ON source_tx.id = tx_in.tx_out_id
JOIN public.tx_out AS source_out
  ON source_out.tx_id = tx_in.tx_out_id
 AND source_out.index = tx_in.tx_out_index
JOIN public.tx_out
  ON tx_out.tx_id = target.id
ORDER BY source_out.id, tx_out.index;

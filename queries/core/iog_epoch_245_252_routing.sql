-- IOG Genesis Allocation: Output Generation & Routing (Epochs 245-252)
--
-- Reproducibility note:
-- This file reconstructs the db-sync query workflow used to derive the observation
-- tables in observations/iog_epoch_245_252_output_routing.md from a depth-15 IOG trace.
-- It is intended to be run against a Cardano db-sync PostgreSQL database together
-- with the traced IOG lineage dataset already loaded or materialized locally.
--
-- Expected upstream input:
--   A depth-15 IOG descendant/output set containing at minimum:
--     root_entity, hop_no, tx_hash, tx_out_id, address, stake_address_view, lovelace, epoch_no
--
-- Replace `iog_depth15_outputs` below with the local relation/view used in your environment.

-- ============================================================================
-- Query 1: UTxO generation timeline for outputs under 50,000 ADA
-- ============================================================================
WITH iog_small_outputs AS (
  SELECT
    o.tx_out_id,
    o.tx_hash,
    o.address,
    o.stake_address_view,
    o.lovelace,
    o.epoch_no,
    b.time AS block_time
  FROM iog_depth15_outputs o
  JOIN public.tx t
    ON encode(t.hash, 'hex') = lower(o.tx_hash)
  JOIN public.block b
    ON b.id = t.block_id
  WHERE o.root_entity = 'IOG'
    AND o.hop_no <= 15
    AND o.lovelace < 50000000000
)
SELECT
  epoch_no,
  MIN(block_time) AS earliest_output,
  MAX(block_time) AS latest_output,
  COUNT(*) AS utxos_created
FROM iog_small_outputs
GROUP BY epoch_no
HAVING epoch_no BETWEEN 244 AND 252
ORDER BY epoch_no;

-- ============================================================================
-- Query 2: Delegation routing for the generated sub-50k wallets
-- ============================================================================
WITH iog_small_outputs AS (
  SELECT DISTINCT
    o.tx_out_id,
    o.tx_hash,
    o.address,
    o.stake_address_view,
    o.lovelace,
    o.epoch_no,
    b.time AS block_time
  FROM iog_depth15_outputs o
  JOIN public.tx t
    ON encode(t.hash, 'hex') = lower(o.tx_hash)
  JOIN public.block b
    ON b.id = t.block_id
  WHERE o.root_entity = 'IOG'
    AND o.hop_no <= 15
    AND o.lovelace < 50000000000
    AND o.stake_address_view IS NOT NULL
),
latest_pool_hash AS (
  SELECT DISTINCT ON (ph.id)
    ph.id,
    ph.view AS pool_id
  FROM public.pool_hash ph
  ORDER BY ph.id
),
delegation_events AS (
  SELECT
    d.addr_id,
    sa.view AS stake_address_view,
    d.active_epoch_no AS epoch_no,
    b.time AS delegation_time,
    lph.pool_id
  FROM public.delegation d
  JOIN public.tx t
    ON t.id = d.tx_id
  JOIN public.block b
    ON b.id = t.block_id
  JOIN public.stake_address sa
    ON sa.id = d.addr_id
  JOIN latest_pool_hash lph
    ON lph.id = d.pool_hash_id
),
matched_delegations AS (
  SELECT
    de.epoch_no,
    de.delegation_time,
    de.pool_id,
    de.stake_address_view
  FROM delegation_events de
  JOIN iog_small_outputs iso
    ON iso.stake_address_view = de.stake_address_view
  WHERE de.epoch_no BETWEEN 245 AND 252
)
SELECT
  epoch_no,
  MIN(delegation_time) AS earliest_delegation,
  MAX(delegation_time) AS latest_delegation,
  pool_id,
  COUNT(DISTINCT stake_address_view) AS wallets_delegated
FROM matched_delegations
GROUP BY epoch_no, pool_id
ORDER BY wallets_delegated DESC, epoch_no, pool_id;

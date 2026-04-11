-- Full dossier for stake1uxztgcgh49sld46q94xtjy7zf8j2tnntd6rswl9dypa9ffqqxrz2a
-- The confirmed merge orchestrator: collects from bridge, executes both three-way merges
-- Run with: psql -h ${DB_HOST} -p 5432 -U codex_audit -d cexplorer_replica \
--   --no-psqlrc -A -F',' --pset=footer=off -f queries/stake1uxztgcgh_dossier.sql

\echo '=== A. All delegations for stake1uxztgcgh ==='
SELECT
  b.epoch_no,
  encode(ph.hash_raw,'hex') AS pool_id_hex,
  opd.ticker_name,
  opd.json->>'name' AS pool_name,
  encode(tx.hash,'hex') AS delegation_tx,
  b.time AS block_time
FROM public.stake_address sa
JOIN public.delegation de ON de.addr_id = sa.id
JOIN public.pool_hash ph ON ph.id = de.pool_hash_id
JOIN public.tx ON tx.id = de.tx_id
JOIN public.block b ON b.id = tx.block_id
LEFT JOIN public.off_chain_pool_data opd ON opd.pool_id = ph.id
WHERE sa.view = 'stake1uxztgcgh49sld46q94xtjy7zf8j2tnntd6rswl9dypa9ffqqxrz2a'
ORDER BY b.epoch_no;

\echo '=== B. Current unspent UTxOs for stake1uxztgcgh ==='
SELECT
  out.id AS tx_out_id,
  encode(tx.hash,'hex') AS created_in_tx,
  b.epoch_no AS created_epoch,
  ROUND(out.value::numeric/1000000,6) AS ada,
  out.address
FROM public.stake_address sa
JOIN public.tx_out out ON out.stake_address_id = sa.id
JOIN public.tx ON tx.id = out.tx_id
JOIN public.block b ON b.id = tx.block_id
WHERE sa.view = 'stake1uxztgcgh49sld46q94xtjy7zf8j2tnntd6rswl9dypa9ffqqxrz2a'
  AND NOT EXISTS (
    SELECT 1 FROM public.tx_in ti
    WHERE ti.tx_out_id = out.tx_id AND ti.tx_out_index = out.index
  )
ORDER BY out.value DESC;

\echo '=== C. All transactions involving stake1uxztgcgh (received large amounts) ==='
SELECT
  'RECEIVED' AS direction,
  encode(tx.hash,'hex') AS tx_hash,
  b.epoch_no,
  b.time::text AS block_time,
  out.id AS tx_out_id,
  ROUND(out.value::numeric/1000000,3) AS ada
FROM public.stake_address sa
JOIN public.tx_out out ON out.stake_address_id = sa.id
JOIN public.tx ON tx.id = out.tx_id
JOIN public.block b ON b.id = tx.block_id
WHERE sa.view = 'stake1uxztgcgh49sld46q94xtjy7zf8j2tnntd6rswl9dypa9ffqqxrz2a'
  AND out.value > 1000000000000  -- > 1M ADA
ORDER BY out.value DESC
LIMIT 50;

\echo '=== D. Total ADA received and current balance ==='
SELECT
  COUNT(*) AS total_utxos_ever,
  ROUND(SUM(out.value)::numeric/1000000,3) AS total_ada_ever_received,
  COUNT(CASE WHEN NOT EXISTS (SELECT 1 FROM public.tx_in ti WHERE ti.tx_out_id=out.tx_id AND ti.tx_out_index=out.index) THEN 1 END) AS current_utxo_count,
  ROUND(SUM(CASE WHEN NOT EXISTS (SELECT 1 FROM public.tx_in ti WHERE ti.tx_out_id=out.tx_id AND ti.tx_out_index=out.index) THEN out.value ELSE 0 END)::numeric/1000000,3) AS current_balance_ada
FROM public.stake_address sa
JOIN public.tx_out out ON out.stake_address_id = sa.id
WHERE sa.view = 'stake1uxztgcgh49sld46q94xtjy7zf8j2tnntd6rswl9dypa9ffqqxrz2a';

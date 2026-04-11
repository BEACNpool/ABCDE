-- Debug: inspect spending transactions for hop0 to understand the full flow
-- Check all INPUTS and OUTPUTS of the first spend tx: d644836e...

\echo '=== Inputs to d644836e (hop0 first spend tx, epoch 263) ==='
SELECT
  txi.tx_out_index,
  encode(src_tx.hash, 'hex') AS source_tx,
  src_txo.index AS source_output_idx,
  src_txo.value / 1000000.0 AS input_ada,
  src_txo.address AS source_address,
  sa.view AS source_stake
FROM tx spend_tx
JOIN tx_in txi ON txi.tx_in_id = spend_tx.id
JOIN tx_out src_txo ON src_txo.id = txi.tx_out_id
JOIN tx src_tx ON src_tx.id = src_txo.tx_id
LEFT JOIN stake_address sa ON sa.id = src_txo.stake_address_id
WHERE encode(spend_tx.hash, 'hex') = 'd644836e0577ca50f98671019123cf82a96018063326686299d9bedc6a1689cd'
ORDER BY txi.tx_out_index;

\echo ''
\echo '=== Outputs of d644836e (hop0 first spend tx) ==='
SELECT
  txo.index,
  txo.value / 1000000.0 AS output_ada,
  txo.address,
  sa.view AS stake_addr
FROM tx spend_tx
JOIN tx_out txo ON txo.tx_id = spend_tx.id
LEFT JOIN stake_address sa ON sa.id = txo.stake_address_id
WHERE encode(spend_tx.hash, 'hex') = 'd644836e0577ca50f98671019123cf82a96018063326686299d9bedc6a1689cd'
ORDER BY txo.index;

\echo ''
\echo '=== ALL UTxOs received by hop0 (stake1u84jrq070) — not just 150M ones ==='
SELECT
  txo.id AS tx_out_id,
  encode(tx_in.hash, 'hex') AS created_tx,
  b.epoch_no AS created_epoch,
  txo.index AS output_index,
  txo.value / 1000000.0 AS ada,
  txo.address
FROM stake_address sa
JOIN tx_out txo ON txo.stake_address_id = sa.id
JOIN tx tx_in ON tx_in.id = txo.tx_id
JOIN block b ON b.id = tx_in.block_id
WHERE sa.view = 'stake1u84jrq070qkg09dg8ta3cqaxech4fck953kcwkptzgp3q6cxsu8x6'
ORDER BY b.epoch_no, tx_in.id, txo.index;

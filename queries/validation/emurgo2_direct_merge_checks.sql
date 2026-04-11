-- EMURGO_2 direct-merge checks
--
-- Purpose:
--   Prove that the 781,381,495 ADA line does not act independently at
--   its first downstream hop. Instead, its first spend co-spends with a
--   UTxO derived from the main EMURGO redemption.

-- 1. Anchor dormancy: how long each redemption output sat untouched
WITH anchor(hash_hex, entity) AS (
  VALUES
    ('242608fc18552a4ac83adabcef7155f3b909e83d469ce89735db8f11d3637e38','EMURGO'),
    ('5ec95a53fa3bb7dc56864bb6e75f369f00aa20e8d8cdc3b66b2fb88ec1b225ef','781M')
)
SELECT a.entity,
       encode(anchor_tx.hash,'hex') AS anchor_tx,
       b.time AS redemption_time,
       encode(spender.hash,'hex') AS first_spend_tx,
       sb.time AS first_spend_time,
       ROUND(EXTRACT(EPOCH FROM (sb.time - b.time))/3600.0, 4) AS hours_dormant
FROM anchor a
JOIN tx anchor_tx ON anchor_tx.hash = decode(a.hash_hex,'hex')
JOIN block b ON b.id = anchor_tx.block_id
JOIN tx_in ti ON ti.tx_out_id = anchor_tx.id AND ti.tx_out_index = 0
JOIN tx spender ON spender.id = ti.tx_in_id
JOIN block sb ON sb.id = spender.block_id
ORDER BY redemption_time;

-- 2. Transaction metadata for the merge sequence
WITH target(hash_hex,label) AS (
  VALUES
    ('242608fc18552a4ac83adabcef7155f3b909e83d469ce89735db8f11d3637e38','EMURGO redemption'),
    ('5ec95a53fa3bb7dc56864bb6e75f369f00aa20e8d8cdc3b66b2fb88ec1b225ef','781M redemption'),
    ('7eb47f8f9ffaaf98f30d8028c7e1d13a8efeebffb65d1f2d4be37ee523ceb9bf','EMURGO hop1'),
    ('743fd0510c4527b4031504b9f3c1703606bfd5e63bed4d1bf857ceeefc4bac1b','EMURGO hop2 split'),
    ('c8596b9cd81f734f8129604ff86f23bd4a910465acb84ad9e9d1ac223ccb4a76','781M hop1 direct merge')
)
SELECT target.label,
       encode(tx.hash,'hex') AS tx_hash,
       b.epoch_no,
       b.time,
       tx.size,
       tx.fee / 1000000.0 AS fee_ada,
       (SELECT COUNT(*) FROM tx_in ti WHERE ti.tx_in_id = tx.id) AS input_count,
       (SELECT COUNT(*) FROM tx_out o WHERE o.tx_id = tx.id) AS output_count,
       tx.out_sum / 1000000.0 AS out_sum_ada
FROM target
JOIN tx ON tx.hash = decode(target.hash_hex,'hex')
JOIN block b ON b.id = tx.block_id
ORDER BY b.time;

-- 3. Inputs to the three relevant post-redemption transactions
WITH txs(hash_hex,label) AS (
  VALUES
    ('7eb47f8f9ffaaf98f30d8028c7e1d13a8efeebffb65d1f2d4be37ee523ceb9bf','EMURGO hop1'),
    ('743fd0510c4527b4031504b9f3c1703606bfd5e63bed4d1bf857ceeefc4bac1b','EMURGO hop2 split'),
    ('c8596b9cd81f734f8129604ff86f23bd4a910465acb84ad9e9d1ac223ccb4a76','781M hop1 direct merge')
)
SELECT t.label,
       i.id AS tx_in_row_id,
       encode(src_tx.hash,'hex') AS src_tx_hash,
       src_out.id AS src_tx_out_id,
       src_out.value / 1000000.0 AS src_ada,
       src_out.address AS src_addr
FROM txs t
JOIN tx cur ON cur.hash = decode(t.hash_hex,'hex')
JOIN tx_in i ON i.tx_in_id = cur.id
JOIN tx_out src_out ON src_out.tx_id = i.tx_out_id AND src_out.index = i.tx_out_index
JOIN tx src_tx ON src_tx.id = src_out.tx_id
ORDER BY cur.id, i.id;

-- 4. Outputs from the same sequence
WITH txs(hash_hex,label) AS (
  VALUES
    ('7eb47f8f9ffaaf98f30d8028c7e1d13a8efeebffb65d1f2d4be37ee523ceb9bf','EMURGO hop1'),
    ('743fd0510c4527b4031504b9f3c1703606bfd5e63bed4d1bf857ceeefc4bac1b','EMURGO hop2 split'),
    ('c8596b9cd81f734f8129604ff86f23bd4a910465acb84ad9e9d1ac223ccb4a76','781M hop1 direct merge')
)
SELECT t.label,
       o.index AS output_idx,
       o.id AS tx_out_id,
       o.value / 1000000.0 AS out_ada,
       o.address AS out_addr
FROM txs t
JOIN tx cur ON cur.hash = decode(t.hash_hex,'hex')
JOIN tx_out o ON o.tx_id = cur.id
ORDER BY cur.id, o.index;

-- ============================================================
-- EMURGO_2 classification checks
-- Purpose:
--   Determine whether the 781,381,495 ADA source consumed by
--   redemption tx 5ec95a53... behaves like a sale-ticket entry
--   or a named founder/TBDP allocation.
--
-- Run as:
--   psql -h 192.168.86.118 -p 5432 -U codex_audit -d cexplorer_replica \
--     -f queries/emurgo2_classification_checks.sql
-- ============================================================

-- ------------------------------------------------------------
-- 1. Source genesis outputs consumed by the four known
--    founder-related redemption transactions
-- ------------------------------------------------------------
WITH targets(hash_hex) AS (
    VALUES
      ('fa2d2a70c0b5fd45cb6c3989f02813061f9d27f15f30ecddd38780c59f413c62'),
      ('208c7d54c1c24059c9314ddbe866edc80adcb8894539b27b6a1430d5c078b998'),
      ('242608fc18552a4ac83adabcef7155f3b909e83d469ce89735db8f11d3637e38'),
      ('5ec95a53fa3bb7dc56864bb6e75f369f00aa20e8d8cdc3b66b2fb88ec1b225ef')
)
SELECT
    t.hash_hex AS tx_hash,
    src.id AS source_tx_out_id,
    src.value / 1000000.0 AS source_ada,
    src.address AS source_address,
    out1.address AS redeemed_to,
    out1.value / 1000000.0 AS redeemed_ada,
    b.time
FROM targets t
JOIN tx tx1
  ON tx1.hash = decode(t.hash_hex, 'hex')
JOIN block b
  ON b.id = tx1.block_id
JOIN tx_in i
  ON i.tx_in_id = tx1.id
JOIN tx_out src
  ON src.tx_id = i.tx_out_id
 AND src.index = i.tx_out_index
JOIN tx_out out1
  ON out1.tx_id = tx1.id
 AND out1.index = 0
ORDER BY b.time;


-- ------------------------------------------------------------
-- 2. Quick amount-presence check inside genesis-relevant rows
--    referenced by those redemptions
-- ------------------------------------------------------------
WITH targets(hash_hex) AS (
    VALUES
      ('fa2d2a70c0b5fd45cb6c3989f02813061f9d27f15f30ecddd38780c59f413c62'),
      ('208c7d54c1c24059c9314ddbe866edc80adcb8894539b27b6a1430d5c078b998'),
      ('242608fc18552a4ac83adabcef7155f3b909e83d469ce89735db8f11d3637e38'),
      ('5ec95a53fa3bb7dc56864bb6e75f369f00aa20e8d8cdc3b66b2fb88ec1b225ef')
),
srcs AS (
    SELECT src.value / 1000000.0 AS source_ada
    FROM targets t
    JOIN tx tx1
      ON tx1.hash = decode(t.hash_hex, 'hex')
    JOIN tx_in i
      ON i.tx_in_id = tx1.id
    JOIN tx_out src
      ON src.tx_id = i.tx_out_id
     AND src.index = i.tx_out_index
)
SELECT
    COUNT(*) AS source_rows,
    SUM(CASE WHEN source_ada = 781381495  THEN 1 ELSE 0 END) AS cnt_781381495,
    SUM(CASE WHEN source_ada = 2074165643 THEN 1 ELSE 0 END) AS cnt_2074165643,
    SUM(CASE WHEN source_ada = 2463071701 THEN 1 ELSE 0 END) AS cnt_2463071701,
    SUM(CASE WHEN source_ada = 648176763  THEN 1 ELSE 0 END) AS cnt_648176763
FROM srcs;


-- ------------------------------------------------------------
-- 3. Timing check: founder redemptions inside first 24h window
-- ------------------------------------------------------------
SELECT
    encode(tx.hash, 'hex') AS tx_hash,
    b.time,
    tx.id
FROM tx
JOIN block b
  ON b.id = tx.block_id
WHERE tx.hash IN (
    decode('fa2d2a70c0b5fd45cb6c3989f02813061f9d27f15f30ecddd38780c59f413c62', 'hex'),
    decode('208c7d54c1c24059c9314ddbe866edc80adcb8894539b27b6a1430d5c078b998', 'hex'),
    decode('242608fc18552a4ac83adabcef7155f3b909e83d469ce89735db8f11d3637e38', 'hex'),
    decode('5ec95a53fa3bb7dc56864bb6e75f369f00aa20e8d8cdc3b66b2fb88ec1b225ef', 'hex')
)
ORDER BY b.time;

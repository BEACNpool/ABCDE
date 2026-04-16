-- MIR boundary-exit trace template
-- Purpose: materialize large exits from a seed stake cluster, then classify them as
--   - fresh stake destinations
--   - enterprise destinations
--   - labeled / manually reviewed destinations downstream
--
-- Replace the seed values and threshold below as needed.

-- 1) seed cluster
DROP TABLE IF EXISTS tmp_mir_seed_stakes;
CREATE TEMP TABLE tmp_mir_seed_stakes(view text primary key) ON COMMIT DROP;
INSERT INTO tmp_mir_seed_stakes(view) VALUES
  ('stake1u80y77jjfcdymt38amg3na9w4p4d89ffw66xqsspdwsa2sqt8epdn'),
  ('stake1u8kgcfdpefrnf5570v47manyyg85jshlrg4p2hrsx3wdspccdda8v'),
  ('stake1uy86sf5xrzcpg2ncddkzz6z2ca2m59qsnu4qxar08g9rvkgwkpjjv'),
  ('stake1uykws5pmwjxktdhlkz0pac3cu2guw6fjys2zaanmdew6xrs5lgv4n'),
  ('stake1u887jrylddch0vh4d2kx72h2ax8t7aeq49zvmry4g9wcj4g3gty8j'),
  ('stake1u9mymn640v59n3mwyfdsg5t6yu34ut9ufvynavsn0ey40ugqdj6lh');

-- 2) threshold, default = 49,000 ADA
DROP TABLE IF EXISTS tmp_mir_threshold;
CREATE TEMP TABLE tmp_mir_threshold(min_lovelace bigint) ON COMMIT DROP;
INSERT INTO tmp_mir_threshold VALUES (49000000000);

-- 3) seed-controlled historical UTxOs
DROP TABLE IF EXISTS tmp_mir_seed_utxos;
CREATE TEMP TABLE tmp_mir_seed_utxos AS
SELECT DISTINCT
  txo.tx_id,
  txo.index AS tx_index,
  txo.address,
  txo.value,
  sa.view AS stake_address
FROM tx_out txo
JOIN stake_address sa ON sa.id = txo.stake_address_id
JOIN tmp_mir_seed_stakes s ON s.view = sa.view;

CREATE INDEX ON tmp_mir_seed_utxos (tx_id, tx_index);

-- 4) spending transactions for those UTxOs
DROP TABLE IF EXISTS tmp_mir_spend_txs;
CREATE TEMP TABLE tmp_mir_spend_txs AS
SELECT DISTINCT
  ti.tx_out_id AS spend_tx_id,
  COUNT(*) OVER (PARTITION BY ti.tx_out_id) AS frontier_input_count,
  SUM(su.value) OVER (PARTITION BY ti.tx_out_id) AS frontier_input_lovelace
FROM tmp_mir_seed_utxos su
JOIN tx_in ti
  ON ti.tx_in_id = su.tx_id
 AND ti.tx_out_index = su.tx_index;

CREATE INDEX ON tmp_mir_spend_txs (spend_tx_id);

-- 5) raw boundary exits
DROP TABLE IF EXISTS tmp_mir_boundary_exits;
CREATE TEMP TABLE tmp_mir_boundary_exits AS
SELECT
  st.spend_tx_id,
  encode(t.hash, 'hex') AS spend_tx_hash,
  b.epoch_no,
  b.time AS block_time,
  st.frontier_input_count,
  st.frontier_input_lovelace,
  txo.index AS dest_index,
  txo.address AS dest_address,
  txo.value AS dest_lovelace,
  sa.view AS dest_stake_address,
  CASE
    WHEN sa.view IN (SELECT view FROM tmp_mir_seed_stakes) THEN 'internal_stake'
    WHEN sa.view IS NOT NULL THEN 'external_stake'
    ELSE 'enterprise'
  END AS dest_type
FROM tmp_mir_spend_txs st
JOIN tx t ON t.id = st.spend_tx_id
JOIN block b ON b.id = t.block_id
JOIN tx_out txo ON txo.tx_id = st.spend_tx_id
LEFT JOIN stake_address sa ON sa.id = txo.stake_address_id
WHERE txo.value >= (SELECT min_lovelace FROM tmp_mir_threshold)
  AND (
    sa.view IS NULL
    OR sa.view NOT IN (SELECT view FROM tmp_mir_seed_stakes)
  );

CREATE INDEX ON tmp_mir_boundary_exits (dest_type);
CREATE INDEX ON tmp_mir_boundary_exits (dest_lovelace DESC);
CREATE INDEX ON tmp_mir_boundary_exits (dest_stake_address);
CREATE INDEX ON tmp_mir_boundary_exits (dest_address);

-- 6) current pool + DRep for traced stake exits
WITH latest_pool AS (
  SELECT DISTINCT ON (d.addr_id)
    d.addr_id,
    d.pool_hash_id,
    d.active_epoch_no,
    d.slot_no,
    d.tx_id,
    d.cert_index
  FROM delegation d
  JOIN stake_address sa ON sa.id = d.addr_id
  WHERE sa.view IN (
    SELECT DISTINCT dest_stake_address
    FROM tmp_mir_boundary_exits
    WHERE dest_stake_address IS NOT NULL
  )
  ORDER BY d.addr_id, d.active_epoch_no DESC, d.slot_no DESC, d.tx_id DESC, d.cert_index DESC
),
latest_vote AS (
  SELECT DISTINCT ON (dv.addr_id)
    dv.addr_id,
    dv.drep_hash_id,
    tx.block_id,
    dv.tx_id,
    dv.cert_index
  FROM delegation_vote dv
  JOIN tx ON tx.id = dv.tx_id
  JOIN stake_address sa ON sa.id = dv.addr_id
  WHERE sa.view IN (
    SELECT DISTINCT dest_stake_address
    FROM tmp_mir_boundary_exits
    WHERE dest_stake_address IS NOT NULL
  )
  ORDER BY dv.addr_id, tx.block_id DESC, dv.tx_id DESC, dv.cert_index DESC
)
SELECT
  e.spend_tx_hash,
  e.epoch_no,
  e.block_time,
  e.dest_type,
  e.dest_address,
  e.dest_stake_address,
  e.dest_lovelace / 1000000.0 AS dest_ada,
  ph.view AS current_pool,
  dh.view AS current_drep
FROM tmp_mir_boundary_exits e
LEFT JOIN stake_address sa ON sa.view = e.dest_stake_address
LEFT JOIN latest_pool lp ON lp.addr_id = sa.id
LEFT JOIN pool_hash ph ON ph.id = lp.pool_hash_id
LEFT JOIN latest_vote lv ON lv.addr_id = sa.id
LEFT JOIN drep_hash dh ON dh.id = lv.drep_hash_id
ORDER BY e.dest_lovelace DESC, e.spend_tx_hash, e.dest_index;

-- Note:
-- This first-pass template intentionally stops at boundary exits.
-- To go deeper, take the external stake destinations and enterprise addresses above threshold,
-- promote them to the next frontier, and repeat. That is the correct anti-obfuscation move.

-- Aggregate destination analysis: where did the 8x150M recipients actually send their 150M?
-- No output-size filter — group all outputs by destination stake/address

\echo '=== Aggregate destinations from ALL spend transactions of 150M UTxOs ==='

WITH recipients AS (
  SELECT v.label, sa.id AS stake_address_id, sa.view AS stake_addr
  FROM stake_address sa
  JOIN (VALUES
    ('150M_hop0', 'stake1u84jrq070qkg09dg8ta3cqaxech4fck953kcwkptzgp3q6cxsu8x6'),
    ('150M_hop2', 'stake1ux0xnj5ljjx734qph69jc8a2mdemgguy5640pednyw7p08c6mjwk6'),
    ('150M_hop3', 'stake1uxz3a23cmjcmautfyel85f56dmw8skznsz0d228km6udsvgra8065'),
    ('150M_hop4', 'stake1uxtj8luzpucf5jp5df0za7klmc9eh0rg2t08zwysa58jtwslp7dqz'),
    ('150M_hop5', 'stake1uytfgj3wquuyz68r3cvx0z75mtnc4wj0cdxe2sgn70za8dqwsfwfr'),
    ('150M_hop6', 'stake1u8mf4hrhd9mtp86zkazlyg4w2zvzeavpa457lyq2vfn55lgwzk6t2'),
    ('150M_hop7', 'stake1uxdpsgk3xpgvh0mj4sch29veh3al8xut2s0al0zy5exgh5ctds492'),
    ('150M_hop8', 'stake1uxl72wy87wxcp8deu0j2kusmspywuz0gnsjf0dxzf6rv9xcwlhxm7')
  ) AS v(label, stake_view) ON sa.view = v.stake_view
),
-- Find all spend transactions for 150M UTxOs
spend_txids AS (
  SELECT DISTINCT
    r.label,
    txi.tx_in_id AS spend_tx_id
  FROM recipients r
  JOIN tx_out txo ON txo.stake_address_id = r.stake_address_id
  JOIN tx_in txi ON txi.tx_out_id = txo.id
  WHERE txo.value > 1000000000000  -- 1M ADA, filtering to only the 150M UTxOs
),
-- Get all outputs of those spending transactions
all_outputs AS (
  SELECT
    st.label,
    encode(tx_spend.hash, 'hex') AS spend_tx_hash,
    b_spend.epoch_no AS spend_epoch,
    txo_out.address AS output_address,
    sa_out.view AS output_stake_addr,
    txo_out.value / 1000000.0 AS output_ada
  FROM spend_txids st
  JOIN tx tx_spend ON tx_spend.id = st.spend_tx_id
  JOIN block b_spend ON b_spend.id = tx_spend.block_id
  JOIN tx_out txo_out ON txo_out.tx_id = st.spend_tx_id
  LEFT JOIN stake_address sa_out ON sa_out.id = txo_out.stake_address_id
)
SELECT
  COALESCE(output_stake_addr, output_address) AS destination,
  CASE WHEN output_stake_addr IS NULL THEN 'byron/script' ELSE 'shelley' END AS addr_type,
  COUNT(DISTINCT label) AS hops_count,
  string_agg(DISTINCT label, ', ' ORDER BY label) AS from_hops,
  COUNT(*) AS output_count,
  round(SUM(output_ada)) AS total_ada
FROM all_outputs
GROUP BY COALESCE(output_stake_addr, output_address), CASE WHEN output_stake_addr IS NULL THEN 'byron/script' ELSE 'shelley' END
ORDER BY total_ada DESC
LIMIT 30;

\echo ''
\echo '=== Hub 1 (Ae2tdPwUPEZ6xYrxCgRDM2NQFM5oajHEoJN3i9ZVV2AbsbvxoJBjVu3yP7W) transactions detail ==='

WITH recipients AS (
  SELECT v.label, sa.id AS stake_address_id
  FROM stake_address sa
  JOIN (VALUES
    ('150M_hop0', 'stake1u84jrq070qkg09dg8ta3cqaxech4fck953kcwkptzgp3q6cxsu8x6'),
    ('150M_hop2', 'stake1ux0xnj5ljjx734qph69jc8a2mdemgguy5640pednyw7p08c6mjwk6'),
    ('150M_hop3', 'stake1uxz3a23cmjcmautfyel85f56dmw8skznsz0d228km6udsvgra8065'),
    ('150M_hop4', 'stake1uxtj8luzpucf5jp5df0za7klmc9eh0rg2t08zwysa58jtwslp7dqz'),
    ('150M_hop5', 'stake1uytfgj3wquuyz68r3cvx0z75mtnc4wj0cdxe2sgn70za8dqwsfwfr'),
    ('150M_hop6', 'stake1u8mf4hrhd9mtp86zkazlyg4w2zvzeavpa457lyq2vfn55lgwzk6t2'),
    ('150M_hop7', 'stake1uxdpsgk3xpgvh0mj4sch29veh3al8xut2s0al0zy5exgh5ctds492'),
    ('150M_hop8', 'stake1uxl72wy87wxcp8deu0j2kusmspywuz0gnsjf0dxzf6rv9xcwlhxm7')
  ) AS v(label, stake_view) ON sa.view = v.stake_view
),
spend_txids AS (
  SELECT DISTINCT r.label, txi.tx_in_id AS spend_tx_id
  FROM recipients r
  JOIN tx_out txo ON txo.stake_address_id = r.stake_address_id
  JOIN tx_in txi ON txi.tx_out_id = txo.id
  WHERE txo.value > 1000000000000
)
SELECT
  st.label,
  encode(tx_spend.hash, 'hex') AS spend_tx_hash,
  b_spend.epoch_no AS spend_epoch,
  to_char(b_spend.time, 'YYYY-MM-DD HH24:MI') AS block_time,
  txo_out.value / 1000000.0 AS hub1_ada_received
FROM spend_txids st
JOIN tx tx_spend ON tx_spend.id = st.spend_tx_id
JOIN block b_spend ON b_spend.id = tx_spend.block_id
JOIN tx_out txo_out ON txo_out.tx_id = st.spend_tx_id
WHERE txo_out.address = 'Ae2tdPwUPEZ6xYrxCgRDM2NQFM5oajHEoJN3i9ZVV2AbsbvxoJBjVu3yP7W'
ORDER BY st.label, b_spend.epoch_no;

\echo ''
\echo '=== Grand total: how much of each 150M hop went to Hub 1 vs other destinations ==='

WITH recipients AS (
  SELECT v.label, sa.id AS stake_address_id
  FROM stake_address sa
  JOIN (VALUES
    ('150M_hop0', 'stake1u84jrq070qkg09dg8ta3cqaxech4fck953kcwkptzgp3q6cxsu8x6'),
    ('150M_hop2', 'stake1ux0xnj5ljjx734qph69jc8a2mdemgguy5640pednyw7p08c6mjwk6'),
    ('150M_hop3', 'stake1uxz3a23cmjcmautfyel85f56dmw8skznsz0d228km6udsvgra8065'),
    ('150M_hop4', 'stake1uxtj8luzpucf5jp5df0za7klmc9eh0rg2t08zwysa58jtwslp7dqz'),
    ('150M_hop5', 'stake1uytfgj3wquuyz68r3cvx0z75mtnc4wj0cdxe2sgn70za8dqwsfwfr'),
    ('150M_hop6', 'stake1u8mf4hrhd9mtp86zkazlyg4w2zvzeavpa457lyq2vfn55lgwzk6t2'),
    ('150M_hop7', 'stake1uxdpsgk3xpgvh0mj4sch29veh3al8xut2s0al0zy5exgh5ctds492'),
    ('150M_hop8', 'stake1uxl72wy87wxcp8deu0j2kusmspywuz0gnsjf0dxzf6rv9xcwlhxm7')
  ) AS v(label, stake_view) ON sa.view = v.stake_view
),
spend_txids AS (
  SELECT DISTINCT r.label, txi.tx_in_id AS spend_tx_id,
    txo.value / 1000000.0 AS original_utxo_ada
  FROM recipients r
  JOIN tx_out txo ON txo.stake_address_id = r.stake_address_id
  JOIN tx_in txi ON txi.tx_out_id = txo.id
  WHERE txo.value > 1000000000000
),
outputs_tagged AS (
  SELECT
    st.label,
    txo_out.value / 1000000.0 AS output_ada,
    CASE WHEN txo_out.address = 'Ae2tdPwUPEZ6xYrxCgRDM2NQFM5oajHEoJN3i9ZVV2AbsbvxoJBjVu3yP7W'
         THEN 'hub1_binance' ELSE 'other' END AS dest_type
  FROM spend_txids st
  JOIN tx_out txo_out ON txo_out.tx_id = st.spend_tx_id
)
SELECT
  label,
  round(SUM(CASE WHEN dest_type = 'hub1_binance' THEN output_ada ELSE 0 END)) AS ada_to_hub1,
  round(SUM(CASE WHEN dest_type = 'other' THEN output_ada ELSE 0 END)) AS ada_to_other,
  round(SUM(output_ada)) AS total_output_ada,
  round(SUM(CASE WHEN dest_type = 'hub1_binance' THEN output_ada ELSE 0 END) /
        NULLIF(SUM(output_ada), 0) * 100, 1) AS hub1_pct
FROM outputs_tagged
GROUP BY label
ORDER BY label;

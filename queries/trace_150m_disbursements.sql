-- Trace where the 8x150M disbursement recipients sent their funds
-- Each recipient received ~150M ADA from f907b625 (epoch 226) and now has ~2 ADA remaining

\echo '=== Step 1: Find all UTxOs received by 8x150M recipients, annotated with spend tx ==='

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
utxos_received AS (
  SELECT
    r.label,
    r.stake_addr,
    txo.id AS tx_out_id,
    txo.value / 1000000.0 AS ada_received,
    b_in.epoch_no AS created_epoch,
    encode(tx_in.hash, 'hex') AS created_tx,
    -- Find the spending tx
    txi.tx_in_id AS spend_tx_id,
    encode(tx_spend.hash, 'hex') AS spend_tx_hash,
    b_spend.epoch_no AS spend_epoch,
    to_char(b_spend.time, 'YYYY-MM-DD HH24:MI:SS') AS spend_block_time
  FROM recipients r
  JOIN tx_out txo ON txo.stake_address_id = r.stake_address_id
  JOIN tx tx_in ON tx_in.id = txo.tx_id
  JOIN block b_in ON b_in.id = tx_in.block_id
  LEFT JOIN tx_in txi ON txi.tx_out_id = txo.id
  LEFT JOIN tx tx_spend ON tx_spend.id = txi.tx_in_id
  LEFT JOIN block b_spend ON b_spend.id = tx_spend.block_id
  WHERE txo.value > 1000000000000  -- only UTxOs > 1M ADA (i.e. the 150M ones)
)
SELECT
  label,
  stake_addr,
  created_tx,
  created_epoch,
  round(ada_received) AS ada_received,
  spend_tx_hash,
  spend_epoch,
  spend_block_time
FROM utxos_received
ORDER BY label, created_epoch;

\echo ''
\echo '=== Step 2: Outputs of the spending transactions (where did the 150M go?) ==='

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
large_utxos AS (
  SELECT
    r.label,
    r.stake_address_id,
    txo.id AS tx_out_id,
    txi.tx_in_id AS spend_tx_id
  FROM recipients r
  JOIN tx_out txo ON txo.stake_address_id = r.stake_address_id
  LEFT JOIN tx_in txi ON txi.tx_out_id = txo.id
  WHERE txo.value > 1000000000000
),
spend_outputs AS (
  SELECT
    lu.label,
    encode(tx_spend.hash, 'hex') AS spend_tx_hash,
    b_spend.epoch_no AS spend_epoch,
    txo_out.index AS output_index,
    txo_out.value / 1000000.0 AS output_ada,
    txo_out.address AS output_address,
    sa_out.view AS output_stake_addr
  FROM large_utxos lu
  JOIN tx tx_spend ON tx_spend.id = lu.spend_tx_id
  JOIN block b_spend ON b_spend.id = tx_spend.block_id
  JOIN tx_out txo_out ON txo_out.tx_id = tx_spend.id
  LEFT JOIN stake_address sa_out ON sa_out.id = txo_out.stake_address_id
  WHERE lu.spend_tx_id IS NOT NULL
)
SELECT
  label,
  spend_tx_hash,
  spend_epoch,
  output_index,
  round(output_ada) AS output_ada,
  output_address,
  output_stake_addr
FROM spend_outputs
ORDER BY label, output_ada DESC;

\echo ''
\echo '=== Step 3: Summary — unique destination stake addresses from all 8 spending txs ==='

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
large_utxos AS (
  SELECT
    r.label,
    r.stake_address_id,
    txo.id AS tx_out_id,
    txi.tx_in_id AS spend_tx_id
  FROM recipients r
  JOIN tx_out txo ON txo.stake_address_id = r.stake_address_id
  LEFT JOIN tx_in txi ON txi.tx_out_id = txo.id
  WHERE txo.value > 1000000000000
),
destination_stakes AS (
  SELECT
    sa_out.view AS dest_stake_addr,
    COUNT(DISTINCT lu.label) AS hops_sending_here,
    string_agg(DISTINCT lu.label, ', ' ORDER BY lu.label) AS which_hops,
    round(SUM(txo_out.value) / 1000000.0) AS total_ada_sent
  FROM large_utxos lu
  JOIN tx_out txo_out ON txo_out.tx_id = lu.spend_tx_id
  LEFT JOIN stake_address sa_out ON sa_out.id = txo_out.stake_address_id
  WHERE lu.spend_tx_id IS NOT NULL
    AND txo_out.value > 1000000000000  -- only large outputs
  GROUP BY sa_out.view
  ORDER BY total_ada_sent DESC
)
SELECT
  dest_stake_addr,
  hops_sending_here,
  which_hops,
  total_ada_sent
FROM destination_stakes;

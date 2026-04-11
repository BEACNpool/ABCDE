-- Correct trace using proper db-sync tx_in schema:
-- tx_in.tx_out_id references tx.id (NOT tx_out.id)
-- tx_in.tx_out_index is the output index within that producing tx

\echo '=== First-hop spend of each 150M UTxO (correct db-sync join) ==='

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
-- Find all UTxOs > 100M ADA at each recipient stake address
large_utxos AS (
  SELECT
    r.label,
    r.stake_addr,
    txo.id AS tx_out_id,
    tx_prod.id AS producing_tx_id,
    encode(tx_prod.hash,'hex') AS producing_tx_hash,
    txo.index AS output_index,
    txo.value / 1000000.0 AS ada_received,
    b_prod.epoch_no AS created_epoch
  FROM recipients r
  JOIN tx_out txo ON txo.stake_address_id = r.stake_address_id
  JOIN tx tx_prod ON tx_prod.id = txo.tx_id
  JOIN block b_prod ON b_prod.id = tx_prod.block_id
  WHERE txo.value > 100000000000000  -- > 100M ADA
),
-- Find the FIRST hop: what transaction consumed each 150M UTxO?
-- CORRECT join: tx_in.tx_out_id = producing_tx.id AND tx_in.tx_out_index = output_index
first_spend AS (
  SELECT
    lu.*,
    encode(spend_tx.hash,'hex') AS spend_tx_hash,
    b_spend.epoch_no AS spend_epoch,
    to_char(b_spend.time,'YYYY-MM-DD HH24:MI') AS spend_time,
    (SELECT count(*) FROM tx_out WHERE tx_id = spend_tx.id) AS spend_output_count,
    (SELECT round(sum(value)/1000000.0) FROM tx_out WHERE tx_id = spend_tx.id) AS spend_total_output_ada
  FROM large_utxos lu
  JOIN tx_in txi ON txi.tx_out_id = lu.producing_tx_id AND txi.tx_out_index = lu.output_index
  JOIN tx spend_tx ON spend_tx.id = txi.tx_in_id
  JOIN block b_spend ON b_spend.id = spend_tx.block_id
)
SELECT
  label,
  stake_addr,
  producing_tx_hash AS created_tx,
  created_epoch,
  round(ada_received) AS ada_received,
  spend_tx_hash,
  spend_epoch,
  spend_time,
  spend_output_count,
  spend_total_output_ada
FROM first_spend
ORDER BY label, created_epoch;

\echo ''
\echo '=== Destination addresses in first-hop spends (where did the 150M go first?) ==='

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
  SELECT r.label, txo.id, tx_prod.id AS producing_tx_id, txo.index AS output_index
  FROM recipients r
  JOIN tx_out txo ON txo.stake_address_id = r.stake_address_id
  JOIN tx tx_prod ON tx_prod.id = txo.tx_id
  WHERE txo.value > 100000000000000
),
first_spends AS (
  SELECT DISTINCT lu.label, txi.tx_in_id AS spend_tx_id
  FROM large_utxos lu
  JOIN tx_in txi ON txi.tx_out_id = lu.producing_tx_id AND txi.tx_out_index = lu.output_index
),
spend_outputs AS (
  SELECT
    fs.label,
    encode(spend_tx.hash,'hex') AS spend_tx_hash,
    b.epoch_no,
    txo_out.value / 1000000.0 AS output_ada,
    COALESCE(sa_out.view, txo_out.address) AS destination
  FROM first_spends fs
  JOIN tx spend_tx ON spend_tx.id = fs.spend_tx_id
  JOIN block b ON b.id = spend_tx.block_id
  JOIN tx_out txo_out ON txo_out.tx_id = fs.spend_tx_id
  LEFT JOIN stake_address sa_out ON sa_out.id = txo_out.stake_address_id
  WHERE txo_out.value > 1000000000000  -- outputs > 1M ADA only
)
SELECT
  label,
  spend_tx_hash,
  epoch_no,
  round(output_ada) AS output_ada,
  destination
FROM spend_outputs
ORDER BY label, output_ada DESC;

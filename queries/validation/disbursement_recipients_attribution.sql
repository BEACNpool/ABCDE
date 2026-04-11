-- Attribution queries for the 8 × 150M ADA disbursement recipients from f907b625 (2B CF+EMURGO merge)
-- and the main routing address stake1u9zjr6e37
-- Run with: psql -h ${DB_HOST} -p 5432 -U codex_audit -d cexplorer_replica \
--   --no-psqlrc -A -F',' --pset=footer=off -f queries/disbursement_recipients_attribution.sql

\echo '=== Delegation history for all 8 x 150M recipients ==='
WITH recipients(label, stake_addr) AS (
  VALUES
    ('200M_unspent',     'stake1uxexwrph9r2p3lv42r7ccjptpmml33u2v3xx4p0q9ks85wc2y9t33'),
    ('150M_hop0',        'stake1u84jrq070qkg09dg8ta3cqaxech4fck953kcwkptzgp3q6cxsu8x6'),
    ('150M_hop2',        'stake1ux0xnj5ljjx734qph69jc8a2mdemgguy5640pednyw7p08c6mjwk6'),
    ('150M_hop3',        'stake1uxz3a23cmjcmautfyel85f56dmw8skznsz0d228km6udsvgra8065'),
    ('150M_hop4',        'stake1uxtj8luzpucf5jp5df0za7klmc9eh0rg2t08zwysa58jtwslp7dqz'),
    ('150M_hop5',        'stake1uytfgj3wquuyz68r3cvx0z75mtnc4wj0cdxe2sgn70za8dqwsfwfr'),
    ('150M_hop6',        'stake1u8mf4hrhd9mtp86zkazlyg4w2zvzeavpa457lyq2vfn55lgwzk6t2'),
    ('150M_hop7',        'stake1uxdpsgk3xpgvh0mj4sch29veh3al8xut2s0al0zy5exgh5ctds492'),
    ('150M_hop8',        'stake1uxl72wy87wxcp8deu0j2kusmspywuz0gnsjf0dxzf6rv9xcwlhxm7'),
    ('routing',          'stake1u9zjr6e37w53a474puhx606ayr3rz2l6jljrmzvlzkk3cmg0m2zw0')
)
SELECT
  r.label,
  r.stake_addr,
  b.epoch_no,
  encode(ph.hash_raw,'hex') AS pool_id_hex,
  opd.ticker_name,
  opd.json->>'name' AS pool_name
FROM recipients r
JOIN public.stake_address sa ON sa.view = r.stake_addr
JOIN public.delegation de ON de.addr_id = sa.id
JOIN public.pool_hash ph ON ph.id = de.pool_hash_id
JOIN public.tx ON tx.id = de.tx_id
JOIN public.block b ON b.id = tx.block_id
LEFT JOIN public.off_chain_pool_data opd ON opd.pool_id = ph.id
ORDER BY r.label, b.epoch_no;

\echo '=== Current balances for all recipients ==='
WITH recipients(label, stake_addr) AS (
  VALUES
    ('200M_unspent',     'stake1uxexwrph9r2p3lv42r7ccjptpmml33u2v3xx4p0q9ks85wc2y9t33'),
    ('150M_hop0',        'stake1u84jrq070qkg09dg8ta3cqaxech4fck953kcwkptzgp3q6cxsu8x6'),
    ('150M_hop2',        'stake1ux0xnj5ljjx734qph69jc8a2mdemgguy5640pednyw7p08c6mjwk6'),
    ('150M_hop3',        'stake1uxz3a23cmjcmautfyel85f56dmw8skznsz0d228km6udsvgra8065'),
    ('150M_hop4',        'stake1uxtj8luzpucf5jp5df0za7klmc9eh0rg2t08zwysa58jtwslp7dqz'),
    ('150M_hop5',        'stake1uytfgj3wquuyz68r3cvx0z75mtnc4wj0cdxe2sgn70za8dqwsfwfr'),
    ('150M_hop6',        'stake1u8mf4hrhd9mtp86zkazlyg4w2zvzeavpa457lyq2vfn55lgwzk6t2'),
    ('150M_hop7',        'stake1uxdpsgk3xpgvh0mj4sch29veh3al8xut2s0al0zy5exgh5ctds492'),
    ('150M_hop8',        'stake1uxl72wy87wxcp8deu0j2kusmspywuz0gnsjf0dxzf6rv9xcwlhxm7'),
    ('routing',          'stake1u9zjr6e37w53a474puhx606ayr3rz2l6jljrmzvlzkk3cmg0m2zw0')
)
SELECT
  r.label,
  r.stake_addr,
  COUNT(out.id) AS utxo_count,
  ROUND(SUM(out.value)::numeric/1000000,3) AS current_balance_ada,
  MIN(b.epoch_no) AS first_active_epoch,
  MAX(b.epoch_no) AS last_active_epoch
FROM recipients r
JOIN public.stake_address sa ON sa.view = r.stake_addr
JOIN public.tx_out out ON out.stake_address_id = sa.id
JOIN public.tx ON tx.id = out.tx_id
JOIN public.block b ON b.id = tx.block_id
WHERE NOT EXISTS (
  SELECT 1 FROM public.tx_in ti
  WHERE ti.tx_out_id = out.tx_id AND ti.tx_out_index = out.index
)
GROUP BY r.label, r.stake_addr
ORDER BY current_balance_ada DESC NULLS LAST;

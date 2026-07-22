\timing on
\set ON_ERROR_STOP on

-- Wanchain Cardano <-> BNB NIGHT bridge incident, 2026-07-20.
-- Read-only apart from session-local TEMP tables. Run against cexplorer_replica.
-- Snapshot/report companion: reports/night_wanchain_incident_2026_07_20.md

SET statement_timeout = '180s';

\set night_ident 11020047
\set bridge_address 'addr1xyw0kswupwx38ljnvq8pwpvae0x69krywdr7cffg3d84ydp9nvv84g58ykxqh90xx6j8ywgjst0dkt430w9lxgdmzncsw5rzpd'
\set w1_stake 'stake1uxwxsrys3lr8ssylatte8xdxdhmrcgcqeath3y3hgpysyvq7kng6l'
\set w2_stake 'stake1u9m8geceu3lqaxfwx36wpenz8tn83f2v6nl82xc3j2cdfcqd7ju39'
\set w3_stake 'stake1uyvwdakz7k4my7gsgggwq53ryx2x0k7exe7frj4drwnmfhse53hr2'
\set w4_stake 'stake1u9046lsq9rmc5a8kzpnx7v9kwy5vquv0q6wt2g8l9mnlg2c0n5ynh'
\set provider_stake 'stake1u885m3ck0hqccswz7zyp564fzh4e429ema9rneuy53ch0vqhj3nvd'
\set liqwid_qnight_contract 'addr1wynz2dws5vjeqhecwg3d7v9q7frzwg8ces042a8x09l9t0g2885qf'
\set binance_allocation_feeder 'addr1vyec4dzr7lsy5apmq2ld95pwtt7d9j9za00xknh960wr7ng2fwyzq'
\set binance_night_custody 'addr1vy26yjamt2hnamy7xqwwvepafhn62pmktyw30gal670slsc7rmelv'
\set binance_1_address 'addr1vx7j284mqe59w2mka36gf5xq0hvu8ms2989553fk5qh3prcapfpj3'
\set credit_pay_hub 'addr1vxhyxumuh98fxf9y4d4z98q34lmtpgqaxxu92thp2ynvnrcf38k4w'

\echo '1. Warehouse tip and canonical NIGHT asset'
SELECT MAX(block_no) AS tip_block, MAX(time) AS tip_time_utc FROM block;

SELECT id AS multi_asset_id,
       encode(policy, 'hex') AS policy_hex,
       encode(name, 'hex') AS asset_name_hex,
       fingerprint
FROM multi_asset
WHERE id = :night_ident;

\echo '2. Four bridge-drain transactions'
WITH attack(tx_hash) AS (
  VALUES
    ('0a4861be5dd1cd0a5ccd7d38855ef8fe233563274c22c27adb4f5980535d2ea1'),
    ('ba4edf844c8dc1289a63660a33a720d24d7dd83825222354b09aee5847132305'),
    ('e4ff7b122df4bc78dc151089a581eedf7997974eaeb74df011a09a889de6f1d7'),
    ('fe9e9de054459578dbfaa5507f447ea4453a7525f801b526d9ffebe6753aaf3d')
), attack_tx AS (
  SELECT a.tx_hash, t.id AS tx_id, b.block_no, b.time
  FROM attack a
  JOIN tx t ON t.hash = decode(a.tx_hash, 'hex')
  JOIN block b ON b.id = t.block_id
), bridge_in AS (
  SELECT i.tx_in_id AS tx_id, SUM(n.quantity)::numeric AS night_star
  FROM attack_tx a
  JOIN tx_in i ON i.tx_in_id = a.tx_id
  JOIN tx_out src ON src.tx_id = i.tx_out_id AND src.index = i.tx_out_index
  JOIN ma_tx_out n ON n.tx_out_id = src.id AND n.ident = :night_ident
  WHERE src.address = :'bridge_address'
  GROUP BY i.tx_in_id
), bridge_out AS (
  SELECT o.tx_id, SUM(n.quantity)::numeric AS night_star
  FROM attack_tx a
  JOIN tx_out o ON o.tx_id = a.tx_id
  JOIN ma_tx_out n ON n.tx_out_id = o.id AND n.ident = :night_ident
  WHERE o.address = :'bridge_address'
  GROUP BY o.tx_id
), w1_out AS (
  SELECT o.tx_id, SUM(n.quantity)::numeric AS night_star
  FROM attack_tx a
  JOIN tx_out o ON o.tx_id = a.tx_id
  JOIN stake_address s ON s.id = o.stake_address_id
  JOIN ma_tx_out n ON n.tx_out_id = o.id AND n.ident = :night_ident
  WHERE s.view = :'w1_stake'
  GROUP BY o.tx_id
)
SELECT a.tx_hash, a.block_no, a.time AS block_time_utc,
       bi.night_star / 1000000.0 AS bridge_input_night,
       bo.night_star / 1000000.0 AS bridge_change_night,
       w1.night_star / 1000000.0 AS w1_received_night
FROM attack_tx a
JOIN bridge_in bi ON bi.tx_id = a.tx_id
JOIN bridge_out bo ON bo.tx_id = a.tx_id
JOIN w1_out w1 ON w1.tx_id = a.tx_id
ORDER BY a.time;

\echo '3. Bridge NIGHT balance immediately before/after the drain and at tip'
WITH cuts(label, cut_time) AS (
  VALUES
    ('pre_attack', TIMESTAMP '2026-07-20 14:46:00'),
    ('post_attack', TIMESTAMP '2026-07-20 14:56:00'),
    ('report_tip', TIMESTAMP '2026-07-22 02:27:16')
), bridge_utxos AS (
  SELECT o.tx_id, o.index, n.quantity::numeric AS night_star,
         cb.time AS create_time, sb.time AS spend_time
  FROM tx_out o
  JOIN ma_tx_out n ON n.tx_out_id = o.id AND n.ident = :night_ident
  JOIN tx ct ON ct.id = o.tx_id
  JOIN block cb ON cb.id = ct.block_id
  LEFT JOIN tx_in i ON i.tx_out_id = o.tx_id AND i.tx_out_index = o.index
  LEFT JOIN tx st ON st.id = i.tx_in_id
  LEFT JOIN block sb ON sb.id = st.block_id
  WHERE o.address = :'bridge_address'
)
SELECT c.label, c.cut_time,
       COUNT(*) FILTER (
         WHERE u.create_time <= c.cut_time
           AND (u.spend_time IS NULL OR u.spend_time > c.cut_time)
       ) AS night_utxos,
       SUM(u.night_star) FILTER (
         WHERE u.create_time <= c.cut_time
           AND (u.spend_time IS NULL OR u.spend_time > c.cut_time)
       ) / 1000000.0 AS night_balance
FROM cuts c CROSS JOIN bridge_utxos u
GROUP BY c.label, c.cut_time
ORDER BY c.cut_time;

\echo '4. Settlement outputs: entity-controlled parcels and locked contracts'
SELECT o.index, o.address, o.address_has_script,
       COALESCE(s.view, 'NO_STAKE_CRED') AS stake_address,
       n.quantity AS night_star,
       n.quantity / 1000000.0 AS night
FROM tx t
JOIN tx_out o ON o.tx_id = t.id
JOIN ma_tx_out n ON n.tx_out_id = o.id AND n.ident = :night_ident
LEFT JOIN stake_address s ON s.id = o.stake_address_id
WHERE t.hash = decode('7a906cde274e3cbdc7e78945b8c0b46bedeb22bba83c40424ebe6d84f546986c', 'hex')
ORDER BY o.index;

\echo '5. Major positive bridge deposits'
WITH bridge_txs AS (
  SELECT DISTINCT i.tx_in_id AS tx_id
  FROM tx_in i
  JOIN tx_out src ON src.tx_id = i.tx_out_id AND src.index = i.tx_out_index
  WHERE src.address = :'bridge_address'
  UNION
  SELECT DISTINCT o.tx_id FROM tx_out o WHERE o.address = :'bridge_address'
), ins AS (
  SELECT i.tx_in_id AS tx_id, SUM(n.quantity)::numeric AS night_star
  FROM bridge_txs w
  JOIN tx_in i ON i.tx_in_id = w.tx_id
  JOIN tx_out src ON src.tx_id = i.tx_out_id AND src.index = i.tx_out_index
  JOIN ma_tx_out n ON n.tx_out_id = src.id AND n.ident = :night_ident
  WHERE src.address = :'bridge_address'
  GROUP BY i.tx_in_id
), outs AS (
  SELECT o.tx_id, SUM(n.quantity)::numeric AS night_star
  FROM bridge_txs w
  JOIN tx_out o ON o.tx_id = w.tx_id
  JOIN ma_tx_out n ON n.tx_out_id = o.id AND n.ident = :night_ident
  WHERE o.address = :'bridge_address'
  GROUP BY o.tx_id
), provider_ins AS (
  SELECT i.tx_in_id AS tx_id, SUM(n.quantity)::numeric AS night_star
  FROM bridge_txs w
  JOIN tx_in i ON i.tx_in_id = w.tx_id
  JOIN tx_out src ON src.tx_id = i.tx_out_id AND src.index = i.tx_out_index
  JOIN stake_address s ON s.id = src.stake_address_id
  JOIN ma_tx_out n ON n.tx_out_id = src.id AND n.ident = :night_ident
  WHERE s.view = :'provider_stake'
  GROUP BY i.tx_in_id
), provider_outs AS (
  SELECT o.tx_id, SUM(n.quantity)::numeric AS night_star
  FROM bridge_txs w
  JOIN tx_out o ON o.tx_id = w.tx_id
  JOIN stake_address s ON s.id = o.stake_address_id
  JOIN ma_tx_out n ON n.tx_out_id = o.id AND n.ident = :night_ident
  WHERE s.view = :'provider_stake'
  GROUP BY o.tx_id
)
SELECT encode(t.hash, 'hex') AS tx_hash, b.time AS block_time_utc,
       (COALESCE(o.night_star, 0) - COALESCE(i.night_star, 0)) / 1000000.0 AS net_bridge_night,
       (COALESCE(pi.night_star, 0) - COALESCE(po.night_star, 0)) / 1000000.0 AS provider_net_sent_night
FROM bridge_txs w
JOIN tx t ON t.id = w.tx_id
JOIN block b ON b.id = t.block_id
LEFT JOIN ins i ON i.tx_id = w.tx_id
LEFT JOIN outs o ON o.tx_id = w.tx_id
LEFT JOIN provider_ins pi ON pi.tx_id = w.tx_id
LEFT JOIN provider_outs po ON po.tx_id = w.tx_id
WHERE COALESCE(o.night_star, 0) - COALESCE(i.night_star, 0) >= 1000000000000
ORDER BY b.time;

\echo '6. Exact 240M NIGHT Binance allocation path on 2026-03-11'
SELECT encode(ct.hash, 'hex') AS create_tx, cb.time AS create_time_utc,
       o.index, o.value / 1000000.0 AS ada,
       n.quantity / 1000000.0 AS night,
       EXISTS (
         SELECT 1
         FROM tx_in source_i
         JOIN tx_out source_o
           ON source_o.tx_id = source_i.tx_out_id
          AND source_o.index = source_i.tx_out_index
         JOIN stake_address source_s ON source_s.id = source_o.stake_address_id
         WHERE source_i.tx_in_id = o.tx_id
           AND source_s.view = :'provider_stake'
       ) AS funded_by_provider,
       CASE WHEN i.tx_in_id IS NULL THEN NULL ELSE encode(st.hash, 'hex') END AS spend_tx,
       sb.time AS spend_time_utc,
       EXISTS (
         SELECT 1 FROM tx_out destination
         WHERE destination.tx_id = i.tx_in_id
           AND destination.address = :'binance_night_custody'
       ) AS spent_into_binance_custody
FROM tx_out o
JOIN tx ct ON ct.id = o.tx_id
JOIN block cb ON cb.id = ct.block_id
JOIN ma_tx_out n ON n.tx_out_id = o.id AND n.ident = :night_ident
LEFT JOIN tx_in i ON i.tx_out_id = o.tx_id AND i.tx_out_index = o.index
LEFT JOIN tx st ON st.id = i.tx_in_id
LEFT JOIN block sb ON sb.id = st.block_id
WHERE o.address = :'binance_allocation_feeder'
ORDER BY cb.time, o.index;

\echo '7. Current W1/W2 wallet-cluster balances'
WITH clusters(label, stake_view) AS (
  VALUES ('W1', :'w1_stake'), ('W2', :'w2_stake'),
         ('W3', :'w3_stake'), ('W4', :'w4_stake')
)
SELECT c.label, COUNT(*) AS unspent_utxos,
       SUM(o.value) / 1000000.0 AS ada,
       SUM(COALESCE(n.quantity, 0)) / 1000000.0 AS night
FROM clusters c
JOIN stake_address s ON s.view = c.stake_view
JOIN tx_out o ON o.stake_address_id = s.id
LEFT JOIN tx_in spent ON spent.tx_out_id = o.tx_id AND spent.tx_out_index = o.index
LEFT JOIN ma_tx_out n ON n.tx_out_id = o.id AND n.ident = :night_ident
WHERE spent.tx_in_id IS NULL
GROUP BY c.label
ORDER BY c.label;

\echo '8. Net NIGHT deposited by W2 into the qNIGHT/Liqwid contract'
WITH target_txs(tx_hash) AS (
  VALUES
    ('2e9981e2458ad2435e50a5c8d3fa75b8babe91ddacf6c9e07406bdc58643b530'),
    ('367fb0ed2d181e0cd2ee4b1991473f31ea58eeb1762f37ffb4b7017f9cf84b5a'),
    ('332b666f7bd8dfd5deb55dbf1fd710c4309c1bd418f47a868d3afd37a93a82bc'),
    ('cf6dcbd2aa6f4a5b772687f87293c9af50196249e8d529072d4c5afdca9692b5'),
    ('ed7b52ea5dd08880b31566bc4fdac9a30725ebf8b85f0ef5b71f35e778e390cf')
), txs AS (
  SELECT x.tx_hash, t.id AS tx_id, b.time
  FROM target_txs x
  JOIN tx t ON t.hash = decode(x.tx_hash, 'hex')
  JOIN block b ON b.id = t.block_id
), ins AS (
  SELECT i.tx_in_id AS tx_id, SUM(n.quantity)::numeric AS night_star
  FROM txs x
  JOIN tx_in i ON i.tx_in_id = x.tx_id
  JOIN tx_out src ON src.tx_id = i.tx_out_id AND src.index = i.tx_out_index
  JOIN ma_tx_out n ON n.tx_out_id = src.id AND n.ident = :night_ident
  WHERE src.address = :'liqwid_qnight_contract'
  GROUP BY i.tx_in_id
), outs AS (
  SELECT o.tx_id, SUM(n.quantity)::numeric AS night_star
  FROM txs x
  JOIN tx_out o ON o.tx_id = x.tx_id
  JOIN ma_tx_out n ON n.tx_out_id = o.id AND n.ident = :night_ident
  WHERE o.address = :'liqwid_qnight_contract'
  GROUP BY o.tx_id
)
SELECT x.tx_hash, x.time AS block_time_utc,
       (COALESCE(o.night_star, 0) - COALESCE(i.night_star, 0)) / 1000000.0 AS net_collateral_night
FROM txs x
LEFT JOIN ins i ON i.tx_id = x.tx_id
LEFT JOIN outs o ON o.tx_id = x.tx_id
ORDER BY x.time;

\echo '9. W4 fan-out: 6,450 fresh 5,000-ADA outputs'
CREATE TEMP TABLE fanout_credentials AS
WITH w4_spend_txs AS (
  SELECT DISTINCT i.tx_in_id AS tx_id
  FROM tx_in i
  JOIN tx_out src ON src.tx_id = i.tx_out_id AND src.index = i.tx_out_index
  JOIN stake_address s ON s.id = src.stake_address_id
  WHERE s.view = :'w4_stake'
)
SELECT o.id AS fanout_tx_out_id, o.payment_cred, o.stake_address_id,
       o.value, (spent.tx_in_id IS NOT NULL) AS is_spent
FROM w4_spend_txs w
JOIN tx_out o ON o.tx_id = w.tx_id
LEFT JOIN tx_in spent ON spent.tx_out_id = o.tx_id AND spent.tx_out_index = o.index
WHERE o.value = 5000000000 AND o.address_has_script = false;

SELECT value / 1000000.0 AS ada, is_spent, COUNT(*) AS outputs,
       SUM(value) / 1000000.0 AS total_ada,
       COUNT(DISTINCT payment_cred) AS payment_credentials,
       COUNT(DISTINCT stake_address_id) AS stake_credentials
FROM fanout_credentials
GROUP BY value, is_spent;

SELECT COUNT(*) FILTER (WHERE EXISTS (
         SELECT 1 FROM tx_out prior
         WHERE prior.payment_cred = f.payment_cred
           AND prior.id <> f.fanout_tx_out_id
       )) AS payment_credentials_with_other_outputs,
       COUNT(*) FILTER (WHERE EXISTS (
         SELECT 1 FROM tx_out prior
         WHERE prior.stake_address_id = f.stake_address_id
           AND prior.id <> f.fanout_tx_out_id
       )) AS stake_credentials_with_other_outputs
FROM fanout_credentials f;

\echo '10. W1 pre-funding from the credit.pay aggregation rail'
WITH funding AS (
  SELECT t.id, b.time
  FROM tx t
  JOIN block b ON b.id = t.block_id
  WHERE t.hash = decode('30d1a8223ff526bdce90348bb3a7deb7e867780cfae19bb35b2f954936c2a15d', 'hex')
), input_totals AS (
  SELECT src.address, SUM(src.value)::numeric AS lovelace
  FROM funding f
  JOIN tx_in i ON i.tx_in_id = f.id
  JOIN tx_out src ON src.tx_id = i.tx_out_id AND src.index = i.tx_out_index
  GROUP BY src.address
), w1_outputs AS (
  SELECT o.address, SUM(o.value)::numeric AS lovelace
  FROM funding f
  JOIN tx_out o ON o.tx_id = f.id
  JOIN stake_address s ON s.id = o.stake_address_id
  WHERE s.view = :'w1_stake'
  GROUP BY o.address
)
SELECT 'input' AS role, f.time AS block_time_utc,
       x.address, x.lovelace / 1000000.0 AS ada
FROM funding f CROSS JOIN input_totals x
UNION ALL
SELECT 'W1 output', f.time, x.address, x.lovelace / 1000000.0
FROM funding f CROSS JOIN w1_outputs x
ORDER BY role;

\echo '11. Pre-public-thread exchange-style deposit staging and sweep rails'
CREATE TEMP TABLE staged_deposits AS
WITH w1_spend_txs AS (
  SELECT DISTINCT i.tx_in_id AS tx_id
  FROM tx_in i
  JOIN tx_out src ON src.tx_id = i.tx_out_id AND src.index = i.tx_out_index
  JOIN stake_address s ON s.id = src.stake_address_id
  JOIN tx t ON t.id = i.tx_in_id
  JOIN block b ON b.id = t.block_id
  WHERE s.view = :'w1_stake'
    AND b.time >= TIMESTAMP '2026-07-20 14:46:00'
    AND b.time < TIMESTAMP '2026-07-20 21:57:00'
)
SELECT o.id, o.tx_id, o.index, o.address, o.value
FROM w1_spend_txs w
JOIN tx_out o ON o.tx_id = w.tx_id
LEFT JOIN stake_address s ON s.id = o.stake_address_id
WHERE o.value IN (50000000000, 100000000000)
  AND (s.view IS NULL OR s.view <> :'w1_stake');

WITH address_first AS (
  SELECT address, MIN(id) AS first_staged_id
  FROM staged_deposits
  GROUP BY address
)
SELECT COUNT(*) AS staged_addresses,
       COUNT(*) FILTER (WHERE NOT EXISTS (
         SELECT 1 FROM tx_out prior
         WHERE prior.address = a.address
           AND prior.id < a.first_staged_id
       )) AS first_seen_with_attacker,
       COUNT(*) FILTER (WHERE EXISTS (
         SELECT 1 FROM tx_out prior
         WHERE prior.address = a.address
           AND prior.id < a.first_staged_id
       )) AS prior_history
FROM address_first a;

WITH linked AS (
  SELECT d.*, i.tx_in_id AS sweep_tx_id,
         EXISTS (
           SELECT 1 FROM tx_out destination
           WHERE destination.tx_id = i.tx_in_id
             AND destination.address = :'credit_pay_hub'
         ) AS to_credit,
         EXISTS (
           SELECT 1 FROM tx_out destination
           WHERE destination.tx_id = i.tx_in_id
             AND destination.address = :'binance_1_address'
         ) AS to_binance1
  FROM staged_deposits d
  LEFT JOIN tx_in i ON i.tx_out_id = d.tx_id AND i.tx_out_index = d.index
)
SELECT CASE WHEN to_credit THEN 'credit.pay'
            WHEN to_binance1 THEN 'Binance 1' END AS rail,
       COUNT(*) AS staged_outputs,
       COUNT(DISTINCT address) AS staged_addresses,
       COUNT(DISTINCT sweep_tx_id) AS sweep_txs,
       SUM(value) / 1000000.0 AS staged_ada
FROM linked
WHERE to_credit OR to_binance1
GROUP BY CASE WHEN to_credit THEN 'credit.pay'
              WHEN to_binance1 THEN 'Binance 1' END
ORDER BY rail;

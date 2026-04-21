-- Hypothesis: If the 4th entry shares beneficial ownership with the Shelley-era 12-address cross-delegation set, some descendants should register or use stake credentials from that set.
-- Expected result: Any overlap is notable and should be investigated. No overlap weakens the case that the 4th-entry descendants and the 12-address set are the same controlled beneficiary set.
-- Interpretation: This is a targeted falsification screen. Absence of overlap does not disprove shared administration.
-- Notes:
--   Read-only, SELECT-only. Prefers explorer.* derived schemas when available.

WITH fourth_seed AS (
  SELECT tx.id AS anchor_tx_id
  FROM public.tx tx
  WHERE tx.hash = decode('5ec95a53fa3bb7dc56864bb6e75f369f00aa20e8d8cdc3b66b2fb88ec1b225ef', 'hex')
),
fourth_descendant_stakes AS (
  SELECT DISTINCT ca.stake_address
  FROM explorer.trace_edges te
  JOIN fourth_seed s ON te.root_tx_id = s.anchor_tx_id
  JOIN explorer.credential_address_map ca
    ON ca.dest_tx_out_id = te.dest_tx_out_id
  WHERE ca.stake_address IS NOT NULL
),
cross_delegating_12 AS (
  SELECT stake_address
  FROM (VALUES
    ('stake1u8stds2advjjwuxypcl7qkeg33ru9muvdlgzt296sg06zjclkd7vt'),
    ('stake1u9t4q48qsjy4mnnd80pe5pexy3m2vwjr7px3rccew7ffgksf86npr'),
    ('stake1uxttvx739dt505d6sxvdykj8336utdq2q92jk3sv253zp5qalcz84'),
    ('stake1uxztgcgh49sld46q94xtjy7zf8j2tnntd6rswl9dypa9ffqqxrz2a'),
    ('stake1u9wxw9y574v9ngskl63effw6qlwl4tg6dr2zrrufhc7anncvvnqkp'),
    ('stake1u833p40y8cm07ra9wgrqgp70z6khc5pttrena97c6en6p8c7pzxda'),
    ('stake1u8dg8spc3skawcyzemtxz8f0zk5eadxftq35qcd4f7n5hrc82xu8k'),
    ('stake1ux3a593q7tq69jkjw7ygqss5mdtteh863r40qhvnftapt6q68puk9'),
    ('stake1ux5tpajlpe25jwazt5aypj37xn9qqfp59tffmj9pjaq2q2qww0acs'),
    ('stake1uxexwrph9r2p3lv42r7ccjptpmml33u2v3xx4p0q9ks85wc2y9t33'),
    ('stake1uxrytqx0v9t0rcz3dlshj08n2w6khfxu3k276vppqsukk2sfw5u56'),
    ('stake1u8rmlr2h99gnvdaagycv97p96mclctn2y6sknryy37m0wtspfnsht')
  ) AS t(stake_address)
)
SELECT
  c12.stake_address,
  CASE WHEN fds.stake_address IS NOT NULL THEN true ELSE false END AS appears_in_fourth_entry_descendants
FROM cross_delegating_12 c12
LEFT JOIN fourth_descendant_stakes fds
  ON fds.stake_address = c12.stake_address
ORDER BY appears_in_fourth_entry_descendants DESC, c12.stake_address;

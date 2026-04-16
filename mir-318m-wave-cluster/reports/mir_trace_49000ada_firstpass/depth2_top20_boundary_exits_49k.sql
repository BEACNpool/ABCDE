COPY (
WITH frontier_stake(view) AS (
  VALUES
    ('stake1uxaertz49825tjhczzy3heghk3nq6jugcvdxtqzn2avgeaqr64xk3'),
    ('stake1u80fnwl4jf822fvqn9p3cum5ncl6lxph0wtdrgc08mw078ct3ysht'),
    ('stake1uy4paxdaxtnnnv48fzc4r8zvwqq25x7mnl9xf7pxhar4ehqnaycxa'),
    ('stake1u9jasamtphty6907hl43t7tfecyqe2ju5lqaw3zfgad33kcvwmlue'),
    ('stake1uy6tdplul92rfp8ewuc6vmncuq7h5rgdwdlfx7hga7faf5qruws4u'),
    ('stake1u909pyegwxe8lwxya5283jctzg6ryttfy42mefyp7639ukggy2hfz'),
    ('stake1u9ua5m029qe3z8tjkmszek0q8dj3hzmxvss8aq05qqghsygg452j2'),
    ('stake1u83sjd5pa4paymq6hled52hjggwmj5yedvdhxdxuumxj7qg4kdzh3'),
    ('stake1uxh5clcr4gjdqhlhfkyljqkfpaqxkc25yfva2cxs5t2w9pc4a8c0h'),
    ('stake1uyx7rsxu9rzlhk9hhrv2enh4rz4fp820xuf06qwqj08rekqfh6j2k'),
    ('stake1uxhpml8xs6zvmtdtf2yxylp3c87xshguxlggpa4kyks966g3lvzzh'),
    ('stake1u8jzezej70zecawsdwhdlvvphuvh9dexjd33w4t3ghh692sfl5nlj'),
    ('stake1uyzfgj0336nl0llsf5rhf4s55rgema2yt82v8k9qv85pf0gy3ce85'),
    ('stake1uyg58xvhn7pmal7k0ml8d45jnvc30dla44r5lpsfv2z5r0gr93jsa'),
    ('stake1uy6rthet2e8lcv2v4j8wnex5px5xkv2l4x3pxnzzcxswgjsuldej4'),
    ('stake1u8m3lka5kk8dw849nhey8ghn8vfykf3s2cmrfteasua0umc8qq0d0'),
    ('stake1u8qdnezzx46h3wugcvadl8h2jjhs5xxystzn7xhcj5eu2rskzvvlm'),
    ('stake1ux8fdwdrdp3x498xw5hs3jskeh9cmhgj70jj593jtnpka3suxrt5s'),
    ('stake1uyj04kvgj55lqkec8uunv0y79khe85678fznm36vpa6wels4jrvlr'),
    ('stake1uycpcww6waycm2ffdfmmc4z8nvptx9er6qn84zqysx0kklstnvw38')
),
frontier_addr(address) AS (
  VALUES
    ('addr1v98pnns6yw8zja9uxzufddpm8tsk5swxf7vv5j4vqjlswgczd4d2t'),
    ('addr1wxtwkls63ae00apdncn4hlxt6jala8367weqam9srlmul5g78wtm4'),
    ('addr1wyc9fpugnw6dprx2kly87mwk0razrh6347qmkn74glq2rlqzsmd6w'),
    ('addr1wxxaleu8a0feusutn3ntnqfg3a55hp0t5l2hqjeau0wg7cc4262zv'),
    ('addr1wymztkhaekt7derv6ceu2xhkcw4zl92m68xyvmcpqlxy0kqggmn4s'),
    ('addr1wyh9nq6fjw72mqud6w7yfe0h4tv04fxdfgcz9akczxgey8c649vxx'),
    ('addr1w9t3xx2jwwh3px0x9gcyz0cxhx29f4rcp0yrpj50ur26regz3gpyl'),
    ('addr1wx5gn92erwwd639twe3m46g3z6c9mdjdpkhcqduzq8g3xgqhwvjwu'),
    ('addr1wxwfdgvamxp0ea4sgvngnnj9pd7aa455uc8z7w54sp8ehxsp77mfy'),
    ('addr1v8aak8psnwz72gvhaawupj5fgl4ukvxz55d3jqt743z8n2sc8zwyh'),
    ('addr1wx4fknf39dsf2s4z6dkm57rmegawyjx6zpl93mju3ml8phgvsa6y8'),
    ('addr1wy4mdmkdggu369d9karndccwgx0cuyuwr7vzpdjktyh0pqsjy7j56'),
    ('addr1wx886xj2uyppjgsxxdjgzknfmykjjerfapgfyvedaagvmmgtevrtr'),
    ('addr1w9zwa7kpxxnnsndrlh5fxuydk48pax3m985q73ja4ntqgpshrvztq'),
    ('addr1w9lkk0dgvcx4d0l5uqsfd393lxdu697epugwefrjxm62dms27y90l'),
    ('addr1vyt8aeq20rvwm2wwx8yvf7kxgejhg7nmlyd032caxn3cpcc6reqkf'),
    ('addr1w8rpse9h098yhydxwwkvzlgxzgpzqc2705jjrlp2yfvcmrcpyych5'),
    ('addr1w8563gqg6yc59y3ex5wsd268nvqz8j2q59dn4nzsgumlw4s3ee8q5'),
    ('addr1w999l4d7rtccm4nutl4xam3kpw8hd4h2r7pf5u8033undccsxyfc9'),
    ('addr1w8fzzf8d7yu4mndpuy2qug57674v29l92jxmjed6vxk5y8c6qrgga')
),
seed_utxos AS (
  SELECT DISTINCT
    txo.tx_id,
    txo.index AS tx_index,
    txo.value,
    CASE
      WHEN sa.view IN (SELECT view FROM frontier_stake) THEN 'stake'
      WHEN txo.address IN (SELECT address FROM frontier_addr) THEN 'enterprise'
      ELSE NULL
    END AS frontier_kind
  FROM tx_out txo
  LEFT JOIN stake_address sa ON sa.id = txo.stake_address_id
  WHERE sa.view IN (SELECT view FROM frontier_stake)
     OR txo.address IN (SELECT address FROM frontier_addr)
),
spend_txs AS (
  SELECT DISTINCT
    ti.tx_out_id AS spend_tx_id,
    su.value AS src_value,
    su.frontier_kind
  FROM seed_utxos su
  JOIN tx_in ti ON ti.tx_in_id = su.tx_id AND ti.tx_out_index = su.tx_index
),
spend_summary AS (
  SELECT spend_tx_id,
         COUNT(*) AS frontier_input_count,
         SUM(src_value) AS frontier_input_lovelace,
         COUNT(*) FILTER (WHERE frontier_kind = 'stake') AS stake_input_count,
         COUNT(*) FILTER (WHERE frontier_kind = 'enterprise') AS enterprise_input_count
  FROM spend_txs
  GROUP BY spend_tx_id
),
dest_rows AS (
  SELECT
    ss.spend_tx_id,
    encode(t.hash,'hex') AS spend_tx_hash,
    b.epoch_no,
    b.time AS block_time,
    ss.frontier_input_count,
    ss.frontier_input_lovelace,
    ss.stake_input_count,
    ss.enterprise_input_count,
    txo.index AS dest_index,
    txo.address AS dest_address,
    txo.value AS dest_lovelace,
    sa.view AS dest_stake_address,
    CASE
      WHEN sa.view IN (SELECT view FROM frontier_stake) THEN 'internal_stake'
      WHEN txo.address IN (SELECT address FROM frontier_addr) THEN 'internal_address'
      WHEN sa.view IS NOT NULL THEN 'external_stake'
      ELSE 'enterprise'
    END AS dest_type
  FROM spend_summary ss
  JOIN tx t ON t.id = ss.spend_tx_id
  JOIN block b ON b.id = t.block_id
  JOIN tx_out txo ON txo.tx_id = ss.spend_tx_id
  LEFT JOIN stake_address sa ON sa.id = txo.stake_address_id
),
shape AS (
  SELECT spend_tx_id,
         COUNT(*) AS total_output_count,
         COUNT(*) FILTER (WHERE dest_type LIKE 'internal%') AS internal_output_count,
         COUNT(*) FILTER (WHERE dest_type = 'external_stake') AS external_stake_output_count,
         COUNT(*) FILTER (WHERE dest_type = 'enterprise') AS enterprise_output_count,
         COALESCE(SUM(dest_lovelace) FILTER (WHERE dest_type LIKE 'internal%'), 0) AS internal_output_lovelace,
         COALESCE(SUM(dest_lovelace) FILTER (WHERE dest_type = 'external_stake'), 0) AS external_stake_output_lovelace,
         COALESCE(SUM(dest_lovelace) FILTER (WHERE dest_type = 'enterprise'), 0) AS enterprise_output_lovelace
  FROM dest_rows
  GROUP BY spend_tx_id
),
latest_pool AS (
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
    SELECT DISTINCT dest_stake_address FROM dest_rows WHERE dest_stake_address IS NOT NULL
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
    SELECT DISTINCT dest_stake_address FROM dest_rows WHERE dest_stake_address IS NOT NULL
  )
  ORDER BY dv.addr_id, tx.block_id DESC, dv.tx_id DESC, dv.cert_index DESC
)
SELECT
  dr.spend_tx_hash,
  dr.epoch_no,
  dr.block_time,
  dr.frontier_input_count,
  dr.frontier_input_lovelace,
  dr.stake_input_count,
  dr.enterprise_input_count,
  dr.dest_index,
  dr.dest_type,
  dr.dest_address,
  dr.dest_stake_address,
  dr.dest_lovelace,
  sh.total_output_count,
  sh.internal_output_count,
  sh.external_stake_output_count,
  sh.enterprise_output_count,
  sh.internal_output_lovelace,
  sh.external_stake_output_lovelace,
  sh.enterprise_output_lovelace,
  ph.view AS current_pool,
  dh.view AS current_drep
FROM dest_rows dr
JOIN shape sh ON sh.spend_tx_id = dr.spend_tx_id
LEFT JOIN stake_address sa ON sa.view = dr.dest_stake_address
LEFT JOIN latest_pool lp ON lp.addr_id = sa.id
LEFT JOIN pool_hash ph ON ph.id = lp.pool_hash_id
LEFT JOIN latest_vote lv ON lv.addr_id = sa.id
LEFT JOIN drep_hash dh ON dh.id = lv.drep_hash_id
WHERE dr.dest_type NOT LIKE 'internal%'
  AND dr.dest_lovelace >= 49000000000
ORDER BY dr.dest_lovelace DESC, dr.spend_tx_hash, dr.dest_index
) TO STDOUT WITH CSV HEADER;

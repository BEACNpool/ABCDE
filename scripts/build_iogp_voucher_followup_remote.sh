#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ -z "${ABCDE_SSH:-}" ]]; then
  echo "Set ABCDE_SSH to the SSH target for the db-sync warehouse host." >&2
  exit 2
fi
DB_NAME="${DB_NAME:-cexplorer_replica}"
OUT_DIR="${1:-$REPO_ROOT/data/small}"
mkdir -p "$OUT_DIR"

run_sql() {
  local out="$1"
  ssh "$ABCDE_SSH" \
    "sudo -n -u postgres psql -q -v ON_ERROR_STOP=1 -d '$DB_NAME' --csv -f -" \
    > "$out"
}

cat <<'SQL' | run_sql "$OUT_DIR/iogp_pool_registration.csv"
WITH tip AS (
  SELECT block_no, epoch_no, time FROM public.block ORDER BY id DESC LIMIT 1
)
SELECT
  tip.block_no AS source_tip_block,
  tip.epoch_no AS source_tip_epoch,
  tip.time AS source_tip_time_utc,
  ph.view AS pool_id_bech32,
  opd.ticker_name,
  pu.pledge AS declared_pledge_lovelace,
  encode(t.hash,'hex') AS registration_tx_hash,
  b.time AS registration_time_utc,
  sar.view AS reward_stake_address,
  sao.view AS owner_stake_address
FROM public.pool_update pu
JOIN public.pool_hash ph ON ph.id = pu.hash_id
LEFT JOIN LATERAL (
  SELECT ticker_name
  FROM public.off_chain_pool_data
  WHERE pool_id = ph.id
  ORDER BY id DESC
  LIMIT 1
) opd ON true
LEFT JOIN public.stake_address sar ON sar.id = pu.reward_addr_id
LEFT JOIN public.pool_owner po ON po.pool_update_id = pu.id
LEFT JOIN public.stake_address sao ON sao.id = po.addr_id
JOIN public.tx t ON t.id = pu.registered_tx_id
JOIN public.block b ON b.id = t.block_id
CROSS JOIN tip
WHERE ph.view = 'pool1x5ge78ks6jc0j8nsfwyqqhk2ukxlkvz7zxlm9utgk6405hh490n'
ORDER BY b.time;
SQL

cat <<'SQL' | run_sql "$OUT_DIR/iogp_pool_epoch_stake.csv"
WITH tip AS (
  SELECT block_no, epoch_no, time FROM public.block ORDER BY id DESC LIMIT 1
), pool AS (
  SELECT id FROM public.pool_hash
  WHERE view = 'pool1x5ge78ks6jc0j8nsfwyqqhk2ukxlkvz7zxlm9utgk6405hh490n'
), roles(stake_address, role) AS (VALUES
  ('stake1uxnwfdn9samwjqj6n3sfgtflxmca47l4dns8snkz0tp9v6c5nnhs3','reward_account'),
  ('stake1u8j97tdpg2m69dl9augnj9zqrh95t3dd6cuxuner6eypzpctfdkkx','registered_owner')
)
SELECT
  tip.block_no AS source_tip_block,
  tip.epoch_no AS source_tip_epoch,
  tip.time AS source_tip_time_utc,
  es.epoch_no,
  sa.view AS stake_address,
  coalesce(r.role, 'other_delegator') AS stake_role,
  es.amount AS active_stake_lovelace
FROM public.epoch_stake es
JOIN pool p ON p.id = es.pool_id
JOIN public.stake_address sa ON sa.id = es.addr_id
LEFT JOIN roles r ON r.stake_address = sa.view
CROSS JOIN tip
WHERE es.epoch_no IN (250,255,260,270,290)
ORDER BY es.epoch_no, es.amount DESC, sa.view;
SQL

cat <<'SQL' | run_sql "$OUT_DIR/voucher_wallet_profile.csv"
CREATE TEMP TABLE voucher_address_outs AS
SELECT o.tx_id, o.index, o.value, o.stake_address_id, b.time AS block_time
FROM public.tx_out o
JOIN public.tx t ON t.id = o.tx_id
JOIN public.block b ON b.id = t.block_id
WHERE o.address = 'addr1qy2qmzemzpx4w3sz0z8fp0x2xwnttksn655uc5sxml2yaznsluv29uarg9hhghehhf7r7kmyrh6wsvtgg2caanrf94us0j0w0n';
ANALYZE voucher_address_outs;

WITH tip AS (
  SELECT block_no, epoch_no, time FROM public.block ORDER BY id DESC LIMIT 1
), target AS (
  SELECT
    'addr1qy2qmzemzpx4w3sz0z8fp0x2xwnttksn655uc5sxml2yaznsluv29uarg9hhghehhf7r7kmyrh6wsvtgg2caanrf94us0j0w0n'::text AS address,
    id AS stake_address_id
  FROM public.stake_address
  WHERE view = 'stake1u9c07x9z7w35zmm5tumm5lpltdjpma8gx95y9vw7e35j67gz7r8a7'
), address_stats AS (
  SELECT
    count(*) AS address_utxos,
    sum(value) AS address_received_lovelace,
    min(block_time) AS first_seen_utc,
    max(block_time) AS last_seen_utc
  FROM voucher_address_outs
), stake_stats AS (
  SELECT
    count(DISTINCT o.address) AS stake_address_count,
    count(*) AS stake_utxos,
    sum(o.value) AS stake_received_lovelace
  FROM target x
  JOIN public.tx_out o ON o.stake_address_id = x.stake_address_id
)
SELECT
  tip.block_no AS source_tip_block,
  tip.epoch_no AS source_tip_epoch,
  tip.time AS source_tip_time_utc,
  x.address,
  sa.view AS stake_address,
  a.address_utxos,
  a.address_received_lovelace,
  s.stake_address_count,
  s.stake_utxos,
  s.stake_received_lovelace,
  a.first_seen_utc,
  a.last_seen_utc
FROM target x
JOIN public.stake_address sa ON sa.id = x.stake_address_id
CROSS JOIN address_stats a
CROSS JOIN stake_stats s
CROSS JOIN tip;
SQL

cat <<'SQL' | run_sql "$OUT_DIR/voucher_wallet_delegations.csv"
WITH tip AS (
  SELECT block_no, epoch_no, time FROM public.block ORDER BY id DESC LIMIT 1
), target AS (
  SELECT id AS stake_address_id
  FROM public.stake_address
  WHERE view = 'stake1u9c07x9z7w35zmm5tumm5lpltdjpma8gx95y9vw7e35j67gz7r8a7'
)
SELECT
  tip.block_no AS source_tip_block,
  tip.epoch_no AS source_tip_epoch,
  tip.time AS source_tip_time_utc,
  sa.view AS stake_address,
  ph.view AS pool_id_bech32,
  coalesce(opd.ticker_name,'') AS ticker_name,
  encode(t.hash,'hex') AS certificate_tx_hash,
  b.time AS certificate_time_utc
FROM target x
JOIN public.delegation d ON d.addr_id = x.stake_address_id
JOIN public.stake_address sa ON sa.id = d.addr_id
JOIN public.pool_hash ph ON ph.id = d.pool_hash_id
LEFT JOIN LATERAL (
  SELECT ticker_name FROM public.off_chain_pool_data
  WHERE pool_id = ph.id ORDER BY id DESC LIMIT 1
) opd ON true
JOIN public.tx t ON t.id = d.tx_id
JOIN public.block b ON b.id = t.block_id
CROSS JOIN tip
ORDER BY b.time, t.id, d.cert_index;
SQL

cat <<'SQL' | run_sql "$OUT_DIR/voucher_wallet_counterparty_summary.csv"
CREATE TEMP TABLE voucher_address_outs AS
SELECT o.tx_id, o.index, o.value, b.time AS block_time
FROM public.tx_out o
JOIN public.tx t ON t.id = o.tx_id
JOIN public.block b ON b.id = t.block_id
WHERE o.address = 'addr1qy2qmzemzpx4w3sz0z8fp0x2xwnttksn655uc5sxml2yaznsluv29uarg9hhghehhf7r7kmyrh6wsvtgg2caanrf94us0j0w0n';
ANALYZE voucher_address_outs;

WITH tip AS (
  SELECT block_no, epoch_no, time FROM public.block ORDER BY id DESC LIMIT 1
), target AS (
  SELECT
    'addr1qy2qmzemzpx4w3sz0z8fp0x2xwnttksn655uc5sxml2yaznsluv29uarg9hhghehhf7r7kmyrh6wsvtgg2caanrf94us0j0w0n'::text AS address,
    id AS stake_address_id
  FROM public.stake_address
  WHERE view = 'stake1u9c07x9z7w35zmm5tumm5lpltdjpma8gx95y9vw7e35j67gz7r8a7'
), target_in AS (
  SELECT tx_id, sum(value) AS target_value, min(block_time) AS event_time
  FROM voucher_address_outs
  GROUP BY tx_id
), inbound AS (
  SELECT
    'inbound'::text AS direction,
    CASE WHEN sa.view IS NOT NULL THEN 'stake_address' ELSE 'address' END AS counterparty_type,
    coalesce(sa.view, po.address) AS counterparty,
    count(DISTINCT d.tx_id) AS transaction_count,
    sum(d.target_value) AS associated_lovelace,
    min(d.event_time) AS first_event_utc,
    max(d.event_time) AS last_event_utc,
    'full target deposit associated with each distinct input identifier'::text AS attribution_note
  FROM target_in d
  JOIN public.tx_in i ON i.tx_in_id = d.tx_id
  JOIN public.tx_out po ON po.tx_id = i.tx_out_id AND po.index = i.tx_out_index
  LEFT JOIN public.stake_address sa ON sa.id = po.stake_address_id
  GROUP BY 2,3
), spends AS (
  SELECT DISTINCT i.tx_in_id AS tx_id
  FROM voucher_address_outs o
  JOIN public.tx_in i ON i.tx_out_id = o.tx_id AND i.tx_out_index = o.index
), outbound AS (
  SELECT
    'outbound'::text AS direction,
    CASE WHEN sa.view IS NOT NULL THEN 'stake_address' ELSE 'address' END AS counterparty_type,
    coalesce(sa.view, o.address) AS counterparty,
    count(DISTINCT o.tx_id) AS transaction_count,
    sum(o.value) AS associated_lovelace,
    min(b.time) AS first_event_utc,
    max(b.time) AS last_event_utc,
    'sum of outputs to identifier in transactions spending target-address UTxOs'::text AS attribution_note
  FROM spends s
  JOIN public.tx_out o ON o.tx_id = s.tx_id
  JOIN public.tx t ON t.id = s.tx_id
  JOIN public.block b ON b.id = t.block_id
  LEFT JOIN public.stake_address sa ON sa.id = o.stake_address_id
  GROUP BY 2,3
), combined AS (
  SELECT * FROM inbound
  UNION ALL
  SELECT * FROM outbound
)
SELECT
  tip.block_no AS source_tip_block,
  tip.epoch_no AS source_tip_epoch,
  tip.time AS source_tip_time_utc,
  c.*
FROM combined c
CROSS JOIN tip
ORDER BY c.direction, c.associated_lovelace DESC, c.counterparty;
SQL

cat <<'SQL' | run_sql "$OUT_DIR/iog_voucher_dominant_traces.csv"
WITH RECURSIVE tip AS (
  SELECT block_no, epoch_no, time FROM public.block ORDER BY id DESC LIMIT 1
), known(identifier, label) AS (VALUES
  ('stake1uxnwfdn9samwjqj6n3sfgtflxmca47l4dns8snkz0tp9v6c5nnhs3','IOGP reward account'),
  ('stake1u8j97tdpg2m69dl9augnj9zqrh95t3dd6cuxuner6eypzpctfdkkx','IOGP registered owner'),
  ('stake1uxt2ggq005kfm3uwe89emy3ka2zgdtrpxfarvz6033l3fqgve6ku2','payer 3'),
  ('stake1u8520s54w57rw6pmshw3yz2p2v5wp9g2ac846qn4wm0rx5skeefny','IOG17-ticker pledge hub'),
  ('stake1ux9vw6azy95waz9l3e8dme7pwmhcn68f77kqd245uxw57nqr9upaa','IOG19-ticker pledge stake'),
  ('stake1u8tl8t5pdr9qn488vc9dpehklntt55au96fkqpd8nr28qyqzr7lax','IOG20-ticker pledge stake'),
  ('stake1u8dmqlfv95cyr9u7gskm03cw4s7vm06jq0kctse4klk4fycpm5q4j','IOG1 chain-holder stake'),
  ('stake1uxumgkkyn0gdkntgsg90jkq3wkwqxqfhh46s6j3xd0z8h6see3xh6','WAV1 owner stake'),
  ('stake1u90z89xl6qkgt0lpn79svmpmz9evstxy4wfp8wgpyfcgg5seurw78','WAV10 owner/reward stake'),
  ('stake1u9c07x9z7w35zmm5tumm5lpltdjpma8gx95y9vw7e35j67gz7r8a7','voucher stake'),
  ('stake1uy6yzwsxxc28lfms0qmpxvyz9a7y770rtcqx9y96m42cttqwvp4m5','voucher 52M funder'),
  ('stake1u8nynuagsfkjfsjfhm57dnyzfae8e5szh4rfdxjk2drt53qwhz039','voucher 28M funder')
), seeds(seed_label, tx_hash) AS (VALUES
  ('voucher_funding_1','bd32485b5035d337e8ba5bcce02024a64c2062e9ce9c5f81be22e62a3da8987b'),
  ('voucher_funding_2','8d9d406cefb7831cc85933b23baf7179b884907d86f480134771d7e737957b4d'),
  ('voucher_funding_3','02c3a6b01b8bf3b20df3d41bc904ff4a22b0a67d2c561d386d34aaa9cd4b55be'),
  ('cluster_dust','bd36b8bf58e7d1d6e3bdbec87ba4cf7ca6ed8ee17e9b53bc5509a653e6947ffb')
), hop AS (
  SELECT
    s.seed_label,
    s.tx_hash AS seed_tx_hash,
    t.id AS tx_id,
    0 AS depth,
    NULL::bigint AS source_stake_address_id,
    NULL::text AS source_address,
    NULL::numeric AS dominant_input_lovelace
  FROM seeds s
  JOIN public.tx t ON t.hash = decode(s.tx_hash,'hex')
  UNION ALL
  SELECT
    h.seed_label,
    h.seed_tx_hash,
    dom.tx_id,
    h.depth + 1,
    dom.stake_address_id,
    dom.address,
    dom.value
  FROM hop h
  JOIN LATERAL (
    SELECT po.tx_id, po.stake_address_id, po.address, po.value, po.index
    FROM public.tx_in i
    JOIN public.tx_out po ON po.tx_id = i.tx_out_id AND po.index = i.tx_out_index
    WHERE i.tx_in_id = h.tx_id
    ORDER BY po.value DESC, po.tx_id, po.index
    LIMIT 1
  ) dom ON true
  WHERE h.depth < 80
)
SELECT
  tip.block_no AS source_tip_block,
  tip.epoch_no AS source_tip_epoch,
  tip.time AS source_tip_time_utc,
  h.seed_label,
  h.seed_tx_hash,
  h.depth,
  encode(t.hash,'hex') AS hop_tx_hash,
  b.time AS hop_time_utc,
  h.dominant_input_lovelace,
  CASE WHEN sa.view IS NOT NULL THEN 'stake_address' ELSE 'address' END AS source_type,
  coalesce(sa.view, h.source_address) AS dominant_source,
  k.label AS source_label,
  'largest-input path; not exclusive provenance'::text AS method_note
FROM hop h
JOIN public.tx t ON t.id = h.tx_id
JOIN public.block b ON b.id = t.block_id
LEFT JOIN public.stake_address sa ON sa.id = h.source_stake_address_id
LEFT JOIN known k ON k.identifier = coalesce(sa.view, h.source_address)
CROSS JOIN tip
ORDER BY h.seed_label, h.depth;
SQL

cat <<'SQL' | run_sql "$OUT_DIR/iogp_reward_wallet_destinations.csv"
WITH tip AS (
  SELECT block_no, epoch_no, time FROM public.block ORDER BY id DESC LIMIT 1
), target AS (
  SELECT id FROM public.stake_address
  WHERE view = 'stake1uxnwfdn9samwjqj6n3sfgtflxmca47l4dns8snkz0tp9v6c5nnhs3'
), spends AS (
  SELECT DISTINCT i.tx_in_id AS tx_id
  FROM target x
  JOIN public.tx_out source_out ON source_out.stake_address_id = x.id
  JOIN public.tx_in i
    ON i.tx_out_id = source_out.tx_id
   AND i.tx_out_index = source_out.index
)
SELECT
  tip.block_no AS source_tip_block,
  tip.epoch_no AS source_tip_epoch,
  tip.time AS source_tip_time_utc,
  CASE WHEN sa.view IS NOT NULL THEN 'stake_address' ELSE 'address' END AS destination_type,
  coalesce(sa.view, o.address) AS destination,
  count(DISTINCT o.tx_id) AS transaction_count,
  sum(o.value) AS output_lovelace,
  min(b.time) AS first_output_utc,
  max(b.time) AS last_output_utc
FROM spends s
JOIN public.tx_out o ON o.tx_id = s.tx_id
JOIN public.tx t ON t.id = s.tx_id
JOIN public.block b ON b.id = t.block_id
LEFT JOIN public.stake_address sa ON sa.id = o.stake_address_id
CROSS JOIN tip
GROUP BY tip.block_no, tip.epoch_no, tip.time, 4,5
ORDER BY output_lovelace DESC, destination;
SQL

cat <<'SQL' | run_sql "$OUT_DIR/voucher_funder_delegations.csv"
WITH tip AS (
  SELECT block_no, epoch_no, time FROM public.block ORDER BY id DESC LIMIT 1
)
SELECT
  tip.block_no AS source_tip_block,
  tip.epoch_no AS source_tip_epoch,
  tip.time AS source_tip_time_utc,
  sa.view AS stake_address,
  ph.view AS pool_id_bech32,
  coalesce(opd.ticker_name,'') AS ticker_name,
  encode(t.hash,'hex') AS certificate_tx_hash,
  b.time AS certificate_time_utc
FROM public.delegation d
JOIN public.stake_address sa ON sa.id = d.addr_id
JOIN public.pool_hash ph ON ph.id = d.pool_hash_id
LEFT JOIN LATERAL (
  SELECT ticker_name FROM public.off_chain_pool_data
  WHERE pool_id = ph.id ORDER BY id DESC LIMIT 1
) opd ON true
JOIN public.tx t ON t.id = d.tx_id
JOIN public.block b ON b.id = t.block_id
CROSS JOIN tip
WHERE sa.view IN (
  'stake1uy6yzwsxxc28lfms0qmpxvyz9a7y770rtcqx9y96m42cttqwvp4m5',
  'stake1u8nynuagsfkjfsjfhm57dnyzfae8e5szh4rfdxjk2drt53qwhz039'
)
ORDER BY sa.view, b.time, t.id, d.cert_index;
SQL

cat <<'SQL' | run_sql "$OUT_DIR/voucher_funder_source_summary.csv"
WITH tip AS (
  SELECT block_no, epoch_no, time FROM public.block ORDER BY id DESC LIMIT 1
), targets AS (
  SELECT id, view FROM public.stake_address
  WHERE view IN (
    'stake1uy6yzwsxxc28lfms0qmpxvyz9a7y770rtcqx9y96m42cttqwvp4m5',
    'stake1u8nynuagsfkjfsjfhm57dnyzfae8e5szh4rfdxjk2drt53qwhz039'
  )
), deposits AS (
  SELECT x.view AS funder_stake_address, o.tx_id, sum(o.value) AS target_value, min(b.time) AS event_time
  FROM targets x
  JOIN public.tx_out o ON o.stake_address_id = x.id
  JOIN public.tx t ON t.id = o.tx_id
  JOIN public.block b ON b.id = t.block_id
  GROUP BY x.view, o.tx_id
), sources AS (
  SELECT DISTINCT
    d.funder_stake_address,
    d.tx_id,
    d.target_value,
    d.event_time,
    CASE WHEN sa.view IS NOT NULL THEN 'stake_address' ELSE 'address' END AS source_type,
    coalesce(sa.view, po.address) AS source
  FROM deposits d
  JOIN public.tx_in i ON i.tx_in_id = d.tx_id
  JOIN public.tx_out po ON po.tx_id = i.tx_out_id AND po.index = i.tx_out_index
  LEFT JOIN public.stake_address sa ON sa.id = po.stake_address_id
)
SELECT
  tip.block_no AS source_tip_block,
  tip.epoch_no AS source_tip_epoch,
  tip.time AS source_tip_time_utc,
  s.funder_stake_address,
  s.source_type,
  s.source,
  count(DISTINCT s.tx_id) AS transaction_count,
  sum(s.target_value) AS associated_lovelace,
  min(s.event_time) AS first_event_utc,
  max(s.event_time) AS last_event_utc,
  'full target deposit associated with each distinct input identifier'::text AS attribution_note
FROM sources s
CROSS JOIN tip
GROUP BY tip.block_no, tip.epoch_no, tip.time, s.funder_stake_address, s.source_type, s.source
ORDER BY s.funder_stake_address, associated_lovelace DESC, s.source;
SQL

for name in \
  iogp_pool_registration \
  iogp_pool_epoch_stake \
  voucher_wallet_profile \
  voucher_wallet_delegations \
  voucher_wallet_counterparty_summary \
  iog_voucher_dominant_traces \
  iogp_reward_wallet_destinations \
  voucher_funder_delegations \
  voucher_funder_source_summary
do
  echo "wrote ${OUT_DIR#$REPO_ROOT/}/$name.csv"
done

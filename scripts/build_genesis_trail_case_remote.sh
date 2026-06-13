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

cat <<'SQL' | run_sql "$OUT_DIR/genesis_trail_recipient_outputs.csv"
WITH tip AS (
  SELECT block_no, epoch_no, time FROM public.block ORDER BY id DESC LIMIT 1
)
SELECT
  tip.block_no AS source_tip_block,
  tip.epoch_no AS source_tip_epoch,
  tip.time AS source_tip_time_utc,
  encode(t.hash,'hex') AS tx_hash,
  b.time AS tx_time_utc,
  o.index AS output_index,
  o.value AS value_lovelace,
  o.value >= 20000000000000 AS is_payment_sized,
  o.address AS recipient_address,
  sa.view AS recipient_stake_address
FROM public.tx_out o
JOIN public.tx t ON t.id = o.tx_id
JOIN public.block b ON b.id = t.block_id
LEFT JOIN public.stake_address sa ON sa.id = o.stake_address_id
CROSS JOIN tip
WHERE o.address =
  'addr1qxspyce8mzttagajlhfzwjpc7ym5vn9es2vgxgs4gq4ykx4qzf3j0kykh63m9lwjyayr3ufhgextnq5csv3p2sp2fvdqg8px4u'
ORDER BY b.time, o.index;
SQL

cat <<'SQL' | run_sql "$OUT_DIR/genesis_trail_payment_inputs.csv"
WITH tip AS (
  SELECT block_no, epoch_no, time FROM public.block ORDER BY id DESC LIMIT 1
), payments(tx_hash) AS (VALUES
  ('a28bddfaa018937419357e94f564d4919ee36a68b494a74348bf2ad7de3a9483'),
  ('f98e5cfe1a3870b829228de3f7b13361d74e1b1e276f9cc41e1379342999837f'),
  ('091209d4bf7c1a3a59990cca5e62ba22e2f3efd968f1a5aa5173cc62b5729f34'),
  ('428dbf03c356ddde0ddcae609980b4fd25691d9fe16dc97a2851bc3caf630c4a'),
  ('99dc49521444e8407828ab0de630c32adc44d87182a1266424f0ae51a187a74a'),
  ('cbed28ac74254206e2792c958e72829e58ee36390d1847149522f5e9bedf1b3e'),
  ('d2d7a601b930722ff6c7c036a22a760f18c9b786bd79ec7118f100e4b79859b2'),
  ('0501a2ad9980262f46bfd5fb48d7a7feed00be3896698c784e03b5a7a8681357'),
  ('dfa5f400e0a13d0fb12191c587cc3b786506bc3e1c9e795a9fc4f9821a981f23')
)
SELECT
  tip.block_no AS source_tip_block,
  tip.epoch_no AS source_tip_epoch,
  tip.time AS source_tip_time_utc,
  p.tx_hash AS payment_tx_hash,
  b.time AS payment_time_utc,
  CASE WHEN sa.view IS NOT NULL THEN 'stake_address' ELSE 'address' END AS payer_type,
  coalesce(sa.view, po.address) AS payer,
  sum(po.value) AS input_lovelace
FROM payments p
JOIN public.tx t ON t.hash = decode(p.tx_hash,'hex')
JOIN public.block b ON b.id = t.block_id
JOIN public.tx_in i ON i.tx_in_id = t.id
JOIN public.tx_out po ON po.tx_id = i.tx_out_id AND po.index = i.tx_out_index
LEFT JOIN public.stake_address sa ON sa.id = po.stake_address_id
CROSS JOIN tip
GROUP BY tip.block_no, tip.epoch_no, tip.time, p.tx_hash, b.time, 6, 7
ORDER BY b.time, payer;
SQL

cat <<'SQL' | run_sql "$OUT_DIR/genesis_trail_recipient_forwarding.csv"
WITH tip AS (
  SELECT block_no, epoch_no, time FROM public.block ORDER BY id DESC LIMIT 1
), recipient_outs AS (
  SELECT o.tx_id, o.index
  FROM public.tx_out o
  WHERE o.address =
    'addr1qxspyce8mzttagajlhfzwjpc7ym5vn9es2vgxgs4gq4ykx4qzf3j0kykh63m9lwjyayr3ufhgextnq5csv3p2sp2fvdqg8px4u'
), spends AS (
  SELECT DISTINCT i.tx_in_id AS tx_id
  FROM recipient_outs ro
  JOIN public.tx_in i ON i.tx_out_id = ro.tx_id AND i.tx_out_index = ro.index
)
SELECT
  tip.block_no AS source_tip_block,
  tip.epoch_no AS source_tip_epoch,
  tip.time AS source_tip_time_utc,
  encode(t.hash,'hex') AS forwarding_tx_hash,
  b.time AS forwarding_time_utc,
  o.index AS output_index,
  o.value AS value_lovelace,
  'addr1qxspyce8mzttagajlhfzwjpc7ym5vn9es2vgxgs4gq4ykx4qzf3j0kykh63m9lwjyayr3ufhgextnq5csv3p2sp2fvdqg8px4u'::text
    AS source_address,
  o.address AS destination_address,
  sa.view AS destination_stake_address
FROM spends s
JOIN public.tx t ON t.id = s.tx_id
JOIN public.block b ON b.id = t.block_id
JOIN public.tx_out o ON o.tx_id = s.tx_id
LEFT JOIN public.stake_address sa ON sa.id = o.stake_address_id
CROSS JOIN tip
WHERE o.address =
  'addr1qygm7m8hjqjgyd2qnrthl49g3jwzvnw8e8zfqqefrdx3d0s3hak00ypysg65pxxh0l223ryuyexu0jwyjqpjjx6dz6lq0pgy99'
ORDER BY b.time, o.index;
SQL

cat <<'SQL' | run_sql "$OUT_DIR/genesis_trail_hub_summary.csv"
WITH tip AS (
  SELECT block_no, epoch_no, time FROM public.block ORDER BY id DESC LIMIT 1
)
SELECT
  tip.block_no AS source_tip_block,
  tip.epoch_no AS source_tip_epoch,
  tip.time AS source_tip_time_utc,
  o.address AS hub_address,
  sa.view AS hub_stake_address,
  count(*) AS deposit_outputs,
  count(DISTINCT o.tx_id) AS deposit_transactions,
  sum(o.value) AS received_lovelace,
  min(b.time) AS first_received_utc,
  max(b.time) AS last_received_utc
FROM public.tx_out o
JOIN public.tx t ON t.id = o.tx_id
JOIN public.block b ON b.id = t.block_id
LEFT JOIN public.stake_address sa ON sa.id = o.stake_address_id
CROSS JOIN tip
WHERE o.address =
  'addr1qygm7m8hjqjgyd2qnrthl49g3jwzvnw8e8zfqqefrdx3d0s3hak00ypysg65pxxh0l223ryuyexu0jwyjqpjjx6dz6lq0pgy99'
GROUP BY tip.block_no, tip.epoch_no, tip.time, o.address, sa.view;
SQL

cat <<'SQL' | run_sql "$OUT_DIR/genesis_trail_stream_bridges.csv"
WITH tip AS (
  SELECT block_no, epoch_no, time FROM public.block ORDER BY id DESC LIMIT 1
), streams(stream_label, source_stake, destination_kind, destination) AS (VALUES
  (
    'iogp_reward_to_burst',
    'stake1uxnwfdn9samwjqj6n3sfgtflxmca47l4dns8snkz0tp9v6c5nnhs3',
    'stake_address',
    'stake1uycla9q3glrugp48cq2r7awemjxepvj4lxs4emw5qmpsclc4tpe52'
  ),
  (
    'burst_to_hub',
    'stake1uycla9q3glrugp48cq2r7awemjxepvj4lxs4emw5qmpsclc4tpe52',
    'address',
    'addr1qygm7m8hjqjgyd2qnrthl49g3jwzvnw8e8zfqqefrdx3d0s3hak00ypysg65pxxh0l223ryuyexu0jwyjqpjjx6dz6lq0pgy99'
  ),
  (
    'recipient_to_hub',
    'stake1uxspyce8mzttagajlhfzwjpc7ym5vn9es2vgxgs4gq4ykxsxm6ggr',
    'address',
    'addr1qygm7m8hjqjgyd2qnrthl49g3jwzvnw8e8zfqqefrdx3d0s3hak00ypysg65pxxh0l223ryuyexu0jwyjqpjjx6dz6lq0pgy99'
  ),
  (
    'same_hub_stream_54m',
    'stake1u97ac8v4jhx7xx9sacnc9xccx8gnaevnhmzgmc6px44q9nszmmydr',
    'address',
    'addr1qygm7m8hjqjgyd2qnrthl49g3jwzvnw8e8zfqqefrdx3d0s3hak00ypysg65pxxh0l223ryuyexu0jwyjqpjjx6dz6lq0pgy99'
  ),
  (
    'same_hub_stream_2m',
    'stake1u8gvuee6w2v2p0gqtnzegldt4pmuhd2wp0y7pvjnpm2dxrca5lx4c',
    'address',
    'addr1qygm7m8hjqjgyd2qnrthl49g3jwzvnw8e8zfqqefrdx3d0s3hak00ypysg65pxxh0l223ryuyexu0jwyjqpjjx6dz6lq0pgy99'
  )
), source_outs AS (
  SELECT
    s.*,
    o.tx_id,
    o.index
  FROM streams s
  JOIN public.stake_address source_sa ON source_sa.view = s.source_stake
  JOIN public.tx_out o ON o.stake_address_id = source_sa.id
), spends AS (
  SELECT DISTINCT
    so.stream_label,
    so.source_stake,
    so.destination_kind,
    so.destination,
    i.tx_in_id AS tx_id
  FROM source_outs so
  JOIN public.tx_in i ON i.tx_out_id = so.tx_id AND i.tx_out_index = so.index
), matched AS (
  SELECT
    s.stream_label,
    s.source_stake,
    s.destination_kind,
    s.destination,
    o.tx_id,
    o.value,
    b.time
  FROM spends s
  JOIN public.tx_out o ON o.tx_id = s.tx_id
  JOIN public.tx t ON t.id = s.tx_id
  JOIN public.block b ON b.id = t.block_id
  LEFT JOIN public.stake_address destination_sa ON destination_sa.id = o.stake_address_id
  WHERE
    (s.destination_kind = 'address' AND o.address = s.destination)
    OR
    (s.destination_kind = 'stake_address' AND destination_sa.view = s.destination)
)
SELECT
  tip.block_no AS source_tip_block,
  tip.epoch_no AS source_tip_epoch,
  tip.time AS source_tip_time_utc,
  m.stream_label,
  m.source_stake,
  m.destination_kind,
  m.destination,
  count(DISTINCT m.tx_id) AS transaction_count,
  count(*) AS output_count,
  sum(m.value) AS output_lovelace,
  min(m.time) AS first_output_utc,
  max(m.time) AS last_output_utc
FROM matched m
CROSS JOIN tip
GROUP BY tip.block_no, tip.epoch_no, tip.time,
  m.stream_label, m.source_stake, m.destination_kind, m.destination
ORDER BY m.stream_label;
SQL

cat <<'SQL' | run_sql "$OUT_DIR/genesis_trail_payment_dominant_traces.csv"
WITH RECURSIVE tip AS (
  SELECT block_no, epoch_no, time FROM public.block ORDER BY id DESC LIMIT 1
), seeds(seed_label, tx_hash) AS (VALUES
  ('payment_2021_04_02','a28bddfaa018937419357e94f564d4919ee36a68b494a74348bf2ad7de3a9483'),
  ('payment_2021_04_26','f98e5cfe1a3870b829228de3f7b13361d74e1b1e276f9cc41e1379342999837f'),
  ('payment_2021_05_24','091209d4bf7c1a3a59990cca5e62ba22e2f3efd968f1a5aa5173cc62b5729f34'),
  ('payment_2021_06_28','428dbf03c356ddde0ddcae609980b4fd25691d9fe16dc97a2851bc3caf630c4a'),
  ('payment_2021_07_26','99dc49521444e8407828ab0de630c32adc44d87182a1266424f0ae51a187a74a'),
  ('payment_2021_08_29','cbed28ac74254206e2792c958e72829e58ee36390d1847149522f5e9bedf1b3e'),
  ('payment_2021_09_27','d2d7a601b930722ff6c7c036a22a760f18c9b786bd79ec7118f100e4b79859b2'),
  ('payment_2021_10_25','0501a2ad9980262f46bfd5fb48d7a7feed00be3896698c784e03b5a7a8681357'),
  ('payment_2021_11_22','dfa5f400e0a13d0fb12191c587cc3b786506bc3e1c9e795a9fc4f9821a981f23')
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
  'largest-input path with tx-id/output-index tie-break; not exclusive provenance'::text
    AS method_note
FROM hop h
JOIN public.tx t ON t.id = h.tx_id
JOIN public.block b ON b.id = t.block_id
LEFT JOIN public.stake_address sa ON sa.id = h.source_stake_address_id
CROSS JOIN tip
ORDER BY h.seed_label, h.depth;
SQL

for name in \
  genesis_trail_recipient_outputs \
  genesis_trail_payment_inputs \
  genesis_trail_recipient_forwarding \
  genesis_trail_hub_summary \
  genesis_trail_stream_bridges \
  genesis_trail_payment_dominant_traces
do
  echo "wrote ${OUT_DIR#$REPO_ROOT/}/$name.csv"
done

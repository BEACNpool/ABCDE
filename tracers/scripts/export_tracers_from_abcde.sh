#!/usr/bin/env bash
# Export the exchange-tracer dataset from the ABCDE warehouse (maintainer-only).
#
# Runs read-only SQL against the cexplorer_replica db-sync schema over SSH and
# writes deterministic CSVs into tracers/data/, then hashes them into
# tracers/data/SHA256SUMS. Public users do not need to run this — the committed
# CSVs are the reproducibility cut; this script is how the maintainer refreshes
# them.
#
# Important ABCDE quirk: UTxO liveness must use tx_in anti-joins. Do NOT rely
# on tx_out.consumed_by_tx_id on the logical subscriber.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="$REPO_DIR/data"
POLICY_ID="d8d5539ee11f21a6748735aeb69d3ed935bb14570f57709279031119"
PSQL='sudo -u postgres psql -d cexplorer_replica -q -v ON_ERROR_STOP=1'

mkdir -p "$OUT_DIR"

run_copy() {
  local out_file="$1"
  ssh abcde "$PSQL" >"$out_file"
  echo "wrote $out_file ($(wc -l <"$out_file") lines)"
}

# Shared CTE: every output row that ever carried a tracer asset.
TRACER_OUTPUTS_CTE="
with tracer_outputs as (
  select
    ma.id as ma_id,
    encode(ma.policy, 'hex') as policy_id,
    encode(ma.name, 'escape') as asset_name,
    encode(ma.name, 'hex') as asset_name_hex,
    ma.fingerprint,
    mto.quantity,
    txo.index as tx_out_index,
    txo.address,
    txo.address_has_script,
    coalesce(sa.view, '') as stake_address,
    encode(tx.hash, 'hex') as tx_hash,
    tx.id as tx_id,
    b.block_no,
    b.time as block_time,
    not exists (
      select 1 from public.tx_in i
      where i.tx_out_id = tx.id and i.tx_out_index = txo.index
    ) as is_unspent
  from public.multi_asset ma
  join public.ma_tx_out mto on mto.ident = ma.id
  join public.tx_out txo on txo.id = mto.tx_out_id
  join public.tx tx on tx.id = txo.tx_id
  join public.block b on b.id = tx.block_id
  left join public.stake_address sa on sa.id = txo.stake_address_id
  where encode(ma.policy, 'hex') = '$POLICY_ID'
)"

# 0. Snapshot receipt: warehouse tip at export time (provenance for every CSV).
run_copy "$OUT_DIR/export_tip_receipt.csv" <<SQL
copy (
  select max(block_no) as tip_block_no, max(time) as tip_block_time,
         '$POLICY_ID' as policy_id, now() at time zone 'utc' as exported_at_utc
  from public.block
) to stdout with csv header;
SQL

# 1. Per-address summary (ever touched vs currently holding).
run_copy "$OUT_DIR/address_summary.csv" <<SQL
copy (
$TRACER_OUTPUTS_CTE
select
  address,
  stake_address,
  bool_or(address_has_script) as address_has_script,
  count(distinct asset_name) as distinct_tracers_ever,
  count(distinct asset_name) filter (where is_unspent) as distinct_tracers_now,
  count(*) as output_rows,
  min(block_time) as first_seen,
  max(block_time) as last_seen,
  array_to_string(array_agg(distinct asset_name order by asset_name) filter (where is_unspent), ';') as current_assets
from tracer_outputs
group by address, stake_address
order by distinct_tracers_now desc, distinct_tracers_ever desc, first_seen
) to stdout with csv header;
SQL

# 2. Per-stake-address rollup (entity-level view; empty stake = enterprise/no staking part).
run_copy "$OUT_DIR/stake_summary.csv" <<SQL
copy (
$TRACER_OUTPUTS_CTE
select
  stake_address,
  count(distinct address) as payment_addresses,
  count(distinct asset_name) as distinct_tracers_ever,
  count(distinct asset_name) filter (where is_unspent) as distinct_tracers_now,
  count(*) as output_rows,
  min(block_time) as first_seen,
  max(block_time) as last_seen
from tracer_outputs
group by stake_address
order by distinct_tracers_now desc, distinct_tracers_ever desc, first_seen
) to stdout with csv header;
SQL

# 3. Current (unspent) tracer UTxOs.
run_copy "$OUT_DIR/current_tracer_utxos.csv" <<SQL
copy (
$TRACER_OUTPUTS_CTE
select
  policy_id, asset_name, asset_name_hex, fingerprint, quantity,
  address, address_has_script, stake_address,
  tx_hash, tx_out_index, block_no, block_time
from tracer_outputs
where is_unspent
order by block_time desc, asset_name
) to stdout with csv header;
SQL

# 4. Full historical output rows for the policy.
run_copy "$OUT_DIR/all_tracer_outputs.csv" <<SQL
copy (
$TRACER_OUTPUTS_CTE
select
  policy_id, asset_name, asset_name_hex, fingerprint, quantity,
  tx_out_index, address, address_has_script, stake_address,
  tx_hash, block_no, block_time, is_unspent
from tracer_outputs
order by block_time, tx_hash, tx_out_index, asset_name
) to stdout with csv header;
SQL

# 5. Per-asset current location + lifetime stats (one row per tracer NFT).
run_copy "$OUT_DIR/asset_current_location.csv" <<SQL
copy (
$TRACER_OUTPUTS_CTE
select
  asset_name,
  asset_name_hex,
  fingerprint,
  min(block_time) as minted_at,
  count(*) as output_rows,
  count(distinct address) as addresses_touched,
  max(address) filter (where is_unspent) as current_address,
  max(stake_address) filter (where is_unspent) as current_stake_address,
  max(tx_hash) filter (where is_unspent) as current_tx_hash,
  max(block_time) filter (where is_unspent) as at_current_location_since
from tracer_outputs
group by asset_name, asset_name_hex, fingerprint
order by asset_name
) to stdout with csv header;
SQL

# 6. Transfer edges: every (asset, from_address -> to_address) hop, one row per
#    spend of a tracer-carrying output into a new tracer-carrying output.
run_copy "$OUT_DIR/transfer_edges.csv" <<SQL
copy (
$TRACER_OUTPUTS_CTE
select
  o.asset_name,
  o.fingerprint,
  o.address as from_address,
  o.stake_address as from_stake_address,
  dtxo.address as to_address,
  coalesce(dsa.view, '') as to_stake_address,
  encode(stx.hash, 'hex') as spend_tx_hash,
  db.block_no,
  db.time as block_time
from tracer_outputs o
join public.tx_in i on i.tx_out_id = o.tx_id and i.tx_out_index = o.tx_out_index
join public.tx stx on stx.id = i.tx_in_id
join public.block db on db.id = stx.block_id
join public.tx_out dtxo on dtxo.tx_id = stx.id
join public.ma_tx_out dmto on dmto.tx_out_id = dtxo.id and dmto.ident = o.ma_id
left join public.stake_address dsa on dsa.id = dtxo.stake_address_id
order by db.time, spend_tx_hash, o.asset_name
) to stdout with csv header;
SQL

# 7. Mint events with the asset's OWN CIP-25 entry.
#    Only the per-asset slice is carried here. A tracer mint tx stamps one 721
#    blob covering every asset it mints, so joining the whole blob onto each
#    asset repeated ~7 KB of identical JSON 505 times (4 MB in a cut whose point
#    is being small). The full blobs are in mint_tx_metadata.csv, deduped.
run_copy "$OUT_DIR/mint_events.csv" <<SQL
copy (
select
  encode(ma.policy, 'hex') as policy_id,
  encode(ma.name, 'escape') as asset_name,
  encode(ma.name, 'hex') as asset_name_hex,
  ma.fingerprint,
  mtm.quantity,
  encode(tx.hash, 'hex') as mint_tx,
  b.block_no,
  b.time as block_time,
  tm.key as metadata_key,
  (tm.json -> encode(ma.policy, 'hex') -> encode(ma.name, 'escape'))::text
    as asset_metadata_json
from public.multi_asset ma
join public.ma_tx_mint mtm on mtm.ident = ma.id
join public.tx tx on tx.id = mtm.tx_id
join public.block b on b.id = tx.block_id
left join public.tx_metadata tm on tm.tx_id = tx.id
where encode(ma.policy, 'hex') = '$POLICY_ID'
order by b.time, ma.name
) to stdout with csv header;
SQL

# 7b. The full on-chain metadata blob per mint transaction, one row each.
run_copy "$OUT_DIR/mint_tx_metadata.csv" <<SQL
copy (
with mint_txs as (
  select distinct mtm.tx_id
  from public.multi_asset ma
  join public.ma_tx_mint mtm on mtm.ident = ma.id
  where encode(ma.policy, 'hex') = '$POLICY_ID'
)
select
  encode(tx.hash, 'hex') as mint_tx,
  b.block_no,
  b.time as block_time,
  tm.key as metadata_key,
  tm.json::text as metadata_json
from mint_txs m
join public.tx tx on tx.id = m.tx_id
join public.block b on b.id = tx.block_id
join public.tx_metadata tm on tm.tx_id = m.tx_id
order by b.time, mint_tx, tm.key
) to stdout with csv header;
SQL

# 8. Mint funding inputs: which addresses funded each mint tx (the tracer
#    operator's wallets — on-chain linkage only, not identity).
run_copy "$OUT_DIR/mint_funding_inputs.csv" <<SQL
copy (
with mint_txs as (
  select distinct mtm.tx_id
  from public.multi_asset ma
  join public.ma_tx_mint mtm on mtm.ident = ma.id
  where encode(ma.policy, 'hex') = '$POLICY_ID'
)
select distinct
  encode(tx.hash, 'hex') as mint_tx,
  b.block_no,
  b.time as block_time,
  prev_out.address as funding_address,
  coalesce(sa.view, '') as funding_stake_address
from mint_txs m
join public.tx tx on tx.id = m.tx_id
join public.block b on b.id = tx.block_id
join public.tx_in i on i.tx_in_id = m.tx_id
join public.tx_out prev_out
  on prev_out.tx_id = i.tx_out_id and prev_out.index = i.tx_out_index
left join public.stake_address sa on sa.id = prev_out.stake_address_id
order by b.time, mint_tx, funding_address
) to stdout with csv header;
SQL

# 9. Daily movement timeline.
run_copy "$OUT_DIR/movement_timeline.csv" <<SQL
copy (
$TRACER_OUTPUTS_CTE
select
  block_time::date as day,
  count(*) as output_rows,
  count(distinct asset_name) as distinct_assets,
  count(distinct address) as distinct_addresses,
  count(distinct tx_hash) as distinct_txs
from tracer_outputs
group by block_time::date
order by day
) to stdout with csv header;
SQL

# 10. On-chain deposit claims: tx metadata (674 msg / 1985) attached to txs
#     that moved tracer assets — includes the senders' own
#     "Deposited to: <Exchange>" labels. Self-reported claims, not proof.
run_copy "$OUT_DIR/deposit_claims.csv" <<SQL
copy (
$TRACER_OUTPUTS_CTE
select
  encode(tx.hash, 'hex') as tx_hash,
  b.block_no,
  b.time as block_time,
  tm.key as metadata_key,
  tm.json::text as metadata_json,
  count(distinct o.asset_name) as tracer_assets_in_tx,
  array_to_string(array_agg(distinct o.asset_name order by o.asset_name), ';') as assets,
  array_to_string(array_agg(distinct o.address order by o.address), ';') as tracer_output_addresses
from tracer_outputs o
join public.tx tx on tx.id = o.tx_id
join public.block b on b.id = tx.block_id
join public.tx_metadata tm on tm.tx_id = o.tx_id
where tm.key in (674, 1985)
group by tx.hash, b.block_no, b.time, tm.key, tm.json::text
order by b.time, tx_hash
) to stdout with csv header;
SQL

# ---------------------------------------------------------------------------
# Canonical study method (docs/26_EXCHANGE_TRACER_METHOD.md)
#
# Sections 11-16 implement the reconstruction rules published by the study
# operator: deterministic wallet-cluster keys, strict deposit validation, exact
# NFT paths, terminus grouping, and participant-vote name resolution. They are
# deliberately stricter than the raw claim rows in section 10.
# ---------------------------------------------------------------------------

# pos  = the exact ordered holder path of every tracer (one row per asset-bearing output)
# dep  = deposits that pass ALL four validation rules
# term = each tracer's current terminus (its unspent position)
METHOD_CTE="
with pos as (
  select p.*,
         row_number() over w as hop,
         lag(cluster_key) over w as prev_cluster_key,
         lag(address) over w as prev_address
  from (
    select
      ma.id as ma_id,
      encode(ma.name, 'escape') as asset_name,
      encode(ma.name, 'hex') as asset_name_hex,
      ma.fingerprint,
      txo.index as tx_out_index,
      txo.address,
      coalesce(sa.view, '') as stake_address,
      case when coalesce(sa.view, '') <> '' then 's:' || sa.view else 'a:' || txo.address end as cluster_key,
      tx.id as tx_id,
      encode(tx.hash, 'hex') as tx_hash,
      tx.block_index,
      b.block_no,
      b.time as block_time,
      not exists (
        select 1 from public.tx_in i
        where i.tx_out_id = tx.id and i.tx_out_index = txo.index
      ) as is_unspent
    from public.multi_asset ma
    join public.ma_tx_out mto on mto.ident = ma.id
    join public.tx_out txo on txo.id = mto.tx_out_id
    join public.tx tx on tx.id = txo.tx_id
    join public.block b on b.id = tx.block_id
    left join public.stake_address sa on sa.id = txo.stake_address_id
    where ma.policy = decode('$POLICY_ID', 'hex')
      and mto.quantity = 1
  ) p
  window w as (partition by asset_name order by block_no, block_index, tx_out_index)
),
dep as (
  select
    p.asset_name,
    p.asset_name_hex,
    p.fingerprint,
    p.tx_hash as deposit_tx,
    p.tx_out_index as deposit_output_index,
    p.block_no as deposit_block_no,
    p.block_time as deposit_time,
    p.hop as deposit_hop,
    p.cluster_key as deposit_cluster_key,
    p.address as deposit_address,
    p.stake_address as deposit_stake_address,
    p.prev_cluster_key as participant_key,
    p.prev_address as participant_address,
    btrim(coalesce(tm.json->'msg'->>1, '')) as claimed_exchange,
    lower(btrim(coalesce(tm.json->'msg'->>1, ''))) as claimed_exchange_norm,
    case when tm.json->'msg'->>1 is null then 'unparsed_msg' else 'msg_index_1' end as name_source,
    tm.json::text as deposit_msg_json
  from pos p
  join public.tx_metadata tm on tm.tx_id = p.tx_id and tm.key = 674
  where tm.json::text ilike '%Red (or Blue) Pill%'   -- rule 2: message identifies the study
    and p.tx_out_index = 0                            -- rule 3: tracer sits in output 0
    and p.prev_cluster_key is not null                -- rule 4: it moved ...
    and p.prev_cluster_key <> p.cluster_key           --         ... to a NEW cluster key
),
term as (
  select
    asset_name,
    cluster_key as terminus_key,
    address as terminus_address,
    stake_address as terminus_stake_address,
    tx_hash as terminus_tx,
    tx_out_index as terminus_output_index,
    block_no as terminus_block_no,
    block_time as terminus_time,
    hop as terminus_hop
  from pos
  where is_unspent
),
votes as (
  select
    t.terminus_key,
    d.claimed_exchange_norm,
    min(d.claimed_exchange) as claimed_exchange,
    count(distinct d.asset_name) as tracers,
    count(distinct d.participant_key) as participants
  from dep d
  join term t on t.asset_name = d.asset_name
  group by t.terminus_key, d.claimed_exchange_norm
),
ranked as (
  select v.*,
    max(participants) filter (where claimed_exchange_norm <> '')
      over (partition by terminus_key) as top_participants,
    count(*) filter (where claimed_exchange_norm <> '')
      over (partition by terminus_key) as named_claims
  from votes v
),
resolution as (
  select
    terminus_key,
    max(top_participants) as top_participants,
    max(named_claims) as named_claims,
    count(*) filter (where claimed_exchange_norm <> '' and participants = top_participants) as leaders,
    min(claimed_exchange) filter (where claimed_exchange_norm <> '' and participants = top_participants) as leader_name
  from ranked
  group by terminus_key
)"

# 11. Method receipt: the canonical identifiers and rules this cut was built with.
run_copy "$OUT_DIR/method_receipt.csv" <<SQL
copy (
  select
    '$POLICY_ID' as policy_id,
    '55bf845d5be91cf210e50511fc34ff35aad645f92290c13c5c3b4186' as policy_key_hash,
    'The Red (or Blue) Pill Study' as study_name,
    'tracer.adagenesistransparency.com' as study_site,
    223391762 as native_script_expiry_slot,
    (select max(slot_no) from public.block) as tip_slot_no,
    (select max(slot_no) from public.block) > 223391762 as mint_window_closed,
    674 as deposit_metadata_label,
    1985 as study_seed_metadata_label,
    2 as participant_threshold,
    'stake credential when present (s:), otherwise payment address (a:)' as node_key_rule,
    'exact-nft' as edge_type,
    'distinct pre-deposit wallet-cluster key' as participant_unit,
    (select max(block_no) from public.block) as tip_block_no,
    (select max(time) from public.block) as tip_block_time,
    now() at time zone 'utc' as exported_at_utc
) to stdout with csv header;
SQL

# 12. Exact NFT holder path: one row per asset-bearing output, in order.
#     same_cluster_as_prev = true marks a self-move (deduplicate these when
#     rendering a holder path; they are kept here so the raw chain is complete).
run_copy "$OUT_DIR/asset_path.csv" <<SQL
copy (
$METHOD_CTE
select
  p.asset_name,
  p.asset_name_hex,
  p.fingerprint,
  p.hop,
  p.cluster_key,
  p.address,
  p.stake_address,
  p.prev_cluster_key,
  (p.prev_cluster_key is not null and p.prev_cluster_key = p.cluster_key) as same_cluster_as_prev,
  p.tx_hash,
  p.tx_out_index,
  p.block_no,
  p.block_time,
  p.is_unspent as is_terminus,
  (d.asset_name is not null) as is_valid_deposit
from pos p
left join dep d on d.asset_name = p.asset_name and d.deposit_tx = p.tx_hash and d.deposit_hop = p.hop
order by p.asset_name, p.hop
) to stdout with csv header;
SQL

# 13. Validated tagged deposits (all four rules) + where that tracer is now.
run_copy "$OUT_DIR/valid_deposits.csv" <<SQL
copy (
$METHOD_CTE
select
  d.asset_name,
  d.asset_name_hex,
  d.fingerprint,
  d.deposit_tx,
  d.deposit_output_index,
  d.deposit_block_no,
  d.deposit_time,
  d.deposit_hop,
  d.claimed_exchange,
  d.claimed_exchange_norm,
  d.name_source,
  d.participant_key,
  d.participant_address,
  d.deposit_cluster_key,
  d.deposit_address,
  d.deposit_stake_address,
  t.terminus_key,
  t.terminus_address,
  t.terminus_tx,
  t.terminus_output_index,
  (t.terminus_hop - d.deposit_hop) as hops_deposit_to_terminus,
  d.deposit_msg_json
from dep d
join term t on t.asset_name = d.asset_name
order by d.deposit_time, d.deposit_tx, d.asset_name
) to stdout with csv header;
SQL

# 14. Name votes: per (terminus cluster, claimed name), tracers vs participants.
#     participants is the vote unit; tracers is only volume.
run_copy "$OUT_DIR/name_votes.csv" <<SQL
copy (
$METHOD_CTE
select
  r.terminus_key,
  r.claimed_exchange,
  r.claimed_exchange_norm,
  r.tracers,
  r.participants,
  (r.claimed_exchange_norm <> '' and r.participants >= 2) as corroborated,
  (r.claimed_exchange_norm <> '' and r.participants = r.top_participants and res.leaders = 1
     and r.top_participants >= 2) as is_resolved_name
from ranked r
join resolution res on res.terminus_key = r.terminus_key
order by r.terminus_key, r.participants desc, r.tracers desc, r.claimed_exchange_norm
) to stdout with csv header;
SQL

# 15. Terminus clusters reached by validated deposits, with the resolution rule
#     applied: a name resolves only on a UNIQUE participant-count lead that
#     clears the 2-participant threshold. Ties and thin claims stay unresolved.
run_copy "$OUT_DIR/terminus_clusters.csv" <<SQL
copy (
$METHOD_CTE
select
  t.terminus_key,
  max(t.terminus_address) filter (where t.terminus_stake_address = '') as terminus_address_if_no_stake,
  count(distinct d.asset_name) as tracers,
  count(distinct d.participant_key) as participants,
  count(distinct d.deposit_tx) as deposit_txs,
  min(d.deposit_time) as first_deposit,
  max(d.deposit_time) as last_deposit,
  max(res.named_claims) as distinct_names_claimed,
  (max(res.named_claims) > 1) as conflicted,
  max(res.top_participants) as top_participants,
  case
    when max(res.named_claims) = 0 then null
    when max(res.top_participants) < 2 then null
    when max(res.leaders) > 1 then null
    else max(res.leader_name)
  end as resolved_exchange,
  case
    when max(res.named_claims) = 0 then 'unresolved_no_named_claim'
    when max(res.top_participants) < 2 then 'unresolved_below_threshold'
    when max(res.leaders) > 1 then 'unresolved_tie'
    else 'resolved'
  end as resolution_status,
  (select count(*) from term t2 where t2.terminus_key = t.terminus_key) as tracers_at_terminus_total
from dep d
join term t on t.asset_name = d.asset_name
join resolution res on res.terminus_key = t.terminus_key
group by t.terminus_key
order by tracers desc, participants desc, t.terminus_key
) to stdout with csv header;
SQL

# 16. Terminus census over ALL tracers (the denominator): where every tracer
#     currently sits, tagged or not.
run_copy "$OUT_DIR/terminus_census.csv" <<SQL
copy (
$METHOD_CTE
select
  t.terminus_key,
  count(*) as tracers_now,
  count(d.asset_name) as tracers_from_validated_deposit,
  count(distinct d.participant_key) as participants,
  min(t.terminus_time) as first_arrival,
  max(t.terminus_time) as last_arrival,
  bool_or(t.terminus_stake_address = '') as has_enterprise_address,
  array_to_string(array_agg(distinct d.claimed_exchange) filter (where d.claimed_exchange is not null and d.claimed_exchange <> ''), ';') as claimed_names
from term t
left join dep d on d.asset_name = t.asset_name
group by t.terminus_key
order by tracers_now desc, t.terminus_key
) to stdout with csv header;
SQL

( cd "$OUT_DIR" && sha256sum *.csv >SHA256SUMS )

# Publish into the queryable compact cut (data/small/tracer_<name>.csv). The two
# copies must never drift: this is the only step that writes them.
SMALL_DIR="$(cd "$REPO_DIR/.." && pwd)/data/small"
for f in "$OUT_DIR"/*.csv; do
  base="$(basename "$f" .csv)"
  # two legacy tables were published under a reordered name — keep them stable
  case "$base" in
    all_tracer_outputs)   table="tracer_all_outputs" ;;
    current_tracer_utxos) table="tracer_current_utxos" ;;
    *)                    table="tracer_${base}" ;;
  esac
  # csv from psql is LF already; strip any CR so the public-artifact manifest
  # (which hashes the working copy) matches the LF bytes git stores.
  sed 's/\r$//' "$f" >"$SMALL_DIR/${table}.csv"
done
echo "published $(ls "$OUT_DIR"/*.csv | wc -l) tables into $SMALL_DIR as tracer_*.csv"

echo "---"
wc -l "$OUT_DIR"/*.csv

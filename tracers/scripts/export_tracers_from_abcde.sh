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

# 7. Mint events with on-chain CIP-25 metadata.
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
  tm.json::text as metadata_json
from public.multi_asset ma
join public.ma_tx_mint mtm on mtm.ident = ma.id
join public.tx tx on tx.id = mtm.tx_id
join public.block b on b.id = tx.block_id
left join public.tx_metadata tm on tm.tx_id = tx.id
where encode(ma.policy, 'hex') = '$POLICY_ID'
order by b.time, ma.name
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

( cd "$OUT_DIR" && sha256sum *.csv >SHA256SUMS )
echo "---"
wc -l "$OUT_DIR"/*.csv

-- Exchange tracer policy report.
-- Source: ABCDE cexplorer_replica public db-sync tables, read-only.
-- Policy: d8d5539ee11f21a6748735aeb69d3ed935bb14570f57709279031119
--
-- Important: use tx_in anti-joins for UTxO liveness on ABCDE. Do not rely on
-- tx_out.consumed_by_tx_id on the logical subscriber.

\set policy_id 'd8d5539ee11f21a6748735aeb69d3ed935bb14570f57709279031119'

with tracer_outputs as (
  select
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
      select 1
      from public.tx_in i
      where i.tx_out_id = tx.id
        and i.tx_out_index = txo.index
    ) as is_unspent
  from public.multi_asset ma
  join public.ma_tx_out mto on mto.ident = ma.id
  join public.tx_out txo on txo.id = mto.tx_out_id
  join public.tx tx on tx.id = txo.tx_id
  join public.block b on b.id = tx.block_id
  left join public.stake_address sa on sa.id = txo.stake_address_id
  where encode(ma.policy, 'hex') = :'policy_id'
),
address_summary as (
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
)
select *
from address_summary
order by distinct_tracers_now desc, distinct_tracers_ever desc, first_seen;

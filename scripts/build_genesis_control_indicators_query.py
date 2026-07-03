#!/usr/bin/env python3
"""Emit the genesis control-indicator extraction SQL (stdout).

The root set is the union of stake addresses in:
  - data/small/governance_genesis_behavior_clusters.csv  (genesis-descended
    behavior clusters from the founders depth-14 staged trace)
  - data/small/iog_current_bag_depth14_top_stake.csv     (top current-value
    stake addresses in the IOG depth-14 bag)

For each stake address the query returns live-tip custody indicators:
activity recency, current holdings, staking/DRep certificate state, reward
withdrawal behavior. These are signals for the deterministic classifier in
build_genesis_control_classification.py — they are not ownership claims.

Usage: build_genesis_control_indicators_query.py [--cohorts]
  default   emit the per-stake-address indicator query
  --cohorts emit the shared-certificate-tx cohort query instead
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLUSTERS = ROOT / "data/small/governance_genesis_behavior_clusters.csv"
TOP_STAKE = ROOT / "data/small/iog_current_bag_depth14_top_stake.csv"


def root_set() -> list[str]:
    keys: set[str] = set()
    for path, col in ((CLUSTERS, "stake_address"), (TOP_STAKE, "stake_address")):
        with path.open() as f:
            for row in csv.DictReader(f):
                v = (row.get(col) or "").strip()
                if v.startswith("stake1"):
                    keys.add(v)
    return sorted(keys)


def values_clause(keys: list[str]) -> str:
    return ",\n    ".join(f"('{k}')" for k in keys)


COMMON = """\
with set_keys(stake_address) as (
  values
    {values}
),
sa as (
  select s.id, s.view
  from public.stake_address s
  join set_keys k on k.stake_address = s.view
)"""

INDICATORS = """\
,
activity as (
  select
    txo.stake_address_id as sa_id,
    count(*) as total_output_rows,
    count(*) filter (where i.tx_out_id is null) as current_utxos,
    coalesce(sum(txo.value) filter (where i.tx_out_id is null), 0) as current_lovelace,
    min(cb.time) as first_received_time,
    max(cb.time) as last_received_time,
    max(sb.time) as last_outgoing_time
  from public.tx_out txo
  join sa on sa.id = txo.stake_address_id
  join public.tx ct on ct.id = txo.tx_id
  join public.block cb on cb.id = ct.block_id
  left join public.tx_in i
    on i.tx_out_id = txo.tx_id and i.tx_out_index = txo.index
  left join public.tx st on st.id = i.tx_in_id
  left join public.block sb on sb.id = st.block_id
  group by txo.stake_address_id
),
deleg as (
  select
    d.addr_id as sa_id,
    count(*) as pool_delegation_certs,
    max(d.active_epoch_no) as latest_pool_active_epoch
  from public.delegation d
  join sa on sa.id = d.addr_id
  group by d.addr_id
),
deleg_latest as (
  select distinct on (d.addr_id)
    d.addr_id as sa_id,
    ph.view as current_pool_bech32,
    b.time as latest_pool_cert_time
  from public.delegation d
  join sa on sa.id = d.addr_id
  join public.pool_hash ph on ph.id = d.pool_hash_id
  join public.tx tx on tx.id = d.tx_id
  join public.block b on b.id = tx.block_id
  order by d.addr_id, d.tx_id desc
),
dv_all as materialized (
  select dv.addr_id, dv.tx_id, dv.drep_hash_id
  from public.delegation_vote dv
  join sa on sa.id = dv.addr_id
),
dv_latest as (
  select distinct on (v.addr_id)
    v.addr_id as sa_id,
    coalesce(dh.view, 'UNKNOWN') as current_drep,
    b.time as latest_drep_cert_time
  from dv_all v
  join public.drep_hash dh on dh.id = v.drep_hash_id
  join public.tx tx on tx.id = v.tx_id
  join public.block b on b.id = tx.block_id
  order by v.addr_id, v.tx_id desc
),
dv_counts as (
  select addr_id as sa_id, count(*) as drep_delegation_certs
  from dv_all group by addr_id
),
regs as (
  select r.addr_id as sa_id, max(r.tx_id) as last_reg_tx
  from public.stake_registration r join sa on sa.id = r.addr_id
  group by r.addr_id
),
deregs as (
  select r.addr_id as sa_id, max(r.tx_id) as last_dereg_tx
  from public.stake_deregistration r join sa on sa.id = r.addr_id
  group by r.addr_id
),
rew as (
  select r.addr_id as sa_id,
         sum(r.amount) as rewards_earned_lovelace,
         max(r.spendable_epoch) as last_reward_spendable_epoch
  from public.reward r join sa on sa.id = r.addr_id
  group by r.addr_id
),
wdr as (
  select w.addr_id as sa_id,
         count(*) as withdrawal_count,
         sum(w.amount) as withdrawn_lovelace,
         max(b.time) as last_withdrawal_time
  from public.withdrawal w
  join sa on sa.id = w.addr_id
  join public.tx tx on tx.id = w.tx_id
  join public.block b on b.id = tx.block_id
  group by w.addr_id
)
select
  sa.view as stake_address,
  coalesce(a.total_output_rows, 0) as total_output_rows,
  coalesce(a.current_utxos, 0) as current_utxos,
  round(coalesce(a.current_lovelace, 0) / 1e6, 6) as current_ada,
  a.first_received_time,
  a.last_received_time,
  a.last_outgoing_time,
  case
    when dr.last_dereg_tx is null and rg.last_reg_tx is not null then true
    when dr.last_dereg_tx is not null and rg.last_reg_tx is not null
      then rg.last_reg_tx > dr.last_dereg_tx
    else false
  end as stake_key_registered,
  coalesce(d.pool_delegation_certs, 0) as pool_delegation_certs,
  dl.current_pool_bech32,
  dl.latest_pool_cert_time,
  d.latest_pool_active_epoch,
  coalesce(dc.drep_delegation_certs, 0) as drep_delegation_certs,
  dvl.current_drep,
  dvl.latest_drep_cert_time,
  round(coalesce(rw.rewards_earned_lovelace, 0) / 1e6, 6) as rewards_earned_ada,
  rw.last_reward_spendable_epoch,
  coalesce(w.withdrawal_count, 0) as withdrawal_count,
  round(coalesce(w.withdrawn_lovelace, 0) / 1e6, 6) as rewards_withdrawn_ada,
  w.last_withdrawal_time,
  round((coalesce(rw.rewards_earned_lovelace, 0) - coalesce(w.withdrawn_lovelace, 0)) / 1e6, 6)
    as rewards_unclaimed_ada
from sa
left join activity a on a.sa_id = sa.id
left join deleg d on d.sa_id = sa.id
left join deleg_latest dl on dl.sa_id = sa.id
left join dv_latest dvl on dvl.sa_id = sa.id
left join dv_counts dc on dc.sa_id = sa.id
left join regs rg on rg.sa_id = sa.id
left join deregs dr on dr.sa_id = sa.id
left join rew rw on rw.sa_id = sa.id
left join wdr w on w.sa_id = sa.id
order by current_ada desc, sa.view;"""

COHORTS = """\
,
cert_events as materialized (
  select 'pool_delegation'::text as cert_type, d.tx_id, d.addr_id
  from public.delegation d join sa on sa.id = d.addr_id
  union all
  select 'vote_delegation', dv.tx_id, dv.addr_id
  from public.delegation_vote dv join sa on sa.id = dv.addr_id
  union all
  select 'withdrawal', w.tx_id, w.addr_id
  from public.withdrawal w join sa on sa.id = w.addr_id
  union all
  select 'stake_registration', r.tx_id, r.addr_id
  from public.stake_registration r join sa on sa.id = r.addr_id
)
select
  c.cert_type,
  encode(tx.hash, 'hex') as tx_hash,
  b.block_no,
  b.time as block_time,
  count(distinct c.addr_id) as set_member_count,
  array_to_string(array_agg(distinct s2.view order by s2.view), ';') as set_members
from cert_events c
join sa s2 on s2.id = c.addr_id
join public.tx tx on tx.id = c.tx_id
join public.block b on b.id = tx.block_id
group by c.cert_type, tx.hash, b.block_no, b.time
having count(distinct c.addr_id) >= 2
order by set_member_count desc, b.time;"""


def main() -> None:
    keys = root_set()
    if not keys:
        raise SystemExit("empty root set — check source CSVs")
    body = COHORTS if "--cohorts" in sys.argv[1:] else INDICATORS
    sys.stdout.write(COMMON.format(values=values_clause(keys)) + body + "\n")
    print(f"-- root set: {len(keys)} stake addresses", file=sys.stderr)


if __name__ == "__main__":
    main()

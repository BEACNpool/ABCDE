-- F11 receipt 7: where the reward-plumbing value goes, hops 1-3.
-- Hop 1 = outputs of exit txs; hop 2/3 = outputs of the txs that spend the
-- previous hop's outputs. Aggregated by destination stake key (or enterprise
-- address when no stake part). NOTE: from hop 2 onward these are tx-output
-- aggregates along the path — unrelated value joining those transactions is
-- included; no taint accounting is claimed. Destinations below 10,000 ADA
-- cumulative are dropped; top 300 per hop.
with cohort(stake_address) as (values
  ('stake1u84u9k7yjnujla4stf25q23r0tcxyj0stmzadwam4k98g3s0euwyc'),
  ('stake1u9j7tecyajslj3lk9pmnrd9456fpfdsnqufpd6vmnwqzg2qkzjl27'),
  ('stake1u9ku4ja8eeens3hxmq26f53v6ujlymz6apyyfhm9g5rpvvqtur40t'),
  ('stake1u9xs3xep7gyjxpxrfv0el7xm2gctntk88ax789zcrlwue3c2xzevu'),
  ('stake1ux47d7aa3l8vk2pf0v6jlj39t00y7lagf68pewgw2cxkcasfmqr5h'),
  ('stake1uxasl8h59m07npqm2fvf7jnfh4etfpufxnpr3d7wzx2nuzqfvwhyv'),
  ('stake1uyclu4dwn93kvnn786x35efaj5nnfa05dd6w92fjgn6nwxcdg7hpg'),
  ('stake1uylhqtxx5ng4tawhcs9n7jgls0mm3q7ely5r565mdz2upqqw8f05q')
),
sa as (
  select s.id from public.stake_address s
  join cohort c on c.stake_address = s.view
),
wtx as (
  select distinct w.tx_id from public.withdrawal w
  join sa on sa.id = w.addr_id
),
hop1_txs as (
  select distinct i.tx_in_id as tx_id
  from wtx
  join public.tx_out o on o.tx_id = wtx.tx_id
  join public.tx_in i on i.tx_out_id = o.tx_id and i.tx_out_index = o.index
  where i.tx_in_id not in (select tx_id from wtx)
),
hop1_out as (
  select o.tx_id, o.index, o.value, o.address, o.stake_address_id
  from hop1_txs h join public.tx_out o on o.tx_id = h.tx_id
),
hop2_txs as (
  select distinct i.tx_in_id as tx_id
  from hop1_out o
  join public.tx_in i on i.tx_out_id = o.tx_id and i.tx_out_index = o.index
  where i.tx_in_id not in (select tx_id from wtx)
    and i.tx_in_id not in (select tx_id from hop1_txs)
),
hop2_out as (
  select o.tx_id, o.index, o.value, o.address, o.stake_address_id
  from hop2_txs h join public.tx_out o on o.tx_id = h.tx_id
),
hop3_txs as (
  select distinct i.tx_in_id as tx_id
  from hop2_out o
  join public.tx_in i on i.tx_out_id = o.tx_id and i.tx_out_index = o.index
  where i.tx_in_id not in (select tx_id from wtx)
    and i.tx_in_id not in (select tx_id from hop1_txs)
    and i.tx_in_id not in (select tx_id from hop2_txs)
),
hop3_out as (
  select o.tx_id, o.index, o.value, o.address, o.stake_address_id
  from hop3_txs h join public.tx_out o on o.tx_id = h.tx_id
),
all_hops as (
  select 1 as hop, * from hop1_out
  union all select 2, * from hop2_out
  union all select 3, * from hop3_out
),
agg as (
  select
    hop,
    coalesce(s2.view, a.address) as destination,
    (s2.view is null) as enterprise_only,
    count(distinct a.tx_id) as txs,
    count(*) as outputs,
    round(sum(a.value) / 1e6, 6) as total_ada
  from all_hops a
  left join public.stake_address s2 on s2.id = a.stake_address_id
  group by hop, coalesce(s2.view, a.address), (s2.view is null)
  having sum(a.value) >= 10000 * 1e6
),
ranked as (
  select *, row_number() over (partition by hop order by total_ada desc) as rn
  from agg
)
select hop, destination, enterprise_only, txs, outputs, total_ada
from ranked
where rn <= 300
order by hop, total_ada desc;

-- F11 receipt 5: where do the swept rewards go? Outputs of all cohort
-- withdrawal txs, grouped by destination stake key / enterprise flag.
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
  select s.id, s.view
  from public.stake_address s
  join cohort c on c.stake_address = s.view
),
wtx as (
  select distinct w.tx_id
  from public.withdrawal w
  join sa on sa.id = w.addr_id
)
select
  coalesce(s2.view, 'ENTERPRISE_NO_STAKE') as destination_stake_address,
  count(distinct o.tx_id) as txs,
  count(*) as outputs,
  round(sum(o.value) / 1e6, 6) as total_ada,
  min(o.tx_id) as first_tx_id,
  max(o.tx_id) as last_tx_id
from wtx
join public.tx_out o on o.tx_id = wtx.tx_id
left join public.stake_address s2 on s2.id = o.stake_address_id
group by coalesce(s2.view, 'ENTERPRISE_NO_STAKE')
order by total_ada desc
limit 25;

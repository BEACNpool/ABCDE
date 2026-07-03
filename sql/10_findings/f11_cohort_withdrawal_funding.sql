-- F11 receipt 1: who funds the withdrawal transactions of the 8x35M cohort?
-- Per cohort key: how many withdrawal txs, how many include an input from the
-- key's own addresses, and how many distinct external stake keys ever funded
-- them. Then the ranked external funders (cohort_keys_served = 8 would show a
-- single operator wallet paying fees for the whole cohort).
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
  select w.addr_id, w.tx_id
  from public.withdrawal w
  join sa on sa.id = w.addr_id
),
inputs as (
  select wtx.addr_id, wtx.tx_id, prev.stake_address_id as in_stake_id
  from wtx
  join public.tx_in i on i.tx_in_id = wtx.tx_id
  join public.tx_out prev
    on prev.tx_id = i.tx_out_id and prev.index = i.tx_out_index
)
select
  sa.view as stake_address,
  count(distinct i.tx_id) as withdrawal_txs,
  count(distinct i.tx_id) filter (where i.in_stake_id = i.addr_id)
    as txs_with_self_funded_input,
  count(distinct i.in_stake_id) filter (where i.in_stake_id is distinct from i.addr_id)
    as distinct_external_funding_stakes
from inputs i
join sa on sa.id = i.addr_id
group by sa.view
order by sa.view;

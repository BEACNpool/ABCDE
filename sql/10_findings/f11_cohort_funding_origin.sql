-- F11 receipt 3: where did each cohort key's first funding come from?
-- For each cohort key's two earliest funding txs: the tx, its time, and the
-- input addresses/stake keys that paid it. A shared input credential across
-- keys is FACT-grade common construction at funding time.
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
firsts as (
  select
    txo.stake_address_id as sa_id,
    txo.tx_id,
    dense_rank() over (partition by txo.stake_address_id order by txo.tx_id) as rn
  from public.tx_out txo
  join sa on sa.id = txo.stake_address_id
)
select distinct
  sa.view as stake_address,
  f.rn as funding_tx_rank,
  encode(t.hash, 'hex') as funding_tx,
  b.block_no,
  b.time as block_time,
  prev.address as input_address,
  coalesce(s2.view, '') as input_stake_address
from firsts f
join sa on sa.id = f.sa_id
join public.tx t on t.id = f.tx_id
join public.block b on b.id = t.block_id
join public.tx_in i on i.tx_in_id = f.tx_id
join public.tx_out prev
  on prev.tx_id = i.tx_out_id and prev.index = i.tx_out_index
left join public.stake_address s2 on s2.id = prev.stake_address_id
where f.rn <= 2
order by sa.view, f.rn, input_address;

-- F11 receipt 6: the wider operator fleet revealed by the reward plumbing.
-- An "exit tx" spends a cohort withdrawal-tx output but is not itself a
-- cohort withdrawal tx. If an exit tx also withdraws rewards for another
-- stake key, the same wallet built both flows at that moment — FACT-grade
-- shared construction. One row per non-cohort stake key so serviced.
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
exit_txs as (
  select distinct i.tx_in_id as tx_id
  from wtx
  join public.tx_out o on o.tx_id = wtx.tx_id
  join public.tx_in i on i.tx_out_id = o.tx_id and i.tx_out_index = o.index
  where i.tx_in_id not in (select tx_id from wtx)
)
select
  s2.view as stake_address,
  count(distinct w2.tx_id) as shared_withdrawal_txs,
  round(sum(w2.amount) / 1e6, 6) as rewards_withdrawn_ada,
  min(b.time) as first_shared_tx_time,
  max(b.time) as last_shared_tx_time
from exit_txs e
join public.withdrawal w2 on w2.tx_id = e.tx_id
join public.stake_address s2 on s2.id = w2.addr_id
join public.tx t on t.id = e.tx_id
join public.block b on b.id = t.block_id
where w2.addr_id not in (select id from sa)
group by s2.view
order by rewards_withdrawn_ada desc;

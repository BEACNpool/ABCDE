-- F11 receipt 4: every staking/governance certificate of the 8x35M cohort,
-- with tx hashes and timestamps — the burst-timing evidence.
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
certs as (
  select sa.view as stake_address, 'stake_registration'::text as cert_type,
         r.tx_id, ''::text as target
  from public.stake_registration r join sa on sa.id = r.addr_id
  union all
  select sa.view, 'pool_delegation', d.tx_id, ph.view
  from public.delegation d
  join sa on sa.id = d.addr_id
  join public.pool_hash ph on ph.id = d.pool_hash_id
  union all
  select sa.view, 'vote_delegation', dv.tx_id, dh.view
  from public.delegation_vote dv
  join sa on sa.id = dv.addr_id
  join public.drep_hash dh on dh.id = dv.drep_hash_id
)
select
  c.stake_address,
  c.cert_type,
  c.target,
  encode(t.hash, 'hex') as tx_hash,
  b.block_no,
  b.time as block_time
from certs c
join public.tx t on t.id = c.tx_id
join public.block b on b.id = t.block_id
order by b.time, c.stake_address;

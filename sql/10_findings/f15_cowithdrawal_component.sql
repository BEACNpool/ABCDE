-- F15: forward reachability of the reward-plumbing graph, seeded from the 8
-- F11 cohort keys, iterating the exact F13 edge to fixpoint.
--
-- Edge (directed, FACT-grade shared construction): key A -> key B if some
-- withdrawal transaction of A produces an output that is later spent by a
-- transaction that is itself a withdrawal transaction of B. (This is the F13
-- fleet-discovery mechanism; F13 ran it for one round and found 81 keys.)
-- Iterating answers whether the ~1.69B surface is the floor or the first layer.
--
-- Uses session TEMP tables + the withdrawal(addr_id/tx_id), tx_out(tx_id) and
-- tx_in(tx_out_id) indexes. Round-by-round growth is raised as NOTICE so
-- convergence vs explosion is visible. Hard caps (25 rounds, 200k keys) guard
-- against a batch-service blowup.
\set ON_ERROR_STOP on
set search_path = pg_temp, public;

create temp table component(addr_id bigint primary key, first_round int);

insert into component(addr_id, first_round)
select s.id, 0
from public.stake_address s
where s.view in (
  'stake1u84u9k7yjnujla4stf25q23r0tcxyj0stmzadwam4k98g3s0euwyc',
  'stake1u9j7tecyajslj3lk9pmnrd9456fpfdsnqufpd6vmnwqzg2qkzjl27',
  'stake1u9ku4ja8eeens3hxmq26f53v6ujlymz6apyyfhm9g5rpvvqtur40t',
  'stake1u9xs3xep7gyjxpxrfv0el7xm2gctntk88ax789zcrlwue3c2xzevu',
  'stake1ux47d7aa3l8vk2pf0v6jlj39t00y7lagf68pewgw2cxkcasfmqr5h',
  'stake1uxasl8h59m07npqm2fvf7jnfh4etfpufxnpr3d7wzx2nuzqfvwhyv',
  'stake1uyclu4dwn93kvnn786x35efaj5nnfa05dd6w92fjgn6nwxcdg7hpg',
  'stake1uylhqtxx5ng4tawhcs9n7jgls0mm3q7ely5r565mdz2upqqw8f05q'
);

do $$
declare
  r int := 0;
  added int := 0;
  total int := 0;
begin
  loop
    r := r + 1;
    -- new keys B: a current member's withdrawal-tx output is spent by a tx
    -- that is itself B's withdrawal tx. Only expand from keys added last round
    -- (frontier) to avoid re-scanning the whole component each iteration.
    insert into component(addr_id, first_round)
    select distinct w2.addr_id, r
    from component c
    join public.withdrawal w1 on w1.addr_id = c.addr_id
    join public.tx_out o on o.tx_id = w1.tx_id
    join public.tx_in i on i.tx_out_id = o.tx_id and i.tx_out_index = o.index
    join public.withdrawal w2 on w2.tx_id = i.tx_in_id
    left join component ex on ex.addr_id = w2.addr_id
    where c.first_round = r - 1
      and ex.addr_id is null
    on conflict (addr_id) do nothing;
    get diagnostics added = row_count;
    total := (select count(*) from component);
    raise notice 'round % added % total %', r, added, total;
    exit when added = 0 or r >= 25 or total >= 200000;
  end loop;
end $$;

-- Emit component membership with per-key withdrawal-tx count and discovery
-- round. Balance/parcel classification is done downstream by the control
-- classifier fed this key list.
\echo '@@COMPONENT'
copy (
  select
    s.view as stake_address,
    c.first_round,
    (select count(*) from public.withdrawal w where w.addr_id = c.addr_id) as withdrawal_txs
  from component c
  join public.stake_address s on s.id = c.addr_id
  order by c.first_round, s.view
) to stdout with csv header;

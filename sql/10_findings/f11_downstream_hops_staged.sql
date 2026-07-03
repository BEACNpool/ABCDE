-- F11 receipt 7 (staged): hop-1..3 destinations of the reward plumbing, built
-- with session TEMP tables so each hop is materialized and indexed instead of
-- re-expanding NOT IN subqueries (the naive single-query form times out).
-- TEMP tables live only in this session and do not touch the replica's public
-- schema (read-only discipline preserved). Emits three aggregated result sets.
\set ON_ERROR_STOP on
\timing off
set search_path = pg_temp, public;

create temp table cohort_sa on commit preserve rows as
select s.id
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

create temp table wtx on commit preserve rows as
select distinct w.tx_id from public.withdrawal w
join cohort_sa c on c.id = w.addr_id;
create index on wtx(tx_id);

-- hop 1: txs that spend a cohort withdrawal output but are not cohort wtx
create temp table hop1_txs on commit preserve rows as
select distinct i.tx_in_id as tx_id
from wtx
join public.tx_out o on o.tx_id = wtx.tx_id
join public.tx_in i on i.tx_out_id = o.tx_id and i.tx_out_index = o.index
left join wtx w2 on w2.tx_id = i.tx_in_id
where w2.tx_id is null;
create index on hop1_txs(tx_id);

create temp table hop1_out on commit preserve rows as
select o.tx_id, o.index, o.value, o.address, o.stake_address_id
from hop1_txs h join public.tx_out o on o.tx_id = h.tx_id;
create index on hop1_out(tx_id, index);

create temp table hop2_txs on commit preserve rows as
select distinct i.tx_in_id as tx_id
from hop1_out o
join public.tx_in i on i.tx_out_id = o.tx_id and i.tx_out_index = o.index
left join wtx w2 on w2.tx_id = i.tx_in_id
left join hop1_txs h1 on h1.tx_id = i.tx_in_id
where w2.tx_id is null and h1.tx_id is null;
create index on hop2_txs(tx_id);

create temp table hop2_out on commit preserve rows as
select o.tx_id, o.index, o.value, o.address, o.stake_address_id
from hop2_txs h join public.tx_out o on o.tx_id = h.tx_id;
create index on hop2_out(tx_id, index);

create temp table hop3_txs on commit preserve rows as
select distinct i.tx_in_id as tx_id
from hop2_out o
join public.tx_in i on i.tx_out_id = o.tx_id and i.tx_out_index = o.index
left join wtx w2 on w2.tx_id = i.tx_in_id
left join hop1_txs h1 on h1.tx_id = i.tx_in_id
left join hop2_txs h2 on h2.tx_id = i.tx_in_id
where w2.tx_id is null and h1.tx_id is null and h2.tx_id is null;

create temp table hop3_out on commit preserve rows as
select o.tx_id, o.index, o.value, o.address, o.stake_address_id
from hop3_txs h join public.tx_out o on o.tx_id = h.tx_id;

create temp table all_hops on commit preserve rows as
select 1 as hop, tx_id, value, address, stake_address_id from hop1_out
union all select 2, tx_id, value, address, stake_address_id from hop2_out
union all select 3, tx_id, value, address, stake_address_id from hop3_out;

-- Two CSV result sets, sentinel-delimited on one stdout stream so a single
-- heavy build produces both (split locally on the @@ markers).

-- Result set A: per-hop rollup (how much value, how concentrated).
\echo '@@HOP_SUMMARY'
copy (
  select
    hop,
    count(distinct tx_id) as txs,
    count(*) as outputs,
    count(distinct coalesce(cast(stake_address_id as text), address)) as distinct_destinations,
    count(*) filter (where stake_address_id is null) as enterprise_outputs,
    round(sum(value) / 1e6, 6) as total_ada
  from all_hops group by hop order by hop
) to stdout with csv header;

-- Result set B: top destinations per hop (>= 10,000 ADA, top 200/hop).
-- NOTE: from hop 2 these are path tx-output aggregates; unrelated value
-- entering those txs is included. No taint accounting is claimed.
\echo '@@HOP_DESTINATIONS'
copy (
  with agg as (
    select hop,
           coalesce(s2.view, a.address) as destination,
           (a.stake_address_id is null) as enterprise_only,
           count(distinct a.tx_id) as txs,
           round(sum(a.value) / 1e6, 6) as total_ada
    from all_hops a
    left join public.stake_address s2 on s2.id = a.stake_address_id
    group by hop, coalesce(s2.view, a.address), (a.stake_address_id is null)
    having sum(a.value) >= 10000 * 1e6
  ),
  ranked as (
    select *, row_number() over (partition by hop order by total_ada desc) rn
    from agg
  )
  select hop, destination, enterprise_only, txs, total_ada
  from ranked where rn <= 200 order by hop, total_ada desc
) to stdout with csv header;

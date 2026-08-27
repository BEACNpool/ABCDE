-- ABCDE F20 — SecondFi recovery-fund verification (reproduce script)
-- Target: Cardano db-sync (cexplorer / cexplorer_replica).
-- Snapshot used for the committed CSVs: block 13740498, 2026-07-29 14:15:46 UTC.
--
-- Purpose: independently check, against mainnet, the claims SecondFi made in its
-- 2026-07-29 11:19:05 UTC public post about the EMURGO-established recovery fund.
-- Every number in findings/F20 comes from one of the queries below.

\set rf   'addr1qyvvn9e9ulvzw2nvgkwraxwrla4a28l7gmduk7jru2rw9kdxkls8aczwgg8u44nj87uaq50rgcjulcxtzv9q8j0g2lss9kv2ss'
\set fund 'addr1q87tedda67n5m385u24cduk3xkqs6md8w532g49stsmpj80uhj6mm4a8fhz0fc4tsmedzdvpp4k6wafz532tqhpkrywscan8n3'
\set hop1 'addr1q9wxf5ks78qu7u43wqutpru3hvhhq6n2g66n26lge72lx4jq8ht8har50c4gq09g9chkg8zaq4tu5udptlc82q7avgjsdwlux6'
\set omni 'addr1vx7j284mqe59w2mka36gf5xq0hvu8ms2989553fk5qh3prcapfpj3'
\set sa2  'addr1q8m5wdncq7rwum73r5cyyr82qx2xjem5k4ehapl3wy36aaerj829vasl3amtcwshgvnn6a25dr850tfw6qaj420d2szsslkku6'
\set vault 'addr1qyjfzgs74e90e7yk5yw7gey0ct35su6qmjsufpjc9w9t0ljf6fs0lrl9v94vqc0aw07wpt7l8l4q354l2az77ca82v2svfvlhl'

-- 0. Snapshot stamp. Every balance below is snapshot-sensitive; record this first.
select max(block_no) as snapshot_block, max(time) as snapshot_time_utc from block;

-- 1. Recovery fund: live balance and UTxO count.
select count(*) as utxos, sum(o.value)/1e6 as ada_now
from tx_out o
where o.address = :'rf'
  and not exists (select 1 from tx_in i where i.tx_out_id = o.tx_id and i.tx_out_index = o.index);

-- 2. Recovery fund: EVERY inflow, one row per transaction.
--    This is the query that decides whether an announced deposit exists.
--    A native-token-only deposit would still appear here (it carries min-ADA).
select b.block_no, b.time at time zone 'UTC' as time_utc, encode(t.hash,'hex') as tx_hash,
       sum(o.value)/1e6 as ada_in
from tx_out o
join tx t on t.id = o.tx_id
join block b on b.id = t.block_id
where o.address = :'rf'
group by 1,2,3
order by 1;

-- 3. Recovery fund: the funding source of every inflow transaction.
with intx as (
  select distinct t.id as tx_id, encode(t.hash,'hex') as tx_hash, b.block_no, b.time
  from tx_out o join tx t on t.id = o.tx_id join block b on b.id = t.block_id
  where o.address = :'rf'
)
select intx.block_no, intx.time, intx.tx_hash, src.address as source_address,
       sum(src.value)/1e6 as source_input_ada
from intx
join tx_in i on i.tx_in_id = intx.tx_id
join tx_out src on src.tx_id = i.tx_out_id and src.index = i.tx_out_index
group by 1,2,3,4
order by 1, 5 desc;

-- 4. Stake-key completeness check: rules out "the deposit went to a sibling address
--    of the same wallet". Returns every payment address under the fund's stake key.
with sid as (
  select distinct o.stake_address_id as id from tx_out o where o.address = :'rf'
)
select o.address, count(*) as n_outs, sum(o.value)/1e6 as ada_received,
       min(b.time) as first_seen, max(b.time) as last_seen
from tx_out o
join sid on sid.id = o.stake_address_id
join tx t on t.id = o.tx_id join block b on b.id = t.block_id
group by 1 order by 3 desc;

-- 5. Provenance of the fund's principal: three hops back from the recovery fund.
--    5a. fund-seeding wallet -> recovery fund
select b.block_no, b.time, encode(t.hash,'hex') as tx_hash, sum(o.value)/1e6 as ada
from tx_out o join tx t on t.id = o.tx_id join block b on b.id = t.block_id
where o.address = :'fund' group by 1,2,3 order by 1;
--    5b. who funded the fund-seeding wallet
with intx as (select distinct t.id as tx_id, b.block_no, b.time
              from tx_out o join tx t on t.id=o.tx_id join block b on b.id=t.block_id
              where o.address = :'fund')
select intx.block_no, intx.time, src.address, sum(src.value)/1e6 as src_ada
from intx join tx_in i on i.tx_in_id = intx.tx_id
join tx_out src on src.tx_id = i.tx_out_id and src.index = i.tx_out_index
group by 1,2,3 order by 1,4 desc;
--    5c. who funded that wallet's 16.1M inflow (expect the shared exchange omnibus)
select src.address, sum(src.value)/1e6 as src_ada
from tx t join tx_in i on i.tx_in_id = t.id
join tx_out src on src.tx_id = i.tx_out_id and src.index = i.tx_out_index
where t.hash = decode('63fe132457e4cb0fd146ea156856414e8e6a2721691c2b5b712fb7555f0b7920','hex')
group by 1 order by 2 desc;

-- 6. The on-chain negotiation: CIP-20 (label 674) messages carried by any transaction
--    that touches the recovery fund, and any message sent TO the second-attacker wallet.
with touch as (
  select distinct t.id as tx_id, encode(t.hash,'hex') as h, b.time
  from tx_out o join tx t on t.id=o.tx_id join block b on b.id=t.block_id where o.address = :'rf'
  union
  select distinct t2.id, encode(t2.hash,'hex'), b.time
  from tx_out o join tx_in i on i.tx_out_id=o.tx_id and i.tx_out_index=o.index
  join tx t2 on t2.id=i.tx_in_id join block b on b.id=t2.block_id where o.address = :'rf'
)
select touch.time, touch.h, md.key, md.json
from touch join tx_metadata md on md.tx_id = touch.tx_id order by touch.time;

-- 7. Ultimatum outcome: did the second-attacker wallet move, or reply, after the demand?
select 'outflow_txs_after_demand' as check, count(distinct i.tx_in_id)::text as value
from tx_out o join tx_in i on i.tx_out_id=o.tx_id and i.tx_out_index=o.index
join tx t2 on t2.id=i.tx_in_id join block b on b.id=t2.block_id
where o.address = :'sa2' and b.time > '2026-07-08 03:34:14'
union all
select 'balance_at_deadline_2026_07_10T2359Z',
 (select coalesce(sum(o.value),0)/1e6 from tx_out o join tx t on t.id=o.tx_id join block b on b.id=t.block_id
   where o.address = :'sa2' and b.time <= '2026-07-10 23:59:00'
     and not exists (select 1 from tx_in i join tx t3 on t3.id=i.tx_in_id join block b3 on b3.id=t3.block_id
                     where i.tx_out_id=o.tx_id and i.tx_out_index=o.index and b3.time <= '2026-07-10 23:59:00'))::text
union all
select 'distinct_cnt_policies_held',
 (select count(distinct ma.policy)::text from tx_out o join ma_tx_out m on m.tx_out_id=o.id
   join multi_asset ma on ma.id=m.ident where o.address = :'sa2'
   and not exists (select 1 from tx_in i where i.tx_out_id=o.tx_id and i.tx_out_index=o.index));

-- 8. Contested 129.4M vault: still zero spends?
select count(*) as spends_ever
from tx_out o join tx_in i on i.tx_out_id=o.tx_id and i.tx_out_index=o.index
where o.address = :'vault';

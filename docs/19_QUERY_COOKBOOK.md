# Query Cookbook

This cookbook gives copy/paste examples for community members who clone ABCDE and want to inspect the committed CSV artifacts.

The examples use the Python `duckdb` package from `requirements/base.txt`.

## Setup

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements/base.txt
```

Run examples from the repo root.

## Did EMURGO remove genesis ADA from its DRep?

```bash
python3 - <<'PY'
import duckdb
con = duckdb.connect("data/abcde_genesis.duckdb", read_only=True)
print(con.sql("""
SELECT bucket, utxos, stake_addrs, ada
FROM emurgo_genesis_leftover_by_drep_bucket
ORDER BY ada DESC
"""))
print(con.sql("""
SELECT "window", label, from_epoch, to_epoch, from_ada, to_ada, delta_ada
FROM emurgo_drep_epoch_deltas
WHERE label IN ('emurgo_official', 'community7_total')
ORDER BY from_epoch
"""))
PY
```

## Top DReps by current voting power

```bash
python3 - <<'PY'
import duckdb
duckdb.sql("""
SELECT
  rank_overall,
  rank_registered,
  profile_class,
  drep_id_bech32,
  voting_power_ada,
  current_delegator_count,
  latest_retention_ratio,
  query_timestamp_utc,
  drep_distribution_epoch
FROM read_csv_auto('data/small/governance_top_drep_profiles_current.csv')
ORDER BY rank_overall;
""").show()
PY
```

## Find DReps with the most genesis-trace exposure

```bash
python3 - <<'PY'
import duckdb
duckdb.sql("""
SELECT
  e.rank_overall,
  e.profile_class,
  e.drep_id_bech32,
  e.dedup_current_ada,
  e.dedup_current_stake_credentials,
  e.root_overlap_summary
FROM read_csv_auto('data/small/governance_top_drep_genesis_trace_exposure.csv') e
ORDER BY e.dedup_current_ada DESC;
""").show()
PY
```

Interpretation: this is trace-derived value whose latest observed DRep target is the DRep. It is not beneficial-ownership evidence.

## Inspect a specific DRep by id

Replace the DRep id below with any `drep_id_bech32` from the profile CSV.

```bash
python3 - <<'PY'
import duckdb
drep = 'drep1jnmmkfwpta0yuwjchw0gu6csh75vy62088egy9n67d0zc7sn83m'
duckdb.sql(f"""
SELECT *
FROM read_csv_auto('data/small/governance_top_drep_profiles_current.csv')
WHERE drep_id_bech32 = '{drep}';
""").show()
PY
```

## Delegator stake-size profile for one DRep

```bash
python3 - <<'PY'
import duckdb
drep = 'drep1jnmmkfwpta0yuwjchw0gu6csh75vy62088egy9n67d0zc7sn83m'
duckdb.sql(f"""
SELECT
  active_stake_bucket,
  current_delegator_count,
  active_stake_ada
FROM read_csv_auto('data/small/governance_top_drep_stake_buckets.csv')
WHERE drep_id_bech32 = '{drep}'
ORDER BY bucket_order;
""").show()
PY
```

This is useful for seeing whether a DRep is supported by a few very large delegators, many small delegators, or a mix.

## Delegation-age profile for one DRep

```bash
python3 - <<'PY'
import duckdb
drep = 'drep1jnmmkfwpta0yuwjchw0gu6csh75vy62088egy9n67d0zc7sn83m'
duckdb.sql(f"""
SELECT
  latest_vote_epoch_bucket,
  current_delegator_count,
  active_stake_ada
FROM read_csv_auto('data/small/governance_top_drep_delegation_age_buckets.csv')
WHERE drep_id_bech32 = '{drep}'
ORDER BY age_bucket_order;
""").show()
PY
```

Older buckets with large active stake are evidence of sticky support, but not proof of off-chain coordination.

## Top SPO pool affiliations for one DRep

```bash
python3 - <<'PY'
import duckdb
drep = 'drep1jnmmkfwpta0yuwjchw0gu6csh75vy62088egy9n67d0zc7sn83m'
duckdb.sql(f"""
SELECT
  pool_rank_for_drep,
  ticker_name,
  pool_id_bech32,
  current_delegator_count,
  active_stake_ada,
  homepage
FROM read_csv_auto('data/small/governance_top_drep_pool_affiliations.csv')
WHERE drep_id_bech32 = '{drep}'
ORDER BY pool_rank_for_drep;
""").show()
PY
```

This shows where current DRep delegators are also staking. It does not identify people or prove why they delegated.

## Check Koios/db-sync agreement

```bash
python3 - <<'PY'
import duckdb
duckdb.sql("""
SELECT
  rank_overall,
  drep_id_bech32,
  koios_drep_id,
  koios_status,
  amount_matches_dbsync,
  meta_url_matches_dbsync,
  meta_hash_matches_dbsync
FROM read_csv_auto('data/small/governance_top_drep_koios_crosscheck.csv')
ORDER BY rank_overall;
""").show()
PY
```

Rows where a match column is false should be inspected before using the profile data publicly.

## Genesis-trace stickiness by root

```bash
python3 - <<'PY'
import duckdb
duckdb.sql("""
SELECT
  rank_overall,
  drep_id_bech32,
  root_seed_id,
  ever_trace_stake_credentials,
  latest_still_this_drep,
  latest_moved_away,
  latest_still_ratio,
  current_ada_latest_still,
  current_ada_moved_away
FROM read_csv_auto('data/small/governance_top_drep_genesis_trace_stickiness.csv')
WHERE ever_trace_stake_credentials > 0
ORDER BY rank_overall, root_seed_id;
""").show()
PY
```

This answers whether traced stake credentials that ever delegated to a DRep still point there as their latest observed DRep target.

## Join the profile table to trace exposure

```bash
python3 - <<'PY'
import duckdb
duckdb.sql("""
WITH p AS (
  SELECT *
  FROM read_csv_auto('data/small/governance_top_drep_profiles_current.csv')
), e AS (
  SELECT *
  FROM read_csv_auto('data/small/governance_top_drep_genesis_trace_exposure.csv')
)
SELECT
  p.rank_overall,
  p.profile_class,
  p.drep_id_bech32,
  p.voting_power_ada,
  p.current_delegator_count,
  p.latest_retention_ratio,
  e.dedup_current_ada,
  e.dedup_current_stake_credentials
FROM p
JOIN e USING (drep_id_bech32)
ORDER BY e.dedup_current_ada DESC;
""").show()
PY
```

## Trace hops with epoch/block context

Hop depth and chain time are different dimensions. Use this when checking
whether traced hops cluster by epoch or block:

```bash
python3 scripts/query_duckdb.py sql/30_query_recipes/trace_hops_with_epoch_block.duckdb.sql
```

For cross-entity merge candidates with exact chain position:

```bash
python3 scripts/query_duckdb.py sql/30_query_recipes/cross_entity_merges_epoch_block.duckdb.sql
```

For DRep exposure timing windows by root seed:

```bash
python3 scripts/query_duckdb.py sql/30_query_recipes/drep_exposure_epoch_windows.duckdb.sql
```

For the current IOG depth-14 bag, use the temporal limits recipe. It shows which
timing fields are present in the per-current-UTXO drilldown:

```bash
python3 scripts/query_duckdb.py sql/30_query_recipes/iog_current_bag_depth_temporal_limits.duckdb.sql
python3 scripts/query_duckdb.py sql/30_query_recipes/iog_current_bag_current_utxos_epoch_block.duckdb.sql
```

See `docs/20_TEMPORAL_QUERY_GUIDE.md` for the full map of which tables carry
exact `epoch_no`, `block_no`, and `block_time_utc` fields.

## Useful questions to ask next

- Which DReps have high current voting power but low historical retention?
- Which DReps have support concentrated in large stake buckets?
- Which DReps have strong support from older delegation cohorts?
- Which DReps show large genesis-trace exposure under the latest observed DRep target?
- Which trace or cross-merge events cluster in the same epoch/block window?
- Which pool communities overlap most with each DRep's current delegators?
- Are any Koios and db-sync metadata fields out of agreement?

## Evidence discipline

The profile pack can support statements about on-chain delegation behavior. It should not be used to infer beneficial ownership, legal identity, nationality, custody, or intent.

---

## Relay surface

Every query below runs against the committed DuckDB — `python -m mcp_server.server`,
`ask.py`, or `duckdb data/abcde_genesis.duckdb` directly. These are the questions
people actually asked when the relay data went public; they are written down here
so nobody has to ask their author.

**Bound by [`docs/27_RELAY_HEALTH_METHOD.md`](27_RELAY_HEALTH_METHOD.md).** Registration
is FACT and reproduces exactly. Reachability is an OBSERVATION from one vantage
point at one moment and is never "the relay is down".

### Everything known about one pool

The question behind almost every request. Swap the ticker.

```sql
SELECT * FROM relay_pool_health WHERE ticker = 'ZZZ';

-- what it registered, and what the last sweep saw for each entry
SELECT endpoint_host, port, resolved_ip, handshake_ok, failure, at_tip
FROM relay_pool_endpoints WHERE ticker = 'ZZZ' ORDER BY endpoint_host;
```

`relay_pool_endpoints` is the join between pools and endpoints — `relay_pool_health`
is keyed by pool and `relay_endpoint_status` by endpoint, so without it there is no
way to ask "what did *this* pool register". There is also a search box for exactly
this on [the page](https://beacnpool.github.io/ABCDE/relays.html#lookup).

### Who shares a relay with whom

```sql
SELECT endpoint, pools, stake_ada, delegators, tickers
FROM relay_shared_endpoints ORDER BY pools DESC LIMIT 20;
```

Registration strings understate this. Pools that register one hostname each still
share a machine, and only resolution finds it:

```sql
SELECT resolved_ip, target_port, pools, distinct_registered_names, stake_ada, tickers
FROM relay_shared_hosts ORDER BY pools DESC LIMIT 20;
```

### Pools producing blocks with no registered relay

```sql
SELECT ticker, stake_ada, delegators, blocks_last_30_epochs, ever_removed_all_relays,
       removed_all_relays_on
FROM relay_pool_health
WHERE registration_class = 'NO_REGISTERED_RELAY' AND minted_last_30_epochs
ORDER BY stake_ada DESC;
```

### Who changed their relay registration, and when

`pool_update` is append-only, so this cannot be edited away. Every row carries the
transaction hash.

```sql
SELECT ticker, changed_at, relays_before, relays_after, direction, tx_hash
FROM relay_registration_changes WHERE direction = 'removed_all'
ORDER BY changed_at DESC;
```

Read the direction honestly — most relay-count changes are pools *adding* capacity:

```sql
SELECT direction, count(*) AS certs, count(DISTINCT pool_bech32) AS pools
FROM relay_registration_changes GROUP BY direction ORDER BY certs DESC;
```

### Pools advertising infrastructure they do not run

```sql
SELECT ticker, stake_ada, pledge_ada, blocks_all_time, endpoint_host, operator,
       endpoints_foreign, endpoints_registered
FROM relay_foreign_infrastructure ORDER BY stake_ada DESC;
```

### Registrations that cannot work at all

Wrong by construction, not by opinion, and fixable by the operator in one
transaction:

```sql
SELECT ticker, stake_ada, endpoint_host, defect, why, blocks_all_time
FROM relay_registration_defects ORDER BY stake_ada DESC;
```

### Why a specific endpoint failed

`refused` and `timeout` are different findings. Refused means something is alive at
that address and actively rejecting; timeout means nothing answered at all.

```sql
SELECT failure, count(*) AS endpoints FROM relay_endpoint_status
WHERE NOT handshake_ok GROUP BY failure ORDER BY endpoints DESC;
```

### How much stake shares one hosting provider

```sql
SELECT as_name, country, pools, stake_ada, pools_single_asn, stake_single_asn
FROM relay_asn_concentration ORDER BY stake_single_asn DESC LIMIT 15;
```

An ASN is a failure domain, not an operator: two pools in one datacenter are
usually two unrelated people who both picked the cheap option.

### Questions this data cannot answer

- **Which relay first propagated a given block.** Block headers record the issuer,
  not the path. Propagation is a network event and is not on-chain. Your own
  node's BlockFetch traces record which *peer* delivered each block; network-wide,
  that is what `blockperf` and pooltool first-seen reporting exist for.
- **Whether a pool is "offline".** Only whether an endpoint answered our prober,
  from one place, at one moment.
- **Who operates a pool, or why they configured it as they did.** A
  misconfiguration and a deliberate free-ride are identical on-chain.

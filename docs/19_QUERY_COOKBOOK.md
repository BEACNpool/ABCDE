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

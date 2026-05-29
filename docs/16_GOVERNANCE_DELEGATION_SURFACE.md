# Governance Delegation Surface

This branch now publishes first-pass SPO and DRep delegation target rollups for trace-derived stake credentials.

## Files

- `data/small/governance_spo_delegation_targets.csv`
- `data/small/governance_drep_delegation_targets.csv`
- `data/manifests/governance-rollups-manifest.json`

## Query examples

```bash
python3 scripts/query_duckdb.py sql/10_findings/governance_spo_delegation_targets_summary.duckdb.sql
python3 scripts/query_duckdb.py sql/10_findings/governance_drep_delegation_targets_summary.duckdb.sql
python3 scripts/query_duckdb.py sql/10_findings/governance_top_spo_targets.duckdb.sql
python3 scripts/query_duckdb.py sql/10_findings/governance_top_drep_targets.duckdb.sql
```

## What this answers

- Which SPO pools received delegation from trace-derived stake credentials?
- Which DReps received vote delegation from trace-derived stake credentials?
- How many distinct traced stake credentials delegated to each target?
- What epoch range was observed?

## What this does not prove

- It does not prove beneficial ownership.
- It does not prove voting intent.
- It does not yet provide human-readable DRep names or pool tickers for every target.
- It is derived from preserved trace receipts, not yet a fresh full v2 staged trace extraction.

## Next enrichment

- Pool metadata/ticker enrichment from db-sync off-chain pool data.
- DRep metadata enrichment from on-chain anchors / governance registry where available.
- Latest-active delegation snapshots per root seed.
- Value-weighted delegation if a reliable stake/value snapshot is included.

## Metadata enrichment

Additional enrichment files:

- `data/small/governance_pool_metadata.csv`
- `data/small/governance_drep_metadata.csv`

These provide pool ticker/name/homepage and DRep registration anchor URL/hash where db-sync has the data. Missing metadata is preserved as missing; the raw target ids remain the durable keys.

Enriched top-target queries:

```bash
python3 scripts/query_duckdb.py sql/10_findings/governance_top_spo_targets_enriched.duckdb.sql
python3 scripts/query_duckdb.py sql/10_findings/governance_top_drep_targets_enriched.duckdb.sql
```

## Latest observed delegation snapshots

Lifetime target rollups answer “who ever received delegation?” Latest snapshots answer “where did the latest observed delegation per traced stake credential point?”

Files:

- `data/small/governance_spo_latest_targets.csv`
- `data/small/governance_drep_latest_targets.csv`

Queries:

```bash
python3 scripts/query_duckdb.py sql/10_findings/governance_latest_spo_targets_enriched.duckdb.sql
python3 scripts/query_duckdb.py sql/10_findings/governance_latest_drep_targets_enriched.duckdb.sql
```

## Value-weighted latest delegation

Files:

- `data/small/governance_spo_latest_value_targets.csv`
- `data/small/governance_drep_latest_value_targets.csv`

These join latest observed delegation targets to preserved current-unspent trace receipts by stake credential. They answer “how much trace-derived value had this as the latest observed delegation target in the receipt set?”

Important: this is **not live pool stake** and must not be used to claim that a pool currently has that much active stake. Validate live pool state separately from db-sync `pool_retire` and `epoch_stake` before making pool-current claims.

Queries:

```bash
python3 scripts/query_duckdb.py sql/10_findings/governance_latest_spo_value_targets_enriched.duckdb.sql
python3 scripts/query_duckdb.py sql/10_findings/governance_latest_drep_value_targets_enriched.duckdb.sql
```

Caveat: value weighting depends on preserved current-unspent trace receipts and should be refreshed after the staged v2 full trace extractor is complete.

## Top DRep profile pack

The repo also publishes a standardized profile pack for the current top DReps as a set, rather than one-off individual dossiers.

Report:

- `reports/top_drep_profiles.md`

Files:

- `data/small/governance_top_drep_profiles_current.csv`
- `data/small/governance_top_drep_stake_buckets.csv`
- `data/small/governance_top_drep_delegation_age_buckets.csv`
- `data/small/governance_top_drep_pool_affiliations.csv`
- `data/small/governance_top_drep_koios_crosscheck.csv`
- `data/small/governance_top_drep_genesis_trace_exposure.csv`
- `data/small/governance_top_drep_genesis_trace_exposure_by_root.csv`
- `data/small/governance_top_drep_genesis_trace_stickiness.csv`
- `data/manifests/top-drep-profiles-manifest.json`

Build:

```bash
bash scripts/build_top_drep_profiles_remote.sh
```

Every generated row carries the db-sync query timestamp and DRep distribution epoch. Registered DRep rows also get a Koios `drep_info` cross-check where available. The report keeps FACT, STRONG INFERENCE, and UNKNOWN boundaries explicit: current DRep power and delegation buckets are db-sync facts; trace-derived genesis exposure is an audit signal; beneficial ownership, intent, and off-chain demographics are not inferred.

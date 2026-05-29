# F06 — SPO and DRep Delegation Targets for Trace-Derived Stake Credentials

## Claim

Preserved trace receipts include Shelley-era pool delegation and Conway-era DRep delegation histories for stake credentials reached by the Genesis traces. v2 now publishes rollups of every observed SPO pool target and DRep target by root seed.

## Grade

FACT for rows derived from preserved trace delegation receipts. Labels/names for pools or DReps are not yet enriched; current outputs identify targets by bech32 id.

## Evidence

- `data/small/governance_spo_delegation_targets.csv`
- `data/small/governance_drep_delegation_targets.csv`
- `data/manifests/governance-rollups-manifest.json`
- `data/abcde_genesis_seed_registry.duckdb`

## Current row counts

- SPO target rows: `5,175`
- DRep target rows: `390`

Rows are grouped by `root_seed_id` and target id. The fourth-entry legacy trace label `emurgo2` is normalized to `fourth_entry_781m`.

## Reproduce

SPO summary:

```sql
SELECT
  root_seed_id,
  count(*) AS distinct_pool_targets,
  sum(distinct_stake_addresses) AS summed_distinct_stake_addresses_per_pool,
  min(first_active_epoch) AS first_active_epoch,
  max(last_active_epoch) AS last_active_epoch
FROM governance_spo_delegation_targets
GROUP BY root_seed_id
ORDER BY root_seed_id;
```

DRep summary:

```sql
SELECT
  root_seed_id,
  count(*) AS distinct_drep_targets,
  sum(distinct_stake_addresses) AS summed_distinct_stake_addresses_per_drep,
  min(first_epoch) AS first_epoch,
  max(last_epoch) AS last_epoch
FROM governance_drep_delegation_targets
GROUP BY root_seed_id
ORDER BY root_seed_id;
```

Top targets:

- `sql/10_findings/governance_top_spo_targets.duckdb.sql`
- `sql/10_findings/governance_top_drep_targets.duckdb.sql`

## Limitations

This is a rollup of observed delegation certificates from preserved trace outputs, not yet a fully refreshed db-sync extraction from a staged v2 full trace table. It documents targets and timing, not beneficial ownership or voting intent.

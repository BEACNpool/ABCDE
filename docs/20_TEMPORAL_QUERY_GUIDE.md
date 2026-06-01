# Temporal Query Guide

Hop depth is not time. A depth-14 trace row and a depth-3 trace row can be close
or far apart on-chain depending on when each transaction happened. For anomaly
review, ask for both:

- trace position: `depth`, `min_depth`, `max_depth`
- chain position: `epoch_no`, `block_no`, `block_time_utc`
- governance observation windows: `first_epoch`, `last_epoch`,
  `first_observed_block_time`, `last_observed_block_time`

## Run The Recipes

From the repo root:

```bash
python scripts/query_duckdb.py sql/30_query_recipes/trace_hops_with_epoch_block.duckdb.sql
python scripts/query_duckdb.py sql/30_query_recipes/cross_entity_merges_epoch_block.duckdb.sql
python scripts/query_duckdb.py sql/30_query_recipes/drep_exposure_epoch_windows.duckdb.sql
python scripts/query_duckdb.py sql/30_query_recipes/iog_current_bag_depth_temporal_limits.duckdb.sql
```

## Exact Chain Position Available

These public tables include exact transaction chain position:

- `bounded_trace_depth3_db`: `epoch_no`, `block_no`, `block_time_utc`
- `seed_anchor_db_verification`: `epoch_no`, `block_no`, `block_time_utc`
- `seed_outputs_db`: `epoch_no`, `block_no`, `block_time_utc`
- `seed_first_spends_db`: `first_spend_epoch`, `first_spend_block_no`,
  `first_spend_time_utc`
- `seed_first_spend_inputs_db`: `input_source_block_no`,
  `first_spend_block_no`
- `staged_cross_entity_merges_depth10`: `epoch_no`, `block_no`,
  `block_time_utc`
- `staged_cross_entity_merges_founders_depth10`: `epoch_no`, `block_no`,
  `block_time_utc`

Use these when checking whether repeated merges, splits, or cross-root events
cluster by epoch/block.

## Observation Windows Available

Governance rollups are not per-transaction traces, but they do include timing
windows:

- `governance_drep_delegation_targets`: first/last observed DRep delegation
  epoch and block time by root/DRep
- `governance_drep_latest_targets`: latest observed DRep target epoch/time
  range by root/DRep
- `governance_spo_delegation_targets`: first/last observed SPO delegation
  active epoch and block time by root/pool
- `governance_spo_latest_targets`: latest observed SPO target epoch/time
  range by root/pool
- `governance_drep_metadata`: DRep registration epoch and block time
- `governance_pool_metadata`: pool metadata `active_epoch_no`

Use these to find timing commonalities, then drill into db-sync for exact
certificate transaction receipts if needed.

## Known Gap

The IOG depth-14 current-bag tables are value/depth/classification rollups.
They do not currently publish per-UTXO `epoch_no`, `block_no`, or
`block_time_utc`. That is fine for confidence bands, but not enough for a
temporal anomaly claim.

For a professional audit, the next extraction should add a per-current-UTXO
artifact with at least:

- `root_seed_id`
- `stake_address`
- `tx_hash`
- `tx_out_index`
- `current_lovelace`
- `min_depth`
- `max_depth`
- `epoch_no`
- `block_no`
- `block_time_utc`
- latest SPO/DRep target fields, where applicable

Until that exists, say: "depth-14 current-bag timing requires deeper db-sync
extraction."

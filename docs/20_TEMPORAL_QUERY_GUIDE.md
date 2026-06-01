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
python scripts/query_duckdb.py sql/30_query_recipes/iog_current_bag_current_utxos_epoch_block.duckdb.sql
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
- `iog_current_bag_depth14_current_utxos`: `epoch_no`, `block_no`,
  `block_time_utc`, plus current value and latest observed SPO/DRep delegation
  context

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

## IOG Current-Bag Drilldown

The IOG depth-14 current-bag cut now includes
`iog_current_bag_depth14_current_utxos`, one row per currently unspent
IOG-descended UTxO in the public cut.

Columns include:

- `root_seed_id`
- `stake_address`
- `tx_hash`
- `tx_out_index`
- `current_lovelace`
- `current_ada`
- `min_depth`
- `epoch_no`
- `block_no`
- `block_time_utc`
- latest observed SPO fields, where applicable
- latest observed DRep fields, where applicable
- latest active-stake epoch/value fields, where applicable

This closes the public timing gap for IOG current-bag anomaly review. Confidence
bands are still interpretive rollups; exact temporal claims should cite
`iog_current_bag_depth14_current_utxos`.

Remaining professional-audit work is classification and provenance review, not
basic epoch/block availability.

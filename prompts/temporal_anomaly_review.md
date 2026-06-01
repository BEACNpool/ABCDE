# Temporal Anomaly Review

Use the local ABCDE repo and its DuckDB database. Do not answer from memory.

Goal: separate hop-depth evidence from epoch/block timing evidence.

Steps:

1. List the tables that contain any of these columns:
   `epoch_no`, `block_no`, `block_time_utc`, `first_epoch`, `last_epoch`,
   `first_observed_block_time`, `last_observed_block_time`.
2. Run `sql/30_query_recipes/trace_hops_with_epoch_block.duckdb.sql`.
   Identify any repeated epochs, adjacent block windows, or unusually tight
   timing clusters. Label each observation as FACT or UNKNOWN.
3. Run `sql/30_query_recipes/cross_entity_merges_epoch_block.duckdb.sql`.
   Which root combinations appear in the same epoch/block neighborhoods?
   Report the exact merge tx hashes, epochs, blocks, and input depth ranges.
4. Run `sql/30_query_recipes/drep_exposure_epoch_windows.duckdb.sql`.
   Which DReps have multi-root genesis-trace exposure and overlapping first/last
   delegation observation windows?
5. Run `sql/30_query_recipes/iog_current_bag_depth_temporal_limits.duckdb.sql`.
   State plainly what timing evidence is missing for the depth-14 current-bag
   bands.
6. Produce two sections:
   - Reproducible From This Clone
   - Needs Deeper db-sync Extraction

Do not infer off-chain ownership, intent, or wallet control. Tight timing
clusters are audit leads, not proof.

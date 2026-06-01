# Data Dictionary

This describes the current v2 seed-registry cut in `data/abcde_genesis_seed_registry.duckdb` and the matching CSV receipts in `data/small/`.

The full Genesis subgraph is not published yet. This first cut proves the new pipeline shape with small, inspectable artifacts.

## `seed_registry`

Source: `anchors.yaml` → `data/small/seed_registry.csv`

| column | meaning |
| --- | --- |
| `seed_id` | Stable v2 identifier, e.g. `iog`, `emurgo`, `cf`, `fourth_entry_781m` |
| `label` | Human-readable label |
| `tx_hash` | Seed redemption transaction hash |
| `amount_ada` | Nominal ADA amount |
| `amount_lovelace` | Amount in lovelace |
| `source_type` | Classification such as `NAMED_FOUNDER` or `SALE_TICKET_SIGNAL` |
| `evidence_grade` | Claim grade for the classification |
| `notes` | Non-attribution notes or caveats |

## `seed_outputs`

Source: ABCDE/db-sync → `data/small/seed_outputs_db.csv`

One row per seed redemption output.

| column | meaning |
| --- | --- |
| `seed_id`, `label` | Join keys back to `seed_registry` |
| `tx_hash`, `tx_id` | db-sync transaction identifiers |
| `tx_out_index` | Output index; currently `0` for all four seeds |
| `value_lovelace` | Output value |
| `address` | Byron-era output address |
| `stake_address` | Usually empty for Byron outputs |
| `epoch_no`, `block_no`, `block_time_utc` | Chain position of seed redemption output |

## `seed_first_spends`

Source: ABCDE/db-sync → `data/small/seed_first_spends_db.csv`

First transaction spending each seed output. Uses correct db-sync join:

```sql
tx_in.tx_out_id = producing_tx.id
AND tx_in.tx_out_index = produced_output.index
```

| column | meaning |
| --- | --- |
| `seed_*` | Source seed output identifiers |
| `first_spend_tx_hash`, `first_spend_tx_id` | First spending transaction |
| `first_spend_epoch`, `first_spend_block_no`, `first_spend_time_utc` | Chain position of first spend |
| `dormant_hours` | Hours from seed output to first spend |
| `spend_input_count`, `spend_output_count` | First-spend transaction shape |
| `spend_output_lovelace` | Total outputs of first-spend transaction |

## `seed_first_spend_inputs`

Source: ABCDE/db-sync → `data/small/seed_first_spend_inputs_db.csv`

Input composition for every seed first-spend transaction.

| column | meaning |
| --- | --- |
| `first_spend_seed_id` | Seed whose first-spend transaction is being inspected |
| `first_spend_tx_hash` | First-spend transaction hash |
| `input_source_tx_hash`, `input_source_tx_out_index` | Consumed UTxO source |
| `input_value_lovelace` | Consumed UTxO value |
| `input_address`, `input_stake_address` | Consumed output address/stake credential |
| `input_source_*` | Chain position of the consumed output |
| `matched_seed_id` | Seed id when the input is itself one of the seed outputs |

## `fourth_entry_direct_cospend`

Source: ABCDE/db-sync → `data/small/fourth_entry_direct_cospend_db.csv`

Focused receipt for finding `F02b`.

| column | meaning |
| --- | --- |
| `fourth_first_spend_tx_hash` | Fourth-entry first-spend tx, currently `c8596b9c...` |
| `input_source_tx_hash`, `input_source_tx_out_index` | Inputs consumed by that tx |
| `input_value_lovelace` | Input value |
| `descendant_of_seed_id` | Populated when the input is detected as a descendant of a tracked seed |
| `emurgo_trace_depth` | Depth from EMURGO seed output to the co-spent input |
| `emurgo_path` | Human-readable tx-hash path from EMURGO seed to co-spent input |

## `artifact_manifest`

Small key/value table embedded in DuckDB with source hashes for the local build.


## `bounded_trace_depth3`

Source: ABCDE/db-sync → `data/small/bounded_trace_depth3_db.csv`

A deliberately shallow bounded UTxO trace from the four current seed outputs. This is a review-cut extractor table, not the full Genesis subgraph.

| column | meaning |
| --- | --- |
| `seed_id`, `label` | Root seed identity |
| `depth` | Distance from seed output; current max depth is `3` |
| `tx_hash`, `tx_id`, `tx_out_index` | UTxO identifier |
| `value_lovelace` | UTxO value |
| `address`, `stake_address` | Output address and stake credential if present |
| `epoch_no`, `block_no`, `block_time_utc` | Chain position |
| `path` | Human-readable path of `tx_hash#index` entries from seed to row |

## `governance_spo_delegation_targets`

Source: preserved legacy trace delegation receipts → `data/small/governance_spo_delegation_targets.csv`

One row per root seed + pool target.

| column | meaning |
| --- | --- |
| `root_seed_id` | v2 root seed id; legacy `emurgo2` normalized to `fourth_entry_781m` |
| `pool_id_bech32` | SPO pool id receiving delegation |
| `distinct_stake_addresses` | Count of traced stake credentials that delegated to this pool |
| `delegation_cert_count` | Count of delegation certificates observed |
| `first_active_epoch`, `last_active_epoch` | Active epoch range |
| `first_observed_block_time`, `last_observed_block_time` | Certificate observation time range |
| `source_files` | Preserved receipt files used |

## `governance_drep_delegation_targets`

Source: preserved legacy trace DRep delegation receipts → `data/small/governance_drep_delegation_targets.csv`

One row per root seed + DRep target.

| column | meaning |
| --- | --- |
| `root_seed_id` | v2 root seed id; legacy `emurgo2` normalized to `fourth_entry_781m` |
| `drep_id_bech32` | DRep id, `drep_always_abstain`, or `drep_always_no_confidence` |
| `distinct_stake_addresses` | Count of traced stake credentials that delegated to this DRep target |
| `delegation_cert_count` | Count of vote delegation certificates observed |
| `first_epoch`, `last_epoch` | Observation epoch range |
| `first_observed_block_time`, `last_observed_block_time` | Certificate observation time range |
| `source_files` | Preserved receipt files used |

## `governance_pool_metadata`

Source: ABCDE/db-sync `pool_hash`, `pool_update`, `pool_metadata_ref`, `off_chain_pool_data`.

| column | meaning |
| --- | --- |
| `pool_id_bech32` | SPO pool id |
| `ticker_name` | Off-chain ticker if available |
| `pool_name` | Off-chain pool name if available |
| `homepage` | Off-chain homepage if available |
| `description` | Off-chain description if available |
| `metadata_url` | Pool metadata URL |
| `metadata_hash_hex` | Pool metadata hash |
| `active_epoch_no` | Latest pool update epoch used for metadata selection |

## `governance_drep_metadata`

Source: ABCDE/db-sync `drep_hash`, `drep_registration`, `voting_anchor`.

| column | meaning |
| --- | --- |
| `drep_id_bech32` | DRep id |
| `deposit` | Registration deposit if recorded |
| `voting_anchor_url` | Latest registration voting-anchor URL if available |
| `voting_anchor_data_hash_hex` | Anchor data hash |
| `registration_tx_hash` | Registration transaction hash |
| `epoch_no`, `block_time_utc` | Latest registration observation |

## `governance_spo_latest_targets`

Latest observed pool delegation per traced stake credential, grouped by root seed + pool.

| column | meaning |
| --- | --- |
| `root_seed_id` | v2 root seed id |
| `pool_id_bech32` | Latest observed pool target |
| `latest_distinct_stake_addresses` | Count of stake credentials whose latest observed pool delegation points here |
| `latest_active_epoch_min`, `latest_active_epoch_max` | Range of active epochs among latest observations |
| `latest_observed_block_time_min`, `latest_observed_block_time_max` | Observation time range |

## `governance_drep_latest_targets`

Latest observed DRep delegation per traced stake credential, grouped by root seed + DRep.

| column | meaning |
| --- | --- |
| `root_seed_id` | v2 root seed id |
| `drep_id_bech32` | Latest observed DRep target |
| `latest_distinct_stake_addresses` | Count of stake credentials whose latest observed DRep delegation points here |
| `latest_epoch_min`, `latest_epoch_max` | Range of epochs among latest observations |
| `latest_observed_block_time_min`, `latest_observed_block_time_max` | Observation time range |

## `governance_top_drep_*`

Source: ABCDE/db-sync current DRep distribution and delegation tables, Koios `drep_info` cross-checks, and preserved ABCDE genesis trace receipts.

These files publish standardized current profiles for the top DReps as a set:

- `data/small/governance_top_drep_profiles_current.csv`
- `data/small/governance_top_drep_stake_buckets.csv`
- `data/small/governance_top_drep_delegation_age_buckets.csv`
- `data/small/governance_top_drep_pool_affiliations.csv`
- `data/small/governance_top_drep_koios_crosscheck.csv`
- `data/small/governance_top_drep_genesis_trace_exposure.csv`
- `data/small/governance_top_drep_genesis_trace_exposure_by_root.csv`
- `data/small/governance_top_drep_genesis_trace_stickiness.csv`

Common columns:

| column | meaning |
| --- | --- |
| `query_timestamp_utc` | UTC timestamp when the source query/script ran |
| `drep_distribution_epoch` | Latest db-sync `drep_distr` epoch used |
| `epoch_stake_epoch` | Latest db-sync `epoch_stake` epoch used where active stake is involved |
| `rank_overall`, `rank_registered` | Rank by current voting power; registered rank excludes system DRep targets |
| `profile_class` | `registered` DRep or `system` target such as always-abstain/no-confidence |
| `drep_id_bech32`, `drep_hash_hex` | DRep identifier forms |

Profile-specific columns:

| column | meaning |
| --- | --- |
| `voting_power_lovelace`, `voting_power_ada` | Current DRep voting power from `drep_distr` |
| `current_delegator_count` | Stake credentials whose latest vote delegation points to this DRep |
| `historical_delegator_count`, `historical_vote_cert_count` | Historical delegation footprint |
| `latest_retention_ratio` | Current latest delegators divided by historical delegators |
| `active_stake_bucket`, `latest_vote_epoch_bucket` | Bucket labels for current stake size and delegation age |
| `pool_rank_for_drep`, `ticker_name`, `active_stake_ada` | Top current SPO pool affiliations by active stake |
| `amount_matches_dbsync`, `meta_url_matches_dbsync`, `meta_hash_matches_dbsync` | Koios cross-check booleans for registered DReps |
| `dedup_current_ada` | Deduped current genesis-trace value whose latest observed DRep target is this DRep |
| `root_overlap_summary` | Root-combination summary used to explain deduped trace exposure |
| `latest_still_this_drep`, `latest_moved_away` | Trace stickiness counts by root seed |

Important: DRep delegation is voting power, not custody. Genesis-trace exposure is an audit signal about traced stake credentials and current UTxOs; it is not beneficial-ownership evidence.


## `staged_trace_depth*_summary`

Source: ABCDE/db-sync staged extraction → `data/small/staged_trace_depth3_summary.csv`, `data/small/staged_trace_depth10_summary.csv`, and founder-only variants.

These are small review summaries for server-side staged extraction runs.

| column | meaning |
| --- | --- |
| `artifact` | Summary type, e.g. `trace_utxos` or `cross_entity_merges` |
| `bucket` | Depth bucket for `trace_utxos`, or root combo for `cross_entity_merges` |
| `rows` | Row count |

## `staged_cross_entity_merges_depth10`

Source: staged server-side views in ABCDE/db-sync → `data/small/staged_cross_entity_merges_depth10.csv`.

| column | meaning |
| --- | --- |
| `merge_tx_hash` | Transaction consuming traced inputs from two or more roots |
| `epoch_no`, `block_no`, `block_time_utc` | Chain position of merge transaction |
| `root_combo` | `+`-joined root seeds observed among traced inputs |
| `root_count` | Number of distinct root seeds observed |
| `traced_input_rows` | Number of traced input rows consumed by the transaction |
| `traced_input_lovelace` | Sum of traced input lovelace, across observed roots |
| `min_input_depth`, `max_input_depth` | Depth range of traced inputs consumed |

## `iog_current_bag_depth14_summary`

Source: staged server-side IOG trace in ABCDE/db-sync → `data/small/iog_current_bag_depth14_summary.csv`.

This is a depth-14 audit cut of currently unspent IOG-descended UTxOs. It is trace membership, not proof of current beneficial ownership.

| column | meaning |
| --- | --- |
| `current_utxo_rows` | Live-unspent UTxO rows in the depth-14 IOG staged trace |
| `current_ada` | Sum of live-unspent lovelace / 1,000,000 |
| `min_depth`, `max_depth` | Depth range of current rows within the staged trace |
| `distinct_stake_addresses` | Distinct Shelley stake addresses among current rows |
| `byron_or_no_stake_utxos`, `byron_or_no_stake_ada` | Current rows/value with no stake credential |
| `shelley_staked_ada` | Current rows/value with a stake credential |

## `iog_current_bag_depth14_current_utxos`

Source: staged server-side IOG trace in ABCDE/db-sync → `data/small/iog_current_bag_depth14_current_utxos.csv`.

One row per currently unspent IOG-descended UTxO in the depth-14 public cut. This is the drilldown table for temporal anomaly review.

| column | meaning |
| --- | --- |
| `root_seed_id` | Root seed, currently `iog` for this table |
| `stake_address` | Stake credential for the UTxO address, when present |
| `tx_hash`, `tx_out_index` | Current UTxO identifier |
| `current_lovelace`, `current_ada` | Current unspent value |
| `min_depth` | Minimum observed trace depth from the IOG seed |
| `epoch_no`, `block_no`, `block_time_utc` | Chain position of the current UTxO's creating transaction |
| `latest_pool_*` | Latest observed SPO delegation context for the stake credential, when present |
| `latest_drep_*` | Latest observed DRep delegation context for the stake credential, when present |
| `active_stake_epoch`, `active_stake_lovelace`, `active_stake_ada` | Latest active-stake snapshot for the stake credential, when present |

## `iog_pool_state_validation`

Source: ABCDE/db-sync pool registration/retirement/epoch stake tables → `data/small/iog_pool_state_validation.csv`.

This validates IOG1/IOG2 live pool status independently from trace-derived delegation rollups.

| column | meaning |
| --- | --- |
| `label`, `pool_view`, `ticker_name` | Pool identity |
| `tip_epoch`, `tip_block`, `tip_time_utc` | Chain tip used by the validation query |
| `retiring_epoch`, `is_retired_at_tip` | Retirement state at tip |
| `latest_epoch_stake_epoch`, `latest_epoch_active_stake_ada` | Latest epoch stake row if the pool is active |

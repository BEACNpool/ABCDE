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

## `governance_genesis_behavior_*`

Source: staged server-side founder depth-14 trace in ABCDE/db-sync plus latest DRep delegation, current DRep distribution, and DRep proposal votes.

Build command (maintainer-only; requires `ABCDE_SSH`):

```bash
TRACE_STAGE_SCHEMA=abcde_forensics_stage_founders_depth14 bash scripts/build_genesis_drep_behavior_surface_remote.sh
```

The full row-level surface is exported to `data/release/genesis_current_governance_surface.csv` and the full signal table to `data/release/governance_genesis_behavior_signals_full.csv`; neither is committed to git (release assets). Public committed cuts are:

- `data/small/governance_genesis_behavior_signals_top.csv` (clusters with `behavior_score >= 5`)
- `data/small/governance_genesis_behavior_by_drep.csv`
- `data/small/governance_genesis_behavior_by_root_drep.csv`
- `data/small/governance_genesis_behavior_clusters.csv`
- `data/small/governance_genesis_behavior_by_proposal.csv`

These files classify current traced value by latest DRep delegation target, public behavior signals, and proposal vote behavior.

| column | meaning |
| --- | --- |
| `snapshot_utc`, `trace_schema` | Build timestamp and staged trace schema |
| `latest_drep_id_bech32`, `latest_drep_hash_id` | Latest observed DRep delegation target for traced stake credentials |
| `output_epoch_no`, `output_block_no`, `output_block_time_utc` | Chain position where the current live-unspent traced output was created |
| `drep_distribution_epoch`, `drep_voting_power_*` | Current DRep distribution snapshot and voting power |
| `behavior_class` | Conservative confidence class or `no_stake_or_byron` |
| `dedup_current_utxos`, `dedup_current_lovelace`, `dedup_current_ada` | Current traced value deduped by UTxO where applicable |
| `trace_value_to_drep_power_ratio` | Deduped traced current value divided by current DRep voting power |
| `root_seed_id`, `root_overlap_summary`, `root_combo` | Genesis root provenance and overlap summary |
| `gov_action_proposal_id`, `proposal_tx_hash`, `proposal_index`, `proposal_type`, `vote` | Proposal/vote fields in proposal rollups |

`governance_genesis_behavior_signals_top.csv` is keyed by stake credential and includes the scoring components:

| column | meaning |
| --- | --- |
| `same_block_event_count`, `max_same_block_stake_peers` | Synchronized output-creation signals by depth/block |
| `same_epoch_drep_event_count`, `max_same_epoch_drep_stake_peers` | Same-epoch DRep cohort signals |
| `voted_proposal_count`, `drep_vote_row_count` | Proposal voting activity for the delegated DRep |
| `same_block_points`, `delegation_sync_points`, `cross_root_points`, `current_drep_points`, `governance_activity_points` | Positive scoring components |
| `service_like_penalty`, `fragmentation_penalty` | Negative scoring components |
| `behavior_score`, `behavior_flags`, `confidence_class`, `confidence_rank`, `scoring_model` | Final deterministic confidence output |

The committed top cut contains only clusters with `behavior_score >= 5`; rows below that threshold exist in the release-asset full table. Scoring weights and class thresholds are recorded in `data/manifests/genesis-drep-behavior-manifest.json`.

Important: these are governance exposure surfaces. They are not custody, ownership, identity, or intent claims. See `docs/21_GENESIS_DREP_BEHAVIOR_ANALYSIS.md` and `docs/06_LIMITATIONS.md`.

## `governance_genesis_spo_by_pool`

Source: Genesis-to-SPO surface export → `data/small/governance_genesis_spo_by_pool.csv`.

Build command (maintainer-only; requires `ABCDE_SSH`):

```bash
TRACE_STAGE_SCHEMA=abcde_forensics_stage_founders_depth14 bash scripts/build_genesis_spo_surface_remote.sh
```

The full per-UTxO surface is exported to `data/release/genesis_current_spo_surface.csv` (release asset, not committed). This committed rollup answers: where is traced current value staked, per root combination and latest observed pool target?

| column | meaning |
| --- | --- |
| `snapshot_utc`, `trace_schema` | Build timestamp and staged trace schema |
| `root_combo` | `+`-joined root seeds whose traces reach the UTxOs |
| `latest_pool_id_bech32` | Latest observed SPO delegation target, or `NOT_DELEGATED_OR_NO_STAKE` |
| `ticker_name`, `pool_name` | Off-chain pool metadata when available |
| `dedup_current_utxos`, `distinct_stake_addresses` | Current live traced UTxO and credential counts, deduped by UTxO |
| `dedup_current_lovelace`, `dedup_current_ada` | Current traced value under this pool target |
| `min_trace_depth` | Minimum trace depth among the rolled-up UTxOs |
| `latest_pool_active_epoch` | Latest delegation active epoch observed |

## `governance_genesis_pool_drep_matrix`

Source: same surface → `data/small/governance_genesis_pool_drep_matrix.csv`.

Pool x DRep cross-tab of traced current value (top 500 rows by value): for each latest pool target, where is the same stake credential's vote delegation pointed? `NO_DREP_DELEGATION` marks credentials with no observed vote delegation.

## `governance_genesis_pool_operator_links`

Source: ABCDE/db-sync pool registration certificates joined against all-time staged trace membership → `data/small/governance_genesis_pool_operator_links.csv`.

One row per (pool, link role, linked stake address) where the pool's latest registration lists an **owner** or **reward address** stake credential that is itself reached by a Genesis trace. This is registration-certificate linkage — stronger than delegation alone, but still not custody, beneficial-ownership, identity, or intent evidence.

| column | meaning |
| --- | --- |
| `pool_id_bech32` | Pool whose latest registration certificate contains the link |
| `link_role` | `owner` or `reward_address` |
| `linked_stake_address` | Trace-reached stake credential in the certificate |
| `min_trace_depth` | Minimum depth at which any trace reached this credential — filter on this; deep links are diluted |
| `root_combo` | Root seeds whose traces reach the credential |
| `pool_active_epoch_no`, `pledge_lovelace`, `registration_tx_hash` | Registration context |

## `staged_trace_depth16_profile`

Source: all-roots depth-16 staged trace (`abcde_forensics_stage_depth16`) → `data/small/staged_trace_depth16_profile.csv`, built by `sql/30_behavior/staged_trace_depth_profile.sql`.

Per (root seed, depth): traced UTxO rows, distinct stake credentials, live-unspent rows, and live-unspent value. This is the dilution receipt for the deepest public trace cut (12.77M rows; fourth entry now traced to depth 16, beyond its previous depth-10 coverage).

**Read `total_lovelace` carefully:** at depth d, *every output* of a transaction that consumed a traced UTxO joins the trace, so summed output value at deep depths vastly exceeds the seed allocation (overbroad taint through exchanges and shared infrastructure). Use `live_unspent_lovelace` and behavior/confidence classification for any current-value statement; never quote deep-depth `total_lovelace` as genesis-attributable value.

The matching whole-run summary is `data/small/staged_trace_depth16_summary.csv` (rows per depth, cross-entity merge candidates per root combo). The full ~528K-row depth-16 cross-entity merge candidate set is a release asset (`data/release/staged_cross_entity_merges_depth16.csv`, `AUDIT_CANDIDATE_SET` — requires classification before any claim).

## `governance_genesis_delegation_timeline`

Source: ABCDE/db-sync delegation + vote-delegation certificates joined against all-time staged trace membership → `data/small/governance_genesis_delegation_timeline.csv`.

Per (cert type, root combo, epoch): how many delegation certificates traced credentials submitted, how many distinct credentials moved, and toward how many distinct targets. The per-certificate detail (573,716 SPO + 45,478 DRep certs for 359,128 traced credentials at depth 14) is exported to `data/release/genesis_delegation_history.csv` (release asset, not committed).

| column | meaning |
| --- | --- |
| `snapshot_utc`, `trace_schema` | Build timestamp and staged trace schema |
| `cert_type` | `spo_delegation` or `drep_vote_delegation` |
| `root_combo` | Root seeds whose traces reach the credential |
| `epoch_no` | Epoch of the certificate's block |
| `cert_count` | Certificates observed |
| `distinct_stake_addresses` | Distinct credentials submitting certificates |
| `distinct_targets` | Distinct pools/DReps targeted |

## `governance_actions_catalog`

Source: ABCDE/db-sync `gov_action_proposal` → `data/small/governance_actions_catalog.csv`.

Reference catalog of every on-chain Conway governance action with lifecycle epochs (`proposed/ratified/enacted/dropped/expired`), deposit, type, and anchor URL/hash. Join `gov_action_proposal_id` or `proposal_tx_hash` against `governance_genesis_behavior_by_proposal` to put proposal-level exposure rollups in context.

## `db_tip_receipt` / `build_info`

Source: warehouse tip query at build time → `data/small/db_tip_receipt.csv`, loaded into the DuckDB as `build_info`.

| column | meaning |
| --- | --- |
| `generated_utc` | UTC timestamp when the receipt was written |
| `db_tip_block`, `db_tip_time`, `db_tip_epoch` | Maximum block number, block time, and epoch in the source warehouse at build time |
| `source` | Source host and database, e.g. `abcde:cexplorer_replica` |
| `staleness_note` | Free-text staleness warning; empty when the warehouse is at chain tip |

Query `build_info` before answering any current-state question; the committed cut is a snapshot at this tip, not a live chain view.

## `iog_pool_state_validation`

Source: ABCDE/db-sync pool registration/retirement/epoch stake tables → `data/small/iog_pool_state_validation.csv`.

This validates IOG1/IOG2 live pool status independently from trace-derived delegation rollups.

| column | meaning |
| --- | --- |
| `label`, `pool_view`, `ticker_name` | Pool identity |
| `tip_epoch`, `tip_block`, `tip_time_utc` | Chain tip used by the validation query |
| `retiring_epoch`, `is_retired_at_tip` | Retirement state at tip |
| `latest_epoch_stake_epoch`, `latest_epoch_active_stake_ada` | Latest epoch stake row if the pool is active |

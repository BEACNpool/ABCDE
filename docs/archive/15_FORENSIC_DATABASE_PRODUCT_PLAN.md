# Full Forensic Database Product Plan

Goal: make ABCDE a public, auditable forensic database for Cardano genesis ADA flows, suitable for community review and governance-context decision making.

## Product promise

A community member should be able to answer:

- Which founding-entity seed did this ADA likely descend from?
- What hops did it take?
- Where did founder-descended ADA merge, split, or route through shared infrastructure?
- Which SPOs received delegation from traceable founder-descended stake credentials?
- Which DReps received governance delegation from traceable founder-descended stake credentials?
- What is FACT vs inference?
- What exact query/artifact supports each claim?

## Database layers

### 1. Source receipts

Small committed receipts and large release artifacts:

- seed registry
- seed tx verification
- seed output receipts
- archived sale-stat source + derived sale-ticket signal
- legacy regression baselines

### 2. Trace membership

Core public tables:

- `trace_utxos`
- `trace_spends`
- `trace_paths` or path receipts for selected claims
- `trace_frontier`

Minimum identity key:

```text
(root_seed_id, tx_hash, tx_out_index)
```

Dedup rule: keep minimum depth per root seed + UTxO.

### 3. Flow events

Derived from trace membership:

- `cross_entity_merge_inputs`
- `cross_entity_merges`
- `cross_entity_merge_outputs`
- `split_events`
- `exchange_first_touch_events`
- `large_exit_events`
- `reactivation_events`

### 4. Stake/governance behavior

Tables for traceable stake credentials:

- `trace_stake_credentials`
- `stake_pool_delegations`
- `stake_pool_delegation_rollups`
- `stake_drep_delegations`
- `stake_drep_delegation_rollups`
- `known_pools`
- `known_dreps`

Community-facing outputs:

- SPOs delegated to by founder-descended stake credentials
- DReps delegated to by founder-descended stake credentials
- time-aligned delegation changes
- evidence grade and lineage for every label

### 5. Labels / inference overlays

Labels must never overwrite facts.

- `labels.address_labels`
- `labels.pool_labels`
- `labels.drep_labels`
- `labels.entity_inferences`

All inferred labels need:

- source
- method
- confidence/grade
- date
- caveat

## Artifact policy

Commit to git:

- code
- docs
- small receipts under ~1 MB when practical
- manifests/checksums
- summary CSVs

Do not commit casually:

- multi-GB trace tables
- depth-11+ full exports
- large Parquet/DuckDB cuts

Publish larger artifacts as release assets / object storage with SHA-256 manifests.

## Near-term build order

1. Expand from seed cut into traceable stake credentials.
2. Extract SPO delegation history for traceable stake credentials.
3. Extract DRep delegation history for traceable stake credentials.
4. Publish first governance rollups.
5. Build staged server-side trace extraction with dedupe.
6. Rebuild full cross-entity merge inventory and compare to preserved baseline.
7. Add community-facing HTML/Markdown summary.

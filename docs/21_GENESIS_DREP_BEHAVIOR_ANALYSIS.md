# Genesis-to-DRep Behavior Analysis

This note defines the next audit track that combines deep Genesis ADA tracing with standardized top-DRep profiling.

The goal is to identify trace-derived behavior patterns first, then cross-reference those patterns against current DRep voting-power surfaces. The order matters: the trace should produce auditable clusters and confidence bands before any DRep-facing interpretation is made.

## Audit Question

Can current DRep voting power be segmented by high-confidence Genesis ADA trace behavior?

Useful sub-questions:

- Which current DRep targets receive voting power from stake credentials reached by deep Genesis traces?
- Which traced current UTxOs look retained-like, custodian-like, exchange-like, shared-infrastructure-like, or unknown?
- Which top DReps have unusually high exposure to specific Genesis roots or behavior classes?
- For a given proposal or voting epoch, how much trace-derived voting power appears aligned for, against, abstain, no-confidence, or not-yet-voted?

## Evidence Boundary

Allowed claims:

- `FACT`: staged trace membership, live-unspent status, latest DRep delegation target, DRep distribution amount, vote record, pool affiliation, timestamp, epoch, and artifact hash.
- `STRONG_INFERENCE`: stable delegation cohorts, synchronized behavior, repeated co-spend patterns, retained-like cluster behavior after explicit classification.
- `WORKING_HYPOTHESIS`: possible coordinated voting surface or founder-aligned governance influence.
- `UNKNOWN`: beneficial ownership, legal identity, custody, intent, nationality, or off-chain coordination.

Do not state that a DRep, founding entity, company, or person controls funds solely because traced stake credentials delegate voting power to a DRep.

## Required Inputs

- Deep staged trace membership from `abcde_forensics_stage_*` schemas.
- Live-unspent filter from db-sync `tx_in` anti-join.
- Latest DRep delegation per stake credential from `public.delegation_vote`.
- Current DRep distribution from `public.drep_distr`.
- Proposal vote rows from governance tables when doing proposal-specific analysis.
- Public labels/classifications with provenance and confidence, never private override notes.

## Implementation Status

The first executable pass now exists.

- Remote staged-table builder: `sql/30_behavior/build_genesis_governance_surface_tables.sql`
- Surface export query: `sql/30_behavior/genesis_current_governance_surface.sql`
- DRep proposal vote export: `sql/30_behavior/drep_proposal_votes.sql`
- Runner: `scripts/build_genesis_drep_behavior_surface_remote.sh`
- Local rollup builder: `scripts/build_genesis_drep_behavior_rollups.py`
- Manifest: `data/manifests/genesis-drep-behavior-manifest.json`
- Confidence signal top cut: `data/small/governance_genesis_behavior_signals_top.csv`
- Full confidence signal output: `data/release/governance_genesis_behavior_signals_full.csv`
- Freshness receipt: `data/small/db_tip_receipt.csv`

The SPO-side companion surface shares the same staged trace membership:

- SPO surface export: `sql/30_behavior/genesis_current_spo_surface.sql` → `data/release/genesis_current_spo_surface.csv`
- Pool operator linkage: `sql/30_behavior/genesis_pool_operator_links.sql` → `data/small/governance_genesis_pool_operator_links.csv`
- Delegation cert history: `sql/30_behavior/genesis_delegation_history.sql` → `data/release/genesis_delegation_history.csv`, with the committed epoch rollup `data/small/governance_genesis_delegation_timeline.csv`
- Governance actions catalog: `sql/30_behavior/governance_actions_catalog.sql` → `data/small/governance_actions_catalog.csv`
- Runner: `scripts/build_genesis_spo_surface_remote.sh`; local rollups: `scripts/build_genesis_spo_rollups.py` → `data/small/governance_genesis_spo_by_pool.csv`, `data/small/governance_genesis_pool_drep_matrix.csv`

Default run target:

```bash
TRACE_STAGE_SCHEMA=abcde_forensics_stage_founders_depth14 bash scripts/build_genesis_drep_behavior_surface_remote.sh
```

The full shared surface is exported to `data/release/genesis_current_governance_surface.csv` and is intentionally not committed to git. Small public rollups are committed under `data/small/`.

Current founder depth-14 run:

- Full surface: `82,494` current traced rows.
- DRep vote export: `22,964` DRep vote rows.
- Full confidence signal table: `49,032` stake-credential cluster rows.
- Committed top signal cut: `3,161` stake-credential cluster rows with `behavior_score >= 5`.
- DRep behavior rollup: `262` data rows.
- Root x DRep behavior rollup: `333` data rows.
- Cluster rollup: top `1,000` stake-address clusters by traced current value.
- Proposal behavior rollup: `15,183` data rows.

The first confidence model is `heuristic_v1_public_signals`. It is a public, deterministic scoring layer over the shared surface. It does not identify owners.

Current signal bands:

| confidence class | clusters | current ADA |
| --- | ---: | ---: |
| `trace_only` | 24,978 | 293,690,928.395440 |
| `weak_behavior_signal` | 20,893 | 265,434,805.909785 |
| `coordinated_like` | 2,995 | 190,547,351.036935 |
| `probable_retained_like` | 85 | 2,690,609.981487 |
| `high_confidence_retained_like` | 81 | 2,582,069.060614 |

These are audit-prioritization flags. They are not ownership, custody, identity, or intent claims.

## Shared Query Shape

Build the analysis around one canonical table or materialized view:

```text
genesis_current_governance_surface
```

Minimum columns:

```text
snapshot_utc
trace_schema
root_seed_id
tx_id
tx_hash
tx_out_index
min_depth
value_lovelace
stake_address_id
stake_address
output_epoch_no
output_block_no
output_block_time_utc
latest_drep_id_bech32
latest_drep_hash_id
latest_vote_epoch
drep_distribution_epoch
drep_voting_power_lovelace
behavior_class
behavior_confidence
classification_reason
classification_source
```

Then derive public CSV cuts from that shared surface:

- `governance_genesis_behavior_signals_top.csv` in git; full signal table as a release artifact
- `governance_genesis_behavior_by_drep.csv`
- `governance_genesis_behavior_by_root_drep.csv`
- `governance_genesis_behavior_by_proposal.csv`
- `governance_genesis_behavior_clusters.csv`

## Behavior Classes

Start with conservative, falsifiable classes:

| class | meaning |
| --- | --- |
| `retained_like` | high-confidence retained-pattern cluster after repeated behavior checks |
| `high_confidence_retained_like` | high score from cross-root, timing, and delegation/vote signals |
| `probable_retained_like` | strong but incomplete retained-pattern evidence |
| `coordinated_like` | multiple timing/delegation/root signals line up |
| `weak_behavior_signal` | one or more useful signals, not enough to interpret |
| `trace_only` | reached by lineage with no behavior score |
| `custodian_or_service_like` | recognizable exchange, custodian, staking service, or pooled infrastructure signal |
| `shared_infrastructure_like` | behavior suggests common infrastructure but not common beneficial ownership |
| `fragmented_unknown` | trace continues into many small or weakly linked outputs |
| `no_stake_or_byron` | current output has no stake credential and cannot be DRep-mapped |
| `overbroad_or_excluded` | trace membership exists but should not be used for governance inference |
| `unknown` | not classified yet |

The scored default is `trace_only`. Promotion above `trace_only` requires public signal columns and reproducible query receipts.

## Confidence Scoring

`heuristic_v1_public_signals` scores stake-credential clusters using only public/reproducible signals from the shared surface and DRep vote export.

Positive points:

| signal | points |
| --- | ---: |
| same-block hop event | +2 |
| repeated same-block hop events | +3 |
| same-epoch DRep cohort | +2 |
| current cluster spans multiple Genesis roots | +4 |
| current DRep delegation exists | +1 |
| delegated DRep has proposal vote rows | +1 |

Negative points:

| signal | points |
| --- | ---: |
| service-like block batch | -5 |
| fragmented single-root cluster with 100+ current UTxOs | -3 |

Confidence classes:

| class | rule |
| --- | --- |
| `trace_only` | no positive behavior score |
| `weak_behavior_signal` | score >= 2 |
| `coordinated_like` | score >= 5 |
| `probable_retained_like` | score >= 8 and current cluster spans multiple roots |
| `high_confidence_retained_like` | score >= 10 with cross-root and same-block signals |
| `custodian_or_service_like` | service-like batch penalty triggered |

Each row carries `behavior_flags`, component point columns, and `scoring_model`.

## Confidence Ladder

1. Trace membership only: useful for inventory, not for influence claims.
2. Live-unspent trace membership: useful for current surface estimates.
3. Stake credential and latest DRep delegation attached: useful for current voting-power exposure.
4. Behavior class assigned with receipts: useful for confidence-banded DRep/governance analysis.
5. Proposal vote joined: useful for proposal-specific alignment summaries.

Do not skip from step 2 to governance conclusions.

## First Implementation Pass

1. DONE: Rebuild or reuse a fresh staged trace snapshot at the target depth, starting with founder-only depth 14 because it already has known comparison receipts.
2. DONE: Export current live-unspent traced UTxOs with stake credentials and latest DRep target.
3. DONE: Deduplicate by current UTxO before summing value across overlapping roots.
4. DONE: Add behavior-class scaffolding with all rows defaulting to `unknown`.
5. DONE: Add proposal-specific joins as a mechanical exposure surface.
6. NEXT: Port the existing IOG confidence-band logic into the shared behavior-class model.
7. NEXT: Regenerate top-DRep profile exposure from the shared staged surface instead of preserved legacy trace receipts.
8. NEXT: Add proposal-specific public interpretation only after classification rules, freshness, hashes, and review notes are published.

## Proposal-Specific Use

For a governance action, report:

- total current DRep voting power by DRep vote choice
- trace-derived voting power by behavior class and root seed
- share of each top DRep's voting power that comes from classified Genesis-trace surface
- exclusions and unknowns
- snapshot timestamp, trace schema, db-sync tip, proposal id, and artifact hashes

Recommended language:

> This proposal view shows current voting-power exposure from classified Genesis-trace audit surfaces. It is not an ownership, custody, or intent claim.

## Public Reporting Rule

Publish the table/CSV, manifest hash, query source, db-sync tip, and classification rules before using the result in any public recommendation or narrative.

# Warehouse Research Program

This is the maintainer workflow for using the full ABCDE PostgreSQL warehouse
to answer questions that the compact public DuckDB cannot answer alone.

## Operating rule

1. Start with `data/abcde_genesis.duckdb` and query `build_info`.
2. Use the warehouse only when the compact cut lacks the required rows,
   columns, trace depth, or full-chain context.
3. Treat replicated `public.*` as read-only.
4. Put reusable derived work in project-owned staging schemas or export it as
   deterministic CSV, Parquet, or DuckDB artifacts.
5. Every result must record the SQL, source tip, generation time, row count,
   artifact hash, exclusions, and evidence grade.
6. Publish data and receipts before using a result in a public narrative.

The warehouse is currently frozen at block `13520244`, epoch `635`,
`2026-06-07 18:44:37 UTC`. Historical queries remain valid through that
boundary. Live-unspent, delegation, governance, and voting-power results are
snapshots at that boundary, not current Cardano state.

## Available server-side surfaces

Read-only inventory observed on 2026-06-13. Row counts below are PostgreSQL
planner estimates and must not be cited as exact result counts.

| Schema | Main surface | Estimated rows | Approximate size |
|---|---|---:|---:|
| `abcde_forensics_stage_depth10` | `trace_utxos` | 14,741 | 5.7 MiB |
| `abcde_forensics_stage_founders_depth12` | `trace_utxos` | 311,823 | 117 MiB |
| `abcde_forensics_stage_founders_depth13` | `trace_utxos` | 1,156,678 | 433 MiB |
| `abcde_forensics_stage_founders_depth14` | `trace_utxos` | 2,836,455 | 1.03 GiB |
| `abcde_forensics_stage_depth16` | `trace_utxos` | 12,775,278 | 4.63 GiB |

The founder depth-14 schema also contains:

- `cross_entity_merges` and `cross_entity_merge_inputs`
- `current_live_utxos`
- `current_iog_utxos`
- `current_latest_vote`
- `current_governance_surface`

These tables carry exact transaction, output, epoch, block, and block-time
fields. The governance surface additionally carries latest DRep target,
observed DRep distribution, behavior classification fields, and the source
snapshot.

## Priority research lanes

### P0 - Provenance and inventory

- Generate a machine-readable warehouse inventory with exact row counts for
  publishable tables and estimates for large internal staging tables.
- Record definitions, columns, indexes, source tip, creation time, and the
  script or SQL that created each derived table.
- Reconcile the public schema catalog with warehouse-only surfaces.
- Replace the placeholder extraction and publishing scripts with a narrow,
  receipt-producing orchestration path.

### P1 - Cross-merge classification

- Explain the 67 legacy cross-merge rows not recovered by the founder
  depth-14 staged method.
- Classify the 22,371 additional candidates as direct merge, inherited merge,
  shared infrastructure/custody candidate, overbroad taint, or excluded.
- Measure how classifications change at depths 12, 13, 14, and 16.
- Publish the broad candidate set separately from reviewed findings.

### P1 - IOG retained-balance confidence bands

- Deduplicate the current IOG-descended UTxO set by transaction output.
- Classify traced value into retained, service/custodian, exchange-likely,
  moved-forward unknown, and excluded/overbroad categories.
- Separate pool delegation, DRep delegation, and uncredentialed outputs.
- Report low/base/high confidence bands. Never describe trace membership as
  beneficial ownership.

### P1 - Genesis-to-governance behavior

- Port the existing IOG confidence logic into the shared behavior model.
- Regenerate top-DRep exposure from the staged depth-14 surface.
- Quantify exposure by root, trace depth, stake bucket, delegation cohort, and
  behavior class.
- Add proposal-specific joins only after classification rules and snapshot
  receipts are published.

### P2 - Temporal behavior

- Measure dormancy, reactivation, movement cadence, and value decay by root.
- Identify same-block and same-epoch cross-root convergence.
- Compare first-touch, stake registration, pool delegation, and DRep
  delegation timing.
- Build watcher datasets only after the upstream warehouse resumes advancing.

### P2 - Metadata and independent cross-checks

- Compare db-sync pool and DRep metadata with Koios and original metadata
  documents.
- Inventory disagreements without silently preferring one source.
- Preserve literal source values, retrieval time, and hashes.

## Question intake

For each new question, create or update an `AUDIT_BACKLOG.md` item containing:

- the exact question;
- why the compact DuckDB is insufficient, if warehouse access is needed;
- required tables and snapshot boundary;
- the SQL or script path;
- expected output class: receipt, candidate set, finding, or report;
- falsification tests and known alternative explanations;
- publication status.

Prefer one focused query lane over a giant multi-frontier query. Large
intermediate results stay server-side; public outputs should be the smallest
reviewable cut that answers the question.

## Completion gate

A warehouse-derived answer is ready for the repo only when:

- the source tip and generation timestamp are present;
- SQL is deterministic and read-only against replicated data;
- exact output row counts are recorded;
- exported artifacts have SHA-256 receipts;
- full addresses and transaction hashes are not truncated;
- FACT, INFERENCE, and UNCERTAINTY are separated;
- limitations and refutation paths are documented;
- public verifiers pass after the artifact is incorporated.


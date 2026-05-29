# Staged Trace Extraction

This branch now has a scalable server-side extraction path for the full forensic database.

The earlier bounded recursive query is useful for small proof receipts, but depth 11+ becomes planner-hostile. The staged extractor avoids one giant recursive CTE by materializing each frontier depth into server-side stage tables with a per-root UTxO primary key.

## Scripts

- `scripts/build_staged_trace_sql.py` — emits db-sync SQL.
- `scripts/build_staged_trace_remote.sh` — runs the SQL on ABCDE and writes a small summary CSV.
- `scripts/export_staged_cross_merges_remote.sh` — exports cross-entity merge rows from the staged views.

Default target schema:

```text
abcde_forensics_stage
```

Use `TRACE_STAGE_SCHEMA` to make disposable review schemas, e.g. `abcde_forensics_stage_depth3`.

## Stage tables

`trace_roots`
: selected seed roots.

`trace_utxos`
: deduped trace membership keyed by `(root_seed_id, tx_id, tx_out_index)`, with `min_depth`.

`trace_frontier`
: one row per newly discovered frontier UTxO.

`trace_spends`
: spending transactions observed from traced UTxOs.

`cross_entity_merge_inputs`
: view of traced inputs consumed by a transaction.

`cross_entity_merges`
: view of transactions consuming UTxOs from two or more root seeds.

## Safe review run

Depth 3 disposable schema:

```bash
TRACE_MAX_DEPTH=3 \
TRACE_STAGE_SCHEMA=abcde_forensics_stage_depth3 \
scripts/build_staged_trace_remote.sh data/small/staged_trace_depth3_summary.csv
```

Expected current summary:

```text
trace_utxos depth 0 = 4
trace_utxos depth 1 = 8
trace_utxos depth 2 = 14
trace_utxos depth 3 = 23
cross_entity_merges emurgo+fourth_entry_781m = 4
```

Note: the staged depth-3 UTxO total is smaller than `bounded_trace_depth3_db.csv` because staged extraction dedupes by `(root_seed_id, tx_id, tx_out_index)` and keeps minimum depth. The bounded proof query preserves path rows.

## Depth-10 candidate run

```bash
TRACE_MAX_DEPTH=10 \
TRACE_STAGE_SCHEMA=abcde_forensics_stage_depth10 \
scripts/build_staged_trace_remote.sh data/small/staged_trace_depth10_summary.csv

TRACE_STAGE_SCHEMA=abcde_forensics_stage_depth10 \
scripts/export_staged_cross_merges_remote.sh data/small/staged_cross_entity_merges_depth10.csv
```

Commit only small summaries/review cuts. Large merge inventories should be release artifacts with SHA-256 manifests, not casual git blobs.

## Founder-only regression mode

To compare against the preserved 521-row named-founder baseline without the fourth-entry root:

```bash
FOUNDERS_ONLY=1 TRACE_MAX_DEPTH=10 TRACE_STAGE_SCHEMA=abcde_forensics_stage_founders_depth10 \
scripts/build_staged_trace_remote.sh data/small/staged_trace_founders_depth10_summary.csv
```

The expected full 521-row inventory likely requires a deeper staged/release extraction, not a simple committed CSV.

## Depth-12 to depth-14 founder-only chase

Founder-only staged runs were extended past the initial depth-10 review cut.

| max depth | staged merge rows | overlap with preserved 521 | legacy missing | staged extras |
| ---: | ---: | ---: | ---: | ---: |
| 12 | 223 | 44 | 477 | 179 |
| 13 | 2,863 | 320 | 201 | 2,543 |
| 14 | 22,825 | 454 | 67 | 22,371 |

The full depth-14 merge export is intentionally kept under `data/release/` and ignored by git. Its hash is recorded in `data/manifests/staged-cross-merge-comparison.json`.

Decision: depth 14 is a useful release-artifact cut, but not a clean replacement for the old 521-row baseline. It recovers most legacy transactions while surfacing many more merge candidates under the newer staged membership rule. The next work is classification/filtering, especially explaining the 67 missing legacy rows and separating true new candidates from inherited/overbroad merges.

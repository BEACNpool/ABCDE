# F07 — Staged Trace Extraction and Founder Merge Candidate Set

## Claim

ABCDE v2 now has a scalable server-side trace extraction path that can materialize founder-descended UTxO membership by frontier depth, dedupe by minimum depth, and derive cross-entity merge candidates from staged tables.

## Audit labels

- **Finding status:** CANDIDATE_SET
- **Claim grade:** FACT for extraction mechanics; UNKNOWN until candidate rows are classified
- **Artifact class:** AUDIT_CANDIDATE_SET / AUDIT_REVIEW_CUT

This is an extraction receipt and candidate set, not a final attribution finding.

## Receipts

- Staged extractor SQL generator: `scripts/build_staged_trace_sql.py`
- Remote runner: `scripts/build_staged_trace_remote.sh`
- Merge exporter: `scripts/export_staged_cross_merges_remote.sh`
- Depth-3 summary: `data/small/staged_trace_depth3_summary.csv`
- Depth-10 all-root summary: `data/small/staged_trace_depth10_summary.csv`
- Depth-10 all-root merge review cut: `data/small/staged_cross_entity_merges_depth10.csv`
- Depth-10 named-founder-only summary: `data/small/staged_trace_founders_depth10_summary.csv`
- Depth-10 named-founder-only merge review cut: `data/small/staged_cross_entity_merges_founders_depth10.csv`

## Current depth-10 results

All four current roots:

- depth 0: 4 deduped UTxOs
- depth 10: 11,247 new frontier UTxOs
- cross-entity merge rows: 402
  - `emurgo+fourth_entry_781m`: 401
  - `emurgo+fourth_entry_781m+iog`: 1

Named founders only (`iog`, `emurgo`, `cf`):

- depth 0: 3 deduped UTxOs
- depth 10: 10,646 new frontier UTxOs
- cross-entity merge rows: 1
  - `emurgo+iog`: 1

## Interpretation

Depth 10 is useful as a public review cut but is still not the final full founder merge inventory. The preserved baseline remains 521 direct named-founder cross-seed consuming transactions, so the next extraction needs deeper staged tables and release-artifact handling rather than a normal committed CSV.

## Caveats

- Staged trace rows are deduped by `(root_seed_id, tx_id, tx_out_index)` and keep minimum depth. They are not path-preserving receipts.
- The bounded recursive query remains the right artifact when a human-readable path is needed for a small proof.
- Cross-entity merge rows are chain-behavior candidates. They do not prove off-chain ownership, intent, or legal control.

## Depth-12 to depth-14 comparison against the preserved 521-row baseline

| max depth | staged merge rows | overlap with baseline 521 | baseline missing | staged extras |
| ---: | ---: | ---: | ---: | ---: |
| 12 | 223 | 44 | 477 | 179 |
| 13 | 2,863 | 320 | 201 | 2,543 |
| 14 | 22,825 | 454 | 67 | 22,371 |

Depth 14 recovers **454 / 521** baseline transaction hashes. It still misses **67** baseline hashes and produces **22,371** additional staged candidates.

This is progress, but it is also a warning: the staged rule is intentionally broader than the preserved baseline. The audit product needs classification layers before presenting the depth-14 candidate set as anything stronger than an `AUDIT_CANDIDATE_SET`.

Tracked comparison receipt:

- `data/small/staged_cross_merge_comparison.csv`
- `data/manifests/staged-cross-merge-comparison.json`

Large local/release artifacts, not tracked in git:

- `data/release/staged_cross_entity_merges_founders_depth12.csv`
- `data/release/staged_cross_entity_merges_founders_depth13.csv`
- `data/release/staged_cross_entity_merges_founders_depth14.csv`

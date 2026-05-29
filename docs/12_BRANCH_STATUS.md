# Current Rebuild Status

Last verified locally with:

```bash
bash scripts/rebuild_seed_cut.sh
```

Result: clean rebuild and all verifiers pass.

## Current rebuilt surface

### Data artifacts

- `data/small/seed_registry.csv`
- `data/small/seed_anchor_db_verification.csv`
- `data/small/seed_outputs_db.csv`
- `data/small/seed_first_spends_db.csv`
- `data/small/seed_first_spend_inputs_db.csv`
- `data/small/fourth_entry_direct_cospend_db.csv`
- `data/small/fourth_entry_sale_ticket_signal.csv`
- `data/small/bounded_trace_depth3_db.csv`
- generated locally: `data/abcde_genesis_seed_registry.duckdb`

### Rebuilt findings

- `F01_named_founder_allocations.md`
- `F02_fourth_entry_first_spend_convergence.md`
- `F02b_fourth_entry_direct_cospend.md`
- `F03_fourth_entry_sale_ticket_origin_signal.md`

### Verification commands

```bash
python3 scripts/verify_seed_artifacts.py
python3 scripts/verify_finding_queries.py
```

Current finding-query verifier executes:

- `sql/10_findings/F01_named_founder_allocations.duckdb.sql`
- `sql/10_findings/F02_fourth_entry_first_spend_convergence.duckdb.sql`
- `sql/10_findings/F02b_fourth_entry_direct_cospend.duckdb.sql`
- `sql/10_findings/F03_fourth_entry_sale_ticket_signal.duckdb.sql`
- `sql/10_findings/bounded_trace_depth3_summary.duckdb.sql`

## Key evidence rebuilt from ABCDE/db-sync

- Four seed anchors are present in db-sync and match expected lovelace values.
- Each seed has one redemption output at index `0`.
- EMURGO and fourth-entry first spends both activate after ~`475.1` hours.
- Fourth-entry first spend `c8596b9c...` directly co-spends:
  - fourth-entry seed output, and
  - an EMURGO-descended UTxO at trace depth 2.
- Bounded depth-3 review-cut trace produces 53 rows and is safe to run.
- F03 sale-ticket signal is re-derived from archived `main2.json`.

## Known boundaries

- This is a clean public starting point, not a claim that every archived audit note has been re-derived.
- `legacy/` is preserved as archive/reference material, not the primary public workflow.


## Cross-merge baseline/probe state

- Legacy direct cross-seed baseline is captured in `data/manifests/legacy-cross-merge-baseline.json`.
- Baseline target: 521 direct cross-seed consuming txs; 308 clean.
- Depth-10 probe is recorded in `data/small/cross_merge_depth10_probe.csv`.
- Depth-10 is useful but insufficient for the full legacy founder-only inventory; full rebuild needs staged server-side tracing.


## Governance delegation rollups

- SPO target rollups: `5,175` rows in `data/small/governance_spo_delegation_targets.csv`.
- Latest SPO snapshots: `2,868` rows in `data/small/governance_spo_latest_targets.csv`.
- DRep target rollups: `390` rows in `data/small/governance_drep_delegation_targets.csv`.
- Latest DRep snapshots: `337` rows in `data/small/governance_drep_latest_targets.csv`.
- These are included in the local DuckDB artifact and verified by `scripts/verify_governance_rollups.py`.
- Metadata enrichment: `1,857` pool metadata rows and `184` DRep metadata rows currently available from db-sync.


## Staged trace extraction milestone

- Added server-side staged extraction scripts:
  - `scripts/build_staged_trace_sql.py`
  - `scripts/build_staged_trace_remote.sh`
  - `scripts/export_staged_cross_merges_remote.sh`
- Depth-3 staged test passed in disposable schema `abcde_forensics_stage_depth3`.
- Depth-10 all-root staged run produced:
  - `data/small/staged_trace_depth10_summary.csv`
  - `data/small/staged_cross_entity_merges_depth10.csv`
  - 402 cross-entity merge rows in the review cut.
- Depth-10 named-founder-only staged run produced:
  - `data/small/staged_trace_founders_depth10_summary.csv`
  - `data/small/staged_cross_entity_merges_founders_depth10.csv`
  - 1 `emurgo+iog` merge row at depth 10.
- Interpretation: staged extraction works; full 521-row legacy founder inventory still requires deeper staged/release extraction, not a normal git CSV.

## Deeper staged founder-only extraction

- Extended founder-only staged runs to depth 12, 13, and 14.
- Depth 14 staged frontier reached 1,679,543 new depth-14 UTxOs.
- Depth 14 exported 22,825 cross-entity merge candidates as a local/release artifact, not a committed git CSV.
- Comparison against preserved 521-row baseline:
  - depth 12: 44 overlap, 477 legacy missing
  - depth 13: 320 overlap, 201 legacy missing
  - depth 14: 454 overlap, 67 legacy missing
- Important interpretation: depth 14 is broader than the preserved baseline and produces 22,371 staged extras. These are audit candidates, not claims.

## IOG current bag audit cut

- Added `scripts/build_iog_current_bag_audit_remote.sh` to validate IOG current-bag claims from staged trace membership plus live db-sync unspent status.
- Depth-14 IOG staged trace currently resolves to **506,900,169.148536 ADA** in live-unspent descendant UTxOs.
- This is a trace-membership audit cut, not proof of current beneficial ownership.
- Pool-state correction:
  - IOG1 is active with latest epoch stake around **10.03M ADA**.
  - IOG2 retired at epoch **237**.
  - Trace-derived latest-delegation rollups must not be used as live pool-stake facts.
- Added IOG confidence-band receipts:
  - high-confidence coordinated retained-like core: **247,261,951.770785 ADA**
  - probable retained-like abstain surface: **278,747,238.425299 ADA**
  - trace-membership current upper bound remains **506,900,169.148536 ADA**

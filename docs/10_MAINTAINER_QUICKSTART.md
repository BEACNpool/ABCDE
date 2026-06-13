# Maintainer Quickstart

This is the current end-to-end v2 seed-cut rebuild path.

## Requirements

- SSH access to the ABCDE host.
- Remote ability to run read-only `psql` via `sudo -n -u postgres`.
- Python 3.12+.

Before extracting, read `docs/22_DATA_TOPOLOGY_AND_FRESHNESS.md` and verify the
warehouse tip. A healthy subscription state does not prove that the upstream
source is current.

## Setup

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements/base.txt
```

## Rebuild current seed cut

```bash
bash scripts/rebuild_seed_cut.sh
```

The script runs:

1. anchor tx verification against db-sync
2. seed output extraction
3. first-spend extraction
4. first-spend input composition extraction
5. fourth-entry direct co-spend extraction
6. bounded depth-3 trace extraction
7. governance rollups, metadata enrichment, value rollups, and top-DRep profile pack
8. local DuckDB/CSV artifact rebuild
9. local verifier

## Outputs

Small committed receipts:

- `data/small/seed_registry.csv`
- `data/small/seed_anchor_db_verification.csv`
- `data/small/seed_outputs_db.csv`
- `data/small/seed_first_spends_db.csv`
- `data/small/seed_first_spend_inputs_db.csv`
- `data/small/fourth_entry_direct_cospend_db.csv`
- `data/small/bounded_trace_depth3_db.csv`
- `data/small/governance_top_drep_profiles_current.csv`
- `data/small/governance_top_drep_stake_buckets.csv`
- `data/small/governance_top_drep_delegation_age_buckets.csv`
- `data/small/governance_top_drep_pool_affiliations.csv`
- `data/small/governance_top_drep_koios_crosscheck.csv`
- `data/small/governance_top_drep_genesis_trace_exposure.csv`
- `data/small/governance_top_drep_genesis_trace_exposure_by_root.csv`
- `data/small/governance_top_drep_genesis_trace_stickiness.csv`

Community DRep entrypoints:

- `profiles/dreps/README.md`
- `docs/18_DREP_PROFILE_PACK.md`
- `docs/19_QUERY_COOKBOOK.md`
- `reports/top_drep_profiles.md`

Generated compact DuckDB cut (committed so a plain clone is query-ready):

- `data/abcde_genesis.duckdb`
- `data/schema_catalog.json`
- `docs/SCHEMA.md`

Large extraction cuts belong in gitignored `data/release/` while under review
and in GitHub Releases with SHA-256 receipts when published. They must not be
described as available to public users merely because they exist on a
maintainer workstation.

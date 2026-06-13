# Start Here

ABCDE makes Cardano genesis ADA analysis reproducible and readable.

The public repo is intentionally small enough to review in git. Heavy extraction happens on the ABCDE warehouse; large DuckDB/Parquet or staged trace exports should be published as release artifacts with hashes, not committed as normal source files.

## Reader path

1. Read the generated community summary:
   - `reports/genesis_forensics_community_summary.md`
2. Review the confidence analysis:
   - `reports/genesis_ada_confidence_analysis.md`
3. Inspect the DRep profile pack:
   - `profiles/dreps/README.md`
   - `reports/top_drep_profiles.md`
   - `docs/18_DREP_PROFILE_PACK.md`
4. Run copy/paste examples from the query cookbook:
   - `docs/19_QUERY_COOKBOOK.md`
5. Review the Genesis-to-DRep behavior analysis:
   - `docs/21_GENESIS_DREP_BEHAVIOR_ANALYSIS.md`
6. Open the findings index:
   - `findings/INDEX.md`
7. Use the data dictionary to understand CSV/table columns:
   - `docs/03_DATA_DICTIONARY.md`
8. Check limitations before making claims:
   - `docs/06_LIMITATIONS.md`
9. Check the data tiers and current snapshot boundary:
   - `docs/22_DATA_TOPOLOGY_AND_FRESHNESS.md`
10. Review the IOGP pledge and voucher-address follow-up:
   - `reports/iogp_voucher_followup.md`
   - `findings/F09_iogp_voucher_followup.md`

## Maintainer path

1. Set up Python dependencies:

   ```bash
   python3 -m venv .venv
   . .venv/bin/activate
   pip install -r requirements/base.txt
   ```

2. Rebuild the current public cut:

   ```bash
   bash scripts/rebuild_seed_cut.sh
   ```

3. Review:
   - `docs/10_MAINTAINER_QUICKSTART.md`
   - `docs/12_BRANCH_STATUS.md`
   - `docs/22_DATA_TOPOLOGY_AND_FRESHNESS.md`
   - `docs/23_WAREHOUSE_RESEARCH_PROGRAM.md`
   - `data/manifests/public-artifacts-manifest.json`

## Core promises

- Source chain facts come from db-sync-derived `public.*` tables on ABCDE.
- Findings separate facts from inference and preserve refutation paths.
- Public datasets contain only the scoped subgraph needed for Genesis ADA forensics, not a full chain mirror.
- Large generated artifacts are release assets with SHA-256 receipts.
- On-chain flow evidence is not off-chain legal attribution.
- DRep delegation is voting power, not custody of delegated funds.

## Current known work queue

- Explain the remaining 67 preserved-baseline cross-merge rows not recovered by depth-14 staged extraction.
- Classify depth-14 staged extras into audited categories before making claims.
- Build the shared Genesis-to-DRep behavior surface from staged deep traces before using trace exposure in proposal-specific analysis (see `AUDIT_BACKLOG.md` B-004).
- Promote large staged trace outputs (full behavior surface, signals table, depth-12/13/14 candidate sets) as release artifacts only after manifesting and review.
- Follow `docs/23_WAREHOUSE_RESEARCH_PROGRAM.md` for warehouse-backed question intake, priorities, receipts, and publication gates.

# Executive Summary

## Scope
Cardano genesis ADA forensic repository documenting on-chain UTxO flow analysis derived from db-sync and exported artifacts already present in the repository.

## Data Source
Cardano db-sync PostgreSQL replica `cexplorer_replica`, synced past block `13,215,210` as documented in archived findings.

## Evidence Standard
Claims retain repository claim grades and are tied to evidence artifacts and reproducibility paths.

## Summary of Canonical Findings
- EMURGO_2 operational convergence, see `../findings/F01_emurgo2_operational_convergence.md`
- Founder redemption timeline, see `../findings/F02_founder_redemption_timeline.md`
- Cross-seed consuming transactions, see `../findings/F03_cross_seed_consuming_transactions.md`
- Clean three-way merge, see `../findings/F04_clean_three_way_merge.md`
- Shared 58-output splitter, see `../findings/F05_shared_58_output_splitter.md`
- Synchronized delegation swarm, see `../findings/F06_synchronized_delegation_swarm.md`
- Exchange liquidation, see `../findings/F07_exchange_liquidation.md`

## Where the Detailed Evidence Lives
- `../evidence/`
- `../queries/`
- `../scripts/`
- `../investigation/archived_findings/`

## Reproducibility Pointer
See `04_REPRODUCIBILITY.md`.

## Limitations Pointer
See `05_LIMITATIONS_AND_NON_ATTRIBUTION.md`.

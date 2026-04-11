# Executive Summary

## Scope
Data-only forensic repository documenting on-chain UTxO flow analysis derived from db-sync and related exported artifacts.

## Data Source
- `cexplorer_replica` db-sync derived data
- Historical exported CSV / JSON / markdown artifacts preserved in-repo

## Evidence Standard
Claims are graded by evidence strength and tied to supporting artifacts and reproducibility paths.

## Summary of Canonical Findings
- Founder allocation and redemption baseline: `../findings/F01_named_founder_allocations.md`
- EMURGO_2 operational convergence: `../findings/F02_emurgo2_operational_convergence.md`
- Cross-seed consuming transactions: `../findings/F03_cross_seed_consuming_transactions.md`
- Clean three-way merge and bridge path: `../findings/F04_clean_three_way_merge.md`, `../findings/A09_bridge_accumulator_before_three_way_merge.md`
- Shared infrastructure and routing behavior: `../findings/F05_shared_58_output_splitter.md`, `../findings/F06_synchronized_delegation_swarm.md`
- CF + EMURGO disbursement chain: `../findings/B01_f907b625_2b_disbursement_chain.md` through `../findings/B18_binance_on_chain_delegation_confirmation.md`
- Exchange liquidation and concentration: `../findings/F07_exchange_liquidation.md`, `../findings/F08_558b_mystery_exchange_address.md`, `../findings/F09_genesis_concentration.md`

## Where the Detailed Evidence Lives
- Evidence artifacts: `../evidence/`
- Historical source docs: `../investigation/archived_findings/`, `../investigation/archived_notes/`

## Reproducibility Pointer
See `04_REPRODUCIBILITY.md`.

## Limitations Pointer
See `05_LIMITATIONS_AND_NON_ATTRIBUTION.md`.

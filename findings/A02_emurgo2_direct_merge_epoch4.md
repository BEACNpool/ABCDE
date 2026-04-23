# A02 — EMURGO_2 Direct Merge Epoch 4

## Label Note
"EMURGO_2" is a trace identifier for the 781,381,495 ADA genesis entry redeemed by transaction `5ec95a53fa3bb7dc56864bb6e75f369f00aa20e8d8cdc3b66b2fb88ec1b225ef`. It is not an attribution to EMURGO.

## Claim
The first post-dormancy spend of the EMURGO_2 genesis redemption output occurs in epoch 4 via transaction `c8596b9cd81f734f8129604ff86f23bd4a910465acb84ad9e9d1ac223ccb4a76`, which directly co-spends the 781,381,495 ADA EMURGO_2 redemption output alongside a 1,074,165,542 ADA EMURGO-descended UTxO from `743fd051...`. The EMURGO_2 redemption output sat dormant for 475.1111 hours before this spend; the EMURGO redemption output sat dormant for 475.0944 hours — a matching dormancy window.

## Grade
FACT — at the level of on-chain co-spend only.

## Scope and Non-Attribution
The epoch-4 direct co-spend establishes shared downstream infrastructure at hop 1 of the EMURGO_2 trace. It does not establish beneficial ownership. See `F02_emurgo2_operational_convergence.md` and `../HYPOTHESES.md` (H-001 vs. H-002).

## Data Basis
Listed in the linked historical findings and supporting artifacts already present in the repository.

## Core Evidence
- `evidence/csv/emurgo2_first_spend_2026-04-08.csv`
- `evidence/csv/emurgo2_anchor_outputs_2026-04-08.csv`

## Key Transactions / Addresses / Stake Credentials
Use the linked evidence files and historical findings for the exact documented items.

## Supporting Evidence Files
- `evidence/csv/emurgo2_first_spend_2026-04-08.csv`
- `evidence/csv/emurgo2_anchor_outputs_2026-04-08.csv`

## Reproduction
- `queries/validation/emurgo2_direct_merge_checks.sql`

## Limitations
See `../docs/05_LIMITATIONS_AND_NON_ATTRIBUTION.md`.

## Related Hypotheses
- `../HYPOTHESES.md` (H-001, H-002)

## Source Lineage
- `investigation/archived_findings/FULL_FINDINGS_2026-04-08_ADDENDUM.md`

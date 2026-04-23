# A01 — EMURGO_2 Frontier Identity

## Label Note
"EMURGO_2" is a trace identifier for the 781,381,495 ADA genesis entry redeemed by transaction `5ec95a53fa3bb7dc56864bb6e75f369f00aa20e8d8cdc3b66b2fb88ec1b225ef`. It is not an attribution to EMURGO.

## Claim
The published `current_unspent.csv` frontier for the EMURGO_2 trace is bit-for-bit identical to the published frontier for the main EMURGO trace:

- EMURGO frontier UTxOs: 49,089.
- EMURGO_2 frontier UTxOs: 49,089.
- Shared `dest_tx_out_id` intersection: 49,089.
- EMURGO_2 ⊆ EMURGO and EMURGO ⊆ EMURGO_2.
- Shelley stake-credential overlap: 6,216 / 6,216.

## Grade
FACT — at the level of set identity only.

## Scope and Non-Attribution
Set identity of the current UTxO frontier proves the two traces landed on the same downstream UTxO set, not that a single beneficial owner controls them. See `F02_emurgo2_operational_convergence.md` and `../HYPOTHESES.md` (H-001 vs. H-002).

## Data Basis
Listed in the linked historical findings and supporting artifacts already present in the repository.

## Core Evidence
- `evidence/overlaps/emurgo2_frontier_overlap_2026-04-08.csv`

## Key Transactions / Addresses / Stake Credentials
Use the linked evidence files and historical findings for the exact documented items.

## Supporting Evidence Files
- `evidence/overlaps/emurgo2_frontier_overlap_2026-04-08.csv`

## Reproduction
- `queries/validation/emurgo2_direct_merge_checks.sql`

## Limitations
See `../docs/05_LIMITATIONS_AND_NON_ATTRIBUTION.md`.

## Related Hypotheses
- `../HYPOTHESES.md` (H-001, H-002)

## Source Lineage
- `investigation/archived_findings/FULL_FINDINGS_2026-04-08_ADDENDUM.md`

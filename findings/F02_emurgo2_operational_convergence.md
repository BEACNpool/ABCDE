# F02 — EMURGO_2 Operational Convergence

## Label Note
"EMURGO_2" is a trace identifier for the 781,381,495 ADA genesis entry redeemed by transaction `5ec95a53fa3bb7dc56864bb6e75f369f00aa20e8d8cdc3b66b2fb88ec1b225ef`. It is not an attribution to EMURGO.

## Claim
From the first post-dormancy spend in epoch 4 onward, the 781,381,495 ADA genesis entry's downstream trace is operationally indistinguishable from the main EMURGO trace:

- First EMURGO_2 spend (tx `c8596b9c...`) directly co-spends with an EMURGO-descended UTxO in the same transaction.
- Current-unspent frontier UTxO overlap with EMURGO: 49,089 / 49,089 (100%).
- Shelley stake-credential overlap with EMURGO: 6,216 / 6,216 (100%).
- Per-credential deoverlap ADA totals are identical to those of the EMURGO trace.

## Grade
FACT — at the level of operational convergence only.

## Scope and Non-Attribution
This finding is FACT for operational behavior, not for beneficial ownership. Byron-era shared infrastructure cannot distinguish co-ownership from custodial administration. The origin-of-funds question for the 781,381,495 ADA entry is tracked separately in `F10_781m_sale_ticket_origin_signal.md` and remains UNRESOLVED.

Two competing hypotheses are consistent with this FACT:
- **H-001** — EMURGO_2 was co-owned with EMURGO
- **H-002** — EMURGO_2 was administered by EMURGO for a separate beneficial owner

Both are WORKING HYPOTHESIS, UNRESOLVED. See `../HYPOTHESES.md`.

## Data Basis
Listed in the linked historical findings and supporting artifacts already present in the repository.

## Core Evidence
- `evidence/markdown/emurgo2_convergence_evidence_2026-04-08.md`
- `evidence/csv/emurgo2_first_spend_2026-04-08.csv`
- `evidence/overlaps/emurgo2_frontier_overlap_2026-04-08.csv`
- `evidence/overlaps/emurgo2_vs_emurgo_anchor_comparison_2026-04-08.csv`

## Key Transactions / Addresses / Stake Credentials
Use the linked evidence files and historical findings for the exact documented items.

## Supporting Evidence Files
- `evidence/markdown/emurgo2_convergence_evidence_2026-04-08.md`
- `evidence/csv/emurgo2_first_spend_2026-04-08.csv`
- `evidence/overlaps/emurgo2_frontier_overlap_2026-04-08.csv`
- `evidence/overlaps/emurgo2_vs_emurgo_anchor_comparison_2026-04-08.csv`

## Reproduction
- `queries/validation/emurgo2_classification_checks.sql`
- `queries/validation/emurgo2_direct_merge_checks.sql`

## Limitations
See `../docs/05_LIMITATIONS_AND_NON_ATTRIBUTION.md`.

## Related Hypotheses
- `../HYPOTHESES.md` (H-001, H-002)

## Source Lineage
- `investigation/archived_findings/MASTER_FINDINGS.md`
- `investigation/archived_findings/FULL_FINDINGS_2026-04-06.md`
- `investigation/archived_findings/FULL_FINDINGS_2026-04-08_ADDENDUM.md`

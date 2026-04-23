# B04 — EMURGO_2 Anchor Confirmation

## Label Note
"EMURGO_2" is a trace identifier for the 781,381,495 ADA genesis entry redeemed by transaction `5ec95a53fa3bb7dc56864bb6e75f369f00aa20e8d8cdc3b66b2fb88ec1b225ef`. It is not an attribution to EMURGO.

## Claim
The EMURGO_2 genesis redemption transaction `5ec95a53...` consumed a single genesis-era source output of exactly 781,381,495 ADA from Byron address `Ae2tdPwUPEZB2zrbrdDkQNPdCndghMUJN8o8XjMaJ1jXgwVevf7TUrdmsSP` and redeemed it to `DdzFFzCqrhspiThx6UaeJASmHTbwbXp2FtdCkF9AU9QXPF9D8sUC7Fqrv9bmYkxradBbqMrSxukTTsqCPNPwRh5PHazdiwWTuJYVMMaf`. The redemption was executed at 2017-09-28 10:09:11 UTC — 5 minutes after the main EMURGO redemption (`242608fc...`, 2017-09-28 10:04:11 UTC).

## Grade
FACT — at the level of anchor transaction mechanics only.

## Scope and Non-Attribution
Sequential redemption timing and identical mechanics indicate a shared redemption operator at the anchor step. They do not establish that the 781,381,495 ADA source was itself an EMURGO allocation. For the origin-of-funds question see `F10_781m_sale_ticket_origin_signal.md`. For the co-ownership vs. administration question see `F02_emurgo2_operational_convergence.md` and `../HYPOTHESES.md`.

## Data Basis
Listed in the linked historical findings and supporting artifacts already present in the repository.

## Core Evidence
- `evidence/csv/emurgo2_anchor_metadata_2026-04-08.csv`
- `evidence/csv/emurgo2_anchor_outputs_2026-04-08.csv`

## Key Transactions / Addresses / Stake Credentials
Use the linked evidence files and historical findings for the exact documented items.

## Supporting Evidence Files
- `evidence/csv/emurgo2_anchor_metadata_2026-04-08.csv`
- `evidence/csv/emurgo2_anchor_outputs_2026-04-08.csv`

## Reproduction
- `queries/loaders/load_investigation_findings.sql`

## Limitations
See `../docs/05_LIMITATIONS_AND_NON_ATTRIBUTION.md`.

## Related Hypotheses
- `../HYPOTHESES.md` (H-001, H-002)

## Source Lineage
- `investigation/archived_findings/FULL_FINDINGS_2026-04-10_ADDENDUM.md`

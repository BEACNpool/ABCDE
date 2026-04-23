# A03 — Convergence Transaction c8596b9c

## Label Note
"EMURGO_2" is a trace identifier for the 781,381,495 ADA genesis entry redeemed by transaction `5ec95a53fa3bb7dc56864bb6e75f369f00aa20e8d8cdc3b66b2fb88ec1b225ef`. It is not an attribution to EMURGO.

## Claim
Transaction `c8596b9cd81f734f8129604ff86f23bd4a910465acb84ad9e9d1ac223ccb4a76` (epoch 4, 2017-10-18 05:15:51 UTC) is simultaneously the EMURGO_2 trace's hop 1 and the EMURGO trace's hop 3. It consumes two inputs — the EMURGO_2 redemption output (781,381,495 ADA) and an EMURGO-descended output from `743fd051...` (1,074,165,542 ADA) — and produces a single operational output of 1,855,547,037 ADA at `DdzFFzCqrhsu3iF6JfUTaapdWq2mXVRFukkS28WFYVDEqkgaaYttH8cT32credS99L5GaoUsEquqEPNH7ae88eKuDL6XsK5ZL56jkfLi`.

## Grade
FACT — at the level of single-transaction co-spend only.

## Scope and Non-Attribution
A single transaction consuming inputs from two distinct redemption lineages is proof of shared control at the spending-key level, not proof of shared beneficial ownership. See `F02_emurgo2_operational_convergence.md` and `../HYPOTHESES.md` (H-001 vs. H-002).

## Data Basis
Listed in the linked historical findings and supporting artifacts already present in the repository.

## Core Evidence
- `evidence/csv/emurgo2_first_spend_2026-04-08.csv`

## Key Transactions / Addresses / Stake Credentials
Use the linked evidence files and historical findings for the exact documented items.

## Supporting Evidence Files
- `evidence/csv/emurgo2_first_spend_2026-04-08.csv`

## Reproduction
- `queries/validation/emurgo2_direct_merge_checks.sql`

## Limitations
See `../docs/05_LIMITATIONS_AND_NON_ATTRIBUTION.md`.

## Related Hypotheses
- `../HYPOTHESES.md` (H-001, H-002)

## Source Lineage
- `investigation/archived_findings/FULL_FINDINGS_2026-04-08_ADDENDUM.md`

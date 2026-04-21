# ABCDE: Cardano Genesis ADA Forensics

## Scope
Data-only forensic repository documenting on-chain UTxO flow analysis derived from db-sync and related exported artifacts.

## Evidence Standard
Claims are graded by evidence strength and tied to supporting artifacts and reproducibility paths.

## Start Here
- Executive summary: `docs/00_EXECUTIVE_SUMMARY.md`
- Repository guide: `docs/01_REPOSITORY_GUIDE.md`
- Method and data provenance: `docs/02_METHOD_AND_DATA_PROVENANCE.md`
- Findings index: `docs/03_FINDINGS_INDEX.md`
- Reproducibility: `docs/04_REPRODUCIBILITY.md`
- Limitations and non-attribution: `docs/05_LIMITATIONS_AND_NON_ATTRIBUTION.md`
- Evidence index: `docs/06_EVIDENCE_INDEX.md`
- Changelog: `docs/07_CHANGELOG.md`

## Canonical Findings
See `findings/`

## Limitations
Byron-era shared infrastructure is a confounder, not a differentiator. Early co-spend, shared splitter behavior, and shared downstream routing for the 781,381,495 ADA fourth entry support the narrower claim that it was administered via infrastructure shared with EMURGO from epoch 4, but they do not distinguish beneficial ownership from custodial administration on current evidence. The stronger signal retained in this repository is the later Shelley-era delegation pattern, especially the 12 cross-delegating stake addresses spanning all three founding pool families.

## Historical Investigation Record
See:
- `investigation/archived_findings/`
- `investigation/archived_notes/`
- `investigation/open_questions/`

## License
See `LICENSE`

# Audit Backlog

This is not a separate narrative track. It is the canonical backlog of unresolved audit questions, refutation tests, and candidate sets for the Genesis ADA audit.

Labels follow `docs/02_GRADING.md`.

## B-001 — Fourth-entry relationship to EMURGO

- **Status:** BACKLOG
- **Claim grade:** WORKING_HYPOTHESIS
- **Artifact class:** AUDIT_BACKLOG

### Current facts

- The fourth-entry first downstream spend directly co-spends with an EMURGO-descended UTxO.
- Preserved legacy evidence reported strong frontier/stake overlap with the EMURGO trace.

### Open interpretations

1. Same beneficial owner as EMURGO.
2. Separate beneficial owner using shared EMURGO/Byron-era administration or custody infrastructure.
3. Another shared-infrastructure explanation not yet isolated.

### Refutation / classification tests

- Look for sustained downstream divergence in stake registration, delegation, DRep behavior, or spending control.
- Look for documentary or on-chain evidence tying the original buyer/holder directly to EMURGO beneficial ownership.
- Keep all outputs labeled as inference unless direct evidence closes the gap.

## B-002 — Founder cross-merge inventory classification

- **Status:** BACKLOG
- **Claim grade:** UNKNOWN until classified
- **Artifact class:** AUDIT_CANDIDATE_SET

### Current facts

- Legacy named-founder baseline: 521 direct cross-seed consuming transactions.
- Depth-14 staged founder cut recovers 454 of those legacy tx hashes.
- Depth-14 staged founder cut also produces 22,371 additional staged candidates.

### Required audit work

- Explain the 67 preserved baseline txs not recovered by the depth-14 staged method.
- Classify staged extras into:
  - clean direct founder merge
  - inherited merge
  - shared infrastructure/custody candidate
  - overbroad taint candidate
  - false positive / exclude
- Publish only classified rows as findings; keep the broad depth-14 set as a release artifact or candidate-set receipt.

## B-003 — Current IOG-descended retained-balance estimate

- **Status:** BACKLOG
- **Claim grade:** UNKNOWN / WORKING_HYPOTHESIS until fresh trace completes
- **Artifact class:** AUDIT_BACKLOG

### Current facts

- Depth-14 staged trace membership now shows about 506.9M ADA in currently unspent IOG-descended UTxOs.
- IOG1/IOG2 live pool-state validation corrected the earlier pool-delegation shortcut: IOG1 has about 10.03M active stake; IOG2 is retired.
- Beneficial ownership remains unproven; the 506.9M figure is trace membership pending classification.

### Required audit work

- Classify the 506.9M depth-14 current-balance cut into retained/custodian/exchange/unknown categories.
- Separate:
  - directly IOG-branded pool delegation
  - DRep-visible current balance
  - exchange/custodian-likely outputs
  - unknown/moved-forward outputs
  - excluded/overbroad taint
- Publish estimate as confidence bands, not as legal ownership proof.

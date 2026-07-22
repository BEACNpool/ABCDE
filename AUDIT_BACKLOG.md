# Audit Backlog

This is not a separate narrative track. It is the canonical backlog of unresolved audit questions, refutation tests, and candidate sets for the Genesis ADA audit and clearly separated companion modules.

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

## B-004 — Genesis-to-DRep behavior surface

- **Status:** IN PROGRESS
- **Claim grade:** UNKNOWN until the shared surface is classified
- **Artifact class:** AUDIT_BACKLOG

### Current facts

- The top-DRep profile pack already publishes Genesis-trace exposure and stickiness for current top DReps.
- Current exposure rows are useful audit signals, but they are derived from preserved trace receipts and do not yet use a shared staged deep-trace classification surface.
- The staged trace extractor can produce deeper server-side trace membership suitable for a fresher shared query surface.
- The first shared founder depth-14 surface now exports current traced UTxOs, latest DRep delegation, DRep distribution, proposal vote joins, and small public rollups.
- The first confidence signal table now scores stake-credential clusters using same-block hop, same-epoch DRep cohort, cross-root, current DRep, governance activity, service-like, and fragmentation signals.

### Required audit work

- Review and harden `genesis_current_governance_surface` from staged trace membership, live-unspent status, latest DRep delegation, and current DRep distribution.
- Review/tune behavior classes with explicit confidence and provenance.
- Regenerate top-DRep exposure from the shared surface.
- Interpret proposal-specific joins only after freshness, hashes, and classification rules are published.
- Keep all public language clear that DRep delegation is voting power, not custody or ownership.

## B-005 — Consolidation-hub depositor and downstream classification

- **Status:** BACKLOG
- **Claim grade:** UNKNOWN until independently classified
- **Artifact class:** AUDIT_BACKLOG

### Current facts

- F10 verifies 807 outputs totaling approximately 9.849B ADA into one
  consolidation address.
- The F10 monthly recipient and F09 IOGP-to-burst stream independently converge
  at that address.
- Two additional same-hub streams are committed as receipt-backed query leads.

### Required audit work

- Enumerate all direct hub depositors and independently reproduce any proposed
  genesis-origin grouping.
- Compare deterministic largest-input paths with broader multi-input ancestry
  so a single-path method is not mistaken for exclusive provenance.
- Classify service, exchange, custody, operational, and unknown patterns using
  explicit evidence gates.
- Trace downstream endpoints and current-unspent descendants from the hub.
- Do not adopt external depositor counts, identities, or ownership claims until
  they are reproduced from committed receipts.

## B-006 — NIGHT/Wanchain attacker attribution and post-incident movement

- **Status:** IN PROGRESS
- **Claim grade:** UNKNOWN beyond the F17 transaction linkages
- **Artifact class:** AUDIT_BACKLOG

### Current facts

- F17 reproduces the 515.206M-NIGHT drain, W1–W4 wallet sequence, Liqwid
  collateral route, exchange-style staging, and 6,450-address ADA fan-out.
- Direct Cardano transaction links reach `credit.pay` and an independently
  tagged Binance 1 wallet, but do not identify the beneficial owner.
- The 6,450 fresh addresses held 32.25M ADA unspent at the F17 snapshot.

### Required audit work

- Monitor W1–W4 and the 6,450 fan-out outputs for consolidations, exchange
  deposits, stake registrations, withdrawals, or reuse with older credentials.
- Preserve timestamped snapshot receipts so later balance changes are not
  confused with the original incident state.
- Trace the BNB Chain signature source, wrapped-NIGHT movements, DEX swaps, and
  centralized-exchange endpoints in a separate BNB Chain evidence package.
- Seek independent ownership evidence for `credit.pay`; do not promote a public
  guess about its operator into a finding.
- Off-chain intent and beneficial control are out of scope for this Cardano
  warehouse: bridge funding and Binance distribution linkage are on-chain facts
  and do not, on their own, establish either.

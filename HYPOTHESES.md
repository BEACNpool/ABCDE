# Hypotheses Framework

This file tracks unresolved explanatory hypotheses for the 781,381,495 ADA fourth genesis entry and related Shelley-era coordination signals.

## Evidence Grades
- **FACT**: Directly queryable from db-sync or deterministic from published artifacts.
- **STRONG INFERENCE**: Strongly supported by current evidence, but not uniquely proven.
- **WORKING HYPOTHESIS**: Plausible explanatory model under active test.
- **UNKNOWN**: Not established from current evidence.

---

## H-001. 4th entry co-owned with EMURGO
- **Status**: UNRESOLVED
- **Grade**: WORKING HYPOTHESIS

### Evidence for
- The first downstream spend of the 4th entry directly co-spends with an EMURGO-descended output in epoch 4.
- Shelley-era downstream overlap is extreme: 100% shared frontier overlap and 100% shared Shelley stake-credential overlap in the published convergence evidence.
- The 4th entry was redeemed 5 minutes after the main EMURGO redemption.

### Evidence against
- Byron-era shared infrastructure is a confounder, not a differentiator. Early co-spend and shared routing do not distinguish co-ownership from shared custodial administration.
- Byron addresses do not carry stake credentials, so the early flow evidence does not resolve beneficial owner identity.
- Splitter and fanout behaviors seen in the period are consistent with standard wallet or custody operations, not unique owner identity.
- No current on-chain evidence cleanly separates administration from beneficial ownership.

### Refutation test
- Find sustained, attributable divergence in downstream control decisions that cannot be explained by common custody, such as independently controlled stake registration, delegation, or spending behavior attributable to the 4th-entry descendants but not EMURGO-administered descendants.

### Sources
- `findings/F02_emurgo2_operational_convergence.md`
- `evidence/markdown/emurgo2_convergence_evidence_2026-04-08.md`
- `docs/05_LIMITATIONS_AND_NON_ATTRIBUTION.md`

---

## H-002. 4th entry administered by EMURGO for a separate beneficial owner
- **Status**: UNRESOLVED
- **Grade**: WORKING HYPOTHESIS

### Evidence for
- Current on-chain evidence supports shared administration from epoch 4 onward, but does not prove shared beneficial ownership.
- The 781,381,495 ADA amount matches a published maximum sale-ticket-sized amount, which is consistent with a separate beneficial owner entering common administration.
- Reviewer critique accepted: shared infrastructure is the null hypothesis for this era, given overlapping personnel and custody patterns across IOG, EMURGO, and CF.

### Evidence against
- The immediate epoch-4 co-spend and later full Shelley-era overlap are stronger than a weak or distant association and may indicate tighter control alignment than ordinary third-party servicing.
- No direct on-chain evidence yet demonstrates an independent owner decision distinct from EMURGO-administered behavior.

### Refutation test
- Show repeated independent downstream decisions by the 4th-entry line, especially stake registration or delegation behavior diverging from EMURGO-administered descendants, or show attributable documentation tying the line to EMURGO beneficial ownership instead.

### Sources
- `investigation/archived_notes/emurgo2_classification_2026-04-08.md`
- `investigation/archived_notes/emurgo2_disclosure_search_2026-04-08.md`
- `docs/05_LIMITATIONS_AND_NON_ATTRIBUTION.md`

---

## H-003. Shelley 12-stake-address cross-delegation indicates coordinated founding-entity operation
- **Status**: OPEN
- **Grade**: STRONG INFERENCE

### Evidence for
- The Shelley-era cross-delegation signal is downstream of Byron-only ambiguity and therefore materially stronger than shared Byron routing evidence.
- The same 12 Shelley stake addresses delegating across all three founding pool families imply coordinated operational control or shared strategic administration in the Shelley era.
- Delegation is an explicit post-Shelley control action, unlike passive Byron address overlap.

### Evidence against
- Shared delegation service, shared automation, or a common administrative operator could still explain the pattern without proving common beneficial ownership.
- On-chain delegation alone does not identify the legal or beneficial owner of the controlled stake.

### Refutation test
- Demonstrate that the 12-address set was produced by unrelated users following public wallet defaults or a broadly shared third-party delegation template with no privileged or coordinated control signal.

### Sources
- `findings/F06_synchronized_delegation_swarm.md`
- `docs/00_EXECUTIVE_SUMMARY.md`
- `docs/05_LIMITATIONS_AND_NON_ATTRIBUTION.md`

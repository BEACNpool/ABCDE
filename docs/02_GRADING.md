# Audit Grading and Labels

ABCDE is an audit repository. Every artifact should be labeled by what it proves and how it may be used.

## Claim grades

- **FACT** — directly queryable from db-sync, deterministic from committed/released artifacts, or reproducible from the published DuckDB cut.
- **STRONG_INFERENCE** — strongly supported by facts, but not uniquely proven.
- **WORKING_HYPOTHESIS** — plausible explanatory model with active refutation tests. Not a conclusion.
- **UNKNOWN** — not established from current evidence.

No finding may convert a hypothesis into a fact without a receipt and a reproducible query path.

## Audit artifact classes

Use these labels in docs/findings/reports instead of informal “investigation” language.

- **AUDIT_RECEIPT** — small, reproducible artifact supporting a specific claim.
- **AUDIT_SUMMARY** — aggregation over receipts, suitable for community reading.
- **AUDIT_REVIEW_CUT** — bounded extract intended for review/classification, not final scope.
- **AUDIT_BASELINE** — preserved comparison target used for regression checks.
- **AUDIT_CANDIDATE_SET** — broad candidate output requiring classification before claims.
- **AUDIT_BACKLOG** — open questions and refutation tests.
- **RELEASE_ARTIFACT** — large generated dataset stored outside git with hashes/manifests.
- **LEGACY_REFERENCE** — archived material retained for comparison, not the public entry point.

## Finding statuses

- **VERIFIED** — current v2 query/artifact reproduces the finding.
- **REVIEW_CUT** — bounded or partial cut; valid within stated scope only.
- **CANDIDATE_SET** — generated candidates requiring classification.
- **BACKLOG** — open question/refutation test.
- **LEGACY_REFERENCE_ONLY** — preserved for context until re-derived or retired.

## Public wording rule

Do not write “proved ownership,” “controlled by,” “misconduct,” or similar off-chain conclusions unless the supporting evidence directly establishes that fact.

Preferred framing:

- “IOG-descended” / “founder-descended” for trace membership.
- “delegated to” for stake/governance observations.
- “candidate” for broad staged outputs pending classification.
- “unresolved” for hypotheses under active audit.

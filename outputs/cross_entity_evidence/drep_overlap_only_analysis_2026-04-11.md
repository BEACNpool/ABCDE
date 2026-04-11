---
title: DRep Governance Participation — Cross-Entity Overlap Addresses Only
date: 2026-04-11
epoch: 620
query: queries/drep_overlap_only_ada_weighted.sql
data: outputs/cross_entity_evidence/drep_overlap_only_ada_weighted_2026-04-11.csv
evidence_grade: FACT (on-chain, epoch 620)
---

# DRep Governance Participation — Cross-Entity Overlap Addresses (Shared-Control Subset)

> **Scope caveat:** This analysis is restricted to stake addresses appearing in 2+ founder trace frontiers simultaneously. Single-trace addresses are excluded because they could represent ADA sold to retail holders. Cross-entity overlap addresses require shared wallet infrastructure and cannot result from independent retail purchases.

## Exclusion: EMURGO | EMURGO_2 Internal Overlap

The EMURGO|EMURGO_2-only overlap tier (4,919 addresses, 62.3M ADA) is **excluded from all cross-entity totals** because the ABCDE investigation already established 100% frontier identity between these two traces (Section 2 — EMURGO_2 Genesis Entry). Every address in the EMURGO frontier appears in EMURGO_2 and vice versa. Including same-entity overlap would inflate the cross-entity coordination metric without adding new signal about shared control across distinct founder allocations.

The excluded tier's DRep breakdown is shown separately in the reference table below for completeness.

| (Excluded) EMURGO\|EMURGO_2 | Addresses | ADA | % of tier |
|-----------------------------|-----------|-----|-----------|
| ABSTAIN | 430 | 22,801,144 | 36.60% |
| NO_DELEGATION | 4,239 | 19,821,440 | 31.82% |
| NAMED_DREP | 228 | 19,063,905 | 30.60% |
| NO_CONFIDENCE | 22 | 614,064 | 0.99% |
| **Subtotal** | **4,919** | **62,300,553** | — |

---

## Summary Finding

As of epoch 620, **1,198 truly cross-entity overlap stake addresses** control ~91.6M ADA. Of that, **87.40% (80.1M ADA) is outside the active Conway governance denominator**. Only ~11.5M ADA (12.60%) actively participates in governance.

These addresses appear simultaneously in the frontiers of at least two *distinct* founder entities (CF, IOG, EMURGO/EMURGO_2 treated as one). Shared-wallet infrastructure is required for an address to appear in multiple founder traces — this cannot result from independent retail purchases.

---

## Result A: Summary Across All Cross-Entity Overlap Addresses

| DRep Category | Stake Addresses | ADA Amount | % of Cross-Entity Total |
|---------------|-----------------|------------|-------------------------|
| NO_DELEGATION | 979 | 63,791,014 | **69.61%** |
| ABSTAIN | 136 | 16,310,850 | **17.80%** |
| NAMED_DREP | 74 | 11,467,464 | 12.51% |
| NO_CONFIDENCE | 9 | 76,140 | 0.08% |
| **GRAND TOTAL** | **1,198** | **91,645,468** | 100.00% |

**Outside active denominator (ABSTAIN + NO_DELEGATION): 80,101,864 ADA (87.40%)**  
**Actively participating (NAMED_DREP + NO_CONFIDENCE): 11,543,604 ADA (12.60%)**

---

## Result B: Breakdown by Cross-Entity Overlap Tier

### 2-Entity: CF | IOG (48 addresses, ~2.9M ADA)

| DRep Category | Addresses | ADA | % of tier |
|---------------|-----------|-----|-----------|
| NAMED_DREP | 7 | 2,460,771 | 84.87% |
| ABSTAIN | 6 | 292,464 | 10.09% |
| NO_DELEGATION | 34 | 80,069 | 2.76% |
| NO_CONFIDENCE | 1 | 66,014 | 2.28% |

Note: Highest active participation rate of any tier (87.15%). ADA is concentrated in 7 NAMED_DREP addresses. Small count (48 addresses). Outside denominator: 12.85%.

---

### 3-Entity: CF | EMURGO | EMURGO_2 (83 addresses, ~4.5M ADA)

| DRep Category | Addresses | ADA | % of tier |
|---------------|-----------|-----|-----------|
| NAMED_DREP | 9 | 2,435,661 | 54.58% |
| ABSTAIN | 7 | 1,922,054 | 43.07% |
| NO_DELEGATION | 66 | 102,905 | 2.31% |
| NO_CONFIDENCE | 1 | 1,557 | 0.03% |

Note: ADA is split between 9 NAMED_DREP addresses and 7 ABSTAIN addresses of nearly equal weight. Outside denominator: 45.38%.

---

### 3-Entity: EMURGO | EMURGO_2 | IOG (1,045 addresses, ~78.8M ADA)

| DRep Category | Addresses | ADA | % of tier |
|---------------|-----------|-----|-----------|
| NO_DELEGATION | 861 | 63,605,180 | **80.70%** |
| ABSTAIN | 121 | 8,705,188 | 11.05% |
| NAMED_DREP | 56 | 6,493,177 | 8.24% |
| NO_CONFIDENCE | 7 | 8,569 | 0.01% |

Note: This is the dominant tier by ADA (~78.8M of 91.6M total). 80.70% NO_DELEGATION. These addresses span IOG and EMURGO/EMURGO_2 traces — the largest cross-entity coordination signal in the dataset. Outside denominator: 91.75%.

---

### 4-Entity: CF | EMURGO | EMURGO_2 | IOG (22 addresses, ~5.5M ADA)

| DRep Category | Addresses | ADA | % of tier |
|---------------|-----------|-----|-----------|
| ABSTAIN | 2 | 5,391,144 | **98.52%** |
| NAMED_DREP | 2 | 77,855 | 1.42% |
| NO_DELEGATION | 18 | 2,860 | 0.05% |

Note: 22 addresses appear in all four founder frontiers simultaneously. Two ABSTAIN addresses control 98.52% of the tier's ADA. The 18 NO_DELEGATION addresses are dust (2,860 ADA total). Outside denominator: 98.57% — the highest removal rate of any tier.

---

## Governance Denominator Interpretation

The Conway governance active denominator includes only ADA delegated to active NAMED_DREPs or to NO_CONFIDENCE. ABSTAIN and NO_DELEGATION are excluded.

For the cross-entity shared-control subset:
- **87.40%** of ADA is structurally outside the active denominator
- The dominant contributor is EMURGO|EMURGO_2|IOG (63.6M ADA NO_DELEGATION alone)
- The 4-entity tier has the sharpest signal: 2 ABSTAIN addresses, 5.39M ADA, 98.52% of tier

The practical effect: these addresses remove themselves from the denominator against which governance proposals must reach threshold. Their absence makes thresholds easier to satisfy with less total active ADA.

---

## Reproducibility

```bash
# Prerequisites
psql -h ${DB_HOST} -U codex_audit -d cexplorer_replica
  CREATE TEMP TABLE emurgo2_stake (stake_address text PRIMARY KEY);
  \copy emurgo2_stake(stake_address) FROM 'data/raw/emurgo2/emurgo2_stake_addrs_import.csv' CSV

# Full query (excludes EMURGO|EMURGO_2-only tier from summary totals)
\i queries/drep_overlap_only_ada_weighted.sql
```

See `queries/drep_overlap_only_ada_weighted.sql` for the full reproducible query.

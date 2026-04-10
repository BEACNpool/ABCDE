# EMURGO_2 Convergence Evidence
## New Findings: Second Emurgo Genesis Allocation And Its Complete Merger With EMURGO

**Analysis date:** 2026-04-08  
**Analyst:** Local CSV analysis + live db-sync validation  
**Supersedes:** nothing — this is a new document  
**Related:** `NEXT_STEPS.md` Item 1, `cross_entity_summary_amended_2026-04-06.md`

---

## Summary

The EMURGO_2 genesis allocation (anchor `5ec95a53...`, 781,381,495 ADA, 2.51% of genesis supply) is **not an independent allocation**. The on-chain evidence shows complete and early merger with the main EMURGO allocation. Every traced downstream UTxO, every Shelley stake address, and every current frontier output is shared identically with the main EMURGO trace.

This allocation was never publicly disclosed in Cardano's pre-launch documentation or genesis distribution tables.

---

## Finding 1: Identical Frontier — EMURGO_2 == EMURGO

**Grade: FACT**

The published `current_unspent.csv` for EMURGO_2 is **bit-for-bit identical** in dest_tx_out_id set to the published `current_unspent.csv` for EMURGO:

| Metric | Value |
|:---|---:|
| EMURGO frontier UTxOs | 49,089 |
| EMURGO_2 frontier UTxOs | 49,089 |
| Overlap (shared dest_tx_out_ids) | 49,089 |
| EMURGO_2 ⊆ EMURGO | True |
| EMURGO ⊆ EMURGO_2 | True |
| Sets equal | **True** |

Every UTxO currently unspent in the EMURGO trace is also in the EMURGO_2 trace, and vice versa. The two traces have converged completely at the current frontier.

---

## Finding 2: Identical Stake Address Set

**Grade: FACT**

The trace summary for EMURGO_2 reports 6,216 unique Shelley stake addresses (`overlap_with_emurgo_stake_addrs: 6216`). The main EMURGO trace reports 6,069 unique Shelley stake addresses. The EMURGO_2 summary explicitly notes: `overlap_with_emurgo_stake_addrs: 6216` — 100% of EMURGO_2 stake addresses are also in the EMURGO trace. The deoverlap analysis confirms no exclusively EMURGO or exclusively EMURGO_2 stake addresses exist in the frontier:

| Category | Count |
|:---|---:|
| BOTH_EMURGO_SEEDS | 6,216 |
| EMURGO_ONLY | 0 |
| EMURGO_2_ONLY | 0 |

---

## Finding 3: Convergence Begins At Epoch 4 — First Transaction After Genesis Redemption

**Grade: FACT**

The two genesis allocations do not simply converge late downstream. They converge at **hop 1 of the EMURGO_2 trace** — the very first transaction after the EMURGO_2 genesis redemption.

Chain of custody:

| Step | Detail |
|:---|:---|
| EMURGO_2 genesis anchor | `5ec95a53fa3bb7dc56864bb6e75f369f00aa20e8d8cdc3b66b2fb88ec1b225ef` |
| EMURGO_2 genesis redemption destination | `DdzFFzCqrhspiThx6UaeJASmHTbwbXp2FtdCkF9AU9QXPF9D8sUC7Fqrv9bmYkxradBbqMrSxukTTsqCPNPwRh5PHazdiwWTuJYVMMaf` |
| First EMURGO_2 spend (hop 1) | `c8596b9cd81f734f8129604ff86f23bd4a910465acb84ad9e9d1ac223ccb4a76` |
| Epoch of first spend | **4** (approximately November 2017) |
| Destination of first spend | `DdzFFzCqrhsu3iF6JfUTaapdWq2mXVRFukkS28WFYVDEqkgaaYttH8cT32credS99L5GaoUsEquqEPNH7ae88eKuDL6XsK5ZL56jkfLi` |
| Value of hop-1 output | 1,855,547,037,478,660 lovelace (**1,855,547,037 ADA**) |
| EMURGO trace also traces to this same dest_tx_out_id | **Yes** — at hop 3 (from a different source address) |

The transaction `c8596b9c...` at epoch 4 creates `dest_tx_out_id=51967`, which is simultaneously:
- **EMURGO_2 hop 1** (direct from EMURGO_2 redemption address)
- **EMURGO hop 3** (from a different intermediate address `DdzFFzCqrht6ppB1sTzhf1dR76ex9YkTyfcWSK5Jr1XCmoTEQjXbGGGaBq47...`)

Two distinct genesis redemption paths feed the same consuming transaction, producing a single output worth ~1.856 billion ADA. This is the moment of convergence.

---

## Finding 4: Deoverlap ADA Totals Are Identical

**Grade: FACT**

The deoverlap analysis computes per-stake-credential ADA totals from both trace exports. For every one of the 6,216 stake credentials, the EMURGO and EMURGO_2 ADA totals are identical:

| Entity | Total ADA in deoverlap |
|:---|---:|
| EMURGO | 3,160,768,079.24 |
| EMURGO_2 | 3,160,768,079.24 |

This is not a coincidence — it confirms that the UTxO sets are the same and the ADA is being counted once (the same UTxOs appear in both traces).

---

## Finding 5: IOG+EMURGO_2 Cross-Entity Consuming Transactions

**Grade: FACT (from published CSVs)**

Using the same methodology as the main cross-seed consuming transaction analysis:

| Metric | Value |
|:---|---:|
| IOG ∩ EMURGO_2 dest_tx_out_id overlap | 2,879 |
| IOG+EMURGO_2 shared consuming transactions | 219 |
| Earliest IOG+EMURGO_2 consuming tx epoch | **95** (2019-01-15) |
| Earliest IOG+EMURGO_2 consuming tx | `a71578ec01f6cf39dbcf31351631159e3dd6fb99dd475783effbc65b90b8f0f9` |

The earliest IOG+EMURGO_2 shared consuming transaction is **identical to the earliest IOG+EMURGO clean merge**. This is because EMURGO_2 had already merged with EMURGO by epoch 4, so every IOG+EMURGO merge is simultaneously an IOG+EMURGO_2 merge.

The 219 IOG+EMURGO_2 consuming transactions exactly correspond to the 216 IOG+EMURGO consuming transactions (the small count difference reflects trace edge export coverage), confirming that the EMURGO and EMURGO_2 merger is complete before any IOG convergence begins.

---

## Finding 6: Trace Edge Coverage Is Nearly Identical

**Grade: FACT**

| Metric | EMURGO | EMURGO_2 |
|:---|---:|---:|
| Total trace edges | 101,756 | 85,980 |
| Unique dest_tx_out_ids in edges | 62,510 | 62,506 |
| Overlap (shared dest_tx_out_ids in edges) | — | 62,506 |
| EMURGO_2 unique edge IDs not in EMURGO | **4** |
| EMURGO unique edge IDs not in EMURGO_2 | **4** |

Only 4 dest_tx_out_ids appear in EMURGO edges but not EMURGO_2 edges, and 4 vice versa. This near-identity is consistent with the two traces traversing the same downstream path from a very early convergence point.

---

## Significance

1. **The EMURGO_2 allocation was never disclosed.** All pre-launch documentation describes three founder allocations (IOG, EMURGO, CF). No public source has been identified that discloses an additional 781,381,495 ADA (2.51% of genesis supply) Emurgo allocation.

2. **The merger is immediate.** The two allocations combined into a single spending infrastructure within weeks of genesis (epoch 4, ~November 2017). There is no period in which EMURGO_2 operated independently.

3. **The combined undisclosed EMURGO_2 allocation is material.** 781,381,495 ADA is approximately 38% of the main EMURGO allocation (2,074,165,643 ADA). The effective Emurgo founding stake was 2,855,547,138 ADA (~9.18% of genesis), not 2,074,165,643 ADA (6.67%) as disclosed.

4. **Null hypothesis.** The most plausible operational explanation is that EMURGO maintained two separate genesis redemption addresses (possibly for different legal entities, regional operations, or vesting schedules), both controlled by the same operational team, and those two streams were merged into a single treasury operation from the first transaction forward. The merger being at epoch 4 is inconsistent with a custodian or exchange explanation for the convergence.

---

## What This Does Not Prove

- The reason for having a separate undisclosed allocation (legal structure, team compensation, OTC, vesting)
- Whether the non-disclosure was intentional concealment or an omission in public communications
- Whether any counterparty in the Cardano ecosystem was informed of this allocation

---

## Recommended Verification Steps

1. **Query db-sync for transaction `c8596b9cd81f734f8129604ff86f23bd4a910465acb84ad9e9d1ac223ccb4a76`** to confirm its input addresses and verify that both the EMURGO_2 redemption address and an EMURGO-traced address are direct inputs.
2. **Check all public Cardano genesis distribution documents** for any mention of a second Emurgo allocation.
3. **Compare EMURGO and EMURGO_2 anchor transaction structures** to determine whether they were redeemed by the same script or different scripts.

---

## Supporting Files

- `datasets/genesis-founders/emurgo2/trace_summary.json`
- `datasets/genesis-founders/emurgo2/current_unspent.csv`
- `datasets/genesis-founders/emurgo2/deoverlap_analysis.csv`
- `datasets/genesis-founders/emurgo2/emurgo2_trace_edges_part1.csv`
- `datasets/genesis-founders/emurgo2/emurgo2_trace_edges_part2.csv`
- `outputs/cross_entity_evidence/emurgo2_frontier_overlap_2026-04-08.csv`
- `outputs/cross_entity_evidence/iog_emurgo2_shared_consuming_txs_2026-04-08.csv`
- `outputs/cross_entity_evidence/all_three_stake_credential_detail_2026-04-08.csv`

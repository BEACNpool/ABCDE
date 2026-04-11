# Founder Allocation Merge Timeline
## Chronological record of cross-entity convergence events

**Compiled:** 2026-04-08  
**Source:** Published trace-edge CSVs, deoverlap analysis, live db-sync validation

---

## Claim-Strength Standard

- **FACT** — directly visible in published CSVs or db-sync
- **STRONG INFERENCE** — simplest explanation of multiple facts
- **HEURISTIC** — label from rule-based analysis

---

## The Five Founder Allocations

| Entity | Anchor TX | Genesis ADA | % Genesis | First Tx Date |
|:---|:---|---:|---:|:---|
| IOG | `fa2d2a70...` | 2,463,071,701 | 7.92% | 2017-09-27 |
| EMURGO | `242608fc...` | 2,074,165,643 | 6.67% | 2017-10-30 |
| **EMURGO_2** ⚠ | **`5ec95a53...`** | **781,381,495** | **2.51%** | **2017-10-18** |
| CF | `208c7d54...` | 648,176,763 | 2.08% | 2017-09-28 |
| **TOTAL DISCLOSED** | | **5,185,414,107** | **16.67%** | |
| **TOTAL ACTUAL** | | **5,966,795,602** | **19.18%** | |
| **Undisclosed (EMURGO_2)** | | **781,381,495** | **2.51%** | |

---

## Timeline Of Convergence Events

### 2017-11 — Epoch 4: EMURGO + EMURGO_2 First Merge

**Grade: FACT**

| Field | Value |
|:---|:---|
| Merging allocations | EMURGO + EMURGO_2 |
| Transaction | `c8596b9cd81f734f8129604ff86f23bd4a910465acb84ad9e9d1ac223ccb4a76` |
| Epoch | 4 |
| Output created | dest_tx_out_id=51967, **1,855,547,037 ADA** |
| EMURGO_2 contribution | hop 1 — direct from EMURGO_2 redemption address |
| EMURGO contribution | hop 3 — from EMURGO intermediate address |
| Result | Both trace lineages feed the same UTxO — merger begins |

This is EMURGO_2's **first downstream transaction**. It immediately combines with EMURGO funds. From this point forward, the two allocations are operationally indistinguishable.

---

### 2019-01-15 — Epoch 95: IOG + EMURGO (+ EMURGO_2) First Clean Merge

**Grade: FACT (live db-sync validated)**

| Field | Value |
|:---|:---|
| Merging allocations | IOG + EMURGO + EMURGO_2 (EMURGO and EMURGO_2 already unified) |
| Transaction | `a71578ec01f6cf39dbcf31351631159e3dd6fb99dd475783effbc65b90b8f0f9` |
| Epoch | 95 |
| Input split | 2 IOG-exclusive, 1 EMURGO-exclusive source inputs |
| Output 2048665 | — |
| Output 2048666 | → `DdzFFzCqrhstmqBkaU98vdHu6PdqjqotmgudToWYEeRmQKDrn4cAgGv9EZKtu1DevLrMA1pdVazufUCK4zhFkUcQZ5Gm88mVHnrwmXvT` (the shared Byron hub/sink) |
| Clean merge | Yes — no prior overlap across inputs |
| Months after genesis | ~16 months |

IOG and EMURGO (including the secret EMURGO_2 allocation) are now sharing a downstream destination for the first time. The destination is the high-volume Byron sink that later appears across all three founder traces.

---

### 2020-05-18 — Epoch 193: IOG + CF First Clean Merge

**Grade: FACT (live db-sync validated)**

| Field | Value |
|:---|:---|
| Transaction | `f9951db326893e5c6cd94407e3d75be4928442aaf5809e435ca3e82c1983949d` |
| Epoch | 193 |
| Input split | 1 IOG-exclusive + 1 CF-exclusive |
| Output 4857107 | → same Byron hub/sink |
| Clean merge | Yes |

---

### 2020-05-27 — Epoch 195: EMURGO + CF First Clean Merge

**Grade: FACT (live db-sync validated)**

| Field | Value |
|:---|:---|
| Transaction | `11c0765f430ecfffbdd1fb400d34bcd61d13af4c2e9332ce215f33de7e48d394` |
| Epoch | 195 |
| Input split | 1 EMURGO-exclusive + 3 CF-exclusive |
| Clean merge | Yes |

---

### 2020-06-02 — Epoch 196: First Three-Way Lineage Merge

**Grade: FACT (live db-sync validated)**

| Field | Value |
|:---|:---|
| Transaction | `197f9d27e49345cc085c9a2951d96c77f57f1cd82a71c095b7b7a3b36e74855d` |
| Epoch | 196 |
| Inputs | 1 IOG-exclusive + 1 EMURGO+CF-shared source input |
| Clean | Partial — EMURGO and CF lines already co-mingled in one input |
| Outputs | 5064341 (157 ADA), 5064342 (10,000 ADA) — both in all-three frontier |

---

### 2020-07-03 — Epoch 202–203: Sink Batch Operation

**Grade: FACT (locally validated)**

| Field | Value |
|:---|:---|
| Sink address | `DdzFFzCqrhstmqBkaU98vdHu6PdqjqotmgudToWYEeRmQKDrn4cAgGv9EZKtu1DevLrMA1pdVazufUCK4zhFkUcQZ5Gm88mVHnrwmXvT` |
| Payment count to splitter | 41 transactions |
| Total value transferred | 78,000,020 ADA |
| Pattern | 39 × 2,000,000 ADA + 2 × 10 ADA |
| All transactions | Same calendar day (2020-07-03) |
| Splitter address | `Ae2tdPwUPEZ6xYrxCgRDM2NQFM5oajHEoJN3i9ZVV2AbsbvxoJBjVu3yP7W` |
| Splitter to bridge (4 txs) | 50,000,000 ADA total → `Ae2tdPwUPEZHiXixpj6Xdju5jti25cY7QhjHZ3WiZypCsfEJoJx5fGujAKn` |

The sink fed 78M ADA to the splitter in a single automated batch. The splitter passed 50M ADA to the bridge in four transactions. These three addresses (sink, splitter, bridge) appear across both IOG and EMURGO trace exports.

---

### 2021-01-01 — Epoch 239: Second Three-Way Merge

**Grade: FACT (live db-sync validated)**

| Field | Value |
|:---|:---|
| Transaction | `34147ef46fd105ed39e3be63ac194e79622fb1bf9ea6e50313a0c3e0e6fd20c3` |
| Epoch | 239 |
| Inputs | 58 total; 1 EMURGO-exclusive + 1 CF-exclusive + 1 IOG+CF-shared |
| Outputs | 7835688 (50,000 ADA → `stake1uxttvx739...`), 7835689 (8,356,376 ADA → `stake1uxztgcgh...`) |
| Clean | No — one input shared across two branches |

---

### 2021-02-25 — Epoch 250: Clean Three-Way Merge

**Grade: FACT (live db-sync validated) — STRONGEST FINDING**

| Field | Value |
|:---|:---|
| Transaction | `571f776c0698c576ddecae145f97e7f284b82ebea70fbc924fa4e2a4a6258020` |
| Epoch | 250 |
| Total inputs | 384 |
| Bridge inputs | 381 from `Ae2tdPwUPEZHiXixpj6Xdju5jti25cY7QhjHZ3WiZypCsfEJoJx5fGujAKn` — 48,718,538 ADA |
| Other inputs | 3 from `addr1q84qw26...` — 1,526,100 ADA |
| IOG-exclusive direct inputs | 2 (tx_out_ids 8926255, 9036401) |
| EMURGO-exclusive direct inputs | 1 (tx_out_id 8064253) |
| CF-exclusive direct inputs | 1 (tx_out_id 10748217) |
| Pair overlaps across inputs | 0 |
| Clean three-way | **Yes** |
| Output 10748946 | 50,000,000 ADA → `stake1uxttvx739...` |
| Output 10748947 | 40 ADA → `stake1u8etn7nd...` |
| Output 10748948 | 244,596 ADA → `stake1uxztgcgh...` |
| All three outputs | In IOG ∩ EMURGO ∩ CF frontier |

---

## Key Beneficiary Stake Credentials

### `stake1uxttvx739dt505d6sxvdykj8336utdq2q92jk3sv253zp5qalcz84`

The primary beneficiary of the two three-way merge outputs.

| Trace | UTxOs | ADA |
|:---|---:|---:|
| IOG | 24 | 216,818,979 |
| EMURGO | 17 | 134,100,674 |
| CF | 7 | 167,075,537 |
| EMURGO_2 | Yes | same as EMURGO |

- Directly receives outputs from `571f776c` (10748946: 50M ADA) and `34147ef4` (7835688: 50M ADA)
- Latest attributed epoch: 406

### `stake1uxztgcgh49sld46q94xtjy7zf8j2tnntd6rswl9dypa9ffqqxrz2a`

| Trace | UTxOs | ADA |
|:---|---:|---:|
| IOG | 7 | 10,715,097 |
| EMURGO | 7 | 18,577,048 |
| CF | 18 | 11,379,155 |
| EMURGO_2 | Yes | same as EMURGO |

- Directly receives outputs from `571f776c` (10748948: 244,596 ADA) and `34147ef4` (7835689: 8,356,376 ADA)

### `stake1ux5tpajlpe25jwazt5aypj37xn9qqfp59tffmj9pjaq2q2qww0acs`

| Trace | UTxOs | ADA |
|:---|---:|---:|
| EMURGO | 1 (tx_out_id 6310510) | 1,375,877,556 |
| CF | 2 (incl. tx_out_id 6310510) | 1,376,252,425 |
| EMURGO_2 | Yes | same as EMURGO |
| IOG | Not in trace | — |

The largest single stake key in the cross-entity overlap: **1.376 billion ADA**. Shared between EMURGO, CF, and EMURGO_2 traces via a single UTxO (6310510) created at epoch 212.

---

## Cumulative Merge Count

| Pair | Total consuming txs | Clean merges | First clean epoch |
|:---|---:|---:|---:|
| EMURGO + EMURGO_2 | Converged at epoch 4 | — | 4 |
| IOG + EMURGO | 216 | 205 | 95 |
| IOG + CF | 49 | 48 | 193 |
| EMURGO + CF | 253 | 54 | 195 |
| IOG + EMURGO + CF (lineage) | 3 | 1 (epoch 250) | 196 |

---

*This document compiles chain-verifiable facts and strong inferences. Intent, beneficial ownership, and legal implications require separate expert analysis.*

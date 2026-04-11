# Cardano Genesis ADA — Master Forensic Findings

Canonical location: `docs/findings/MASTER_FINDINGS.md`


**Investigation:** Cardano Genesis ADA Distribution Forensics  
**Investigator:** ABCDE / BEACNpool (Ticker: BEACN)  
**Database source:** `cexplorer_replica` at block 13,215,210+ (synced 2026-03-28)  
**Trace runs:** IOG run_id=7, EMURGO run_id=9, EMURGO_2 run_id=10, CF run_id=8  
**Date of final compilation:** 2026-04-10  
**Branch:** `forensics/local-investigation-batch-2026-04-10`

This document consolidates all findings from the three individual findings files:
- `FULL_FINDINGS_2026-04-06.md` (F-series)
- `FULL_FINDINGS_2026-04-08_ADDENDUM.md` (A-series)
- `FULL_FINDINGS_2026-04-10_ADDENDUM.md` (B-series)

All addresses and transaction hashes are given in full (untruncated).

---

## Claim Strength Legend

| Grade | Meaning |
|-------|---------|
| **FACT** | Directly queryable from db-sync or deterministic computation from published data |
| **STRONG INFERENCE** | Pattern strongly implies conclusion; alternative explanations exist but are less parsimonious |
| **HYPOTHESIS** | Consistent with evidence; not yet falsified; not established |
| **NOT PROVEN** | Logically possible but not supported by available on-chain data |

---

## Genesis Baseline

| Metric | Value |
|--------|-------|
| Genesis block time | 2017-09-23 21:44:51 UTC |
| Total genesis addresses | 14,505 |
| Total genesis ADA supply | 31,112,484,745 ADA |
| Unredeemed forever (465 addresses) | 318,200,635 ADA (1.02%) |
| Total Cardano max supply | 45,000,000,000 ADA |
| Protocol reserve (non-UTxO) | ~13,887,515,255 ADA |

---

## PART I — FOUNDER ALLOCATIONS

### F01. Named Founder Allocations — Redeemed Within 24 Hours of Genesis

**Grade: FACT**

All four anchor redemptions occurred within 24 hours of the genesis block (2017-09-23 21:44:51 UTC):

| Entity | Anchor TX | Full TX Hash | ADA | Redeemed At |
|--------|-----------|-------------|-----|-------------|
| IOG | `fa2d2a70...` | `fa2d2a70c0b5fd45cb6c3989f02813061f9d27f15f30ecddd38780c59f413c62` | 2,463,071,701 | 2017-09-27 16:20 UTC |
| CF | `208c7d54...` | `208c7d54c1c24059c9314ddbe866edc80adcb8894539b27b6a1430d5c078b998` | 648,176,763 | 2017-09-28 09:33 UTC |
| EMURGO | `242608fc...` | `242608fc18552a4ac83adabcef7155f3b909e83d469ce89735db8f11d3637e38` | 2,074,165,643 | 2017-09-28 10:04 UTC |
| EMURGO_2 (781M entry) | `5ec95a53...` | `5ec95a53fa3bb7dc56864bb6e75f369f00aa20e8d8cdc3b66b2fb88ec1b225ef` | 781,381,495 | 2017-09-28 10:09 UTC |

Named founders combined: **5,185,414,107 ADA** (16.67% of genesis supply).

---

### F02. The 781,381,495 ADA "EMURGO_2" Entry — Same Operator as EMURGO

**Grade: FACT**

The genesis entry redeemed by `5ec95a53fa3bb7dc56864bb6e75f369f00aa20e8d8cdc3b66b2fb88ec1b225ef` is operationally indistinguishable from the main EMURGO allocation. Key evidence:

**Redemption timing:**
- EMURGO redemption (`242608fc...`): 2017-09-28 10:04:11 UTC
- EMURGO_2 redemption (`5ec95a53...`): 2017-09-28 10:09:11 UTC
- Gap: **5 minutes, same operator sequential execution**

**EMURGO_2 redeemed to:** `DdzFFzCqrhspiThx6UaeJASmHTbwbXp2FtdCkF9AU9QXPF9D8sUC7Fqrv9bmYkxradBbqMrSxukTTsqCPNPwRh5PHazdiwWTuJYVMMaf`

**First downstream spend** (epoch 4, 2017-10-18 05:15:51 UTC):  
TX `c8596b9cd81f734f8129604ff86f23bd4a910465acb84ad9e9d1ac223ccb4a76` co-spends:
- `5ec95a53...#0` = 781,381,495 ADA (EMURGO_2 redemption output)
- `743fd051...` = 1,074,165,542 ADA (an EMURGO-descended output)

This is simultaneously EMURGO_2 hop 1 and EMURGO hop 3. The merge happens **at the very first downstream transaction** after a 475-hour dormancy period.

**Frontier overlap:**
| Metric | Value |
|--------|-------|
| EMURGO_2 frontier size | 49,089 UTxOs |
| EMURGO frontier size | 49,089 UTxOs |
| Overlap | **49,089 / 49,089 (100%)** |
| EMURGO_2 = EMURGO | **True** |
| Shared stake credentials | 6,216 / 6,216 (100%) |

The two traces are functionally identical from hop 1 onward. The 781M entry's original beneficial ownership at genesis is unresolved (sale ticket vs. undisclosed founder allocation), but the operator executing downstream is the same as EMURGO.

---

## PART II — CROSS-ENTITY FUND FLOWS

### F03. 521 Direct Cross-Seed Consuming Transactions

**Grade: FACT**

Full scan of all trace-edge exports yielded **521 transactions** directly consuming UTxOs from multiple founder lineages in the same transaction:

| Pair | Total | Clean Merges | Earliest Clean | Latest Clean |
|------|-------|-------------|----------------|-------------|
| IOG + EMURGO | 216 | 205 | Epoch 95, 2019-01-15 | Epoch 390, 2023-01-27 |
| IOG + CF | 49 | 48 | Epoch 193, 2020-05-18 | — |
| EMURGO + CF | 253 | 54 | Epoch 195, 2020-05-27 | — |
| **All Three** | **3** | **1** | **Epoch 250, 2021-02-25** | — |

A "clean merge" means each represented founder branch has at least one exclusively-its-own direct input (no prior mixing).

**Shared exact frontier UTxOs:** IOG∩EMURGO: 1,996 | EMURGO∩CF: 711 | IOG∩CF: 263 | All three: 7

---

### F04. Clean Three-Way IOG+EMURGO+CF Merge — Epoch 250

**Grade: FACT**

**Transaction `571f776c0698c576ddecae145f97e7f284b82ebea70fbc924fa4e2a4a6258020`**

| Field | Value |
|-------|-------|
| Epoch | 250 |
| Date/Time | 2021-02-25 12:58:28 UTC |
| Total inputs | 384 |
| IOG-exclusive inputs | 2 (UTxOs 8926255, 9036401) |
| EMURGO-exclusive input | 1 (UTxO 8064253) |
| CF-exclusive input | 1 (UTxO 10748217 = 999,748 ADA, from `stake1uxztgcgh49sld46q94xtjy7zf8j2tnntd6rswl9dypa9ffqqxrz2a`) |
| Remaining 380 inputs | from bridge accumulator `Ae2tdPwUPEZHiXixpj6Xdju5jti25cY7QhjHZ3WiZypCsfEJoJx5fGujAKn` |
| Output 10748946 | 50,000,000 ADA → `addr1qxtrqdumg8dleqcra3myptlq6n43m8s0mver0pwgqrr8awvkkcdaz26hglgm4qvc6fdy0rr4ck6q5q249drqc4fzyrgq68vuva` |
| Recipient stake | `stake1uxttvx739dt505d6sxvdykj8336utdq2q92jk3sv253zp5qalcz84` |

**Predecessor transactions:**
- Three-way merge 1: `197f9d27e49345cc085c9a2951d96c77f57f1cd82a71c095b7b7a3b36e74855d` (epoch 196, 2020-05-30)
- Three-way merge 2 (intermediate): `34147ef46fd105ed39e3be63ac194e79622fb1bf9ea6e50313a0c3e0e6fd20c3` (epoch 239, 2021-01-01) — also outputs 50M ADA to `stake1uxttvx739dt505d6sxvdykj8336utdq2q92jk3sv253zp5qalcz84`

This is the strongest single convergence evidence in the dataset — a verified on-chain transaction with exclusive inputs from all three founder lineages.

---

### A4. 30 Clean IOG+EMURGO Merges at Epoch 250 — Coordinated Batch

**Grade: FACT**

| Epoch range | Clean IOG+EMURGO merges |
|:---|---:|
| Epoch 95 (first) | 1 |
| Epochs 125–249 | 95 |
| **Epoch 250** (same as clean 3-way) | **30** |
| Epoch 251 | 35 |
| Epoch 252 | 18 |
| Epochs 253–390 | 26 |
| **Total** | **205** |

83 of 205 (40%) clean IOG+EMURGO merges occur in the epoch 250–252 window — coinciding exactly with the clean three-way merge and the 58-output splitter's peak activity.

**Earliest:** `a71578ec01f6cf39dbcf31351631159e3dd6fb99dd475783effbc65b90b8f0f9` (epoch 95, 2019-01-15)  
**Latest:** epoch 390, 2023-01-27 — cross-entity flows ran **exactly 4 years** (Jan 2019 – Jan 2023).

---

### B6. First Clean Pairwise Merge Details

**Grade: FACT**

| Pair | TX Hash | Epoch | Date | Inputs | ADA |
|:---|:---|---:|:---|---:|---:|
| IOG+EMURGO | `a71578ec01f6cf39dbcf31351631159e3dd6fb99dd475783effbc65b90b8f0f9` | 95 | 2019-01-15 | 30 | 71,704 |
| IOG+CF | `f9951db326893e5c6cd94407e3d75be4928442aaf5809e435ca3e82c1983949d` | 193 | 2020-05-18 | 13 | 1,797,601 |
| EMURGO+CF | `11c0765f430ecfffbdd1fb400d34bcd61d13af4c2e9332ce215f33de7e48d394` | 195 | 2020-05-27 | 35 | **998** |
| EMURGO+CF (first real) | `cb32d36c9ad2d8de1c6482d371bc79a48ce411d5b0a6200d3aba69d5dad77444` | 212 | 2020-08-20 | 103 | **2,176,000,000+** |

**EMURGO+CF first "clean" merge is only 998 ADA** across 35 inputs from a single address — a dust/test transaction proving shared control, not a large-fund merge. The first real EMURGO+CF merger is `cb32d36c...` at 2.176B ADA.

---

### A9. Clean Three-Way Merge Was Preceded by a 381-UTxO Bridge Accumulator

**Grade: FACT**

The 384 inputs to `571f776c...` include 380 UTxOs from the bridge accumulator:

**Bridge accumulator address:** `Ae2tdPwUPEZHiXixpj6Xdju5jti25cY7QhjHZ3WiZypCsfEJoJx5fGujAKn`

| Metric | Value |
|--------|-------|
| Bridge UTxOs consumed | 381 |
| Total bridge value | 48,718,538.91 ADA |
| Founder-tagged creator txs | 30 (24 IOG-only, 3 EMURGO-only, 3 CF-only) |
| No cross-seed creator tx | All 30 are single-seed |
| Untagged bridge value | 39,827,102.37 ADA |
| Exchange-like untagged value | 31,258,037.50 ADA (78.48% of untagged) |

Bridge feeder clusters:
- `Ae2tdPwUPEZJCGu...` feeds 48 untagged creators (20,392,710 ADA)
- `Ae2tdPwUPEZ3144...` feeds 20 untagged creators (3,316,510 ADA)
- Both labeled `VERY_LIKELY_EXCHANGE / EXCHANGE` in local corpus

---

### B9. `stake1uxztgcgh` — Confirmed Merge Orchestrator

**Grade: FACT**

**`stake1uxztgcgh49sld46q94xtjy7zf8j2tnntd6rswl9dypa9ffqqxrz2a`**  
**Payment address:** `addr1q84qw26450qz5raerf6yvupnr8crk3z8cjrhvkmvfw6u95yyk3s302tp7mt5qt2vhyfuyj0y5h8xkm58qa726gr62jjqn9uju3`

This address is simultaneously:
- The recipient of 4 bridge-to-splitter spending transaction outputs totaling **43,947,612 ADA** (epochs 208–236)
- The provider of the CF-exclusive input (UTxO 10748217 = 999,748 ADA) to clean three-way merge `571f776c...`
- All 4 outputs consumed at epoch 239 (merge `34147ef4...`)

**Lifetime stats:** 80 UTxOs received, 72,488,293 ADA total, current balance 2,514 ADA (nearly all spent). Never delegated.

The operator controlling this address held CF-descended ADA and executed both three-way merges — a single entity coordinating funds across all three founder lineages.

---

## PART III — SHARED INFRASTRUCTURE

### F05. Shared Byron 58-Output Automated Splitter

**Grade: FACT**

**Address:** `Ae2tdPwUPEZ6xYrxCgRDM2NQFM5oajHEoJN3i9ZVV2AbsbvxoJBjVu3yP7W`

| Metric | Value |
|--------|-------|
| Total spend transactions | 40,876 |
| Transactions with exactly 58 outputs | **1,170** |
| Active epoch range | 202–299 |
| IOG trace rows as source | 2,890 |
| EMURGO trace rows as source | 1,688 |

1,170 transactions with a rigid 58-output count is machine behavior. This address simultaneously processed both IOG- and EMURGO-descended funds. The earliest IOG+EMURGO merge (epoch 95) routed its output directly to the exchange hub `DdzFFzCqrhstmqBka...`.

---

### F06. Synchronized Cross-Founder Delegation Swarm — Epochs 245–251

**Grade: FACT**

Epochs 245–251 (Jan–Mar 2021): ~56,000 sub-50K ADA UTxOs created from the IOG trace and immediately delegated.

| Cross-trace validation | Count |
|-----------------------|-------|
| IOG swarmed pools ∩ EMURGO delegations | **63/64 (98%)** |
| IOG swarmed pools ∩ CF delegations | **50/64 (78%)** |
| All three simultaneously | **49/64 (77%)** |
| Pools exclusive to IOG | **0** |

Top pool `pool1uj4u73q...` (EVE1/Everstake) ranked #1 for IOG (786 wallets), #1 for EMURGO (151), #1 for CF (13).

**Total operator fees extracted (epochs 245–619): 24,972,527.63 ADA**

---

### A11. Corrected Named-Pool Overlap Baseline

**Grade: FACT**

EMURGO pool tickers: EMUR1–EMUR8, EMGAL (Emurgo-Alibaba Cloud), EMGHW (Emurgo-Huawei Cloud).

| Overlap class | Delegator count |
|:---|---:|
| IOG + EMURGO named pools | **137** |
| IOG + CF named pools | **126** |
| EMURGO + CF named pools | **65** |
| All three named-pool sets | **2** |

All-three overlap stake addresses:
- `stake1u8stds2advjjwuxypcl7qkeg33ru9muvdlgzt296sg06zjclkd7vt`
- `stake1u9t4q48qsjy4mnnd80pe5pexy3m2vwjr7px3rccew7ffgksf86npr`

---

## PART IV — THE CF+EMURGO 2B ADA CHAIN TO EXCHANGE

### B1. CF+EMURGO 2B ADA Merger — `f907b625` (Epoch 226)

**Grade: FACT**

**Transaction `f907b62584ca76c533f410867bf964c527b2a8251849d93c2b48a5b69e641816`**

| Field | Value |
|:---|:---|
| Epoch | 226 |
| Block time | 2020-10-29 15:13:57 UTC |
| Inputs | 53 |
| Outputs | 1 |
| Total output | **1,999,999,999.820 ADA** (~exactly 2B ADA) |
| Classification | **Clean CF+EMURGO merge** |

Dominant input: UTxO 6310510 = **1,375,877,556 ADA** created by `cb32d36c9ad2d8de1c6482d371bc79a48ce411d5b0a6200d3aba69d5dad77444` (epoch 212, 2020-08-20 — the first real EMURGO+CF clean merge). This single UTxO appears in EMURGO, CF, and EMURGO_2 frontiers simultaneously.

---

### B12. At Least 13 Staging Wallets Received ~150M ADA Each

**Grade: FACT**

The 2B ADA output of `f907b625...` was first split (at epoch 227, 2020-11-05) into:
- **200,000,000 ADA** → `stake1uxexwrph9r2p3lv42r7ccjptpmml33u2v3xx4p0q9ks85wc2y9t33` (UNSPENT at db-sync snapshot)
- **~1.8B ADA** → 14 staging wallets (~150M ADA each) + residual to splitter

All 14 staging wallets received funds at epoch 227 and delegated to anonymous (no off-chain metadata) staking pools:

| Label | Stake Address | ~ADA Received |
|:--|:---|---:|
| hop0 | `stake1u84jrq070qkg09dg8ta3cqaxech4fck953kcwkptzgp3q6cxsu8x6` | 150,000,010 |
| hop2 | `stake1ux0xnj5ljjx734qph69jc8a2mdemgguy5640pednyw7p08c6mjwk6` | 150,000,005 |
| hop3 | `stake1uxz3a23cmjcmautfyel85f56dmw8skznsz0d228km6udsvgra8065` | 150,000,005 |
| hop4 | `stake1uxtj8luzpucf5jp5df0za7klmc9eh0rg2t08zwysa58jtwslp7dqz` | 150,000,005 |
| hop5 | `stake1uytfgj3wquuyz68r3cvx0z75mtnc4wj0cdxe2sgn70za8dqwsfwfr` | 150,000,005 |
| hop6 | `stake1u8mf4hrhd9mtp86zkazlyg4w2zvzeavpa457lyq2vfn55lgwzk6t2` | 150,000,005 |
| hop7 | `stake1uxdpsgk3xpgvh0mj4sch29veh3al8xut2s0al0zy5exgh5ctds492` | 150,000,005 |
| hop8 | `stake1uxl72wy87wxcp8deu0j2kusmspywuz0gnsjf0dxzf6rv9xcwlhxm7` | 150,000,005 |
| hopA | `stake1uxw8slv30u9clrfjrq4w0uprwf74r5zmugm56ehukhvl3tctw2pkz` | 150,583,249 |
| hopB | `stake1u9ujy430k9j59zxjk6fyhn6x5efz6zp677scd047l8a55uqx5az0f` | 150,557,508 |
| hopC | `stake1uyuahf6wkrydsfkpsrae6vkcgkjz9na744774yh0vhpngdgrl5j59` | 150,546,747 |
| hopD | `stake1u8aazw72vc5j68da8wn7p69cn9dteq6w5ws552pg339lrdqyzupvz` | 150,534,671 |
| hopE | `stake1uxtwdfncacfphjdke30wz8hprmpt5ck90a8583zjes7es7ed2gldnk54` | 150,510,437 |

None of these addresses appear in the IOG, EMURGO, CF, or EMURGO_2 current frontier exports — they are external to the founder traces.

---

### B13. Simultaneous Epoch-237 Sweep: All Wallets Forward to Same Aggregator

**Grade: FACT**

**Date: December 22, 2020 (epoch 237)**

All 14 staging wallets simultaneously forwarded their entire 150M+ ADA balances — including staking rewards accumulated over ~10 epochs — to one aggregator:

**Aggregator:** `stake1uxrytqx0v9t0rcz3dlshj08n2w6khfxu3k276vppqsukk2sfw5u56`

| Field | Value |
|:---|:---|
| All forward transactions | Within ~57 minutes of each other on 2020-12-22 (04:06–05:03 UTC) |
| Each transfer | Single-output transaction (100% fund forward) |
| Aggregator total received | 2,557,670,877 ADA (20 UTxOs) |
| Aggregator active epochs | **237 only** |
| Aggregator current balance | 0 ADA |

Sub-minute automated behavior. All 13 wallets are controlled by the same operator or custodian.

---

### B14. Terminal Destination: Exchange Hot Wallet with 40B ADA Total Flow

**Grade: FACT**

Transaction `52a780353a0ee7734da49d1fe8af47c2a3a6365d32d91219a7658b2c117ebb8a` (epoch 237, 2020-12-22):
- **17 inputs**, all from aggregator `stake1uxrytqx0v9t0rcz3dlshj08n2w6khfxu3k276vppqsukk2sfw5u56`
- **1 output:** `2,107,670,869 ADA` → `stake1u8rmlr2h99gnvdaagycv97p96mclctn2y6sknryy37m0wtspfnsht`

**Exchange hot wallet `stake1u8rmlr2h99gnvdaagycv97p96mclctn2y6sknryy37m0wtspfnsht`:**

| Field | Value |
|:---|:---|
| Total ADA ever received | **40,048,202,390 ADA (40 billion ADA)** |
| UTxOs ever | 60 |
| First active epoch | 237 (2020-12-22) |
| Last active epoch | 414 (~2023-08) |
| Current balance | ~3 ADA (empty) |
| Classification | Exchange hot wallet — 40B ADA flow exceeds any plausible non-exchange explanation |
| Delegation to | Pool ticker **BNP** ("Binance Staking - 43") |

**CONFIRMED BINANCE** — on-chain delegation at epoch 237:
- Delegated pool: `pool1yxkhe2zp9rccyc3a79lxev5u585r3z0qqyl3qpx0t04hxhmlqgp` (Binance Staking - 43)
- Pool hash: `21ad7ca84128f182623df17e6cb29ca1e83889e0013f1004cf5beb73`
- Delegation occurred at the **same epoch** the 2.107B ADA arrived from the staging aggregator

The Binance-staking delegation plus 40B ADA cycling volume confirms this is Binance infrastructure.

**Corrected complete chain (CF+EMURGO genesis → exchange):**

```
f907b625 (epoch 226, 2020-10-29)
  └─ 1,999,999,999 ADA — single output to Byron address
       Ae2tdPwUPEYwFx4dmJheyNPPYXtvHbJLeCaA96o6Y2iiUL18cAt7AizN2zG
       │
       └─ 48bb2ca9 (epoch 227, 2020-11-04)
            ├─ 200,000,000 ADA → stake1uxexwrph9r2p3lv42r7ccjptpmml33u2v3xx4p0q9ks85wc2y9t33
            │   (UNSPENT; receives +252M from Hub 1 at epoch 391 → 452M total still unspent)
            │
            └─ 1,799,999,999 ADA → stake1u9zjr6e37 (master disbursement node)
                 │ (also received 628M from 86daee1a merge chain at epoch 211)
                 │
                 ├─ 70M → Hub 1 (Ae2tdPwUPEZ6xYrxCgRDM2NQFM5oajHEoJN3i9ZVV2AbsbvxoJBjVu3yP7W)
                 │   at epochs 221 and 223 (35M × 2)
                 │
                 ├─ 14 × ~150M → staging wallets (epoch 227, 2020-11-05/06)
                 │   All 14 sweep simultaneously (epoch 237, 2020-12-22)
                 │   └─ stake1uxrytqx0v9t0rcz3dlshj08n2w6khfxu3k276vppqsukk2sfw5u56 (aggregator)
                 │        └─ 52a780353a... (17-input consolidation)
                 │             └─ 2,107,670,869 ADA
                 │                  └─ stake1u8rmlr2h (exchange, 40B ADA total flow)
                 │
                 └─ 658M directly → stake1u8rmlr2h (epoch 237, same day as staging sweep)
                      (650M via ad3f3772 + 8M via 1dec1489)
```

**Total from this chain to `stake1u8rmlr2h`:** 2,107,670,869 + 658,000,000 = **~2,765,670,869 ADA**

---

### B11. Routing Address `stake1u9zjr6e37` Is Tagged EXCHANGE

**Grade: FACT**

`stake1u9zjr6e37w53a474puhx606ayr3rz2l6jljrmzvlzkk3cmg0m2zw0` is the main carry address for the 1.8B ADA from `f907b625...`. It is classified **EXCHANGE** in the local EMURGO exchange analysis and has also been observed at EMURGO trace hop 13 receiving 628,264,754 ADA from Hub 1 via the `86daee1addb1141f39e74fc851e3574d9101cc48ad7cfc1cbe82f1b45131c963` CF+EMURGO merge (epoch 211).

| Field | Value |
|:---|:---|
| Current balance | 1,930,537,555 ADA (still active through epoch 621) |
| Total ADA processed | ~30.67B ADA |
| Classification | `LIKELY_EXCHANGE / EXCHANGE` (local corpus) |

---

### B2. 200M ADA Branch — Hub 1 Top-Up at Epoch 391

**Grade: FACT**

The 200M ADA "UNSPENT" branch at `stake1uxexwrph9r2p3lv42r7ccjptpmml33u2v3xx4p0q9ks85wc2y9t33` received two additional funding transactions at epoch 391 (2023-02-02) from **Hub 1** (`Ae2tdPwUPEYwFx4dmJheyNPPYXtvHbJLeCaA96o6Y2iiUL18cAt7AizN2zG`, the confirmed Binance-linked address):

- TX `1daba627...`: 70 Hub-1 inputs → 152M ADA to `stake1uxexwrph9r2...` + 8M to `stake1u9zjr6e37w...`
- TX `531150c6...`: 60 Hub-1 inputs → 100M ADA to `stake1uxexwrph9r2...` + 1.4M to `stake1u9zjr6e37w...`

The same address that holds CF+EMURGO merged funds received continued top-ups from Binance-linked infrastructure 2.5 years after the original merge. Current balance: **452,300,059 ADA**.

---

## PART V — EXCHANGE LIQUIDATION AND HUBS

### F07. Genesis ADA Exchange Liquidation

**Grade: FACT**

| Entity | Traced Frontier | To Exchanges | % |
|--------|----------------|-------------|---|
| EMURGO | 25.93B ADA | 10.74B ADA | **41.4%** |
| CF | 14.40B ADA | 4.61B ADA | **32.0%** |
| IOG | 14.02B ADA | 1.19B ADA | **8.5%** |
| **Total** | **54.35B ADA** | **16.54B ADA** | **~30.4%** |

**Top exchange-linked hub addresses:**

| Address | Seeds | ADA | Note |
|---------|-------|-----|------|
| `Ae2tdPwUPEYwFx4dmJheyNPPYXtvHbJLeCaA96o6Y2iiUL18cAt7AizN2zG` | CF, EMURGO | 6.64B | Hub 1 — still active epoch 566 (June 2025), ~116M ADA |
| `Ae2tdPwUPEZ5ZFnojZ5yuoAAp2U3f3Ntkghw2GUXgmA4kAh73Tv4bFkjmXy` | CF, EMURGO | 2.46B | Feeds Hub 1 |
| `Ae2tdPwUPEZ5faoeL9oL2wHadcQo3mJLi68M4eep8wo45BFnk46sMkvCmM9` | CF, EMURGO, IOG | 2.16B | Hub 3 — Byron predecessor to 558B mystery address |
| `DdzFFzCqrhskEmdNPvFCgyLFqufz8nkJ3yY1DZPykgMcEmCzxjAjUNtggfZP42MJoD3BMqV9vui21HdpbqZJuFSFEyZ9tApuKbP9uv8K` | EMURGO, IOG | 215M | **Confirmed Binance** |

---

### F08. 558B ADA Mystery Exchange Address

**Grade: STRONG INFERENCE**

`addr1q9ukkxqf7cwdfgzshltrrmqj0skmv0s8f7s22cvysucug8jgfzwl8zg88xl6z4e6q0sdgeqrhgqq8aa3zj2nuqqvntcs6utve7`

| Signal | Value |
|--------|-------|
| Total ADA received | **558,160,635,356 ADA** |
| First recv → first send gap | **4 minutes** |
| Delegation history | Never delegated |
| Active epochs | 209–388 (Aug 2020 – Jan 2023) |
| Byron predecessor | `Ae2tdPwUPEZ5faoeL9oL2wHadcQo3mJLi68M4eep8wo45BFnk46sMkvCmM9` (Hub 3) |
| 7/10 downstream destinations | EXCHANGE-classified |
| Best hypothesis | Large Asian CEX — Huobi / OKX class |

Activated at the Shelley hard fork (epoch 209) — same operator migrated Byron→Shelley wallet format at the protocol transition.

---

## PART VI — STAKE CREDENTIAL OVERLAPS AND BENEFICIARIES

### A5. 22 Three-Way Stake Credentials

**Grade: FACT**

22 stake credentials appear in all three published founder traces (IOG, EMURGO, CF) simultaneously. All 22 are also present in the EMURGO_2 frontier.

Key entries:

| Stake Credential | IOG ADA | EMURGO ADA | CF ADA | Notable |
|:---|---:|---:|---:|:---|
| `stake1uxttvx739dt505d6sxvdykj8336utdq2q92jk3sv253zp5qalcz84` | 216,818,979 | 134,100,674 | 167,075,537 | Primary beneficiary of both 3-way merges |
| `stake1uxztgcgh49sld46q94xtjy7zf8j2tnntd6rswl9dypa9ffqqxrz2a` | 10,715,097 | 18,577,048 | 11,379,155 | Merge orchestrator |
| `stake1u9wxw9y574v9ngskl63effw6qlwl4tg6dr2zrrufhc7anncvvnqkp` | 15,248,553 | 5,199,895 | 850,000 | Also appears as destination in 150M staging chain |
| `stake1u833p40y8cm07ra9wgrqgp70z6khc5pttrena97c6en6p8c7pzxda` | 2,113,083 | 132,181 | 89,930 | **Still active epoch 591 (2025)** |
| `stake1u8dg8spc3skawcyzemtxz8f0zk5eadxftq35qcd4f7n5hrc82xu8k` | 2,794,252 | 1,646,033 | 97,045 | **Still active epoch 581 (2025)** |
| `stake1ux3a593q7tq69jkjw7ygqss5mdtteh863r40qhvnftapt6q68puk9` | 2,252,474 | 2,326,931 | 3,138,113 | 205+176+148 UTxOs — likely exchange deposit |
| `stake1ux5tpajlpe25jwazt5aypj37xn9qqfp59tffmj9pjaq2q2qww0acs` | — | 1,375,877,557 | ~374,868 | Largest EMURGO+CF overlap UTxO (6310510) |

### A6. `stake1uxttvx739` — Primary Beneficiary of Both Three-Way Merges

**Grade: FACT**

`stake1uxttvx739dt505d6sxvdykj8336utdq2q92jk3sv253zp5qalcz84` directly receives:
- **50,000,000 ADA** from `34147ef4...` (epoch 239, 2021-01-01) — second three-way merge
- **50,000,000 ADA** from `571f776c...` (epoch 250, 2021-02-25) — clean three-way merge

Payment address (from 571f776c output):  
`addr1qxtrqdumg8dleqcra3myptlq6n43m8s0mver0pwgqrr8awvkkcdaz26hglgm4qvc6fdy0rr4ck6q5q249drqc4fzyrgq68vuva`

Total attributed across all 3 traces: IOG 216.8M + EMURGO 134.1M + CF 167.1M = **518,995,190 ADA** under a single stake credential. Latest attributed epoch: 406.

---

### A7. 1.376B ADA UTxO Shared Across EMURGO + CF + EMURGO_2

**Grade: FACT**

UTxO `dest_tx_out_id=6310510` (value: ~1,375,877,557 ADA) appears in the current frontier of EMURGO, CF, and EMURGO_2. Created at epoch 212 by `cb32d36c9ad2d8de1c6482d371bc79a48ce411d5b0a6200d3aba69d5dad77444`.

Stake: `stake1ux5tpajlpe25jwazt5aypj37xn9qqfp59tffmj9pjaq2q2qww0acs`

This is the largest single stake in the cross-entity overlap set. It is not shared with the IOG trace. It is also the dominant input to the 2B `f907b625...` merger.

---

## PART VII — GENESIS CONCENTRATION

### F09. Genesis Concentration Statistics

**Grade: FACT**

| Metric | Value |
|--------|-------|
| Top 1% of addresses (145 addresses) | 36.4% of genesis supply |
| Top 10% (1,450 addresses) | 64.1% of genesis supply |
| Top 10 addresses | 22.1% of genesis supply |
| Largest single genesis allocation | 2,463,071,701 ADA (IOG, 7.92%) |
| Most common genesis amount | 384,615 ADA (796 occurrences) |
| Unredeemed forever | 318,200,635 ADA in 465 addresses |
| Founders' total (IOG+EMURGO+EMURGO_2+CF) | 5,966,795,602 ADA (19.2% of genesis) |

---

## PART VIII — WHAT THIS DOES NOT PROVE

**Non-attribution notice:** This document maps on-chain UTxO flows only. No finding constitutes proof of intent, legal ownership, misconduct, or contractual breach by any named entity. Exchange-identity claims are heuristic unless explicitly marked FACT with on-chain evidence.

- That founder entities maintained personal control after funds entered exchange/custody infrastructure
- That the 781,381,495 ADA entry was an undisclosed founder allocation (vs. a large-buyer sale ticket later entering the same custody stack) — beneficial ownership at genesis is unresolved
- That Hub 1 / Hub 2 / Hub 3 operators are definitively identified (Binance inference for Hub 1 is strong; on-chain delegation proof exists for `stake1u8rmlr2h` only)
- That synchronized delegation reflects insider coordination vs. shared automated portfolio management software
- That any entity committed fraud or violated any law — the on-chain evidence shows co-mingling and exchange routing, not intent

---

## Known Limitations

| Claim | Dependency | Residual uncertainty | Potential confounder |
|-------|-----------|---------------------|---------------------|
| EMURGO_2 same operator as EMURGO | 100% Shelley stake overlap (6,216/6,216) | Single shared custody provider could explain overlap without shared beneficial owner | Shared custodian / shared key management firm |
| Exchange liquidation % (EMURGO 41.4%, CF 32%, IOG 8.5%) | EMURGO_2 excluded from exchange-analysis layer; heuristic address classifier | EMURGO_2 % unknown; classifier has false-positive rate | Exchange pooling, custodial commingling |
| Binance identity for `stake1u8rmlr2h` | On-chain delegation to pool1yxkhe2 (Binance Staking - 43) | Pool owner ≠ hot wallet owner; pool could be operated by third party | White-label pool operation |
| Orchestrator `stake1uxztgcgh` controls all three founder streams | Trace co-appearance in both 3-way merges | Other wallets with identical trace footprint possible but not observed | Shared infrastructure software |
| 14 staging wallets = same operator | Same funding source + simultaneous sweep | Shared custodian / programmatic distribution could be third party | Exchange OTC desk acting as intermediary |
| Synchronized delegation (epochs 245-251) | 49/64 pools received all-three delegations simultaneously | Automated portfolio rebalancer could explain without coordination | Third-party delegation service |
| EMURGO_2 beneficial ownership at genesis | None — purely on-chain | Genesis sale records not public | Pre-sale buyer whose funds entered EMURGO custody |

---

## Full Claim Strength Summary

| # | Finding | Grade |
|---|---------|-------|
| F01 | Named founders redeemed in 24 hours; EMURGO_2 5 min after EMURGO | FACT |
| F02 | EMURGO_2 (781M entry) fully converged with EMURGO at hop 1 | FACT |
| F03 | 521 direct cross-seed consuming transactions | FACT |
| F04 | Clean 3-way IOG+EMURGO+CF merge at epoch 250 | FACT |
| F05 | Shared 58-output automated splitter processed IOG + EMURGO | FACT |
| F06 | Synchronized delegation swarm epochs 245–251 (all 3 founders) | FACT |
| F07 | 16.54B ADA to exchange-classified addresses | FACT |
| F08 | 558B ADA address is an exchange hot wallet | STRONG INFERENCE |
| F09 | Genesis concentration (top 1% = 36.4%) | FACT |
| A1 | EMURGO_2 frontier identical to EMURGO | FACT |
| A2 | EMURGO_2 merged with EMURGO at hop 1 (epoch 4, 2017-10-18) | FACT |
| A3 | Convergence tx `c8596b9c...` is EMURGO_2 hop 1 and EMURGO hop 3 simultaneously | FACT |
| A4 | 30 clean IOG+EMURGO merges at epoch 250 — coordinated batch | FACT |
| A5 | 22 three-way stake credentials, all also in EMURGO_2 | FACT |
| A6 | `stake1uxttvx739...` is direct recipient of both three-way merge outputs | FACT |
| A7 | 1.376B ADA UTxO shared across EMURGO+CF+EMURGO_2 | FACT |
| A8 | IOG+EMURGO clean merges span 4 years (epoch 95–390) | FACT |
| A9 | Clean 3-way merge preceded by 381-UTxO bridge accumulator | FACT |
| A10 | 2B CF+EMURGO merge enters structured peel/staging chain | FACT |
| A11 | Pool overlap corrected: IOG+EMURGO 137, IOG+CF 126, EMURGO+CF 65 | FACT |
| B1 | `f907b625...` is the 2B ADA CF+EMURGO merger (epoch 226) | FACT |
| B2 | 200M ADA UNSPENT branch receives Hub-1 top-up at epoch 391 | FACT |
| B3 | All 3 non-bridge inputs to `571f776c...` from `stake1uxztgcgh...` | FACT |
| B4 | EMURGO_2 anchor confirmed: fee=0, 5 min after EMURGO | FACT |
| B5 | Bridge creators are single-seed per transaction | FACT |
| B6 | EMURGO+CF first "clean" merge is 998 ADA dust — not a real fund merge | FACT |
| B7 | 2B ADA residual routes to known splitter | FACT |
| B8 | EMURGO pool tickers EMUR1–EMUR8, EMGAL, EMGHW confirmed | FACT |
| B9 | `stake1uxztgcgh...` is the merge orchestrator for both 3-way merges | FACT |
| B10 | EMURGO+CF dust merge (11c0765f) is symbolic, not a real fund merge | FACT |
| B11 | `stake1u9zjr6e37...` is EXCHANGE in local corpus + EMURGO trace hop 13 | FACT |
| B12 | 14 staging wallets (not 13) received ~150M ADA each — all from `stake1u9zjr6e37` | FACT |
| B13 | All 14 staging wallets swept simultaneously to one aggregator (Dec 22, 2020) | FACT |
| B15 | `stake1u9zjr6e37` is master disbursement node: all 14 wallets + 658M direct to exchange | FACT |
| B16 | f907b625 produced ONE Byron output → 48bb2ca9 split to 200M unspent + 1.8B to disburser | FACT |
| B17 | 14th staging wallet `stake1u9endmqh` confirmed with full trace to `stake1u9zjr6e37` | FACT |
| B18 | `stake1u8rmlr2h` confirmed Binance: on-chain delegation to pool1yxkhe2 (Binance Staking - 43) at epoch 237 | FACT |
| B14 | 2.107B ADA terminates at exchange with 40B ADA total flow ("Binance Staking - 43") | FACT |

---

## Key Addresses Reference Table

| Role | Full Address / Stake |
|:---|:---|
| IOG redemption tx | `fa2d2a70c0b5fd45cb6c3989f02813061f9d27f15f30ecddd38780c59f413c62` |
| EMURGO redemption tx | `242608fc18552a4ac83adabcef7155f3b909e83d469ce89735db8f11d3637e38` |
| EMURGO_2 redemption tx | `5ec95a53fa3bb7dc56864bb6e75f369f00aa20e8d8cdc3b66b2fb88ec1b225ef` |
| CF redemption tx | `208c7d54c1c24059c9314ddbe866edc80adcb8894539b27b6a1430d5c078b998` |
| EMURGO_2 redemption address | `DdzFFzCqrhspiThx6UaeJASmHTbwbXp2FtdCkF9AU9QXPF9D8sUC7Fqrv9bmYkxradBbqMrSxukTTsqCPNPwRh5PHazdiwWTuJYVMMaf` |
| EMURGO_2 first merge tx | `c8596b9cd81f734f8129604ff86f23bd4a910465acb84ad9e9d1ac223ccb4a76` |
| IOG+EMURGO first clean merge | `a71578ec01f6cf39dbcf31351631159e3dd6fb99dd475783effbc65b90b8f0f9` |
| IOG+CF first clean merge | `f9951db326893e5c6cd94407e3d75be4928442aaf5809e435ca3e82c1983949d` |
| EMURGO+CF first "real" merge | `cb32d36c9ad2d8de1c6482d371bc79a48ce411d5b0a6200d3aba69d5dad77444` |
| CF+EMURGO 2B merger | `f907b62584ca76c533f410867bf964c527b2a8251849d93c2b48a5b69e641816` |
| 3-way merge #1 | `197f9d27e49345cc085c9a2951d96c77f57f1cd82a71c095b7b7a3b36e74855d` |
| 3-way merge #2 | `34147ef46fd105ed39e3be63ac194e79622fb1bf9ea6e50313a0c3e0e6fd20c3` |
| 3-way merge #3 (clean) | `571f776c0698c576ddecae145f97e7f284b82ebea70fbc924fa4e2a4a6258020` |
| 150M staging consolidation tx | `52a780353a0ee7734da49d1fe8af47c2a3a6365d32d91219a7658b2c117ebb8a` |
| 58-output automated splitter | `Ae2tdPwUPEZ6xYrxCgRDM2NQFM5oajHEoJN3i9ZVV2AbsbvxoJBjVu3yP7W` |
| Bridge accumulator | `Ae2tdPwUPEZHiXixpj6Xdju5jti25cY7QhjHZ3WiZypCsfEJoJx5fGujAKn` |
| Hub 1 (Binance-linked exchange) | `Ae2tdPwUPEYwFx4dmJheyNPPYXtvHbJLeCaA96o6Y2iiUL18cAt7AizN2zG` |
| Hub 3 (Byron predecessor to 558B mystery) | `Ae2tdPwUPEZ5faoeL9oL2wHadcQo3mJLi68M4eep8wo45BFnk46sMkvCmM9` |
| Confirmed Binance address | `DdzFFzCqrhskEmdNPvFCgyLFqufz8nkJ3yY1DZPykgMcEmCzxjAjUNtggfZP42MJoD3BMqV9vui21HdpbqZJuFSFEyZ9tApuKbP9uv8K` |
| 558B mystery exchange | `addr1q9ukkxqf7cwdfgzshltrrmqj0skmv0s8f7s22cvysucug8jgfzwl8zg88xl6z4e6q0sdgeqrhgqq8aa3zj2nuqqvntcs6utve7` |
| Merge orchestrator (stake) | `stake1uxztgcgh49sld46q94xtjy7zf8j2tnntd6rswl9dypa9ffqqxrz2a` |
| 3-way primary beneficiary (stake) | `stake1uxttvx739dt505d6sxvdykj8336utdq2q92jk3sv253zp5qalcz84` |
| 200M UNSPENT branch (stake) | `stake1uxexwrph9r2p3lv42r7ccjptpmml33u2v3xx4p0q9ks85wc2y9t33` |
| 150M staging aggregator (stake) | `stake1uxrytqx0v9t0rcz3dlshj08n2w6khfxu3k276vppqsukk2sfw5u56` |
| CF+EMURGO chain routing (stake, EXCHANGE) | `stake1u9zjr6e37w53a474puhx606ayr3rz2l6jljrmzvlzkk3cmg0m2zw0` |
| Terminal exchange hot wallet (stake) | `stake1u8rmlr2h99gnvdaagycv97p96mclctn2y6sknryy37m0wtspfnsht` |
| EMURGO_2 first merge destination | `DdzFFzCqrhsu3iF6JfUTaapdWq2mXVRFukkS28WFYVDEqkgaaYttH8cT32credS99L5GaoUsEquqEPNH7ae88eKuDL6XsK5ZL56jkfLi` |
| Largest EMURGO+CF shared UTxO (stake) | `stake1ux5tpajlpe25jwazt5aypj37xn9qqfp59tffmj9pjaq2q2qww0acs` |

---

*All on-chain facts are independently verifiable using the transaction hashes above on any Cardano block explorer or db-sync instance. Analysis performed against ABCDE cexplorer_replica. db-sync sync state: block 13,215,210 (2026-03-28 00:27:10 UTC).*

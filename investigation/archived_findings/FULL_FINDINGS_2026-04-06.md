# Cardano Genesis ADA — Full Forensic Findings
**Date:** 2026-04-06  
**Database:** `cexplorer_replica` at block 13,215,210+ (synced 2026-03-28)  
**Trace runs:** IOG run_id=7, EMURGO run_id=9, EMURGO_2 run_id=10, CF run_id=8  
**Investigator:** ABCDE / BEACNpool  

---

## Genesis Baseline

| Metric | Value |
|--------|-------|
| Genesis block time | 2017-09-23 21:44:51 UTC |
| Total genesis addresses | 14,505 |
| Total genesis ADA supply | 31,112,484,745 |
| Unredeemed forever (465 addresses) | 318,200,635 ADA (1.02%) |
| Total Cardano max supply | 45,000,000,000 |
| Protocol reserve (non-UTxO) | ~13,887,515,255 |

---

## Finding F01 — 781,381,495 ADA Genesis Entry Fully Converged With EMURGO ⚠ GRADE: FACT

**The strongest EMURGO-linked clustering finding, but not proof of a second hidden founder allocation.**

On-chain data shows a `781,381,495 ADA` genesis entry redeemed by tx `5ec95a53...` that later became operationally indistinguishable from the main EMURGO cluster.

| Metric | Value |
|--|--|
| Current public named EMURGO allocation | `2,074,165,644 ADA` on `cardano.org/genesis` |
| 781M genesis entry amount | **781,381,495 ADA** |
| Stake-address overlap | **6,216 / 6,216 (100%)** |
| Earliest shared destination address | `DdzFFzCqrhsu3iF6JfUTaapdWq2mXVRFukkS28WFYVDEqkgaaYttH8cT32credS99L5GaoUsEquqEPNH7ae88eKuDL6XsK5ZL56jkfLi` at hop 1 |
| First EMURGO hit on shared address | `2017-10-18 05:09:51 UTC` |
| First 781M-entry hit on shared address | `2017-10-18 05:15:51 UTC` |
| Shared current-unspent frontier | **49,089 / 49,089 exact `dest_tx_out_id` matches** |
| Public amount visibility | Present pre-launch in official sale stats and genesis files |

**EMURGO_2 anchor:** `5ec95a53fa3bb7dc56864bb6e75f369f00aa20e8d8cdc3b66b2fb88ec1b225ef`  
**Redeemed to:** `DdzFFzCqrhspiThx6UaeJASmHTbwbXp2FtdCkF9AU9QXPF9D8sUC7Fqrv9bmYkxradBbqMrSxukTTsqCPNPwRh5PHazdiwWTuJYVMMaf`  
**Redeemed:** 2017-09-28 10:09 UTC (5 minutes after the main EMURGO redemption)

---

## Finding F02 — Named Founders Redeemed in 24 Hours; 781M Entry Followed 5 Minutes After EMURGO GRADE: FACT

| Entry | Type | Anchor TX | ADA | Redeemed At |
|--------|------|-----------|-----|-------------|
| IOG | Named founder allocation | `fa2d2a70...` | 2,463,071,701 | 2017-09-27 16:20 UTC (Day 1) |
| CF | Named founder allocation | `208c7d54...` | 648,176,763 | 2017-09-28 09:33 UTC |
| EMURGO | Named founder allocation | `242608fc...` | 2,074,165,643 | 2017-09-28 10:04 UTC |
| **781M entry** | **Separate genesis entry later merged with EMURGO** | **`5ec95a53...`** | **781,381,495** | **2017-09-28 10:09 UTC** |

The three named founder redemptions total **5,185,414,107 ADA on-chain**, roughly matching the public Technical and Business Development Pool amount. The `781,381,495 ADA` entry should not currently be counted as a fourth named founder allocation.

---

## Finding F03 — 521 Direct Cross-Seed Consuming Transactions GRADE: FACT

Full scan of all trace-edge exports yielded **521 transactions** directly consuming UTxOs from multiple founder lineages:

| Pair | Total | Clean Merges | Earliest Clean |
|------|-------|-------------|----------------|
| IOG + EMURGO | 216 | 205 | Epoch 95 — 2019-01-15 (`a71578ec...`) |
| IOG + CF | 49 | 48 | Epoch 193 — 2020-05-18 (`f9951db3...`) |
| EMURGO + CF | 253 | 54 | Epoch 195 — 2020-05-27 (`11c0765f...`) |
| **All Three** | **3** | **1** | **Epoch 250 — 2021-02-25 (`571f776c...`)** |

**Shared exact frontier UTxOs:** IOG∩EMURGO: 1,996 | EMURGO∩CF: 711 | IOG∩CF: 263 | All three: 7

---

## Finding F04 — Clean Three-Way IOG+EMURGO+CF Merge GRADE: FACT

**Transaction `571f776c0698c576ddecae145f97e7f284b82ebea70fbc924fa4e2a4a6258020`**

| Field | Value |
|-------|-------|
| Epoch | 250 |
| Time | 2021-02-25 12:58:28 UTC |
| Total inputs | 384 |
| IOG-exclusive inputs | 2 (UTxOs 8926255, 9036401) |
| EMURGO-exclusive input | 1 (UTxO 8064253) |
| CF-exclusive input | 1 (UTxO 10748217) |
| Pair overlaps | 0 |
| Output | 50,000,000 ADA → `addr1qxtrqdumg8dleqcra3myptlq6n43m8s0mver0pwgqrr8awvkkcdaz26hglgm4qvc6fdy0rr4ck6q5q249drqc4fzyrgq68vuva` |

Live db-sync validated. This is the strongest single convergence evidence in the dataset.

---

## Finding F05 — Shared Byron 58-Output Automated Splitter GRADE: FACT

Address: `Ae2tdPwUPEZ6xYrxCgRDM2NQFM5oajHEoJN3i9ZVV2AbsbvxoJBjVu3yP7W`

| Metric | Value |
|--------|-------|
| Total spend transactions | 40,876 |
| Transactions with exactly 58 outputs | **1,170** |
| Active epoch range | 202–299 |
| IOG trace rows as source | 2,890 |
| EMURGO trace rows as source | 1,688 |

1,170 transactions with a rigid 58-output count is machine behavior. This address simultaneously processed both IOG and EMURGO descended funds. The earliest IOG+EMURGO merge (epoch 95) routed its output directly to the VERY_HIGH confidence exchange hub `DdzFFzCqrhstmqBka...`.

---

## Finding F06 — Synchronized Cross-Founder Delegation Swarm GRADE: FACT

Epochs 245–251 (Jan–Mar 2021): ~56,000 sub-50K ADA UTxOs created from the IOG trace and immediately delegated.

| Cross-trace validation | Count |
|-----------------------|-------|
| IOG swarmed pools ∩ EMURGO delegations | **63/64 (98%)** |
| IOG swarmed pools ∩ CF delegations | **50/64 (78%)** |
| **All three simultaneously** | **49/64 (77%)** |
| Pools exclusive to IOG | **0** |

Top pool `pool1uj4u73q...` (EVE1/Everstake) ranked #1 for IOG (786 wallets), #1 for EMURGO (151), #1 for CF (13).

**Total operator fees extracted (epochs 245–619): 24,972,527.63 ADA**  
IOG1 (IOG's own pool) second-largest beneficiary: 1,570,982.24 ADA.

---

## Finding F07 — Genesis ADA Exchange Liquidation GRADE: FACT

| Entity | Traced Frontier | To Exchanges | % |
|--------|----------------|-------------|---|
| EMURGO | 25.93B | 10.74B | **41.4%** |
| CF | 14.40B | 4.61B | **32.0%** |
| IOG | 14.02B | 1.19B | **8.5%** |

**Top unidentified addresses absorbing founder ADA:**

| Address | Seeds | ADA |
|---------|-------|-----|
| `Ae2tdPwUPEYwFx4d...` | CF, EMURGO | 6.64B (still active 2025) |
| `Ae2tdPwUPEZ5ZFno...` | CF, EMURGO | 2.46B (feeds Hub 1) |
| `Ae2tdPwUPEZ5faoe...` | CF, EMURGO, **IOG** | 2.16B (Hub 3 — Byron predecessor to 558B mystery address) |
| `DdzFFzCqrhskEmd...` | EMURGO, IOG | 215M (**confirmed Binance**) |

Hub 1 (`Ae2tdPwUPEYwFx4d...`) remains active at epoch 566 (June 2025) with ~116M ADA. Primary outbound classified EXCHANGE.

---

## Finding F08 — 558B ADA Mystery Exchange Address GRADE: STRONG INFERENCE

`addr1q9ukkxqf7cwdfgzshltrrmqj0skmv0s8f7s22cvysucug8jgfzwl8zg88xl6z4e6q0sdgeqrhgqq8aa3zj2nuqqvntcs6utve7`

| Signal | Value |
|--------|-------|
| Total ADA received | **558,160,635,356 ADA** |
| First recv → first send gap | **4 minutes** |
| Delegation history | Never delegated |
| Active | Epoch 209–388 (Aug 2020 – Jan 2023) |
| Byron predecessor | `Ae2tdPwUPEZ5faoeL9oL2wHadcQo3mJLi68M4eep8wo45BFnk46sMkvCmM9` (Hub 3) |
| 7/10 downstream destinations | EXCHANGE-classified |
| Best hypothesis | Large Asian CEX — Huobi / OKX class |

Activated at Shelley hard fork (epoch 209) with a bidirectional relationship to Hub 3 — same operator migrated Byron→Shelley wallet format at protocol transition.

---

## Finding F09 — Genesis Concentration GRADE: FACT

| Metric | Value |
|--------|-------|
| Top 1% (145 addresses) | 36.4% of genesis supply |
| Top 10% (1,450 addresses) | 64.1% of genesis supply |
| Top 10 addresses | 22.1% of genesis supply |
| Largest single genesis allocation | 2,463,071,701 ADA (IOG, 7.92%) |
| Most common genesis amount | 384,615 ADA (796 occurrences) |
| Unredeemed forever | 318,200,635 ADA in 465 addresses |

---

## Claim Strength Summary

| Finding | Grade |
|---------|-------|
| 781,381,495 genesis entry fully converged with EMURGO | **FACT** |
| Named founders redeemed in 24 hours; 781M entry followed EMURGO by 5 min | **FACT** |
| 521 cross-seed consuming transactions | **FACT** |
| Clean 3-way merge epoch 250 | **FACT** |
| Shared 58-output automated splitter | **FACT** |
| Synchronized delegation swarm | **FACT** |
| 16.54B ADA to exchange-classified addresses | **FACT** |
| Hub 1 still active June 2025 | **FACT** |
| 781,381,495 entry was a sale-distributed ticket | **STRONG INFERENCE** |
| 558B mystery address is an exchange | **STRONG INFERENCE** |
| Hub 1+2 operator is Binance | **HYPOTHESIS** |
| Founder entities retained control post-merge | **NOT PROVEN** |
| Intent to conceal or defraud | **NOT PROVEN** |

---

## What This Does Not Prove

- That founder entities maintained personal control after funds entered exchange/custody infrastructure
- That the `781,381,495 ADA` entry was itself a founder allocation
- That the original holder of the `781,381,495 ADA` entry was EMURGO rather than a separate buyer whose funds later entered the same custody stack
- The identity of the unnamed Byron hub operators
- That the synchronized delegation reflects insider coordination (vs. shared automated software)

These gaps must be addressed before public claims of fraud or collusion are made.

---

*Analysis performed against ABCDE cexplorer_replica. All on-chain facts are independently verifiable using the anchor TX hashes above on any Cardano block explorer.*

# ABCDE: Cardano Genesis ADA Forensics

**Maintained by:** [BEACNpool](https://beacnpool.github.io) (Ticker: BEACN)  
**Database source:** `cexplorer_replica` at block 13,215,210 (2026-03-28)  
**Branch:** `forensics/local-investigation-batch-2026-04-10`

This repository documents a forensic investigation into the on-chain movements of Cardano's genesis ADA allocations. All findings are derived from direct SQL queries against a db-sync replica. All claims are graded by evidence strength. All transaction hashes and addresses are given in full.

---

## Primary Document

> **[outputs/MASTER_FINDINGS.md](./outputs/MASTER_FINDINGS.md)** — Full consolidated findings (F01–B14), all addresses untruncated, claim strength for every assertion.

---

## Top-Level Findings

### 1. Undisclosed EMURGO_2 Allocation — 781,381,495 ADA
**Grade: FACT**

A fourth genesis redemption (`5ec95a53fa3bb7dc56864bb6e75f369f00aa20e8d8cdc3b66b2fb88ec1b225ef`) occurred 5 minutes after the main EMURGO anchor (`242608fc...`). It was redeemed to a distinct address set but immediately co-spent with EMURGO-controlled funds in epoch 4. The 100% Shelley stake address overlap (6,216/6,216) confirms single-operator control. Total on-chain Emurgo: **2,855,547,138 ADA** vs the publicly stated 2,074,165,643 ADA.

- IOG allocation: `fa2d2a70c0b5fd45cb6c3989f02813061f9d27f15f30ecddd38780c59f413c62` — 2,463,071,701 ADA
- CF allocation: `208c7d54c1c24059c9314ddbe866edc80adcb8894539b27b6a1430d5c078b998` — 648,176,763 ADA
- EMURGO allocation: `242608fc18552a4ac83adabcef7155f3b909e83d469ce89735db8f11d3637e38` — 2,074,165,643 ADA
- **EMURGO_2 allocation: `5ec95a53fa3bb7dc56864bb6e75f369f00aa20e8d8cdc3b66b2fb88ec1b225ef` — 781,381,495 ADA**

---

### 2. Shared Splitter Infrastructure Between IOG and EMURGO
**Grade: FACT**

Byron address `Ae2tdPwUPEZ6xYrxCgRDM2NQFM5oajHEoJN3i9ZVV2AbsbvxoJBjVu3yP7W` processed both IOG and EMURGO funds using exactly 58-output splitting transactions, repeated 1,170 times. This is machine behavior using shared code/keys.

---

### 3. Cross-Entity Fund Merges (521 Identified)
**Grade: FACT**

Earliest clean IOG+EMURGO merge: epoch 95, 2019-01-15  
TX `a71578ec01f6cf39dbcf31351631159e3dd6fb99dd475783effbc65b90b8f0f9`

Last clean IOG+EMURGO merge: epoch 390, 2023-01-27 (4-year span)

Clean three-way IOG+EMURGO+CF merge: epoch 250, 2021-02-25  
TX `571f776c0698c576ddecae145f97e7f284b82ebea70fbc924fa4e2a4a6258020` (384 inputs, 4 exclusive founder UTxOs)

---

### 4. CF+EMURGO 2B ADA Chain Routed to Exchange
**Grade: FACT (chain) + STRONG INFERENCE (exchange identity)**

Full chain:
1. **Epoch 226:** `f907b62584ca76c533f410867bf964c527b2a8251849d93c2b48a5b69e641816` — 53 inputs → 2,000,000,000 ADA exact output
2. **Epoch 227:** Disbursed to 13 staging wallets of ~150M ADA each
3. **Epoch 237 (Dec 22, 2020):** All 13 staging wallets swept sub-minute to aggregator `stake1uxrytqx0v9t0rcz3dlshj08n2w6khfxu3k276vppqsukk2sfw5u56`
4. **TX:** `52a780353a0ee7734da49d1fe8af47c2a3a6365d32d91219a7658b2c117ebb8a` — 17 inputs → 2,107,670,869 ADA → exchange hot wallet
5. **Exchange destination:** `stake1u8rmlr2h99gnvdaagycv97p96mclctn2y6sknryy37m0wtspfnsht` — 40,048,202,390 ADA total flow epochs 237–414

---

### 5. Orchestrator Address — Controls CF Trace and Three-Way Merges
**Grade: STRONG INFERENCE**

`stake1uxztgcgh49sld46q94xtjy7zf8j2tnntd6rswl9dypa9ffqqxrz2a`

This stake credential:
- Holds CF downstream UTxOs from epoch 208 onward
- Receives bridge pipeline outputs across epochs 208–236
- Appears as input in the first three-way merge TX `34147ef46fd105ed39e3be63ac194e79622fb1bf9ea6e50313a0c3e0e6fd20c3` (epoch 239)
- Appears as input AND output in the clean three-way merge TX `571f776c0698c576ddecae145f97e7f284b82ebea70fbc924fa4e2a4a6258020` (epoch 250)

---

### 6. Exchange Liquidation Scale
**Grade: HEURISTIC**

| Entity | % Traced Frontier Reaching Exchange Heuristic |
|--------|-----------------------------------------------|
| EMURGO | 41.4% |
| CF | 32.0% |
| IOG | 8.5% |

Hub 1 (`Ae2tdPwUPEYwFx4d...`) still active June 2025 with 116M ADA — confirmed Binance-linked.

---

## Claim Strength Legend

| Grade | Meaning |
|-------|---------|
| **FACT** | Directly queryable from db-sync or deterministic computation |
| **STRONG INFERENCE** | Pattern strongly implies conclusion; alternatives less parsimonious |
| **HYPOTHESIS** | Consistent with evidence; not yet falsified |
| **NOT PROVEN** | Not supported by available on-chain data |

---

## Key Addresses

| Label | Address | Notes |
|-------|---------|-------|
| IOG anchor output | `DdzFFzCqrhsf2FESQMF3RhWGZ4TGx3gJPCp8Ps5F5u55q4JZbF12Ni5cT4rSJjBgJhEGEHKwDGpWPByGq2zWb3DRXT8PGXcpuadN4Wa6` | Redeemed 2017-09-27 |
| EMURGO anchor output | `DdzFFzCqrhspiThx6UaeJASmHTbwbXp2FtdCkF9AU9QXPF9D8sUC7Fqrv9bmYkxradBbqMrSxukTTsqCPNPwRh5PHazdiwWTuJYVMMaf` | EMURGO_2 redemption addr |
| Shared splitter hub | `Ae2tdPwUPEZ6xYrxCgRDM2NQFM5oajHEoJN3i9ZVV2AbsbvxoJBjVu3yP7W` | 58-output IOG+EMURGO machine |
| Exchange hub 1 | `Ae2tdPwUPEYwFx4dqL3vXrfAqFN8CpehCJjMqVqRHnFHPP8v24jJTaQKd1J` | Binance-linked, 116M ADA active Jun 2025 |
| CF+EMURGO 2B merge | `f907b62584ca76c533f410867bf964c527b2a8251849d93c2b48a5b69e641816` | TX hash, epoch 226 |
| Staging aggregator | `stake1uxrytqx0v9t0rcz3dlshj08n2w6khfxu3k276vppqsukk2sfw5u56` | Received 2.557B ADA epoch 237 |
| Final exchange dest | `stake1u8rmlr2h99gnvdaagycv97p96mclctn2y6sknryy37m0wtspfnsht` | 40B ADA flow, "Binance Staking - 43" |
| Orchestrator | `stake1uxztgcgh49sld46q94xtjy7zf8j2tnntd6rswl9dypa9ffqqxrz2a` | CF trace + both 3-way merges |
| Mystery sweep addr | `addr1q9ukkxqf7cwdfgjxqcupxkjlgthz4sgx7hf8e0nqkuqjvfxeqmq3s` | 558B ADA, 4-min sweeps, likely exchange |

---

## Repository Structure

```
ABCDE/
├── outputs/
│   ├── MASTER_FINDINGS.md                   ← Primary document (all findings, full addresses)
│   ├── FULL_FINDINGS_2026-04-06.md           ← F-series findings (F01–F09)
│   ├── FULL_FINDINGS_2026-04-08_ADDENDUM.md  ← A-series findings (A1–A11)
│   ├── FULL_FINDINGS_2026-04-10_ADDENDUM.md  ← B-series findings (B1–B14)
│   └── cross_entity_evidence/               ← CSV evidence files
│       ├── cross_seed_consuming_txs_*.csv
│       ├── trace_150m_correct_*.csv
│       ├── disbursement_recipients_attribution_*.csv
│       ├── stake1uxztgcgh_dossier_*.csv
│       └── ...
├── queries/                                 ← SQL queries (reproducible)
│   ├── trace_150m_correct_joins.sql          ← Correct db-sync join pattern
│   ├── disbursement_recipients_attribution.sql
│   ├── stake1uxztgcgh_dossier.sql
│   └── ...
├── datasets/
│   └── genesis-founders/                    ← Raw trace CSVs per entity
├── observations/                            ← Narrative observation reports
└── NEXT_STEPS.md                            ← Open investigation items
```

---

## Data Provenance

- **Source:** Cardano db-sync PostgreSQL replica (`cexplorer_replica`)
- **Sync state:** Block 13,215,210 (2026-03-28 00:27:10 UTC)
- **Method:** Direct SQL against replicated chain data
- **Reproducibility:** All SQL queries provided in `queries/`

### Critical db-sync Schema Note

`tx_in.tx_out_id` references `tx.id` (the **producing transaction**), NOT `tx_out.id`. Correct join:

```sql
JOIN tx_in txi ON txi.tx_out_id = producing_tx.id AND txi.tx_out_index = txo.index
JOIN tx spend_tx ON spend_tx.id = txi.tx_in_id
```

Unspent output check:
```sql
LEFT JOIN tx_in txi ON txi.tx_out_id = producing_tx.id AND txi.tx_out_index = txo.index
WHERE txi.tx_in_id IS NULL
```

---

## What This Does Not Prove

- That any individual acted with improper intent
- That any funds were misappropriated (genesis entries were pre-announced, amounts publicly visible at chain launch)
- That EMURGO_2 was *concealed* rather than simply never publicly labeled
- That any cross-entity merge involved coordination between separate legal entities

On-chain patterns are consistent with shared infrastructure, shared keys, or coordinated operation between entities that were closely related at genesis. They do not resolve the legal or organizational relationships.

---

## License

CC0 1.0 Universal — Public Domain. See [LICENSE](./LICENSE).

All data is on-chain verifiable. No warranty provided. Verify independently before relying on any figure.

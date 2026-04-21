# Investigation Next Steps
**Last updated:** 2026-04-10  
**Status:** Active — DB blocked (client IP changed to ${DB_HOST}; fix pg_hba.conf); new findings documented in `FULL_FINDINGS_2026-04-10_ADDENDUM.md`

---

## Latest DB-Backed Additions — 2026-04-08

- `781M` first downstream spend is a **direct co-spend** with an EMURGO-derived UTxO, not merely a later shared-address overlap
- Both EMURGO and `781M` redemption outputs sat dormant for about `475.1` hours, then activated on `2017-10-18`
- The public-sale profile still matches the max `Tranche 4` / `Japan` / `Company` / `BTC` ticket
- Official EMURGO self-descriptions conflict on chronology: some pages say Tokyo since `June 2017`, later pages say established in `2015`
- The old official `cardano.org/en/ada-distribution-audit/` page has been recovered via Wayback; the unresolved gap is now the underlying tranche reports or any standalone attachment beyond that page, not the existence of a public audit page
- The clean three-way merge path includes a **381-UTxO bridge accumulator**; directly tagged creator txs are all single-seed (`24 IOG`, `3 EMURGO`, `3 CF`)
- The top two feeder addresses behind the **351 untagged** bridge creators already appear in **49** distinct untagged creator txs totaling **24.908M ADA** of bridge output (`62.54%` of untagged bridge value) and are labeled **exchange-like** in the local corpus
- The broader weak exchange-like screen now covers **64** untagged bridge creator txs totaling **31.258M ADA** of bridge output (`78.48%` of untagged bridge value), leaving only **8.569M ADA** outside that screen
- The residual `8.569M ADA` is itself split between **210 single-feeder creators** (`3.002M ADA`) and a **12-tx late large multi-feeder batch cluster** (`3.057M ADA` across epochs `240-249`)
- The **210 single-feeder** residual creators are a genuinely unlabeled set in the current local corpus: they map to **209** unique feeder addresses and **0 / 209** appear anywhere in the local exchange-analysis exports
- That 12-tx residual batch cluster now looks like a **standardized consolidation layer**, not a hidden common wallet: **11 / 12** creators hit an exact **80-input** shape, none of their feeder source tx hashes are shared across creators, and exact denominations (`10`, `100`, `1,000`, `5,000 ADA`) recur across multiple creators even while the feeder addresses themselves mostly do not
- Clean CF+EMURGO merge `f907b625...` enters a **structured 150M ADA peel chain** after an immediate 200M / 1.8B split
- The main `f907b625...` carry stake is already tagged **`LIKELY_EXCHANGE / EXCHANGE`** in local EMURGO exchange analysis and is fed from Hub 1; the 200M branch is later re-funded by two **Hub-1-only** txs paired with that carry stake, and a later carry stake delegates to **`BNP` / `Binance Staking - 43`**
- Sampled follow-on large txs on the other 150M side branches are mostly **same-stake self-churn**, making the 200M branch the unusual later-funded side branch
- Corrected named-pool overlap baseline is **137 IOG+EMURGO**, **126 IOG+CF**, **65 EMURGO+CF**, **2 all-three** after fixing EMURGO pool matching

Implication: the live attribution question is narrower, but not closed. The `781M` source is consistent with a sale-ticket-sized entry administered via infrastructure shared with EMURGO from epoch 4, while EMURGO's own public chronology remains inconsistent enough that the original-holder story cannot yet be reduced to a simple yes/no on corporate existence.

---

## Completed 2026-04-10

- [x] **All 6 db-sync query scripts run successfully** — bridge creator step 1, steps 3–6, EMURGO_2 analysis
- [x] **Bridge creator tagging complete** — 24 IOG, 3 CF, 3 EMURGO creator txs all single-seed; 3,616/3,675 feeders untagged (bridge recirculations)
- [x] **Top-50 cross-seed txs by value ranked** — `cb32d36c` (2.176B, CF+EMURGO clean, epoch 212) is the largest; `f907b625` (2.000B exactly, CF+EMURGO clean, epoch 226, 53→1)
- [x] **2B ADA peel chain traced** — 8 × 150M disbursements to external stake addresses (none in founder traces), 200M UNSPENT, residual to splitter
- [x] **EMURGO_2 anchor confirmed by db-sync** — epoch 0, slot 19513, 2017-09-28 10:09:11 (exactly 5 min after EMURGO)
- [x] **All 3 non-bridge inputs to `571f776c` identified** — all from `stake1uxztgcgh` (the secondary beneficiary and CF-input provider simultaneously)
- [x] **First pairwise clean merge dossiers** — IOG+CF: 1.8M ADA; EMURGO+CF: only 998 ADA (35 inputs, 1 address — symbolic/test tx)
- [x] **New client IP documented** — ${DB_HOST}; pg_hba.conf update required on db server

---

## Completed 2026-04-08

- [x] **EMURGO_2 == EMURGO confirmed** — identical 49,089-UTxO frontier, 100% deoverlap overlap, 0 exclusive entries either side
- [x] **EMURGO_2 merged with EMURGO at hop 1, epoch 4** — convergence tx `c8596b9c...` creates 1.856B ADA UTxO from both EMURGO_2 hop-1 and EMURGO hop-3 inputs
- [x] **30 clean IOG+EMURGO merges at epoch 250** — coordinated batch coinciding with clean three-way merge
- [x] **22 three-way stake credentials fully characterized** — all also in EMURGO_2; `stake1uxttvx739...` is the primary beneficiary (directly receives 50M ADA from both three-way merges)
- [x] **1.376B ADA UTxO (id=6310510)** confirmed shared across EMURGO+CF+EMURGO_2 at epoch 212
- [x] **205 clean IOG+EMURGO merges run to epoch 390** (January 27, 2023) — sustained pattern confirmed (4-year span, Jan 2019–Jan 2023)
- [x] **381-UTxO bridge accumulator behind `571f776c...` characterized** — 30 directly founder-tagged creator txs, all single-seed
- [x] **Single-feeder residual bridge bucket triaged locally** — `210` creators, `209` unique feeder addresses, and `0` local exchange-corpus hits
- [x] **12 late residual bridge batch creators classified** — standardized `80`-input-style consolidation batches with weak cross-creator feeder reuse, not a dominant hidden wallet cluster
- [x] **2B clean CF+EMURGO merge `f907b625...` traced into structured peel chain** — repeated ~150M side outputs plus 200M branch
- [x] **`f907b625...` downstream chain now has convergent exchange/custody signals** — `stake1u9zjr...` is tagged `LIKELY_EXCHANGE / EXCHANGE`, the 200M branch is later re-funded by Hub-1-only paired txs, and a later carry stake delegates to `BNP` / `Binance Staking - 43`
- [x] **Named-pool overlap baseline corrected** — EMURGO pool scope fixed; pairwise and all-three counts refreshed live
- [x] Annotated cross-seed consuming transactions CSV with correct clean_merge flags
- [x] Merge timeline document
- [x] EMURGO_2 convergence evidence document
- [x] db-sync query scripts written and live-tested
- [x] Seed-trace tagging Python script for bridge feeder analysis

---

## Immediate Priorities (Do First)

### 1. Identify The Original Holder Of The 781,381,495 ADA Entry ⚠ HIGHEST PRIORITY
Public-source review is now complete enough to narrow the question. The exact `781,381,495 ADA` amount was public before launch in official sale stats and genesis files, and it later converged almost immediately with the EMURGO pipeline. The open question is no longer "was the amount hidden?" but **who originally held this entry at redemption**.

- [x] Search official Cardano public docs and repos for the exact amount
- [x] Confirm the amount was public pre-launch in sale stats and genesis files
- [x] Confirm immediate downstream convergence with EMURGO
- [x] Confirm the first `781M` downstream spend directly co-spends with an EMURGO-derived UTxO
- [x] Confirm that official EMURGO public materials conflict on founding/registration chronology
- [x] Recover the old official public audit summary page (`/en/ada-distribution-audit/`)
- [ ] Determine whether the entry reflects co-ownership with EMURGO, separate beneficial ownership under shared administration, or an unrelated buyer later entering common custody
- [ ] Reconcile EMURGO chronology (`2015` vs `June 2017`) using archived company materials or registry records
- [ ] Recover the underlying tranche audit reports or any standalone summary attachment beyond the recovered public audit page
- [ ] Prove the exact historical target of the rebuilt `Further information on the sale` sentence, if possible
- [ ] Look for buyer/distributor metadata that can name the holder

**Key data:**
- Anchor TX: `5ec95a53fa3bb7dc56864bb6e75f369f00aa20e8d8cdc3b66b2fb88ec1b225ef`
- Amount: 781,381,495 ADA (2.51% of genesis supply)
- Redeemed to: `DdzFFzCqrhspiThx6UaeJASmHTbwbXp2FtdCkF9AU9QXPF9D8sUC7Fqrv9bmYkxradBbqMrSxukTTsqCPNPwRh5PHazdiwWTuJYVMMaf`
- EMURGO_2 overlap with EMURGO stake addresses: **6,216 / 6,216 = 100%**
- Earliest shared destination address with EMURGO: `DdzFFzCqrhsu3iF6...` at hop 1 on 2017-10-18
- Direct merge tx: `c8596b9c...` consumes `5ec95a53...#0` plus EMURGO-derived `743fd051...#0`
- Shared current-unspent frontier with EMURGO: **49,089 / 49,089**
- EMURGO official public chronology: inconsistent (`2015` established in Japan vs `June 2017` Tokyo registration)

---

### 2. Load Investigation Findings Into Database
Status: **completed on 2026-04-08**.

Created reference tables:

- `genesis_investigation_findings`
- `genesis_entity_allocations`
- `genesis_key_transactions`
- `genesis_investigation_notes`

Current follow-up:

- [ ] Refresh the wording in the DB rows to match the revised EMURGO_2 classification
- [ ] Keep `codex_audit` as read-only after any future refreshes

Historical loader command:
```bash
psql -h ${DB_HOST} -p 5432 -U postgres -d cexplorer_replica \
  -f queries/load_investigation_findings.sql
```

---

### 3. Identify Hub 1 Operator — Still Active in 2025
Hub 1 address `Ae2tdPwUPEYwFx4dmJheyNPPYXtvHbJLeCaA96o6Y2iiUL18cAt7AizN2zG` has **~116M ADA as of epoch 566 (June 2025)** and remains active. This is a living entity.

- [ ] Submit to Chainalysis or Elliptic for named-exchange attribution
- [ ] Check the Binance cold wallet database (Hub 1 feeds into confirmed Binance address `DdzFFzCqrhskEmd...`)
- [ ] Query current balance: `SELECT SUM(value)/1000000.0 FROM tx_out WHERE address = 'Ae2tdPwUPEYwFx4dmJheyNPPYXtvHbJLeCaA96o6Y2iiUL18cAt7AizN2zG' AND NOT EXISTS (SELECT 1 FROM tx_in WHERE tx_out_id = tx_out.tx_id AND tx_out_index = tx_out.index)`
- [ ] Trace its last 20 transactions to see if it's still actively moving ADA

---

### 4. Full Backtrace of Every Clean Pairwise Merge (Updated 2026-04-10)
For the 205 clean IOG+EMURGO, 48 clean IOG+CF, and 54 clean EMURGO+CF merges: trace each direct input one hop back. Classify each merge point as:
- `FOUNDER_CONTROLLED` — address matches known founder infrastructure
- `EXCHANGE` — matches exchange roster
- `CUSTODY` — third-party custodian signature
- `OTC` — over-the-counter desk pattern
- `UNKNOWN`

SQL template in `queries/cross_entity_merge_validation.sql`. Extend with hop-back logic.

Priority sub-branches now identified:

- [ ] Do one-hop db-sync enrichment for the **12** late residual bridge batch creators when the replica is responsive again: source-output age, source-tx fanout, and any missed exchange/custody signatures upstream
- [ ] Do one-hop db-sync enrichment for the top **single-feeder** residual creators, starting with `860fbcc1...` (`999,504.833984 ADA`) and `82ae9465...` (`279,302.521853 ADA`), since the local exchange corpus provides **0** attribution hits for that bucket
- [x] Trace the `f907b625...` peel recipients — **COMPLETED 2026-04-10**: 13+ staging wallets (not 8); all swept Dec 22, 2020 to aggregator stake1uxrytqx0; 2.107B ADA terminal to exchange (40B ADA flow); see B12–B14
- [ ] Determine whether the 200M unspent branch (`stake1uxexwrph9`) has independent exchange/custody labeling beyond Hub-1 paired funding
- [x] Run `queries/stake1uxztgcgh_dossier.sql` — **COMPLETED 2026-04-10**: no delegations; 72.5M ADA lifetime; 2,514 ADA current
- [x] Run `queries/disbursement_recipients_attribution.sql` — **COMPLETED 2026-04-10**: all 8 labeled hops now 2.1 ADA; routing address 1.93B; 200M UNSPENT 452M ADA
- [ ] Identify 14th staging wallet — trace `0c028480d2eb68dc...` to its source stake address (it reached aggregator via ab9f763a→66db994d chain)
- [ ] Get dossier on `stake1u8rmlr2h99gnvdaagycv97p96mclctn2y6sknryy37m0wtspfnsht` — identify exchange from OSINT or blockchain analytics (40B ADA flow, epochs 237–414)

**Pending DB fix** (client IP ${DB_HOST} must be added to pg_hba.conf):
```bash
export PGPASSWORD=REDACTED_DB_PASSWORD
psql -h ${DB_HOST} -p 5432 -U codex_audit -d cexplorer_replica \
  --no-psqlrc -A -F',' --pset=footer=off \
  -f queries/stake1uxztgcgh_dossier.sql > outputs/cross_entity_evidence/stake1uxztgcgh_dossier_2026-04-10.csv
psql -h ${DB_HOST} -p 5432 -U codex_audit -d cexplorer_replica \
  --no-psqlrc -A -F',' --pset=footer=off \
  -f queries/disbursement_recipients_attribution.sql > outputs/cross_entity_evidence/disbursement_recipients_attribution_2026-04-10.csv
```

---

## Secondary Steps

### 5. Re-Run Pool Overlap With Genesis Filter
The corrected chain-wide baseline is now:

- `IOG+EMURGO`: **137**
- `IOG+CF`: **126**
- `EMURGO+CF`: **65**
- `IOG+EMURGO+CF`: **2**

The remaining task is to make that screen **genesis-constrained**. Add `WHERE stake_address IN (SELECT stake_address FROM delegation_history trace exports)` or equivalent founder-trace gating to get the genesis-specific overlap count.

### 6. Identify the 558B ADA Mystery Address
`addr1q9ukkxqf7cwdfgzshltrrmqj0skmv0s8f7s22cvysucug8jgfzwl8zg88xl6z4e6q0sdgeqrhgqq8aa3zj2nuqqvntcs6utve7`
- Compare against known Huobi and OKX ADA deposit addresses
- Its bidirectional relationship with Hub 3 (`Ae2tdPwUPEZ5faoe...`) confirms same operator
- Activated epoch 209 (Shelley HF), drained epoch 374 (Nov 2022)

### 7. Extend EMURGO_2 Trace Hub Classification
Run hub-classification pass on `emurgo2/` trace specifically. Check if `emurgo2/deoverlap_analysis.csv` reveals any addresses exclusive to EMURGO_2 that don't appear in the main EMURGO trace — those would be the most diagnostic.

### 8. Investigate the 100 × 1 ADA Genesis Dust Addresses
100 genesis addresses received exactly 1 ADA each. Determine if they are spent, to whom, and whether they cluster to a single entity. Could be a signing/activation mechanism.

---

## Evidence Bundle for Public Release

When ready to publish, prepare per-finding bundles:

| Finding | Evidence Files | Status |
|---------|---------------|--------|
| 781M entry converged with EMURGO | `emurgo2/trace_summary.json`, `emurgo2/deoverlap_analysis.csv`, `observations/emurgo2_disclosure_search_2026-04-08.md`, `observations/emurgo2_classification_2026-04-08.md`, `observations/emurgo_corporate_chronology_conflict_2026-04-08.md`, `observations/genesis_sale_audit_material_gap_2026-04-08.md` | Ready to publish with chronology caveat and missing-document caveat narrowed to underlying reports |
| IOG+EMURGO first merge | `cross_seed_consuming_transactions_2026-04-06.csv`, `first_merge_validation_2026-04-06.md` | Ready |
| Clean 3-way merge (epoch 250) | `first_merge_validation_2026-04-06.md`, `cross_entity_summary_amended_2026-04-06.md` | Ready |
| 58-output splitter | `cross_entity_summary_amended_2026-04-06.md` Finding 2, on-chain query | Ready |
| Synchronized delegation swarm | `genesis_fee_extraction_report.md`, `cross_entity_epoch_245_251_analysis.md` | Ready |
| Exchange liquidation | `genesis_exchange_liquidation_report.md` | Ready — needs named-exchange IDs |
| Hub 1 still active | On-chain query needed at time of publication | Query before publishing |

---

## Null Hypothesis Checklist (Must Address Before Publishing)
Before any public release, these alternatives must be addressed:

- [ ] **Shared exchange**: All merges could reflect exchange infrastructure (users of the same CEX whose deposits were processed together). Strongest alternative for later merges.
- [ ] **Shared custody**: IOHK, Emurgo, and CF may have used the same custodian (e.g., BitGo), whose internal systems co-mingled funds.
- [x] **781M amount publicly visible**: Official sale stats and genesis files exposed the amount pre-launch; the unresolved question is entity attribution, not amount visibility.
- [ ] **781M entry not a founder allocation**: Treat the entry as a sale-ticket-sized genesis output unless new source material directly ties it to a founder/TBDP line item.
- [ ] **Delegation automation**: The epoch 245–251 swarm could reflect Daedalus wallet auto-delegation behavior triggered by the same software update across all users.

---

## Key Reference Data

| Entity | Genesis TX | ADA | % of Genesis |
|--------|-----------|-----|-------------|
| IOG | `fa2d2a70...` | 2,463,071,701 | 7.92% |
| EMURGO | `242608fc...` | 2,074,165,643 | 6.67% |
| **781M entry** | **`5ec95a53...`** | **781,381,495** | **2.51%** |
| CF | `208c7d54...` | 648,176,763 | 2.08% |
| **NAMED FOUNDERS TOTAL** | | **5,185,414,107** | **~16.67%** |
| Genesis supply | | 31,112,484,745 | 100% |
| Total ADA supply | | 45,000,000,000 | — |

| Key Merge | TX | Epoch | Date |
|-----------|---|-------|------|
| IOG+EMURGO first clean | `a71578ec...` | 95 | 2019-01-15 |
| IOG+CF first clean | `f9951db3...` | 193 | 2020-05-18 |
| EMURGO+CF first clean | `11c0765f...` | 195 | 2020-05-27 |
| All-three first lineage | `197f9d27...` | 196 | 2020-06-02 |
| **All-three CLEAN** | **`571f776c...`** | **250** | **2021-02-25** |

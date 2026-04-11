# Cardano Genesis ADA — New Findings Addendum
**Date:** 2026-04-08  
**Supersedes:** nothing — addendum to `outputs/FULL_FINDINGS_2026-04-06.md`  
**New findings from local CSV analysis and db-sync validation**

---

## Summary of New Findings Today

| # | Finding | Grade | Source |
|---|---------|-------|--------|
| A1 | EMURGO_2 frontier is identical to EMURGO — same 49,089 UTxOs | FACT | Local CSV |
| A2 | EMURGO_2 merged with EMURGO at hop 1, epoch 4 (~Nov 2017) | FACT | Local CSV |
| A3 | Convergence tx `c8596b9c...` combines EMURGO_2 hop-1 with EMURGO hop-3 | FACT | Local CSV |
| A4 | 30 clean IOG+EMURGO merges at epoch 250 alone — coordinated batch | FACT | Local CSV |
| A5 | 22 three-way stake credentials, all also present in EMURGO_2 | FACT | Local CSV |
| A6 | `stake1uxttvx739...` is the primary beneficiary of both three-way merges | FACT | Local CSV |
| A7 | 1.376B ADA UTxO (tx_out_id 6310510) shared across EMURGO+CF+EMURGO_2 | FACT | Local CSV |
| A8 | IOG+EMURGO clean merges continue through epoch 390 (April 2022) | FACT | Local CSV |
| A9 | Clean three-way path includes a 381-UTxO bridge accumulator with 30 single-seed founder-tagged creator txs | FACT | db-sync + Local CSV |
| A10 | 2B clean CF+EMURGO merge `f907b625...` enters a structured 150M peel chain | FACT | db-sync |
| A11 | Corrected named-pool overlap baseline is 137 IOG+EMURGO, 126 IOG+CF, 65 EMURGO+CF, and 2 all-three addresses | FACT | db-sync |

---

## A1. EMURGO_2 Frontier Is Identical To EMURGO

**Grade: FACT**

The published `current_unspent.csv` files for EMURGO and EMURGO_2 contain exactly the same set of `dest_tx_out_id` values:

| Metric | Value |
|:---|---:|
| EMURGO frontier size | 49,089 UTxOs |
| EMURGO_2 frontier size | 49,089 UTxOs |
| Overlap | 49,089 (100%) |
| `EMURGO_2 == EMURGO` | **True** |
| Deoverlap EMURGO_ONLY | 0 |
| Deoverlap EMURGO_2_ONLY | 0 |
| BOTH_EMURGO_SEEDS | 6,216 (100% of stake credentials) |
| Combined deoverlap ADA (each) | 3,160,768,079.24 ADA |

The total counted ADA (3.16B) exceeds the combined genesis allocation (2.854B) because staking rewards and the trace includes UTxOs beyond just the genesis principal.

EMURGO_2 trace edges overlap with EMURGO edges from the very first shared destination: 62,506 shared `dest_tx_out_id`s in trace edges, out of 62,510 in EMURGO and 62,506 in EMURGO_2. The two traces are functionally the same dataset.

---

## A2. EMURGO_2 Merged With EMURGO At Hop 1 — Epoch 4

**Grade: FACT**

The EMURGO_2 trace shows a single hop-1 edge:

| Field | Value |
|:---|:---|
| Source (EMURGO_2 anchor redemption address) | `DdzFFzCqrhspiThx6UaeJASmHTbwbXp2FtdCkF9AU9QXPF9D8sUC7Fqrv9bmYkxradBbqMrSxukTTsqCPNPwRh5PHazdiwWTuJYVMMaf` |
| Hop-1 destination tx | `c8596b9cd81f734f8129604ff86f23bd4a910465acb84ad9e9d1ac223ccb4a76` |
| Epoch | **4** |
| Time | **2017-10-18 05:15:51+00** |
| dest_tx_out_id | **51967** |
| Destination address | `DdzFFzCqrhsu3iF6JfUTaapdWq2mXVRFukkS28WFYVDEqkgaaYttH8cT32credS99L5GaoUsEquqEPNH7ae88eKuDL6XsK5ZL56jkfLi` |
| Value | 1,855,547,037,478,660 lovelace (**1,855,547,037 ADA**) |

This same `dest_tx_out_id=51967` also appears in the EMURGO trace at **hop 3**, from source address `DdzFFzCqrht6ppB1sTzhf1dR76ex9YkTyfcWSK5Jr1XCmoTEQjXbGGGaBq47...`. The merge is not just "same destination later"; `c8596b9c...` directly co-spends:

- the `781M` redemption output from `5ec95a53...`
- an EMURGO-derived output (`tx_out_id=51962`) created 100 seconds earlier by `743fd051...`

**Context:** EMURGO was redeemed at `2017-09-28 10:04:11+00`. EMURGO_2 was redeemed at `2017-09-28 10:09:11+00` — **5 minutes later**. Both outputs then sat dormant for about `475.1` hours before being activated on **2017-10-18**, with the `781M` line entering a direct EMURGO co-spend in its first downstream transaction.

---

## A3. Convergence Transaction `c8596b9c...`

**Grade: FACT**

Full hash: `c8596b9cd81f734f8129604ff86f23bd4a910465acb84ad9e9d1ac223ccb4a76`

This transaction at epoch 4 is simultaneously:
- The **first downstream spend** of the EMURGO_2 allocation (EMURGO_2 hop 1)
- A **third-hop transaction** in the EMURGO trace (EMURGO hop 3)

Its two inputs are:

- `5ec95a53...#0` = `781,381,495 ADA`
- `743fd051...#0` = `1,074,165,542.657684 ADA`

And `743fd051...#0` is itself a direct descendant of the EMURGO redemption:

- `242608fc...` -> `7eb47f8f...#0` -> `743fd051...#0` -> `c8596b9c...`

It then creates a single material output of **~1.856B ADA** at `DdzFFzCqrhsu3iF6JfUTaapdWq2mXVRFukkS28WFYVDEqkgaaYttH8cT32credS99L5GaoUsEquqEPNH7ae88eKuDL6XsK5ZL56jkfLi`, plus a dust output.

From this point forward, the two allocations are operationally identical in the trace data.

**Note on the EMURGO_2 note in `load_investigation_findings.sql`:** the investigation file states: *"Exact amount was public in sale/genesis data pre-launch and matches the published maximum single ticket amount."* The current best classification is a sale-ticket-sized genesis entry redeemed 5 minutes after EMURGO and immediately merged with the same operational infrastructure. Whether this represents an additional undisclosed founder allocation or a large buyer's redemption remains an open question. The chain evidence shows same-operator behavior; the beneficial ownership at genesis is unresolved.

---

## A4. 30 Clean IOG+EMURGO Merges At Epoch 250 — Same Window As Clean Three-Way

**Grade: FACT**

The annotated cross-seed consuming transaction file shows the epoch distribution of clean IOG+EMURGO merges:

| Epoch range | Clean IOG+EMURGO merges |
|:---|---:|
| Epoch 95 (Jan 2019) | 1 (first) |
| Epochs 125–220 | 11 |
| Epochs 244–249 | 14 |
| **Epoch 250** | **30** |
| Epoch 251 | 35 |
| Epoch 252 | 18 |
| Epochs 253–270 | 75 |
| Epochs 283–390 | 7 (latest at epoch 390) |

**205 total clean IOG+EMURGO merges.** 

The epoch 250–252 window accounts for **83 of 205** (40%) clean IOG+EMURGO merges. This is the same window as:
- The clean three-way merge (`571f776c`, epoch 250)
- The 58-output automated splitter's peak activity (epochs 202–299)
- The synchronized delegation swarm peak (epochs 245–251)

The concentration of 30 clean IOG+EMURGO merges in a single epoch, coinciding with the clean three-way merge, is consistent with a coordinated large-scale batch operation.

Latest clean IOG+EMURGO merge: **epoch 390 (April 2022)** — cross-entity flows continued for more than a year after the clean three-way merge.

---

## A5. Twenty-Two Three-Way Stake Credentials — All Also In EMURGO_2

**Grade: FACT**

22 stake credentials appear in the current frontier of all three published seed traces (IOG, EMURGO, CF). All 22 are also present in the EMURGO_2 frontier.

Key entries:

| Stake credential | IOG ADA | EMURGO ADA | CF ADA | Notable |
|:---|---:|---:|---:|:---|
| `stake1uxttvx739...` | 216,818,979 | 134,100,674 | 167,075,537 | **Primary beneficiary** of both three-way merge outputs |
| `stake1uxztgcgh...` | 10,715,097 | 18,577,048 | 11,379,155 | Secondary beneficiary of three-way merge outputs |
| `stake1u9wxw9y5...` | 15,248,553 | 5,199,895 | 850,000 | High IOG allocation |
| `stake1u833p40y...` | 2,113,083 | 132,181 | 89,930 | **Still active epoch 591 (2025)** |
| `stake1u8dg8spc...` | 2,794,252 | 1,646,033 | 97,045 | **Still active epoch 581 (2025)** |
| `stake1ux3a593q...` | 2,252,474 | 2,326,931 | 3,138,113 | 205+176+148 UTxOs — likely exchange deposit |

The two still-active addresses (epochs 581, 591) indicate entities that received genesis-traced ADA and remain active on-chain as of 2025. These are high-priority follow-up targets.

---

## A6. `stake1uxttvx739...` — Primary Beneficiary Of Both Three-Way Merges

**Grade: FACT**

This stake credential is the single most important address in the three-way convergence evidence.

| Metric | Value |
|:---|:---|
| IOG trace: UTxOs | 24, totaling **216,818,979 ADA** |
| EMURGO trace: UTxOs | 17, totaling **134,100,674 ADA** |
| CF trace: UTxOs | 7, totaling **167,075,537 ADA** |
| EMURGO_2 trace | Present (same as EMURGO) |
| **Directly receives output 10748946** | 50,000,000 ADA from clean three-way merge `571f776c` (epoch 250) |
| **Directly receives output 7835688** | 50,000,000 ADA from intermediate three-way merge `34147ef4` (epoch 239) |
| Bech32 payment address (from 571f776c output) | `addr1qxtrqdumg8dleqcra3myptlq6n43m8s0mver0pwgqrr8awvkkcdaz26hglgm4qvc6fdy0rr4ck6q5q249drqc4fzyrgq68vuva` |
| Latest attributed epoch | 406 |

This address is a direct on-chain beneficiary of the clean three-way merge. It does not matter whether the merge was executed by founders, an exchange, or a custodian — `stake1uxttvx739...` is the entity that received the merged output.

---

## A7. 1.376B ADA UTxO Shared Across EMURGO + CF + EMURGO_2

**Grade: FACT**

`dest_tx_out_id=6310510` appears in the current frontier of EMURGO, CF, and EMURGO_2. It is a single UTxO created at epoch 212 worth **1,375,877,556,825,443 lovelace (~1,375,877,557 ADA)**.

The same stake key (`stake1ux5tpajlpe25jwazt5aypj37xn9qqfp59tffmj9pjaq2q2qww0acs`) also holds a second UTxO in the CF trace (6272746, ~374,868 ADA), for a combined CF-attributed total of **~1,376,252,425 ADA** under this single stake credential.

This is the largest single stake key in the cross-entity overlap set and is not shared with the IOG trace. It is an entity that received EMURGO-descended and CF-descended funds but not IOG-descended funds at the current frontier.

---

## A8. IOG+EMURGO Clean Merges Continue Through Epoch 390

**Grade: FACT**

The 205 clean IOG+EMURGO merges span from epoch 95 (January 2019) to epoch 390 (April 2022). The latest clean merge at epoch 390 is more than three years after the first merge and a full year after the clean three-way merge.

This means cross-entity fund flows in the trace data were not a one-time event but a sustained operational pattern across more than three years.

---

## A9. Clean Three-Way Merge Was Preceded By A 381-UTxO Bridge Accumulator

**Grade: FACT**

The clean three-way merge `571f776c...` did not arise from a small number of already-mixed creator transactions. Live db-sync plus local feeder-tagging shows:

| Metric | Value |
|:---|---:|
| Bridge address consumed by `571f776c...` | `Ae2tdPwUPEZHiXixpj6Xdju5jti25cY7QhjHZ3WiZypCsfEJoJx5fGujAKn` |
| Bridge UTxOs consumed | **381** |
| Distinct bridge creator transactions | **381** |
| Total bridge value consumed | **48,718,538.910083 ADA** |
| Founder-tagged feeder rows | **59** |
| Distinct founder-tagged creator txs | **30** |
| Tagged creator composition | **24 IOG, 3 EMURGO, 3 CF, 0 mixed-seed** |

Directly tagged bridge value:

| Seed | ADA created into bridge |
|:---|---:|
| IOG | 7,891,768.743028 |
| EMURGO | 936,750.999248 |
| CF | 62,916.794297 |
| **Total tagged** | **8,891,436.536573** |
| **Untagged remainder** | **39,827,102.373510** |

This sharpens the provenance story. The directly attributable creator transactions are all single-seed. Cross-seed co-mingling therefore occurs at or after the bridge accumulation stage, not inside the directly tagged creators themselves.

The untagged side now has a stronger intermediate classification as well. Clustering the `351` all-none creator txs by feeder address shows:

- `Ae2tdPwUPEZJCGu...` feeds **48** untagged creators totaling **20,392,710.427112 ADA**
- `Ae2tdPwUPEZ3144...` feeds **20** untagged creators totaling **3,316,510 ADA**

Those counts overlap heavily: **19** creator txs use both addresses. On a creator-union basis, the two addresses participate in **49 / 351** distinct untagged creator txs whose combined bridge output totals **24,908,249.390956 ADA**, or about **62.54%** of the untagged bridge value. Both are already labeled **`VERY_LIKELY_EXCHANGE / EXCHANGE`** in the local exchange-analysis corpus, with `Ae2tdPwUPEZJCGu...` appearing under both IOG and EMURGO.

Using the broader local exchange-analysis screen, **21** exchange-like feeder addresses appear across the untagged bridge creator set. Their creator union covers **64 / 351** untagged creator txs and **31,258,037.496911 ADA** of bridge output, or about **78.48%** of the untagged bridge value. The residual outside that weak exchange-like screen is **8,569,064.876599 ADA**.

That residual is itself split, not homogeneous:

- **210** single-feeder creators totaling **3,002,202.484344 ADA**
- **59** `2-6` feeder creators totaling **2,145,630.622907 ADA**
- **6** `8-13` feeder creators totaling **364,576.426584 ADA**
- **12** late `33-78` feeder creators totaling **3,056,655.342764 ADA**

The single-feeder side is not just a weak exchange-label spillover. Those **210** creators map to **209** unique feeder addresses, and **0 / 209** appear anywhere in the local exchange-analysis corpus. The top **10** single-feeder creators account for about **65.63%** of single-feeder bridge value, and the top **20** account for about **77.79%**.

The 12 large residual creators now have a stronger internal profile:

- **917** feeder rows across **12** creators
- **11 / 12** creators use an exact **80-input** shape; the remaining creator has **37** inputs
- all 12 are **single-output** creators with narrow fees of **1.055781-2.213181 ADA**
- **882** distinct feeder source transactions feed the cluster, and **0** source transaction hashes are shared across different creators
- address overlap is still weak: **810 / 832** feeder addresses appear in only one creator, **21** appear in two creators, and only **1** appears in three creators
- **867 / 917** feeder inputs are under **10k ADA**, but those sub-`10k` inputs contribute only about **33.97%** of cluster input value; the remaining **50** larger inputs contribute about **66.03%**
- exact denomination recurrence is visible across creators (`10`, `100`, `1,000`, and `5,000 ADA` all recur in **7-8** creators), even though the feeder addresses themselves mostly do not

That profile is more consistent with a standardized late consolidation batcher sweeping heterogeneous smaller Byron balances plus a few larger anchors than with a final hidden dominant wallet cluster feeding every creator.

Four bridge-spend transactions route **43,947,612.106576 ADA** into `addr1q84qw26450...` / `stake1uxztgcgh...`, and all four of those outputs are later spent in intermediate three-way merge `34147ef4...` before the clean three-way merge at epoch 250.

---

## A10. A 2B Clean CF+EMURGO Merge Enters A Structured Peel Chain

**Grade: FACT**

`f907b62584ca76c533f410867bf964c527b2a8251849d93c2b48a5b69e641816` is one of the largest clean pairwise merges in the dataset:

| Metric | Value |
|:---|:---|
| Epoch | 226 |
| Time | 2020-10-29 15:13:57 UTC |
| Inputs | 53 |
| Outputs | 1 |
| Total output | **1,999,999,999.820448 ADA** |
| Classification | **clean CF+EMURGO merge** |

Its single 2B output is first spent by `48bb2ca...`, which immediately splits it into:

- **200,000,000 ADA** to `stake1uxexwrph9r2...` (still unspent in the db-sync snapshot used here)
- **1,799,999,999.640 ADA** to `stake1u9zjr6e37w...`

After that first split, the carry output stays under the same stake credential for multiple hops while repeated side outputs of about **150,000,005 ADA** are peeled off to fresh stake credentials. Verified side recipients include:

- `stake1u84jrq070...`
- `stake1ux0xnj5lj...`
- `stake1uxz3a23cm...`
- `stake1uxtj8luzp...`
- `stake1uytfgj3wq...`
- `stake1u8mf4hrhd...`
- `stake1uxdpsgk3x...`
- `stake1uxl72wy87...`

This is a structured treasury/custody-style peel chain, not a random dissipation pattern.

Important constraint: these peel recipients and the carry stake credentials produced **0 hits** in the current founder frontier exports for IOG, EMURGO, CF, and EMURGO_2. That does not prove non-founder control, but it does mean the peel recipients are not simply persisting as obvious current-frontier founder outputs.

Later stake profiling further sharpens the interpretation:

- the main carry stake `stake1u9zjr6e37w...` has received **30.67B ADA** in total and still holds **1.93B ADA** unspent
- the 200M branch stake `stake1uxexwrph9r2...` has since accumulated **452.30M ADA** total and still holds that amount unspent
- the 200M branch is later re-funded by two epoch-391 transactions, `1daba627...` and `531150c...`, whose inputs are **exclusively** from **Hub 1** and whose paired outputs go to both `stake1uxexwrph9r2...` and `stake1u9zjr6e37w...`
- the repeated 150M side-recipient stakes mostly accumulated about **450.5M ADA** each and are now reduced to dust or zero
- sampled later large transactions on multiple 150M side-recipient stakes are single-input same-stake respends, making the 200M branch operationally distinct from the rest of the peeled branches checked here
- a later carry stake in the same lineage, `stake1u8rmlr2h99gn...`, has received **40.05B ADA** total and has a recorded delegation to pool ticker **`BNP`** with pool name **`Binance Staking - 43`**
- the main carry stake `stake1u9zjr6e37w...` is also already labeled **`LIKELY_EXCHANGE / EXCHANGE`** in the local EMURGO exchange-analysis export, with matching EMURGO and EMURGO_2 trace-edge rows showing it sourced from Hub 1 at epoch 211

That Binance-staking signal does **not** prove Binance controlled the lineage at the original clean merge point. It does, however, materially strengthen the exchange/custody explanation for the later downstream chain, and the 200M branch now also links directly into that same Hub-1-fed operational cluster.

---

## A11. Corrected Named-Pool Overlap Baseline

**Grade: FACT**

The original pool-overlap runner undercounted EMURGO because it matched only `ticker_name ILIKE 'EMURGO%%'`. Live db-sync re-checking with expanded EMURGO pool scope (`EMUR*`, `EMG*`, and pool names beginning with `Emurgo`) yields the corrected chain-wide baseline:

| Overlap class | Delegator count |
|:---|---:|
| IOG + EMURGO named pools | **137** |
| IOG + CF named pools | **126** |
| EMURGO + CF named pools | **65** |
| All three named-pool sets | **2** |

The two chain-wide all-three addresses are:

- `stake1u8stds2advjjwuxypcl7qkeg33ru9muvdlgzt296sg06zjclkd7vt`
- `stake1u9t4q48qsjy4mnnd80pe5pexy3m2vwjr7px3rccew7ffgksf86npr`

This is still a chain-wide screen, not a genesis-constrained one, so it is best treated as a corrected baseline for follow-up rather than a publication-ready genesis-specific count.

---

## Db-Sync Status Note

db-sync access was restored on 2026-04-08 and the EMURGO_2 classification queries were re-run live against `cexplorer_replica`.

The remaining shell runners in `scripts/` are still useful for batch regeneration, but they are no longer blocked as an investigation prerequisite.

---

## New Artifacts Created Today

| File | Contents |
|:---|:---|
| `outputs/cross_entity_evidence/emurgo2_convergence_evidence_2026-04-08.md` | Full EMURGO_2 convergence analysis |
| `observations/emurgo2_classification_2026-04-08.md` | Sale-ticket classification plus direct merge mechanics |
| `outputs/cross_entity_evidence/merge_timeline_2026-04-08.md` | Chronological merge event timeline |
| `outputs/cross_entity_evidence/cross_seed_consuming_transactions_annotated_2026-04-08.csv` | 521 cross-seed txs with correct clean_merge flags |
| `outputs/cross_entity_evidence/emurgo2_frontier_overlap_2026-04-08.csv` | Pairwise overlap counts including EMURGO_2 |
| `outputs/cross_entity_evidence/iog_emurgo2_shared_consuming_txs_2026-04-08.csv` | 219 IOG+EMURGO_2 shared consuming txs |
| `outputs/cross_entity_evidence/all_three_stake_credential_detail_2026-04-08.csv` | 22 three-way stake credentials with per-entity ADA |
| `observations/bridge_path_to_three_way_merge_2026-04-08.md` | Bridge accumulator analysis behind `571f776c...` |
| `outputs/cross_entity_evidence/bridge_untagged_creator_address_clusters_2026-04-08.csv` | Address-cluster summary for the all-none bridge creator feeders |
| `outputs/cross_entity_evidence/bridge_untagged_creator_top_exchange_union_2026-04-08.csv` | The 49-creator top-exchange-cluster union behind the untagged bridge remainder |
| `outputs/cross_entity_evidence/bridge_untagged_creator_exchange_like_union_2026-04-08.csv` | The 64-creator union covered by the broader exchange-like bridge feeder screen |
| `outputs/cross_entity_evidence/bridge_untagged_residual_creators_2026-04-08.csv` | All-none residual bridge creators outside the current exchange-like screen |
| `outputs/cross_entity_evidence/bridge_untagged_residual_large_batch_cluster_2026-04-08.csv` | The 12 late large multi-feeder residual bridge creators |
| `outputs/cross_entity_evidence/bridge_residual_large_batch_patterns_2026-04-08.csv` | Per-creator concentration, fee, and denomination profile for the 12 late residual batch creators |
| `outputs/cross_entity_evidence/bridge_residual_large_batch_shared_addresses_2026-04-08.csv` | Feeder addresses reused across the 12 late residual batch creators |
| `outputs/cross_entity_evidence/bridge_residual_large_batch_recurring_values_2026-04-08.csv` | Exact feeder ADA values recurring across the 12 late residual batch creators |
| `outputs/cross_entity_evidence/bridge_residual_single_feeder_top20_2026-04-08.csv` | Top 20 one-input residual bridge creators outside the exchange-like screen |
| `outputs/cross_entity_evidence/bridge_residual_single_feeder_corpus_status_2026-04-08.csv` | Exchange-corpus hit status for all 210 one-input residual bridge creators |
| `observations/f907b625_cf_emurgo_peel_chain_2026-04-08.md` | Structured downstream peel chain from 2B CF+EMURGO merge |
| `outputs/cross_entity_evidence/f907_200m_branch_refunding_outputs_2026-04-08.csv` | Epoch-391 paired top-up outputs for the 200M branch and main carry stake |
| `outputs/cross_entity_evidence/f907_200m_branch_refunding_input_sources_2026-04-08.csv` | Exclusive Hub 1 input sourcing for the epoch-391 200M-branch top-ups |
| `outputs/cross_entity_evidence/f907_side_branch_large_outputs_2026-04-08.csv` | Large-output history for the 200M and 150M peeled side branches |
| `outputs/cross_entity_evidence/pool_overlap_chain_wide_2026-04-08.csv` | Corrected chain-wide named-pool overlap counts |
| `outputs/cross_entity_evidence/pool_overlap_all_three_chain_wide_addresses_2026-04-08.csv` | Two chain-wide all-three named-pool addresses |
| `outputs/cross_entity_evidence/named_pool_ticker_list_2026-04-08.csv` | Corrected named-pool roster including EMURGO pools |
| `queries/bridge_input_creator_table_step1.sql` | SQL for 381 bridge input creator analysis |
| `queries/emurgo2_direct_merge_checks.sql` | Reproducible SQL for the direct EMURGO/781M merge proof |
| `queries/f907b625_peel_chain_checks.sql` | Reproducible SQL for the 2B CF+EMURGO peel chain |
| `scripts/run_bridge_creator_step1.sh` | Runner for Step 1 |
| `scripts/run_step3_splitter_bridge_expansion.sh` | Runner for Step 3 |
| `scripts/run_step4_first_merge_backtrace.sh` | Runner for Step 4 |
| `scripts/run_step5_triply_shared_dossiers.sh` | Runner for Step 5 |
| `scripts/run_step6_genesis_pool_overlap.sh` | Runner for Step 6 |
| `scripts/run_emurgo2_analysis.sh` | Runner for EMURGO_2 db-sync analysis |
| `scripts/tag_creator_feeders_with_seed_traces.py` | Python: seed-trace tagging of bridge feeder inputs |
| `scripts/summarize_bridge_untagged_creators.py` | Python: cluster summary for the all-none bridge creator feeder addresses |
| `scripts/analyze_bridge_residual_large_batches.py` | Python: pattern profiler for the 12 late residual batch creators |

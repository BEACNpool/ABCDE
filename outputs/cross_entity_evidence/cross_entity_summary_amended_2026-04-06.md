# Cardano Genesis Cross-Entity Evidence
## Amended Draft: What The ABCDE Exports Prove, Suggest, And Still Need

**Amendment date:** 2026-04-06  
**Supersedes:** `outputs/cross_entity_evidence/cross_entity_summary.md` dated 2026-04-03  
**Dataset basis:** ABCDE exports derived from Cardano db-sync at block 13,215,210+  
**Purpose:** tighten claim strength, correct scope issues, add stronger convergence evidence, and recommend next investigative steps  
**Supplemental live-db validation:** `outputs/cross_entity_evidence/first_merge_validation_2026-04-06.md`  
**Full direct-merge scan:** `outputs/cross_entity_evidence/cross_seed_merge_summary_2026-04-06.md`  
**Hub classification appendix:** `outputs/cross_entity_evidence/hub_classification_appendix_2026-04-06.md`  
**Route-chain artifacts:** `outputs/cross_entity_evidence/sink_to_splitter_transactions_2026-04-06.csv`, `outputs/cross_entity_evidence/splitter_to_bridge_forward_trace_2026-04-06.csv`, `outputs/cross_entity_evidence/clean_three_way_direct_input_breakdown_2026-04-06.csv`, `outputs/cross_entity_evidence/focal_source_outputs_in_571f_2026-04-06.csv`, `outputs/cross_entity_evidence/bridge_inputs_value_distribution_2026-04-06.csv`

---

## Executive Summary

- **FACT:** founder-allocation traces do converge into identical downstream UTxOs. The published frontier exports share `1,996` exact `dest_tx_out_id`s between IOG and EMURGO, `711` between EMURGO and CF, `263` between IOG and CF, and `7` across all three.
- **FACT:** grouping the published trace-edge files by consuming transaction yields `521` direct cross-seed consuming transactions: `216` IOG+EMURGO, `49` IOG+CF, `253` EMURGO+CF, and `3` three-way.
- **FACT:** the earliest clean direct pairwise merge is IOG+EMURGO transaction `a71578ec...` at epoch `95` on `2019-01-15 21:50:51+00`, well before the earliest clean CF-involving merges in May 2020.
- **FACT:** only `1` of the `3` direct three-way transactions is a clean three-way merge with exclusive direct inputs from all three founder branches: epoch-250 transaction `571f776c...`.
- **FACT:** live db-sync validation confirms exemplar consuming transactions behind the three-way overlap set, including epoch-250 transaction `571f776c...` which directly consumes focal source UTxOs traced from IOG, EMURGO, and CF in the published exports.
- **FACT:** the Byron address `Ae2tdPwUPEZ6xYrxCgRDM2NQFM5oajHEoJN3i9ZVV2AbsbvxoJBjVu3yP7W` is a real shared hub in both IOG and EMURGO trace exports and repeatedly executes 58-output distributions.
- **FACT:** live db-sync validation now confirms a concrete route chain: `DdzFFzCqrhstmqBkaU98vdHu6PdqjqotmgudToWYEeRmQKDrn4cAgGv9EZKtu1DevLrMA1pdVazufUCK4zhFkUcQZ5Gm88mVHnrwmXvT` paid `Ae2tdPwUPEZ6xYrxCgRDM2NQFM5oajHEoJN3i9ZVV2AbsbvxoJBjVu3yP7W` in `41` transactions totaling `78,000,020 ADA`, and `Ae2tdPwUPEZ6xYrxCgRDM2NQFM5oajHEoJN3i9ZVV2AbsbvxoJBjVu3yP7W` paid `Ae2tdPwUPEZHiXixpj6Xdju5jti25cY7QhjHZ3WiZypCsfEJoJx5fGujAKn` in `4` transactions totaling `50,000,000 ADA`.
- **FACT:** clean three-way merge transaction `571f776c0698c576ddecae145f97e7f284b82ebea70fbc924fa4e2a4a6258020` takes `381` direct inputs from `Ae2tdPwUPEZHiXixpj6Xdju5jti25cY7QhjHZ3WiZypCsfEJoJx5fGujAKn`, totaling `48,718,538.910083 ADA`.
- **STRONG INFERENCE:** the recurring Byron infrastructure is not one homogeneous wallet. The current best classification is a shared sink/routing hub (`DdzFFzCqrhstmqBkaU98vdHu6PdqjqotmgudToWYEeRmQKDrn4cAgGv9EZKtu1DevLrMA1pdVazufUCK4zhFkUcQZ5Gm88mVHnrwmXvT`), an automated splitter (`Ae2tdPwUPEZ6xYrxCgRDM2NQFM5oajHEoJN3i9ZVV2AbsbvxoJBjVu3yP7W`), and a smaller bridge/aggregator (`Ae2tdPwUPEZHiXixpj6Xdju5jti25cY7QhjHZ3WiZypCsfEJoJx5fGujAKn`).
- **FACT:** `423` stake credentials delegated to both named IOG and named EMURGO pool sets. `12` stake credentials delegated to all three named pool sets.
- **IMPORTANT:** the published SQL for the 12-address result is chain-wide. By itself it does **not** prove those 12 addresses are genesis-traced addresses. Treat it as cross-pool behavior evidence unless a genesis filter is added.
- **FACT:** only `7` stake credentials overlap across all three published `delegation_history.csv` exports from the seed traces themselves.
- **STRONG INFERENCE:** common custody, exchange, treasury service, or shared operators likely handled funds descended from more than one founder allocation.
- **IMPORTANT:** many EMURGO+CF direct consuming transactions are inherited-overlap events rather than fresh clean pairwise merges; the clean-vs-overlapping distinction matters when grading the evidence.
- **NOT PROVEN:** intent to hide, fraudulent collusion, or continued joint founder control over the converged outputs.

---

## Claim-Strength Standard

- **FACT** = directly visible in published CSVs or directly reproducible from db-sync
- **STRONG INFERENCE** = the simplest explanation of multiple facts, but not exclusive proof
- **HEURISTIC** = label derived from rules or metadata, not chain-canonical proof of identity or intent

---

## Methodological Corrections From The First Draft

1. **Anchor transaction labeling needed correction.** The first draft described EMURGO and CF using their first downstream spend transaction hashes rather than the original redemption anchor transaction hashes used in the dataset.
2. **The strongest genesis-specific signal is exact downstream UTxO convergence, not the chain-wide pool overlap table.**
3. **The 12 all-three delegates result is not genesis-specific unless the SQL is explicitly constrained to genesis-traced stake credentials.**
4. **Pool ticker naming uses `off_chain_pool_data`.** That is operator-submitted metadata cached by db-sync. It is useful, but it is not chain-canonical identity proof.
5. **Exchange labels in `exchange-analysis/` are heuristic.** They should not be restated as named-exchange fact without separate evidence.

---

## Corrected Anchor Table

The ABCDE trace files use the redemption transaction as the hop-1 source and the first downstream spend transaction as the hop-1 destination.

| Entity | Redemption Anchor TX | First Downstream Spend TX | Note |
|:---|:---|:---|:---|
| IOG | `fa2d2a70c0b5fd45cb6c3989f02813061f9d27f15f30ecddd38780c59f413c62` | `0d94ce298776bd6bf220084d7af093b2d403668a45f55a9c813b2efd0ffd1e10` | First draft already used the correct IOG anchor |
| EMURGO | `242608fc18552a4ac83adabcef7155f3b909e83d469ce89735db8f11d3637e38` | `7eb47f8f9ffaaf98f30d8028c7e1d13a8efeebffb65d1f2d4be37ee523ceb9bf` | The first draft mislabeled the first spend tx as the anchor |
| CF | `208c7d54c1c24059c9314ddbe866edc80adcb8894539b27b6a1430d5c078b998` | `49bef29428b70222f26f33c282209bf17b9e76a6ffa46a21e3925d325381caa7` | The first draft mislabeled the first spend tx as the anchor |

---

## Finding 1: Exact Downstream UTxO Convergence Across Seed Traces

**Grade: FACT**

This is the strongest genesis-specific result in the current exports.

Pairwise overlap in published `current_unspent.csv` frontiers:

| Pair | Shared Exact `dest_tx_out_id` Count |
|:---|---:|
| IOG ∩ EMURGO | 1,996 |
| IOG ∩ CF | 263 |
| EMURGO ∩ CF | 711 |
| IOG ∩ EMURGO ∩ CF | 7 |

The seven exact triply-shared outputs currently visible in all three frontier exports are:

| `dest_tx_out_id` | `dest_tx_hash` | Epoch | Address | Stake Credential | ADA |
|---:|:---|---:|:---|:---|---:|
| 5064341 | `197f9d27e49345cc085c9a2951d96c77f57f1cd82a71c095b7b7a3b36e74855d` | 196 | `DdzFFzCqrht8tJfdsZLWasUaYHyvZBE99fu1nCAFcmnbCT4wvyciMTwUPJNbf17GTCZ3KDnWCzYFku6uWy5pkdimEkpwMH2vab1XEqSH` | | 157.848089 |
| 5064342 | `197f9d27e49345cc085c9a2951d96c77f57f1cd82a71c095b7b7a3b36e74855d` | 196 | `Ae2tdPwUPEZ1xgFDwEF4k8CpVUMULvu3AUTqBLHxb568YsiLmVczvC52C7A` | | 10000 |
| 7835688 | `34147ef46fd105ed39e3be63ac194e79622fb1bf9ea6e50313a0c3e0e6fd20c3` | 239 | `addr1qxtrqdumg8dleqcra3myptlq6n43m8s0mver0pwgqrr8awvkkcdaz26hglgm4qvc6fdy0rr4ck6q5q249drqc4fzyrgq68vuva` | `stake1uxttvx739dt505d6sxvdykj8336utdq2q92jk3sv253zp5qalcz84` | 50000000 |
| 7835689 | `34147ef46fd105ed39e3be63ac194e79622fb1bf9ea6e50313a0c3e0e6fd20c3` | 239 | `addr1qxeh8yl2gp06x7zyqduh26ap7qxzzf8v9mwd4zg0dw703e5yk3s302tp7mt5qt2vhyfuyj0y5h8xkm58qa726gr62jjqsl3gc8` | `stake1uxztgcgh49sld46q94xtjy7zf8j2tnntd6rswl9dypa9ffqqxrz2a` | 8356376.525206 |
| 10748946 | `571f776c0698c576ddecae145f97e7f284b82ebea70fbc924fa4e2a4a6258020` | 250 | `addr1qxtrqdumg8dleqcra3myptlq6n43m8s0mver0pwgqrr8awvkkcdaz26hglgm4qvc6fdy0rr4ck6q5q249drqc4fzyrgq68vuva` | `stake1uxttvx739dt505d6sxvdykj8336utdq2q92jk3sv253zp5qalcz84` | 50000000 |
| 10748947 | `571f776c0698c576ddecae145f97e7f284b82ebea70fbc924fa4e2a4a6258020` | 250 | `addr1qxfxlatvpnl7wywyz6g4vqyfgmf9mdyjsh3hnec0yuvrhk8jh8axm6pzha46j5e7j3a2mjdvnpufphgjawhyh0tg9r3sk85ls4` | `stake1u8etn7ndaq3t76af2vlfg74dexkfs7ysm5fwhtjth45z3ccdme5gq` | 40 |
| 10748948 | `571f776c0698c576ddecae145f97e7f284b82ebea70fbc924fa4e2a4a6258020` | 250 | `addr1q84qw26450qz5raerf6yvupnr8crk3z8cjrhvkmvfw6u95yyk3s302tp7mt5qt2vhyfuyj0y5h8xkm58qa726gr62jjqn9uju3` | `stake1uxztgcgh49sld46q94xtjy7zf8j2tnntd6rswl9dypa9ffqqxrz2a` | 244596.263181 |

**What this proves:** the lineages from separate founder allocations reached the same downstream outputs.

**What this does not prove:** that the founding entities themselves still controlled those outputs at the time of convergence. The merge could have occurred inside exchange, custody, OTC, treasury-management, or other third-party infrastructure.

---

## Finding 2: The Shared Byron Hub `Ae2tdPwUPEZ6xYrxCgRDM2NQFM5oajHEoJN3i9ZVV2AbsbvxoJBjVu3yP7W`

**Grade: FACT (shared presence and activity) | STRONG INFERENCE (shared-operator conclusion)**

Address:

`Ae2tdPwUPEZ6xYrxCgRDM2NQFM5oajHEoJN3i9ZVV2AbsbvxoJBjVu3yP7W`

Published and locally verified facts:

| Metric | Value |
|:---|---:|
| Total spend transactions | 40,876 |
| Active epoch range | 202-299 |
| Transactions with exactly 58 outputs | 1,170 |
| Transactions with 50+ outputs | 1,561 |
| Maximum outputs in a single spend | 58 |
| IOG trace rows where this address is the `source_address` | 2,890 |
| EMURGO trace rows where this address is the `source_address` | 1,688 |

Representative 58-output transactions already published in the evidence pack:

| Epoch | TX Hash | Outputs | ADA |
|---:|:---|---:|---:|
| 248 | `b4e2114645eb655ce5536311399f1714afa16cec9108838b68a97c786819a898` | 58 | 994340 |
| 248 | `cbf1cd35ff81be6bba6ad80fec75a0bbc33c7e0b85c10969f3d760d138fe723f` | 58 | 1592139 |
| 248 | `64a2d660a802a98340f425378ed77d971692a92a5dd2b076cb35c2feac7e0b0e` | 58 | 810521 |
| 248 | `979576998e288e80a9b745d14c988b5b29237ea17764797bf628586921f74814` | 58 | 440737 |
| 248 | `c925e6cb0a81734a1ad46ca7d5249d4731b76511d4df6a226a9ab22874862b95` | 58 | 800389 |

This address is a real shared operational hub across the IOG and EMURGO traces. That materially strengthens the common-infrastructure hypothesis.

Live db-sync route validation adds a stronger point:

- `DdzFFzCqrhstmqBkaU98vdHu6PdqjqotmgudToWYEeRmQKDrn4cAgGv9EZKtu1DevLrMA1pdVazufUCK4zhFkUcQZ5Gm88mVHnrwmXvT` paid `Ae2tdPwUPEZ6xYrxCgRDM2NQFM5oajHEoJN3i9ZVV2AbsbvxoJBjVu3yP7W` in `41` transactions totaling `78,000,020 ADA`, all on `2020-07-03`.
- The value pattern was highly regular: `39` outputs of exactly `2,000,000 ADA` and `2` outputs of exactly `10 ADA`.
- `Ae2tdPwUPEZ6xYrxCgRDM2NQFM5oajHEoJN3i9ZVV2AbsbvxoJBjVu3yP7W` then paid `Ae2tdPwUPEZHiXixpj6Xdju5jti25cY7QhjHZ3WiZypCsfEJoJx5fGujAKn` in `4` transactions totaling `50,000,000 ADA`.
- One of those four verified bridge-funding outputs, `5678309` created by `8d782da14a4b797a753bf276ae0f8f2616f27bb3faed72c741e34c81c13fc7c0`, was later spent in `26174c832f6261944ac9074817b0dbe8ef7f81d55f193723672cfd0065d0bc04`, which sits inside the bridge wallet's downstream path.

The first draft overstated the conclusion. The data supports:

- common downstream handling
- heavy automation
- reuse of the same Byron infrastructure across both traces

The data does **not** by itself identify whether the operator was:

- a founder entity treasury team
- a centralized exchange
- a shared custody provider
- an OTC settlement desk
- another third-party service layer

---

## Finding 3: Delegation Overlap Needs To Be Split Into Two Different Results

### 3A. Chain-Wide Named-Pool Overlap

**Grade: FACT**

This is the result published in the original draft:

- `423` stake credentials delegated to both named IOG and named EMURGO pool sets
- `12` stake credentials delegated to named IOG, named EMURGO, and named CF pool sets

This is real, but the published SQL is chain-wide:

```sql
SELECT sa.view FROM stake_address sa
WHERE sa.id IN (SELECT addr_id FROM delegation WHERE pool_hash_id IN iog_pools)
  AND sa.id IN (SELECT addr_id FROM delegation WHERE pool_hash_id IN emurgo_pools)
  AND sa.id IN (SELECT addr_id FROM delegation WHERE pool_hash_id IN cf_pools);
```

Because this query is not restricted to genesis-traced stake credentials, it should be described as **cross-pool behavior evidence**, not standalone genesis-proof evidence.

### 3B. Genesis-Trace Delegation Overlap

**Grade: FACT**

Using the published seed-specific `delegation_history.csv` exports, the overlap counts are:

| Overlap Type | Count |
|:---|---:|
| IOG ∩ EMURGO | 967 |
| IOG ∩ CF | 53 |
| EMURGO ∩ CF | 77 |
| IOG ∩ EMURGO ∩ CF | 7 |

The 7 stake credentials present in all three published seed-trace delegation exports are:

```text
stake1u85re0n76p05ld36le8ytuuhdst0lu4mmh8g53hmpqd6txsxxta6n
stake1u86jl5trmfr70cjfe6capkl2ptx05l8jflspswgh79el5ygcv8xwh
stake1u87mehxnkc68j98vsmuf6vrrlcfygppyxvkkwm4n89n2jssanukrm
stake1u89zwwc9sntxuh2e7qtjydkfdse9fv8uckzqvcg2xp6yw9gj6yp06
stake1u8etn7ndaq3t76af2vlfg74dexkfs7ysm5fwhtjth45z3ccdme5gq
stake1u907m66smf4lefjzgp7v7zzmjpjeljrvdm5vttv6nulm0asv2de62
stake1uxvvzsuuk8v0r2kksutrwvd2fe0kms3d4qh5a3su5vky53gjx9uqw
```

**Amended interpretation:** the 12-address named-pool result is still useful, but the 7-address full-trace result is the cleaner genesis-linked overlap metric from the published exports.

---

## Finding 4: Twenty-Two Current Stake Credentials Appear In All Three Frontier Exports

**Grade: FACT**

Across the three published `current_unspent.csv` frontiers:

- IOG unique current stake credentials: `11,588`
- EMURGO unique current stake credentials: `6,069`
- CF unique current stake credentials: `2,067`
- Current stake credentials appearing in all three frontier exports: `22`

This is a useful lead set for follow-up, but it must be handled carefully:

- do **not** sum the per-seed ADA columns as if they were independent balances
- some of these overlaps are driven by exact repeated `dest_tx_out_id`s already listed in Finding 1
- once traces converge, the same later UTxO can legitimately appear in more than one seed export

So this result is evidence of downstream co-mingling, not proof of separate founder balances sitting side by side under one stake key.

---

## Finding 5: The CFLOW Concentration Is Real But Weak

**Grade: FACT (descriptive) | WEAK INFERENCE (interpretive)**

Of the 12 chain-wide named-pool all-three addresses in `all_three_entity_addresses.csv`, all 12 CF delegations point to `CFLOW`.

That is noteworthy. It is **not** strong enough on its own to imply insider knowledge or insider status. It can also reflect:

- path dependence
- one pool being more visible or more active during the period sampled
- operator preference unrelated to founder affiliation
- noise from a small sample

This point should remain in the report only as a descriptive pattern, not as a centerpiece claim.

---

## What This Amended Report Supports

- The founder-allocation traces **did** co-mingle downstream.
- At least one heavily automated Byron hub **did** process both IOG-descended and EMURGO-descended funds.
- Cross-pool delegation overlap exists both chain-wide and within the published seed-trace exports.
- The existing evidence justifies a deeper investigation into shared custody, exchange routing, or common treasury operations.

---

## What This Amended Report Does Not Yet Support

- Named-exchange attribution as **FACT** unless backed by independent public labeling or stronger cluster proof
- The claim that all 12 chain-wide all-three delegates are genesis-linked
- The claim that the founder entities themselves retained control after the traces converged
- The claim of deceptive intent or concealment from fragmentation patterns alone

---

## Recommended Next Steps

1. **Start with the bridge-input creator table for transaction `571f776c0698c576ddecae145f97e7f284b82ebea70fbc924fa4e2a4a6258020`.** The highest-value next task is to classify the `381` creator transactions behind the bridge inputs from `Ae2tdPwUPEZHiXixpj6Xdju5jti25cY7QhjHZ3WiZypCsfEJoJx5fGujAKn`. For each creator transaction, capture:
   - creator tx hash
   - creator time
   - input addresses feeding that creator transaction
   - whether those inputs are tagged by the IOG, EMURGO, or CF trace exports
   - whether the creator output is fixed-size, round-number, or bespoke
2. **Trace the full sink -> splitter batch forward.** Use `outputs/cross_entity_evidence/sink_to_splitter_transactions_2026-04-06.csv` to follow all `41` payments from `DdzFFzCqrhstmqBkaU98vdHu6PdqjqotmgudToWYEeRmQKDrn4cAgGv9EZKtu1DevLrMA1pdVazufUCK4zhFkUcQZ5Gm88mVHnrwmXvT` into the first downstream spend path of `Ae2tdPwUPEZ6xYrxCgRDM2NQFM5oajHEoJN3i9ZVV2AbsbvxoJBjVu3yP7W`, and measure how much of that same-day batch eventually enters `Ae2tdPwUPEZHiXixpj6Xdju5jti25cY7QhjHZ3WiZypCsfEJoJx5fGujAKn`.
3. **Expand the verified splitter -> bridge leg into a descendant graph.** Start from the four confirmed transactions already isolated in `outputs/cross_entity_evidence/splitter_to_bridge_forward_trace_2026-04-06.csv`:
   - `a9af4adba1feb3cf84d41c0ed6d8084ae57d0991e14ffcddbd1fa49f6249de7b`
   - `37600a6ffb718e609db73d508c048027ce9f1e0549c65450ab35588da46e6be9`
   - `8d782da14a4b797a753bf276ae0f8f2616f27bb3faed72c741e34c81c13fc7c0`
   - `a20ca4ba7bd46739e8f8ff8c1e94b583cf4751a311fcf9f157318933c522ba3d`
   The goal is to determine which bridge outputs feed the clean three-way merge directly and which peel off into separate infrastructure branches.
4. **Backtrace the first merge point for every shared exact output.** For each of the `1,996`, `711`, `263`, and `7` shared `dest_tx_out_id`s, find the first transaction where separate seed lineages enter the same downstream path. Keep pairwise merges and three-way merges in separate tables.
5. **Build a first-merge dossier for the three triply-shared transactions.** Use full transaction hashes and exact input/output tables for:
   - `197f9d27e49345cc085c9a2951d96c77f57f1cd82a71c095b7b7a3b36e74855d`
   - `34147ef46fd105ed39e3be63ac194e79622fb1bf9ea6e50313a0c3e0e6fd20c3`
   - `571f776c0698c576ddecae145f97e7f284b82ebea70fbc924fa4e2a4a6258020`
   Mark each as clean three-way, inherited overlap, or mixed.
6. **Re-run the 12-address delegation query with an explicit genesis filter.** Restrict to stake credentials present in the seed-trace exports, then publish chain-wide and genesis-constrained counts side by side so the named-pool overlap result cannot be criticized as scope drift.
7. **Publish the exact SQL behind every public CSV that may be challenged.** At minimum, publish the SQL for `all_three_entity_addresses.csv`, the exact-output overlap tables, and the new route-chain artifacts so the reproduction path is explicit.
8. **Separate facts from heuristics in every public-facing summary.** Keep named-exchange attribution, concealment language, and intent language out of FACT findings unless independently proven. The strongest current claims are route-chain convergence and shared operational infrastructure, not final legal ownership.
9. **Add a null-hypothesis section and a hostile-review section.** The null hypotheses are shared exchange infrastructure, shared custody, treasury outsourcing, or a mix of those. The hostile-review section should spell out exactly which claims are proven by chain data and which remain inference.
10. **Correct the anchor/spend distinction everywhere this report is quoted.** EMURGO and CF were mis-described in the first draft, and that error should not be allowed to propagate into external write-ups.

---

## Supporting Files

- `datasets/genesis-founders/iog/current_unspent.csv`
- `datasets/genesis-founders/emurgo/current_unspent.csv`
- `datasets/genesis-founders/cf/current_unspent.csv`
- `datasets/genesis-founders/iog/delegation_history.csv`
- `datasets/genesis-founders/emurgo/delegation_history.csv`
- `datasets/genesis-founders/cf/delegation_history.csv`
- `outputs/cross_entity_evidence/all_three_entity_addresses.csv`
- `outputs/cross_entity_evidence/byron_splitter_evidence.csv`
- `outputs/cross_entity_evidence/sink_to_splitter_transactions_2026-04-06.csv`
- `outputs/cross_entity_evidence/splitter_to_bridge_forward_trace_2026-04-06.csv`
- `outputs/cross_entity_evidence/clean_three_way_direct_input_breakdown_2026-04-06.csv`
- `outputs/cross_entity_evidence/focal_source_outputs_in_571f_2026-04-06.csv`
- `outputs/cross_entity_evidence/bridge_inputs_value_distribution_2026-04-06.csv`

---

*Prepared as a stricter amendment to the 2026-04-03 draft.*
*The goal of this version is not to weaken the investigation. It is to tighten the parts that are real enough to survive hostile review.*

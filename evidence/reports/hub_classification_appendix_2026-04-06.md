# Hub Classification Appendix
## Recurring Byron infrastructure around the earliest clean merges

**Appendix date:** 2026-04-06  
**Purpose:** classify the recurring addresses that sit immediately downstream of the earliest clean pairwise merges and inside the strongest clean three-way merge  
**Primary evidence classes:** published founder trace-edge CSVs, live db-sync validation, and public explorer / documentation references  
**Structured trace-local metrics:** `outputs/cross_entity_evidence/hub_trace_local_stats_2026-04-06.json`  
**Live route artifacts:** `outputs/cross_entity_evidence/sink_to_splitter_transactions_2026-04-06.csv`, `outputs/cross_entity_evidence/splitter_to_bridge_forward_trace_2026-04-06.csv`, `outputs/cross_entity_evidence/clean_three_way_direct_input_breakdown_2026-04-06.csv`, `outputs/cross_entity_evidence/focal_source_outputs_in_571f_2026-04-06.csv`, `outputs/cross_entity_evidence/bridge_inputs_value_distribution_2026-04-06.csv`

---

## Bottom line

The strongest current explanation is not "one founder treasury secretly chopping itself into thousands of wallets." It is that founder-descended flows repeatedly touch shared Byron-era service infrastructure with at least three distinct roles:

1. A high-volume shared sink / routing hub
2. A mechanical automated splitter
3. A smaller intermediate bridge / aggregator

The live replica now confirms the route chain directly:

1. `DdzFFzCqrhstmqBkaU98vdHu6PdqjqotmgudToWYEeRmQKDrn4cAgGv9EZKtu1DevLrMA1pdVazufUCK4zhFkUcQZ5Gm88mVHnrwmXvT` paid `Ae2tdPwUPEZ6xYrxCgRDM2NQFM5oajHEoJN3i9ZVV2AbsbvxoJBjVu3yP7W` in `41` transactions totaling `78,000,020 ADA`, all on `2020-07-03`.
2. `Ae2tdPwUPEZ6xYrxCgRDM2NQFM5oajHEoJN3i9ZVV2AbsbvxoJBjVu3yP7W` paid `Ae2tdPwUPEZHiXixpj6Xdju5jti25cY7QhjHZ3WiZypCsfEJoJx5fGujAKn` in `4` transactions totaling `50,000,000 ADA`.
3. Clean three-way merge transaction `571f776c0698c576ddecae145f97e7f284b82ebea70fbc924fa4e2a4a6258020` then consumed `381` direct inputs from `Ae2tdPwUPEZHiXixpj6Xdju5jti25cY7QhjHZ3WiZypCsfEJoJx5fGujAKn`, totaling `48,718,538.910083 ADA`.

That does not rule out collusion or common control in specific cases, but it materially changes the burden of proof. The infrastructure pattern looks more like shared operational rails than a single clean founder-owned wallet tree.

---

## Classification table

| Address | Working classification | Confidence | Why |
| --- | --- | --- | --- |
| `DdzFFzCqrhstmqBkaU98vdHu6PdqjqotmgudToWYEeRmQKDrn4cAgGv9EZKtu1DevLrMA1pdVazufUCK4zhFkUcQZ5Gm88mVHnrwmXvT` | Exchange/custody/shared-routing sink | High | Very large public footprint, repeated cross-seed receipt, and now a live-validated direct payment chain into the splitter |
| `Ae2tdPwUPEZ6xYrxCgRDM2NQFM5oajHEoJN3i9ZVV2AbsbvxoJBjVu3yP7W` | Automated splitter / distribution wallet | High | Repeated exact 58-output fan-outs, many 50+ output spends inside founder traces, and live-validated funding from the sink plus onward funding of the bridge |
| `Ae2tdPwUPEZHiXixpj6Xdju5jti25cY7QhjHZ3WiZypCsfEJoJx5fGujAKn` | Intermediate bridge / aggregator wallet | High | Present across all three founder traces, low-fanout behavior, and now confirmed as the dominant direct input source to the clean three-way merge |

---

## Address 1: `DdzFFzCqrhstmqBkaU98vdHu6PdqjqotmgudToWYEeRmQKDrn4cAgGv9EZKtu1DevLrMA1pdVazufUCK4zhFkUcQZ5Gm88mVHnrwmXvT`

### Classification

**High-confidence shared sink / routing hub.**

### Why this classification fits

- Public explorer evidence is large-scale and exchange-like. AdaScan reports:
  - `150,966` total transactions
  - `20,180,619,991.547100 ADA` total received
  - `20,180,619,991.545600 ADA` total sent
  - zero current balance
- In the founder trace exports, this address appears on **all three founder branches** as both a recipient and a spender.
- Within the founder traces alone, it appears as:
  - `1,104` traced outputs received
  - `379` traced spending transactions
  - active from `2018-12-06` through `2020-07-03`
- The earliest clean pairwise merge outputs land directly on this address:
  - IOG+EMURGO: `a71578ec01f6cf39dbcf31351631159e3dd6fb99dd475783effbc65b90b8f0f9` at epoch `95`
  - IOG+CF: `f9951db326893e5c6cd94407e3d75be4928442aaf5809e435ca3e82c1983949d` at epoch `193`
- The live replica confirms this address directly funded the splitter address `Ae2tdPwUPEZ6xYrxCgRDM2NQFM5oajHEoJN3i9ZVV2AbsbvxoJBjVu3yP7W`:
  - `41` outputs / `41` receiving transactions
  - total `78,000,020 ADA`
  - first seen `2020-07-03 08:13:11+00`
  - last seen `2020-07-03 16:16:51+00`
  - value pattern: `39` outputs of exactly `2,000,000 ADA` and `2` outputs of exactly `10 ADA`

### What it suggests

- This address behaves much more like an omnibus sink or routing wallet than a tidy private founder treasury wallet.
- Clean pairwise founder merges feed into it early, and it then funds the splitter directly in a highly regular same-day batch.
- It is reasonable to treat this address as **exchange-like or custody-like infrastructure** until disproven.

### What it does not prove

- It does **not** by itself prove Binance, Coinbase, or any specific named exchange.
- It does **not** prove beneficial ownership by any founder entity.
- It does **not** prove realized sale execution just because founder-descended UTxOs arrive there.

---

## Address 2: `Ae2tdPwUPEZ6xYrxCgRDM2NQFM5oajHEoJN3i9ZVV2AbsbvxoJBjVu3yP7W`

### Classification

**High-confidence automated splitter / distribution wallet.**

### Why this classification fits

- In the founder traces, this address shows classic mechanical fan-out behavior:
  - `323` traced spending transactions
  - `18` traced spend transactions with exactly `58` outputs
  - `31` traced spend transactions with `50+` outputs
  - maximum observed traced output count per spend transaction: `58`
- It is active across all three founder traces as both destination and source:
  - first trace-local inbound activity: `2020-07-03`
  - last trace-local outbound activity: `2021-10-22`
- Public explorer evidence also shows very large scale:
  - Blockchair reports `119,835` history entries on the address page
  - the address remained publicly active through at least `2024-01-16`
- The live replica now confirms the sink-to-splitter leg directly:
  - source address `DdzFFzCqrhstmqBkaU98vdHu6PdqjqotmgudToWYEeRmQKDrn4cAgGv9EZKtu1DevLrMA1pdVazufUCK4zhFkUcQZ5Gm88mVHnrwmXvT`
  - destination address `Ae2tdPwUPEZ6xYrxCgRDM2NQFM5oajHEoJN3i9ZVV2AbsbvxoJBjVu3yP7W`
  - `41` transactions totaling `78,000,020 ADA`
- The live replica also confirms the splitter-to-bridge leg directly:
  - source address `Ae2tdPwUPEZ6xYrxCgRDM2NQFM5oajHEoJN3i9ZVV2AbsbvxoJBjVu3yP7W`
  - destination address `Ae2tdPwUPEZHiXixpj6Xdju5jti25cY7QhjHZ3WiZypCsfEJoJx5fGujAKn`
  - `4` transactions totaling `50,000,000 ADA`

### Verified splitter -> bridge transactions

| TX Hash | `dest_tx_out_id` | ADA | Time UTC | First Spend TX |
| --- | ---: | ---: | --- | --- |
| `a9af4adba1feb3cf84d41c0ed6d8084ae57d0991e14ffcddbd1fa49f6249de7b` | 5497972 | 10000000 | `2020-07-04 04:11:11+00` | `963c761a2e798bfe2e35bf7d3bb888c1c178fb8407b9e431b93bcddbd7fe83d0` |
| `37600a6ffb718e609db73d508c048027ce9f1e0549c65450ab35588da46e6be9` | 5550334 | 10000000 | `2020-07-07 05:44:11+00` | `024ae3eaedfd98e5fa61b2650eab0ef1f40190da600a5cd8b2184a60856e8737` |
| `8d782da14a4b797a753bf276ae0f8f2616f27bb3faed72c741e34c81c13fc7c0` | 5678309 | 10000000 | `2020-07-13 02:05:51+00` | `26174c832f6261944ac9074817b0dbe8ef7f81d55f193723672cfd0065d0bc04` |
| `a20ca4ba7bd46739e8f8ff8c1e94b583cf4751a311fcf9f157318933c522ba3d` | 7061516 | 20000000 | `2020-11-14 00:02:54+00` | `988b65ca092d5d4254ce4313d593aafdd0bab57a59ac9059332e74087ea08858` |

### What it suggests

- This is not a normal retail wallet.
- The repeated exact-output mechanical pattern is consistent with scripted batch distribution.
- The more defensible description is **automated splitter inside a shared Byron infrastructure cluster**, not "proof of concealment" by itself.

### What it does not prove

- The address format being Byron legacy is not suspicious on its own. Official guidance still notes exchange support for Byron legacy formats, including `Ae2` and `DdzFF`.
- Fragmentation alone is not proof of laundering or concealment. Cardano wallets and exchange systems can legitimately produce many addresses and UTxOs.

---

## Address 3: `Ae2tdPwUPEZHiXixpj6Xdju5jti25cY7QhjHZ3WiZypCsfEJoJx5fGujAKn`

### Classification

**High-confidence intermediate bridge / aggregator wallet.**

### Why this classification fits

- This address is present across **all three founder traces**, but its behavior is different from the splitter:
  - `125` traced inbound outputs
  - `41` traced source UTxOs later spent
  - only `31` traced spending transactions
  - maximum observed traced output count per spend transaction: `3`
  - zero traced `58`-output or `72`-output spending transactions
- Its trace-local active window is narrower:
  - first inbound: `2020-06-02`
  - last outbound: `2021-02-25`
- Its top trace-local outputs include large Shelley-era addresses such as:
  - `addr1qxtrqdumg8dleqcra3myptlq6n43m8s0mver0pwgqrr8awvkkcdaz26hglgm4qvc6fdy0rr4ck6q5q249drqc4fzyrgq68vuva` with `590,000,000 ADA` across traced rows
  - `addr1q84qw26450qz5raerf6yvupnr8crk3z8cjrhvkmvfw6u95yyk3s302tp7mt5qt2vhyfuyj0y5h8xkm58qa726gr62jjqn9uju3` with `27,466,616.180623 ADA`
- The live replica now shows this address is not merely adjacent to the clean three-way merge. It is the dominant direct input address into transaction `571f776c0698c576ddecae145f97e7f284b82ebea70fbc924fa4e2a4a6258020`:
  - `381` direct inputs
  - `381` distinct creator transactions
  - `48,718,538.910083 ADA` total
  - creator-time window `2020-06-03 17:31:31+00` through `2021-02-21 21:54:42+00`
  - the only other direct input address in the transaction is `addr1q84qw26450qz5raerf6yvupnr8crk3z8cjrhvkmvfw6u95yyk3s302tp7mt5qt2vhyfuyj0y5h8xkm58qa726gr62jjqn9uju3` with `3` inputs totaling `1,526,100.481646 ADA`
- The value distribution is partly mechanical rather than purely bespoke:
  - `5` bridge inputs are exactly `1,000,000 ADA`
  - several smaller fixed-value clusters repeat twice each, including `4.998796519 ADA`, `2.499797119 ADA`, `0.499797119 ADA`, `0.199797119 ADA`, `0.099834159 ADA`, and `0.098834159 ADA`

### Focal source outputs consumed directly by the clean three-way merge

| `source_tx_out_id` | Source TX Hash | Address | ADA | Spent In |
| ---: | --- | --- | ---: | --- |
| 8064253 | `a66e639963ddfbe81f1f1cbb7dafe5827c1d4cd1458e91b5a9379e27d96961de` | `Ae2tdPwUPEZHiXixpj6Xdju5jti25cY7QhjHZ3WiZypCsfEJoJx5fGujAKn` | 910915.170105 | `571f776c0698c576ddecae145f97e7f284b82ebea70fbc924fa4e2a4a6258020` |
| 8926255 | `cb60f72cb3fa8b421c6df258b34bea849d9fe1f8929763bf0ffa0bfc1413e8d7` | `Ae2tdPwUPEZHiXixpj6Xdju5jti25cY7QhjHZ3WiZypCsfEJoJx5fGujAKn` | 561453.520694 | `571f776c0698c576ddecae145f97e7f284b82ebea70fbc924fa4e2a4a6258020` |
| 9036401 | `7ef156177588a4205ef8339a02457b69fd8b2a00dadc5a6596f5aaf642771e72` | `Ae2tdPwUPEZHiXixpj6Xdju5jti25cY7QhjHZ3WiZypCsfEJoJx5fGujAKn` | 474635.146535 | `571f776c0698c576ddecae145f97e7f284b82ebea70fbc924fa4e2a4a6258020` |
| 10748217 | `d1f9929510f8f69185299a2916d595284810b778313bb08e3b1d71d97a418fb1` | `addr1q84qw26450qz5raerf6yvupnr8crk3z8cjrhvkmvfw6u95yyk3s302tp7mt5qt2vhyfuyj0y5h8xkm58qa726gr62jjqn9uju3` | 999748.890172 | `571f776c0698c576ddecae145f97e7f284b82ebea70fbc924fa4e2a4a6258020` |

### What it suggests

- This address looks like an **internal bridge / aggregator** that consolidates Byron-cluster flows and forwards them into downstream structure, including the clean three-way merge itself.
- The strongest clean three-way evidence is therefore not just "the same outputs converge later." It is "the merge transaction is overwhelmingly funded from one cross-seed bridge address."
- The `381`-of-`381` creator-transaction pattern indicates the bridge inputs were sourced from a wide staged buildup, not from a single last-minute consolidation transaction.

### What it does not prove

- No strong public identity label surfaced for this address in the public search pass.
- The classification is therefore behavioral, not identity-based.

---

## Why the distinction matters

- If all three addresses were treated as the same kind of wallet, the report would overstate what the chain proves.
- The sink, splitter, and bridge roles imply a **system**:
  - pairwise founder-descended flows converge into high-volume shared routing
  - that routing feeds an automated splitter
  - the splitter feeds a lower-fanout bridge
  - the bridge becomes the dominant direct input source to the clean three-way merge
- That system is suspicious enough to justify deeper investigation, but it is analytically different from saying "the founders were obviously hiding funds in one wallet."

---

## Current best-supported interpretation

- **Strongest supported claim:** founder-descended flows repeatedly enter shared operational wallet infrastructure, and the clean three-way merge is overwhelmingly funded from that bridge layer.
- **Most likely infrastructure picture:** exchange/custody/shared-routing sink plus scripted Byron distribution wallets plus intermediate bridge wallets.
- **Still not proven:** whether the shared infrastructure was founder-controlled, third-party exchange/custody infrastructure, or a mix of both at different points in time.

---

## Recommended next steps

1. Build a one-hop neighborhood table for `Ae2tdPwUPEZHiXixpj6Xdju5jti25cY7QhjHZ3WiZypCsfEJoJx5fGujAKn`:
   - creator transactions for all `381` direct inputs into `571f776c0698c576ddecae145f97e7f284b82ebea70fbc924fa4e2a4a6258020`
   - source-address mix of those creator transactions
   - founder-seed labels for the inputs feeding those creator transactions
2. Trace the `41` sink-to-splitter payments from `DdzFFzCqrhstmqBkaU98vdHu6PdqjqotmgudToWYEeRmQKDrn4cAgGv9EZKtu1DevLrMA1pdVazufUCK4zhFkUcQZ5Gm88mVHnrwmXvT` through first spend, to see how much of that same-day batch enters the later bridge cluster.
3. Expand the splitter-to-bridge pass from the verified four transactions into a full descendant graph:
   - `a9af4adba1feb3cf84d41c0ed6d8084ae57d0991e14ffcddbd1fa49f6249de7b`
   - `37600a6ffb718e609db73d508c048027ce9f1e0549c65450ab35588da46e6be9`
   - `8d782da14a4b797a753bf276ae0f8f2616f27bb3faed72c741e34c81c13fc7c0`
   - `a20ca4ba7bd46739e8f8ff8c1e94b583cf4751a311fcf9f157318933c522ba3d`
4. Classify the high-value creator transactions behind the bridge inputs, especially those producing repeated `1,000,000 ADA` bridge outputs in late 2020 and early 2021.
5. Keep identity claims narrower than infrastructure claims. At this stage, the infrastructure story is stronger than the legal-ownership story.

---

## Public corroboration

- AdaScan address page for `DdzFFzCqrhstmqBkaU98vdHu6PdqjqotmgudToWYEeRmQKDrn4cAgGv9EZKtu1DevLrMA1pdVazufUCK4zhFkUcQZ5Gm88mVHnrwmXvT`:
  - https://adascan.net/address/DdzFFzCqrhstmqBkaU98vdHu6PdqjqotmgudToWYEeRmQKDrn4cAgGv9EZKtu1DevLrMA1pdVazufUCK4zhFkUcQZ5Gm88mVHnrwmXvT/
- Blockchair address page for `Ae2tdPwUPEZ6xYrxCgRDM2NQFM5oajHEoJN3i9ZVV2AbsbvxoJBjVu3yP7W`:
  - https://blockchair.com/cardano/address/Ae2tdPwUPEZ6xYrxCgRDM2NQFM5oajHEoJN3i9ZVV2AbsbvxoJBjVu3yP7W
- Coinbase help on Cardano legacy Byron address support:
  - https://help.coinbase.com/en/coinbase/getting-started/crypto-education/ada-address-restrictions
- EMURGO on legacy Byron prefixes still used by centralized exchanges:
  - https://www.emurgo.io/press-news/yoroi-wallet-how-to-send-and-receive-ada/
- EMURGO on one wallet generating several addresses from the same private key:
  - https://www.emurgo.io/press-news/yoroi-wallet-a-guide-to-the-receive-menu/

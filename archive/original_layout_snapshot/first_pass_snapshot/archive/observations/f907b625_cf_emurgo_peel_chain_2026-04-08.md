# `f907b625...` Clean CF+EMURGO Merge Peel Chain
**Date:** 2026-04-08
**Question:** What happens downstream of the large clean CF+EMURGO merge `f907b625...` at epoch 226?

## Root Transaction

`f907b62584ca76c533f410867bf964c527b2a8251849d93c2b48a5b69e641816`

Live db-sync confirms:

- epoch: **226**
- block time: **2020-10-29 15:13:57 UTC**
- inputs: **53**
- outputs: **1**
- total output: **1,999,999,999.820448 ADA**
- annotated classification: **clean CF+EMURGO merge**

This is one of the largest clean pairwise merges in the dataset.

## First Split

The single `f907b625...` output is first spent by:

- `48bb2ca95450f38d7cedac5e2ceb2eb4fc96cdbe4757e2d99821ffe486862b9d`

That spend immediately splits the 2B output into:

- **200,000,000 ADA** to `stake1uxexwrph9r2p3lv42r7ccjptpmml33u2v3xx4p0q9ks85wc2y9t33`
- **1,799,999,999.640 ADA** to `stake1u9zjr6e37w53a474puhx606ayr3rz2l6jljrmzvlzkk3cmg0m2zw0`

The 200M branch remains unspent in the current db-sync snapshot used here.

That branch is not isolated after the first split. It is later re-funded twice in epoch **391**:

- `1daba6274dbbe2f6a9cf3a031ee716597e14e7c43b1beec6ee2650ad6ee76b5a`
- `531150c6924b6054d9cc3801297477e9b7aeba0f5ee34f17241e8b97d579e3e0`

Live db-sync confirms both transactions:

- spend **exclusively** from Byron address **Hub 1** (`Ae2tdPwUPEYwFx4dmJheyNPPYXtvHbJLeCaA96o6Y2iiUL18cAt7AizN2zG`)
- output funds to the **same two stake credentials**:
  - `stake1uxexwrph9r2...` receives **152,299,985 ADA** and **100,000,000 ADA**
  - `stake1u9zjr6e37w...` receives the paired companion outputs of **8,007,872.284526 ADA** and **1,408,414.619271 ADA**

So the later top-ups to the 200M branch are not independent external credits. They are direct Hub-1-sourced paired splits alongside the already exchange-tagged main carry stake.

By contrast, sampled follow-on large transactions on the 150M side branches look different. For example:

- `aa182046...` spends a single input from `stake1u84jrq070...` and recreates that same side branch at **150,000,007.825567 ADA**
- `f7b1437d...` spends a single input from `stake1ux0xnj5lj...` and recreates that same side branch at **150,549,271.077355 ADA**
- `99791cba...` spends a single input from `stake1uxz3a23cm...` and recreates that same side branch at **150,550,157.402652 ADA**

Those sampled side-branch follow-on transactions are same-stake self-churn with reward accretion, not fresh Hub-1 fan-in. So the 200M branch is operationally distinct from the rest of the peeled branches in the later history checked here.

## Systematic Peel Pattern

After that first split, the large carry output remains on the same stake credential `stake1u9zjr...` for multiple hops while repeated ~150M ADA side outputs are peeled off to distinct stake credentials.

Carry path:

| Hop | Carry ADA | Spent in tx |
|---|---:|---|
| 0 | 1,999,999,999.820 | `48bb2ca...` |
| 1 | 1,799,999,999.640 | `c7b39e6f...` |
| 2 | 1,649,999,989.460 | `f2879310...` |
| 3 | 1,649,989,990.280 | `4290d90d...` |
| 4 | 1,499,989,985.100 | `3eda4d63...` |
| 5 | 1,349,989,979.920 | `18b383c4...` |
| 6 | 1,199,989,974.739 | `5d36b176...` |
| 7 | 1,173,244,680.956 | `f9dc5121...` |
| 8 | 1,023,244,675.775 | `1ee44b55...` |
| 9 | 873,244,670.595 | `5538e1f4...` |
| 10 | 723,244,665.415 | `5d2f7feb...` |
| 11 | 683,244,665.236 | `ad3f3772...` |
| 12 | 650,000,000.000 | `e98be2aa...` |

The repeated side-output pattern visible along that path:

| Hop | Side output ADA | Recipient stake credential |
|---|---:|---|
| 1 | 150,000,010.000 | `stake1u84jrq070...` |
| 3 | 150,000,005.000 | `stake1ux0xnj5lj...` |
| 4 | 150,000,005.000 | `stake1uxz3a23cm...` |
| 5 | 150,000,005.000 | `stake1uxtj8luzp...` |
| 6 | 150,000,005.000 | `stake1uytfgj3wq...` |
| 7 | 150,000,005.000 | `stake1u8mf4hrhd...` |
| 8 | 150,000,005.000 | `stake1uxdpsgk3x...` |
| 9 | 150,000,005.000 | `stake1uxl72wy87...` |

That is an on-chain peel chain, not a one-off split.

## Later Stake-Profile Signal

Using live db-sync stake profiling for the exact high-value outputs in the peel chain:

- the main carry stake `stake1u9zjr6e37w...` has received **30.67B ADA** in total and still holds **1.93B ADA** unspent in the current snapshot
- the 200M branch stake `stake1uxexwrph9r2...` has since accumulated **452.30M ADA** total and still holds **452.30M ADA** unspent
- the 200M branch stake has **0 delegation transactions** in db-sync, but its two large later top-ups come directly from **Hub 1** and are output-paired with `stake1u9zjr6e37w...`
- the repeated 150M side-recipient stakes mostly accumulated about **450.5M ADA** total each and are now reduced to near-dust residuals (`2.1 ADA`, `1.004662 ADA`, or `0`)
- sampled later large transactions on multiple 150M side-recipient stakes are single-input same-stake respends, which looks more like internal address rotation / reward accretion than fresh external funding
- the later carry stake `stake1u8rmlr2h99gn...` has received **40.05B ADA** total, is now reduced to **2.759875 ADA** unspent, and has a recorded delegation to pool ticker **`BNP`** with pool name **`Binance Staking - 43`**
- the main carry stake `stake1u9zjr6e37w...` already appears in the local EMURGO exchange-analysis export as **`LIKELY_EXCHANGE / EXCHANGE`**
- the matching EMURGO and EMURGO_2 trace-edge rows feeding that same stake show source address **Hub 1** (`Ae2tdPwUPEYwFx4dmJheyNPPYXtvHbJLeCaA96o6Y2iiUL18cAt7AizN2zG`) creating `dest_tx_out_id=6273230` at epoch **211**

That last point is especially important.

This does **not** prove Binance or any exchange controlled the lineage at the original clean merge point. But it does show that the downstream peel lineage later intersects infrastructure explicitly labeled as Binance staking, while the main carry stake is separately tagged in the local exchange-analysis dataset and linked to Hub 1, and the 200M branch itself is later re-funded directly from Hub 1 in paired transactions with that same carry stake. That combination materially strengthens the exchange/custody interpretation relative to a pure isolated treasury hypothesis.

## Frontier Lookup Constraint

I checked the peel recipients and the carry stake credentials against the current founder frontier exports:

- `datasets/genesis-founders/iog/current_unspent.csv`
- `datasets/genesis-founders/emurgo/current_unspent.csv`
- `datasets/genesis-founders/cf/current_unspent.csv`
- `datasets/genesis-founders/emurgo2/current_unspent.csv`

Result:

- **0 hits** in each current frontier file

That does **not** prove non-founder control, but it does mean these downstream peel recipients are not simply persisting as obvious current-frontier founder outputs in the exported traces.

## Best Current Interpretation

The chain evidence supports a narrow, defensible claim:

> One of the largest clean CF+EMURGO merges does not dissipate randomly. It enters a structured custody/treasury-style peel chain with repeated ~150M ADA disbursements to fresh stake credentials while a large carry output remains under the same stake credential across successive hops.

The 200M side branch no longer looks like an unrelated dormant carve-out. Its later funding behavior places it inside the same Hub-1-linked operational cluster as the main carry branch.

What remains open is control attribution:

- founder treasury
- shared custodian
- exchange/custody batching
- OTC settlement structure

The later `Binance Staking - 43` delegation signal, combined with the Hub-1-only re-funding of the 200M branch, means the exchange/custody branch of that null hypothesis is now materially stronger than it was before this pass.

## Reproducibility

Main transaction:

- `f907b62584ca76c533f410867bf964c527b2a8251849d93c2b48a5b69e641816`

Saved query bundle:

- `queries/f907b625_peel_chain_checks.sql`

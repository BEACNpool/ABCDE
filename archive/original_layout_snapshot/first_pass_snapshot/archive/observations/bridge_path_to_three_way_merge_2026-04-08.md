# Bridge Path To The Clean Three-Way Merge
**Date:** 2026-04-08
**Question:** How was the bridge address feeding the clean three-way merge `571f776c...` assembled, and where does direct founder-trace tagging actually appear?

## Core Result

The bridge stage behind the clean three-way merge is real, but it is more structured than a simple "mixed founders in one creator transaction" story.

Live db-sync plus local feeder-tagging shows:

- `571f776c...` consumed **381** bridge UTxOs from `Ae2tdPwUPEZHiXixpj6Xdju5jti25cY7QhjHZ3WiZypCsfEJoJx5fGujAKn`
- those **381** bridge UTxOs were created by **381** distinct creator transactions
- total bridge value consumed by `571f776c...`: **48,718,538.910083 ADA**

So the immediate pre-merge structure is an address-level accumulator, not a small number of already-mixed creator transactions.

## Direct Founder-Tagged Creator Transactions

Feeder-input tagging against the founder trace-edge and frontier exports found:

- **59** tagged feeder rows
- across **30** distinct bridge creator transactions

Per creator-transaction seed composition:

- `IOG`: **24** creator txs
- `EMURGO`: **3** creator txs
- `CF`: **3** creator txs
- mixed-seed creator txs: **0**

This matters.

The bridge creator transactions that can be directly tied back to founder trace IDs are all **single-seed** creators. The cross-seed co-mingling is therefore happening at or after the bridge-accumulation stage, not inside these directly tagged creator txs themselves.

## Directly Tagged Bridge Value

Summing bridge value created by the directly tagged creator txs:

- `IOG`: **7,891,768.743028 ADA**
- `EMURGO`: **936,750.999248 ADA**
- `CF`: **62,916.794297 ADA**

Combined directly tagged bridge value:

- **8,891,436.536573 ADA**

Untagged creator transactions still dominate the bridge:

- untagged creator txs: **351**
- untagged bridge value: **39,827,102.373510 ADA**

Best current reading:

- the bridge contains a minority of directly founder-tagged creator flows
- the majority is already inside common intermediate infrastructure that the simple seed-tagging pass cannot attribute one step back

## Untagged Creator Cluster Signal

The "untagged" side is not evenly diffuse.

Clustering the all-none creator transactions by feeder address shows:

- `Ae2tdPwUPEZJCGuAQyPGCMUXS4XH9DZdH5sfPPruHi6WRtmKAw79bH25nF6` feeds **48** untagged creator txs totaling **20,392,710.427112 ADA** across epochs **232-249**
- `Ae2tdPwUPEZ3144Xnww5Et54apKUr9go5s3pL9SUdAU4E5igRZPj1Gfa66o` feeds **20** untagged creator txs totaling **3,316,510 ADA** across epochs **246-249**

Together those two feeder addresses account for:

- feeder participation in **48** and **20** untagged creator txs respectively
- **19** overlapping creator txs where both addresses appear together
- **49 / 351** distinct untagged creator txs in the union of those two clusters
- **24,908,249.390956 ADA** of bridge output value from that creator union
- about **62.54%** of all untagged bridge value

The local exchange-analysis corpus already flags both addresses as exchange-like:

- `Ae2td...JCGu...` appears as **`VERY_LIKELY_EXCHANGE / EXCHANGE`** in both IOG and EMURGO exchange-analysis exports
- `Ae2td...3144...` appears as **`VERY_LIKELY_EXCHANGE / EXCHANGE`** in the IOG exchange-analysis export

So the untagged bridge mass is not just unattributable residue. A large majority of it already clusters into Byron feeder addresses that the local exchange-analysis pass independently treats as exchange/custody infrastructure.

The broader exchange-like screen is even stronger. Treating any feeder address with a non-`NOT_EXCHANGE` label in the local exchange-analysis corpus as exchange-like yields:

- **21** exchange-like feeder addresses inside the untagged creator set
- **64 / 351** distinct untagged creator txs in the creator union
- **31,258,037.496911 ADA** of bridge output value
- about **78.48%** of all untagged bridge value

That leaves a residual untagged bridge remainder of only **8,569,064.876599 ADA** (about **21.52%**) outside the current exchange-like screen.

## Residual Structure

That remaining `8.569M ADA` is not homogeneous.

Residual creator segmentation:

- **210** single-feeder creators totaling **3,002,202.484344 ADA** (**35.04%** of the residual)
- **59** small multi-feeder creators (`2-6` feeders) totaling **2,145,630.622907 ADA** (**25.04%**)
- **6** mid-size multi-feeder creators (`8-13` feeders) totaling **364,576.426584 ADA** (**4.25%**)
- **12** large multi-feeder creators (`33-78` feeders) totaling **3,056,655.342764 ADA** (**35.67%**)

Only **317,184.914155 ADA** of the residual sits in the smallest "single-feeder and under 10k ADA" bucket.

The single-feeder side is cleaner than it first looked:

- the **210** single-feeder residual creators map to **209** unique feeder addresses
- **0 / 209** of those feeder addresses appear anywhere in the local exchange-analysis corpus
- the top **10** single-feeder creators account for about **65.63%** of single-feeder bridge value
- the top **20** account for about **77.79%**
- the only repeated single-feeder address created two near-identical **4,998.796519 ADA** bridge creators about **30 minutes** apart on **2020-11-29**

So this bucket is not merely a weak-label spillover from the local exchange screen. It is a genuinely unlabeled residual set in the current local corpus, dominated by a relatively small number of larger one-input creators.

The 12 large residual multi-feeder creators are especially notable:

- all are single-output bridge creators
- they cluster late, across epochs **240-249**
- they range from **78,173.370808 ADA** to **520,930.145997 ADA**
- together they consume a union of **832** feeder addresses
- feeder-address recurrence inside that 12-tx cluster is extremely weak; the most recurrent address appears in only **3 / 12** creators

That is consistent with a residual operational batching layer, but not with a single dominant residual feeder wallet comparable to the exchange-like clusters already identified.

The pattern is now tighter than that first description suggested.

- the cluster contains **917** feeder rows across **12** creator transactions
- **11 / 12** creators hit an exact **80-input** shape; the remaining creator has **37** inputs
- all 12 are **single-output** bridge creators with narrow fees: **1.055781-2.213181 ADA**
- the 11 eighty-input creators all pay about **2.09-2.21 ADA**, consistent with a repeated consolidation template
- **882** distinct feeder source transactions feed the cluster, but **0** source transaction hashes are shared across different creators
- address reuse across creators is still sparse: **810 / 832** feeder addresses appear in only one creator, **21** appear in two creators, and only **1** address appears in three creators

The value mix also looks like batched deposit consolidation rather than a single hidden treasury wallet.

- **867 / 917** feeder inputs are under **10k ADA**
- **598 / 917** are under **1k ADA**
- those sub-`10k` inputs contribute only about **33.97%** of input value
- the remaining **50** inputs at `>=10k ADA` contribute about **66.03%**

So the cluster is not "all dust", but it is also not a small set of large feeder wallets. It is a high-input-count sweep made up of a long tail of smaller Byron outputs plus a modest number of larger anchors.

Exact denomination recurrence points the same way. Across the 12 creators:

- exact **`10 ADA`** inputs appear in **8** creators
- exact **`100 ADA`** inputs appear in **7** creators
- exact **`1,000 ADA`** inputs appear in **7** creators
- exact **`5,000 ADA`** inputs appear in **7** creators

Those denominations recur across creators, but the addresses and source transactions do not. That is more consistent with standardized customer or operational balance sizes being swept by the same batching logic than with a single residual wallet cluster feeding every creator.

## Splitter -> Bridge -> Intermediate Three-Way Path

Four verified bridge-spend transactions are especially important because they route directly into the previously known intermediate three-way merge path:

| Bridge spend tx | To `addr1q84qw26450...` / `stake1uxztgcgh...` | To `Ae2tdPwUPEYwNgu...` |
|---|---:|---:|
| `963c761a...` | 8,737,703.715404 ADA | 1,500,000 ADA |
| `024ae3ea...` | 6,281,772.356271 ADA | 4,000,000 ADA |
| `26174c83...` | 9,642,248.499705 ADA | 6,000,000 ADA |
| `988b65ca...` | 19,285,887.535196 ADA | 6,000,000 ADA |

Totals:

- to `addr1q84qw26450...` / `stake1uxztgcgh...`: **43,947,612.106576 ADA**
- to `Ae2tdPwUPEYwNgu...`: **17,500,000 ADA**

All four `addr1q84qw26450...` outputs were later spent in:

- `34147ef46fd105ed39e3be63ac194e79622fb1bf9ea6e50313a0c3e0e6fd20c3`

That transaction is the known intermediate three-way merge before the clean three-way merge at epoch 250.

## Best Current Interpretation

The bridge findings sharpen the provenance story:

> The clean three-way merge did not arise from a handful of already-mixed founder creator transactions. Instead, separate single-seed creator flows were accumulated by a common bridge address, alongside a much larger pool of already-intermediate infrastructure, before entering the shared three-way merge path.

That "already-intermediate infrastructure" is now narrower than it first looked. At least the dominant untagged feeder cluster is already exchange-like in the local corpus, which materially strengthens an exchange/custody staging interpretation for the bridge remainder.

This is stronger than a generic "same addresses later" story, but it is still compatible with multiple control explanations:

- shared founder-controlled treasury infrastructure
- shared custodian
- exchange/custody batching
- OTC / broker staging

## Reproducibility

Artifacts used:

- `outputs/cross_entity_evidence/bridge_creator_inventory_result_a_2026-04-08.csv`
- `outputs/cross_entity_evidence/bridge_creator_feeders_result_b_2026-04-08.csv`
- `outputs/cross_entity_evidence/bridge_creator_feeders_tagged_2026-04-08.csv`
- `outputs/cross_entity_evidence/bridge_creator_summary_result_c_2026-04-08.csv`
- `outputs/cross_entity_evidence/bridge_untagged_creator_address_clusters_2026-04-08.csv`
- `outputs/cross_entity_evidence/bridge_untagged_creator_top_exchange_union_2026-04-08.csv`
- `outputs/cross_entity_evidence/bridge_untagged_creator_exchange_like_union_2026-04-08.csv`
- `outputs/cross_entity_evidence/bridge_untagged_residual_creators_2026-04-08.csv`
- `outputs/cross_entity_evidence/bridge_untagged_residual_large_batch_cluster_2026-04-08.csv`
- `outputs/cross_entity_evidence/bridge_residual_large_batch_patterns_2026-04-08.csv`
- `outputs/cross_entity_evidence/bridge_residual_large_batch_shared_addresses_2026-04-08.csv`
- `outputs/cross_entity_evidence/bridge_residual_large_batch_recurring_values_2026-04-08.csv`
- `outputs/cross_entity_evidence/bridge_residual_single_feeder_top20_2026-04-08.csv`
- `outputs/cross_entity_evidence/bridge_residual_single_feeder_corpus_status_2026-04-08.csv`
- `outputs/cross_entity_evidence/splitter_bridge_spending_expansion_2026-04-08.csv`

Scripts:

- `scripts/run_bridge_creator_step1.sh`
- `scripts/tag_creator_feeders_with_seed_traces.py`
- `scripts/summarize_bridge_untagged_creators.py`
- `scripts/analyze_bridge_residual_large_batches.py`
- `scripts/run_step3_splitter_bridge_expansion.sh`

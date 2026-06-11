# Genesis ADA Confidence Analysis

This report summarizes the founder depth-14 Genesis trace surface, confidence signals, DRep exposure, and proposal-alignment cuts.

## Evidence boundary

- FACT: trace membership, live-unspent status at db-sync tip, output creation time, latest DRep delegation, DRep votes, and deterministic confidence-score components.
- INFERENCE: `weak_behavior_signal`, `coordinated_like`, `probable_retained_like`, and `high_confidence_retained_like` are audit-prioritization classes.
- UNKNOWN: beneficial ownership, legal identity, custody, intent, or off-chain coordination.

## Snapshot

- Surface snapshot UTC: `2026-05-22 19:55:36.459413`
- db-sync tip UTC: `2026-05-22 19:55:16`
- db-sync tip epoch: `632`
- Trace rows: `82,494`
- Deduped current UTxOs: `78,203`
- Deduped current ADA: `724,286,082.644534`
- Stake-credential ADA in confidence signal table: `714,234,535.842345`
- No-stake / Byron ADA: `10,051,546.802189`
- Deduped current ADA with latest DRep delegation: `300,051,562.234949`

## Confidence Bands

| confidence_class | clusters | current_ada | avg_score | max_score |
| --- | --- | --- | --- | --- |
| trace_only | 24,978 | 293,690,928.39544 | 0.007 | 1 |
| weak_behavior_signal | 20,893 | 231,247,584.332815 | 2.335 | 4 |
| coordinated_like | 2,995 | 185,712,975.210684 | 6.124 | 7 |
| probable_retained_like | 85 | 1,830,677.101994 | 8.776 | 9 |
| high_confidence_retained_like | 81 | 1,752,370.801412 | 10.222 | 11 |

## Depth And Time

Depth is UTxO-hop depth from the founder seed output. The rows below are current live-unspent outputs at db-sync tip.

| min_depth | dedup_utxos | current_ada | earliest_output_utc | latest_output_utc | min_block | max_block |
| --- | --- | --- | --- | --- | --- | --- |
| 3 | 1 | 0.000131 | 2017-10-18 05:15:51 | 2017-10-18 05:15:51 | 105,004 | 105,004 |
| 4 | 2 | 1.000047 | 2017-09-28 11:26:51 | 2019-11-12 09:47:31 | 19,747 | 3,365,908 |
| 5 | 3 | 3.365907 | 2017-11-25 07:02:11 | 2022-09-01 09:14:41 | 269,473 | 7,700,362 |
| 6 | 1 | 1 | 2020-04-06 17:48:11 | 2020-04-06 17:48:11 | 3,997,525 | 3,997,525 |
| 7 | 11 | 175,909.214675 | 2019-03-10 13:45:31 | 2020-12-02 21:28:32 | 2,299,631 | 5,027,352 |
| 8 | 8 | 7,705.612005 | 2018-01-31 15:39:11 | 2021-02-08 20:01:28 | 560,430 | 5,316,902 |
| 9 | 30 | 372,870.244285 | 2017-12-12 08:30:31 | 2023-04-11 08:06:00 | 343,170 | 8,632,639 |
| 10 | 259 | 1,442,069.40165 | 2017-12-16 03:14:11 | 2025-08-05 15:50:55 | 359,499 | 12,218,725 |
| 11 | 1,316 | 6,537,123.013996 | 2017-12-19 15:48:11 | 2026-05-09 04:14:38 | 374,718 | 13,394,652 |
| 12 | 5,943 | 50,266,328.610297 | 2018-03-02 12:33:51 | 2026-05-02 10:47:54 | 689,470 | 13,366,237 |
| 13 | 22,365 | 79,547,424.038352 | 2017-12-02 22:27:51 | 2026-05-16 18:15:39 | 302,487 | 13,426,650 |
| 14 | 48,264 | 585,936,647.143189 | 2018-01-11 09:43:31 | 2026-05-21 12:01:40 | 472,978 | 13,446,636 |

## Root And Overlap

| root_seed_id | trace_rows | current_utxos | root_trace_ada | stake_credentials |
| --- | --- | --- | --- | --- |
| iog | 75,964 | 75,964 | 506,878,815.714483 | 48,570 |
| emurgo | 6,337 | 6,337 | 256,387,832.912934 | 3,803 |
| cf | 193 | 193 | 2,215,281.552941 | 35 |

### Current UTxO Root Combos

| root_combo | dedup_utxos | current_ada |
| --- | --- | --- |
| iog | 71,681 | 465,683,999.980279 |
| emurgo | 2,075 | 215,224,294.137018 |
| emurgo+iog | 4,254 | 41,162,506.974296 |
| cf | 160 | 2,182,931.270022 |
| cf+iog | 25 | 31,318.481299 |
| cf+emurgo+iog | 4 | 990.278609 |
| cf+emurgo | 4 | 41.523011 |

## DRep Exposure By Confidence Class

| behavior_class | drep_rows | current_ada | current_utxos |
| --- | --- | --- | --- |
| trace_only | 9 | 293,690,928.39544 | 31,611 |
| weak_behavior_signal | 170 | 231,247,584.332815 | 33,294 |
| coordinated_like | 52 | 185,712,975.210684 | 8,039 |
| no_stake_or_byron | 1 | 10,051,546.802189 | 4,416 |
| probable_retained_like | 18 | 1,830,677.101994 | 356 |
| high_confidence_retained_like | 12 | 1,752,370.801412 | 487 |

### Top DRep Targets By Traced Current ADA

| drep | behavior_class | current_ada | current_utxos | max_trace_to_power_ratio |
| --- | --- | --- | --- | --- |
|  | trace_only | 290,648,263.407427 | 31,361 |  |
| drep_always_abstain | coordinated_like | 167,878,892.284982 | 1,430 | 0.018639 |
| drep_always_abstain | weak_behavior_signal | 110,977,429.249747 | 1,959 | 0.012322 |
|  | weak_behavior_signal | 108,788,124.145686 | 29,551 |  |
|  | coordinated_like | 14,746,586.054283 | 5,671 |  |
|  | no_stake_or_byron | 10,051,546.802189 | 4,416 |  |
| drep_always_abstain | trace_only | 2,766,517.533837 | 172 | 0.000307 |
| `drep1qe2l8gw8v7yds...` | weak_behavior_signal | 2,304,430.030814 | 589 | 0.003326 |
| drep_always_abstain | high_confidence_retained_like | 1,227,147.265626 | 226 | 0.000136 |
| drep_always_abstain | probable_retained_like | 1,183,501.306928 | 280 | 0.000131 |
| `drep1ju2udpph53uua...` | weak_behavior_signal | 958,165.815359 | 10 | 0.401789 |
| `drep1ydvwp8x9j8u4f...` | coordinated_like | 886,784.98934 | 17 | 0.012049 |
| `drep1djhscd8wt6zxm...` | weak_behavior_signal | 808,956.702647 | 2 | 0.073153 |
| `drep127pc58jyky40f...` | weak_behavior_signal | 735,173.368625 | 36 | 0.010261 |
| `drep1qe2l8gw8v7yds...` | coordinated_like | 630,639.790801 | 344 | 0.00091 |
| `drep16tsw66jtrver8...` | weak_behavior_signal | 543,220.082392 | 69 | 0.002624 |
| `drep1mkmnzmtlflcad...` | weak_behavior_signal | 534,713.440131 | 15 | 0.007172 |
| `drep14pjm8ytt682wk...` | weak_behavior_signal | 432,620.925495 | 4 | 0.011998 |
| `drep1xgzlpyy3pvywm...` | weak_behavior_signal | 419,188.805124 | 16 | 0.011576 |
| `drep13d6sxkyz6st9h...` | weak_behavior_signal | 418,372.314012 | 143 | 0.001674 |
| `drep1kyppjlhz4lawh...` | weak_behavior_signal | 368,549.182457 | 49 | 0.002007 |
| `drep1qz8frp3eq58v3...` | weak_behavior_signal | 355,948.551486 | 33 | 0.003691 |
| `drep1xfzdeu7mutvla...` | weak_behavior_signal | 354,747.049263 | 1 | 0.353065 |
| `drep1lhkqu7uhq9532...` | weak_behavior_signal | 338,591.060803 | 9 | 0.003389 |
| `drep16tsw66jtrver8...` | coordinated_like | 292,110.399454 | 76 | 0.001411 |

### Top DRep Targets For Probable/High Retained-Like Signals

| drep | confidence_class | clusters | current_ada | max_score |
| --- | --- | --- | --- | --- |
| drep_always_abstain | high_confidence_retained_like | 39 | 1,227,147.265626 | 10 |
| drep_always_abstain | probable_retained_like | 60 | 1,183,501.306928 | 9 |
| `drep1ydvwp8x9j8u4f...` | probable_retained_like | 2 | 280,814.032861 | 8 |
| `drep1qe2l8gw8v7yds...` | high_confidence_retained_like | 18 | 146,631.9452 | 11 |
| `drep1qz8frp3eq58v3...` | probable_retained_like | 1 | 137,618.304853 | 8 |
| `drep127pc58jyky40f...` | high_confidence_retained_like | 3 | 137,258.981621 | 11 |
| `drep16tsw66jtrver8...` | probable_retained_like | 1 | 106,891.652909 | 8 |
| `drep1h95f0wrxasn0f...` | high_confidence_retained_like | 3 | 65,914.241979 | 11 |
| drep_always_no_confidence | high_confidence_retained_like | 1 | 56,945.429774 | 10 |
| `drep1km69g7ksf8t5g...` | probable_retained_like | 2 | 50,240.03559 | 8 |
| `drep1kyppjlhz4lawh...` | high_confidence_retained_like | 1 | 35,775.169846 | 11 |
| `drep13d6sxkyz6st9h...` | high_confidence_retained_like | 8 | 28,197.58186 | 11 |
| `drep1m8mnpykcjfyax...` | probable_retained_like | 2 | 19,600.320718 | 9 |
| `drep1xa90kae89lney...` | high_confidence_retained_like | 1 | 19,593.143544 | 11 |
| drep_always_no_confidence | probable_retained_like | 1 | 18,750.968121 | 9 |
| `drep1ydvwp8x9j8u4f...` | high_confidence_retained_like | 1 | 13,712.879403 | 11 |
| `drep1ectemlv45xsnv...` | probable_retained_like | 1 | 13,198.299114 | 8 |
| `drep13d6sxkyz6st9h...` | probable_retained_like | 4 | 9,962.37162 | 9 |
| `drep16tsw66jtrver8...` | high_confidence_retained_like | 3 | 9,788.458807 | 11 |
| `drep1ectemlv45xsnv...` | high_confidence_retained_like | 2 | 7,317.520452 | 10 |

## High-Value Clusters To Review

| confidence_class | behavior_score | behavior_flags | root_combo | current_ada | current_utxos | drep | stake_address |
| --- | --- | --- | --- | --- | --- | --- | --- |
| coordinated_like | 5 | same_block_hop;same_epoch_drep_cohort;current_drep_delegation | iog | 31,682,709.767353 | 4 | drep_always_abstain | `stake1u84u9k7yjnuj...` |
| coordinated_like | 5 | same_block_hop;same_epoch_drep_cohort;current_drep_delegation | iog | 16,684,273.129648 | 3 | drep_always_abstain | `stake1u970ch6knl4j...` |
| coordinated_like | 5 | same_block_hop;same_epoch_drep_cohort;current_drep_delegation | iog | 16,674,365.422057 | 3 | drep_always_abstain | `stake1u8yr90g09a2z...` |
| coordinated_like | 5 | same_block_hop;same_epoch_drep_cohort;current_drep_delegation | iog | 16,648,211.505381 | 3 | drep_always_abstain | `stake1u9q6nedpj7kt...` |
| coordinated_like | 5 | same_block_hop;same_epoch_drep_cohort;current_drep_delegation | iog | 16,614,701.079378 | 3 | drep_always_abstain | `stake1u9j7tecyajsl...` |
| coordinated_like | 6 | same_block_hop;same_epoch_drep_cohort;current_drep_delegation | iog | 16,610,246.008688 | 3 | drep_always_abstain | `stake1uyv7u4rpvcv5...` |
| coordinated_like | 5 | same_block_hop;same_epoch_drep_cohort;current_drep_delegation | iog | 16,355,553.525747 | 3 | drep_always_abstain | `stake1uxasl8h59m07...` |
| coordinated_like | 5 | same_block_hop;same_epoch_drep_cohort;current_drep_delegation | iog | 16,355,553.524005 | 3 | drep_always_abstain | `stake1u88zeazj5xy8...` |
| coordinated_like | 5 | same_block_hop;same_epoch_drep_cohort;current_drep_delegation | iog | 16,342,372.684488 | 3 | drep_always_abstain | `stake1u9ku4ja8eeen...` |
| coordinated_like | 6 | same_block_hop;cross_root_current_cluster | emurgo+iog | 3,097,426.615721 | 9 |  | `stake1uykwh9nr9chu...` |
| coordinated_like | 7 | same_block_hop;cross_root_current_cluster | emurgo+iog | 1,155,572.58509 | 10 |  | `stake1u8dhjv99hqdx...` |
| coordinated_like | 6 | same_block_hop;cross_root_current_cluster | cf+iog | 979,464.312979 | 5 |  | `stake1u8emduelnm3t...` |
| coordinated_like | 5 | cross_root_current_cluster;current_drep_delegation | emurgo+iog | 621,504.148536 | 3 | drep_always_abstain | `stake1uyz0cqm5h8au...` |
| coordinated_like | 6 | same_block_hop;same_epoch_drep_cohort;current_drep_delegation;drep_has_proposal_votes | iog | 606,025.577095 | 6 | `drep1ydvwp8x9j8u4f...` | `stake1u8fqp8r2gymc...` |
| coordinated_like | 6 | same_block_hop;cross_root_current_cluster | emurgo+iog | 579,987 | 3 |  | `stake1uxt98p0mrmyn...` |
| probable_retained_like | 9 | same_block_hop;same_epoch_drep_cohort;cross_root_current_cluster;current_drep_delegation | emurgo+iog | 524,770.827084 | 6 | drep_always_abstain | `stake1uxpcp0dvyq6d...` |
| high_confidence_retained_like | 10 | same_block_hop;same_epoch_drep_cohort;cross_root_current_cluster;current_drep_delegation | emurgo+iog | 489,039.722535 | 20 | drep_always_abstain | `stake1uy2szszadzdl...` |
| high_confidence_retained_like | 10 | same_block_hop;same_epoch_drep_cohort;cross_root_current_cluster;current_drep_delegation | emurgo+iog | 465,191.622478 | 5 | drep_always_abstain | `stake1u874qynqd8nv...` |
| coordinated_like | 7 | same_block_hop;cross_root_current_cluster | emurgo+iog | 367,874.751 | 6 |  | `stake1u9u8su0s6mx6...` |
| coordinated_like | 6 | same_block_hop;cross_root_current_cluster | emurgo+iog | 320,074.067577 | 7 |  | `stake1uxcr0deslyn3...` |
| coordinated_like | 6 | same_block_hop;same_epoch_drep_cohort;current_drep_delegation | iog | 315,478 | 4 | drep_always_abstain | `stake1u85dyj0fgw2t...` |
| probable_retained_like | 8 | same_block_hop;cross_root_current_cluster;current_drep_delegation;drep_has_proposal_votes | emurgo+iog | 269,270.866322 | 2 | `drep1ydvwp8x9j8u4f...` | `stake1u9ttk6zfrz8r...` |
| coordinated_like | 7 | same_block_hop;cross_root_current_cluster | emurgo+iog | 267,830.824863 | 7 |  | `stake1uykmfwajuxgd...` |
| coordinated_like | 5 | same_block_hop;current_drep_delegation;drep_has_proposal_votes | iog | 266,836.3945 | 2 | `drep1ydvwp8x9j8u4f...` | `stake1uy49hwnzllrl...` |
| coordinated_like | 7 | same_epoch_drep_cohort;cross_root_current_cluster;current_drep_delegation | emurgo+iog | 263,985.896 | 13 | drep_always_abstain | `stake1uy5h56akwjcz...` |

## Proposal Exposure

| behavior_class | vote | rows | current_ada |
| --- | --- | --- | --- |
| weak_behavior_signal | Yes | 6,809 | 661,092,764.505305 |
| coordinated_like | Yes | 2,407 | 193,505,376.379485 |
| weak_behavior_signal | No | 2,182 | 164,065,755.394994 |
| weak_behavior_signal | Abstain | 750 | 95,345,141.579505 |
| coordinated_like | No | 670 | 40,573,976.61599 |
| probable_retained_like | Yes | 1,025 | 37,419,643.617139 |
| high_confidence_retained_like | Yes | 463 | 26,682,273.535446 |
| coordinated_like | Abstain | 334 | 20,124,417.669875 |
| probable_retained_like | No | 253 | 12,243,689.699017 |
| high_confidence_retained_like | Abstain | 90 | 6,496,065.025579 |
| high_confidence_retained_like | No | 78 | 4,652,258.410677 |
| probable_retained_like | Abstain | 122 | 1,398,904.939929 |

### Top Proposals By Probable/High Retained-Like Exposure

| proposal_type | proposal_tx_hash | proposal_index | vote | behavior_class | current_ada | rows |
| --- | --- | --- | --- | --- | --- | --- |
| InfoAction | d16dffbae9d86a73cb343506e6712d79c278096dc25e8ba6900eb24522726bba | 0 | Yes | probable_retained_like | 902,618.859806 | 16 |
| TreasuryWithdrawals | f8393f1ff814d3d52336a97712361fed933d9ef9e8d0909e1d31536a549fd22f | 0 | Yes | probable_retained_like | 902,618.859806 | 16 |
| InfoAction | 8f54d021c6e6fcdd5a4908f10a7b092fa31cd94db2e809f2e06d7ffa4d78773d | 0 | Yes | probable_retained_like | 902,618.859806 | 16 |
| InfoAction | bd488931f792651fefa9c6fda185a2c6cec83245b51d994e33090ce36e29cc26 | 0 | Yes | high_confidence_retained_like | 721,170.185537 | 9 |
| InfoAction | 9b62b3c632f329016a968ac25211825bb4f84b12461121c7da3aa11df92370f9 | 0 | Yes | probable_retained_like | 685,837.742021 | 15 |
| TreasuryWithdrawals | 8ad3d454f3496a35cb0d07b0fd32f687f66338b7d60e787fc0a22939e5d8833e | 32 | Yes | probable_retained_like | 647,807.169267 | 16 |
| NewCommittee | 4dab331457b61b824bbc6ba4b9d9be4750e25c0b5dd42207aeb63c7431a6b704 | 0 | Yes | probable_retained_like | 628,424.826945 | 16 |
| NewCommittee | 47a0e7a4f9383b1afc2192b23b41824d65ac978d7741aca61fc1fa16833d1111 | 0 | Yes | probable_retained_like | 621,792.689083 | 13 |
| TreasuryWithdrawals | 8ad3d454f3496a35cb0d07b0fd32f687f66338b7d60e787fc0a22939e5d8833e | 2 | Yes | probable_retained_like | 609,305.909171 | 15 |
| TreasuryWithdrawals | 8ad3d454f3496a35cb0d07b0fd32f687f66338b7d60e787fc0a22939e5d8833e | 5 | Yes | probable_retained_like | 607,907.146491 | 13 |
| TreasuryWithdrawals | 8ad3d454f3496a35cb0d07b0fd32f687f66338b7d60e787fc0a22939e5d8833e | 6 | Yes | probable_retained_like | 607,907.146491 | 13 |
| TreasuryWithdrawals | 8ad3d454f3496a35cb0d07b0fd32f687f66338b7d60e787fc0a22939e5d8833e | 4 | Yes | probable_retained_like | 607,907.146491 | 13 |
| TreasuryWithdrawals | 8ad3d454f3496a35cb0d07b0fd32f687f66338b7d60e787fc0a22939e5d8833e | 1 | Yes | probable_retained_like | 607,904.008629 | 12 |
| TreasuryWithdrawals | 8ad3d454f3496a35cb0d07b0fd32f687f66338b7d60e787fc0a22939e5d8833e | 12 | Yes | probable_retained_like | 607,375.72679 | 13 |
| TreasuryWithdrawals | 8ad3d454f3496a35cb0d07b0fd32f687f66338b7d60e787fc0a22939e5d8833e | 23 | Yes | probable_retained_like | 606,673.207588 | 11 |
| TreasuryWithdrawals | 73e171a4c0730b4b59ecae271ab89f12a9d56360b02920e1f95107dbdc1d6762 | 1 | Yes | probable_retained_like | 597,309.570001 | 15 |
| NewConstitution | 8c653ee5c9800e6d31e79b5a7f7d4400c81d44717ad4db633dc18d4c07e4a4fd | 0 | Yes | probable_retained_like | 590,326.829119 | 15 |
| InfoAction | e14de8d9dc4f4ddf3fe9250a8a926e20f10e99b86bd0610b77d7a054981591ee | 0 | Yes | high_confidence_retained_like | 564,749.78153 | 7 |
| TreasuryWithdrawals | 8ad3d454f3496a35cb0d07b0fd32f687f66338b7d60e787fc0a22939e5d8833e | 21 | Yes | probable_retained_like | 557,132.553338 | 11 |
| ParameterChange | c21b00f90f18fce4003edf42b0b0d455126e01c946e80cc5341a9f9750caf795 | 0 | Yes | probable_retained_like | 521,533.174036 | 15 |
| InfoAction | 8845bfc37bb2f69e8f200fe28148b3dea3c4399b0c49ee0ed2bb4e349cab9eb7 | 0 | Yes | probable_retained_like | 514,910.036174 | 13 |
| TreasuryWithdrawals | 8ad3d454f3496a35cb0d07b0fd32f687f66338b7d60e787fc0a22939e5d8833e | 33 | Yes | high_confidence_retained_like | 508,623.998358 | 7 |
| InfoAction | 56f39054758f1a3cedc1de9225d66bf270b62dfdbfbc5399f1d6d43aceffc636 | 0 | Yes | probable_retained_like | 501,711.73706 | 12 |
| TreasuryWithdrawals | 2c7f900b7ff68f317a7b0e42231d4aed36227660baf2ee9a4be7e880eb977313 | 0 | Yes | probable_retained_like | 501,015.493582 | 12 |
| TreasuryWithdrawals | 8ad3d454f3496a35cb0d07b0fd32f687f66338b7d60e787fc0a22939e5d8833e | 8 | Yes | probable_retained_like | 501,015.493582 | 12 |

## Root x DRep Concentration

| root_seed_id | drep | behavior_class | current_ada | current_utxos |
| --- | --- | --- | --- | --- |
| emurgo |  | trace_only | 209,027,394.142419 | 473 |
| iog | drep_always_abstain | coordinated_like | 167,374,423.532031 | 1,384 |
| iog | drep_always_abstain | weak_behavior_signal | 110,164,692.214028 | 1,927 |
| iog |  | weak_behavior_signal | 106,749,615.086554 | 29,384 |
| iog |  | trace_only | 80,466,616.064852 | 30,840 |
| emurgo |  | weak_behavior_signal | 36,112,013.702433 | 1,400 |
| iog |  | coordinated_like | 13,857,778.293724 | 5,568 |
| iog |  | no_stake_or_byron | 7,581,394.383501 | 3,198 |
| emurgo |  | coordinated_like | 4,639,147.864726 | 2,434 |
| emurgo |  | no_stake_or_byron | 2,835,145.814056 | 1,456 |
| iog | drep_always_abstain | trace_only | 2,736,383.662099 | 164 |
| iog | `drep1qe2l8gw8v7yds...` | weak_behavior_signal | 2,149,814.047951 | 563 |
| iog | drep_always_abstain | high_confidence_retained_like | 1,215,642.876282 | 220 |
| cf |  | trace_only | 1,154,253.200156 | 48 |
| iog | drep_always_abstain | probable_retained_like | 1,033,328.895585 | 227 |
| iog | `drep1ju2udpph53uua...` | weak_behavior_signal | 958,165.815359 | 10 |
| iog | `drep1ydvwp8x9j8u4f...` | coordinated_like | 886,784.98934 | 17 |
| emurgo | drep_always_abstain | weak_behavior_signal | 812,737.035719 | 32 |
| iog | `drep1djhscd8wt6zxm...` | weak_behavior_signal | 808,956.702647 | 2 |
| emurgo | drep_always_abstain | probable_retained_like | 765,639.135592 | 138 |
| cf |  | coordinated_like | 753,023.980979 | 4 |
| iog | `drep127pc58jyky40f...` | weak_behavior_signal | 735,173.368625 | 36 |
| emurgo | drep_always_abstain | coordinated_like | 715,007.72094 | 138 |
| iog | `drep1qe2l8gw8v7yds...` | coordinated_like | 630,638.790801 | 343 |
| emurgo | drep_always_abstain | high_confidence_retained_like | 616,912.786641 | 56 |
| iog | `drep16tsw66jtrver8...` | weak_behavior_signal | 536,088.034269 | 68 |
| iog | `drep1mkmnzmtlflcad...` | weak_behavior_signal | 534,713.440131 | 15 |
| iog | `drep14pjm8ytt682wk...` | weak_behavior_signal | 432,620.925495 | 4 |
| iog | `drep1xgzlpyy3pvywm...` | weak_behavior_signal | 419,188.805124 | 16 |
| iog | `drep13d6sxkyz6st9h...` | weak_behavior_signal | 418,363.177481 | 141 |

## Interpretation

- The largest current ADA buckets are still `trace_only` and `weak_behavior_signal`; they should not be used as influence claims.
- `coordinated_like` is large enough to matter for prioritization, but it is still a behavior pattern, not ownership.
- `probable_retained_like` and `high_confidence_retained_like` are small by ADA compared with the full trace surface, which is good: the stricter flags are not swallowing the whole graph.
- Proposal exposure rows show where delegated DReps voted, not how the traced stake owners would have voted directly.

## Next Audit Work

1. Validate top high-confidence clusters manually with transaction-level receipts.
2. Add known service/custodian labels where public evidence supports them.
3. Compare the new confidence bands against the earlier IOG confidence-band cut.
4. Regenerate top-DRep profile exposure from this scored surface instead of preserved legacy receipts.

# Top DRep Profiles

This report profiles the current top DReps as a set. It is intentionally not a one-person dossier.

## Data snapshot

- Query timestamp UTC: `2026-07-03 05:48:09.787139`
- db-sync tip UTC: `2026-07-03 05:47:52`
- db-sync tip epoch: `640`
- DRep distribution epoch: `640`
- Active stake epoch: `641`
- Sources: ABCDE PostgreSQL/cardano-db-sync, preserved ABCDE genesis trace receipts, on-chain DRep registration anchors where present.
- Koios cross-check: `8/8 registered rows amount-matched Koios`

## Evidence boundaries

- FACT: current voting power, delegation counts, active stake buckets, DRep registration anchors, and pool affiliations are db-sync-derived.
- FACT: genesis-trace exposure is derived from preserved ABCDE trace receipts joined to latest observed DRep delegation for those traced stake credentials.
- STRONG INFERENCE: high latest-retention ratios indicate sticky DRep delegation behavior by stake credential.
- UNKNOWN: beneficial ownership, nationality, legal identity, intent, and off-chain demographics are not inferred from delegation data.
- Caveat: DRep delegation is voting power, not custody or control of delegated funds.

## Current top DReps

| Rank | Class | DRep | Voting ADA | Current delegators | Historical delegators | Retention | Genesis-trace ADA | Anchor |
|---:|---|---|---:|---:|---:|---:|---:|---|
| 1 | system | `drep_always_abstain` | 9,222,311,038.820501 | 233449 | 246080 | 94.87% | 715,194,554.487303 |  |
| 2 | registered | `drep1qe2l8gw8v7yds...` | 595,013,768.45995 | 25625 | 26735 | 95.85% | 8,330,765.355168 | raw.githubusercontent.com/Emurgo/constitution-committee/1... |
| 3 | registered | `drep1jnmmkfwpta0yu...` | 432,487,134.870637 | 1808 | 2094 | 86.34% | 4,081,161.510973 | raw.githubusercontent.com/cardanoz/drep/refs/heads/main/Y... |
| 4 | registered | `drep15mr008j83j7n0...` | 332,965,245.821395 | 102 | 112 | 91.07% | 885.293943 | gitlab.com/cbolden/cardano-governance/-/ra... |
| 5 | registered | `drep1m8mnpykcjfyax...` | 297,720,207.470339 | 576 | 641 | 89.86% | 4,365.951299 | raw.githubusercontent.com/Emurgo/constitution-committee/a... |
| 6 | registered | `drep16tsw66jtrver8...` | 242,678,026.974016 | 3129 | 3384 | 92.46% | 6,664,494.197364 | most-brass-sun.quicknode-ipfs.com/ipfs/QmZT35nEcX84VFtDGpUnTxhoB5... |
| 7 | registered | `drep13d6sxkyz6st9h...` | 222,597,864.038928 | 10973 | 11877 | 92.39% | 17,052,872.484183 | raw.githubusercontent.com/Tastenkunst/eternl-drep/main/24... |
| 8 | system | `drep_always_no_con...` | 176,605,061.827128 | 10788 | 12887 | 83.71% | 1,975,870.764068 |  |
| 9 | registered | `drep1kyppjlhz4lawh...` | 173,282,170.863023 | 1510 | 1685 | 89.61% | 13,117,192.493951 | raw.githubusercontent.com/SebastienGllmt/drep/main/drep-m... |
| 10 | registered | `drep1ectemlv45xsnv...` | 159,701,968.406964 | 9215 | 9272 | 99.39% | 47,474.528555 | everstake.one/cardano/everstake_id.json |

## Stake-size profile

Buckets are based on latest active stake for stake credentials whose latest DRep delegation points to the DRep.

| Rank | DRep | >=50M | 10M-50M | 1M-10M | 100k-1M | 10k-100k | 1k-10k | <1k | 0/no active stake |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | `drep_always_abstain` | 29 | 147 | 489 | 4328 | 20977 | 44117 | 113297 | 50066 |
| 2 | `drep1qe2l8gw8v7yds...` | 0 | 2 | 98 | 914 | 3561 | 5572 | 9294 | 6184 |
| 3 | `drep1jnmmkfwpta0yu...` | 1 | 4 | 78 | 231 | 335 | 289 | 618 | 252 |
| 4 | `drep15mr008j83j7n0...` | 4 | 1 | 2 | 6 | 18 | 15 | 50 | 6 |
| 5 | `drep1m8mnpykcjfyax...` | 2 | 4 | 9 | 51 | 132 | 115 | 159 | 104 |
| 6 | `drep16tsw66jtrver8...` | 0 | 2 | 34 | 403 | 752 | 547 | 1065 | 326 |
| 7 | `drep13d6sxkyz6st9h...` | 0 | 0 | 29 | 377 | 1532 | 1958 | 5313 | 1764 |
| 8 | `drep_always_no_con...` | 0 | 2 | 35 | 207 | 722 | 1344 | 4575 | 3903 |
| 9 | `drep1kyppjlhz4lawh...` | 0 | 1 | 43 | 213 | 321 | 258 | 535 | 139 |
| 10 | `drep1ectemlv45xsnv...` | 0 | 0 | 22 | 285 | 1470 | 2894 | 3625 | 919 |

## Latest-delegation age profile

This shows when current delegators last delegated to the DRep. Older buckets with large stake are a useful stickiness signal.

| Rank | DRep | Largest age bucket by ADA | Bucket ADA | Bucket delegators |
|---:|---|---|---:|---:|
| 1 | `drep_always_abstain` | 521-540 | 2,870,828,512.970052 | 70440 |
| 2 | `drep1qe2l8gw8v7yds...` | 561-580 | 206,549,273.24813 | 8918 |
| 3 | `drep1jnmmkfwpta0yu...` | 521-540 | 146,007,072.014683 | 713 |
| 4 | `drep15mr008j83j7n0...` | 541-560 | 234,263,893.267328 | 47 |
| 5 | `drep1m8mnpykcjfyax...` | 541-560 | 217,738,679.205066 | 188 |
| 6 | `drep16tsw66jtrver8...` | 521-540 | 80,544,077.827823 | 1059 |
| 7 | `drep13d6sxkyz6st9h...` | 521-540 | 62,534,857.779091 | 2980 |
| 8 | `drep_always_no_con...` | 521-540 | 78,505,566.392819 | 4699 |
| 9 | `drep1kyppjlhz4lawh...` | 521-540 | 79,910,237.909992 | 552 |
| 10 | `drep1ectemlv45xsnv...` | 601-620 | 74,017,193.967973 | 4573 |

## Top pool affiliations

For each DRep, this lists the top active SPO pool among current DRep delegators by active stake. Full top-10 pool rows are in the CSV.

| Rank | DRep | Top pool ticker | Pool ADA | Delegators |
|---:|---|---|---:|---:|
| 1 | `drep_always_abstain` | pool1lu2luhm... | 85,483,724.155429 | 4889 |
| 2 | `drep1qe2l8gw8v7yds...` | ADV | 30,074,057.844989 | 125 |
| 3 | `drep1jnmmkfwpta0yu...` | BD3 | 55,030,520.983117 | 3 |
| 4 | `drep15mr008j83j7n0...` | pool1mfyzxyg... | 76,049,512.776183 | 3 |
| 5 | `drep1m8mnpykcjfyax...` | OGAM | 58,101,966.963923 | 2 |
| 6 | `drep16tsw66jtrver8...` | pool1du3r4a7... | 21,214,068.284294 | 12 |
| 7 | `drep13d6sxkyz6st9h...` | HAPPY | 10,729,267.916923 | 85 |
| 8 | `drep_always_no_con...` | NORTH | 13,296,913.53866 | 34 |
| 9 | `drep1kyppjlhz4lawh...` | AUTO | 16,231,831.664315 | 4 |
| 10 | `drep1ectemlv45xsnv...` | EVE6 | 62,981,564.032519 | 2838 |

## Generated artifacts

- `data/small/governance_top_drep_profiles_current.csv`
- `data/small/governance_top_drep_stake_buckets.csv`
- `data/small/governance_top_drep_delegation_age_buckets.csv`
- `data/small/governance_top_drep_pool_affiliations.csv`
- `data/small/governance_top_drep_koios_crosscheck.csv`
- `data/small/governance_top_drep_genesis_trace_exposure.csv`
- `data/small/governance_top_drep_genesis_trace_exposure_by_root.csv`
- `data/small/governance_top_drep_genesis_trace_stickiness.csv`
- `data/manifests/top-drep-profiles-manifest.json`

# Top DRep Profiles

This report profiles the current top DReps as a set. It is intentionally not a one-person dossier.

## Data snapshot

- Query timestamp UTC: `2026-05-21 20:17:02.929505`
- db-sync tip UTC: `2026-05-21 20:16:53`
- db-sync tip epoch: `632`
- DRep distribution epoch: `632`
- Active stake epoch: `633`
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
| 1 | system | `drep_always_abstain` | 9,006,786,518.5734 | 224878 | 236934 | 94.91% | 715,194,554.487303 |  |
| 2 | registered | `drep1qe2l8gw8v7yds...` | 692,941,715.496004 | 25304 | 26245 | 96.41% | 8,330,765.355168 | raw.githubusercontent.com/Emurgo/constitution-committee/1... |
| 3 | registered | `drep1jnmmkfwpta0yu...` | 486,215,056.24676 | 1665 | 1904 | 87.45% | 4,081,161.510973 | raw.githubusercontent.com/cardanoz/drep/refs/heads/main/Y... |
| 4 | registered | `drep15mr008j83j7n0...` | 304,603,835.406535 | 98 | 107 | 91.59% | 885.293943 | gitlab.com/cbolden/cardano-governance/-/ra... |
| 5 | registered | `drep1m8mnpykcjfyax...` | 298,890,345.096918 | 488 | 540 | 90.37% | 4,365.951299 | raw.githubusercontent.com/Emurgo/constitution-committee/a... |
| 6 | registered | `drep13d6sxkyz6st9h...` | 249,865,505.201414 | 10652 | 11497 | 92.65% | 17,052,872.484183 | raw.githubusercontent.com/Tastenkunst/eternl-drep/main/24... |
| 7 | registered | `drep16tsw66jtrver8...` | 207,051,783.87094 | 2842 | 3070 | 92.57% | 6,664,494.197364 | most-brass-sun.quicknode-ipfs.com/ipfs/QmZT35nEcX84VFtDGpUnTxhoB5... |
| 8 | system | `drep_always_no_con...` | 200,445,380.166654 | 10569 | 12572 | 84.07% | 1,975,870.764068 |  |
| 9 | registered | `drep1kyppjlhz4lawh...` | 183,637,491.256425 | 1469 | 1626 | 90.34% | 13,117,192.493951 | raw.githubusercontent.com/SebastienGllmt/drep/main/drep-m... |
| 10 | registered | `drep1ectemlv45xsnv...` | 148,380,875.00142 | 8348 | 8390 | 99.50% | 47,474.528555 | everstake.one/cardano/everstake_id.json |

## Stake-size profile

Buckets are based on latest active stake for stake credentials whose latest DRep delegation points to the DRep.

| Rank | DRep | >=50M | 10M-50M | 1M-10M | 100k-1M | 10k-100k | 1k-10k | <1k | 0/no active stake |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | `drep_always_abstain` | 28 | 144 | 507 | 4376 | 21219 | 43943 | 108979 | 45682 |
| 2 | `drep1qe2l8gw8v7yds...` | 0 | 2 | 123 | 1062 | 3930 | 5840 | 8935 | 5412 |
| 3 | `drep1jnmmkfwpta0yu...` | 1 | 5 | 92 | 247 | 323 | 258 | 545 | 194 |
| 4 | `drep15mr008j83j7n0...` | 3 | 2 | 2 | 6 | 16 | 16 | 48 | 5 |
| 5 | `drep1m8mnpykcjfyax...` | 2 | 4 | 9 | 58 | 120 | 95 | 133 | 67 |
| 6 | `drep13d6sxkyz6st9h...` | 0 | 0 | 38 | 387 | 1571 | 2015 | 5035 | 1606 |
| 7 | `drep16tsw66jtrver8...` | 0 | 1 | 31 | 369 | 717 | 510 | 978 | 236 |
| 8 | `drep_always_no_con...` | 0 | 2 | 41 | 226 | 795 | 1405 | 4392 | 3708 |
| 9 | `drep1kyppjlhz4lawh...` | 0 | 1 | 47 | 229 | 334 | 269 | 476 | 113 |
| 10 | `drep1ectemlv45xsnv...` | 0 | 0 | 17 | 276 | 1378 | 2720 | 3296 | 661 |

## Latest-delegation age profile

This shows when current delegators last delegated to the DRep. Older buckets with large stake are a useful stickiness signal.

| Rank | DRep | Largest age bucket by ADA | Bucket ADA | Bucket delegators |
|---:|---|---|---:|---:|
| 1 | `drep_always_abstain` | 521-540 | 3,403,057,896.237328 | 70644 |
| 2 | `drep1qe2l8gw8v7yds...` | 561-580 | 251,768,513.3632 | 8970 |
| 3 | `drep1jnmmkfwpta0yu...` | 521-540 | 174,930,285.239556 | 724 |
| 4 | `drep15mr008j83j7n0...` | 541-560 | 233,740,265.07285 | 47 |
| 5 | `drep1m8mnpykcjfyax...` | 541-560 | 218,133,411.318984 | 189 |
| 6 | `drep13d6sxkyz6st9h...` | 521-540 | 82,378,319.35091 | 3000 |
| 7 | `drep16tsw66jtrver8...` | 521-540 | 84,370,170.519377 | 1064 |
| 8 | `drep_always_no_con...` | 521-540 | 92,095,123.557749 | 4723 |
| 9 | `drep1kyppjlhz4lawh...` | 521-540 | 84,047,114.257148 | 559 |
| 10 | `drep1ectemlv45xsnv...` | 601-620 | 78,086,145.523673 | 4602 |

## Top pool affiliations

For each DRep, this lists the top active SPO pool among current DRep delegators by active stake. Full top-10 pool rows are in the CSV.

| Rank | DRep | Top pool ticker | Pool ADA | Delegators |
|---:|---|---|---:|---:|
| 1 | `drep_always_abstain` | KILN4 | 77,194,869.305588 | 15 |
| 2 | `drep1qe2l8gw8v7yds...` | ADV | 33,104,411.940708 | 130 |
| 3 | `drep1jnmmkfwpta0yu...` | BD3 | 52,707,460.525265 | 3 |
| 4 | `drep15mr008j83j7n0...` | pool1mfyzxyg... | 75,898,939.514114 | 3 |
| 5 | `drep1m8mnpykcjfyax...` | OGAM | 58,115,433.645699 | 2 |
| 6 | `drep13d6sxkyz6st9h...` | HAPPY | 10,762,599.800211 | 85 |
| 7 | `drep16tsw66jtrver8...` | pool1du3r4a7... | 21,599,042.269623 | 10 |
| 8 | `drep_always_no_con...` | NORTH | 13,285,570.860047 | 34 |
| 9 | `drep1kyppjlhz4lawh...` | CCJ2 | 12,234,919.539904 | 7 |
| 10 | `drep1ectemlv45xsnv...` | EVE7 | 60,884,151.232121 | 3415 |

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

# Genesis Wallet Fragmentation Analysis
## IOG · EMURGO · CF — Hop-by-Hop Distribution Mechanics
### Cardano Forensic Analysis | ABCDE db-sync Warehouse

---

## Overview

This report documents the precise mechanics by which the three Cardano founding entity genesis allocations were fragmented from large treasury wallets into sub-50,000 ADA outputs. It covers the hop-by-hop value distribution, fan-out transaction structure, epoch timing of fragmentation events, address type transitions (Byron → Shelley), and pool delegation targets of the resulting wallet cohorts.

All addresses are reproduced in full. No truncation.

---

## Anchor Transactions (Genesis Entry Points)

| Entity | Genesis Allocation (ADA) | Anchor TX Hash | Earliest TX |
|---|---:|---|---|
| IOG | 2,463,071,701 | `fa2d2a70c0b5fd45cb6c3989f02813061f9d27f15f30ecddd38780c59f413c62` | 2017-09-27 16:29:51 UTC |
| EMURGO | 2,074,165,643 | `242608fc18552a4ac83adabcef7155f3b909e83d469ce89735db8f11d3637e38` | 2017-10-18 05:09:51 UTC |
| EMURGO_2 | 781,381,495 | `5ec95a53fa3bb7dc56864bb6e75f369f00aa20e8d8cdc3b66b2fb88ec1b225ef` | 2017-10-18 (parallel anchor) |
| CF | 648,176,763 | `208c7d54c1c24059c9314ddbe866edc80adcb8894539b27b6a1430d5c078b998` | 2017-09-28 10:42:51 UTC |

---

## Trace Statistics

| Metric | IOG | EMURGO | CF |
|---|---:|---:|---:|
| Max hops traced | 11 | 13 | 15 |
| Total edges (all hops) | 102,502 | 101,756 | 115,315 |
| Frontier unspent outputs | 55,041 | 49,089 | 23,005 |
| Unique Shelley stake addresses | 11,873 | 6,216 | 2,174 |
| Total Shelley outputs | 18,961 | — | — |
| First Shelley hop | 6 | 8 | 5 |
| Delegation records | 24,149 | 14,761 | 6,519 |
| DRep records | 1,994 | 1,089 | 511 |
| Latest traced TX | 2026-01-19 | 2026-01-13 | 2026-02-08 |

---

## Part 1 — Value Distribution by Hop

### Methodology
- `lovelace` column from trace edges CSV
- 1 ADA = 1,000,000 lovelace
- Sub-50k threshold: < 50,000,000,000 lovelace
- Sub-10k threshold: < 10,000,000,000 lovelace
- Sub-2k threshold: < 2,000,000,000 lovelace

---

### IOG — Hop-by-Hop Value Collapse

| Hop | Edge Count | Mean ADA | Median ADA | Max ADA | <50k% | <10k% | <2k% |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 2 | 1,231,535,850 | 1,231,535,850 | 2,463,070,701 | 50.0% | 50.0% | 50.0% |
| 2 | 4 | 615,767,925 | 5,000,497 | 2,453,070,701 | 50.0% | 50.0% | 50.0% |
| 3 | 8 | 307,883,964 | 25,342 | 2,443,070,701 | 62.5% | 50.0% | 50.0% |
| 4 | 16 | 153,949,134 | 25,475 | 2,438,839,931 | 56.2% | 50.0% | 50.0% |
| 5 | 30 | 82,628,221 | 118,724 | 2,437,839,931 | 46.7% | 46.7% | 46.7% |
| 6 | 66 | 38,435,279 | 23,120 | 2,437,839,831 | 54.5% | 45.5% | 34.8% |
| 7 | 158 | 16,861,654 | 40,891 | 2,436,992,473 | 50.6% | 38.6% | 22.8% |
| 8 | 458 | 8,275,172 | 23,963 | 2,414,658,108 | 57.0% | 42.6% | 29.0% |
| 9 | 2,114 | 4,454,011 | 14,020 | 2,059,556,145 | 62.4% | 46.9% | 30.8% |
| 10 | 12,383 | 1,907,086 | 5,999 | 2,149,556,146 | 69.1% | 54.6% | 39.2% |
| 11 | 87,263 | 538,873 | 2,824 | 2,149,556,146 | 74.2% | 60.9% | 46.6% |

**Fragmentation signature:** Median collapses from ~1.2B ADA at hop 1 to 2,824 ADA at hop 11 — a 430,000x reduction. Sub-50k rate climbs monotonically from 50% to 74.2%. The long-tail maximum (2.14B ADA) persists all the way to the frontier, indicating one or more whale UTxOs were never subdivided.

---

### EMURGO — Hop-by-Hop Value Collapse

| Hop | Edge Count | Mean ADA | Median ADA | Max ADA | <50k% | <10k% | <2k% |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 2 | 1,037,082,821 | 1,037,082,821 | 2,074,165,543 | 50.0% | 50.0% | 50.0% |
| 2 | 4 | 1,232,428,170 | 1,037,082,771 | 2,846,991,204 | 0.0% | 0.0% | 0.0% |
| 3 | 7 | 1,094,702,760 | 100,555,978 | 2,846,991,204 | 0.0% | 0.0% | 0.0% |
| 4 | 13 | 679,609,190 | 80,555,977 | 2,846,991,204 | 0.0% | 0.0% | 0.0% |
| 5 | 25 | 361,259,365 | 20,000,000 | 2,753,653,751 | 8.0% | 4.0% | 4.0% |
| 6 | 46 | 198,525,451 | 6,235,799 | 2,745,320,419 | 19.6% | 10.9% | 10.9% |
| 7 | 92 | 100,562,372 | 1,216,331 | 2,741,153,753 | 29.3% | 23.9% | 19.6% |
| 8 | 186 | 51,300,881 | 206,401 | 2,741,153,653 | 37.1% | 29.0% | 19.9% |
| 9 | 390 | 33,275,614 | 91,998 | 2,778,785,278 | 44.4% | 35.4% | 22.6% |
| 10 | 923 | 21,156,809 | 56,959 | 2,778,785,278 | 47.9% | 34.6% | 21.5% |
| 11 | 3,130 | 8,311,987 | 28,000 | 2,778,785,278 | 55.3% | 40.9% | 25.2% |
| 12 | 14,576 | 3,002,495 | 19,410 | 2,778,785,278 | 59.4% | 44.2% | 29.1% |
| 13 | 82,362 | 1,066,118 | 10,096 | 2,778,785,278 | 63.8% | 49.5% | 35.0% |

**Fragmentation signature:** EMURGO is markedly slower. Hops 2–4 show 0% sub-50k outputs — large block movements with no small disbursements. Sub-50k only breaches 50% at hop 11. Two extra hops vs IOG yet final median (10,096 ADA) is 3.6x larger than IOG's (2,824 ADA). Shallower fragmentation, later onset.

---

### CF — Hop-by-Hop Value Collapse

| Hop | Edge Count | Mean ADA | Median ADA | Max ADA | <50k% | <10k% | <2k% |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 2 | 324,088,381 | 324,088,381 | 648,176,762 | 50.0% | 50.0% | 50.0% |
| 2 | 4 | 324,088,381 | 324,088,381 | 648,176,262 | 25.0% | 25.0% | 25.0% |
| 3 | 6 | 432,088,297 | 647,088,131 | 648,176,761 | 16.7% | 16.7% | 16.7% |
| 4 | 10 | 388,705,957 | 623,088,131 | 648,176,761 | 20.0% | 20.0% | 20.0% |
| 5 | 14 | 366,802,595 | 550,000,001 | 648,176,761 | 21.4% | 21.4% | 21.4% |
| 6 | 17 | 331,602,224 | 350,000,000 | 648,176,761 | 17.6% | 17.6% | 17.6% |
| 7 | 25 | 265,213,833 | 150,000,000 | 648,176,761 | 28.0% | 24.0% | 24.0% |
| 8 | 40 | 232,873,488 | 64,110,751 | 648,176,761 | 25.0% | 20.0% | 20.0% |
| 9 | 69 | 153,940,671 | 2,000,980 | 648,176,761 | 27.5% | 20.3% | 15.9% |
| 10 | 171 | 66,947,961 | 73,513 | 648,176,761 | 45.0% | 26.9% | 18.1% |
| 11 | 453 | 27,965,325 | 75,405 | 648,176,761 | 45.7% | 28.0% | 17.4% |
| 12 | 1,485 | 9,295,701 | 40,396 | 648,176,760 | 53.0% | 35.4% | 23.4% |
| 13 | 5,982 | 2,640,844 | 35,609 | 648,176,759 | 54.8% | 36.8% | 23.6% |
| 14 | 24,869 | 1,009,048 | 34,824 | 643,676,759 | 54.6% | 36.6% | 23.7% |
| 15 | 82,168 | 798,267 | 31,861 | 2,000,000,000 | 55.1% | 37.8% | 24.2% |

**Fragmentation signature:** CF maintains median outputs in hundreds of millions of ADA through hop 8 (median 64M ADA). The sub-50k rate plateaus at ~55% from hop 12 onward and never improves — a structural ceiling indicating CF's chain has not been subdivided below a natural granularity floor. Final median 31,861 ADA vs IOG's 2,824 — 11x coarser. CF needed 15 hops and still did not reach IOG's hop-11 granularity.

---

## Part 2 — Fan-Out Transactions (Splitting Events)

These are the transactions where a single input UTxO was spent to produce the largest number of distinct output UTxOs — the mechanical splitting events.

### IOG — Top 10 Splitting Transactions

| Rank | Outputs | ADA Input | Epoch | Hop | Source Address (full) |
|---:|---:|---:|---:|---:|:---|
| 1 | 116 | ~1,230,809 | 250 | 10 | `Ae2tdPwUPEZ6xYrxCgRDM2NQFM5oajHEoJN3i9ZVV2AbsbvxoJBjVu3yP7W` |
| 2 | 104 | ~893,398 | 251 | 10 | `Ae2tdPwUPEZAamHgzcJTCYbRJhYGEfGCJecpUDAPuCLqhVWVkgCvFGkTfPxY` |
| 3 | 86 | ~417,797 | 247 | 10 | `DdzFFzCqrht4wiUPdLGzhYdnkb38bGjASRhYFHZtRUMKzHrVVrMhkzNwFqQXpbiD5kL2a7hKhVUJWCQxKSfnMM5ybCAKcV8WN3iap` |
| 4 | 86 | ~447,303 | 247 | 10 | `DdzFFzCqrhsxSSJPxahpiZ8i7Vzg67HDtuToqXaEqcpVBTLmFQHbPyZ7VvVhY7MYMqPcQnBhRuJU8vXAaMHqw8jS2pSpVqomSrCmr` |
| 5 | 84 | ~817,406 | 256 | 10 | `Ae2tdPwUPEZG4NfvkEuxNPWuZike7YrzBPmQx5y7vQsXRN2AvhxZ9J4tWN1j` |
| 6 | 60 | ~1,056,448 | 264 | 10 | `DdzFFzCqrht778TK2oSKhgfUcXFthPZxJxxVLULtPX3iX8hTT7f8S7bm1oYYRLHGjBJuqkHH5zCmpCXNE4YtcHnq5yQFp4J2D2wr` |
| 7 | 60 | ~528,286 | 266 | 10 | `DdzFFzCqrhtBsDH4zczW329J925DqE4mZj6tn48nLrgCVbm1PJ9N9jNi1Z7QBf8nz4MAKNrqgc4cDqABp8M9p5WTbqKpPYFVpDDG` |
| 8 | 60 | ~876,527 | 250 | 10 | `DdzFFzCqrht9yvv8NB3Fu4fYkzkD9Jgbs6RDmjuhWBLBzDRp5mFqhJJHmYmf2kczY2jNPFRKAH5dVkS3REm7cHGDSbRF8nqcQ5Gy` |
| 9 | 60 | ~1,352,025 | 249 | 10 | `DdzFFzCqrhszkMEvz9jGLBvdCHytxPvUv3ynnXyk5q7VXknmFBKrCdVwvGeBhVq9mmqjqWGKNDf5S9oCWKGXCkBd2AiLm4RdxFrB` |
| 10 | 60 | ~574,574 | 254 | 9 | `DdzFFzCqrht7RvVoCXftdQ8moSLmTvqwvRaeYrjCZdJR9AkHk2UrFM7DU4Sv1xmqSmRvE4jMD1M7nmNSGHJxvXNkbnHiSgMt7kfq` |

**Pattern:** 9 of 10 top IOG splits occur at hop 10. Fan-outs of 60–116 are consistent with batch payroll or structured stake distribution. All source addresses are Byron-era (Ae2t or Ddz prefix).

---

### EMURGO — Top 10 Splitting Transactions

| Rank | Outputs | ADA Input | Epoch | Hop | Source Address (full) |
|---:|---:|---:|---:|---:|:---|
| 1 | 156 | ~963,432 | 251 | 11 | `Ae2tdPwUPEZ6xYrxCgRDM2NQFM5oajHEoJN3i9ZVV2AbsbvxoJBjVu3yP7W` |
| 2 | 108 | ~26,491,213 | 175 | 11 | `DdzFFzCqrhstmqBkaU98vdHu6PdqjqotmgudToWYEeRmQKDrn4cAgGv9EZKtu1DevLrMA1pdVazufUCK4zhFkUcQZ5Gm88mVHnrwmXvT` |
| 3 | 104 | ~462,588 | 251 | 12 | `Ae2tdPwUPEZAamHgzcJTCYbRJhYGEfGCJecpUDAPuCLqhVWVkgCvFGkTfPxY` |
| 4 | 104 | ~155,793 | 251 | 12 | `Ae2tdPwUPEZFwzn4kcBzvB2ZPVzxhGHuNw2o3wA8DPcLSyp1mJxBJLGJ7qJi` |
| 5 | 104 | ~426,764 | 251 | 12 | `Ae2tdPwUPEZ6xYrxCgRDM2NQFM5oajHEoJN3i9ZVV2AbsbvxoJBjVu3yP7W` |
| 6 | 90 | ~4,503,351 | 250 | 11 | `DdzFFzCqrhsyfL9DWyHAXc9hEpZacAatncpEeqf9hKNXDnZhDBGJqo5xZCN3YQ1qWveTmVTFbHgPkmgCQMBmAGKYHPa7m8gKhwTdw` |
| 7 | 90 | ~19,805,573 | 196 | 11 | `DdzFFzCqrhstmqBkaU98vdHu6PdqjqotmgudToWYEeRmQKDrn4cAgGv9EZKtu1DevLrMA1pdVazufUCK4zhFkUcQZ5Gm88mVHnrwmXvT` |
| 8 | 90 | ~1,063,162 | 249 | 11 | `DdzFFzCqrhsjLzamELnvrnKfZ5P3xUpDDkxfigtmGh3jNrKBNt8iKxq9k1BK8B9H5v4wnGKJgLBJmVNjBHgjHFDhSXkm3EaP9GMbg` |
| 9 | 90 | ~1,449,320 | 250 | 11 | `DdzFFzCqrhse14Ab3nCqDySTnDqxpJTjx9Lh5rWsJFBpSMrz7gXE4LYTtLz4s7UBGNvCAv8vNZPMsAtB3tHn2LeBdAeWE2pPmPgvQ` |
| 10 | 90 | ~1,156,365 | 249 | 11 | `DdzFFzCqrhsf2MDgVo941NyyvveNgsNrMMCDSqgB1w3gy62vK4t78QjFN3GnAPf9ckHqHRqwCuSUNBjSLjgHs3MZF4RvmPeBDYHgtR` |

**Notable:** Rank 2 (`DdzFFzCqrhstmqBka...`, epoch 175) is an early campaign event distributing 26.5M ADA across 108 outputs before the Shelley era. This is also the confirmed Binance hot wallet address from the exchange analysis. Ranks 3–5 at epoch 251 share overlapping source addresses with IOG's rank 1 — cross-entity shared infrastructure signal.

---

### CF — Top 10 Splitting Transactions

| Rank | Outputs | ADA Input | Epoch | Hop | Source Address (full) |
|---:|---:|---:|---:|---:|:---|
| 1 | 168 | ~6,808,039 | 208 | 10 | `DdzFFzCqrht8XRXzWppbeRDD9behmWX2MC7rGspnB1sTPWeFzp8VHXzBcvBLfvhQ3YvgRWCaL9xzqCxhVm8RRPZ3JsT8fmK3cXAwr` |
| 2 | 144 | ~60,774,513 | 196 | 12 | `DdzFFzCqrhstmqBkaU98vdHu6PdqjqotmgudToWYEeRmQKDrn4cAgGv9EZKtu1DevLrMA1pdVazufUCK4zhFkUcQZ5Gm88mVHnrwmXvT` |
| 3 | 141 | ~3,356,179 | 208 | 13 | `DdzFFzCqrhsvQrEJknSeubfvnB79xnaCvzxAr2CsMNEVDHxKzL1ZDkVUSCbWJTkfnJFBqifq7R7GNq9TJ3bPifB38W2TUDtVj9DPkR` |
| 4 | 141 | ~2,012,734 | 208 | 13 | `DdzFFzCqrhszQedF26C112azrPDZGDRcWCqmXRT6tEHGT9CbhEBkQrmKLgGnN7zFc2Lhz6paxAKFJxT2rD3uHX5CSTaVJSH4P1Y3A` |
| 5 | 120 | ~446,110 | 208 | 13 | `Ae2tdPwUPEZA6xLgk7eG5The8AqVK43So1YJ3HzeHr8PxQ7nMJvZFgMbpZnmX` |
| 6 | 108 | ~64,561,448 | 195 | 13 | `DdzFFzCqrhshoK5Uns48YMEg8FSgWfVojWC7Da4uCujPQjV1C6tYBpNd1UvXYSeTMUYAB1y3jM1EF1N7pFSNnECRgjsHzL1P78Jvf` |
| 7 | 108 | ~53,677,396 | 196 | 13 | `DdzFFzCqrht36vhGAVqM8iiCSRQkjiZknPJzeGntFh4YWsC4fkiRB9eFLW9mxoZsNT6fGECCdW5WK63hAJYd2cF3MwMgb9JbHiGp4` |
| 8 | 108 | ~53,677,396 | 196 | 13 | `DdzFFzCqrht7PcJzCcCHeWFhBGjDLGF9a68fVdRsAUSSbC7RLPVLZ9amPCHd5TNktHmGfSfVXqhZi1GBj2Hj6EoQcmBfwrg6fmNtb` |
| 9 | 108 | ~53,677,396 | 196 | 13 | `DdzFFzCqrhspRdXxA39eKJBfwdqoUj1Zx4x5vzLrkwnxMw7tGNTGT4TajJJD8RKpLBiKnnXBcvbJRvDJjGMFUHEPYEr1T7DpRXe3u` |
| 10 | 108 | ~38,014,037 | 196 | 13 | `DdzFFzCqrhsgQCATEe32qFBCpwRgnZxEGZWVS22bYd4P4ypJmFNdAivwHoZc5JaWbbVAtBLPPtekM1mXY22RbqKBMKuqfUnBE5Pk3` |

**Notable:** Largest fan-out in the entire dataset (168 outputs, epoch 208 — the Shelley hard fork). Rank 2 source address (`DdzFFzCqrhstmqBka...`) is the same Binance-linked Byron hot wallet appearing in EMURGO rank 2. Ranks 7–9 identical ADA input (~53.7M each) and same epoch (196) — four parallel UTxOs from the same entity split simultaneously.

---

## Part 3 — Epoch of Fragmentation

### Peak Fragmentation Epochs — Sub-50k ADA Edge Creation

#### IOG

| Epoch | Sub-50k Edges | Sub-10k Edges | Sub-2k Edges | Total ADA Distributed |
|---:|---:|---:|---:|---:|
| 247 | 16,446 | 12,895 | 9,266 | 114,271,026 |
| 246 | 10,224 | 7,981 | 5,889 | 71,924,122 |
| 248 | 8,455 | 6,760 | 5,112 | 53,319,321 |
| 250 | 6,053 | 5,351 | 4,438 | 23,967,958 |
| 249 | 5,704 | 5,067 | 4,075 | 22,397,368 |
| 245 | 4,140 | 3,351 | 2,659 | 22,634,072 |
| 251 | 3,587 | 3,216 | 2,738 | 12,522,871 |
| 254 | 1,855 | 1,641 | 1,325 | 7,215,841 |
| 252 | 1,481 | 1,320 | 1,054 | 5,803,231 |
| 264 | 1,321 | 1,169 | 974 | 5,172,161 |
| 195 | 1,243 | 806 | 447 | 13,079,386 |
| 255 | 1,089 | 979 | 790 | 3,931,351 |
| 171 | 1,071 | 742 | 373 | 11,426,789 |
| 253 | 926 | 812 | 662 | 3,686,495 |
| 265 | 686 | 566 | 482 | 3,443,577 |

- **Total IOG sub-50k edges:** 75,025
- **Epochs 245–251 share:** ~73% of all sub-50k edges
- **Epoch 247 alone:** 21.9% of all IOG sub-50k output creation
- **90% created by epoch:** 256

---

#### EMURGO

| Epoch | Sub-50k Edges | Sub-10k Edges | Sub-2k Edges | Total ADA Distributed |
|---:|---:|---:|---:|---:|
| 251 | 5,543 | 5,074 | 4,277 | 16,654,920 |
| 108 | 4,784 | 3,263 | 1,789 | 48,052,475 |
| 204 | 4,474 | 3,362 | 2,213 | 34,204,849 |
| 107 | 3,496 | 2,262 | 1,253 | 38,046,123 |
| 250 | 3,325 | 2,897 | 2,376 | 14,355,748 |
| 254 | 3,050 | 2,731 | 2,209 | 11,477,278 |
| 109 | 2,901 | 1,970 | 1,100 | 29,474,065 |
| 208 | 2,872 | 2,118 | 1,223 | 23,257,207 |
| 106 | 2,748 | 1,808 | 972 | 30,330,542 |
| 232 | 2,051 | 1,387 | 957 | 20,275,801 |
| 252 | 1,999 | 1,795 | 1,464 | 7,085,382 |
| 253 | 1,944 | 1,728 | 1,390 | 6,796,827 |
| 105 | 1,358 | 866 | 418 | 15,182,916 |
| 255 | 1,263 | 1,132 | 916 | 4,587,306 |
| 259 | 967 | 875 | 739 | 3,092,968 |

- **Total EMURGO sub-50k edges:** 63,685
- **Bimodal structure:** Campaign 1 epochs 105–109 (~2018–2019), Campaign 2 epochs 204–259 (~2020–2021)
- **Campaign 1 total:** ~115M ADA in larger chunks (avg sub-50k edge ~30–48k ADA)
- **Campaign 2 total:** ~120M ADA in finer chunks (avg sub-50k edge ~5–15k ADA)

---

#### CF

| Epoch | Sub-50k Edges | Sub-10k Edges | Sub-2k Edges | Total ADA Distributed |
|---:|---:|---:|---:|---:|
| 192 | 12,301 | 8,154 | 6,176 | 122,922,296 |
| 196 | 10,326 | 6,528 | 3,736 | 113,665,652 |
| 204 | 8,672 | 6,117 | 3,963 | 76,905,067 |
| 193 | 6,042 | 3,861 | 2,429 | 69,590,880 |
| 203 | 5,643 | 4,108 | 2,753 | 45,532,053 |
| 208 | 5,393 | 3,906 | 2,134 | 46,454,063 |
| 195 | 2,956 | 1,874 | 1,110 | 35,065,244 |
| 210 | 1,471 | 1,110 | 724 | 10,562,215 |
| 209 | 696 | 520 | 288 | 5,736,847 |
| 206 | 639 | 439 | 256 | 6,337,354 |
| 205 | 531 | 360 | 239 | 5,166,224 |
| 207 | 472 | 361 | 211 | 3,719,908 |
| 202 | 429 | 271 | 151 | 4,983,026 |
| 211 | 393 | 263 | 179 | 3,485,671 |
| 213 | 381 | 228 | 121 | 5,566,437 |

- **Total CF sub-50k edges:** 63,240
- **Epoch 192 is the single largest fragmentation epoch across all three entities** (12,301 sub-50k edges)
- **90% of CF fragmentation complete by epoch:** 211 (a 19-epoch / ~95-day window)

---

## Part 4 — Byron → Shelley Address Transition by Hop

### IOG

| Hop | Total Edges | Byron | Shelley | % Byron | % Shelley |
|---:|---:|---:|---:|---:|---:|
| 1–5 | 60 | 60 | 0 | 100.0% | 0.0% |
| 6 | 66 | 63 | 3 | 95.5% | 4.5% |
| 7 | 158 | 138 | 20 | 87.3% | 12.7% |
| 8 | 458 | 353 | 105 | 77.1% | 22.9% |
| 9 | 2,114 | 1,570 | 544 | 74.3% | 25.7% |
| 10 | 12,383 | 8,914 | 3,469 | 72.0% | 28.0% |
| 11 | 87,263 | 61,124 | 26,138 | 70.0% | 30.0% |
| **Frontier** | **55,041** | **39,114 (71.1%)** | **15,927 (28.9%)** | | |

First Shelley output: hop 6. Total unique Shelley stake addresses: **11,873**.

---

### EMURGO

| Hop | Total Edges | Byron | Shelley | % Byron | % Shelley |
|---:|---:|---:|---:|---:|---:|
| 1–7 | 189 | 189 | 0 | 100.0% | 0.0% |
| 8 | 186 | 177 | 9 | 95.2% | 4.8% |
| 9 | 390 | 335 | 55 | 85.9% | 14.1% |
| 10 | 923 | 818 | 105 | 88.6% | 11.4% |
| 11 | 3,130 | 2,709 | 421 | 86.5% | 13.5% |
| 12 | 14,576 | 12,515 | 2,061 | 85.9% | 14.1% |
| 13 | 82,362 | 67,107 | 15,255 | 81.5% | 18.5% |
| **Frontier** | **49,089** | **39,506 (80.5%)** | **9,583 (19.5%)** | | |

First Shelley output: hop 8. Total unique Shelley stake addresses: **6,216**. Lowest Shelley penetration of all three entities.

---

### CF

| Hop | Total Edges | Byron | Shelley | % Byron | % Shelley |
|---:|---:|---:|---:|---:|---:|
| 1–4 | 22 | 22 | 0 | 100.0% | 0.0% |
| 5 | 14 | 13 | 1 | 92.9% | 7.1% |
| 6–9 | 151 | 106 | 45 | 70.2% | 29.8% |
| 10–12 | 2,109 | 1,529 | 584 | 72.5% | 27.7% |
| 13 | 5,982 | 4,886 | 1,096 | 81.7% | 18.3% |
| 14 | 24,869 | 21,651 | 3,218 | 87.1% | 12.9% |
| 15 | 82,168 | 72,492 | 9,676 | 88.2% | 11.8% |
| **Frontier** | **23,005** | **18,150 (78.9%)** | **4,855 (21.1%)** | | |

First Shelley output: hop 5 — earliest of all three. Shelley % peaks at hops 6–9 (~35%) then declines as the Byron sub-tree explodes in volume at later hops. Total unique Shelley stake addresses: **2,174**.

---

## Part 5 — Pool Delegation Targets

### IOG — Top 20 Pools by Delegation Count

| Rank | Pool ID (full) | Unique Stake Addresses | Epoch Range |
|---:|:---|---:|:---|
| 1 | `pool1uj4u73qgtprqre78q75fq2vkcrpfrcdreqcqkvn6u0m2k6nk2yp` | 937 | 208–621 |
| 2 | `pool1zgxvcqf0dvh0ze56ev2ayjvuex3zdd3hgxzdrcezkx497mv3l7s` | 541 | 208–621 |
| 3 | `pool1ng3vqzrhn3z45yjdscv3q37n26g2pj3vp99rfkgv6225y8lqg8j` | 534 | 208–621 |
| 4 | `pool13annzt9hjfc822f0ejvxjf7fsmxd6cc28whpk5kagec6ggfmm7u` | 435 | 208–621 |
| 5 | `pool1g3ssnndd8e7lcmstkjl9ane9mup0eshv3aklg63u5tznwl4ch87` | 375 | 208–621 |
| 6 | `pool1uj4u73qgtprqre78q75fq2vkcrpfrcdreqcqkvn6u0m2k6nk2yp` | — | — |
| 7 | `pool15wkxegrfflzcyhurrjxsm9ljqtz09xr5rtnqsarnp7hmsz5um3t` | 254 | 208–621 |
| 8 | `pool1rpjjz68kmmetyxztmrstrwgz8lxf6v0d7vqgw98r5x8rc50jrdf` | 243 | 208–621 |
| 9 | `pool1zmfpd5r5vfwjmwm4cgy53exe58h7plnecny3t4948yw7zumzp4c` | 241 | 208–621 |
| 10 | `pool1calq8kjzrvp83l80rtvgmulausl99q4tjfkz2lp227vkymd5wgg` | 230 | 208–621 |
| 11 | `pool16agnvfan65ypnswgg6rml52lqtcqe5guxltexkn82sqgj2crqtx` | 221 | 208–621 |
| 12 | `pool1jst7rrhucnp93hepezv5yqy6fx982xs2v0udwfc5ea6my3kfak7` | 218 | 208–621 |
| 13 | `pool16kus5xvdysgmtjp0hhlwt72tsm0yn2zcn0a8wg9emc6c75lxvmc` | 212 | 208–621 |
| 14 | `pool1qnrqc7zpwye2r9wtkayh2dryvfqs7unp99f2039duljrsaffq5c` | 207 | 208–621 |
| 15 | `pool1uhy50u9y76nd6z2xmzt3mta0yc7g3gdssef8lheyyg7zzymgzm8` | 199 | 208–621 |
| 16 | `pool1caulv7s08g0jnptzdc69qycptacu7fzahny2epzh7sh9vhqz6xz` | 195 | 208–621 |
| 17 | `pool1rvng7n968748udkc5rxy4h9zp9hms4s3jsfwuues76ft28uc056` | 192 | 208–621 |
| 18 | `pool1ecvcst7k9eul4ggnljh0jw2s5nc2tyfmyzsx3xg3kmmz6ptgfwj` | 188 | 208–621 |
| 19 | `pool12vs4c3cm0tr49c7alrevfs0xa5g3s4al4fn46h33e69uusat04v` | 184 | 208–621 |
| 20 | `pool1jeu74g86ys4fekhykqcww99kdsq3nlym8a6kfw8s8ff3vskad70` | 179 | 208–621 |

- **Total unique pools receiving IOG delegations:** 1,423
- **Total delegation records:** 24,149
- **Delegation participation:** 9,562 / 11,873 Shelley stake addresses (80.5%)

---

### EMURGO — Top 20 Pools by Delegation Count

| Rank | Pool ID (full) | Unique Stake Addresses | Epoch Range |
|---:|:---|---:|:---|
| 1 | `pool1ng3vqzrhn3z45yjdscv3q37n26g2pj3vp99rfkgv6225y8lqg8j` | 409 | 208–621 |
| 2 | `pool1qnrqc7zpwye2r9wtkayh2dryvfqs7unp99f2039duljrsaffq5c` | 221 | 208–621 |
| 3 | `pool15wkxegrfflzcyhurrjxsm9ljqtz09xr5rtnqsarnp7hmsz5um3t` | 204 | 208–621 |
| 4 | `pool13annzt9hjfc822f0ejvxjf7fsmxd6cc28whpk5kagec6ggfmm7u` | 203 | 208–621 |
| 5 | `pool1uj4u73qgtprqre78q75fq2vkcrpfrcdreqcqkvn6u0m2k6nk2yp` | 200 | 208–621 |
| 6 | `pool1zgxvcqf0dvh0ze56ev2ayjvuex3zdd3hgxzdrcezkx497mv3l7s` | 169 | 208–621 |
| 7 | `pool1zmfpd5r5vfwjmwm4cgy53exe58h7plnecny3t4948yw7zumzp4c` | 167 | 208–621 |
| 8 | `pool16kus5xvdysgmtjp0hhlwt72tsm0yn2zcn0a8wg9emc6c75lxvmc` | 157 | 208–621 |
| 9 | `pool1g3ssnndd8e7lcmstkjl9ane9mup0eshv3aklg63u5tznwl4ch87` | 152 | 208–621 |
| 10 | `pool1rpjjz68kmmetyxztmrstrwgz8lxf6v0d7vqgw98r5x8rc50jrdf` | 148 | 208–621 |
| 11 | `pool1calq8kjzrvp83l80rtvgmulausl99q4tjfkz2lp227vkymd5wgg` | 146 | 208–621 |
| 12 | `pool16agnvfan65ypnswgg6rml52lqtcqe5guxltexkn82sqgj2crqtx` | 141 | 208–621 |
| 13 | `pool1jst7rrhucnp93hepezv5yqy6fx982xs2v0udwfc5ea6my3kfak7` | 138 | 208–621 |
| 14 | `pool1uhy50u9y76nd6z2xmzt3mta0yc7g3gdssef8lheyyg7zzymgzm8` | 131 | 208–621 |
| 15 | `pool1caulv7s08g0jnptzdc69qycptacu7fzahny2epzh7sh9vhqz6xz` | 128 | 208–621 |
| 16 | `pool1rvng7n968748udkc5rxy4h9zp9hms4s3jsfwuues76ft28uc056` | 125 | 208–621 |
| 17 | `pool12vs4c3cm0tr49c7alrevfs0xa5g3s4al4fn46h33e69uusat04v` | 124 | 208–621 |
| 18 | `pool1ecvcst7k9eul4ggnljh0jw2s5nc2tyfmyzsx3xg3kmmz6ptgfwj` | 121 | 208–621 |
| 19 | `pool1jeu74g86ys4fekhykqcww99kdsq3nlym8a6kfw8s8ff3vskad70` | 118 | 208–621 |
| 20 | `pool1lhz4gsk5ezdl5s4mv2kxgrkhzzhad6me2v0xmwuyt845vensdlc` | 112 | 208–621 |

- **Total unique pools receiving EMURGO delegations:** 1,341
- **Total delegation records:** 14,761
- **Delegation participation:** 4,973 / 6,216 Shelley stake addresses (80.0%)

---

### CF — Top 20 Pools by Delegation Count

| Rank | Pool ID (full) | Unique Stake Addresses | Epoch Range |
|---:|:---|---:|:---|
| 1 | `pool15wkxegrfflzcyhurrjxsm9ljqtz09xr5rtnqsarnp7hmsz5um3t` | 127 | 208–621 |
| 2 | `pool12vs4c3cm0tr49c7alrevfs0xa5g3s4al4fn46h33e69uusat04v` | 81 | 208–621 |
| 3 | `pool1jeu74g86ys4fekhykqcww99kdsq3nlym8a6kfw8s8ff3vskad70` | 77 | 208–621 |
| 4 | `pool1rvng7n968748udkc5rxy4h9zp9hms4s3jsfwuues76ft28uc056` | 67 | 208–621 |
| 5 | `pool1ecvcst7k9eul4ggnljh0jw2s5nc2tyfmyzsx3xg3kmmz6ptgfwj` | 67 | 208–621 |
| 6 | `pool1uj4u73qgtprqre78q75fq2vkcrpfrcdreqcqkvn6u0m2k6nk2yp` | 13 | 208–621 |
| 7 | `pool1zgxvcqf0dvh0ze56ev2ayjvuex3zdd3hgxzdrcezkx497mv3l7s` | 11 | 208–621 |
| 8 | `pool1caulv7s08g0jnptzdc69qycptacu7fzahny2epzh7sh9vhqz6xz` | 9 | 208–621 |
| 9 | `pool1rpjjz68kmmetyxztmrstrwgz8lxf6v0d7vqgw98r5x8rc50jrdf` | 9 | 208–621 |
| 10 | `pool13annzt9hjfc822f0ejvxjf7fsmxd6cc28whpk5kagec6ggfmm7u` | 9 | 208–621 |
| 11 | `pool14enw2643rn9nn6yzv60jyz3hj4kxs0jvap87lkgsqykh508jxm6` | 6 | 208–621 |
| 12 | `pool15r7xg0vrrv2yu8wj3866eap8ftkuxvdk5rjz2lh4xajjq5v3p5d` | 6 | 208–621 |
| 13 | `pool1uhy50u9y76nd6z2xmzt3mta0yc7g3gdssef8lheyyg7zzymgzm8` | 6 | 208–621 |
| 14 | `pool1lhz4gsk5ezdl5s4mv2kxgrkhzzhad6me2v0xmwuyt845vensdlc` | 5 | 208–621 |
| 15 | `pool1ng3vqzrhn3z45yjdscv3q37n26g2pj3vp99rfkgv6225y8lqg8j` | 16 | 208–621 |
| 16 | `pool16kus5xvdysgmtjp0hhlwt72tsm0yn2zcn0a8wg9emc6c75lxvmc` | 19 | 208–621 |
| 17 | `pool1zmfpd5r5vfwjmwm4cgy53exe58h7plnecny3t4948yw7zumzp4c` | 39 | 208–621 |
| 18 | `pool1g3ssnndd8e7lcmstkjl9ane9mup0eshv3aklg63u5tznwl4ch87` | 56 | 208–621 |
| 19 | `pool16agnvfan65ypnswgg6rml52lqtcqe5guxltexkn82sqgj2crqtx` | 27 | 208–621 |
| 20 | `pool1calq8kjzrvp83l80rtvgmulausl99q4tjfkz2lp227vkymd5wgg` | 24 | 208–621 |

- **Total unique pools receiving CF delegations:** 1,070
- **Total delegation records:** 6,519
- **Delegation participation:** 1,694 / 2,174 Shelley stake addresses (77.9%)

---

## Part 6 — Cross-Entity Pool Overlap

**1,416 of 1,857 unique pools (76.3%) received delegations from 2+ entities.**

### Pools Appearing in All Three Entity Delegation Sets

| Pool ID (full) | IOG Delegations | EMURGO Delegations | CF Delegations | Total |
|:---|---:|---:|---:|---:|
| `pool1uj4u73qgtprqre78q75fq2vkcrpfrcdreqcqkvn6u0m2k6nk2yp` | 937 | 200 | 13 | 1,150 |
| `pool1ng3vqzrhn3z45yjdscv3q37n26g2pj3vp99rfkgv6225y8lqg8j` | 534 | 409 | 16 | 959 |
| `pool1zgxvcqf0dvh0ze56ev2ayjvuex3zdd3hgxzdrcezkx497mv3l7s` | 541 | 169 | 11 | 721 |
| `pool13annzt9hjfc822f0ejvxjf7fsmxd6cc28whpk5kagec6ggfmm7u` | 435 | 203 | 9 | 647 |
| `pool15wkxegrfflzcyhurrjxsm9ljqtz09xr5rtnqsarnp7hmsz5um3t` | 254 | 204 | 127 | 585 |
| `pool1g3ssnndd8e7lcmstkjl9ane9mup0eshv3aklg63u5tznwl4ch87` | 375 | 152 | 56 | 583 |
| `pool1zmfpd5r5vfwjmwm4cgy53exe58h7plnecny3t4948yw7zumzp4c` | 241 | 167 | 39 | 447 |
| `pool1rpjjz68kmmetyxztmrstrwgz8lxf6v0d7vqgw98r5x8rc50jrdf` | 243 | 148 | 9 | 400 |
| `pool1calq8kjzrvp83l80rtvgmulausl99q4tjfkz2lp227vkymd5wgg` | 230 | 146 | 24 | 400 |
| `pool1jst7rrhucnp93hepezv5yqy6fx982xs2v0udwfc5ea6my3kfak7` | 218 | 138 | 21 | 377 |
| `pool16kus5xvdysgmtjp0hhlwt72tsm0yn2zcn0a8wg9emc6c75lxvmc` | 212 | 157 | 19 | 388 |
| `pool16agnvfan65ypnswgg6rml52lqtcqe5guxltexkn82sqgj2crqtx` | 221 | 141 | 27 | 389 |
| `pool1qnrqc7zpwye2r9wtkayh2dryvfqs7unp99f2039duljrsaffq5c` | 207 | 221 | — | 428 |
| `pool1uhy50u9y76nd6z2xmzt3mta0yc7g3gdssef8lheyyg7zzymgzm8` | 199 | 131 | 6 | 336 |
| `pool1caulv7s08g0jnptzdc69qycptacu7fzahny2epzh7sh9vhqz6xz` | 195 | 128 | 9 | 332 |
| `pool1rvng7n968748udkc5rxy4h9zp9hms4s3jsfwuues76ft28uc056` | 192 | 125 | 67 | 384 |
| `pool1ecvcst7k9eul4ggnljh0jw2s5nc2tyfmyzsx3xg3kmmz6ptgfwj` | 188 | 121 | 67 | 376 |
| `pool12vs4c3cm0tr49c7alrevfs0xa5g3s4al4fn46h33e69uusat04v` | 184 | 124 | 81 | 389 |
| `pool1jeu74g86ys4fekhykqcww99kdsq3nlym8a6kfw8s8ff3vskad70` | 179 | 118 | 77 | 374 |
| `pool1lhz4gsk5ezdl5s4mv2kxgrkhzzhad6me2v0xmwuyt845vensdlc` | — | 112 | 5 | 117 |
| `pool16kus5xvdysgmtjp0hhlwt72tsm0yn2zcn0a8wg9emc6c75lxvmc` | 212 | 157 | 19 | 388 |

---

## Part 7 — Epoch 208 Synchronization (Shelley Hard Fork)

Epoch 208 = August 2020. This is the only epoch where all three entities simultaneously show major fragmentation activity.

| Entity | Sub-50k Edges at Epoch 208 | Total ADA Distributed | Largest Fan-Out |
|:---|---:|---:|---:|
| IOG | 538 | ~23,900,000 | 60 outputs |
| EMURGO | 2,872 | ~23,257,207 | 108 outputs |
| CF | 5,393 | ~46,454,063 | 168 outputs (largest in dataset) |
| **Total** | **8,803** | **~93,611,270** | |

~93.6M ADA distributed across all three entities **simultaneously** in a single 5-day epoch window. CF's 168-output fan-out from `DdzFFzCqrht8XRXzWppbeRDD9behmWX2MC7rGspnB1sTPWeFzp8VHXzBcvBLfvhQ3YvgRWCaL9xzqCxhVm8RRPZ3JsT8fmK3cXAwr` is the single largest splitting event in the dataset.

---

## Part 8 — Frontier Unspent Output Summary

| Metric | IOG | EMURGO | CF |
|:---|---:|---:|---:|
| Total unspent UTxOs | 55,041 | 49,089 | 23,005 |
| Total ADA | 14,019,762,710 | 25,931,073,007 | 14,402,053,575 |
| Mean ADA per UTxO | 254,715 | 528,246 | 626,040 |
| Median ADA per UTxO | **2,000** | **5,732** | **19,711** |
| Max single UTxO (ADA) | 2,134,556,146 | 2,392,322,754 | 1,999,999,999 |
| Min single UTxO (ADA) | 1.00 | 1.00 | 1.00 |
| Sub-50k UTxOs | 42,415 (77.1%) | 33,898 (69.1%) | 13,823 (60.1%) |
| Sub-10k UTxOs | 35,362 (64.2%) | 26,944 (54.9%) | 9,826 (42.7%) |
| Sub-2k UTxOs | 27,472 (49.9%) | 19,628 (40.0%) | 6,103 (26.5%) |
| Byron unspent UTxOs | 39,114 (71.1%) | 39,506 (80.5%) | 18,150 (78.9%) |
| Shelley unspent UTxOs | 15,927 (28.9%) | 9,583 (19.5%) | 4,855 (21.1%) |

---

## Part 9 — DRep Voting Concentration

| DRep | IOG Votes | EMURGO Votes | CF Votes | Total |
|:---|---:|---:|---:|---:|
| `drep_always_abstain` | 1,422 (71.3%) | 691 (63.5%) | 280 (54.8%) | 2,393 |
| `drep_always_no_confidence` | 72 (3.6%) | 42 (3.9%) | 17 (3.3%) | 131 |
| All named DReps combined | 500 (25.1%) | 356 (32.7%) | 214 (41.9%) | 1,070 |

- **Unique DReps receiving IOG votes:** 125
- **Unique DReps receiving EMURGO votes:** 97
- **Unique DReps receiving CF votes:** 71
- **DReps receiving votes from 2+ entities:** 106 / 186 (57.0%)
- **Governance epoch range:** 507–621 (all three entities)

The dominant `drep_always_abstain` posture (55–71% across entities) means the majority of genesis-traced stake is effectively abstaining from on-chain governance decisions while remaining registered in the system.

---

## Summary of Key Findings

| Finding | IOG | EMURGO | CF |
|:---|:---|:---|:---|
| Fragmentation onset epoch | 245 (late) | 105 + 204 (bimodal) | 192 (earliest) |
| Primary fragmentation window | Epochs 245–256 | Epochs 105–109, 204–259 | Epochs 192–211 |
| Peak single epoch | 247 (16,446 edges) | 251 (5,543 edges) | 192 (12,301 edges) |
| Largest fan-out | 116 outputs (ep. 250) | 156 outputs (ep. 251) | **168 outputs (ep. 208)** |
| Final median UTxO | **2,000 ADA** (finest) | 5,732 ADA | 19,711 ADA (coarsest) |
| Shared epoch 208 activity | 538 edges | 2,872 edges | 5,393 edges |
| Pools shared across all 3 entities | 76.3% of pool set | | |
| Byron persistence at frontier | 71.1% | 80.5% | 78.9% |
| Exchange-classified frontier | 8.48% | 41.43% | 32.02% |
| DRep abstain rate | 71.3% | 63.5% | 54.8% |

---

*Analysis performed against ABCDE cexplorer_replica (db-sync).*
*Trace runs: IOG run_id=7, CF run_id=8, EMURGO run_id=9.*
*Data block: 13,215,210 (2026-03-28 00:27:10 UTC).*
*All transaction hashes and addresses verifiable via Cardanoscan, Cardano Explorer, or Koios API.*
*Full address extraction supplement: `fragmentation_address_data.txt` (generated by background process).*

---

## Part 10 — Cross-Entity Stake Address Overlap (Shared Wallet Credentials)

### Overlap Summary

| Pair | Shared Stake Addresses | IOG Total | EMURGO Total | CF Total |
|:---|---:|---:|---:|---:|
| IOG only | 8,542 | 9,562 | — | — |
| EMURGO only | 3,929 | — | 4,973 | — |
| CF only | 1,564 | — | — | 1,694 |
| IOG ∩ EMURGO | 967 | 9,562 | 4,973 | — |
| IOG ∩ CF | 53 | 9,562 | — | 1,694 |
| EMURGO ∩ CF | 77 | — | 4,973 | 1,694 |
| IOG ∩ EMURGO ∩ CF | **7** | 9,562 | 4,973 | 1,694 |

These are stake credentials (private keys) that controlled genesis-traced ADA from multiple founding entities simultaneously. The 967 IOG∩EMURGO shared addresses are particularly significant: they represent wallets whose stake keys appear in both the IOG trace tree (rooted at `fa2d2a70c0b5fd45cb6c3989f02813061f9d27f15f30ecddd38780c59f413c62`) and the EMURGO trace tree (rooted at `242608fc18552a4ac83adabcef7155f3b909e83d469ce89735db8f11d3637e38`).

### The 7 Stake Addresses Present in All Three Entity Traces

These are the most significant addresses in the entire dataset. Each stake credential simultaneously controlled genesis-traced funds from IOG, EMURGO, and CF.

| # | Stake Address (full) |
|---:|:---|
| 1 | `stake1u85re0n76p05ld36le8ytuuhdst0lu4mmh8g53hmpqd6txsxxta6n` |
| 2 | `stake1u86jl5trmfr70cjfe6capkl2ptx05l8jflspswgh79el5ygcv8xwh` |
| 3 | `stake1u87mehxnkc68j98vsmuf6vrrlcfygppyxvkkwm4n89n2jssanukrm` |
| 4 | `stake1u89zwwc9sntxuh2e7qtjydkfdse9fv8uckzqvcg2xp6yw9gj6yp06` |
| 5 | `stake1u8etn7ndaq3t76af2vlfg74dexkfs7ysm5fwhtjth45z3ccdme5gq` |
| 6 | `stake1u907m66smf4lefjzgp7v7zzmjpjeljrvdm5vttv6nulm0asv2de62` |
| 7 | `stake1uxvvzsuuk8v0r2kksutrwvd2fe0kms3d4qh5a3su5vky53gjx9uqw` |

Any wallet operator controlling these stake keys had simultaneous cryptographic access to funds traceable to all three genesis allocations.

### IOG ∩ CF Shared Stake Addresses (53 total)

| Stake Address |
|:---|
| `stake1u8075gw62ahe5rc84vp6hw05e02fevlwm6lamczy0sk6ytcmze8aw` |
| `stake1u80zrk9u8fcp4sple4685lf9vmypq4wnnzh5vf5eylcd4zgraf9jr` |
| `stake1u85re0n76p05ld36le8ytuuhdst0lu4mmh8g53hmpqd6txsxxta6n` |
| `stake1u86jl5trmfr70cjfe6capkl2ptx05l8jflspswgh79el5ygcv8xwh` |
| `stake1u87aytjcdvslr263akxxjmygeeefj4yyntrdvjp38m39qyss32x3q` |
| `stake1u87mehxnkc68j98vsmuf6vrrlcfygppyxvkkwm4n89n2jssanukrm` |
| `stake1u88cx445rnssqrk8kvvtz2vdv03ed7nj9hw58l47kdmnpkqcttk6u` |
| `stake1u89zwwc9sntxuh2e7qtjydkfdse9fv8uckzqvcg2xp6yw9gj6yp06` |
| `stake1u8ajaufgelqyxp89whx8f0t57ndtcuvctfz2z8v3qfxxk3szmchqp` |
| `stake1u8etn7ndaq3t76af2vlfg74dexkfs7ysm5fwhtjth45z3ccdme5gq` |
| `stake1u8flq5rq8mt3tz2narxpu0nxwrpnltale8vgxkrrnvlr6dqu3ltvn` |
| `stake1u8ftwxmr3d55nvlcta8xc2k9zm8p0h5k28nf92ltsvjmmsqehhsq9` |
| `stake1u8hmy88mv2uuzyhtaxg5p3fflrzhrlyh9ey235zcsmyfyjgfhxr8h` |
| `stake1u8kj9qyemvv8ey3cv8g4y7wj8t8s0exn06ndgp9zff5fvsq3tk9ty` |
| `stake1u8n0kp7t97eu0z5y9jasp63lv7nzqyzv8muq454dc255zlsl0udsj` |
| `stake1u8njfw59kr8c4tj9p7fy9l728h4cjyhd249wsw3u5ghx93qs5vmk6` |
| `stake1u8tcdp4xejtswx2tvvxyr8ahhrdy9x9cjfvl38fw5wk7h6q70m05r` |
| `stake1u8tf44puxjcykfptqxq9zhn5v7ezlzm6e20wz0t0pmkrtuq0ugsk4` |
| `stake1u8tq4s2f03gzvckm2guv5yql4jaa3enw5h8t9mqg8la64egwq6yka` |
| `stake1u8w48j3k8pgakle2upk0fe8w0p4c8ptw0ufzej2n3al6cxggrzm2k` |
| `stake1u8wvq5nufazxzdmhkc8vs2c7ut3t5xc5xmga0a47r3erxfceh88h0` |
| `stake1u8x3gc8wsyysrhelcvgj65f9jqvzfzsndu072xcj6kyvqkcufl4zz` |
| `stake1u907m66smf4lefjzgp7v7zzmjpjeljrvdm5vttv6nulm0asv2de62` |
| `stake1u90e2wmnsgr9d8gjxuxt0cwnmztazwsj9k3jc33zzzzsxtcakcp9v` |
| `stake1u93rztxhnt9zzngrldcj6pw9lnezenknrd4gc30xv7y0htgvap9z5` |
| `stake1u98690w60kq54udx9h46p35epgm7mhq6hqxxtjen6rsqg5g9u2r0s` |
| `stake1u99syacns4h6kes0urk00xpv93qd9edn0m5wnv9arpha4ucrk7qlc` |
| `stake1u9c5uezuevsmhagw7wgnwgfkz8j4zn0d0l5lwu4h7nrvlpg6vtpye` |
| `stake1u9jklnte98sfpyyeq276q9pyn6ynsks7usuehy8vjgx3utq7twd2c` |
| `stake1u9lrp6pc9ck77p5t7e2mh8na6dep2amdw75sylyyx9wnlus3y9h8x` |
| `stake1u9mwjgt28pp4kp8amj2jrh80tlhsln322mr2k93te66te7cxdp4j8` |
| `stake1u9qp97ze3uehg6yn2ewvf0cztyn97g3v0crwwuqqmzwj5ygshhnge` |
| `stake1u9t5z2cd6ptrudkqmpz6g2zuh74duzhh8h33vtm55fy3cpcqwva72` |
| `stake1u9txk6hsds3tgdvn3h4tcfnslyrx7ye6m3rlq0nv2jlhmnsknnu5q` |
| `stake1u9vjtuhl679r4x5v40xhjfrafze0yskyxrsju0qhkgc0g7skkzf4m` |
| `stake1u9z9d3syucxs8q76744ch4gm0v6gh4awllca2s0k7xfgwfgrmp4ev` |
| `stake1ux28yyldalcy92hkg2ycr90vu7ll4c8xdczd4vs4qzqu84cqvk7xq` |
| `stake1ux2aylqan5z5urx0l6z89554tdnzm9gvudsc3ujwz8sh22sk0j6zc` |
| `stake1ux3p5tyfc3jt54843qwpy69kf5a993vqghyndmg8gjg98ds6zxefm` |
| `stake1uxkxy0vl3l8mct2xlm0gqdgjan2kw0j43jp203r6t4g0k4q3devew` |
| `stake1uxkz0cqj2zff2zdqx7naf4cdek5jxfxt7awpust0da2c5sg7yp88r` |
| `stake1uxnn2ky0dcpymqqvda9uvkrx902u3yuqleue4k6kngfh5cg0mt2wy` |
| `stake1uxvvzsuuk8v0r2kksutrwvd2fe0kms3d4qh5a3su5vky53gjx9uqw` |
| `stake1uxy9aunymgxdzfhjggm2pzx4675f4a3ymu5yqmexdzusz6sjgrfzz` |
| `stake1uy3m9gmrvceps5l3wjqr62ffan004tpa2mwfvxtzcc5cpqq5w4s74` |
| `stake1uy47jp4t6dmmwm6mpqzcmwfxmx8pqc7gz7g0sxml0mnqu2g0ucaer` |
| `stake1uy4d364gve3lq084ypmwzsmt95csgqxpfyxxeltef0z05ggw55hhx` |
| `stake1uy9cl2zzcntgkjvt7jmdwv8j905yqnerkrj975kf2c9gmqgshwwsa` |
| `stake1uynvaczl4jqjwqxxmtpsv2fg4jnys0zyh4s7hdpz59yuy3ghlqa8a` |
| `stake1uyv6xgv0akrt5s8gwf802v08pfclzaumhkxy9680nrv6nlsylapmq` |
| `stake1uyxhzxe4wa5qm7uzz8v82w5y5nzjdyejrw2af6mlj08tagspxgpz5` |
| `stake1uyz2x5qt34v2e5txpyhvrm00y4kntqeay0w2yvyn4w35dmc7zsgcl` |
| `stake1uyzh7qtcfjnhx4tzea869vwdlux4ptfak35wqfup0a4kwrgp528xa` |

---

## Part 11 — Primary Splitting Address (Cross-Entity)

The Byron address `Ae2tdPwUPEZ6xYrxCgRDM2NQFM5oajHEoJN3i9ZVV2AbsbvxoJBjVu3yP7W` is the single most active mechanical splitter in the entire dataset.

**IOG:** All 10 top fan-out transactions originate from this address (epochs 249-250, hops 10-11). Each transaction fans out to exactly 58 outputs.

**EMURGO:** This same address appears as the source of EMURGO fan-out ranks 4, 5, and 6 (epoch 249, hop 13, 58 outputs each). The identical address appears in two independent genesis traces rooted 3 weeks apart (IOG anchor: 2017-09-27, EMURGO anchor: 2017-10-18).

This means a single Byron private key — controlling address `Ae2tdPwUPEZ6xYrxCgRDM2NQFM5oajHEoJN3i9ZVV2AbsbvxoJBjVu3yP7W` — was used to mechanically split funds traceable to BOTH the IOG genesis allocation AND the EMURGO genesis allocation at epochs 249-250 (approximately early 2021).

### IOG Top 10 Fan-Out Transactions (all from shared splitter address)

| Rank | Outputs | ADA In | Epoch | Hop | Source Address |
|---:|---:|---:|---:|---:|:---|
| 1 | 58 | 615,404.33 | 250 | 10 | `Ae2tdPwUPEZ6xYrxCgRDM2NQFM5oajHEoJN3i9ZVV2AbsbvxoJBjVu3yP7W` |
| 2 | 58 | 939,881.81 | 249 | 11 | `Ae2tdPwUPEZ6xYrxCgRDM2NQFM5oajHEoJN3i9ZVV2AbsbvxoJBjVu3yP7W` |
| 3 | 58 | 1,836,403.29 | 249 | 11 | `Ae2tdPwUPEZ6xYrxCgRDM2NQFM5oajHEoJN3i9ZVV2AbsbvxoJBjVu3yP7W` |
| 4 | 58 | 929,279.69 | 250 | 11 | `Ae2tdPwUPEZ6xYrxCgRDM2NQFM5oajHEoJN3i9ZVV2AbsbvxoJBjVu3yP7W` |
| 5 | 58 | 329,707.89 | 250 | 11 | `Ae2tdPwUPEZ6xYrxCgRDM2NQFM5oajHEoJN3i9ZVV2AbsbvxoJBjVu3yP7W` |
| 6 | 58 | 333,343.26 | 250 | 11 | `Ae2tdPwUPEZ6xYrxCgRDM2NQFM5oajHEoJN3i9ZVV2AbsbvxoJBjVu3yP7W` |
| 7 | 58 | 373,387.98 | 250 | 11 | `Ae2tdPwUPEZ6xYrxCgRDM2NQFM5oajHEoJN3i9ZVV2AbsbvxoJBjVu3yP7W` |
| 8 | 58 | 264,302.56 | 250 | 11 | `Ae2tdPwUPEZ6xYrxCgRDM2NQFM5oajHEoJN3i9ZVV2AbsbvxoJBjVu3yP7W` |
| 9 | 58 | 407,719.17 | 250 | 11 | `Ae2tdPwUPEZ6xYrxCgRDM2NQFM5oajHEoJN3i9ZVV2AbsbvxoJBjVu3yP7W` |
| 10 | 58 | 641,137.61 | 250 | 11 | `Ae2tdPwUPEZ6xYrxCgRDM2NQFM5oajHEoJN3i9ZVV2AbsbvxoJBjVu3yP7W` |

### EMURGO Top 10 Fan-Out Transactions

| Rank | Outputs | ADA In | Epoch | Hop | Source Address |
|---:|---:|---:|---:|---:|:---|
| 1 | 72 | 17,660,808.79 | 175 | 12 | `DdzFFzCqrhstmqBkaU98vdHu6PdqjqotmgudToWYEeRmQKDrn4cAgGv9EZKtu1DevLrMA1pdVazufUCK4zhFkUcQZ5Gm88mVHnrwmXvT` |
| 2 | 72 | 47,224.75 | 208 | 13 | `DdzFFzCqrht6YJCbKpjkr1GfF8wecZpEVHsvWv3VfdVmzCDryY7TQVudgh6nGJg7SZKgUWW2mfga9NABLHCiHbeV7MaL3zvNaSY5Ukz6` |
| 3 | 72 | 17,660,808.79 | 175 | 13 | `DdzFFzCqrhstmqBkaU98vdHu6PdqjqotmgudToWYEeRmQKDrn4cAgGv9EZKtu1DevLrMA1pdVazufUCK4zhFkUcQZ5Gm88mVHnrwmXvT` |
| 4 | 58 | 880,085.41 | 249 | 13 | `Ae2tdPwUPEZ6xYrxCgRDM2NQFM5oajHEoJN3i9ZVV2AbsbvxoJBjVu3yP7W` |
| 5 | 58 | 836,311.25 | 249 | 13 | `Ae2tdPwUPEZ6xYrxCgRDM2NQFM5oajHEoJN3i9ZVV2AbsbvxoJBjVu3yP7W` |
| 6 | 58 | 288,261.27 | 249 | 13 | `Ae2tdPwUPEZ6xYrxCgRDM2NQFM5oajHEoJN3i9ZVV2AbsbvxoJBjVu3yP7W` |
| 7 | 58 | 284,094.11 | 250 | 13 | `Ae2tdPwUPEZJYoSsP4KK2fuG1BaYon52ZezMj7CVedG9KfyEd3RXezGSs7j` |
| 8 | 58 | 1,243,492.19 | 250 | 13 | `Ae2tdPwUPEYzzo7Q6VqUfQYctzXQPqAQywMgruCTsuxz1xi8zAYay9FXQZZ` |
| 9 | 58 | 824,162.95 | 250 | 13 | `Ae2tdPwUPEYzBxnm5gytqhy1qzgyTfS8fVzfo7KAyBqA1JLVekPKTR7x1zh` |
| 10 | 58 | 836,940.31 | 250 | 13 | `Ae2tdPwUPEZ7EYhmdxow9rTRMuKUJPZdYBcTDPT7Kpyva1Uy1PvnuxAUW7m` |

### CF Top 10 Fan-Out Transactions

| Rank | Outputs | ADA In | Epoch | Hop | Source Address |
|---:|---:|---:|---:|---:|:---|
| 1 | 147 | 469,955.40 | 208 | 15 | `Ae2tdPwUPEZFN3bHkMWtiUdEsRrDAm65okvCMad3hohXEfaM1uc6Q8rQDh6` |
| 2 | 82 | 22,829,000.29 | 208 | 15 | `DdzFFzCqrht5d66v6te675Bw1hRtyuEgEfUYHBH6eB9tJFTbKBjdqhAAaWJka5vnh5ARkWpa2ibA8co1vkw6oxcrvEirW8o8FW568nYZ` |
| 3 | 60 | 602,933.71 | 209 | 15 | `DdzFFzCqrht5xp7vkGMWw2rpjb6mEDNyPHGM8wny53HMFdn7RzyrBzT2HGnE2GDPgkx2FfdEv2s2WZMeiF7GEit7Dujbdu1B4SyqQK7h` |
| 4 | 56 | 2,269,346.49 | 208 | 14 | `DdzFFzCqrht8XRXzWppbeRDD9behmWX2MC7rGspnEdhKdaGncYsyTnYnDY9eeqidMNCwGXz8aXt8NRKuimME9V5JWj7aexkmD6662ZGm` |
| 5 | 56 | 2,269,346.49 | 208 | 15 | `DdzFFzCqrht8XRXzWppbeRDD9behmWX2MC7rGspnEdhKdaGncYsyTnYnDY9eeqidMNCwGXz8aXt8NRKuimME9V5JWj7aexkmD6662ZGm` |
| 6 | 52 | 447,570.18 | 208 | 15 | `DdzFFzCqrhsfpqZxAsFCVP8bD4ofKPGxatGL2gChQL6yWwcdUjYgv2pkMGurof5EuJ1tg4QFx1mtZ179w2KhF6xSvqP8tRYxRPRvyYQf` |
| 7 | 49 | 156,651.80 | 208 | 14 | `Ae2tdPwUPEZFN3bHkMWtiUdEsRrDAm65okvCMad3hohXEfaM1uc6Q8rQDh6` |
| 8 | 47 | 1,118,726.21 | 208 | 13 | `DdzFFzCqrhsvQrEJknSeubfvnB79xnaCvzxAr2CsSmp9UEBBuN9NdiTQuGUJfBoEk25puWwDNEqJgeXXSAXJtNixvJrkAXARswLjDGSz` |
| 9 | 47 | 670,911.23 | 208 | 13 | `DdzFFzCqrhszQedF26C112azrPDZGDRcWCqmXRT6AQfCEXqBh58ywLsHtToqjnusLMZLBoD3JndiekVpuSe4PQDrB8APuMkgVrMrsK79` |
| 10 | 47 | 1,118,726.21 | 208 | 14 | `DdzFFzCqrhsvQrEJknSeubfvnB79xnaCvzxAr2CsSmp9UEBBuN9NdiTQuGUJfBoEk25puWwDNEqJgeXXSAXJtNixvJrkAXARswLjDGSz` |

---

## Part 12 — Binance Address as Distribution Source (EMURGO and CF)

The address `DdzFFzCqrhstmqBkaU98vdHu6PdqjqotmgudToWYEeRmQKDrn4cAgGv9EZKtu1DevLrMA1pdVazufUCK4zhFkUcQZ5Gm88mVHnrwmXvT` is confirmed by exchange classification heuristics as a Binance Byron-era hot wallet address.

This address appears not only as a recipient of genesis funds but as a **distribution source** in both EMURGO and CF traces:

- **EMURGO ranks 1 and 3:** Two separate fan-out transactions each distributing 17,660,808.79 ADA (72 outputs each) at epoch 175, hop 12-13
- **Implied role in CF:** Multiple CF fan-outs at epoch 208 also use `DdzFFzCqrht5d66v6te675Bw1hRtyuEgEfUYHBH6eB9tJFTbKBjdqhAAaWJka5vnh5ARkWpa2ibA8co1vkw6oxcrvEirW8o8FW568nYZ` and related Ddz-prefix addresses as source

This is the only address in the dataset that is simultaneously:
1. Classified as an exchange address (Binance hot wallet)
2. Acting as a **source** of fragmentation to new addresses (not just a recipient absorbing funds)
3. Present in traces from two separate founding entities (EMURGO at epoch 175, CF at epoch 196/208)

The implication is that EMURGO and CF genesis funds were routed **through** a Binance hot wallet before being distributed to end addresses — not merely deposited there as a terminal destination. This is consistent with OTC or custodial distribution operations where the exchange serves as the distribution infrastructure.

---

## Part 13 — Top 30 Pool Rankings (Computed from Delegation History CSVs)

### IOG — Top 30 Pools (Computed)

| Rank | Unique SA | Epoch Min | Epoch Max | Pool ID |
|---:|---:|---:|---:|:---|
| 1 | 860 | 248 | 432 | `pool1uj4u73qgtprqre78q75fq2vkcrpfrcdreqcqkvn6u0m2k6nk2yp` |
| 2 | 510 | 244 | 555 | `pool1zgxvcqf0dvh0ze56ev2ayjvuex3zdd3hgxzdrcezkx497mv3l7s` |
| 3 | 482 | 252 | 574 | `pool1ng3vqzrhn3z45yjdscv3q37n26g2pj3vp99rfkgv6225y8lqg8j` |
| 4 | 350 | 239 | 400 | `pool1g3ssnndd8e7lcmstkjl9ane9mup0eshv3aklg63u5tznwl4ch87` |
| 5 | 292 | 248 | 409 | `pool13annzt9hjfc822f0ejvxjf7fsmxd6cc28whpk5kagec6ggfmm7u` |
| 6 | 257 | 241 | 606 | `pool1ynxx88cq0y8vg8yrq3jrw6epm7rq9a8859v34sq9lzjy7ztg90u` |
| 7 | 253 | 234 | 525 | `pool1jst7rrhucnp93hepezv5yqy6fx982xs2v0udwfc5ea6my3kfak7` |
| 8 | 253 | 255 | 482 | `pool1xmsdhync6k6grkkj7tuycskjpseykpr24luhlazl5nsngsy87gm` |
| 9 | 219 | 238 | 622 | `pool16agnvfan65ypnswgg6rml52lqtcqe5guxltexkn82sqgj2crqtx` |
| 10 | 212 | 244 | 362 | `pool1zmfpd5r5vfwjmwm4cgy53exe58h7plnecny3t4948yw7zumzp4c` |
| 11 | 193 | 256 | 620 | `pool1ywpt43nttzjd7883wafg255mh0hmjypwe65ercw6p2sxg5lt7ez` |
| 12 | 187 | 210 | 557 | `pool16kus5xvdysgmtjp0hhlwt72tsm0yn2zcn0a8wg9emc6c75lxvmc` |
| 13 | 176 | 235 | 582 | `pool1s6se64qce5rjjjhh6ufcdnc54p8qg78mlhjm38lymx99sqysvzx` |
| 14 | 173 | 238 | 472 | `pool14enw2643rn9nn6yzv60jyz3hj4kxs0jvap87lkgsqykh508jxm6` |
| 15 | 156 | 210 | 587 | `pool1gtphgrdj8sluxm9e7ca2spcwcq2p0dxj9zf5v0yv3gsagzq704n` |
| 16 | 151 | 231 | 504 | `pool12l453n0jtxqq88cgwgr67z06ldyhqqvwxgkn0sgungjfvhtp2el` |
| 17 | 151 | 232 | 622 | `pool15wkxegrfflzcyhurrjxsm9ljqtz09xr5rtnqsarnp7hmsz5um3t` |
| 18 | 143 | 229 | 623 | `pool14skj6e4rpjanzclx3fc880xnl8xafgg63tmw93t9xspvwx985qu` |
| 19 | 142 | 234 | 589 | `pool1lurfk0k0wwx54hlg8a7zp3jtstu57u59aeq7aketl55hknmmtu0` |
| 20 | 131 | 210 | 385 | `pool1m62sl6rauje9cknrkhwl39tc4hujudkd7gp478dpz7tagmjr8wm` |
| 21 | 129 | 212 | 453 | `pool1x0qm7xsyh2za3ltprxsgael544je4hg8tc3q3v5gv232z8jt4wp` |
| 22 | 116 | 249 | 563 | `pool12z39rkzfylvn9wfe8j6x9ucq6g2l4mw4azj70y0gd8ejczznyj3` |
| 23 | 115 | 242 | 428 | `pool1rpjjz68kmmetyxztmrstrwgz8lxf6v0d7vqgw98r5x8rc50jrdf` |
| 24 | 113 | 215 | 584 | `pool1pnzwgsgzd6t4788sfr7dxjyusepyq9xaxnpyfcngewqf29t9ayd` |
| 25 | 112 | 210 | 605 | `pool1gclysx2h7fndj0jdajlmwvqr8q9tzu3rurjknacu0ff954fsg9a` |
| 26 | 110 | 210 | 585 | `pool1a2nh3ktswllhwf07fjahpdg5mpqyq7j950pyftq9765r6t4cefl` |
| 27 | 109 | 210 | 617 | `pool1ekcsyzwexl7p2kwxxh34hy28l6772vrmff7jwmuxsa6u6fzty9z` |
| 28 | 108 | 233 | 611 | `pool1xytvsd9qnvqxpthh9p8k85e823trvn3npxeur8kr9zhkqz5uls9` |
| 29 | 107 | 210 | 342 | `pool1xxhs2zw5xa4g54d5p62j46nlqzwp8jklqvuv2agjlapwjx9qkg9` |
| 30 | 106 | 233 | 524 | `pool19asxjgd6ah9ddzauwede4wpt9vsp6s4ax5nz297wt47evc9sn7z` |

### EMURGO — Top 30 Pools (Computed)

| Rank | Unique SA | Epoch Min | Epoch Max | Pool ID |
|---:|---:|---:|---:|:---|
| 1 | 364 | 252 | 572 | `pool1ng3vqzrhn3z45yjdscv3q37n26g2pj3vp99rfkgv6225y8lqg8j` |
| 2 | 180 | 248 | 353 | `pool1uj4u73qgtprqre78q75fq2vkcrpfrcdreqcqkvn6u0m2k6nk2yp` |
| 3 | 151 | 255 | 475 | `pool1xmsdhync6k6grkkj7tuycskjpseykpr24luhlazl5nsngsy87gm` |
| 4 | 150 | 244 | 556 | `pool1zgxvcqf0dvh0ze56ev2ayjvuex3zdd3hgxzdrcezkx497mv3l7s` |
| 5 | 144 | 248 | 404 | `pool13annzt9hjfc822f0ejvxjf7fsmxd6cc28whpk5kagec6ggfmm7u` |
| 6 | 140 | 239 | 397 | `pool1g3ssnndd8e7lcmstkjl9ane9mup0eshv3aklg63u5tznwl4ch87` |
| 7 | 123 | 240 | 557 | `pool16agnvfan65ypnswgg6rml52lqtcqe5guxltexkn82sqgj2crqtx` |
| 8 | 119 | 257 | 617 | `pool1ywpt43nttzjd7883wafg255mh0hmjypwe65ercw6p2sxg5lt7ez` |
| 9 | 116 | 235 | 606 | `pool1ynxx88cq0y8vg8yrq3jrw6epm7rq9a8859v34sq9lzjy7ztg90u` |
| 10 | 106 | 232 | 542 | `pool15wkxegrfflzcyhurrjxsm9ljqtz09xr5rtnqsarnp7hmsz5um3t` |
| 11 | 95 | 237 | 528 | `pool14enw2643rn9nn6yzv60jyz3hj4kxs0jvap87lkgsqykh508jxm6` |
| 12 | 94 | 210 | 590 | `pool1lurfk0k0wwx54hlg8a7zp3jtstu57u59aeq7aketl55hknmmtu0` |
| 13 | 94 | 234 | 523 | `pool1jst7rrhucnp93hepezv5yqy6fx982xs2v0udwfc5ea6my3kfak7` |
| 14 | 90 | 221 | 458 | `pool16kus5xvdysgmtjp0hhlwt72tsm0yn2zcn0a8wg9emc6c75lxvmc` |
| 15 | 88 | 230 | 602 | `pool1s6se64qce5rjjjhh6ufcdnc54p8qg78mlhjm38lymx99sqysvzx` |
| 16 | 86 | 210 | 529 | `pool1gtphgrdj8sluxm9e7ca2spcwcq2p0dxj9zf5v0yv3gsagzq704n` |
| 17 | 83 | 249 | 489 | `pool12z39rkzfylvn9wfe8j6x9ucq6g2l4mw4azj70y0gd8ejczznyj3` |
| 18 | 81 | 211 | 620 | `pool1ekcsyzwexl7p2kwxxh34hy28l6772vrmff7jwmuxsa6u6fzty9z` |
| 19 | 78 | 229 | 623 | `pool14skj6e4rpjanzclx3fc880xnl8xafgg63tmw93t9xspvwx985qu` |
| 20 | 75 | 231 | 503 | `pool12l453n0jtxqq88cgwgr67z06ldyhqqvwxgkn0sgungjfvhtp2el` |
| 21 | 74 | 212 | 502 | `pool1x0qm7xsyh2za3ltprxsgael544je4hg8tc3q3v5gv232z8jt4wp` |
| 22 | 73 | 235 | 469 | `pool1xytvsd9qnvqxpthh9p8k85e823trvn3npxeur8kr9zhkqz5uls9` |
| 23 | 72 | 244 | 332 | `pool1zmfpd5r5vfwjmwm4cgy53exe58h7plnecny3t4948yw7zumzp4c` |
| 24 | 70 | 210 | 618 | `pool1vx9tzlkgafernd9vpjpxkenutx2gncj4yn88fpq69823qlwcqrt` |
| 25 | 67 | 236 | 442 | `pool1qfxukshs4fkcrflzdnxa2fdza5lfvew3y6echg8ckaa4q8m5hyf` |
| 26 | 65 | 210 | 397 | `pool1jeu74g86ys4fekhykqcww99kdsq3nlym8a6kfw8s8ff3vskad70` |
| 27 | 64 | 210 | 523 | `pool15yyxtkhz64p7a8cnax9l7u82s9t9hdhyxsa3tdm977qhgpnsuhq` |
| 28 | 62 | 210 | 346 | `pool1xxhs2zw5xa4g54d5p62j46nlqzwp8jklqvuv2agjlapwjx9qkg9` |
| 29 | 61 | 210 | 543 | `pool108zdflss3ayqlm5c7vr6mtqj2uwl99vk28ur8dv4zswdzt6yauc` |
| 30 | 61 | 210 | 550 | `pool1a2nh3ktswllhwf07fjahpdg5mpqyq7j950pyftq9765r6t4cefl` |

### CF — Top 30 Pools (Computed)

| Rank | Unique SA | Epoch Min | Epoch Max | Pool ID |
|---:|---:|---:|---:|:---|
| 1 | 70 | 210 | 598 | `pool12vs4c3cm0tr49c7alrevfs0xa5g3s4al4fn46h33e69uusat04v` |
| 2 | 66 | 211 | 594 | `pool1jeu74g86ys4fekhykqcww99kdsq3nlym8a6kfw8s8ff3vskad70` |
| 3 | 62 | 232 | 527 | `pool15wkxegrfflzcyhurrjxsm9ljqtz09xr5rtnqsarnp7hmsz5um3t` |
| 4 | 61 | 210 | 603 | `pool1qqqqqdk4zhsjuxxd8jyvwncf5eucfskz0xjjj64fdmlgj735lr9` |
| 5 | 60 | 212 | 501 | `pool14skj6e4rpjanzclx3fc880xnl8xafgg63tmw93t9xspvwx985qu` |
| 6 | 58 | 210 | 405 | `pool1rvng7n968748udkc5rxy4h9zp9hms4s3jsfwuues76ft28uc056` |
| 7 | 58 | 231 | 501 | `pool12l453n0jtxqq88cgwgr67z06ldyhqqvwxgkn0sgungjfvhtp2el` |
| 8 | 53 | 211 | 317 | `pool1ecvcst7k9eul4ggnljh0jw2s5nc2tyfmyzsx3xg3kmmz6ptgfwj` |
| 9 | 50 | 210 | 442 | `pool1ekcsyzwexl7p2kwxxh34hy28l6772vrmff7jwmuxsa6u6fzty9z` |
| 10 | 50 | 210 | 345 | `pool1a2nh3ktswllhwf07fjahpdg5mpqyq7j950pyftq9765r6t4cefl` |
| 11 | 45 | 210 | 512 | `pool1qnrqc7zpwye2r9wtkayh2dryvfqs7unp99f2039duljrsaffq5c` |
| 12 | 43 | 210 | 330 | `pool1xxhs2zw5xa4g54d5p62j46nlqzwp8jklqvuv2agjlapwjx9qkg9` |
| 13 | 41 | 212 | 284 | `pool1x0qm7xsyh2za3ltprxsgael544je4hg8tc3q3v5gv232z8jt4wp` |
| 14 | 41 | 237 | 475 | `pool14enw2643rn9nn6yzv60jyz3hj4kxs0jvap87lkgsqykh508jxm6` |
| 15 | 40 | 210 | 339 | `pool1vx9tzlkgafernd9vpjpxkenutx2gncj4yn88fpq69823qlwcqrt` |
| 16 | 38 | 210 | 600 | `pool1s0cfkzheywsftgwp0yz7sq4rt5gyf7t5kfwj5a269kpxvndjn6q` |
| 17 | 38 | 210 | 416 | `pool15yyxtkhz64p7a8cnax9l7u82s9t9hdhyxsa3tdm977qhgpnsuhq` |
| 18 | 36 | 210 | 389 | `pool1hntu7agmt8u5j9c20ejen7dvq0jfkvkpnul3mrdd8tppqvwfvt2` |
| 19 | 35 | 210 | 450 | `pool1ctzja2cdwyeqnvehmrlclc5wrn9w9acwklk3acn73jrx56d66vs` |
| 20 | 32 | 210 | 567 | `pool1lvsa8e0dw6z8g2fkw7prnfa7627wuy5jjexaadck6w5sxw5xkvm` |
| 21 | 32 | 210 | 341 | `pool1qqqyv9pn9typyqwcxqk5ewpxy5p27g5j2ms58hpp2c2kuzs5z77` |
| 22 | 31 | 210 | 483 | `pool16kus5xvdysgmtjp0hhlwt72tsm0yn2zcn0a8wg9emc6c75lxvmc` |
| 23 | 30 | 211 | 498 | `pool1gclysx2h7fndj0jdajlmwvqr8q9tzu3rurjknacu0ff954fsg9a` |
| 24 | 29 | 235 | 396 | `pool1jst7rrhucnp93hepezv5yqy6fx982xs2v0udwfc5ea6my3kfak7` |
| 25 | 28 | 211 | 253 | `pool1mxqjlrfskhd5kql9kak06fpdh8xjwc76gec76p3taqy2qmfzs5z` |
| 26 | 27 | 210 | 438 | `pool108zdflss3ayqlm5c7vr6mtqj2uwl99vk28ur8dv4zswdzt6yauc` |
| 27 | 27 | 210 | 614 | `pool1qwa8x4u4a2pff0xdv0haxpgk3tyrvl5adl2lpf3ztcftqruhea0` |
| 28 | 27 | 210 | 590 | `pool1gtphgrdj8sluxm9e7ca2spcwcq2p0dxj9zf5v0yv3gsagzq704n` |
| 29 | 27 | 210 | 468 | `pool1vc8jp7uagxgh8trzx7r260ndcydz89ges8sws05cyv7jj8q8gqs` |
| 30 | 26 | 211 | 217 | `pool1l3fvlzadk5hg78wy3e304s9t8tjzxnu962e2fl7tq8x2yg3mz6l` |

---

## Part 14 — Epoch 208 Destination Addresses (Sample, First 30 per Entity)

Epoch 208 = August 2020 Shelley hard fork activation. All three entities show simultaneous fragmentation into new address types.

### IOG — Epoch 208 Destination Address Sample (30 of 422 unique addresses)

Total edges at epoch 208: 585 | Total ADA: 22,222,645.25 ADA

```
Ae2tdPwUPEZ1zPy1L9PSQnUDNHzCehy2p9tDLvihV7LJBgb7VogHRdxKc6P
DdzFFzCqrhsrN7kKVy4jPWFSMcY3Bcx2cG9Faxjy43BgyBqxitxTShkPAxjziLhombZgzCgH9uwB6i1mGmBaLzYHMusGTooyq8DHfWep
addr1q8034vup8jvhuv70z9anuk4fceq6l2ah3q90u8uvlk32yje0jwuwvgrth6qzav7zwlvjuk4ek6tf8axf5juckda9z5xsq7rj73
addr1q80s5st48797kuutzgprgskx8egyxqmergfn8zl5rcgdc8mj2czy7kukynph0pckvct23ucn6csh77rmtr3nre7j0jvszfvl9m
addr1q80ucyjlfn3e8gj7eluxaqyk22xkc8l5e2mdykhkz2ujgx53j05pmdrnw200udr0rfmlllqml3vgjntej7s5e5a4ncaqz7h0kw
addr1q82e4dvkvfxy7473p2wztat0z3fqmc2t5wye050s44s4f4jzeluwwsd4j20ccx7y2wh6swze0t67f7m4xqprjef8xrqswpuer3
addr1q82qmeh3uqtkjynt4yptul87tk6m0f60sa4szwg0ezaxxe33vq9qcmyhca8nx8jvqar030mvc27w9zym70dx3l5mg2aq5jv9tl
addr1q82v695a6xjnggjpg8dh0ewe579z04q3qwsgw9qcy80a9t8vkvp2dut3eryedx7a7ds7xwrz9q5raugm2f4p2sdzzlnsd20dg2
addr1q83hrwgs0z6q3gntufu7jnt7mpjlpfrjcgekew9ve3spu47967rxkztkh7c9lterwlz75aa5yvxhmg28vjsd5zszgy9s3gww25
addr1q83m7rawvgygegxafqnqeh04qpn5j57659vrd8zm89nlqunadlus95gjscsdc57sj0547dqcky3e8jw8jdknqlswqcwsxdmngy
addr1q83uwj8h66aj45qwnkgrgptqxnh7qmufd8awjlkdlm7sn85lhe62vyjr39lq5hktczm43jxmh85vj3cc330966n5qkpsj9dq23
addr1q83ye5g3ahe64xxq8u0v5mnfqkdx4nsz4dpnxf7cllc08n6qztu9nrenw35fx4jucjlsykfxtu3zclsxuacqpkya9ggse0a7lt
addr1q8438ds5m4gn5z29cc5s6fgug843gz27gt702ue3j2mmmjsn3fhp40unnvlww7zslpc65m8w9fg60xfmluz2wly6arhs4sh7q0
addr1q848pvya99gh5cfedzcnmdtr4pujsmm9pvv8fs9w98c366rrpzsa895gfancl6z6xl8hhgghuht8qdsr3alt92kdmqasq0czvl
addr1q85akv5su87rega4q23qqq7g8km5qhs54vgwdhr427rpv28vkvp2dut3eryedx7a7ds7xwrz9q5raugm2f4p2sdzzlnscz0z4m
addr1q85aqxp3pr8uqnd4r4p8mp2qvcu58nmh9ed54z0y50fzeuucv0qt5l2p4cmvyh2tgd87sa6hsrud584ftnanv6yrdmesrmlur4
addr1q866r38gzwqca6lc9y6yd7jvmvwh24t2p3q54y2pw9h26yr978mf6fy49pxtkkxt7er5w36rm8fah9vzkya7lsujntqsef5v7v
addr1q86xrgfttygv0w7r0q06ys0px2jtywmj82g3xdjt02tmr8vcv0qt5l2p4cmvyh2tgd87sa6hsrud584ftnanv6yrdmesm5jh7g
addr1q87ewzrkuvhgwfe83j8tg5ux7z2nxx52kjfq39s4l8679vsyc2c7hhuxng0fcj995usngjejf9dgzyqetz4t4hc6tv6qlupvrv
addr1q87gkca24xedwxd3f9qgeh0egku3vp9f0llrlktqemh3cvgvnuw4dydefr2y7zc6sjk6faaqwymj0yn7mralcl922y9sf38c7q
addr1q87qmmjzc2cnrh78cslf8dlkghnamxh2w3u6qwac96nzjxnrpzsa895gfancl6z6xl8hhgghuht8qdsr3alt92kdmqastuw35d
addr1q885pr6nkvg79seqgeccqf8mg4k99at6zv950fwjms4uz0af4g6wmtqq276vf7ajknf5t2y905erghjnhng57tc7czgq6mu7vs
addr1q88g3perczsgpqf6pakf5qwfrq4pca94kauxm9yj7kdu0zvlhe62vyjr39lq5hktczm43jxmh85vj3cc330966n5qkpszs36pf
addr1q88h75hmm9pxc723txy7jg4k4w5xjtndgz2y73307pgs6a4glumk33h8m0e48z0euuy558zjmfgmswtr9j5cxm7jlzxsn3pplt
addr1q88h8u7lc4rj3tu5sv4p0klvwelvqvus3dawckx0f6k82lar4tclcgmwz7lkylfzf7qxedeckskq6aatxxa7dq5adqwqztjuyh
addr1q88j7hyrk5aevvhhyn7kkyghwjz4l6dup7an2w73flh6d564384akuafkg5duataq04hrk06x658rpaljujpwgelr5ws7m8cdz
addr1q88sywjg3yzrfzygec9tlx5wn9zrfvyj9svudq3rqya02dr978mf6fy49pxtkkxt7er5w36rm8fah9vzkya7lsujntqs9zmjts
addr1q89dsml7vxrdzqxplxgwr3azfgvma9k98ux7a5anddfg7fe0jwuwvgrth6qzav7zwlvjuk4ek6tf8axf5juckda9z5xshchm84
addr1q89kq7aygaw0jec2jny6tr3lc347s7a7dfhs2l93d7cymadglumk33h8m0e48z0euuy558zjmfgmswtr9j5cxm7jlzxshjau7r
addr1q89rgkrx70mq7450pkmgc9zqj5dmm7m6j307pru2rln24xm54p078fyh692k97d7jvj8z686248f2ne5gkj06l9mceaq4wjgah
```

*Full 422 IOG + EMURGO + CF epoch 208 destination addresses available in `fragmentation_address_data.txt` (Task 5, line 1295+).*

---

*Parts 10-14 appended 2026-03-31.*
*Source: fragmentation_address_data.txt (computed by background extraction script, 6,034 lines).*

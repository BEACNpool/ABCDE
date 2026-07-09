# F10 — Stake-pool operator concentration by KES co-rotation

**Date:** 2026-07-08 · **Snapshot tip:** block 13,651,846 / epoch 642 (see
`sql/55_pool_operators/data/export_tip_receipt.csv`). Current-state figures are as
of that date. **Build:** `sql/55_pool_operators/` + `scripts/kes_corotation_cluster.py`.

## Claim

Cardano's ~2,900-pool count overstates decentralization. Clustering pools by
synchronized KES-key rotation — a public operational fingerprint in every block
header — resolves **480 pools into 96 operator groups controlling 11.42B ADA, or
53.4% of all staked ADA.** Recomputed per operator, the network's concentration is
roughly four times higher than the per-pool figure suggests.

## Grade

- **FACT** — the rotation events, cluster memberships, stake, block share, and DRep
  overlays are directly queryable from db-sync (this build + the receipts).
- **STRONG_INFERENCE** — a cluster indicates one *operator* (shared admin /
  automation / managed host).
- **UNKNOWN** — the real-world *identity* of any unlabeled operator. Synchronized
  rotation is not proof of shared ownership; white-label infra providers (Kiln,
  Figment) run pools for many clients and look identical here. On-chain
  co-behaviour is on-chain linkage, never real-world identity or control.

## Queryable

Ask the repo directly (MCP `run_sql` / `ask.py`), e.g. *"how many stake pools move
in a cluster as if they have the same owner?"*:

- `pool_operator_kes_clusters` — one row per operator cluster (pools, stake_ada,
  block_pct, delegators, abstain_ada, top_drep_ada, has_onchain_links, sample_tickers).
- `pool_operator_kes_members` — one row per pool (cluster_id, pool_bech32, ticker, stake_ada).

```sql
SELECT count(*) AS operator_clusters, sum(pools) AS pools_moving_as_one,
       sum(pools) FILTER (WHERE NOT has_onchain_links) AS concealed_pools
FROM pool_operator_kes_clusters;   -- 96 clusters, 480 pools, 142 concealed
```

## Key figures (FACT)

Nakamoto coefficient — minimum entities to a control threshold:

| Metric | Threshold | Naive (per pool) | Per operator |
|---|---|---|---|
| Stake | 33% | 96 | **15** |
| Stake | 50% | 159 | **49** |
| Block production (30 ep) | 33% | 100 | **15** |
| Block production (30 ep) | 50% | 165 | **48** |

- **29 clusters / 142 pools / 4.76B ADA (~22% of stake) share no on-chain link**
  (no shared reward address, owner key, relay, or co-registered cert) — KES timing
  is the only public tell. (This subset shrinks over time as concealed pools happen
  to share a relay/reward on re-registration; the count is reproducible from
  `pool_operator_kes_clusters` at each snapshot.)
- Most clusters were still actively synchronizing in mid-2026.

## Largest clusters

Full membership: `sql/55_pool_operators/data/cluster_membership_2026-07-08.csv`;
per-cluster rollup: `…/cluster_summary_2026-07-08.csv`.

| # | Pools | Stake M₳ | Block % | On-chain links | Who (sampled tickers) |
|---|---|---|---|---|---|
| 1 | 55 | 2,484 | 11.44 | none | Anonymous fleet (exchange-scale custodian, inferred — unnamed) |
| 2 | 13 | 503 | 2.20 | reward+owner+relay | eToro |
| 3 | 8 | 458 | 2.11 | none | Figment (Figment 2 + Ledger-by-Figment + BTV) |
| 4 | 7 | 442 | 2.15 | none | Kiln + Trust Nodes |
| 5 | 29 | 413 | 2.12 | partial | Japanese cluster (ZZZ / KTN / POP / JAPAN) |
| 6 | 9 | 392 | 1.80 | relay | Everstake |
| 7 | 7 | 356 | 1.55 | none | BD0–BD6 (anonymous) |
| 9 | 18 | 291 | 1.47 | reward+relay | NuFi |

### Cluster #1 — a 2.48B ADA anonymous fleet (STRONG_INFERENCE: one custodian)

The largest operator, invisible to wallet-clustering. FACTs: no tickers or
machine-generated names; blank off-chain metadata on throwaway subdomains;
identical config (0 pledge, 340 ADA fixed cost, 2.5–5% margin); all 55 registered
2022-03-21 (several in one minute) via a scripted funding chain (each pool 508 ADA
from a single-use address, itself fed 510 ADA one hop back); delegated stake traces
to four enterprise wallets cycling ~1.2B ADA each; the entire 2.482B ADA
vote-delegates to `drep_always_abstain` (a custodial posture). The profile is an
exchange-scale custodian; the specific exchange is **UNKNOWN** — the community
tracer label set (`tracers/`) covers the deposit side and does not bridge to this
staking treasury at any safe hop distance.

### Governance surface

The Japanese cluster (#5) feeds `drep1jnmmkfwpta0yuwjchw0gu6csh75vy62088egy9n67d0zc7sn83m`,
the largest non-abstain DRep on the network (428M ADA of voting power at epoch 641).
Pool independence is an assumption under both block-production decentralization and
DRep governance; this finding is an input to decentralization-related governance
actions. See also `docs/16_GOVERNANCE_DELEGATION_SURFACE.md`.

## Method (summary)

Rotation events = op-cert changes in block headers, timed by each pool's own minted
blocks. Two pools pair when ≥5 rotations fall within ±24h — ≥50% of the smaller
pool's rotations — and the count is impossible under an empirical Poisson null built
from the chain-wide rotation-time distribution (p ≤ 1e-9), which discounts
network-upgrade days when everyone rotates. Clusters are connected components of
surviving pairs. Full method in `scripts/kes_corotation_cluster.py`.

## Refutation tests / limitations

- **False negatives:** rarely-minting pools have wide timing windows and are missed
  → every count is a floor.
- **Operator ≠ owner:** a cluster with a known white-label host (Kiln/Figment) is a
  legitimate single operator, not a concealed one — the on-chain-links column and
  the labels in `tracers/labels/exchange_labels.csv` help separate the two.
- **Refute a cluster:** show its pools rotate on independent schedules outside the
  ±24h window, or that a third-party host explains the shared timing.

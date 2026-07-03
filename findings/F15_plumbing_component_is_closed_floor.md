# F15 — The reward-plumbing operation is a closed 115-key component; ~1.694B ADA is the floor

## Claim

Iterating the F13 reward-plumbing edge to fixpoint from the eight F11 cohort
keys reaches a **closed component of 115 stake keys** and no more:

- Forward reachability (key A → key B when a withdrawal-tx output of A is spent
  by a transaction that is itself a withdrawal tx of B) grows
  **8 → 89 (round 1) → 115 (round 2) → 115 (round 3, fixpoint).** Round 1
  reproduces the F13 fleet exactly; round 2 adds 26 keys; round 3 adds none.
- Of the 115 keys, **50 currently hold ADA** (≥1,000); **42 hold exactly
  35,000,000 ADA**, and the total holder balance is **1,693,922,205 ADA** —
  identical to the F11+F14 combined surface.
- **The 26 keys discovered in round 2 add zero parcels**: every one is a
  near-empty reward-routing key. Extending the plumbing graph past the F13
  fleet added structure but not a single new 35M parcel.
- **All 50 holders delegate to `drep_always_abstain`** — unanimous, no
  exceptions across the whole component.

Within the reward-plumbing linkage, **1,693,922,205 ADA across 42 exact-35M
parcels (50 holders total) is the complete, closed surface.** It is a hard
floor for the operation and the entire extent reachable through this specific
linkage.

## Grade

- **FACT**: the 115-key component and its round-by-round convergence; the 50
  holders; the 42 exact-35M parcels; the 1,693,922,205 ADA total; the unanimous
  `drep_always_abstain` delegation; and that the 26 round-2 keys hold no
  parcels. All reproducible from `f15_cowithdrawal_component` and
  `component_control_indicators`.
- **STRONG_INFERENCE**: the 115 keys are one operation (same basis as F11/F14 —
  shared withdrawal-transaction construction, uniform parcels, uniform
  governance posture).
- **WORKING_HYPOTHESIS**: founding-entity-linked custody (the IOG depth-14
  trace reaches the seed keys; it does not identify the operator).
- **UNKNOWN**: ownership, identity, intent.

### What "floor" does and does not mean

- **Floor, not ceiling of the real-world entity.** This is the complete surface
  reachable through *withdrawal-plumbing* edges. Parcels held by the same
  operator but never wired into this reward-sweep plumbing — or linked only
  through the exchange-scale hubs (F13), which are shared by millions of
  unrelated users and therefore cannot be used as linkage edges — would not be
  reached here. So 1.694B is a rigorous lower bound on the operation, not a
  proof of its maximum.
- **Directionality.** The edge is directed (A funds B's withdrawal). Forward
  reachability from the eight seeds captures the plumbing they feed; a key that
  only *funds* a seed and is never funded onward could be missed. The clean
  round-3 fixpoint and the zero-parcel round-2 additions make an undiscovered
  parcel layer within this linkage unlikely, but not impossible.
- **Batch-service caveat (unchanged from F14):** shared withdrawal construction
  is FACT-grade shared control at signing time; "one operator" rather than "one
  custody service with pooled tooling" stays STRONG_INFERENCE.

### Snapshot-boundary notes

Component membership and balances at live tip `13,630,389`+ (2026-07-03).
Balances/delegation are snapshot-sensitive; the graph structure and parcel
history are historical facts.

## Evidence

- `data/small/f15_cowithdrawal_component.csv` (115 keys, discovery round)
- `data/small/component_control_indicators.csv` (per-key classification)
- `data/small/component_control_summary.csv` (pattern × consistency rollup)
- `data/manifests/component-control-indicators-manifest.json`
- SQL: `sql/10_findings/f15_cowithdrawal_component.sql`
- driver: `scripts/build_component_control_indicators_remote.sh`
- upstream: [F11](F11_eight_key_35m_custody_cohort.md),
  [F13](F13_reward_plumbing_downstream_and_tracer_bridge.md),
  [F14](F14_fleet_is_same_35m_parcel_structure.md)

## Reproduce

From a clone (DuckDB):

```sql
-- the closed surface: 42 exact-35M parcels, 50 holders, unanimous abstention
SELECT COUNT(*) FILTER (WHERE current_ada >= 1000)              AS holders,
       COUNT(*) FILTER (WHERE ABS(current_ada - 35000000) < 2)  AS exact_35m,
       COUNT(*) FILTER (WHERE current_ada >= 1000
                        AND current_drep = 'drep_always_abstain') AS abstain_holders,
       ROUND(SUM(current_ada) FILTER (WHERE current_ada >= 1000), 0) AS holder_ada
FROM component_control_indicators;

-- round-2 keys add structure, not parcels
SELECT c.first_round,
       COUNT(*)                                     AS keys,
       COUNT(*) FILTER (WHERE i.current_ada >= 1000) AS holders
FROM f15_cowithdrawal_component c
JOIN component_control_indicators i USING (stake_address)
GROUP BY c.first_round ORDER BY c.first_round;
```

Maintainers (warehouse):

```bash
ABCDE_SSH=<host> bash scripts/build_component_control_indicators_remote.sh
```

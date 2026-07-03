# F14 — The F13 fleet is the same 35M-parcel institutional custody structure as the F11 cohort

## Claim

Classifying the 81 F13 fleet stake keys through the same control-indicator
pipeline as the genesis set (separate `fleet_control_*` output) shows the fleet
is not merely "keys that shared a withdrawal transaction" — it is **more of the
same structure** the F11 cohort sampled:

- **42 of the 81 fleet keys currently hold ADA** (≥1,000); the other 39 are
  drained/dust reward-routing keys (near-zero balance).
- **34 of those 42 hold exactly 35,000,000 ADA** (within 2 ADA) — the same
  round parcel size as all eight F11 cohort keys — totaling **1,190,000,000
  ADA**. (A looser "within one 35M multiple" band catches 40 of 42, but that
  depends on a dust tolerance; the hard, defensible number is the 34 exact
  35M holders.)
- **All 42 holders delegate to `drep_always_abstain`** — identical governance
  posture to the F11 cohort.
- The 20 fleet holders in the `CERT_ACTIVE_PRINCIPAL_STATIC` pattern are spread
  across **14 different pools** (deliberate dispersion, as in F11) and are
  **all reward-swept 215–308 times** (the same epoch-cadence extraction).
- Total fleet-holder balance is **1,413,922,205 ADA**; adding the F11 cohort's
  280,000,000 ADA gives a combined **~1,693,922,205 ADA** on-chain custody
  surface across ~50 keys.

The F11 eight-key cohort was a small sample of a **~50-key, ~1.69-billion-ADA
institutional custody operation** built from uniform 35,000,000 ADA parcels,
uniform governance abstention, pool dispersion, and epoch-cadence reward
sweeps.

## Grade

- **FACT**: the parcel sizes, the 34 exact-35M holders and their 1.19B ADA sum,
  the unanimous `drep_always_abstain` delegation, the pool spread, the
  withdrawal counts, and the combined ~1.69B figure — all directly queryable in
  `fleet_control_indicators` at the recorded tip.
- **STRONG_INFERENCE**: the fleet and the F11 cohort are one operation. Shared
  withdrawal-transaction construction (F13, FACT) plus identical parcel size,
  identical governance posture, and identical reward-extraction cadence is not
  a coincidence of unrelated holders.
- **WORKING_HYPOTHESIS**: the operation is the founding-entity-linked custody
  lineage the depth-14 IOG trace descends from. The trace reaches these keys;
  it does not identify the operator. `fe_control_consistency` sits at MEDIUM
  for the holders (no multi-key certificate cohort exists *within* the fleet
  set — the fleet was found via shared withdrawals, not shared cert txs — so
  the batch-operation flag does not fire here even though F13 establishes shared
  control at signing time).
- **UNKNOWN**: legal/beneficial ownership, operator identity, and intent.

### Counterexamples and cautions

- **Managed-staking provider**: a custodian running uniform 35M client parcels
  could in principle produce this shape. What argues against "many unrelated
  clients" is the uniformity *combined with* shared withdrawal-transaction
  construction (F13) — a provider typically does not co-sign different clients'
  reward withdrawals in one transaction. This keeps "one operation" at
  STRONG_INFERENCE rather than FACT.
- **Not all 81 are holders**: 39 fleet keys are near-empty. They are part of
  the plumbing (reward-routing / drained keys), so "50-key operation" counts
  the ~50 keys that hold or held 35M parcels, not all 81 routing keys. The
  81-key figure is the shared-withdrawal fleet; the ~42 holders are the custody
  parcels.
- **Parcel count is a floor**: this classifies only the 81 keys discovered via
  one hop of shared withdrawals from the eight seed keys.
  [F15](F15_plumbing_component_is_closed_floor.md) iterates that sweep to
  fixpoint (115 keys, closed at round 3) and confirms the ~1.694B / 42-parcel
  surface is complete within reward-plumbing linkage — the wider sweep added 26
  keys but zero new parcels.

### Snapshot-boundary notes

All figures at live tip `13,630,389`+ (2026-07-03). Balances and delegation are
snapshot-sensitive; parcel sizes and withdrawal history are historical facts
that do not decay.

## Evidence

- `data/small/fleet_control_indicators.csv` (per-key classification, 81 rows)
- `data/small/fleet_control_summary.csv` (pattern × consistency rollup)
- `data/small/f11_downstream_fleet.csv` (the fleet root set, from F13)
- `data/manifests/fleet-control-indicators-manifest.json` (thresholds, tip)
- upstream: [F11](F11_eight_key_35m_custody_cohort.md),
  [F13](F13_reward_plumbing_downstream_and_tracer_bridge.md)

## Reproduce

From a clone (DuckDB):

```sql
-- the 35M parcel structure and unanimous abstention across the fleet
SELECT custody_pattern,
       COUNT(*)                                         AS keys,
       COUNT(*) FILTER (WHERE ABS(current_ada - 35000000) < 2) AS exact_35m,
       COUNT(*) FILTER (WHERE current_drep = 'drep_always_abstain') AS abstain,
       ROUND(SUM(current_ada), 0)                       AS total_ada
FROM fleet_control_indicators
WHERE current_ada >= 1000
GROUP BY custody_pattern
ORDER BY total_ada DESC;
```

Maintainers (warehouse):

```bash
ABCDE_SSH=<host> bash scripts/build_fleet_control_indicators_remote.sh
```

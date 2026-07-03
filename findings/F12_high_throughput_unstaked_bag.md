# F12 — High-throughput unstaked 213.8M-ADA bag reached by the IOG depth-14 trace

## Claim

Stake address
`stake1u9eacqarqgnjvqkr6wk9843mpr49jx8zeuzg4k4tpt9p08grvhlmc` held
**213,852,164 ADA across 1,492 UTxOs** at tip block `13,630,389` (2026-07-03)
and is operationally the opposite of the F11 cohort:

- First funded 2024-10-14; 4,944 lifetime output rows in under 21 months.
- **Actively moving on extraction day**: last outgoing 02:01 UTC, last
  incoming 12:11 UTC on 2026-07-03 (three new UTxOs and ~20k ADA arrived
  between two same-day extractions).
- **Never registered for staking, no delegation or governance certificate of
  any kind, zero rewards ever earned** — at this balance, roughly 5–6M ADA of
  staking rewards per year are being deliberately forfeited.
- The IOG depth-14 staged trace (rerun at the live boundary 2026-07-03)
  reaches **4 of its UTxOs, 56,165,056 ADA, at depth 14** — about 26% of the
  current balance; the traced parcels are unchanged since the 2026-06-07 cut
  while the rest of the bag churns around them.
- No overlap with the exchange-tracer dataset: none of the 70 tracer-touched
  addresses share this stake key (checked against `tracer_address_summary` at
  the same tip).

High UTxO count, high churn, no staking, no certificates, and round-the-clock
movement is the operating shape of a custodial/settlement wallet (exchange,
OTC desk, or payment processor). Forfeiting millions in staking rewards is
strong behavioral evidence of an operator that prioritizes liquidity and
stake-key invisibility over yield.

## Grade

- **FACT**: balance, UTxO count, activity timestamps, absence of any
  registration/delegation/withdrawal certificate, the depth-14 trace reach of
  the 56.16M traced subset, and the zero tracer overlap.
- **STRONG_INFERENCE**: single-operator high-throughput custody. The flow
  volume and UTxO management cadence are not retail behavior.
- **WORKING_HYPOTHESIS**: the wallet is an exchange-adjacent
  custodial/settlement operation, and the 56.16M traced subset represents
  IOG-descended value parked inside it. If correct, that traced parcel is an
  **exit-to-market signal** for genesis-descended value — but the trace shows
  those specific UTxOs have not moved since at least 2026-06-07.
- **UNKNOWN**: the operator's identity, whether the untraced ~158M shares
  provenance with the traced 56M, and whether the traced parcels belong to a
  customer or to the operator.

### Why this is not bundled into F11

The F11 cohort and this key both score as genesis-linked custody, but they are
different phenomena: F11 is static principal with synchronized certificates
and metronomic reward extraction (institutional treasury shape); F12 is
unstaked, certificate-free, high-churn liquidity (settlement shape). Merging
them would blur both signals — `custody_pattern` separates them as
`CERT_ACTIVE_PRINCIPAL_STATIC` vs `ACTIVE_MANAGED`, and
`fe_control_consistency` is `MEDIUM` for F11 keys but `LOW` here (activity
this recent and this liquid is weak evidence of *original-custodian*
retention; it is better evidence of third-party custody).

### Refutation tests (open)

- A tracer NFT landing at any address of this stake key would let the
  crowd-label layer test the exchange hypothesis directly.
- Convergence between this key's counterparty addresses and
  `tracer_deposit_claims` custody clusters would upgrade or kill the
  exchange reading.
- Movement of the four traced UTxOs (watch `iog_current_bag_depth14_*` on
  future refreshes) would convert the parked-parcel observation into a flow
  to follow.

### Snapshot-boundary notes

All figures at live tip `13,630,389` (2026-07-03); depth-14 trace values from
the same-day staged rerun (15:12 UTC). At the previous 2026-06-07 boundary the
traced subset was identical (4 UTxOs, 56.16M), while total-balance history
between boundaries is not part of the committed cut — no growth-rate claim is
made.

## Evidence

- `data/small/genesis_control_indicators.csv` (the
  `custody_pattern = 'ACTIVE_MANAGED'`, 213.8M row)
- `data/small/iog_current_bag_depth14_top_stake.csv` (traced subset, depth 14)
- `data/small/tracer_address_summary.csv` (no-overlap check)
- `data/manifests/genesis-control-indicators-manifest.json` (thresholds, tip)

## Reproduce

From a clone (DuckDB):

```sql
SELECT i.*, t.current_ada AS iog_traced_ada
FROM genesis_control_indicators i
LEFT JOIN iog_current_bag_depth14_top_stake t USING (stake_address)
WHERE i.stake_address =
  'stake1u9eacqarqgnjvqkr6wk9843mpr49jx8zeuzg4k4tpt9p08grvhlmc';
```

```sql
SELECT count(*) FROM tracer_address_summary
WHERE stake_address =
  'stake1u9eacqarqgnjvqkr6wk9843mpr49jx8zeuzg4k4tpt9p08grvhlmc';
```

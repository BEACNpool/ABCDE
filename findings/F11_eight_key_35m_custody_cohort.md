# F11 — Eight-key 35M-ADA custody cohort with synchronized certificates and enterprise-funded reward sweeps

## Claim

Eight stake addresses, each holding **exactly 35,000,000 ADA** at tip block
`13,630,389` (2026-07-03), form one operational cohort:

- All eight were first funded within a four-day window (2022-01-27 to
  2022-01-31), each from single-use **enterprise** (`addr1v…`, no stake part)
  input addresses.
- All eight registered and delegated in synchronized bursts: three stake
  registrations on 2022-01-24 within 2.5 hours; the remaining registrations
  and **all eight pool delegations on 2022-03-21 within a 3-hour window**
  (16:52–19:49 UTC) — each key to a **different** pool (two share
  `pool1fqas6y…`), one certificate transaction per key, minutes apart.
- None re-delegated since; then **all eight delegated to
  `drep_always_abstain` on 2025-02-09/10 within 7.5 hours**, again one tx per
  key.
- Each key's rewards are swept by ~307–309 withdrawal transactions
  (2,459 total — near one per epoch for 4+ years; ~3.9–4.1M ADA earned per
  key; unclaimed residue only 9–12k ADA). **Every withdrawal transaction is
  fee-funded exclusively by enterprise addresses** (zero self-funded inputs,
  zero staked external funders across all 2,459 txs) and **every output of
  those transactions pays enterprise addresses** (2,459/2,459; total tx output
  volume 2,223,505,114 ADA), keeping the reward flow invisible to stake-key
  tracking.
- All eight stake addresses are reached by the IOG depth-14 staged trace at
  depths 12–14, with trace-reached current value between 12.7M and 31.8M ADA
  per key at the trace's snapshot boundary.
- Despite intermittent spends (latest 2022-10 to 2023-09), each key's balance
  stands at exactly 35,000,000 ADA — consistent with internal reorganization
  rather than exit.

The pattern — identical round parcels, synchronized certificate bursts one tx
per key, deliberate pool dispersion, epoch-cadence reward extraction through
enterprise-only plumbing — is the shape of one professional custodian
operating all eight keys with automated tooling.

## Grade

- **FACT**: all figures above — balances, funding txs and their enterprise
  inputs, certificate txs and timestamps, withdrawal counts, the
  enterprise-only funding/destination property of all 2,459 withdrawal txs,
  and depth-12–14 IOG-trace reach — are directly queryable from the committed
  receipts and the warehouse.
- **STRONG_INFERENCE**: the eight keys are operated by a single
  custodian/toolchain. Independent owners do not buy identical 35M parcels in
  the same 4-day window, certify in the same minutes-apart bursts three years
  running, and share an enterprise-only fee-funding pipeline.
- **WORKING_HYPOTHESIS**: the custodian is the founding-entity lineage the
  depth-14 IOG trace descends from (`fe_control_consistency = MEDIUM`,
  `custody_pattern = CERT_ACTIVE_PRINCIPAL_STATIC` for all eight). The trace
  reaches the keys; it does not identify the operator.
- **UNKNOWN**: legal ownership, beneficial ownership, the operator's
  identity, and intent.

### Counterexamples and alternatives considered

- **Pure cold storage** (compare the 96 `NEVER_SPENT_COLD` keys in
  `genesis_control_indicators`): those show no certificate or withdrawal
  activity at all. This cohort is the opposite — continuously serviced.
- **Exchange hot wallet** (compare F12): exchange-pattern keys show irregular
  high-frequency third-party flows and typically no staking certificates.
  This cohort's flows are metronomic and internal.
- **Third-party staking custodian serving eight unrelated clients**: not
  eliminated. The identical parcel sizes, same-window funding, and shared
  fee-funding pipeline argue for one principal, but a custody service with
  pooled tooling could produce similar signatures. This is why single-operator
  stays STRONG_INFERENCE and FE-linkage stays WORKING_HYPOTHESIS.
- The always-abstain vote delegation (2025-02-09/10) is consistent with an
  institution avoiding governance exposure ahead of the post-Chang deadline
  for large stake, but many actors did the same; timing alone carries no
  attribution weight.

### Snapshot-boundary notes

- Custody indicators and balances: live tip `13,630,389` (2026-07-03).
- IOG depth-14 trace membership and trace-reached values: staged trace rerun
  at the live boundary on 2026-07-03 (snapshot 15:12 UTC); values are
  unchanged from the 2026-06-07 cut — the traced parcels have not moved.
  Per-key traced value covers 36–91% of each 35M balance, so "IOG-descended"
  applies to the traced portion, not automatically to every lovelace.
- These eight keys are absent from `governance_genesis_behavior_clusters`
  (that surface samples the top-1000 behavior clusters at its own snapshot);
  they enter the root set via `iog_current_bag_depth14_top_stake`.

## Evidence

- `data/small/genesis_control_indicators.csv` (the eight rows,
  `custody_pattern = CERT_ACTIVE_PRINCIPAL_STATIC`)
- `data/small/f11_cohort_funding_origin.csv` (receipt 3: first-funding txs
  and their enterprise inputs)
- `data/small/f11_cohort_cert_timeline.csv` (receipt 4: every certificate,
  tx hash, timestamp)
- `data/small/f11_cohort_withdrawal_funding.csv` (receipt 1: 0 self-funded,
  0 staked-external-funded withdrawal txs per key)
- `data/small/f11_cohort_external_funders.csv` (receipt 2: empty result —
  no staked external funder exists)
- `data/small/f11_cohort_reward_destinations.csv` (receipt 5: 2,459/2,459
  withdrawal txs output to enterprise addresses only)
- `data/small/iog_current_bag_depth14_top_stake.csv` (trace membership)
- SQL: `sql/10_findings/f11_cohort_*.sql`;
  manifest: `data/manifests/genesis-control-indicators-manifest.json`

## Reproduce

From a clone (DuckDB):

```sql
SELECT stake_address, current_ada, pool_delegation_certs, current_drep,
       withdrawal_count, rewards_earned_ada, custody_pattern
FROM genesis_control_indicators
WHERE custody_pattern = 'CERT_ACTIVE_PRINCIPAL_STATIC';
```

Maintainers with warehouse access:

```bash
for q in sql/10_findings/f11_cohort_*.sql; do
  ssh "$ABCDE_SSH" "sudo -n -u postgres psql -q -v ON_ERROR_STOP=1 \
    -d cexplorer_replica --csv -f -" < "$q"
done
```

# F13 — F11 reward-plumbing fleet, consolidation hubs, and a genesis→tracer-mapped-exchange bridge

## Claim

Following the enterprise-address reward plumbing of the F11 cohort downstream
reveals three things:

1. **A wider operator fleet.** The transactions that spend the cohort's
   withdrawal outputs ("exit transactions") also withdraw staking rewards for
   **81 other stake keys** that are not in the F11 cohort, moving
   **17,699,838 ADA** of those keys' rewards through the same transactions
   between 2022-04 and 2026-06. Building a withdrawal for stake key A and stake
   key B in one transaction requires holding both keys' credentials at that
   moment — FACT-grade shared control at signing time. The eight-key cohort is
   the tip of an operation servicing at least 89 stake keys.

2. **The plumbing funnels into exchange-scale hot addresses.** The first
   external hop routes overwhelmingly (96.5% of the top-200 hop-1 destinations
   by value) into **enterprise addresses**, dominated by four:
   `addr1v8v3auqmw…ydzvs5`, `addr1v95sf69j…scta2yzg`, `addr1vypr00ss…gst3pe4`,
   and `addr1v9u7va2s…q9nnwl9`. Each of these has **1.0–1.5 million lifetime
   outputs and gross received ADA of 118–172 billion** — i.e. each has received
   **2.5×–3.8× the entire ~45.6B ADA supply** over its life. Gross receipts
   exceeding total supply is only possible if the same coins recirculate
   through the address millions of times, which is the structural signature of
   a **recirculating settlement / exchange-scale hot address**, not an
   accumulation sink. Hop-1 gross routed value from the F11 plumbing is ~2.08B
   ADA; this too is **flow-through, not distinct principal** — the
   caterpillar-style withdrawal chain recirculates value through these hubs
   across four years, so the figure measures routing activity, not a balance.

3. **A bridge to a tracer-mapped, Kraken-claimed deposit cluster.** One hop-1
   destination is stake key
   `stake1u833p40y8cm07ra9wgrqgp…`, which received **2,140,863 ADA** directly
   from the reward plumbing at hop 1 (more across hops 2–3). That same stake
   key was **independently flagged by the community exchange-tracer campaign**:
   it holds 15+ tracer NFTs, and **15 tracer deposit-claim transactions name it
   "Kraken."** Two independent datasets — the genesis-descended reward trace
   (this repo's warehouse extraction) and the crowd tracer campaign — converge
   on the same cluster.

## Grade

- **FACT**:
  - the 81 non-cohort stake keys sharing withdrawal transactions, and the
    17.70M ADA of their rewards so moved;
  - the hop-1 concentration into four enterprise hubs, each with 1.0–1.5M
    lifetime outputs and 118–172B ADA gross received;
  - the 2,140,863 ADA routed from the reward plumbing to
    `stake1u833p40y…` at hop 1;
  - that `stake1u833p40y…` holds 15+ tracer NFTs and that 15 tracer
    deposit-claim transactions carry the string "Kraken."
- **STRONG_INFERENCE**: the 81 fleet keys and the 8-key cohort are one
  operation. Shared-key withdrawal construction, repeated across four years and
  funneling into the same two hubs, is not coincidental co-signing.
- **WORKING_HYPOTHESIS**:
  - the four enterprise hubs are exchange/settlement hot addresses (the
    supply-exceeding gross throughput is the structural evidence; which specific
    exchange is not established here);
  - genesis-descended reward value has reached an exchange (Kraken) deposit
    address — i.e. an **exit-to-market** event for that 2.14M ADA slice.
- **UNKNOWN / explicitly not claimed**:
  - The Kraken attribution is the tracer **sender's self-report**, not Kraken's
    confirmation (see `tracers/README.md` grading). The bridge upgrades to
    STRONG_INFERENCE only if independent submitters or Kraken's own published
    deposit addresses corroborate the cluster.
  - Hop-2 and hop-3 destination values are path tx-output aggregates that
    include unrelated value entering those transactions; **no taint accounting
    or proportional attribution is claimed** beyond hop 1.
  - Legal ownership, identity, and intent of any address remain UNKNOWN.

### Counterexamples and cautions

- **Gross vs net**: the multi-billion hop totals are recirculation, not
  holdings. The honest magnitude of *rewards* extracted is the F11 figure
  (~31–33M ADA withdrawn across the 8 keys) plus the 17.70M across the fleet.
- **Shared-tx ≠ same owner in every case**: batching services can co-sign
  unrelated clients' withdrawals. The dominance of two hubs and the
  single-operator F11 signature make one operator the strong reading, but a
  managed-staking provider is not excluded — hence STRONG_INFERENCE, not FACT,
  for "one operation."
- **The Kraken node is a deposit cluster, not Kraken's treasury**: value
  reaching a deposit address means it was sent *toward* the exchange by
  whoever controls the sending key; it does not mean Kraken owns the genesis
  ADA.

### Snapshot-boundary notes

All receipts extracted at live tip `13,630,389`/`13,632,393` (2026-07-03).
Tracer membership and deposit claims are from the committed `tracer_*` cut
(same day). The reward-plumbing structure is historical and does not decay;
the hub current balances are snapshot-sensitive.

## Evidence

- `data/small/f11_downstream_fleet.csv` (81 fleet keys, shared-tx rewards)
- `data/small/f11_downstream_hop_summary.csv` (per-hop rollup)
- `data/small/f11_downstream_hop_destinations.csv` (top destinations, hops 1–3)
- `data/small/f11_hub_classification.csv` (hub lifetime profiles)
- `data/small/tracer_address_summary.csv`, `data/small/tracer_deposit_claims.csv`
  (the Kraken-claimed cluster)
- SQL: `sql/10_findings/f11_downstream_fleet.sql`,
  `f11_downstream_hops_staged.sql`, `f11_hub_classification.sql`

## Reproduce

From a clone (DuckDB):

```sql
-- the genesis→Kraken-claimed bridge, cross-validated across two datasets
SELECT d.hop, d.destination, d.total_ada,
       s.distinct_tracers_ever, s.distinct_tracers_now
FROM f11_downstream_hop_destinations d
JOIN tracer_address_summary s ON s.stake_address = d.destination
WHERE d.destination LIKE 'stake1u833p40y%';

SELECT DISTINCT metadata_json
FROM tracer_deposit_claims
WHERE metadata_json LIKE '%Kraken%';
```

Maintainers (warehouse):

```bash
for q in f11_downstream_fleet f11_downstream_hops_staged f11_hub_classification; do
  ssh "$ABCDE_SSH" "sudo -n -u postgres psql -q -v ON_ERROR_STOP=1 \
    -d cexplorer_replica -f -" < "sql/10_findings/$q.sql"
done
```

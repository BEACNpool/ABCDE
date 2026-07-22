# F17 — Wanchain NIGHT bridge drain, token provenance, and attacker flow

## Claim

The Wanchain Cardano ↔ BNB Chain NIGHT bridge was drained on 2026-07-20, and
ABCDE reproduces the Cardano-side incident from bridge inventory through the
attacker's first monetization and dispersal paths:

- Four transactions between `14:46:50` and `14:55:05 UTC` transferred exactly
  **515,206,545.426856 NIGHT** from the bridge to the first attacker wallet
  cluster. That was **97.751708%** of the bridge's immediately pre-attack NIGHT
  balance.
- A common provider cluster supplied **687,961,318.3 NIGHT** across seven major
  bridge deposits. Three branches of that provider descend directly from
  settlement outputs 12–14; settlement outputs 12–15 total
  **3,660,000,000.01 NIGHT**, matching Midnight TGE Ltd.'s disclosed 3.66B
  allocation to the 0.01-NIGHT settlement balancing adjustment.
- The bridge received 370M NIGHT immediately before Binance Alpha's December
  2025 NIGHT launch. The provider later routed exactly **240M NIGHT** through a
  two-output Cardano path on 2026-03-11, matching Binance's published 240M-NIGHT
  HODLer Airdrop allocation. Wanchain independently stated that Binance chose
  Wanchain-wrapped NIGHT for distribution.
- The attacker routed **68,273,140.469065 NIGHT net** into the qNIGHT/Liqwid
  contract and borrowed **4,364,479.583143 ADA**. Before the first public trace,
  it staged **3.75M ADA** through 39 exchange-style deposit addresses.
- Of those staged deposits, 1.45M ADA was swept through the same high-throughput
  `credit.pay` aggregation rail that pre-funded W1, and 700K ADA was co-spent in
  transactions feeding the independently tagged Binance 1 wallet. A later
  route placed **32.25M ADA** into **6,450 fresh, unspent addresses**, exactly
  5,000 ADA each.

These facts establish the drain, Cardano-side token provenance, commercial
distribution linkage, and attacker flow. They do **not** identify the natural
person behind the wallets or establish any off-chain intent.

## Grade

- **FACT:** the four drain transactions, times and values; bridge balances;
  settlement-output values; provider-to-bridge flows; exact 240M-NIGHT path;
  W1–W4 sequencing; Liqwid collateral and borrowing amounts; current balances;
  staged-deposit counts; direct co-spends; and the 6,450-address fan-out. These
  are reproduced directly from ABCDE/db-sync.
- **EXTERNAL_CORROBORATION:** BlockSec's TreasuryCheck validator root-cause
  analysis; Wanchain's incident acknowledgement and Binance-distribution
  statement; Midnight Foundation's containment notice; Binance's campaign and
  240M-NIGHT allocation notices; and Midnight's allocation/unlock disclosures.
  The report preserves direct links and keeps these separate from warehouse
  facts.
- **STRONG_INFERENCE:** settlement outputs 12–15 are the TGE allocation;
  `addr1vy26…` is Binance NIGHT distribution/custody; and `credit.pay` is a
  centralized-exchange aggregation rail. Exact value matches, direct funding,
  transaction structure, and public attribution support these labels, but do
  not prove beneficial ownership.
- **UNKNOWN:** the attacker's legal identity, country, exchange accounts,
  whether any Wanchain signer/key was separately compromised, and who operates
  `credit.pay`. Off-chain intent is out of scope for a Cardano warehouse.

### Scope boundary

The bridge inventory descends from the genesis settlement transaction and did
not pass through the community thaw contracts; per Midnight's published
tokenomics paper the Foundation and TGE Ltd. entity allocations were unlocked
with no protocol lockup, separate from the community claim pool. This finding
records that provenance as on-chain data and takes no position on off-chain
ownership, control, intent, or any exchange's participation — those are outside
what Cardano db-sync can establish.

### Snapshot boundary

Historical transaction paths are stable. Unspent balances and the status of
the 6,450 fan-out outputs are snapshot-sensitive. The report snapshot ends at
block `13,708,969`, `2026-07-22 02:27:16 UTC`; the full verification rerun
passed at block `13,709,033`, `2026-07-22 02:51:03 UTC`.

## Evidence

- **Query-ready tables (clone-and-ask, no node):** the `night_incident_*` tables in the compact
  DuckDB — `night_incident_summary` (headline metrics + grades), `night_incident_drain_txs`,
  `night_incident_bridge_balance`, `night_incident_actors` (labeled wallets + roles + balances),
  `night_incident_ada_fanout` (the 6,450 fresh 5,000-ADA addresses), `night_incident_staged_deposits`,
  `night_incident_liqwid_collateral`, `night_incident_bridge_supply`,
  `night_incident_settlement_provenance`, `night_incident_binance_240m`,
  `night_incident_cluster_balance`, `night_incident_label_balances`.
- Data report and external-source links: `reports/night_wanchain_incident_2026_07_20.md`
- Read-only warehouse receipt query (regenerates the tables):
  `sql/40_night/night_wanchain_incident_2026_07_20.remote.sql`
- NIGHT module and full-supply provenance context:
  `docs/25_NIGHT_TOKEN_PROVENANCE.md`

## Reproduce

Run against the live `cexplorer_replica` warehouse with `psql`:

```sql
\i sql/40_night/night_wanchain_incident_2026_07_20.remote.sql
```

The script is read-only apart from session-local temporary tables and stops on
the first SQL error.

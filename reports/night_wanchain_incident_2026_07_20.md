# NIGHT / Wanchain bridge incident — Cardano-side data report

- **Incident:** Wanchain Cardano ↔ BNB Chain NIGHT bridge drain
- **Attack window:** 2026-07-20 14:46:50–14:55:05 UTC
- **Asset:** NIGHT, policy `0691b2fecca1ac4f53cb6dfb00b7013e561d1f34403b957cbb5af1fa`, fingerprint `asset1wd3llgkhsw6etxf2yca6cgk9ssrpva3wf0pq9a`
- **Graded finding:** [`F17`](../findings/F17_night_wanchain_bridge_incident.md)
- **Reproduction SQL:** [`night_wanchain_incident_2026_07_20.remote.sql`](../sql/40_night/night_wanchain_incident_2026_07_20.remote.sql)
- **Query-ready tables:** `night_incident_*` in the compact DuckDB — see [`docs/25_NIGHT_TOKEN_PROVENANCE.md`](../docs/25_NIGHT_TOKEN_PROVENANCE.md)

This report states only what the Cardano chain shows, graded FACT / STRONG_INFERENCE / UNKNOWN.
Every number is reproducible from a plain clone — query the tables listed below, don't trust the
prose. On-chain linkage is never off-chain ownership, control, or intent.

## What happened

Four transactions moved **515,206,545.426856 NIGHT** out of the bridge's Cardano-side lock
address into one attacker wallet (W1) in 8 minutes 15 seconds — **97.751708%** of the bridge's
immediately pre-attack NIGHT balance. This is a bridge-contract drain; it is not a NIGHT mint and
touches nothing in Midnight's own consensus. *(FACT — `night_incident_drain_txs`,
`night_incident_bridge_balance`.)*

| UTC | Transaction | NIGHT → W1 |
|---|---|---:|
| 14:46:50 | `0a4861be5dd1cd0a5ccd7d38855ef8fe233563274c22c27adb4f5980535d2ea1` | 203,001,692.164714 |
| 14:51:25 | `ba4edf844c8dc1289a63660a33a720d24d7dd83825222354b09aee5847132305` | 129,633,878.020714 |
| 14:53:18 | `e4ff7b122df4bc78dc151089a581eedf7997974eaeb74df011a09a889de6f1d7` | 120,430,264.324714 |
| 14:55:05 | `fe9e9de054459578dbfaa5507f447ea4453a7525f801b526d9ffebe6753aaf3d` | 62,140,710.916714 |
| **Total** | | **515,206,545.426856** |

Bridge NIGHT balance: **527,056,309.124849** before → **11,847,785.641993** after.

External root-cause analysis (off-chain, linked for reference, not an ABCDE claim): BlockSec
Phalcon attributes the first extraction to a non-injective signed-message encoding in Wanchain's
TreasuryCheck validator, tracing the authorizing signature to a legitimate BSC transaction that
covered ~3,110 NIGHT and was reused to extract 203,001,692 NIGHT
([root-cause](https://x.com/Phalcon_xyz/status/2079443108027421183),
[signature reuse](https://x.com/Phalcon_xyz/status/2079451633847783655)). Wanchain acknowledged the
withdrawal and disabled the bridge; Midnight Foundation described it as an isolated third-party
bridge incident with its own protocol/validators unaffected
([Wanchain](https://x.com/wanchain_org/status/2079444149066244340),
[Midnight](https://x.com/midnightfdn/status/2079546529673609701)). Primary public on-chain trace:
[UTxOMaestro thread](https://x.com/UTxOMaestro/status/2079324720600649737).

## The attacker wallets

Four wallets, one operator — linked by direct ADA transfers, not co-spend/CIOH heuristics.
Full addresses, roles, grades and current balances are in `night_incident_actors`.

- W1 `addr1qysj48kpy8qra2g64scvu79n489qrv2uys5ggsrun29v5f5udqxfpr7x0pqfl6khjwv6vm0k8s3spn6h0zfrwszfqgcqeld8kj` — received the drain, sold NIGHT on DEXs, staged exchange deposits.
- W2 `addr1qx7haxyr5qdwcpkvdjmrjnk8wzrsyh7usaajpt3crmted5nkw3n3ner7p6vjudr5urnxywhx0zj5e487w5d3ry4s6nsq2k7aq5` — collateralized NIGHT in qNIGHT/Liqwid; round-tripped funds with W1.
- W3 `addr1qyx992x3khmvc0leu8qge5gs4yys53eecarkx29cyekqfzscummv9adtkfu3qsssupfzxgv5vldajdnuj8926xa8kn0q3mhtym` — fresh ADA vault; forwarded ADA to W4.
- W4 `addr1q8qr45yl9tlllu3cnl28qq279lqrkdea0rg59djn5qfrkv6lt4lqq28h3f60vyrxductvufgcpcc7p5uk5s07th87s4s3qvakc` — dispersed ADA into the 6,450-address fan-out.

Because W1 and W2 exchanged funds back and forth, single "W1→W2 = X" totals are ambiguous by
design; the durable facts are the tables below. *(FACT — `night_incident_cluster_balance`.)*

## Where the value went

- **NIGHT collateral:** W2 deposited **68,273,140.469065 NIGHT net** into the qNIGHT/Liqwid
  lending contract across 5 transactions. *(FACT — `night_incident_liqwid_collateral`.)*
- **Staged exchange deposits:** before the public thread, W1 fanned **3,750,000 ADA** into 39
  exchange-style deposit addresses (50K/100K-ADA outputs), swept toward the `credit.pay` and the
  community-tagged **Binance 1** rails. *(FACT — `night_incident_staged_deposits`.)*
- **The wallet farm:** W3→W4 created **6,450 fresh base addresses holding exactly 5,000 ADA each
  (32,250,000 ADA total), none spent** at the snapshot. Every payment and stake credential first
  appeared in this fan-out. *(FACT — `night_incident_ada_fanout`.)*

The 39-address staging and the 6,450-address farm are distinct patterns — the first was swept into
aggregators immediately, the second is a later, still-unspent farm. Do not conflate them.

## Where the bridge NIGHT came from

- W1 was created **2026-07-20 10:29:36** — ~4h before the first drain tx — with
  **4,621.558246 ADA** from the wallet holding the **`$credit.pay` ADA Handle**, a high-throughput
  aggregation rail. *(FACT it holds the handle and funded W1; the exchange behind it is UNKNOWN.)*
- The bridge NIGHT inventory descends from the genesis settlement transaction
  `7a906cde274e3cbdc7e78945b8c0b46bedeb22bba83c40424ebe6d84f546986c`. Its outputs 12–15 total
  **3,660,000,000.01 NIGHT**. A single provider cluster fed by those branches supplied
  **687,961,318.3 NIGHT** to the bridge across seven major deposits, including 120M (Dec 6) +
  240M (Dec 7) + 10M (Dec 8) immediately before the Binance Alpha NIGHT launch, and on 2026-03-11
  routed **exactly 240,000,000 NIGHT** (95 + 239,999,905, both provider-funded) into a Binance
  distribution/custody address. *(FACT for the on-chain sums/flows; STRONG_INFERENCE for the entity
  labels — `night_incident_bridge_supply`, `night_incident_settlement_provenance`,
  `night_incident_binance_240m`.)*

The bridge inventory did not pass through the community Glacier Drop / Scavenger Mine thawing
contracts. Per Midnight's published tokenomics paper, the Foundation and TGE Ltd. entity
allocations were unlocked with no protocol lockup, separate from the community claim pool that
thaws in four 25% tranches ([tokenomics paper, pp. 44–46](https://45047878.fs1.hubspotusercontent-na1.net/hubfs/45047878/Midnight-Tokenomics-And-Incentives-Whitepaper.pdf)).
This report records that provenance as data and takes no position beyond it.

## Grades

- **FACT:** transaction hashes, times, values, balances, wallet sequencing, settlement parcel
  sums, provider→bridge deposits, Liqwid flows, deposit/fan-out counts — all reproduced from
  ABCDE/db-sync and shipped as the `night_incident_*` tables.
- **STRONG_INFERENCE:** settlement outputs 12–15 are the disclosed TGE allocation;
  `addr1vy26…` is a Binance NIGHT distribution/custody address; `credit.pay` is an exchange-style
  aggregation rail. Supported by exact value matches, direct funding and public attribution — not
  proof of beneficial ownership.
- **UNKNOWN:** the attacker's natural-person identity, country, which exchange operates
  `credit.pay`, and whether any Wanchain signer/key was separately compromised. These are KYC /
  subpoena questions the Cardano chain cannot answer.

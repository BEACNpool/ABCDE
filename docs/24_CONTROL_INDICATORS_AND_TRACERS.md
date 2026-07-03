# Control Indicators, Freshness Catalog, and Exchange Tracers

Added 2026-07-03. Three surfaces that deepen the compact database: quantified
freshness/accuracy, custody-pattern control indicators for genesis-descended
stake, and the Genesis Trail exchange-tracer dataset.

## 1. Freshness and accuracy quantification

Table `data_freshness_catalog` (built by `scripts/build_freshness_catalog.py`)
has one row per committed table: row count, byte size, SHA-256, last git commit
time, age in days at refresh, and a `snapshot_sensitive` flag.

Reading it correctly:

- **Historical fact receipts never decay.** Mint events, past transactions,
  anchor verifications, first spends — correct forever once verified.
- **`snapshot_sensitive = true` tables decay.** Current UTxOs, latest
  delegation targets, live profiles are only accurate as of the tip in
  `db_tip_receipt` (or an older per-table receipt/commit time if the table
  was not refreshed in the latest cut).
- To bound any answer's accuracy: cite the table's `last_commit_utc`, the
  `db_tip_receipt` tip, and whether the table is snapshot-sensitive.

Genesis **authenticity** is separately re-proven on every refresh:
`seed_anchor_db_verification` re-verifies the four genesis anchor txs
(hashes and amounts in `anchors.yaml`) against db-sync, and every derived
table carries SHA-256 receipts in `data/manifests/`.

## 2. Genesis control indicators (`genesis_control_indicators`)

For ~1,000 genesis-descended stake addresses (the founders depth-14 behavior
clusters plus the IOG depth-14 top-stake set), live-tip custody indicators:

- activity: first/last received, last outgoing, current UTxOs and ADA
- certificate state: registration, pool delegation (count + latest target),
  DRep delegation (count + latest target)
- rewards: earned, withdrawn, **unclaimed**, last withdrawal
- derived flags: `never_spent`, `principal_static`, `keys_alive_recent_cert`,
  `rewards_never_withdrawn`, `institutional_passivity`, `batch_operated`
- classes: `custody_pattern` and `fe_control_consistency`

`genesis_control_cert_cohorts` lists certificate transactions in which **two
or more** set members were certified together. One transaction certifying many
stake keys was constructed by one wallet at that moment — that shared-control
linkage at signing time is FACT-grade; who operates the wallet is not
established by it.

### The wording rule applied

`fe_control_consistency` (HIGH / MEDIUM / LOW / EXITED_OR_DISPERSED /
INDETERMINATE) is a **WORKING_HYPOTHESIS** classification meaning: *the
on-chain pattern is consistent with the original custodian still holding the
keys.* Signals used, and why:

- **Recent certificates over static principal** — a re-delegation last year on
  a stake key whose funds haven't moved in 5 years proves someone holds the
  key *now* while the principal stays parked. Keys alive + principal static is
  the classic institutional-custody shape.
- **Never-withdrawn rewards** at meaningful size — retail rotates and spends;
  a treasury that never claims rewards across years is passivity at
  institutional scale.
- **Batch operation** — membership in multi-key certificate transactions ties
  keys to a common operator at signing time.

It never asserts legal ownership, identity, or intent. Thresholds are fixed
constants recorded in `data/manifests/genesis-control-indicators-manifest.json`;
changing them is a new data version. Rebuild:
`ABCDE_SSH=<host> bash scripts/build_genesis_control_indicators_remote.sh`.

## 3. Exchange tracers (`tracer_*` tables)

The community's Genesis Trail exchange-tracer campaign: 505 tracer NFTs
(policy `d8d5539ee11f21a6748735aeb69d3ed935bb14570f57709279031119`) sent to
suspected exchange deposit addresses. Deposit addresses sweep into custody
wallets, so tracer movement maps custody clusters publicly and replayably.

Tables: `tracer_address_summary`, `tracer_stake_summary`,
`tracer_asset_current_location`, `tracer_current_utxos`, `tracer_all_outputs`,
`tracer_transfer_edges`, `tracer_mint_events`, `tracer_mint_funding_inputs`,
`tracer_deposit_claims`, `tracer_movement_timeline`, `tracer_export_tip_receipt`.

`tracer_deposit_claims` carries the senders' own on-chain CIP-20 messages —
six exchanges are named (Coinbase, Kraken, Binance, KuCoin, Bybit, Gate.io) in
56 labeled transactions. Grade those as **self-reported claims**: the message
existing on-chain is FACT; the sender's assertion about the destination is
WORKING_HYPOTHESIS until independently corroborated (convergent independent
claims on one custody cluster, or sweep-pattern confirmation via
`tracer_transfer_edges`).

Full receipts, refresh script, and the crowd-label template live in
[`tracers/`](../tracers/README.md).

## Why tracers matter for the genesis question

If genesis-descended value moves to an address inside a tracer-mapped custody
cluster, "reached an exchange-claimed cluster" becomes statable with a grade —
an exit-to-market signal — while wallets that never touch mapped clusters and
score HIGH on control consistency look retained. Both directions sharpen the
core question: **who still holds the genesis ADA, and has it gone to market?**

# Tracers — Genesis Trail exchange-tracer dataset

Deterministic receipts for **The Genesis Trail exchange tracer** NFT policy:

```
policy_id: d8d5539ee11f21a6748735aeb69d3ed935bb14570f57709279031119
```

505 single-quantity tracer NFTs were minted (CIP-25 metadata on each mint tx:
`"on-chain forensics tracer, not a collectible"`, project `"The Genesis Trail
exchange tracer"`) and sent to addresses of interest — primarily suspected
exchange deposit addresses. Because a deposit address sweeps into an exchange's
custody wallets, watching where a tracer NFT lands and moves gives a public,
replayable signal of which custody cluster an address feeds.

## What this dataset proves — and what it does not

- **FACT:** every row here is directly queryable from the Cardano chain via a
  db-sync schema. "Tracer X reached address Y at block Z" and "tracer X
  currently sits at address W" are facts, reproducible from any db-sync
  instance with the SQL in `sql/` and `scripts/`.
- **NOT proven:** "address Y belongs to exchange E." Attribution requires
  labels (deposit-address receipts, exchange statements, corroborated
  crowd-sourced submissions). Until a label with evidence exists in
  `labels/exchange_labels.csv`, treat any exchange naming as
  **WORKING_HYPOTHESIS** at best. Per the repo-wide wording rule: on-chain
  linkage is not real-world identity or control.

## Snapshot provenance

`data/export_tip_receipt.csv` records the warehouse tip (block number and
block time) and UTC export timestamp for the committed cut. All CSVs in
`data/` come from one export run and are hashed in `data/SHA256SUMS`.

Current cut: tip block `13,628,563` (2026-07-03 04:54:49 UTC) —
505 tracers minted, 70 addresses ever touched, 24 addresses currently
holding, 2,829 historical output rows, 505 live tracer UTxOs, 0 burned.

## Files

| file | grain | what it answers |
|---|---|---|
| `data/export_tip_receipt.csv` | 1 row | when/at what tip this cut was taken |
| `data/address_summary.csv` | per payment address | who ever touched / currently holds tracers, first/last seen, current asset list |
| `data/stake_summary.csv` | per stake address | entity-level rollup (addresses sharing a stake key) |
| `data/current_tracer_utxos.csv` | per live UTxO | exactly where each tracer sits right now |
| `data/asset_current_location.csv` | per tracer NFT | one row per asset: mint time, hops, addresses touched, current location |
| `data/all_tracer_outputs.csv` | per historical output row | the full movement history of the policy |
| `data/transfer_edges.csv` | per (asset, spend) hop | from-address → to-address edges for every tracer move |
| `data/mint_events.csv` | per asset mint | mint tx + full on-chain CIP-25 metadata |
| `data/mint_funding_inputs.csv` | per (mint tx, input address) | which addresses funded each mint (tracer operator's on-chain linkage) |
| `data/movement_timeline.csv` | per day | daily activity: rows, assets, addresses, txs |
| `data/deposit_claims.csv` | per (tx, metadata key) | on-chain tx messages attached to tracer moves, incl. senders' "Deposited to: \<Exchange\>" claims |
| `labels/exchange_labels.csv` | per labeled address | attribution layer — **starts empty by design** |
| `sql/exchange_tracer_policy.sql` | — | standalone psql report query (any db-sync instance) |
| `scripts/export_tracers_from_abcde.sh` | — | maintainer refresh script (regenerates `data/` + `SHA256SUMS`) |

## Reading the data

- **"Which addresses look like exchange deposit sweeps?"** Start with
  `address_summary.csv`: addresses with high `distinct_tracers_ever` but low
  `distinct_tracers_now` received tracers and swept them onward. Then follow
  those assets in `transfer_edges.csv` to see where they consolidated.
- **"Where did tracers pile up?"** `stake_summary.csv` — e.g. the top stake
  key currently holds 100 distinct tracers on a single address; consolidation
  points like that are custody-cluster candidates (WORKING_HYPOTHESIS until
  labeled).
- **UTxO liveness note:** on the ABCDE logical subscriber, liveness is
  computed with `tx_in` anti-joins. Do **not** use
  `tx_out.consumed_by_tx_id` there — it is not reliably populated on the
  replica.

## On-chain exchange claims (`data/deposit_claims.csv`)

Many deposit transactions carry a CIP-20 (key `674`) message written by the
sender, e.g. `"Deposited to:", "Coinbase", "The Red (or Blue) Pill Study",
"tracer.adagenesistransparency.com"`; one tx uses a custom key `1985`
(`{"exchange": "Kraken"}`). Six exchanges are named this way: **Coinbase,
Kraken, Binance, KuCoin, Bybit, Gate.io**.

Grade these as **self-reported claims** (WORKING_HYPOTHESIS →
STRONG_INFERENCE once corroborated): the message is on-chain (FACT that it
was written), but it is the *sender asserting* which exchange the destination
address belongs to, not the exchange. Corroboration comes from independent
submitters naming the same entity for the same custody cluster, or from
sweep-pattern analysis in `transfer_edges.csv`.

## Attribution labels (`labels/exchange_labels.csv`)

Columns: `address, stake_address, claimed_entity, label_type, evidence,
evidence_url, submitted_by, submitted_date, grade`.

- `label_type`: e.g. `deposit_address` (a tracer was sent to an address the
  submitter generated at the exchange), `hot_wallet`, `self_report`, `other`.
- `evidence`: what backs the claim (screenshot hash, tx receipt, statement).
- `grade`: per `docs/02_GRADING.md` — `FACT` only if deterministically
  checkable on-chain; deposit-address receipts are typically
  `STRONG_INFERENCE`; unverified submissions are `WORKING_HYPOTHESIS`.

A tracer landing at a labeled address upgrades "tracer reached address Y" to
"tracer reached an address labeled E (grade G)" — the claim never gets
stronger than its label's grade.

## Refreshing (maintainer only)

```bash
tracers/scripts/export_tracers_from_abcde.sh
```

Requires SSH access to the ABCDE warehouse (`ssh abcde`, read-only queries
against `cexplorer_replica`). Public users don't need this — the committed
CSVs plus `SHA256SUMS` are the reproducibility cut, and
`sql/exchange_tracer_policy.sql` reruns the core report on any db-sync
instance.

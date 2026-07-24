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

## Canonical study method

The study operator publishes an agent guide defining how this dataset must be
reconstructed and how far its conclusions may be pushed: deterministic
wallet-cluster keys, strict deposit validation, exact NFT paths, terminus
grouping, and a participant-vote threshold for resolving an exchange name.
Source: <https://tracer.adagenesistransparency.com/TRACER_README.md>
(retrieved 2026-07-24; the document is unversioned).

ABCDE implements those rules against its own db-sync warehouse (sections 11–16
of `scripts/export_tracers_from_abcde.sh`) and ships the result as the
`tracer_method_receipt`, `tracer_asset_path`, `tracer_valid_deposits`,
`tracer_name_votes`, `tracer_terminus_clusters` and `tracer_terminus_census`
tables. **Read `docs/26_EXCHANGE_TRACER_METHOD.md` before answering any
question from this dataset** — it is the rule set, the strictness notes, and
the limits.

The older tables in this directory stay as raw receipts; they are deliberately
looser than the method tables (`deposit_claims.csv`, for example, holds every
674/1985 message attached to a tracer-moving transaction, including unrelated
674 traffic from other applications).

## Snapshot provenance

`data/export_tip_receipt.csv` records the warehouse tip (block number and
block time) and UTC export timestamp for the committed cut. All CSVs in
`data/` come from one export run and are hashed in `data/SHA256SUMS`.
`data/method_receipt.csv` additionally records the identifiers and rules the
method tables were built with.

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
| `data/method_receipt.csv` | 1 row | canonical identifiers, rules and threshold used for this cut |
| `data/asset_path.csv` | per (asset, hop) | the exact ordered holder path of every tracer, with cluster keys |
| `data/valid_deposits.csv` | per validated deposit | deposits passing all four validation rules: participant, claimed name, current terminus |
| `data/name_votes.csv` | per (terminus, name) | tracer count vs distinct-participant count per claimed name |
| `data/terminus_clusters.csv` | per terminus reached by a tagged deposit | resolution result + full name split (conflicts preserved) |
| `data/terminus_census.csv` | per terminus, all tracers | the denominator — where every tracer sits now |
| `labels/exchange_labels.csv` | per labeled address | attribution layer — **starts empty by design** |
| `sql/exchange_tracer_policy.sql` | — | standalone psql report query (any db-sync instance) |
| `scripts/export_tracers_from_abcde.sh` | — | maintainer refresh script (regenerates `data/` + `SHA256SUMS`, publishes `data/small/tracer_*.csv`) |

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
(`{"exchange": "Kraken"}`). Seven exchanges are named this way: **Coinbase,
Kraken, Binance, KuCoin, Bybit, Gate.io, UEX.us**.

Grade these as **self-reported claims** (WORKING_HYPOTHESIS →
STRONG_INFERENCE once corroborated): the message is on-chain (FACT that it
was written), but it is the *sender asserting* which exchange the destination
address belongs to, not the exchange.

This file is the raw evidence, not the vote. It includes 674 traffic from
unrelated applications and the `1985` study-seed label. The corroboration bar
lives in `valid_deposits.csv` / `name_votes.csv` / `terminus_clusters.csv`: a
name resolves only on a **unique lead of ≥2 distinct pre-deposit wallet-cluster
keys** converging on the same terminus cluster.

## Attribution labels (`labels/exchange_labels.csv`)

Columns: `address, stake_address, claimed_entity, label_type, evidence,
evidence_url, submitted_by, submitted_date, grade`.

Rows are **mechanically derived** from the method tables by
`scripts/build_exchange_labels.py` — never hand-entered — so every grade is
reproducible from the committed CSVs.

- `label_type`:
  - `custody_cluster` — a terminus wallet-cluster whose name resolved (unique
    participant lead, ≥2 distinct participant wallets).
  - `deposit_address` — an address a participant deposited a tracer to,
    carrying that participant's claim.
- `evidence`: tracer and participant counts plus the full vote split or the
  terminus resolution status behind the row.
- `grade`: per `docs/02_GRADING.md`. A deposit address **cannot** be
  corroborated by other participants — an exchange issues each user their own
  deposit address, so its claim count is thin by construction. Its support
  therefore comes from the terminus its tracers reach: `STRONG_INFERENCE` when
  that terminus resolved to the same name, `WORKING_HYPOTHESIS` otherwise.

A tracer landing at a labeled address upgrades "tracer reached address Y" to
"tracer reached an address labeled E (grade G)" — the claim never gets
stronger than its label's grade.

## Refreshing (maintainer only)

```bash
tracers/scripts/export_tracers_from_abcde.sh   # refresh data/ + data/small/tracer_*.csv
python tracers/scripts/build_exchange_labels.py # re-derive labels/exchange_labels.csv
```

Requires SSH access to the ABCDE warehouse (`ssh abcde`, read-only queries
against `cexplorer_replica`). Public users don't need this — the committed
CSVs plus `SHA256SUMS` are the reproducibility cut, and
`sql/exchange_tracer_policy.sql` (core report) plus
`sql/60_tracers/exchange_tracer_method.remote.sql` (canonical method) rerun on
any db-sync instance.

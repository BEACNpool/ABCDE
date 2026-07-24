# Exchange Tracer Method — The Red (or Blue) Pill Study

How ABCDE reconstructs the community exchange-tracer dataset, and the rules any
answer built on it must follow.

The measurement rules below are the study operator's published agent guide for
the tracer data. ABCDE implements them against its own db-sync warehouse
instead of a public API, so the reconstruction is reproducible offline from the
committed tables and re-derivable from any db-sync instance.

- Study: **The Red (or Blue) Pill Study** — `tracer.adagenesistransparency.com`
- **Rules source:** <https://tracer.adagenesistransparency.com/TRACER_README.md>
  ("Agent guide to the Cardano exchange tracer data"), retrieved **2026-07-24**.
  That document carries no version stamp, so this file pins what it said on that
  date; re-read it before assuming the rules still match.
- Dataset background and raw receipts: `tracers/README.md`, `docs/24_CONTROL_INDICATORS_AND_TRACERS.md`
- Reproduction SQL: `tracers/scripts/export_tracers_from_abcde.sh` (sections 11–16)
- Results under these rules: `findings/F19_exchange_tracer_convergence.md`

## What a tracer proves

A tracer is a **quantity-1 native asset** under one policy. A non-fungible asset
has an exact transaction path: at any moment exactly one unspent output holds
it, and every move is a specific transaction. "Tracer X sat in output N of tx H
at block B" is a **FACT**.

Everything after that is weaker, in this order:

1. **Exact NFT edge** (FACT) — that asset moved in that transaction.
2. **Wallet-cluster grouping** (on-chain heuristic) — payment addresses sharing
   a stake credential are one on-chain wallet, *not* a proven legal entity.
3. **Self-reported exchange name** (claim) — the depositor's CIP-20 message. The
   message is FACT; the attribution is the depositor's assertion.
4. **ADA value paths** (indicative only) — ADA commingles, so a dominant output
   is a flow indicator, never a cryptographic continuation of value.

Never turn contact with an address into custody, ownership, or personal
identity. Never turn a self-reported exchange name into verified exchange
attribution. This is the repo-wide wording rule in `CLAUDE.md`, applied here.

## Canonical identifiers

Committed as a queryable row in `tracer_method_receipt`:

| field | value |
|---|---|
| policy ID | `d8d5539ee11f21a6748735aeb69d3ed935bb14570f57709279031119` |
| policy key hash | `55bf845d5be91cf210e50511fc34ff35aad645f92290c13c5c3b4186` |
| native-script expiry | mainnet slot `223391762` |
| deposit metadata | CIP-20 transaction message, label `674` |
| study-seed metadata | label `1985` |
| study name in metadata | `The Red (or Blue) Pill Study` |
| study site in metadata | `tracer.adagenesistransparency.com` |
| participant threshold | `2` distinct external participant wallets |

**The policy ID is the asset-identity boundary.** Never select tracers by a
`TRACER` name prefix — any policy can mint that name.

## The measurement rules

### Node key (wallet cluster)

One deterministic key per holder:

- `s:<stake_address>` when the payment address has a stake credential;
- `a:<payment_address>` when it does not (enterprise and Byron addresses).

Grouping by stake credential is an on-chain wallet heuristic. It is not
corporate identity, custody, or beneficial ownership.

### Exact holder path

Every asset-bearing output, ordered by `(block_no, tx.block_index, tx_out.index)`.
That ordered sequence is the tracer's exact path. Consecutive positions with the
same cluster key are self-moves — `tracer_asset_path.same_cluster_as_prev`
flags them so a holder path can be deduplicated without losing the raw chain.

Liveness is computed with a `tx_in` anti-join. Do **not** use
`tx_out.consumed_by_tx_id` on the ABCDE subscriber — it is not populated.

### Valid tagged deposit

A CIP-20 message names an exchange only when **all four** hold:

1. the transaction carries metadata label `674`;
2. the message identifies this study;
3. **output 0** holds quantity 1 of an asset under the tracer policy;
4. that output moves the tracer to a cluster key **different** from its
   preceding holder.

The name applies **only to the tracer in output 0**. Tracers returned as change
in later outputs do not inherit it. Other applications also use label `674`: a
matching label without a study tracer in output 0 is unrelated metadata.

The exchange name is `msg[1]`. Counting normalizes case and surrounding
whitespace; the evidence keeps the exact on-chain spelling and the raw JSON.

### Participant unit and name resolution

- **Participant** = the distinct wallet-cluster key holding the tracer
  *immediately before* the deposit. One participant sending ten tracers is one
  vote, not ten.
- **Terminus** = the cluster key of the tracer's current unspent output.
- Group deposited tracers by terminus. Within each terminus, count tracers and
  distinct participant keys **separately** per claimed name.
- A name **resolves** only when it has a unique lead by distinct participant
  count **and** at least `2` distinct participant wallets support it.
- Ties stay `unresolved_tie`; thin claims stay `unresolved_below_threshold`.
  Minority and conflicting names are preserved, never discarded.

Distinct wallet keys are not necessarily distinct people. Chain-only
reconstruction cannot establish that a participant is an independent person, so
these counts are *wallet* votes and are labelled as such.

## The tables

| table | grain | what it answers |
|---|---|---|
| `tracer_method_receipt` | 1 row | identifiers, rules, threshold, tip and export time for this cut |
| `tracer_asset_path` | per (asset, hop) | the exact ordered holder path of every tracer |
| `tracer_valid_deposits` | per validated deposit | who deposited, what name they claimed, where that tracer is now |
| `tracer_name_votes` | per (terminus, name) | tracer count vs participant count per claimed name |
| `tracer_terminus_clusters` | per terminus reached by a tagged deposit | the resolution result and the full name split |
| `tracer_terminus_census` | per terminus, ALL tracers | the denominator: where every tracer currently sits |

Raw, unfiltered receipts stay in the older tables (`tracer_all_outputs`,
`tracer_transfer_edges`, `tracer_deposit_claims`, `tracer_mint_events`, …).
`tracer_deposit_claims` is deliberately **looser** than
`tracer_valid_deposits`: it holds every 674/1985 message attached to any
tracer-moving transaction, including non-study 674 traffic. Use it as evidence,
not as the vote.

## Answering questions with these tables

**Where is tracer X now?**

```sql
SELECT terminus_key, terminus_address, terminus_tx, terminus_time
FROM tracer_terminus_census c JOIN tracer_asset_path p USING (terminus_key)
WHERE p.asset_name = 'TRACER…' AND p.is_terminus;
```

Cite `db_tip_receipt` / `tracer_method_receipt.tip_block_time` — this is a
snapshot, not a live chain view. For a current-state answer, re-query the chain.

**Where has tracer X been?**

```sql
SELECT hop, cluster_key, address, tx_hash, block_time, is_valid_deposit
FROM tracer_asset_path WHERE asset_name = 'TRACER…' ORDER BY hop;
```

**How many tracers reached a named exchange cluster?**

Numerator from `tracer_terminus_clusters`, denominator from
`tracer_terminus_census` (all tracers), status buckets from
`tracer_valid_deposits` vs the census. Always report both.

**Is a Coinbase / Kraken label supported?**

```sql
SELECT terminus_key, claimed_exchange, tracers, participants, corroborated
FROM tracer_name_votes WHERE claimed_exchange_norm = 'kraken'
ORDER BY participants DESC;
```

`corroborated = true` means ≥2 distinct participant wallets. A cluster's
`resolution_status` in `tracer_terminus_clusters` is the answer; the full vote
split is the evidence.

**Did several participants converge?**

Compare `participant_key` values and `terminus_key` in
`tracer_valid_deposits`. Shared terminus = shared on-chain contact; the
exchange identity still rests on the label vote.

**Where did the associated ADA go?**

Not answered by these tables. An ADA sweep is a **separate**, bounded,
dominant-output walk, and its edges must stay labelled `value-indicative`.
Never mix exact NFT edges and indicative ADA edges into one unlabelled path or
centrality calculation.

## Deliberate strictness (differences from a loose read)

- **Label `1985` is not a participant vote.** It appears on early study-seed
  transactions. It is retained in `tracer_deposit_claims` as evidence and
  excluded from the vote.
- **Non-study `674` traffic is excluded.** Many transactions that move a tracer
  carry unrelated 674 metadata from other applications.
- **`msg[1]` is read strictly.** A message written as one flat string instead of
  an array (`"Deposited to:, Kucoin, …"`) yields no `msg[1]`; those rows are kept
  with `name_source = 'unparsed_msg'` and an empty name rather than being
  pattern-matched into a vote. They are visible, not silently dropped.
- **Address-level claim counts are not votes.** Counting how many claim messages
  point at an address inflates a single participant into many. The vote unit is
  the distinct pre-deposit wallet-cluster key.

## Independent verification (no warehouse required)

The asset path is public, so anyone can re-derive it from the chain directly.
Using the public Koios mainnet endpoint `https://api.koios.rest/api/v1`:

```bash
# every asset under the policy (paginate in blocks of 1000)
curl --get 'https://api.koios.rest/api/v1/policy_asset_list' \
  --data-urlencode '_asset_policy=d8d5539ee11f21a6748735aeb69d3ed935bb14570f57709279031119' \
  --data-urlencode 'select=asset_name,fingerprint,total_supply' \
  --data-urlencode 'offset=0' --data-urlencode 'limit=1000'

# where one tracer sits right now (asset name in hex)
curl 'https://api.koios.rest/api/v1/asset_utxos' -H 'content-type: application/json' \
  --data '{"_asset_list":[["d8d5539ee11f21a6748735aeb69d3ed935bb14570f57709279031119","<ASSET_NAME_HEX>"]],"_extended":false}'

# that tracer's full history, then resolve the transactions (batches of ≤50)
curl --get 'https://api.koios.rest/api/v1/asset_txs' \
  --data-urlencode '_asset_policy=d8d5539ee11f21a6748735aeb69d3ed935bb14570f57709279031119' \
  --data-urlencode '_asset_name=<ASSET_NAME_HEX>' --data-urlencode '_history=true' \
  --data-urlencode 'offset=0' --data-urlencode 'limit=1000'
```

Confirm supply is `1` before treating an asset as non-fungible, keep pagination
stable, cache immutable transaction responses by hash, and refresh current
UTxOs for any current-state question.

## Limits

- A tracer proves contact with an address, not custody, ownership, or identity.
- A label-`674` exchange name is a depositor's claim.
- Several deposits from one wallet are one wallet-level source.
- Several wallet keys are not necessarily several people.
- A shared stake credential is an on-chain wallet cluster, not a corporate identity.
- Hub shape (high fan-in, batching, consolidation) also occurs in protocols,
  payment services and custodians — it corroborates, it does not identify.
- Current position and all-time passage are different questions.
- Absence from a reconstruction can mean incomplete history or provider lag, not
  absence from the chain.
- Classifying a wallet as a genuine participant, operator, or demo source can
  depend on off-chain provenance that is not derivable from transaction shape.
  ABCDE applies **no exclusion list**: every raw claim in the cut is published,
  so these counts are not claimed to match the study site's own participant
  statistics. The one shape signal available is how many tracers a participant
  wallet received at mint:

  ```sql
  SELECT d.participant_key, count(*) AS deposits,
         (SELECT count(*) FROM tracer_asset_path p
           WHERE p.hop = 1 AND p.cluster_key = d.participant_key) AS tracers_minted_to_it
  FROM tracer_valid_deposits d GROUP BY 1 ORDER BY deposits DESC;
  ```

  Minting straight to a participant is ordinary distribution, so a non-zero
  count is not an operator signal on its own — read it alongside the scale (see
  `findings/F19_exchange_tracer_convergence.md`).
- The mint window is open until the native-script expiry slot, so the tracer set
  can grow. Check `tracer_method_receipt.mint_window_closed` before treating any
  inventory count as final.

When publishing anything derived from these tables, state the policy ID, the
snapshot tip, the node-key rule, the edge evidence type, the label threshold,
and whether any exclusions were applied.

# F19 — Exchange tracer convergence under the study's canonical method

## Claim

ABCDE reproduces **The Red (or Blue) Pill Study** exchange-tracer dataset under
the study operator's published reconstruction rules (node keys, strict deposit
validation, exact NFT paths, terminus grouping, participant-vote resolution) and
publishes the result as queryable `tracer_*` tables.

Applying those rules to the full policy at the snapshot tip:

- **505 tracer NFTs**, every one quantity 1, none burned; **4,383 asset-bearing
  outputs** across **58 distinct wallet-cluster keys**; the longest single-asset
  path is **217 hops**.
- **62 deposits pass all four validation rules**, cast by **11 distinct
  pre-deposit wallet-cluster keys** and naming **7 exchanges**: Coinbase, Kraken,
  Binance, KuCoin, Gate.io, Bybit and UEX.us.
- Those 62 tracers currently sit in **11 terminus clusters**. Only **3 clear the
  2-participant corroboration threshold**:
  - **Coinbase** — 30 tracers from 6 participant wallets, no competing name.
  - **Kraken** — 16 tracers from 8 participant wallets, in a terminus holding 17
    deposited tracers: **1 conflicting Coinbase claim** from a single wallet is
    retained in the vote split and does not determine the name.
  - **KuCoin** — 2 tracers from 2 participant wallets.
- **Every Binance claim fails the threshold.** The 8 Binance-named deposits land
  in **4 separate terminus clusters, each supported by exactly one participant
  wallet**. Gate.io, Bybit and UEX.us are likewise single-wallet claims.
- The labelled subset is small: **436 of 505 tracers** currently sit in terminus
  clusters that **no** validated study deposit reaches, and the largest terminus
  holds **100 tracers with zero validated deposits**. Convergence in this dataset
  is much wider than its self-reported labels.

## Grade

- **FACT** — the tracer inventory, every exact NFT edge and holder path, the 62
  validated deposits and their metadata, the tracer/participant counts per
  claimed name, and the current terminus of every tracer. All are deterministic
  from db-sync and reproducible with
  `sql/60_tracers/exchange_tracer_method.remote.sql`.
- **STRONG_INFERENCE** — that the three threshold-clearing terminus clusters are
  custody clusters of the named exchange. Multiple independent participant
  wallets deposited to addresses that converge on one cluster, which is the
  shape of exchange deposit-sweep custody. It is not proof of ownership.
- **WORKING_HYPOTHESIS** — every single-participant name, including all four
  Binance-claimed clusters. One wallet asserting a name is one claim, not
  corroboration.
- **UNKNOWN** — the real-world operator of any cluster, and whether distinct
  wallet keys are distinct people.

## Method

`docs/26_EXCHANGE_TRACER_METHOD.md` is the binding rule set. In brief:

- Node key = `s:<stake_address>`, or `a:<payment_address>` when the address has
  no stake credential.
- A `674` message names an exchange only if it identifies the study, output 0
  carries a policy tracer, and that output moves the tracer to a **different**
  cluster key. The name applies to the output-0 tracer only.
- The vote unit is the **distinct pre-deposit wallet-cluster key**, not the
  claim message and not the tracer count. A name resolves only on a unique
  participant-count lead of at least 2 wallets; ties and thin claims stay
  unresolved and all competing names are preserved.

Two deposits carry the study message flattened into a single string, so they
expose no `msg[1]`. They are recorded with `name_source = 'unparsed_msg'` and an
empty name rather than pattern-matched into a vote; both were cast by one wallet
that also cast a parsed KuCoin claim, so excluding them changes no resolution.

Label `1985` (one transaction, `{"exchange": "Kraken"}`) is a study-seed label,
not a participant report, and is excluded from the vote. It remains visible in
`tracer_deposit_claims`.

## Participant provenance (no exclusions applied)

Chain shape cannot separate a genuine participant from an operator or demo
wallet, and ABCDE applies no exclusion list. What the chain does show, from a
join of `tracer_asset_path` (hop 1) against `tracer_valid_deposits`:

```sql
SELECT d.participant_key, count(*) AS deposits,
       (SELECT count(*) FROM tracer_asset_path p
         WHERE p.hop = 1 AND p.cluster_key = d.participant_key) AS tracers_minted_to_it
FROM tracer_valid_deposits d GROUP BY 1 ORDER BY deposits DESC;
```

**8 of the 11 participant wallets received tracers directly at mint.** That is
consistent with ordinary distribution — the operator mints a tracer straight to
the participant who asked for one — so it is not by itself an operator signal.
One wallet is different in scale: `s:stake1u9q68puzz…` had **320 of the 505
tracers minted to it** and is the study's own distribution wallet. It cast one
Kraken deposit. Excluding it leaves **7 external participant wallets** on the
Kraken vote and changes **no** resolution in this cut.

The mint window is still open — tip slot `193,355,371` against the native-script
expiry `223,391,762` — so the tracer set can still grow. Every count here is a
snapshot at the tip recorded in `tracer_method_receipt`.

## Reproduce

```sql
-- the three resolved clusters and the full vote split behind them
SELECT terminus_key, tracers, participants, conflicted,
       resolution_status, resolved_exchange
FROM tracer_terminus_clusters ORDER BY tracers DESC;

SELECT terminus_key, claimed_exchange, tracers, participants, corroborated
FROM tracer_name_votes ORDER BY terminus_key, participants DESC;

-- denominator: where all 505 tracers actually are
SELECT terminus_key, tracers_now, tracers_from_validated_deposit
FROM tracer_terminus_census ORDER BY tracers_now DESC LIMIT 10;
```

Independent of this repo, the same reconstruction runs against public Koios
endpoints — commands in `docs/26_EXCHANGE_TRACER_METHOD.md`.

## Limits

A tracer proves that an asset contacted an address. It does not prove custody,
beneficial ownership, or the identity of any person or company. An exchange name
in a deposit message is the depositor's claim about the destination, not a
statement by the exchange. Distinct wallet keys are not necessarily distinct
people, and ABCDE applies no participant-exclusion list, so these counts are not
claimed to match the study site's own participant statistics. Current position
and all-time passage are different questions: this cut answers the former at the
snapshot tip recorded in `tracer_method_receipt` and `db_tip_receipt`.

# Genesis Trail Monthly Stream and Consolidation Hub

This report answers two questions raised by
[adagenesistransparency.com](https://www.adagenesistransparency.com/), accessed
June 13, 2026:

1. Did the site expose chain data not already committed in ABCDE?
2. Did it identify useful warehouse queries?

The answer to both is yes. The site supplied identifiers and a flow hypothesis
that were not present as a dedicated ABCDE evidence package. ABCDE independently
queried the frozen warehouse snapshot and reproduced the core on-chain pattern.

The source snapshot ends at block `13,520,244`, epoch `635`,
`2026-06-07 18:44:37 UTC`.

## Public-site footprint

As of June 13, 2026, the public footprint observed for this project was the
apex domain and `www` host:

- `https://adagenesistransparency.com/`
- `https://www.adagenesistransparency.com/`

The live certificates were host-specific, and web search did not expose another
project subdomain. That is an observation, not proof that no unpublished
subdomain exists.

The same site publishes its material as internal routes rather than separate
domains, including `/graph`, `/identifiers`, `/report/overview`,
`/report/timeline`, `/report/forward-trail`, and `/report/caveats`. Its external
links point primarily to Cardanoscan transaction pages, X posts, and a YouTube
thumbnail host. The separately named
`adaredemptiontransparency.com` is a different public report and is already
handled as an external source in F09.

## What was new to ABCDE

The nine payment transaction hashes, four payer credentials, recipient
address, consolidation-hub address, and full payment-to-genesis trace set were
not present in the committed F01-F09 evidence packages.

The site was therefore useful as an external lead. Its narrative and identity
implications are not evidence in ABCDE; only independently reproduced chain
records are promoted below.

## Independently verified recipient series

**FACT.** Recipient address:

`addr1qxspyce8mzttagajlhfzwjpc7ym5vn9es2vgxgs4gq4ykx4qzf3j0kykh63m9lwjyayr3ufhgextnq5csv3p2sp2fvdqg8px4u`

- 11 outputs total
- 9 outputs of at least 20M ADA
- payment-sized total: `184,580,695.400465 ADA`
- all-output total: `184,837,022.651928 ADA`
- payment-sized period: `2021-04-02` through `2021-11-22`

The nine payment transactions used four input stake credentials. Exact hashes,
timestamps, values, and credentials are committed in
`genesis_trail_recipient_outputs` and `genesis_trail_payment_inputs`.

These records establish a recurring transfer series. They do not establish
recipient identity or contract terms.

## Consolidation flow

**FACT.** Transactions spending the recipient outputs sent 10 outputs totaling
`184,837,020.994894 ADA` to:

`addr1qygm7m8hjqjgyd2qnrthl49g3jwzvnw8e8zfqqefrdx3d0s3hak00ypysg65pxxh0l223ryuyexu0jwyjqpjjx6dz6lq0pgy99`

The hub received:

- 807 outputs
- `9,849,508,503.491169 ADA`
- from `2021-01-30 19:02:01` through `2022-09-07 04:04:51 UTC`

Gross received is not a balance and does not identify the hub operator.

## Connection to F09

F09 established that the IOGP reward credential sent `925,000,100 ADA` across
32 transactions to:

`stake1uycla9q3glrugp48cq2r7awemjxepvj4lxs4emw5qmpsclc4tpe52`

The new query continues that chain:

- IOGP reward credential to burst: `925,000,100 ADA`
- burst credential to the same consolidation hub:
  `925,000,294.515631 ADA` across 33 transactions
- monthly recipient to that hub: `184,837,020.994894 ADA`

Two additional stake credentials also sent `53,999,997.336236 ADA` and
`2,200,009.336236 ADA` to the same hub. These are committed as query leads,
not identity claims.

This shared destination is a direct connection between the site-derived lead
and ABCDE's existing F09 result.

## Deterministic genesis paths

**FACT as path existence.** All nine payment transactions terminate at the same
IOG genesis transaction under ABCDE's deterministic largest-input method:

`0ae3da29711600e94a33fb7441d2e76876a9a1e98b5ebdefbf2e3bc535617616`

Depths range from 25 to 29 hops. The full hop receipts are committed in
`genesis_trail_payment_dominant_traces`.

This method follows one largest input per transaction with a stable tie-break.
It establishes a path, not exclusive provenance or beneficial ownership.

## What remains open

The website describes a broader depositor census and classifies depositors by
genesis origin. ABCDE did not independently reproduce that complete
classification in this pass. It is recorded as backlog rather than adopted as
a finding.

The next useful warehouse work is:

- enumerate every direct hub depositor;
- compute deterministic and multi-input genesis-origin evidence per depositor;
- classify service, custody, exchange, and unknown patterns without assigning
  legal ownership;
- trace the hub's downstream endpoints and current-unspent descendants.

## Conclusion

The external site contained useful identifiers and a hypothesis that ABCDE did
not already package. The resulting warehouse queries produced a new verified
finding.

The connection between the two answers is concrete: the site-derived monthly
recipient and ABCDE's existing IOGP-to-burst stream independently converge at
the same 9.849B-ADA gross-receipt hub, and all nine payment paths reach the same
IOG genesis terminal under the documented deterministic method.

# F10 — 781,381,495 ADA Sale-Ticket Origin Signal

## Label Note
"EMURGO_2" is a trace identifier for the 781,381,495 ADA genesis entry redeemed by transaction `5ec95a53fa3bb7dc56864bb6e75f369f00aa20e8d8cdc3b66b2fb88ec1b225ef`. It is not an attribution to EMURGO. This finding concerns the *origin* of those funds at genesis, not the downstream operator.

## Claim
The 781,381,495 ADA source amount consumed by the EMURGO_2 anchor redemption is an exact match for the published maximum single sale-ticket `adamax` value in the official pre-launch Cardano ada-sale statistics across four orthogonal slices, and is outside the range of published named-founder allocations. This pattern is consistent with a large-buyer sale-ticket origin rather than a second named-founder line item.

| Slice | adamax (ADA) |
|:---|---:|
| Tickets / Tranche 4 | 781,381,495 |
| Tickets / Region / Japan | 781,381,495 |
| Tickets / User type / Company | 781,381,495 |
| Tickets / Currency / BTC | 781,381,495 |
| Tickets / All / All | 781,381,495 |
| Buyers / User type / Company / All | 781,381,495 |

Size-band context from the same archived statistics:
- Only 9 tickets fell in the 100,000,000 ≤ amount < 1,000,000,000 band, totaling 1,898,764,352 ADA.
- Only 1 buyer exceeded 1,000,000,000 ADA, totaling 1,173,221,790 ADA.
- Company-class tickets totaled 1,675,030,503 ADA across 166 tickets; the 781,381,495 ADA value alone represents approximately 46.65% of all ADA sold to company-classified buyers, and the equality between max ticket and max buyer suggests a single-ticket acquisition rather than multi-ticket aggregation.

The named founder allocations sit outside the sale-ticket distribution:

| Entity | Allocation (ADA) |
|:---|---:|
| IOG | 2,463,071,701 |
| EMURGO | 2,074,165,643 |
| CF | 648,176,763 |

The `adamax = 781,381,495` value is a standalone sale-ticket maximum, distinct from the founder allocations above.

## Grade
STRONG INFERENCE — the amount match across four orthogonal sale-slice maxima is a highly specific signal for a sale-ticket origin, but does not by itself identify the beneficial owner or exclude all alternative explanations.

## Scope and Non-Attribution
This finding speaks to the *origin* of the 781,381,495 ADA at genesis, not to downstream operational control. It is compatible with the operational convergence finding (`F02`) — a sale-ticket-origin allocation whose funds were placed into EMURGO-shared infrastructure immediately at redemption would produce the observed chain behavior. The Japan / Company / Tranche 4 / BTC slice match is circumstantial and does not name any specific buyer. See `../HYPOTHESES.md` H-002.

This finding does not:
- Identify any specific named buyer.
- Prove the ticket was purchased by an entity unrelated to EMURGO.
- Prove the ticket was purchased by EMURGO or an EMURGO affiliate or predecessor vehicle.
- Resolve conflicts in EMURGO's own public chronology (2015 vs. June 2017 corporate establishment).

## Data Basis
Pre-launch archived Cardano ada-sale statistics preserved in the `cardano-foundation/cardano-org` repository, plus the official Cardano genesis / AVVM files preserved in `input-output-hk/cardano-sl`.

## Core Evidence
- `investigation/archived_notes/emurgo2_classification_2026-04-08.md`
- `investigation/archived_notes/emurgo2_disclosure_search_2026-04-08.md`

## Public Source References
- Archived sale statistics: `cardano-foundation/cardano-org` — `static/archive/static.iohk.io/adasale/js/stats/main2.json` (update timestamp `2017-08-28T15:23:53.138Z`).
- AVVM entry for the unlabeled 781,381,495,000,000 lovelace address `Mutep7fz4IHpNS1eHXnQRPJOmciz9ql1QJF9IAt4XBY=`: `input-output-hk/cardano-sl` — `scripts/avvm-files/avvm-utxo.json` at commit `3e9264363e17398930ac87b5b52dd9b6e6b512d0` (2017-09-15).
- Named founder tokenomics narrative: `cardano.org/genesis/` and `cardano-foundation/cardano-org` — `src/pages/genesis.js`.

## Key Transactions / Addresses / Stake Credentials
- Source address at genesis: `Ae2tdPwUPEZB2zrbrdDkQNPdCndghMUJN8o8XjMaJ1jXgwVevf7TUrdmsSP`
- Redemption transaction: `5ec95a53fa3bb7dc56864bb6e75f369f00aa20e8d8cdc3b66b2fb88ec1b225ef`
- Redemption destination: `DdzFFzCqrhspiThx6UaeJASmHTbwbXp2FtdCkF9AU9QXPF9D8sUC7Fqrv9bmYkxradBbqMrSxukTTsqCPNPwRh5PHazdiwWTuJYVMMaf`

## Supporting Evidence Files
- `investigation/archived_notes/emurgo2_classification_2026-04-08.md`
- `investigation/archived_notes/emurgo2_disclosure_search_2026-04-08.md`

## Reproduction
- Public statistic replication is file-based — inspect the archived `main2.json` at the cited commit.
- On-chain amount and address can be verified with any db-sync or block-explorer lookup of tx `5ec95a53fa3bb7dc56864bb6e75f369f00aa20e8d8cdc3b66b2fb88ec1b225ef`.

## Limitations
See `../docs/05_LIMITATIONS_AND_NON_ATTRIBUTION.md`.

## Related Findings
- `F02_emurgo2_operational_convergence.md` — downstream operational convergence with EMURGO (FACT).
- `B04_emurgo2_anchor_confirmation.md` — anchor transaction mechanics (FACT).

## Related Hypotheses
- `../HYPOTHESES.md` (H-002 — administered by EMURGO for a separate beneficial owner)

## Source Lineage
- `investigation/archived_notes/emurgo2_classification_2026-04-08.md`
- `investigation/archived_notes/emurgo2_disclosure_search_2026-04-08.md`

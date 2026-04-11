# EMURGO_2 Classification Check
**Date:** 2026-04-08
**Question:** Is the `781,381,495 ADA` source consumed by tx `5ec95a53...` better explained as a second founder/TBDP allocation, or as a sale-distributed voucher ticket later converging with EMURGO?

## DB-Backed Redemption Mapping

Live `cexplorer_replica` confirms these source outputs were consumed by the four redemptions:

| Redemption tx | Source ADA | Source address | Redeemed to | Time |
|---|---:|---|---|---|
| `fa2d2a70...` | 2,463,071,701 | `Ae2tdPwUPEZKQuZh2UndEoTKEakMYHGNjJVYmNZgJk2qqgHouxDsA5oT83n` | `DdzFFzCqrhsytyf2...` | 2017-09-27 16:20:51 UTC |
| `208c7d54...` | 648,176,763 | `Ae2tdPwUPEZ9dH9VC4iVXZRNYe5HGc73AKVMYHExpgYBmDMkgCUgnJGqqqq` | `DdzFFzCqrht1RAzC...` | 2017-09-28 09:33:11 UTC |
| `242608fc...` | 2,074,165,643 | `Ae2tdPwUPEZGcVv9qJ3KSTx5wk3dHKNn6G3a3eshzqX2y3N9LzL3ZTBEApq` | `DdzFFzCqrhsi4ogK...` | 2017-09-28 10:04:11 UTC |
| `5ec95a53...` | 781,381,495 | `Ae2tdPwUPEZB2zrbrdDkQNPdCndghMUJN8o8XjMaJ1jXgwVevf7TUrdmsSP` | `DdzFFzCqrhspiThx...` | 2017-09-28 10:09:11 UTC |

This confirms the `5ec95a53...` transaction is consuming a single genesis-era source output of exactly `781,381,495 ADA`.

## Public Sale Data Comparison

Official archived Cardano sale stats show:

- `Tickets / All / All`: `14,402` tickets, `25,927,070,538 ADA` total, `adamax = 781,381,495`
- `Buyers / All / All`: `9,912` buyers, `25,927,070,538 ADA` total, `adamax = 1,173,221,790`
- `Tickets / Tranche 4`: `adamax = 781,381,495`
- `Tickets / User type / Company`: `adamax = 781,381,495`
- `Buyers / User type / Company / All`: `adamax = 781,381,495`
- `Tickets / Region / Japan`: `adamax = 781,381,495`
- `Tickets / Currency / BTC`: `adamax = 781,381,495`

Official size-band stats further show:

- Only `9` tickets fell in the `100,000,000 ≤ amount < 1,000,000,000` band
- Those `9` tickets totaled `1,898,764,352 ADA`
- Only `1` voucher holder exceeded `1,000,000,000 ADA`, totaling `1,173,221,790 ADA`

Company-side stats narrow it further:

- `Tickets / User type / Company`: `166` tickets, `1,675,030,503 ADA` total, `adamax = 781,381,495`
- `Buyers / User type / Company / All`: `77` buyers, `1,675,030,503 ADA` total, `adamax = 781,381,495`

Because the max company **buyer** amount and max company **ticket** amount are exactly the same, the largest company-side holder appears to have been a **single-ticket buyer**, not a company aggregating multiple tickets into a larger buyer total.

## Interpretation

The strongest inference from the public source material is:

> `781,381,495 ADA` matches the published maximum single sale-ticket amount, while the named founder allocations of `2,074,165,643 ADA` and `2,463,071,701 ADA` sit outside the published voucher-sale range.

The archived sale profile also points in a specific direction:

> The same amount appears as the maximum ticket in the `Tranche 4`, `Japan`, `Company`, and `BTC` groupings, making the original holder look more like a large Japanese company-side sale participant than a separate named founder/TBDP line item.

An additional consequence of the company-side stats:

> If the `781,381,495 ADA` source is a sale ticket, it likely represents one discrete company voucher that alone accounts for about `46.65%` of all ADA sold to company-classified buyers.

That means the `5ec95a53...` source is more consistent with:

- a **sale-distributed voucher/ticket entry**

than with:

- a **second named Technical and Business Development Pool line item**

## What Still Holds

- The on-chain overlap result remains significant: downstream Shelley stake-address overlap with EMURGO is still `6,216 / 6,216 = 100%`.
- The `5ec95a53...` redemption still appears operationally adjacent to the main EMURGO redemption, only 5 minutes later.

## Convergence Timing

The overlap is not only eventual.

CSV trace comparison shows:

- **Earliest shared destination address appears at hop 1**
- Shared address: `DdzFFzCqrhsu3iF6JfUTaapdWq2mXVRFukkS28WFYVDEqkgaaYttH8cT32credS99L5GaoUsEquqEPNH7ae88eKuDL6XsK5ZL56jkfLi`
- First seen in `EMURGO` trace: tx `7eb47f8f...`, output `51961`, `2017-10-18 05:09:51+00`
- First seen in `EMURGO_2` trace: tx `c8596b9c...`, output `51967`, `2017-10-18 05:15:51+00`

So the two lineages are already landing on the same Byron address within minutes of their first traced post-redemption activity.

## Direct Merge Mechanics

Live db-sync makes the early merge sharper than an address-overlap story.

The relevant sequence is:

| Time (UTC) | Tx | What happens |
|---|---|---|
| 2017-09-28 10:04:11 | `242608fc...` | EMURGO redemption |
| 2017-09-28 10:09:11 | `5ec95a53...` | `781,381,495 ADA` redemption |
| 2017-10-18 05:09:51 | `7eb47f8f...` | First EMURGO post-redemption spend |
| 2017-10-18 05:14:11 | `743fd051...` | EMURGO splits its main output into `1,074,165,542.657684 ADA` and `1,000,000,000 ADA` |
| 2017-10-18 05:15:51 | `c8596b9c...` | First `781M` post-redemption spend co-spends the `781M` redemption with the `1,074,165,542.657684 ADA` EMURGO-derived branch |

The `c8596b9c...` input set is:

| Input tx | Input tx_out_id | ADA | Provenance |
|---|---:|---:|---|
| `5ec95a53...` | `14539` | 781,381,495.000000 | `781M` redemption output |
| `743fd051...` | `51962` | 1,074,165,542.657684 | direct descendant of the EMURGO redemption |

The `c8596b9c...` output set is:

| Output tx_out_id | ADA | Address |
|---|---:|---|
| `51966` | 0.000131 | `DdzFFzCqrhsfeFUG...` |
| `51967` | 1,855,547,037.478660 | `DdzFFzCqrhsu3iF6...` |

That means the `781M` line does **not** operate independently at its first downstream hop. Its first spend is already a direct co-spend with an EMURGO-derived UTxO.

Dormancy timing is also unusually tight:

- EMURGO redemption output sat untouched for `475.0944` hours before its first spend.
- The `781M` redemption output sat untouched for `475.1111` hours before its first spend.

So both redemption outputs were activated after essentially the same ~19.8-day dormancy window and then merged into the same transaction path within six minutes.

## Public Audit Trail Clarification

The public-source side is now narrower than it looked at the start of the day.

An official standalone Cardano audit page did exist:

- `https://www.cardano.org/en/ada-distribution-audit/`

Wayback preserves that page from at least mid-2018 onward, and its content matches the audit narrative now embedded in the rebuilt `cardano.org/genesis/` page.

That means the missing piece is **not** whether Cardano ever published a public audit summary page. It did.

The missing piece is the deeper document layer the page itself references:

- three tranche-specific audits
- an `overall summary document`

I still have not found those underlying reports as standalone public files.

## Attribution Constraint

The public-sale profile still points toward a large voucher holder:

- max ticket in `Tranche 4`
- max ticket in `Japan`
- max ticket in `Company`
- max ticket in `BTC`

The chronology argument is useful, but not yet stable enough to resolve attribution by itself.

Official EMURGO materials are internally inconsistent:

- several 2018-2019 EMURGO press pages describe EMURGO as registered in Tokyo since June 2017 and in Singapore since May 2018
- several 2023-2024 EMURGO press pages describe EMURGO as established in 2015 in Japan

That means the official public record currently supports **two conflicting timelines** for EMURGO's corporate origin.

Practical consequence:

- the June 2017 timeline, if taken literally, would push the original sale buyer toward a predecessor vehicle, affiliate, founder-linked company, or later-custody handoff
- the 2015 timeline, if taken literally, would leave open the possibility that an EMURGO precursor or EMURGO itself participated during the sale era

So the sale-ticket interpretation remains strong, but the corporate-chronology angle is still an unresolved sub-question rather than a clean exclusion.

The frontier result is even stronger:

- `EMURGO current_unspent.csv`: `49,089` rows
- `EMURGO_2 current_unspent.csv`: `49,089` rows
- Exact shared `dest_tx_out_id` intersection: **`49,089 / 49,089`**

That means the two current unspent frontier sets are not merely similar. They are **identical**.

## What Changes

This evidence weakens the claim:

- `EMURGO_2 is a second undisclosed founder allocation`

and strengthens the narrower claim:

- `A publicly visible sale-ticket-sized genesis entry later converged completely with the EMURGO downstream cluster`

## Best Current Framing

The current evidence best supports:

> A very large sale-distributed genesis entry of `781,381,495 ADA` was redeemed on 2017-09-28 and then converged almost immediately with the main EMURGO operational pipeline, becoming fully identical at the current-unspent frontier level.

This is a materially different claim from asserting a second hidden founder allocation.

## Remaining Open Questions

- Was the `781,381,495 ADA` ticket originally purchased by a predecessor or affiliate later absorbed into EMURGO operations?
- Was the `781,381,495 ADA` ticket held by an unrelated buyer whose funds entered EMURGO custody almost immediately after redemption?
- How should EMURGO's own conflicting public chronology claims (`2015` versus `June 2017`) be reconciled?
- Did the convergence occur immediately under common control, or only after later exchange/custody consolidation?
- Can any archived sale records, distributor records, or internal voucher metadata tie this genesis ticket to a named entity?

## Reproducibility

SQL checks used for the live database portion are saved at:

- `queries/emurgo2_classification_checks.sql`
- `queries/emurgo2_direct_merge_checks.sql`

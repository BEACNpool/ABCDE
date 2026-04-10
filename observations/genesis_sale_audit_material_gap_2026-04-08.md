# Genesis Sale Audit Material Gap
**Date:** 2026-04-08
**Question:** What official public audit material about the original ada voucher sale is actually preserved in the archived Cardano site source, and what is missing?

## What The Archive Preserves

The local `cardano.org` source archive preserves a detailed public summary of the sale audit process.

From the public `cardano-org` source in `src/components/GenesisStats/index.js`:

- Attain Corporation of Japan is named as the manager of the voucher sale
- Cardano Foundation says it performed three separate audits covering `T1/T2`, `T3/T3.5`, and `T4`
- Cardano Foundation says it interviewed Attain representatives in both the UK and Japan
- Cardano Foundation says it had full independent access to the source data
- The archived summary describes audit scope across proceeds reconciliation, customer sales analysis, distributor activity analysis, KYC adherence, and review of Attain as an entity
- The summary also says tranche 4 showed materially stronger KYC adherence than earlier tranches
- The recovered page includes three public summary tables: tranche totals, country totals, and age-demographic totals
- The page also embeds a D3 chart backed by archived `wp-content/uploads/2017/08/data-1.csv`

This is meaningful public process disclosure, not just a one-line claim that "an audit happened."

## Recovered Official Audit Page

The old official `cardano.org` site did have a standalone public audit page:

- `https://www.cardano.org/en/ada-distribution-audit/`

Wayback CDX shows successful captures of that page from at least `2018-07-17` through `2020-06-23`.

That page was not a rumor or third-party mirror. It was an official `cardano.org` page with:

- page title: `Ada distribution audit - Cardano`
- OpenGraph description beginning `Executive summary – (Token Sales Audit)`
- the same Attain / tranche / KYC / proceeds-reconciliation summary now embedded in the current site
- the line that `an overall summary document was created`
- tranche totals, country totals, age-demographic totals, and an embedded chart
- sibling translation slugs visible in archived HTML (`/ja/audit-report-summary-2/`, `/zh/audit-report-summary-3/`)

So the official public audit page itself is no longer missing. Best current reading is that this page was itself the public executive-summary layer. What remains missing is any underlying tranche-report layer or separate downloadable attachment beyond the page.

## What The Archive Does Not Preserve

I did **not** find the underlying tranche audit reports or any separate standalone summary attachment as files in either:

- the local `cardano.org` source archive, or
- the archived standalone `ada-distribution-audit` page HTML

The preserved `adasale` archive contains:

- `main2.json`
- `size4.json`
- `owners2.json`
- `inequality.json`
- `timeline3.json`
- `tranches3.json`
- front-end assets for the sale statistics page

It does **not** contain:

- audit PDFs
- tranche audit reports as separate downloadable files
- a standalone final summary attachment separate from the recovered page

I also did not find any `.pdf`, `.doc`, or similar document links in the archived `ada-distribution-audit` page HTML itself. The English page directly references only:

- `wp-content/uploads/2017/08/image_1-1140x298.png`
- `wp-content/uploads/2017/08/image_2-1140x433.png`
- `wp-content/uploads/2017/08/data-1.csv`
- `wp-content/uploads/2018/03/bb781f21c78c6f9e6be9dd989260c4c1c09aef27-1.png`

The archived Japanese translation additionally references:

- `wp-content/uploads/2017/08/image_3.png`
- `wp-content/uploads/2017/08/image_4.png`

Those appear to be extra chart assets for the same public summary page, not report attachments.

So the old official page appears to have been an executive-summary web page, not a download index.

I also recovered a separate archived page:

- `https://www.cardano.org/en/cardano-audit-reports/`

But that page is an unrelated transparency track for FP Complete's engineering audit reports on Cardano code, not a token-sale audit repository. It should not be conflated with the voucher-sale audit trail.

Targeted Wayback CDX sweeps for obvious official-path document names also came back empty:

- `www.cardano.org/*audit*.pdf`
- `www.cardano.org/*distribution*.pdf`
- `www.cardano.org/*summary*.pdf`
- `www.cardano.org/wp-content/uploads/*audit*`
- `www.cardano.org/wp-content/uploads/*summary*`
- `www.cardano.org/wp-content/uploads/*distribution*`
- `www.cardano.org/wp-content/uploads/*tranche*`

So there is currently no simple `cardano.org` PDF path recovery for the missing document layer.

## The Missing "Further Information" Link

The preserved genesis page source includes this sentence in the `Genesis Proceeds` section:

> "The ada vouchers were sold by a Japanese corporation and its sales force in Japan with total gross sales of 108,844.5 BTC. Further information on the sale can be found here."

But in the archived React source (`src/pages/genesis.js`), that sentence appears as plain translated text:

- there is no `Link` component
- there is no `href`
- there is no obvious target URL for the word "here"

So the archived source preserves a reference to additional sale material, but not the actual destination.

## 2024 Migration Pattern

The current `cardano.org/genesis/` page was added in the public repo on `2024-03-05` by commit `1e6d2a60...` (`Add Genesis distribution page`).

That commit did two relevant things at once:

- added the new `Genesis Proceeds` text, including the orphaned `Further information on the sale can be found here.`
- embedded the old audit narrative into `src/components/GenesisStats/index.js` under `Ada Distribution Audit`

Then commit `13e0923c...` on `2024-03-11` switched the stats iframe to the locally archived `static.iohk.io/adasale/` assets while keeping the embedded audit text.

The older WordPress-era `genesis-block-distribution` page did **not** contain the later `108,844.5 BTC` / `Further information ... here` sentence in its page body. It did, however, link to the standalone `Ada distribution audit` page through the site navigation.

Best current inference:

- the standalone official audit page was folded into the rebuilt `genesis` page in 2024
- the `here` text in the rebuilt page is probably a leftover reference to that older standalone audit material
- but I do **not** yet have page-level HTML proving that the exact word `here` previously linked directly to `/en/ada-distribution-audit/`

## Best Current Reading

The public-audit trail appears to have two layers:

1. A preserved official public summary layer, now directly recovered as the archived `ada-distribution-audit` page.
2. A still-missing document layer, where the underlying tranche audits may have existed but are not present in the source archive available here.

Important refinement:

- the phrase `overall summary document` may refer to the recovered executive-summary web page itself
- I do **not** currently have evidence of a separate downloadable final summary file

The preserved official public summary layer now has two independently recovered forms:

- the old standalone `cardano.org/en/ada-distribution-audit/` page
- the newer integrated `cardano.org/genesis/` audit section and source archive

## Investigation Use

This matters because the missing tranche-level document layer is exactly where named buyer, distributor, refund, or tranche-specific anomalies would most likely surface.

The absence of those materials in the archive means:

- current public-source review is sufficient to support the sale-ticket interpretation
- but not sufficient to name the original holder of the `781,381,495 ADA` entry

## Next Follow-Up

- Search for archived tranche audit PDFs or any standalone summary attachment, if one existed separately from the recovered page
- Look for archived copies of the underlying reports on `cardanofoundation.org`, forum uploads, static subdomains, or third-party mirrors
- If needed, prove the exact historical target of the rebuilt `Further information ... here` sentence, though the strongest candidate is now the recovered standalone official audit page

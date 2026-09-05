# Match replay: what a punch means

The boxing board can replay a **realized spot P&L** result. It does not award
invented match points. The scoreboard remains the existing total-book ADA
equivalent mark, including open assets, receipt marks, rewards and deposits.
A loss makes the trader absorb a blow; it is not income earned by the opponent.

`scripts/match_fight.py` is a pure Decimal accounting helper. It reads the
publisher's public transaction evidence; it makes no network calls, consults no
private strategy records, uses no market price and cannot sign transactions.
`match_snapshot.py` adds its result to every existing move without changing the
score formula. Run the publisher with `--no-history --out /tmp/match.json` to
inspect a fresh candidate without changing the published snapshot or history.

## Public contract

Every move adds `event_id = agent + ":" + tx_hash` and `effect`:

```json
{
  "type": "realized_spot_pnl",
  "status": "verified",
  "ada": "-16.6527975875598159469371959",
  "cost_basis_ada": "120.8099345875598159469371959",
  "net_proceeds_ada": "104.157137",
  "basis_method": "separate_liquid_and_qUSDM_average_cost_including_fees",
  "claim_scope": "realized spot P&L; includes entry, order and allocated protocol fees, not total-book P&L",
  "source_tx_hashes": ["basis transaction hashes, then disposal hash"],
  "reason": "Net ADA proceeds minus allocated average spot basis; not match points."
}
```

Amounts are decimal strings or `null`. Only a verified disposal has numeric
P&L. A verified break-even disposal has numeric zero. Missing evidence is never
converted to zero.

| Type | Meaning | Numeric P&L |
| --- | --- | --- |
| `realized_spot_pnl` | Supported USDM disposal into ADA | Verified result only |
| `trade_activity` | Spot purchase, or unsupported trade shape | `null` |
| `position_conversion` | Supply, redeem or receipt movement; plain pinned conversions can be verified | `null` |
| `none` | Funding, stake registration, order, cancellation, other movement | `null` |

`status` is `verified`, `unknown` or `not_applicable`. An unknown sale remains
`trade_activity`, not `realized_spot_pnl`. The UI must require both the realized
type and verified status before using `ada` for a numeric hit. Purchases may
show a blocked jab/position opening, with no profit number. Funding and setup
remain neutral. Initial playback must be explicitly requested; subsequent
automatic playback deduplicates `event_id`. Reduced motion retains the result
without a traveling arm. No server-side intensity threshold is implied.

## Accounting convention and gates

The helper maintains **separate liquid USDM and pinned qUSDM cost buckets**.
Each bucket uses weighted average ADA cost. The visible convention is
"Average cost · liquid USDM and qUSDM tracked separately".
A purchase adds its negative net book ADA delta to basis. That delta already
includes the agent's paid network/batcher fees, so they are not added twice.
Explicitly proved order placement/cancellation fees add to the same basis.
At a disposal, allocated basis is `cost * (USDM sold / USDM held)` and realized
P&L is net book ADA proceeds minus that basis. Unrelated wallet/network costs
remain total-book costs, outside this named spot accounting convention.

A proved supply transfers `liquid cost × (USDM supplied / liquid USDM held)`
from liquid basis into the qtoken bucket, then adds its protocol network fee
to qtoken cost. A proved redemption transfers
`qtoken cost × (qtoken units burned / qtoken units held)` back to liquid basis,
then adds its redemption network fee. **Actual received USDM** becomes liquid
inventory. Interest is reflected in those actual additional units when they
are eventually sold; no APY, exchange-rate forecast or assumed interest amount
is inserted. The unconverted rail retains its own known liquid basis.

For a verified conversion, `effect.conversion_accounting` publishes decimal
strings for `basis_transferred_ada`, `protocol_fee_ada`, `liquid_usdm_after`,
`liquid_basis_ada_after`, `qtoken_raw_after`, and `qtoken_basis_ada_after`.
Conversion `ada` remains null because conversion alone realizes no ADA profit.

The raw `fight_evidence` object retains integer ADA/USDM deltas, input USDM,
paid network fee, exact qtoken changes and inputs, asset-scope eligibility,
origin eligibility, order-fee status, conversion proof and transaction index.
USDM and qUSDM match the **full policy and asset name**. Every owned
input/output must have a complete asset list; any other asset, including an
unknown receipt with no net movement, stops supported basis. A trade mixed with a
mint, nonzero withdrawal, certificate or stake deposit is also unsupported.
Explicitly parsed zero-ADA script withdrawals are permitted: these validation
hooks are not reward income. Missing or malformed withdrawal amounts fail closed.

Spot cashflow must also involve one of the two observed pool scripts: the
publisher's pinned Minswap V2 pool
`ea07b733d932129c378af627436e7cbc2ef0bf96e0036bb51b3bde6b`, or the direct USDM
pool in Grok's four current acquisitions
`d8b69fc53637bcfadbc4469083f706bc293f4d9d2296646c5ca167bb` (first acquisition
`80f58672a47f54d365f6d55721d96fce044736e7b05abe2b8fe40c28b43fd92a`). No protocol
name is inferred for that second pin. Direct trades require the exact opposite
USDM pool leg and opposite ADA flow; other pool assets must be unchanged.
Shared Minswap fills additionally rely on the publisher's existing full-batch
fee and receiver checks. This prevents an ordinary loan cashflow from becoming
an invented cheap acquisition. New venues require a proved adapter.

The replay requires a zero-USDM funding origin. It detects duplicate agent/tx
identities, missing chronology, impossible input inventory and display/raw
disagreement. Same-block events require distinct nonnegative transaction
indices; equal timestamps in different blocks follow block order. The
publisher also reconciles raw USDM deltas to current liquid USDM across wallet
and order addresses, and raw qUSDM deltas to the live wallet's exact qtoken
quantity. A whole-history identity/chronology or
final reconciliation failure disables that agent's results, without disabling
the opponent's independent history.

Order cancellation is explicit when raw wallet-plus-order flows preserve USDM
and the only ADA loss is a proved network fee funded entirely by that book.
It is labeled `cancel`, not a fictitious filled swap. Ambiguous order fees
invalidate subsequent basis. No fee cap is treated as actual paid fee by this
helper; existing publisher fill attribution still supplies the move cashflow.

Only a **plain pinned USDM/qUSDM conversion** preserves basis through lending.
The qtoken policy is
`9e00df0615de0a7b121a7f961d43e23165b8e81b64786c6eb708d370`, with an empty asset
name, cross-checked against `match_positions.py`. The market is
[`addr1wxd35v2m3fff5ah6rqq4stamqpp6n4fd7d2v5mq2fcrcl3s3kkuk7`](https://cardanoscan.io/address/addr1wxd35v2m3fff5ah6rqq4stamqpp6n4fd7d2v5mq2fcrcl3s3kkuk7).
These are the existing Liqwid preflight pins, also observed in both fighters'
public supply transactions. Proof requires:

- Only this fighter's wallet plus exactly one pinned market input and output;
  no borrow/collateral/foreign-output leg or qtoken DEX order.
- Wallet ADA loss exactly equals its paid network fee.
- Exact opposite wallet/market USDM movement, with unchanged market ADA and
  all other market assets.
- Exactly the pinned qtoken mint/burn, equal to the owned qtoken delta; every
  remaining qtoken stays in the wallet.
- The market datum's supplied and qtoken fields change by those exact amounts;
  every other datum field stays structurally identical.
- Reconstructed liquid/qtoken inventory covers the consumed inputs and
  converted quantities.

Unknown receipts, borrow/mixed conversions and other unsupported transfers
**permanently invalidate subsequent basis**. They do not erase an earlier
supported sale. A later apparently empty wallet, new funding or otherwise
valid conversion does not reset that failure. Both current plain Liqwid
supplies are supported; their later rail sales and proved redeem-then-sale
sequences can therefore produce verified positive or negative realized results.

The helper depends on the public provider's complete transaction history and
the publisher's wallet/order ownership classification. Reconciliation and
origin checks catch concrete omissions; they are not a cryptographic proof
that a provider returned every transaction. P&L is an accounting result under
the named convention, not a price forecast or a measure of trading skill.

## Reproducible current loss

BEACN's completed sale is transaction
`f968263ce596b664211d495cc17940d1205e98cc4f717c4ac2855ee3dda58c54`.
It sold 24.088633 USDM for 104.157137 ADA net of its 2 ADA batcher fee.

The acquisitions were 78.509894 USDM for 392.78 ADA
(`328f3fcb…`) and 48.177267 USDM for 242 ADA (`dc63f0fa…`). The three explicit
order placement fees were 0.185697, 0.185697 and 0.213329 ADA
(`d74687ca…`, `9323a1af…`, `b26de6a7…`). The public result includes their full
transaction hashes in `source_tx_hashes`.

```text
USDM inventory = 78.509894 + 48.177267 = 126.687161
ADA basis = 392.78 + 242 + .185697 + .185697 + .213329 = 635.364723
Allocated basis = 635.364723 * (24.088633 / 126.687161)
                = 120.8099345875598159469371959 ADA
Realized spot P&L = 104.157137 - allocated basis
                 = -16.6527975875598159469371959 ADA
```

The later 78.509894 USDM Liqwid supply is a proved conversion into a receipt,
not another disposal. Its ADA P&L remains `null`, while its transferred basis
and protocol fee are retained for subsequent sales.

## Verification

```sh
cd scripts
python3 -m unittest test_match_fight test_match_snapshot_semantics test_match_cost_attribution test_match_positions
```
The tests cover the real loss arithmetic, positive and break-even disposals,
neutral setup/buys, separate liquid/qtoken basis, future rail profit, partial
redemptions and actual interest units, unknown receipt invalidation without
reset, wrong market/mint/datum/borrow rejection, raw asset identity,
incomplete history, duplicate events, same-second ordering, malformed monetary
values, cancellation attribution and publisher cancellation classification.

Do not derive punches from adjacent history scores: price changes and receipt
accrual change those marks without a trade. In particular legacy reconstructed
history (`src="b"`) omits receipt principal after supply. A chain fingerprint
is not an event ID because receipt-valued positions can change without a new
transaction. Neither source supports per-trade profit attribution.

## Sharing an animated scorecard

The board’s **Share GIF** button prepares the newest meaningful recorded move
(including lending/setup), with an optional choice among the last two moves per
fighter. It produces a local 800×600, three-second, 36-frame looping GIF. It
never substitutes a profitable trade for a newer neutral move. The export
labels the move as a historical replay, includes its date and result, and keeps
both books fixed to the captured snapshot while the live page can refresh.

The preview can be paused, and reduced-motion preferences start it paused.
The saved file remains animated. Download works without a sharing API. On
supporting browsers, **Share GIF** invokes the device’s file share sheet from a
fresh button click after encoding; elsewhere it downloads the file for manual
attachment. Cancelling the share sheet keeps the prepared file. No social post
is automatically sent, and no rendering/upload service receives the snapshot.

Rendering and GIF encoding run from locally served files in `match-share/`.
A module worker bounds memory and output size, reports progress, and terminates
on cancellation. Object URLs are released when replaced or the dialog closes.
The existing PNG export is retained. Encoder source/version/license, resource
limits and message contract are in [MATCH_GIF_ENCODER.md](MATCH_GIF_ENCODER.md).

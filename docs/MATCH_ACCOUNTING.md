# Match accounting and display contract

The scoreboard compares both books in ADA-equivalent against one equalized starting
score. Current holdings include wallet ADA, refundable deposits, available staking
rewards, funds in open orders and priced supply receipts. A marked gain is not a
quote for an executable exit: pool, batcher and network costs still apply.

## Fee attribution correction (2026-09-05 UTC)

A Minswap fill can execute several unrelated orders against the same pool. The
transaction's entire pool delta is not one orderer's execution price or fee.
The BEACN STOP fill `f968263ce596b664211d495cc17940d1205e98cc4f717c4ac2855ee3dda58c54`
executed 24.088633 USDM alongside another order for 2,221.582336 USDM. The old
rollup assigned the full pool movement to the smaller order, producing an invalid
9,845.270598 ADA cumulative execution bill.

The corrected decoder proves fee attribution from the pinned Minswap V2 script,
each consumed order's success receiver and maximum batcher fee, and conservation
across all pool and recipient outputs. A maximum is only treated as paid when the
whole batch's observed fees equal the sum of every cap. Since each fee is capped,
equality proves each order paid its cap. Missing datums, discounted fees, partial
orders, mixed wallet inputs and unfamiliar pool shapes stop publication until the
attribution is independently supported. They are never guessed as zero.

That reconstruction gives BEACN 6 ADA of batcher fees and 1.889215 ADA of network
fees through the observed transaction set, for 7.889215 ADA in total. These are a
historical correction receipt; use the current snapshot for subsequent costs.
The combined fee figure includes network and batcher fees only. Pool trading fees
and price impact are embedded in the executed fills and are excluded from this
fee breakdown; they still affect the actual holdings and score.

Network fees belong to the credential that funds the transaction. A batcher's own
network fee is not an additional fee paid directly by the orderer.

## Supply receipts are not spot sales

The recognized Liqwid qUSDM policy is matched exactly. Sending USDM while receiving
its supply receipt is classified separately from an ADA/USDM spot swap, as is
redemption. Both remain visible chain events, and their actual wallet-paid network
fees remain costs. The receipt's marked value remains part of the current book.
This corrected both agents' spot-trade counts without changing their holdings or
the scoring formula.

## Historical chart

Published history is retained as published. Earlier receipt-valuation gaps are
still present, so this series must not be used as a clean strategy backtest.
The page and downloadable scorecard disclose that limitation. The plot uses a
vertical axis fitted to its selected values. Exact values, times and observed or
reconstructed provenance can be read with a keyboard-accessible snapshot control,
or in the snapshot table. No historic point was rewritten for this refresh.

## Reproduce the checks

```sh
python3 -m unittest discover -s scripts -p 'test_match*.py'
python3 -m unittest discover -s tests -p test_match_snapshot.py
python3 scripts/match_snapshot.py --out match.json --history history.json
python3 scripts/verify_match_snapshot.py match.json
```

`test_match_cost_attribution.py` uses synthetic counterparties to reproduce the
shared-batch failure, a discounted fee, missing datum, changed receiver and receipt
supply/redemption. The verifier checks paid fees, nonnegative fee components,
component totals, trade/event counts, marked holdings and the equalized baseline.

## Supported current book schema

The current position schema supports ADA, Moneta USDM, its recognized Liqwid supply
receipt and the recognized unfilled orders. Its market-activity validator requires
an unlevered position. Borrowing, LP positions and new receipt types require new
valuation, debt and liquidation accounting plus verifier fixtures before entering
the live book; a UI label is not sufficient support. Unknown fee shapes stop the
snapshot publisher, and the public page exposes the age of the last verified
snapshot.

# F03 — Fourth-Entry Sale-Ticket Origin Signal

## Claim

The fourth-entry amount `781,381,495 ADA` exactly matches the preserved legacy finding's reported `adamax` value across six Cardano pre-launch ada-sale statistic slices:

- Tickets / Tranche 4
- Tickets / Region / Japan
- Tickets / User type / Company
- Tickets / Currency / BTC
- Tickets / All / All
- Buyers / User type / Company / All

This is a strong origin signal for a large sale-ticket entry, not a proof of buyer identity.

## Grade

STRONG_INFERENCE.

The on-chain amount is FACT. The sale-statistic match is now directly re-derived from archived `main2.json` in `cardano-foundation/cardano-org`.

## Evidence

- `data/sources/adasale_main2.json`
- `data/small/fourth_entry_sale_ticket_signal.csv`
- `legacy/2026-05-20-pre-v2-import/findings/F10_781m_sale_ticket_origin_signal.md`

## Reproduce

```sql
WITH fourth AS (
  SELECT amount_ada
  FROM seed_registry
  WHERE seed_id = 'fourth_entry_781m'
)
SELECT
  s.slice,
  s.metric,
  s.amount_ada,
  s.amount_ada = fourth.amount_ada AS matches_fourth_entry_amount
FROM fourth_entry_sale_ticket_signal s
CROSS JOIN fourth
ORDER BY s.slice;
```

Expected current result: all six rows return `matches_fourth_entry_amount = true`.

## Non-attribution

This finding concerns origin-size fingerprinting only. It does not identify the buyer and does not resolve downstream operational control.

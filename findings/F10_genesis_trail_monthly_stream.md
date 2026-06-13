# F10 — Genesis Trail Monthly Stream and Consolidation Hub

## Claim

A recipient address received nine payment-sized outputs between April and
November 2021, totaling `184,580,695.400465 ADA`. Across all 11 outputs, the
address received `184,837,022.651928 ADA`, then forwarded
`184,837,020.994894 ADA` to one consolidation hub.

That hub received `9,849,508,503.491169 ADA` in 807 outputs. It also received
`925,000,294.515631 ADA` from the burst credential that F09 independently
connected to `925,000,100 ADA` of IOGP reward-credential outflows.

Deterministic largest-input paths from all nine payment transactions terminate
at the same `2,463,071,701 ADA` IOG genesis transaction.

## Grade

- **FACT** for the transaction outputs, payer credentials, forwarding flows,
  hub totals, stream bridges, and deterministic path existence.
- **STRONG_INFERENCE** that the monthly stream belongs to the broader
  IOGP/burst/consolidation operational flow because the independently verified
  streams converge at the same hub and genesis terminal.
- **UNKNOWN** for recipient identity, beneficial ownership, custody, sale
  terms, purpose, or intent.

Dominant-input tracing follows one deterministic largest-input path. It does
not establish exclusive provenance.

## Evidence

- `data/small/genesis_trail_recipient_outputs.csv`
- `data/small/genesis_trail_payment_inputs.csv`
- `data/small/genesis_trail_recipient_forwarding.csv`
- `data/small/genesis_trail_hub_summary.csv`
- `data/small/genesis_trail_stream_bridges.csv`
- `data/small/genesis_trail_payment_dominant_traces.csv`
- `reports/genesis_trail_case.md`
- `scripts/build_genesis_trail_case_remote.sh`
- `scripts/verify_genesis_trail_case.py`

All receipts record source tip block `13520244`, epoch `635`, and time
`2026-06-07 18:44:37 UTC`.

## Reproduce

From a clone:

```bash
python scripts/verify_genesis_trail_case.py
python scripts/query_duckdb.py claims/sql/genesis_trail_monthly_stream.sql
```

Maintainers with warehouse access can rebuild the CSV receipts:

```bash
ABCDE_SSH=abcde scripts/build_genesis_trail_case_remote.sh
python scripts/build_genesis_db.py
python scripts/verify_genesis_trail_case.py
```

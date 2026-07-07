# Trace warehouse (`trace` schema on abcde)

Local materializations built on the abcde warehouse to make genesis hop-tracing
an index lookup instead of a live recursive graph walk. `public.*` stays
read-only; everything here lives in the local `trace` / `governance` / `explorer`
schemas. Built 2026-07-06/07; canonical warehouse state:
`~/.openclaw/workspace/infra/ABCDE_DATA_WAREHOUSE_STATE.md`.

## Files

- `build_genesis_reach.sql` — builds `trace.genesis_reach`, the genesis ADA
  reachability graph: breadth-first from all 14,505 Byron genesis outputs, depth
  ≤8, fan-out cap 50 (wide batch/exchange txs recorded in `trace.genesis_wide_tx`,
  not expanded). Staging-and-swap so readers never see a partial build; a receipt
  row lands in `trace.build_receipt` each run. Installed on abcde at
  `/usr/local/share/abcde-trace/`; runner `/usr/local/bin/build_genesis_trace.sh`
  (env `DEPTH`/`CAP`); weekly cron Sun 04:30 `DEPTH=8`.
- `recreate_matviews.sql` — the 7 governance/explorer analytics matviews.
- `genesis_tag_intersection.sql` — cross the reach graph against
  `governance.genesis_address_tags`.
- `liquidity_intel_detect.sql` — Liquidity Intel standing job: detects dormant
  (≥5y / genesis) outputs spent in the last 24h and whether the spend heads toward
  a tagged exchange-deposit address, into the local `intel` schema
  (`intel.dormant_moves` / `liquidity_daily` / `build_receipt`). Idempotent 24h
  upsert; installed on abcde, hourly cron (:07). The `intel` schema is exposed via
  the PostgREST API but the data itself is **not** committed here (private feed;
  opsbox emails a daily digest via `ops/liquidity_intel_email.py`). Spend detection
  uses `tx_in` — never `consumed_by_tx_id` (0%-populated on this db-sync).
- `data/` — deterministic exports (all hashed in `SHA256SUMS`, provenance in
  `export_tip_receipt.csv`, tip block 13,647,367):
  - `genesis_never_moved.csv` — the 465 genesis outputs never spent since 2017.
  - `genesis_address_tags.csv` — the 74 graded labels (4 genesis-entity anchors +
    70 tracer/exchange-deposit addresses) that seed `governance.genesis_address_tags`.
  - `genesis_reach_depth_summary.csv` — per-depth graph shape: outputs, reach ADA,
    and unspent-at-tip counts/value. Note `reach_ada` exceeds total ADA supply at
    depth ≥5 because reachability double-counts co-mingled value — this is the
    reachability-not-attribution property, not an error.
  - `liquidity_exchange_summary.csv` — per tagged-exchange claim: address count,
    ADA ever through, live balance now, and genesis-reachability (all 0/8-hop).

The full `trace.genesis_reach` graph (3.86M rows) is intentionally NOT committed —
`build_genesis_reach.sql` regenerates it deterministically from the warehouse in
~7 min. The committed cut is the compact, hashed, reproducible essence.

## Semantics — read before citing

`trace.genesis_reach` encodes **REACHABILITY, not value attribution.** `depth` is
the minimum hop count from any genesis seed. Every output of a tx that spends a
reached output is "reached" — at depth ≥5 this co-mingles heavily with unrelated
funds, so depth ≤4 is the analytically tight zone. "Reached" is never a claim of
ownership or control; entity/exchange naming requires a graded label in
`governance.genesis_address_tags`, per the wording rule in `../../tracers/README.md`.

## Headline findings (tip block 13,647,367, 2026-07-07)

- **465 genesis outputs — 318,200,635 ADA — have never moved since 2017.**
  Largest single untouched output 11.78M ADA. All Byron `Ae2…` addresses.
- The 4 named genesis-entity anchors (IOG, EMURGO, Cardano Foundation, and the
  781M "fourth entry") each spent their genesis allocation at depth 1 on
  2017-09-27/28 — none still unspent at the original address.
- **0 of 59 tagged exchange-deposit addresses are reachable from genesis within
  8 hops.** The tracer-tagged modern deposit addresses and genesis-era supply are
  disjoint at this depth — a FACT that constrains any "founder→exchange" narrative.

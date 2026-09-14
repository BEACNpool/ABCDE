# ABCDE warehouse — final derived-data export

Exported 2026-09-14 04:25 UTC from the ABCDE `cexplorer_replica` database (cardano-db-sync 13.6 on
PostgreSQL 16), at chain tip block **13,938,331** (`chain_tip.txt`). The server was powered off
afterwards, so this is the last copy of these tables anywhere public.

The raw chain tables are not included: they are about 585 GB and can be rebuilt by syncing a
Cardano node and db-sync. What is here is everything ABCDE derived on top of them.

## Layout

- `schema.sql`: DDL for every exported schema (`pg_dump --schema-only`). Some views reference
  db-sync's `public` tables, so they only load into a database that has db-sync's schema.
- `data/<schema>/<table>.csv.gz.part-NNN`: gzipped CSV with a header row, split into parts
  of at most 90 MB to fit GitHub's file limit. Join the parts before decompressing:

  ```sh
  cat data/night/flow.csv.gz.part-* | gunzip > flow.csv
  ```

- `rows.tsv`: table, exported row count, exit status.
- `SHA256SUMS`: checksums of every part. Verify with `sha256sum -c SHA256SUMS`.

`bytea` columns are written in PostgreSQL's `\x…` hex form.

## Contents

| Schema | What it holds |
|---|---|
| `trace` | Genesis reach: every UTxO reached from the founder/genesis roots (3.86M rows). |
| `abcde_forensics_stage_founders_depth14` | The depth-14 founder trace (UTxOs, frontier, spends) and the current live/governance surface of the traced coins. |
| `night` | The NIGHT token spend-flow graph (2.15M rows). |
| `governance` | DRep votes, registry, delegation snapshot, proposals, vote power, genesis address tags and treasury views. |
| `relay` | Relay-health registrations, endpoints, ASN data and 91,844 reachability observations (method: `docs/27_RELAY_HEALTH_METHOD.md` on `main`). |
| `peers` | Pools whose registered relays connected to BEACN's relay, per day, plus a per-day count of unidentified peers. |
| `explorer`, `scrolls`, `public` custom tables | Epoch stats, fee revenue, the Ledger Scrolls registry mirror, and small tracing helper tables (the `public` ones were empty at export and ship as headers only). |

## Read before using

- **FACT vs INFERENCE.** Labels in `governance.genesis_address_tags` carry their own confidence
  column (`FACT`, `STRONG_INFERENCE`, …). An exchange attribution is a claim, not a certainty.
- **`governance.treasury_withdrawals` and `governance.treasury_flow` are known to be wrong as
  payout records.** They date a withdrawal by the proposal's submission time and include
  requests that were never enacted. Do not read them as money paid out; filter the underlying
  proposals by `enacted_epoch` instead.
- **Relay observations are one vantage point at one moment.** An unreachable endpoint in
  `relay.observation` is not evidence that a pool was offline.
- **Peers data is deliberately reduced.** Only peers whose IP matched a pool's publicly
  registered relay are listed individually. Other addresses (which can include private block
  producers) are not published, only a per-day count, and the raw 90-day observation log was
  not exported.

## Not exported publicly

These schemas were kept out of this public export on purpose and preserved privately:
`intel` (liquidity-intel data; the detection SQL on `main` stays public), `profile` (a private
wallet profile), `secondfi` (per-wallet victim and key-exposure lists from the SecondFi
incident, which would work as a target list), and `poolsync` (unpublished operator-clustering
inferences).

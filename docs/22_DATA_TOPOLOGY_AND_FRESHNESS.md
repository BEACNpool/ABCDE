# Data Topology and Freshness

ABCDE has three data tiers. They serve different purposes and should not be
described as interchangeable.

## 1. Committed public database

`data/abcde_genesis.duckdb` is the primary query surface for a normal clone.
It is a compact, read-only database built from `anchors.yaml` and the committed
`data/small/*.csv` receipts.

Verified on 2026-06-12:

| Property | Value |
|---|---:|
| DuckDB size | 41,955,328 bytes (40.01 MiB) |
| Tables | 71 |
| Aggregate rows across all tables | 118,706 |
| Committed source CSVs | 69 |
| Source CSV size | 43,909,619 bytes (41.88 MiB) |
| SHA-256 | `da51eff0e243507f67ceb27dde856c7f34346b60c62f551fd6547f1599ab11c9` |

The aggregate row count is a dataset inventory number, not a count of unique
transactions, addresses, people, or entities. Several tables are rollups or
different views over related source records.

For freshness-sensitive work, query `build_info` first:

```sql
SELECT
  db_tip_block,
  db_tip_epoch,
  db_tip_time,
  source_generated_utc,
  staleness_note
FROM build_info;
```

The machine-readable schema is `data/schema_catalog.json`; the generated
human-readable schema is `docs/SCHEMA.md`.

## 2. Large extraction and release data

`data/release/` is a gitignored local landing area for larger CSV, DuckDB, or
Parquet cuts. It is not populated by a plain clone and its local contents are
not evidence that a public release exists.

Published large cuts belong in
[GitHub Releases](https://github.com/BEACNpool/ABCDE/releases) with an
`artifacts.sha256` manifest. Fetch and verify a published bundle with:

```bash
python scripts/fetch_db.py
```

Use these artifacts when a question needs detail intentionally excluded from
the compact database. Cite the release tag, asset name, and checksum in any
result derived from them.

## 3. Maintainer warehouse

The full ABCDE PostgreSQL warehouse is the maintainer extraction source. It is
not shipped in this repository and is not required for public querying.

Read-only verification on 2026-06-12 found:

| Property | Value |
|---|---:|
| Database | `cexplorer_replica` |
| PostgreSQL size | 606,383,021,079 bytes (`565 GB` from PostgreSQL) |
| Replicated relations | 75 ready |
| Subscription | enabled |

Extraction scripts should treat replicated `public.*` tables as read-only.
Project-derived tables and files must retain the source tip and generation time
needed to reproduce their snapshot boundary.

## Current snapshot boundary

The committed DuckDB and the warehouse currently agree on:

| Property | Value |
|---|---:|
| Block | 13,520,244 |
| Epoch | 635 |
| Block time | 2026-06-07 18:44:37 UTC |

The warehouse is stalled at that point pending upstream relay recovery. All
subscribed relations are ready, but ready does not mean current: no replicated
table can contain chain state after the source stopped advancing.

Therefore:

- historical facts at or before the recorded tip remain queryable;
- live-unspent, current delegation, DRep distribution, governance lifecycle,
  and proposal-vote answers are snapshots as of that tip;
- a matching local and warehouse tip proves consistency between those two
  surfaces, not freshness against the Cardano chain;
- every refresh must update `data/small/db_tip_receipt.csv`, rebuild DuckDB and
  the schema catalog, and rerun the verifiers before publication.

Machine-local clone paths and host addressing are operator details, not
portable project interfaces. Public documentation and scripts should use
repository-relative paths.

# Data Topology and Freshness

ABCDE has three data tiers. They serve different purposes and should not be
described as interchangeable.

## 1. Committed public database

`data/abcde_genesis.duckdb` is the primary query surface for a normal clone.
It is a compact, read-only database built from `anchors.yaml` and the committed
`data/small/*.csv` receipts.

Verified on 2026-07-03:

| Property | Value |
|---|---:|
| DuckDB size | 48,246,784 bytes (46.01 MiB) |
| Tables | 94 |
| Aggregate rows across all tables | 128,721 |
| Committed source CSVs | 92 |
| Source CSV size | 47,801,609 bytes (45.59 MiB) |

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

The warehouse recovered to live mainnet replication on 2026-06-23 (the earlier
2026-06-07 stall is over). The authoritative refresh boundary is whatever
`data/small/db_tip_receipt.csv` records — as of the 2026-07-03 cut:

| Property | Value |
|---|---:|
| Block | 13,628,717 |
| Epoch | 639 |
| Block time | 2026-07-03 05:50:34 UTC |

**Tables are not all refreshed at once.** Per-table freshness is quantified in
`data/small/data_freshness_catalog.csv` (row counts, hashes, last commit time,
age, snapshot sensitivity). Tables refreshed in the 2026-07-03 cut include the
seed-cut receipts, governance metadata, top-DRep current profiles, control
indicators, and tracers; the depth-14 IOG current-bag tables and the
genesis-behavior surface remain snapshots at their recorded earlier boundary
(2026-06-07 tip / 2026-05-22 staged snapshot) until their heavy traces are
rerun.

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

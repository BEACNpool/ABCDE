# Data Topology and Freshness

ABCDE has three data tiers. They serve different purposes and should not be
described as interchangeable.

## 1. Committed public database

`data/abcde_genesis.duckdb` is the primary query surface for a normal clone.
It is a compact, read-only database built from `anchors.yaml` and the committed
`data/small/*.csv` receipts.

The current schema inventory is generated in `data/schema_catalog.json` and
`docs/SCHEMA.md`; table and row counts change when modules are added. Query
`information_schema.tables` or the MCP `list_tables()` tool instead of relying
on a dated count in prose.

The aggregate row count is a dataset inventory number, not a count of unique
transactions, addresses, people, or entities. Several tables are rollups or
different views over related source records.

For freshness-sensitive work, inspect `build_info` alongside the **module
receipt**. These build/global fields alone do not date every table:

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

### Committed top-cuts

Some tables are too large to commit in full without pushing the DuckDB past the
size gate. For those, the compact clone holds a **value-ranked top-cut** and the
full table is a release-tier artifact. `scripts/topcut_large_csvs.py` (run by
`finalize_cut.sh`) enforces this and writes a `<table>.coverage.json` sidecar
recording full row count, kept rows, and % of value retained.

Currently cut: `iog_current_bag_depth14_current_utxos` — the compact clone keeps
the **top 15,000 UTxOs by value (~98.1% of the depth-14 bag's ADA)**; the full
75k-row table is `data/release/iog_current_bag_depth14_current_utxos_full.csv`
(regenerate with `scripts/build_iog_current_bag_audit_remote.sh`). Aggregate
depth-14 tables (`_summary`, `_by_depth`, `_top_stake`, `_confidence_bands`,
cluster classifications) remain committed in full, so bag totals and
distributions are exact; only the per-UTxO long tail of dust is release-tier.

## 3. Maintainer warehouse

The full ABCDE PostgreSQL warehouse is the maintainer extraction source. It is
not shipped in this repository and is not required for public querying.

Its size and operational configuration are not part of the portable public
interface. Public reproducibility means reproducing a claim from committed
rows or an identified, checksummed release; it does not imply public access to
the maintainer's full database.

Extraction scripts should treat replicated `public.*` tables as read-only.
Project-derived tables and files must retain the source tip and generation time
needed to reproduce their snapshot boundary.

## Per-module snapshot boundaries

**Tables are not all refreshed at once.** The committed `db_tip_receipt` and
`build_info` supply global/build context, while individual extraction receipts
and manifests define the relevant table boundary. `data_freshness_catalog`
records inventory and file age; a commit timestamp is not a substitute for an
extraction's chain tip.

For example, the founding-accountability module uses
`data/manifests/founding-evidence-manifest.json` and
`data/small/founding_query_receipts.csv`. Its governance cut does not refresh
the older genesis traces, monthly-stream receipts, custody graph, incident
records, NIGHT holder cut, or relay sweeps. Those retain their own boundaries.
See [the founder evidence guide](28_FOUNDER_ACCOUNTABILITY_EVIDENCE.md) for how
to join the new and historical evidence without treating them as one snapshot.

Therefore:

- historical facts at or before their recorded tips remain queryable;
- unspent outputs, stake snapshots, DRep distributions, governance lifecycle
  and proposal votes must name their appropriate tip or epoch;
- the epoch-stake snapshot and DRep distribution epoch are distinct from the
  latest extracted block; neither is a live wallet balance;
- a matching local and warehouse tip proves consistency between those two
  surfaces, not independent freshness against mainnet;
- a module refresh must preserve source tips, generation times, exact SQL and
  artifact hashes, rebuild DuckDB/schema, and rerun the relevant verifiers.

Machine-local clone paths and host addressing are operator details, not
portable project interfaces. Public documentation and scripts should use
repository-relative paths.

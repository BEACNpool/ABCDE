# Rebuilding From db-sync

Maintainer-only workflow.

1. Configure `.env` from `.env.example`.
2. Confirm ABCDE replication state, source tip, and upstream freshness. See
   `docs/22_DATA_TOPOLOGY_AND_FRESHNESS.md`.
3. Load `anchors.yaml` into a staging table.
4. Run `sql/01_extract` against `cexplorer_replica`.
5. Run `sql/02_enrich` for labeled/inferred overlays.
6. Run `sql/03_publish` to export DuckDB + Parquet.
7. Run `scripts/verify.py` against the published bundle.
8. Commit only code, manifests, summaries, and findings; publish large bundles via release/storage.

The source tip must be written to `data/small/db_tip_receipt.csv` before the
compact database is rebuilt. Matching the warehouse tip is necessary for
consistency, but it is not proof that the warehouse is current with Cardano.

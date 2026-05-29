# Rebuilding From db-sync

Maintainer-only workflow.

1. Configure `.env` from `.env.example`.
2. Confirm ABCDE replication lag and source tip.
3. Load `anchors.yaml` into a staging table.
4. Run `sql/01_extract` against `cexplorer_replica`.
5. Run `sql/02_enrich` for labeled/inferred overlays.
6. Run `sql/03_publish` to export DuckDB + Parquet.
7. Run `scripts/verify.py` against the published bundle.
8. Commit only code, manifests, summaries, and findings; publish large bundles via release/storage.

# Reproducing Locally

Public users should not need db-sync.

Public clone-and-query flow:

```bash
just bootstrap
just test

duckdb data/abcde_genesis.duckdb <<'SQL'
SELECT * FROM seeds ORDER BY amount_ada DESC;
SQL
```

Public claim receipts are in `claims/`:

```bash
python scripts/verify_claim_receipts.py
```

Each receipt has SQL, expected row count, output hash, and an evidence grade.

## Current public cut

The repo ships a compact DuckDB built from `anchors.yaml` and every
`data/small/*.csv` file:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements/base.txt
python3 scripts/build_genesis_db.py
python3 scripts/selftest.py
python3 scripts/verify_claim_receipts.py
```

Artifacts:

- `data/abcde_genesis.duckdb`
- `data/small/*.csv`
- `data/schema_catalog.json`
- `docs/SCHEMA.md`
- `claims/manifest.json`

Large/full cuts, when published, are fetched into `data/release/`:

```bash
python scripts/fetch_db.py
```


## Run a finding query without the DuckDB CLI

```bash
. .venv/bin/activate
python3 scripts/query_duckdb.py sql/10_findings/F02b_fourth_entry_direct_cospend.duckdb.sql
python3 scripts/verify_finding_queries.py
```

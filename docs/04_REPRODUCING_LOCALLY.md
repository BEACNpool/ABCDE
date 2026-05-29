# Reproducing Locally

Public users should not need db-sync.

Planned flow:

```bash
just download-data
just verify

duckdb data/abcde_genesis.duckdb <<'SQL'
SELECT * FROM seed_registry ORDER BY label;
SQL
```

Each finding in `findings/` should contain a query that runs against the published DuckDB file.


## Current v2 seed-registry cut

Until the full Genesis subgraph is published, the repo ships a tiny seed-registry cut:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements/base.txt
python3 scripts/build_seed_artifacts.py
python3 scripts/verify_seed_artifacts.py
```

Artifacts:

- `data/small/seed_registry.csv`
- `data/small/seed_anchor_db_verification.csv`
- `data/small/seed_outputs_db.csv`
- `data/small/seed_first_spends_db.csv`
- `data/small/seed_first_spend_inputs_db.csv`
- `data/small/fourth_entry_direct_cospend_db.csv`
- generated locally: `data/abcde_genesis_seed_registry.duckdb`


## Run a finding query without the DuckDB CLI

```bash
. .venv/bin/activate
python3 scripts/query_duckdb.py sql/10_findings/F02b_fourth_entry_direct_cospend.duckdb.sql
python3 scripts/verify_finding_queries.py
```

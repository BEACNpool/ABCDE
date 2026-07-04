#!/usr/bin/env python3
"""Build the compact, query-ready ABCDE genesis DuckDB from committed sources.

Loads:
  - anchors.yaml            -> table `seeds`
  - data/small/*.csv        -> one table per file (named after the file stem)

Also emits a machine- and AI-readable schema catalog so query tools (the MCP
server and ask.py) can ground the model in the real tables and columns.

Outputs:
  - data/abcde_genesis.duckdb   (the database)
  - data/schema_catalog.json    (tables, columns, types, row counts, samples)
  - docs/SCHEMA.md              (human-readable catalog)

Run:  python scripts/build_genesis_db.py
Idempotent: the database and catalog are rebuilt from scratch each run.
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import duckdb
import yaml

REPO = Path(__file__).resolve().parents[1]
DB_PATH = REPO / "data" / "abcde_genesis.duckdb"
SMALL_DIR = REPO / "data" / "small"
ANCHORS = REPO / "anchors.yaml"
DB_TIP_RECEIPT = REPO / "data" / "small" / "db_tip_receipt.csv"
CATALOG_JSON = REPO / "data" / "schema_catalog.json"
SCHEMA_MD = REPO / "docs" / "SCHEMA.md"

SAMPLE_ROWS = 3

# CSV stems NOT loaded into the shipped product DB. The *_raw control extracts
# are strictly subsumed by their classified `_indicators` tables (same rows,
# fewer columns); the *_cert_cohorts / external_funders are empty negative
# results already stated in prose in F11 / doc 24. They remain as maintainer
# build inputs (the classifier reads *_raw), just kept out of the clone-and-ask
# surface so an LLM grounds on the canonical table, not a duplicate or an empty.
SKIP_TABLE_STEMS = {
    "genesis_control_indicators_raw",
    "fleet_control_indicators_raw",
    "component_control_indicators_raw",
    "genesis_control_cert_cohorts",
    "fleet_control_cert_cohorts",
    "component_control_cert_cohorts",
    "f11_cohort_external_funders",
}


def sanitize(name: str) -> str:
    """Turn a file stem into a safe SQL identifier."""
    ident = re.sub(r"[^0-9a-zA-Z_]", "_", name).strip("_").lower()
    if not ident or ident[0].isdigit():
        ident = f"t_{ident}"
    return ident


def load_seeds(con: duckdb.DuckDBPyConnection) -> None:
    data = yaml.safe_load(ANCHORS.read_text(encoding="utf-8"))
    seeds = data.get("seeds", [])
    con.execute("DROP TABLE IF EXISTS seeds")
    con.execute(
        """
        CREATE TABLE seeds (
            seed_id        VARCHAR,
            label          VARCHAR,
            tx_hash        VARCHAR,
            amount_ada     BIGINT,
            source_type    VARCHAR,
            evidence_grade VARCHAR
        )
        """
    )
    for s in seeds:
        con.execute(
            "INSERT INTO seeds VALUES (?, ?, ?, ?, ?, ?)",
            [
                s.get("seed_id"),
                s.get("label"),
                s.get("tx_hash"),
                s.get("amount_ada"),
                s.get("source_type"),
                s.get("evidence_grade"),
            ],
        )
    print(f"  seeds: {len(seeds)} rows (from anchors.yaml)")


def load_csvs(con: duckdb.DuckDBPyConnection) -> dict[str, str]:
    """Load every CSV in data/small/ as its own table. Returns {table: source_file}."""
    mapping: dict[str, str] = {}
    for csv in sorted(SMALL_DIR.glob("*.csv")):
        if csv.stem in SKIP_TABLE_STEMS:
            continue
        table = sanitize(csv.stem)
        if table == "seeds":  # never shadow the anchors-derived table
            table = "csv_seeds"
        con.execute(f'DROP TABLE IF EXISTS "{table}"')
        con.execute(
            f'CREATE TABLE "{table}" AS '
            f"SELECT * FROM read_csv_auto(?, header=true, sample_size=-1)",
            [str(csv)],
        )
        n = con.execute(f'SELECT count(*) FROM "{table}"').fetchone()[0]
        mapping[table] = csv.relative_to(REPO).as_posix()
        print(f"  {table}: {n} rows (from {mapping[table]})")
    return mapping


def load_build_info(con: duckdb.DuckDBPyConnection) -> None:
    """Expose snapshot provenance to agents querying the DuckDB."""
    try:
        git_commit = subprocess.check_output(
            ["git", "-C", str(REPO), "rev-parse", "--short=12", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        git_commit = "unknown"

    con.execute("DROP TABLE IF EXISTS build_info")
    con.execute(
        """
        CREATE TABLE build_info AS
        SELECT
          'scripts/build_genesis_db.py' AS generated_by,
          ? AS git_commit,
          generated_utc AS source_generated_utc,
          db_tip_block,
          db_tip_time,
          db_tip_epoch,
          source,
          staleness_note
        FROM read_csv_auto(?, header=true)
        LIMIT 1
        """,
        [git_commit, str(DB_TIP_RECEIPT)],
    )


def build_catalog(con: duckdb.DuckDBPyConnection, sources: dict[str, str]) -> dict:
    sources = {"seeds": "anchors.yaml", "build_info": "data/small/db_tip_receipt.csv", **sources}
    tables = [r[0] for r in con.execute("SHOW TABLES").fetchall()]
    catalog = {
        "generated_utc": "deterministic-from-committed-sources",
        "database": DB_PATH.relative_to(REPO).as_posix(),
        "tables": {},
    }
    for t in sorted(tables):
        cols = con.execute(
            "SELECT column_name, data_type FROM information_schema.columns "
            "WHERE table_name = ? ORDER BY ordinal_position",
            [t],
        ).fetchall()
        n = con.execute(f'SELECT count(*) FROM "{t}"').fetchone()[0]
        sample = con.execute(f'SELECT * FROM "{t}" LIMIT {SAMPLE_ROWS}').fetchall()
        col_names = [c[0] for c in cols]
        catalog["tables"][t] = {
            "source": sources.get(t, "unknown"),
            "row_count": n,
            "columns": [{"name": c[0], "type": c[1]} for c in cols],
            "sample_rows": [dict(zip(col_names, [_jsonable(v) for v in row])) for row in sample],
        }
    return catalog


def _jsonable(v):
    try:
        json.dumps(v)
        return v
    except TypeError:
        return str(v)


def write_schema_md(catalog: dict) -> None:
    lines = [
        "# ABCDE Genesis Database — Schema Catalog",
        "",
        "_Auto-generated by `scripts/build_genesis_db.py` from committed sources._",
        "",
        f"Database: `{catalog['database']}`  ·  Tables: {len(catalog['tables'])}",
        "",
        "This catalog is what the MCP server and `ask.py` hand to the AI so it can "
        "write correct SQL. Regenerate it whenever the data changes.",
        "",
    ]
    for t, info in catalog["tables"].items():
        lines.append(f"## `{t}`  ({info['row_count']:,} rows)")
        lines.append("")
        lines.append(f"Source: `{info['source']}`")
        lines.append("")
        lines.append("| column | type |")
        lines.append("| --- | --- |")
        for c in info["columns"]:
            lines.append(f"| `{c['name']}` | {c['type']} |")
        lines.append("")
    SCHEMA_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    if not SMALL_DIR.exists():
        raise SystemExit(f"missing {SMALL_DIR}")
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    SCHEMA_MD.parent.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()

    print(f"Building {DB_PATH.relative_to(REPO)} ...")
    con = duckdb.connect(str(DB_PATH))
    try:
        load_seeds(con)
        sources = load_csvs(con)
        load_build_info(con)
        catalog = build_catalog(con, sources)
    finally:
        con.close()

    CATALOG_JSON.write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")
    write_schema_md(catalog)
    print(f"\nWrote {CATALOG_JSON.relative_to(REPO)} and {SCHEMA_MD.relative_to(REPO)}")
    print(f"Done. {len(catalog['tables'])} tables in {DB_PATH.relative_to(REPO)}")


if __name__ == "__main__":
    main()

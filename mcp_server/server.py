"""Read-only MCP server over the ABCDE genesis ADA database.

Exposes four tools so an AI client (Claude Desktop, Claude Code, etc.) can ask
where the genesis ADA went:

  - list_tables()              -> tables with row counts and sources
  - describe_table(name)       -> columns, types, and sample rows
  - run_sql(sql, max_rows=200) -> result of a single read-only query
  - starter_questions()        -> grounded example questions to try

The database is opened ``read_only=True`` and every statement is checked by the
shared guard in ``mcp_server.readonly`` (single SELECT/WITH/PRAGMA/EXPLAIN/SHOW/
DESCRIBE only). If the compact DB is missing it is built from committed sources.

Run:  python -m mcp_server.server      (stdio transport)
"""
from __future__ import annotations

import sys
from pathlib import Path

# Make `import mcp_server...` resolve whether this file is launched as a module
# (`python -m mcp_server.server`) or by absolute path (how Claude Code / Codex /
# Claude Desktop typically start an MCP server).
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mcp.server.fastmcp import FastMCP

from mcp_server.readonly import (
    UnsafeSQLError,
    ensure_db,
    load_catalog,
    run_select,
)

mcp = FastMCP("abcde-genesis")


@mcp.tool()
def list_tables() -> dict:
    """List every table in the genesis database with its row count and source."""
    catalog = load_catalog()
    return {
        "database": catalog.get("database", "data/abcde_genesis.duckdb"),
        "tables": [
            {
                "name": name,
                "row_count": info.get("row_count"),
                "source": info.get("source"),
                "columns": [c["name"] for c in info.get("columns", [])],
            }
            for name, info in catalog.get("tables", {}).items()
        ],
    }


@mcp.tool()
def describe_table(name: str) -> dict:
    """Describe one table: its columns, types, row count, and sample rows."""
    catalog = load_catalog()
    info = catalog.get("tables", {}).get(name)
    if info is None:
        available = sorted(catalog.get("tables", {}).keys())
        return {"error": f"unknown table '{name}'", "available_tables": available}
    return {"name": name, **info}


@mcp.tool()
def run_sql(sql: str, max_rows: int = 200) -> dict:
    """Run a single read-only SQL query (SELECT/WITH/PRAGMA/EXPLAIN/SHOW/DESCRIBE).

    Writes and multi-statements are rejected. Results are capped at ``max_rows``.
    """
    try:
        return run_select(sql, max_rows=max_rows)
    except UnsafeSQLError as exc:
        return {"error": f"rejected: {exc}"}
    except Exception as exc:  # surface DuckDB errors to the model
        return {"error": str(exc)}


@mcp.tool()
def starter_questions() -> dict:
    """Grounded example questions you can ask of the genesis ADA database."""
    return {
        "questions": [
            "Which named founder entities are in the seeds table, and how much genesis ADA did each receive?",
            "Where did EMURGO's genesis ADA end up — which SPOs and DReps does the trace reach?",
            "Did EMURGO actually remove genesis ADA from its DRep, and how much is left there?",
            "Which DReps hold the most genesis-traced stake?",
            "How much IOG-descended ADA is still unspent, and what are the confidence bands?",
            "Which stake pools (SPOs) received the most genesis-descended delegation?",
            "What is the evidence grade attached to the fourth genesis entry?",
            "Which trace or cross-entity merge events cluster by epoch and block, not just hop depth?",
        ],
        "tip": "Call list_tables() then describe_table(name) to ground your SQL before run_sql().",
    }


def main() -> None:
    ensure_db()
    mcp.run()


if __name__ == "__main__":
    main()

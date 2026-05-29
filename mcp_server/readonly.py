"""Shared read-only DuckDB helpers and SQL guard.

Used by both the MCP server (`mcp_server/server.py`) and the CLI fallback
(`ask.py`) so the read-only enforcement is identical everywhere.

The genesis database is opened with ``read_only=True``; on top of that we
statically reject anything that is not a single read-only statement. This is
defence in depth: even if DuckDB would refuse a write, we never want the model
to be able to ATTACH/COPY/INSTALL/LOAD or run multiple statements.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import duckdb

REPO = Path(__file__).resolve().parents[1]
DB_PATH = REPO / "data" / "abcde_genesis.duckdb"
CATALOG_JSON = REPO / "data" / "schema_catalog.json"
BUILD_SCRIPT = REPO / "scripts" / "build_genesis_db.py"

# A statement may only *start* with one of these.
_ALLOWED_PREFIXES = ("select", "with", "pragma", "explain", "show", "describe", "desc")

# These keywords may never appear (as whole words) anywhere in the statement.
_BLOCKED_KEYWORDS = (
    "insert", "update", "delete", "drop", "create", "alter", "attach", "detach",
    "copy", "install", "load", "export", "import", "truncate", "replace", "call",
    "set", "reset", "vacuum", "grant", "revoke", "merge",
)
_BLOCKED_RE = re.compile(
    r"\b(" + "|".join(_BLOCKED_KEYWORDS) + r")\b", re.IGNORECASE
)


class UnsafeSQLError(ValueError):
    """Raised when a statement is not a single read-only query."""


def _strip_comments(sql: str) -> str:
    # Remove /* block */ comments and -- line comments.
    sql = re.sub(r"/\*.*?\*/", " ", sql, flags=re.DOTALL)
    sql = re.sub(r"--[^\n]*", " ", sql)
    return sql


def assert_read_only(sql: str) -> str:
    """Return the cleaned SQL if it is a single read-only statement, else raise."""
    if not sql or not sql.strip():
        raise UnsafeSQLError("Empty query.")
    cleaned = _strip_comments(sql).strip()
    # Allow exactly one optional trailing semicolon; any other ';' means
    # multiple statements, which we reject.
    cleaned = cleaned.rstrip()
    if cleaned.endswith(";"):
        cleaned = cleaned[:-1].rstrip()
    if ";" in cleaned:
        raise UnsafeSQLError("Multiple statements are not allowed.")
    lowered = cleaned.lower()
    if not lowered.startswith(_ALLOWED_PREFIXES):
        raise UnsafeSQLError(
            "Only read-only SELECT/WITH/PRAGMA/EXPLAIN/SHOW/DESCRIBE queries are allowed."
        )
    match = _BLOCKED_RE.search(cleaned)
    if match:
        raise UnsafeSQLError(f"Disallowed keyword in query: {match.group(1).upper()}")
    return cleaned


def ensure_db() -> None:
    """Build the compact DB from committed sources if it is missing."""
    if DB_PATH.exists():
        return
    subprocess.run([sys.executable, str(BUILD_SCRIPT)], check=True)
    if not DB_PATH.exists():
        raise RuntimeError(f"build script did not produce {DB_PATH}")


def connect_read_only() -> duckdb.DuckDBPyConnection:
    ensure_db()
    return duckdb.connect(str(DB_PATH), read_only=True)


def run_select(sql: str, max_rows: int = 200) -> dict:
    """Run a guarded read-only query and return columns + capped rows."""
    cleaned = assert_read_only(sql)
    con = connect_read_only()
    try:
        cur = con.execute(cleaned)
        columns = [d[0] for d in cur.description] if cur.description else []
        rows = cur.fetchmany(max_rows)
    finally:
        con.close()
    return {
        "columns": columns,
        "rows": [[_jsonable(v) for v in row] for row in rows],
        "row_count": len(rows),
        "truncated": len(rows) >= max_rows,
    }


def load_catalog() -> dict:
    ensure_db()
    if CATALOG_JSON.exists():
        return json.loads(CATALOG_JSON.read_text(encoding="utf-8"))
    return {"tables": {}}


def _jsonable(v):
    try:
        json.dumps(v)
        return v
    except TypeError:
        return str(v)

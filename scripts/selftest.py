#!/usr/bin/env python3
"""One-shot self-test for the ABCDE clone-and-ask setup.

Run from the repo root:   py -3 scripts/selftest.py
No arguments, no API key needed. Prints PASS/FAIL for each check.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))  # so `import mcp_server` / `import ask` work from anywhere

ok = 0
fail = 0


def _try_import(mod: str) -> bool:
    try:
        __import__(mod)
        return True
    except Exception:
        return False


def check(name: str, cond: bool, detail: str = "") -> None:
    global ok, fail
    mark = "PASS" if cond else "FAIL"
    if cond:
        ok += 1
    else:
        fail += 1
    print(f"  [{mark}] {name}" + (f" - {detail}" if detail else ""))


print("ABCDE self-test")
print("repo:", REPO)
print()

# 1. Database opens read-only and has data
print("1. Database")
try:
    import duckdb

    db = REPO / "data" / "abcde_genesis.duckdb"
    check("database file exists", db.exists(), str(db))
    con = duckdb.connect(str(db), read_only=True)
    tables = [r[0] for r in con.execute("show tables").fetchall()]
    check("tables present", len(tables) > 0, f"{len(tables)} tables")
    seeds = con.execute("select label, amount_ada from seeds order by amount_ada desc").fetchall()
    check("seeds table has rows", len(seeds) > 0, f"{len(seeds)} seeds")
    for label, ada in seeds:
        print(f"        - {label}: {ada:,} ADA")
    con.close()
except Exception as e:
    check("database checks", False, repr(e))

# 2. MCP server: import, name, read-only enforcement (behavioral)
print("\n2. MCP server")


def seed_count() -> int:
    import duckdb

    c = duckdb.connect(str(REPO / "data" / "abcde_genesis.duckdb"), read_only=True)
    try:
        return c.execute("select count(*) from seeds").fetchone()[0]
    finally:
        c.close()


try:
    import mcp_server.server as s

    check("server imports", True)
    check("server name is abcde-genesis", s.mcp.name == "abcde-genesis", s.mcp.name)

    before = seed_count()
    sel = str(s.run_sql("select count(*) from seeds"))
    check("SELECT returns data", str(before) in sel or "row" in sel.lower(), sel[:70])

    # Attempt writes, then prove the data is untouched.
    for stmt in ("DROP TABLE seeds", "UPDATE seeds SET amount_ada=0", "select 1; select 2"):
        try:
            s.run_sql(stmt)
        except Exception:
            pass
    after = seed_count()
    check("writes are blocked (seeds intact)", after == before and after > 0,
          f"{before} seeds before / {after} after")
except Exception as e:
    check("MCP server checks", False, repr(e))

# 3. ask.py CLI: imports and builds a schema-grounded prompt (no API call)
print("\n3. ask.py CLI")
try:
    import ask

    check("ask.py imports", True)
    cat = (REPO / "data" / "schema_catalog.json")
    check("schema catalog present", cat.exists(), f"{cat.stat().st_size} bytes" if cat.exists() else "missing")
    check("anthropic SDK installed", _try_import("anthropic"))
    check("mcp SDK installed", _try_import("mcp"))
except Exception as e:
    check("ask.py checks", False, repr(e))


print()
print(f"RESULT: {ok} passed, {fail} failed")
sys.exit(1 if fail else 0)

#!/usr/bin/env python3
"""ask.py — CLI text-to-SQL fallback for the ABCDE genesis ADA database.

Gives Claude a single read-only ``run_sql`` tool over the compact DuckDB and
runs a bounded agentic loop until it produces a plain-English answer. The schema
catalog is embedded in a cached system prompt so repeated questions are cheap.

Usage:
  python ask.py "where did EMURGO's genesis ADA end up?"   # one-shot
  python ask.py                                            # interactive

Environment:
  ANTHROPIC_API_KEY   required
  ABCDE_MODEL         model id (default: claude-sonnet-4-6)
"""
from __future__ import annotations

import json
import os
import sys

from mcp_server.readonly import (
    UnsafeSQLError,
    load_catalog,
    run_select,
)

DEFAULT_MODEL = "claude-sonnet-4-6"
MAX_STEPS = 12
MAX_ROWS = 200

RUN_SQL_TOOL = {
    "name": "run_sql",
    "description": (
        "Run a single read-only SQL query against the genesis DuckDB and get the "
        "rows back. Only SELECT/WITH/PRAGMA/EXPLAIN/SHOW/DESCRIBE are allowed; "
        f"results are capped at {MAX_ROWS} rows. Use the schema in the system "
        "prompt to write correct DuckDB SQL."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "sql": {"type": "string", "description": "A single read-only SQL statement."},
        },
        "required": ["sql"],
    },
}


def build_system_prompt() -> str:
    catalog = load_catalog()
    lines = [
        "You are a careful Cardano genesis-ADA forensics analyst answering questions",
        "over a read-only DuckDB database. Use the run_sql tool to inspect the real",
        "data before answering; never invent table or column names.",
        "",
        "EVIDENCE RULES (see docs/02_GRADING.md): report findings as FACT,",
        "STRONG_INFERENCE, WORKING_HYPOTHESIS, or UNKNOWN. On-chain flows and",
        "delegations are what the data shows; NEVER assert off-chain legal ownership,",
        "intent, or wallet control beyond what the on-chain data demonstrates.",
        "",
        "When done, give a concise plain-English answer and cite the tables you used.",
        "",
        "=== SCHEMA CATALOG ===",
        f"database: {catalog.get('database', 'data/abcde_genesis.duckdb')}",
        "",
    ]
    for name, info in catalog.get("tables", {}).items():
        cols = ", ".join(f"{c['name']} {c['type']}" for c in info.get("columns", []))
        lines.append(f"TABLE {name} ({info.get('row_count')} rows; source {info.get('source')})")
        lines.append(f"  columns: {cols}")
        sample = info.get("sample_rows", [])
        if sample:
            lines.append(f"  sample: {json.dumps(sample[0], default=str)}")
    return "\n".join(lines)


def _do_run_sql(sql: str) -> str:
    try:
        result = run_select(sql, max_rows=MAX_ROWS)
        return json.dumps(result, default=str)
    except UnsafeSQLError as exc:
        return json.dumps({"error": f"rejected: {exc}"})
    except Exception as exc:
        return json.dumps({"error": str(exc)})


def answer(client, model: str, system_prompt: str, question: str) -> str:
    messages = [{"role": "user", "content": question}]
    system = [{"type": "text", "text": system_prompt, "cache_control": {"type": "ephemeral"}}]
    for _ in range(MAX_STEPS):
        resp = client.messages.create(
            model=model,
            max_tokens=2048,
            system=system,
            tools=[RUN_SQL_TOOL],
            messages=messages,
        )
        messages.append({"role": "assistant", "content": resp.content})
        if resp.stop_reason != "tool_use":
            return "".join(b.text for b in resp.content if b.type == "text").strip()
        tool_results = []
        for block in resp.content:
            if block.type != "tool_use":
                continue
            sql = block.input.get("sql", "") if isinstance(block.input, dict) else ""
            out = _do_run_sql(sql)
            tool_results.append(
                {"type": "tool_result", "tool_use_id": block.id, "content": out}
            )
        messages.append({"role": "user", "content": tool_results})
    return "(stopped: reached the step limit without a final answer)"


def main() -> None:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        sys.exit("ANTHROPIC_API_KEY is not set. Export it (or put it in .env) and retry.")
    try:
        import anthropic
    except ImportError:
        sys.exit("anthropic SDK not installed. Run: py -3 -m pip install -r requirements/base.txt")

    model = os.environ.get("ABCDE_MODEL", DEFAULT_MODEL)
    client = anthropic.Anthropic(api_key=api_key)
    system_prompt = build_system_prompt()

    args = [a for a in sys.argv[1:] if a.strip()]
    if args:
        print(answer(client, model, system_prompt, " ".join(args)))
        return

    print(f"ABCDE genesis Q&A (model: {model}). Ctrl-C or empty line to quit.")
    while True:
        try:
            q = input("\nask> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if not q:
            return
        print(answer(client, model, system_prompt, q))


if __name__ == "__main__":
    main()

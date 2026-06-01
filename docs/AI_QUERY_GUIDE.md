# AI Query Guide

This repo ships a compact, query-ready genesis ADA database and two ways for an
AI to query it: an **MCP server** (primary) and an **`ask.py` CLI** (fallback).

## 1. Clone, set up a venv, install

```bash
git clone https://github.com/BEACNpool/ABCDE.git
cd ABCDE

# Linux / macOS
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements/base.txt
```

```powershell
# Windows (PowerShell)
git clone https://github.com/BEACNpool/ABCDE.git
cd ABCDE
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
py -3 -m pip install -r requirements/base.txt
```

The database `data/abcde_genesis.duckdb` is committed, so you can query
immediately. If it is ever missing, both query paths rebuild it automatically
from committed sources (`scripts/build_genesis_db.py`).

> Windows note: a bare `python`/`pip` may hit the Windows Store alias. Use
> `py -3` and `py -3 -m pip` instead.

## 2. MCP server (primary, no API key)

The server is `mcp_server/server.py` (server name `abcde-genesis`). It exposes
`list_tables`, `describe_table`, `run_sql`, and `starter_questions`, all
read-only.

If you already use **Claude Code** or **OpenAI Codex** with a subscription, this
is the entire setup — **no API key required**. Queries run through your existing
login. (The `ask.py` CLI in section 3 is only for people who prefer a raw API key.)

### Claude Desktop

Add to your `claude_desktop_config.json` (Settings → Developer → Edit Config):

```json
{
  "mcpServers": {
    "abcde-genesis": {
      "command": "python",
      "args": ["-m", "mcp_server.server"],
      "cwd": "/absolute/path/to/ABCDE"
    }
  }
}
```

On Windows, use `py` as the command and a Windows path for `cwd` (note the
doubled backslashes required by JSON):

```json
{
  "mcpServers": {
    "abcde-genesis": {
      "command": "py",
      "args": ["-3", "-m", "mcp_server.server"],
      "cwd": "C:\\Users\\you\\ABCDE"
    }
  }
}
```

If you installed into a venv, point `command` at that venv's Python
(`/path/to/ABCDE/.venv/bin/python` or `C:\\Users\\you\\ABCDE\\.venv\\Scripts\\python.exe`)
so the dependencies resolve.

### Claude Code

```bash
# Linux / macOS
claude mcp add abcde-genesis -- python -m mcp_server.server
```

```powershell
# Windows
claude mcp add abcde-genesis -- py -3 -m mcp_server.server
```

Run the command from the repo root (or pass the working directory) so `cwd`
resolves to the clone. Then ask, e.g. *"Using abcde-genesis, where did EMURGO's
genesis ADA end up, and which DReps hold the most genesis-traced stake?"*

### OpenAI Codex (uses your Codex subscription)

Add to `~/.codex/config.toml`:

```toml
[mcp_servers.abcde-genesis]
command = "python"
args = ["-m", "mcp_server.server"]
cwd = "/absolute/path/to/ABCDE"
# Windows:
# command = "py"
# args = ["-3", "-m", "mcp_server.server"]
# cwd = "C:\\Users\\you\\ABCDE"
```

The server also works when launched directly by file path
(`.../mcp_server/server.py`) — it adds its own repo root to `sys.path`, so the
`cwd` form above and the file-path form are both fine.

## 3. `ask.py` CLI (API-key fallback)

A text-to-SQL loop using the Anthropic SDK. It hands Claude a read-only
`run_sql` tool and prints a plain-English answer.

```bash
export ANTHROPIC_API_KEY=sk-ant-...     # or put it in .env
# optional: export ABCDE_MODEL=claude-sonnet-4-6   (default)

python ask.py "where did EMURGO's genesis ADA end up?"   # one-shot
python ask.py                                            # interactive
```

```powershell
# Windows
$env:ANTHROPIC_API_KEY = "sk-ant-..."
py -3 ask.py "which DReps hold the most genesis-traced stake?"
```

## 4. Full / large dataset

The compact in-repo DB is for instant clone-and-ask and is the supported public
dataset in a plain clone. Large/full extraction cuts are published via GitHub
Releases when a release is available:

```bash
python scripts/fetch_db.py              # latest release, if one exists
python scripts/fetch_db.py --tag v2.0.0 # a specific tag
```

It downloads into `data/release/` (gitignored) and verifies every asset against
the `artifacts.sha256` manifest shipped in the release. If no release exists
yet, use the committed `data/abcde_genesis.duckdb` and `data/small/*.csv`
receipts. Requires the GitHub CLI (`gh`) authenticated.

## 5. Safety notes

- The DB is opened `read_only=True`; only a single
  `SELECT`/`WITH`/`PRAGMA`/`EXPLAIN`/`SHOW`/`DESCRIBE` is allowed. Writes,
  multi-statements, and `ATTACH`/`COPY`/`INSTALL`/`LOAD`/etc. are rejected.
- Treat every answer under the evidence grading standard in `docs/02_GRADING.md`.
- Use `prompts/audit_every_figure.md` for a structured AI review and
  `python scripts/verify_claim_receipts.py` for machine-checkable headline
  claim receipts.
- Never assert off-chain ownership, intent, or wallet control beyond what the
  on-chain flows and delegations show (see `CLAUDE.md`).
- See `docs/STARTER_QUESTIONS.md` for grounded example questions.

<div align="center">

# ⬡ ABCDE

### A BEACN Cardano Data Explorer

**Clone the repo. Query the evidence. Check the claims yourself.**

An open-source collection of queryable Cardano evidence: **genesis ADA**
traces, founder-related governance records, the **NIGHT** token distribution and
July 2026 bridge drain, the **SecondFi** incident, community exchange tracers,
and stake-pool relay observations. A plain clone contains selected snapshots
and receipts; the full Cardano chain and maintainer warehouse are not included.

No node. No relay. No db-sync. No API key. Just `git clone` and ask.

<br>

![Cardano](https://img.shields.io/badge/Cardano-public%20evidence-0033AD?style=for-the-badge)
![Query](https://img.shields.io/badge/query-DuckDB%20%2B%20AI-000000?style=for-the-badge)
![No dbsync](https://img.shields.io/badge/no%20node%20·%20no%20db--sync-required-2ea44f?style=for-the-badge)
![Evidence](https://img.shields.io/badge/every%20claim-graded-8A2BE2?style=for-the-badge)
![License](https://img.shields.io/badge/license-MIT-lightgrey?style=for-the-badge)

**Queryable CSVs + DuckDB · graded findings · reproducible claim receipts**

*Each module has its own snapshot boundary. Inspect its receipt or manifest, then `build_info` and `data_freshness_catalog`; a newer module does not refresh older tables.*

<br>

[![Watch the 90-second tour](https://beacnpool.github.io/ABCDE/og/main.png)](https://beacnpool.github.io/ABCDE/media/abcde-showcase-720p.mp4)

**[▶ Watch the 90-second tour](https://beacnpool.github.io/ABCDE/media/abcde-showcase-720p.mp4)** — a real clone, a real Claude Code session, and the NIGHT bridge-drain receipts pulled live.

</div>

---

## Why this exists

Cardano's genesis allocations and transaction history are public, but joining
flows, delegation certificates and governance records for an audit can require
a large chain index. ABCDE publishes selected extracts so people can check
specific claims without maintaining that infrastructure.

ABCDE flips that. The whole compact dataset is **committed to this repo as one
small DuckDB file**. Clone it and you have an instant, local, read-only database
of genesis-ADA flows, delegation history, governance behavior, and exchange
tracing — ready for an AI to query in plain English, **without touching the
chain and without a single shared server anyone could break.** Everyone
checking out the same commit gets the same dataset and can verify its published
receipts. Full-depth lineage, current beneficial ownership and
unpublished warehouse queries are not implied by that reproducibility.

```
   the old way                              ABCDE
┌────────────────────┐            ┌────────────────────────┐
│ full node (100s GB)│            │  git clone (compact)  │
│ + relay            │            │                        │
│ + db-sync Postgres │   ──────►  │  ask your AI, locally  │
│ + days of sync     │            │  read-only, reproducible│
└────────────────────┘            └────────────────────────┘
```

---

## ⚡ 30-second quickstart

```bash
git clone https://github.com/BEACNpool/ABCDE.git
cd ABCDE
python -m venv .venv && source .venv/bin/activate    # Windows: py -3 -m venv .venv ; .venv\Scripts\activate
python -m pip install -r requirements/base.txt
```

*(The venv matters: modern Ubuntu/Debian pythons refuse bare `pip install` — PEP 668.)*

Use it with an MCP-compatible AI client such as Codex. From the clone root,
with the virtual environment active:

```bash
codex mcp add abcde-genesis -- "$PWD/.venv/bin/python" "$PWD/mcp_server/server.py"
```

The local database needs no API key; any AI client uses its own authentication.

…and just ask:

> **"Where did EMURGO's genesis ADA end up — which pools and DReps does the trace reach?"**
>
> **"How much genesis-descended ADA is still unspent, and how confident is the trace?"**
>
> **"Which exchanges are named in the on-chain tracer deposit claims?"**
>
> **"Which stake pools advertise a relay that another pool also advertises?"**

The read-only MCP server exposes four tools — `list_tables()`,
`describe_table(name)`, `run_sql(sql)`, `starter_questions()` — and **rejects
writes and multi-statement input**, so the AI can explore freely
without ever mutating the data.

You can also query directly without an AI:

```bash
python scripts/query_duckdb.py claims/sql/seed_allocations.sql
```

More client configuration is in [`docs/AI_QUERY_GUIDE.md`](docs/AI_QUERY_GUIDE.md).
The historical `ask.py` CLI requires a separate provider API key; MCP and direct
SQL do not depend on that CLI.

---

## What's inside

| Area | What you can ask |
|---|---|
| 🌱 **Genesis seeds** | Three named founder allocations — IOG `2.46B`, EMURGO `2.07B`, Cardano Foundation `648M` — and a separate `781M` entry whose beneficial owner is unresolved, with verification receipts. |
| 🔀 **Traces** | Bounded and depth-14 staged traces of where each seed's ADA flowed, plus cross-entity merge candidate sets. |
| 💰 **IOG trace snapshot** | Unspent outputs reached by the depth-14 IOG trace at its recorded boundary, with heuristic bands and a value-ranked UTxO cut. Trace membership is not an IOG-owned balance. |
| 🗳️ **Governance** | Genesis-trace delegation surfaces plus a founder-accountability cut of DRep identities, epoch distributions, votes and proposal lifecycle records. [Evidence guide](docs/28_FOUNDER_ACCOUNTABILITY_EVIDENCE.md). |
| 🧭 **Control indicators** | Snapshot custody indicators per trace-reached stake key — dormancy, unclaimed rewards, certificate liveness, batch-operation cohorts — with a graded `fe_control_consistency` score. |
| 🌙 **NIGHT token** | Companion module: supply and concentration rollups, a compact holder cut, an optional full graph at its recorded snapshot, and a receipt-backed investigation of the July 2026 Wanchain bridge drain and attacker flow. |
| 🧾 **Freshness catalog** | Source-file row counts, hashes, age and snapshot sensitivity. Use it with module receipts to establish the relevant chain boundary. |
| 📡 **Relay health** | Pool relay registrations at the module snapshot, shared endpoint strings, registration history and observed reachability. Shared infrastructure does not identify ownership; an unanswered probe is not proof of an offline relay. Live page: **[relays.html](https://beacnpool.github.io/ABCDE/relays.html)** · [F21](findings/F21_relay_registration_and_reachability.md) · [method](docs/27_RELAY_HEALTH_METHOD.md). |
| 🧮 **MINFREE** | A slider for `minPoolCost`. The floor is a flat ₳ tax taken before delegators see a lovelace — raise it and a 1M ₳ pool gets worse, saturated pools barely notice. Live: **[minfree.html](https://beacnpool.github.io/ABCDE/minfree.html)**. |
| 📡 **Exchange tracers** | A community exchange-tracer dataset (`tracer_*`); crowd-sourced attribution, kept for reference and graded accordingly. |

Ground your queries on the generated schema — [`docs/SCHEMA.md`](docs/SCHEMA.md)
(human) and `data/schema_catalog.json` (machine). Start with
[`docs/STARTER_QUESTIONS.md`](docs/STARTER_QUESTIONS.md).

---

## 🔍 Showcase: following one thread to the end

A historical worked example from the July 2026 custody cut. Its receipt chain
lives in [`findings/`](findings/INDEX.md); use its own boundary when repeating
the figures:

> Starting from **8 stake keys that each hold exactly 35,000,000 ADA**
> ([F11](findings/F11_eight_key_35m_custody_cohort.md)), we followed their
> reward-sweep plumbing downstream
> ([F13](findings/F13_reward_plumbing_downstream_and_tracer_bridge.md)),
> classified the wallets it touched
> ([F14](findings/F14_fleet_is_same_35m_parcel_structure.md)), and iterated the
> linkage to its fixpoint
> ([F15](findings/F15_plumbing_component_is_closed_floor.md)).
>
> At that snapshot: a **115-key component under the published withdrawal
> linkage**, with 50 holder keys totaling approximately **1.694B ADA**, including
> 42 approximately 35M parcels. Those 50 holders delegated to always-abstain.
> The analysis also follows a hop where genesis-descended value reaches a deposit cluster the community
> tracer campaign independently flagged as an exchange.

Every step is graded, and the grading is the point: on-chain linkage is stated as
on-chain linkage. Component membership does not establish the number of
beneficial owners or identify a founding entity as custodian.

---

## 🎓 Every claim is graded

This is an **audit tool**, not a rumor mill. Each finding carries an explicit
evidence grade ([`docs/02_GRADING.md`](docs/02_GRADING.md)):

| Grade | Meaning |
|---|---|
| **FACT** | Directly queryable / deterministic from committed artifacts. |
| **STRONG_INFERENCE** | Strongly supported by facts, not uniquely proven. |
| **WORKING_HYPOTHESIS** | Plausible model, actively tested — not a conclusion. |
| **UNKNOWN** | Not established from current evidence. |

> **The hard rule:** ABCDE maps on-chain flows and delegation behavior. It
> **never** asserts off-chain legal ownership, identity, intent, or wallet
> control beyond what the chain shows. The AI is bound by the same rule — see
> [`CLAUDE.md`](CLAUDE.md).

---

## ✅ Integrity you can verify yourself

Everyone clones the **same** dataset, and you can prove it hasn't drifted:

```bash
just test                              # self-test + public claim receipts
python scripts/verify_claim_receipts.py   # re-run headline SQL, check row counts + hashes
python scripts/build_genesis_db.py        # rebuild the DuckDB from source CSVs, deterministically
```

- **Claim receipts** ([`claims/`](claims/)) pin each headline figure to SQL, an
  expected row count, and a SHA-256 of the result. If the data changed, the hash
  fails.
- **CI** rebuilds the DB, smoke-tests a read-only query, proves the write-guard
  rejects mutations, and runs the structure verifier on every push.
- **Freshness is explicit.** `build_info` records build/global-receipt metadata;
  `data_freshness_catalog` inventories source files and their age. For a claim,
  use the relevant module's source tip, distribution epoch and query receipt.
  The [`founder evidence guide`](docs/28_FOUNDER_ACCOUNTABILITY_EVIDENCE.md)
  explains the September governance cut and the older lineage/custody cuts.
  File modification or commit time alone does not establish chain freshness.


---

## 📦 Big data, kept clonable

The compact in-repo DuckDB is deliberately small so a plain `git clone` stays
instant. When a table is too large to commit in full (e.g. the per-UTxO
drilldown), the clone keeps a **value-ranked top-cut** — retaining ~98% of the
ADA — and the full table ships as a release-tier artifact:

```bash
python scripts/fetch_db.py             # pull full cuts from the latest GitHub Release (if published)
```

The **full NIGHT spend-flow graph** (1.36M nodes, ~630 MB) is hosted in-repo on
a **custom git ref** (`refs/night-full/data`), so a normal `git clone` never
downloads it — clones stay lean — yet anyone can fetch it on demand:

```bash
python scripts/fetch_night_full.py     # git-fetch the custom ref + checksum verify
```

See [`docs/22_DATA_TOPOLOGY_AND_FRESHNESS.md`](docs/22_DATA_TOPOLOGY_AND_FRESHNESS.md)
for the compact / release / warehouse tiers and how they differ.

---

## 🗺️ Where to go next

- **New here?** → [`docs/00_START_HERE.md`](docs/00_START_HERE.md) and the
  investor-focused [What Every ADA Investor Should Know About Genesis ADA](reports/what_ada_investors_should_know_about_genesis_ada.md)
- **Want to query?** → [`docs/STARTER_QUESTIONS.md`](docs/STARTER_QUESTIONS.md) ·
  [`docs/AI_QUERY_GUIDE.md`](docs/AI_QUERY_GUIDE.md) ·
  [`docs/19_QUERY_COOKBOOK.md`](docs/19_QUERY_COOKBOOK.md)
- **Investigating founder accountability?** → [`Evidence, queries and open questions`](docs/28_FOUNDER_ACCOUNTABILITY_EVIDENCE.md)
- **Want the findings?** → [`findings/INDEX.md`](findings/INDEX.md)
- **Want the NIGHT module?** → [`docs/25_NIGHT_TOKEN_PROVENANCE.md`](docs/25_NIGHT_TOKEN_PROVENANCE.md) · [`F16`](findings/F16_night_mint_provenance_and_concentration.md) · [`F17`](findings/F17_night_wanchain_bridge_incident.md)
- **Want the exchange tracers?** → [`docs/26_EXCHANGE_TRACER_METHOD.md`](docs/26_EXCHANGE_TRACER_METHOD.md) · [`F19`](findings/F19_exchange_tracer_convergence.md)
- **Want to audit us?** → [`prompts/audit_every_figure.md`](prompts/) ·
  [`docs/02_GRADING.md`](docs/02_GRADING.md) · [`claims/`](claims/)
- **Method & limits** → [`docs/01_METHOD.md`](docs/01_METHOD.md) ·
  [`docs/06_LIMITATIONS.md`](docs/06_LIMITATIONS.md)

<div align="center">
<br>

**Built by [BEACNpool](https://github.com/BEACNpool) · MIT licensed · on-chain truth, grass-roots tools**

*If ABCDE helped you understand where the genesis ADA went, ⭐ the repo and clone it forward.*

</div>

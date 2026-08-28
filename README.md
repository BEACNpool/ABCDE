<div align="center">

# ⬡ ABCDE

### A BEACN Cardano Data Explorer

**Clone the repo. Point your AI at it. The whole chain, one clone away.**

A grass-roots, open-source, AI-queryable snapshot of Cardano's on-chain history.
It began by tracking **genesis ADA** — and grew into a full-chain explorer: the
**NIGHT** token distribution and the July 2026 bridge drain, the **SecondFi**
incident, community exchange tracers, Conway governance behavior, and the
**relay surface** of every current stake pool.

No node. No relay. No db-sync. No API key. Just `git clone` and ask.

<br>

![Cardano](https://img.shields.io/badge/Cardano-full--chain%20explorer-0033AD?style=for-the-badge)
![Query](https://img.shields.io/badge/query-DuckDB%20%2B%20AI-000000?style=for-the-badge)
![No dbsync](https://img.shields.io/badge/no%20node%20·%20no%20db--sync-required-2ea44f?style=for-the-badge)
![Evidence](https://img.shields.io/badge/every%20claim-graded-8A2BE2?style=for-the-badge)
![License](https://img.shields.io/badge/license-MIT-lightgrey?style=for-the-badge)

**`157` query-ready tables · `23` audited findings · every figure hash-receipted**

*Each module carries its own freshness receipt — the genesis cut is epoch `641`, the relay surface epoch `651`. Query `build_info` and `data_freshness_catalog` before any current-state answer.*

<br>

[![Watch the 90-second tour](https://beacnpool.github.io/ABCDE/og/main.png)](https://beacnpool.github.io/ABCDE/media/abcde-showcase-720p.mp4)

**[▶ Watch the 90-second tour](https://beacnpool.github.io/ABCDE/media/abcde-showcase-720p.mp4)** — a real clone, a real Claude Code session, and the NIGHT bridge-drain receipts pulled live.

</div>

---

## Why this exists

Cardano's founder ("genesis") ADA is public on-chain, but **answering real
questions about it normally means running a full node, a relay, and a db-sync
Postgres warehouse** — hundreds of gigabytes and days of sync before you can run
a single query.

ABCDE flips that. The whole compact dataset is **committed to this repo as one
small DuckDB file**. Clone it and you have an instant, local, read-only database
of genesis-ADA flows, delegation history, governance behavior, and exchange
tracing — ready for an AI to query in plain English, **without touching the
chain and without a single shared server anyone could break.** Everyone who
clones gets the exact same integrity-checked dataset.

```
   the old way                              ABCDE
┌────────────────────┐            ┌────────────────────────┐
│ full node (100s GB)│            │  git clone  (~36 MiB)  │
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

Then wire it into the AI you already use — **no API key if you have Claude Code,
Claude Desktop, or Codex:**

```bash
claude mcp add abcde-genesis -- python -m mcp_server.server
```

…and just ask:

> **"Where did EMURGO's genesis ADA end up — which pools and DReps does the trace reach?"**
>
> **"How much genesis-descended ADA is still unspent, and how confident is the trace?"**
>
> **"Which exchanges are named in the on-chain tracer deposit claims?"**
>
> **"Which stake pools advertise a relay that another pool also advertises?"**

The read-only MCP server exposes four tools — `list_tables()`,
`describe_table(name)`, `run_sql(sql)`, `starter_questions()` — and **rejects any
statement that isn't a single read-only `SELECT`**, so the AI can explore freely
without ever mutating the data.

<details>
<summary><b>No subscription? Use the API-key CLI instead</b></summary>

```bash
export ANTHROPIC_API_KEY=sk-ant-...
python ask.py "where did IOG's genesis ADA flow, by trace depth?"   # one-shot
python ask.py                                                        # interactive
```

Full setup for Codex `config.toml`, Claude Desktop JSON, and Windows paths is in
[`docs/AI_QUERY_GUIDE.md`](docs/AI_QUERY_GUIDE.md).

</details>

---

## What's inside `157` tables

| Area | What you can ask |
|---|---|
| 🌱 **Genesis seeds** | The four founder allocations — IOG `2.46B`, EMURGO `2.07B`, the `781M` fourth entry, Cardano Foundation `648M` — each with db-sync verification receipts. |
| 🔀 **Traces** | Bounded and depth-14 staged traces of where each seed's ADA flowed, plus cross-entity merge candidate sets. |
| 💰 **IOG current bag** | How much IOG-descended ADA is still unspent (`~494M`), with confidence bands, cluster classifications, and per-UTxO drilldown. |
| 🗳️ **Governance** | Genesis-descended stake by SPO and by DRep, pool/DRep metadata, a top-DRep profile pack, and every Conway governance action. |
| 🧭 **Control indicators** | Live custody signals per genesis stake key — dormancy, unclaimed rewards, certificate liveness, batch-operation cohorts — with a graded `fe_control_consistency` score. |
| 🌙 **NIGHT token** | Companion module: the entire 24B-NIGHT supply traced from its single genesis mint to every current holder, plus a receipt-backed investigation of the July 2026 Wanchain bridge drain and attacker flow. |
| 🧾 **Freshness catalog** | Row count, hash, age, and snapshot-sensitivity of *every* table, so any answer can state exactly how fresh its evidence is. |
| 📡 **Relay health** | Every current pool's on-chain relay registration, which pools share infrastructure or advertise relays they don't run, the full history of relay-registration changes with transaction hashes, and how much stake sits behind a single hosting provider. Live page: **[relays.html](https://beacnpool.github.io/ABCDE/relays.html)** · [F21](findings/F21_relay_registration_and_reachability.md) · [method](docs/27_RELAY_HEALTH_METHOD.md). |
| 📡 **Exchange tracers** | A community exchange-tracer dataset (`tracer_*`); crowd-sourced attribution, kept for reference and graded accordingly. |

Ground your queries on the generated schema — [`docs/SCHEMA.md`](docs/SCHEMA.md)
(human) and `data/schema_catalog.json` (machine). Start with
[`docs/STARTER_QUESTIONS.md`](docs/STARTER_QUESTIONS.md).

---

## 🔍 Showcase: following one thread to the end

A worked example of what the dataset makes possible — the full receipt chain
lives in [`findings/`](findings/INDEX.md), every number reproducible from a plain
clone:

> Starting from **8 stake keys that each hold exactly 35,000,000 ADA**
> ([F11](findings/F11_eight_key_35m_custody_cohort.md)), we followed their
> reward-sweep plumbing downstream
> ([F13](findings/F13_reward_plumbing_downstream_and_tracer_bridge.md)),
> classified the wallets it touched
> ([F14](findings/F14_fleet_is_same_35m_parcel_structure.md)), and iterated the
> linkage to its fixpoint
> ([F15](findings/F15_plumbing_component_is_closed_floor.md)).
>
> The result: a **closed 115-key component holding `1,693,922,205` ADA** in
> uniform 35M parcels, all delegated to the same always-abstain DRep — and a
> hop where genesis-descended value reaches a deposit cluster the community
> tracer campaign independently flagged as an exchange.

Every step is graded, and the grading is the point: on-chain linkage is stated as
on-chain linkage, never as real-world ownership.

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
- **Freshness is explicit.** `build_info` and `data/small/db_tip_receipt.csv`
  record the exact chain tip this cut was taken at (**block `13,630,993`, epoch
  `640`, 2026-07-03**). Current-state answers are snapshots at that tip, not live
  chain state — and the freshness catalog tells you which tables are
  snapshot-sensitive.

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

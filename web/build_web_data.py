#!/usr/bin/env python3
"""Build the static data layer for the ABCDE explorer site.

The site is an onboarding launchpad, not a query tool: it hands you copy-paste
setup for your AI + OS and shows what the dataset contains so you know what to
ask. So this emits small JSON only (no Parquet, no query engine):

  web/dist/data/
    stats.json      hero numbers (seeds, whale surface, tip)
    families.json   table families -> counts + member tables (the data map)
    questions.json  curated example questions grouped by theme
    findings.json   findings list (title, grade, claim) -> GitHub
    showcase.json   a small on-chain "taste" (seeds, whale, hubs) — no crowd data

Deliberately omits the crowd-sourced exchange-tracer attribution from the site
(it stays in the repo/DB, just not broadcast). Run: python web/build_web_data.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "abcde_genesis.duckdb"
OUT = ROOT / "web" / "dist" / "data"


def q1(con, sql):
    return con.execute(sql).fetchone()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(DB), read_only=True)

    tip = q1(con, "SELECT db_tip_block, db_tip_epoch, db_tip_time FROM build_info")
    seeds = con.execute(
        "SELECT label, amount_ada, source_type, evidence_grade FROM seeds "
        "ORDER BY amount_ada DESC").fetchall()
    holders = q1(con, "SELECT count(*) FROM component_control_indicators WHERE current_ada>=1000")[0]
    exact35 = q1(con, "SELECT count(*) FROM component_control_indicators WHERE abs(current_ada-35000000)<2")[0]
    comp_ada = q1(con, "SELECT round(sum(current_ada)) FROM component_control_indicators WHERE current_ada>=1000")[0]
    comp_keys = q1(con, "SELECT count(*) FROM f15_cowithdrawal_component")[0]
    n_tables = q1(con, "SELECT count(*) FROM information_schema.tables WHERE table_schema='main'")[0]
    total_rows = q1(con, """SELECT sum(cnt) FROM (
        SELECT (SELECT count(*) FROM information_schema.tables) ) t""")[0] if False else None
    iog_bag = q1(con, "SELECT round(current_ada) FROM iog_current_bag_depth14_summary")[0]

    stats = {
        "tip_block": tip[0], "tip_epoch": tip[1], "tip_time": str(tip[2]),
        "tables": n_tables,
        "seeds": [{"label": s[0], "amount_ada": s[1], "source_type": s[2], "grade": s[3]} for s in seeds],
        "seed_total_ada": sum(s[1] for s in seeds),
        "component_keys": comp_keys, "component_holders": holders,
        "exact_35m": exact35, "component_ada": comp_ada, "iog_bag_ada": iog_bag,
    }
    (OUT / "stats.json").write_text(json.dumps(stats, indent=2))

    # --- families (the data map) from the committed table catalog ----------
    cat = json.loads((ROOT / "data" / "table_catalog.json").read_text())
    fam: dict[str, dict] = {}
    for t in cat["tables"]:
        f = fam.setdefault(t["family"], {"family": t["family"], "table_count": 0,
                                         "total_rows": 0, "tables": []})
        f["table_count"] += 1
        f["total_rows"] += t.get("row_count") or 0
        f["tables"].append({"table": t["table"], "rows": t.get("row_count"),
                            "findings": t.get("findings", [])})
    order = ["Genesis seeds", "Traces", "IOG current bag", "Governance rollups",
             "Genesis→DRep behavior", "Control indicators", "Reward-plumbing receipts",
             "IOGP / voucher", "Genesis Trail", "Fourth entry", "NIGHT token",
             "Exchange tracers", "Meta", "Other"]
    fams = sorted(fam.values(), key=lambda x: (order.index(x["family"]) if x["family"] in order else 99))
    (OUT / "families.json").write_text(json.dumps(fams, indent=2))

    # --- curated example questions (what to ask) --------------------------
    questions = [
        {"theme": "Where the genesis ADA went", "qs": [
            "Where did EMURGO's genesis ADA end up — which pools and DReps does the trace reach?",
            "Where did IOG's genesis ADA flow, by trace depth?",
            "How much IOG-descended ADA is still unspent, and how confident is the trace?"]},
        {"theme": "The founder seeds", "qs": [
            "Which named founder entities are in the seeds table, and how much did each receive?",
            "What is the evidence grade on the 781,381,495 ADA fourth entry?"]},
        {"theme": "Custody & control", "qs": [
            "Which genesis-descended stake keys hold exactly 35,000,000 ADA, and how are they classified?",
            "How much genesis-descended ADA sits with stake keys whose rewards were never withdrawn?",
            "Which stake keys show recent certificate activity while their principal hasn't moved in years?"]},
        {"theme": "Governance", "qs": [
            "Which DReps hold the most genesis-traced stake?",
            "Which stake pools received the most genesis-descended delegation?"]},
        {"theme": "Freshness & method", "qs": [
            "What chain tip is this snapshot taken at, and which tables are snapshot-sensitive?",
            "For any figure you give me, cite the table and its evidence grade."]},
    ]
    (OUT / "questions.json").write_text(json.dumps(questions, indent=2))

    # --- showcase: on-chain taste only (no crowd tracer data) -------------
    top_parcels = con.execute(
        "SELECT stake_address, current_ada, current_drep, withdrawal_count "
        "FROM component_control_indicators WHERE current_ada>=1000 "
        "ORDER BY current_ada DESC LIMIT 8").fetchall()
    hubs = con.execute(
        "SELECT address, lifetime_outputs, gross_received_ada FROM f11_hub_classification "
        "ORDER BY gross_received_ada DESC").fetchall()
    showcase = {
        "seeds": stats["seeds"],
        "whale": {"component_keys": comp_keys, "holders": holders, "exact_35m": exact35,
                  "total_ada": comp_ada,
                  "parcels": [{"stake_address": p[0], "ada": p[1], "drep": p[2],
                               "withdrawals": p[3]} for p in top_parcels]},
        "hubs": [{"address": h[0], "lifetime_outputs": h[1], "gross_received_ada": h[2]} for h in hubs],
    }
    (OUT / "showcase.json").write_text(json.dumps(showcase, indent=2, default=str))

    # --- findings ---------------------------------------------------------
    fj = json.loads((ROOT / "findings" / "findings.json").read_text())
    findings = []
    for f in fj["findings"]:
        md = ROOT / f["file"]
        claim = ""
        if md.exists():
            m = re.search(r"##\s+Claim\s*\n+(.+?)(?:\n##|\Z)", md.read_text(encoding="utf-8"), re.S)
            if m:
                claim = re.sub(r"\s+", " ", m.group(1)).strip()[:360]
        findings.append({"id": f["id"], "title": f["title"], "grade": f.get("index_label", ""),
                         "claim": claim or f.get("claim", ""),
                         "url": f"https://github.com/BEACNpool/ABCDE/blob/main/{f['file']}"})
    (OUT / "findings.json").write_text(json.dumps(findings, indent=2))

    print(f"done. families={len(fams)}, findings={len(findings)}, tables={n_tables}")


if __name__ == "__main__":
    main()

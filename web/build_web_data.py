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
        {"theme": "Follow the founders' money", "qs": [
            "Where did EMURGO's 2 billion ADA actually go — which pools and DReps does the trace reach?",
            "How much of the 2017 founder ADA is still sitting unspent, and where?",
            "Trace IOG's genesis ADA hop by hop — how deep does it go before it stops?"]},
        {"theme": "The uncomfortable questions", "qs": [
            "Which billion-ADA wallets never vote in governance?",
            "How much genesis-descended ADA has funneled into exchange-scale wallets?",
            "Find stake keys that haven't moved their principal in years but keep renewing certificates — who's still holding the keys?"]},
        {"theme": "The 1.69-billion-ADA operation", "qs": [
            "Show me every wallet holding exactly 35,000,000 ADA and how they vote.",
            "Is the 115-key genesis cluster really one operation, or coincidence? What's the evidence and its grade?"]},
        {"theme": "NIGHT: who got the airdrop?", "qs": [
            "Who holds the single 25%-of-supply NIGHT position, and has it moved?",
            "How concentrated is NIGHT really — what do the top 5, 10, and 100 addresses hold?",
            "Does every NIGHT token trace back to the genesis mint with nothing unaccounted?"]},
        {"theme": "Keep me honest", "qs": [
            "For every figure you give me, cite the exact table and its evidence grade.",
            "What can this data NOT prove — where does on-chain linkage stop short of ownership?"]},
    ]
    (OUT / "questions.json").write_text(json.dumps(questions, indent=2))

    # --- hooks: provocative-but-provable headlines (real numbers, graded) -
    def q(sql):
        return con.execute(sql).fetchone()
    night_top_pct = q("SELECT pct_of_supply FROM night_holder_top ORDER BY qty_night DESC LIMIT 1")[0]
    night_top5 = q("SELECT cumulative_pct FROM night_concentration_curve WHERE top_n=5")[0]
    night_top10 = q("SELECT cumulative_pct FROM night_concentration_curve WHERE top_n=10")[0]
    night_depth = int(float(q("SELECT value FROM night_summary WHERE metric='max_flow_level'")[0]))
    night_holders = int(float(q("SELECT value FROM night_summary WHERE metric='reachable_current_leaf_utxos'")[0]))
    hub_gross = q("SELECT max(gross_received_ada) FROM f11_hub_classification")[0]
    hub_x = hub_gross / 45_600_000_000  # vs ~total ADA supply
    hooks = [
        {"slug": "night-25", "kicker": "NIGHT", "grade": "FACT",
         "headline": "6 Billion NIGHT. One Address. One UTxO.",
         "sub": f"A quarter of the entire NIGHT supply — {night_top_pct:.2f}% — sits unspent in a single output held by one address.",
         "ask": "How concentrated is the NIGHT supply, and how much does the single largest address hold?"},
        {"slug": "35m-cohort", "kicker": "Genesis ADA", "grade": "STRONG_INFERENCE",
         "headline": f"{exact35} Wallets. The Exact Same 35,000,000 ADA. One Silent Vote.",
         "sub": f"A closed {comp_keys}-key operation holds {comp_ada/1e9:.2f} billion ADA — and every wallet is delegated to “always abstain.”",
         "ask": "Which genesis-descended stake keys hold exactly 35,000,000 ADA, and how do they all vote?"},
        {"slug": "supply-hub", "kicker": "Genesis ADA", "grade": "FACT",
         "headline": f"One Wallet Has Received {hub_x:.1f}× All the ADA in Existence.",
         "sub": f"{hub_gross/1e9:.0f} billion ADA has cycled through a single address — the structural signature of an exchange-scale hot wallet.",
         "ask": "Which addresses have gross-received more ADA than the total supply, and what does that imply?"},
        {"slug": "night-depth", "kicker": "NIGHT", "grade": "FACT",
         "headline": f"Every NIGHT Token, Traced From One Mint — {night_depth:,} Hops Deep.",
         "sub": f"The full spend graph of the 24-billion-NIGHT airdrop closes exactly: {night_holders:,} current holders, zero unaccounted.",
         "ask": "Does the traced NIGHT supply conserve back to the 24 billion genesis mint?"},
        {"slug": "night-top5", "kicker": "NIGHT", "grade": "FACT",
         "headline": "It Takes Just 5 Wallets to Hold Half of NIGHT.",
         "sub": f"Top 5 addresses: {night_top5:.1f}%. Top 10: {night_top10:.1f}%. The airdrop is steeply concentrated at the top.",
         "ask": "What share of NIGHT do the top 5 and top 10 addresses hold?"},
        {"slug": "genesis-unspent", "kicker": "Genesis ADA", "grade": "FACT",
         "headline": "Half a Billion ADA From 2017's Genesis Has Never Moved.",
         "sub": f"~{iog_bag/1e6:.0f}M ADA descended from IOG's genesis allocation still sits unspent, traced 14 hops from the source.",
         "ask": "How much IOG-descended genesis ADA is still unspent, and how confident is the trace?"},
    ]
    (OUT / "hooks.json").write_text(json.dumps(hooks, indent=2))

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

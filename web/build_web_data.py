#!/usr/bin/env python3
"""Build the static web-explorer data layer from the shipped DuckDB.

Everything the site needs is prebuilt here so the page is fully functional
without any backend:

  web/dist/data/
    stats.json        hero numbers (seeds, whale surface, tracers, tip)
    featured.json     curated entities for the guided explorer
    findings.json     findings list (title, grade, summary) for browse/search
    catalog.json      the table catalog (family / rows / snapshot / finding)
    parquet/*.parquet a curated table set for the in-browser DuckDB-WASM console
    parquet/manifest.json  table -> columns, for the console schema browser

Run:  python web/build_web_data.py   (reads data/abcde_genesis.duckdb)
Idempotent; deterministic. Outputs are gitignored (built for deploy).
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "abcde_genesis.duckdb"
OUT = ROOT / "web" / "dist" / "data"
PARQUET = OUT / "parquet"

# Tables exported to Parquet for the live SQL console. Curated to the
# compelling, queryable surface (not all 105) to keep the download small.
EXPORT_TABLES = [
    "seeds", "seed_registry",
    "genesis_control_indicators", "fleet_control_indicators",
    "component_control_indicators", "component_control_summary",
    "f15_cowithdrawal_component", "f11_downstream_fleet",
    "f11_hub_classification", "f11_downstream_hop_destinations",
    "tracer_address_summary", "tracer_deposit_claims", "tracer_transfer_edges",
    "tracer_asset_current_location", "tracer_stake_summary",
    "governance_top_drep_profiles_current", "governance_actions_catalog",
    "iog_current_bag_depth14_top_stake", "iog_current_bag_depth14_summary",
    "epoch_context", "data_freshness_catalog", "build_info", "table_catalog",
]


def q1(con, sql):
    return con.execute(sql).fetchone()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    PARQUET.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(DB), read_only=True)

    tip = q1(con, "SELECT db_tip_block, db_tip_epoch, db_tip_time FROM build_info")
    seeds = con.execute(
        "SELECT label, amount_ada, source_type, evidence_grade FROM seeds "
        "ORDER BY amount_ada DESC").fetchall()

    holders = q1(con, "SELECT count(*) FROM component_control_indicators WHERE current_ada>=1000")[0]
    exact35 = q1(con, "SELECT count(*) FROM component_control_indicators WHERE abs(current_ada-35000000)<2")[0]
    comp_ada = q1(con, "SELECT round(sum(current_ada)) FROM component_control_indicators WHERE current_ada>=1000")[0]
    comp_keys = q1(con, "SELECT count(*) FROM f15_cowithdrawal_component")[0]
    tracer_nfts = q1(con, "SELECT count(*) FROM tracer_asset_current_location")[0]
    tracer_addr = q1(con, "SELECT count(*) FROM tracer_address_summary")[0]
    n_tables = q1(con, "SELECT count(*) FROM information_schema.tables WHERE table_schema='main'")[0]
    iog_bag = q1(con, "SELECT round(current_ada) FROM iog_current_bag_depth14_summary")[0]

    stats = {
        "tip_block": tip[0], "tip_epoch": tip[1], "tip_time": str(tip[2]),
        "tables": n_tables,
        "seeds": [{"label": s[0], "amount_ada": s[1], "source_type": s[2], "grade": s[3]} for s in seeds],
        "seed_total_ada": sum(s[1] for s in seeds),
        "component_keys": comp_keys, "component_holders": holders,
        "exact_35m": exact35, "component_ada": comp_ada,
        "tracer_nfts": tracer_nfts, "tracer_addresses": tracer_addr,
        "iog_bag_ada": iog_bag,
    }
    (OUT / "stats.json").write_text(json.dumps(stats, indent=2))

    # --- featured entities for the guided explorer -----------------------
    exchanges = {}
    for (mj,) in con.execute("SELECT metadata_json FROM tracer_deposit_claims").fetchall():
        for ex in ("Coinbase", "Kraken", "Binance", "KuCoin", "Kucoin", "Bybit", "Gate.io"):
            if ex.lower() in (mj or "").lower():
                key = "KuCoin" if ex.lower() == "kucoin" else ex
                exchanges[key] = exchanges.get(key, 0) + 1
    top_parcels = con.execute(
        "SELECT stake_address, current_ada, current_drep, withdrawal_count, custody_pattern "
        "FROM component_control_indicators WHERE current_ada>=1000 "
        "ORDER BY current_ada DESC LIMIT 12").fetchall()
    hubs = con.execute(
        "SELECT address, lifetime_outputs, gross_received_ada FROM f11_hub_classification "
        "ORDER BY gross_received_ada DESC").fetchall()
    top_dreps = con.execute(
        "SELECT * FROM governance_top_drep_profiles_current LIMIT 10").fetchall()
    drep_cols = [d[0] for d in con.execute("SELECT * FROM governance_top_drep_profiles_current LIMIT 0").description]

    featured = {
        "seeds": stats["seeds"],
        "whale": {
            "component_keys": comp_keys, "holders": holders, "exact_35m": exact35,
            "total_ada": comp_ada,
            "parcels": [
                {"stake_address": p[0], "ada": p[1], "drep": p[2],
                 "withdrawals": p[3], "pattern": p[4]} for p in top_parcels],
        },
        "hubs": [{"address": h[0], "lifetime_outputs": h[1], "gross_received_ada": h[2]} for h in hubs],
        "exchanges": [{"name": k, "claim_txs": v} for k, v in
                      sorted(exchanges.items(), key=lambda kv: -kv[1])],
        "top_dreps": [dict(zip(drep_cols, r)) for r in top_dreps],
    }
    (OUT / "featured.json").write_text(json.dumps(featured, indent=2, default=str))

    # --- findings (from findings.json + markdown titles) -----------------
    fj = json.loads((ROOT / "findings" / "findings.json").read_text())
    findings = []
    for f in fj["findings"]:
        md = ROOT / f["file"]
        claim = ""
        if md.exists():
            text = md.read_text(encoding="utf-8")
            m = re.search(r"##\s+Claim\s*\n+(.+?)(?:\n##|\Z)", text, re.S)
            if m:
                claim = re.sub(r"\s+", " ", m.group(1)).strip()[:400]
        findings.append({
            "id": f["id"], "title": f["title"], "grade": f.get("index_label", ""),
            "claim": claim or f.get("claim", ""),
            "url": f"https://github.com/BEACNpool/ABCDE/blob/main/{f['file']}",
        })
    (OUT / "findings.json").write_text(json.dumps(findings, indent=2))

    # --- table catalog ----------------------------------------------------
    cat = json.loads((ROOT / "data" / "table_catalog.json").read_text())
    (OUT / "catalog.json").write_text(json.dumps(cat, indent=2))

    # --- parquet export + schema manifest --------------------------------
    manifest = {}
    for t in EXPORT_TABLES:
        exists = q1(con, f"SELECT count(*) FROM information_schema.tables "
                          f"WHERE table_schema='main' AND table_name='{t}'")[0]
        if not exists:
            print(f"  skip (absent): {t}")
            continue
        con.execute(
            f"COPY (SELECT * FROM \"{t}\") TO '{PARQUET / (t + '.parquet')}' "
            f"(FORMAT PARQUET, COMPRESSION ZSTD)")
        cols = con.execute(f'SELECT * FROM "{t}" LIMIT 0').description
        n = q1(con, f'SELECT count(*) FROM "{t}"')[0]
        manifest[t] = {"rows": n, "columns": [c[0] for c in cols]}
        print(f"  parquet {t}: {n} rows, {len(cols)} cols")
    (PARQUET / "manifest.json").write_text(json.dumps(manifest, indent=2))

    total = sum(p.stat().st_size for p in PARQUET.glob("*.parquet"))
    print(f"done. {len(manifest)} parquet tables, {total/1e6:.1f} MB total")


if __name__ == "__main__":
    main()

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
from datetime import timezone
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
        {"theme": "Trace the Wanchain NIGHT bridge hack", "qs": [
            "How much NIGHT was drained from the Wanchain bridge on 2026-07-20, and what share of the bridge was that?",
            "List the 6,450 fresh addresses the stolen ADA was split into — how much is in each, and is any spent yet?",
            "Show the labeled wallets in the bridge incident with their roles, current balances, and the grade of each label.",
            "Where did the bridge's NIGHT inventory come from — trace it back toward the genesis settlement."]},
        {"theme": "Trace the SecondFi / Yoroi incident", "qs": [
            "How much ADA was confirmed stolen in the SecondFi incident, and how much was swept into the contested 129M vault?",
            "What is the current balance of the SecondFi contested vault, the recovery fund, and the second-attacker wallet — and has any of it moved?",
            "How many wallets were cryptographically confirmed key-exposed, and at what rate per ring?",
            "Show the labeled SecondFi wallets and where the confirmed-theft ADA was routed."]},
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
    inc_drained = float(q("SELECT value FROM night_incident_summary WHERE metric='night_drained'")[0])
    inc_pct = float(q("SELECT value FROM night_incident_summary WHERE metric='pct_of_bridge_night_taken'")[0])
    inc_fan_n, inc_fan_ada = q("SELECT count(*), sum(ada) FROM night_incident_ada_fanout WHERE is_spent='f'")
    sf_theft = float(q("SELECT value FROM secondfi_incident_summary WHERE metric='confirmed_theft_ada'")[0])
    sf_vault = float(q("SELECT value FROM secondfi_incident_summary WHERE metric='contested_vault_ada_now'")[0])
    sf_exposed = int(float(q("SELECT value FROM secondfi_incident_summary WHERE metric='key_exposure_confirmed_stakes'")[0]))
    emurgo_left = float(q("SELECT ada FROM emurgo_genesis_leftover_by_drep_bucket WHERE bucket = 'EMURGO official'")[0])
    emurgo_pull = abs(float(q("SELECT delta_ada FROM emurgo_drep_epoch_deltas WHERE \"window\" = 'community7_removal' AND label = 'community7_total'")[0]))
    hooks = [
        {"slug": "emurgo-drep", "kicker": "EMURGO DRep", "grade": "FACT",
         "headline": f"EMURGO's DRep Still Has 297M. Genesis Left On It: {emurgo_left:,.1f} ADA.",
         "sub": f"They pulled ~{emurgo_pull/1e6:.1f}M ADA off the seven community DReps at epoch 578. What remains on their official DRep is a single depth-14 leftover. Clone the repo and run the query.",
         "ask": "Did EMURGO actually remove genesis ADA from its DRep, and how much is left there?"},
        {"slug": "night-bridge-drain", "kicker": "NIGHT bridge incident", "grade": "FACT",
         "headline": f"{inc_pct:.1f}% of a Bridge, Gone in 8 Minutes.",
         "sub": f"Four transactions moved {inc_drained/1e6:.1f}M NIGHT out of the Wanchain bridge on 2026-07-20; {inc_fan_n:,} fresh wallets now hold {inc_fan_ada/1e6:.2f}M ADA of the proceeds — exactly 5,000 ADA each, still unspent.",
         "ask": "Trace the 2026-07-20 Wanchain NIGHT bridge drain: how much was taken and where is the ADA now?"},
        {"slug": "secondfi-frozen", "kicker": "SecondFi incident", "grade": "FACT",
         "headline": f"{sf_vault/1e6:.0f}M ADA, Swept Into One Vault, Not a Lovelace Out.",
         "sub": f"The confirmed SecondFi theft was {sf_theft/1e6:.2f}M ADA; a further {sf_vault/1e6:.1f}M ADA was consolidated into a single wallet that has zero outflows since 2026-06-25. {sf_exposed:,} wallets were cryptographically confirmed key-exposed. Query the current state yourself.",
         "ask": "What is the current balance of the SecondFi contested vault and the recovery fund, and has any of it moved?"},
        {"slug": "night-25", "kicker": "NIGHT", "grade": "FACT",
         "headline": "6 Billion NIGHT. One Address. One UTxO.",
         "sub": f"A quarter of the entire NIGHT supply — {night_top_pct:.2f}% — sits unspent in a single output held by one address.",
         "ask": "How concentrated is the NIGHT supply, and how much does the single largest address hold?"},
        {"slug": "35m-cohort", "kicker": "Genesis ADA", "grade": "STRONG_INFERENCE",
         "headline": f"{exact35} Wallets. The Exact Same 35,000,000 ADA. One Silent Vote.",
         "sub": f"A closed {comp_keys}-key operation holds {comp_ada/1e9:.2f} billion ADA — and every wallet is delegated to “always abstain.”",
         "ask": "Which genesis-descended stake keys hold exactly 35,000,000 ADA, and how do they all vote?"},
        {"slug": "supply-hub", "kicker": "Genesis ADA", "grade": "FACT",
         "headline": f"One Address Has Received {hub_x:.1f}× All the ADA in Existence.",
         "sub": f"{hub_gross/1e9:.0f} billion ADA has cycled through a single address — the structural signature of an exchange-scale hot wallet.",
         "ask": "Which addresses have gross-received more ADA than the total supply, and what does that imply?"},
        {"slug": "night-depth", "kicker": "NIGHT", "grade": "FACT",
         "headline": f"Every NIGHT Token, Traced From One Mint — {night_depth:,} Hops Deep.",
         "sub": f"The full spend graph of the 24-billion-NIGHT distribution closes exactly: {night_holders:,} current unspent leaf UTxOs, zero unaccounted.",
         "ask": "Does the traced NIGHT supply conserve back to the 24 billion genesis mint?"},
        {"slug": "night-top5", "kicker": "NIGHT", "grade": "FACT",
         "headline": "It Takes Just 5 Addresses to Hold Half of NIGHT.",
         "sub": f"Top 5 addresses: {night_top5:.1f}%. Top 10: {night_top10:.1f}%. The airdrop is steeply concentrated at the top.",
         "ask": "What share of NIGHT do the top 5 and top 10 addresses hold?"},
        {"slug": "genesis-unspent", "kicker": "Genesis ADA", "grade": "FACT",
         "headline": "Half a Billion IOG-Descended ADA Remains Unspent.",
         "sub": f"~{iog_bag/1e6:.0f}M ADA descended from IOG's genesis allocation sits in current UTxOs reached by a depth-14 trace.",
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

    # --- relay health -----------------------------------------------------
    # The relay page is data-driven so its published numbers can never drift
    # from the DuckDB. Older cuts have no relay tables; skip silently.
    have_relay = con.execute(
        "SELECT count(*) FROM information_schema.tables "
        "WHERE table_name = 'relay_pool_health'").fetchone()[0]
    if have_relay:
        def rows(sql):
            cur = con.execute(sql)
            cols = [d[0] for d in cur.description]
            return [dict(zip(cols, r)) for r in cur.fetchall()]

        relay = {
            # Emit strict UTC ISO-8601. str(datetime) uses a space separator,
            # which browsers parse inconsistently, and the local offset would
            # publish the operator's timezone for no reason.
            "checked_at": q1(con, "SELECT max(last_checked) FROM relay_pool_health"
                             )[0].astimezone(timezone.utc).isoformat(timespec="seconds"),
            "totals": rows("""
                SELECT count(*) AS pools, sum(stake_ada) AS stake_ada,
                       sum(delegators) AS delegators
                FROM relay_pool_health""")[0],
            "registration": rows("""
                SELECT registration_class AS class, count(*) AS pools,
                       sum(stake_ada) AS stake_ada
                FROM relay_pool_health GROUP BY 1 ORDER BY 2 DESC"""),
            "reachability": rows("""
                SELECT reachability_class AS class, count(*) AS pools,
                       sum(stake_ada) AS stake_ada, sum(delegators) AS delegators
                FROM relay_pool_health GROUP BY 1 ORDER BY 2 DESC"""),
            "by_stake_band": rows("""
                SELECT CASE WHEN coalesce(stake_ada,0)=0 THEN 'no active stake'
                            WHEN stake_ada < 100000   THEN 'under 100k ADA'
                            WHEN stake_ada < 1000000  THEN '100k - 1M ADA'
                            WHEN stake_ada < 10000000 THEN '1M - 10M ADA'
                            ELSE '10M ADA and above' END AS band,
                       count(*) AS pools,
                       count(*) FILTER (WHERE reachability_class='NONE_REACHABLE') AS none_reachable,
                       round(100.0*count(*) FILTER (WHERE reachability_class='NONE_REACHABLE')
                             / count(*), 1) AS pct_none
                FROM relay_pool_health
                GROUP BY 1 ORDER BY min(coalesce(stake_ada,0))"""),
            "shared_endpoints": rows("""
                SELECT endpoint, pools, stake_ada, delegators, tickers
                FROM relay_shared_endpoints ORDER BY stake_ada DESC NULLS LAST LIMIT 15"""),
            "shared_hosts": rows("""
                SELECT resolved_ip, target_port, pools, stake_ada, delegators,
                       distinct_registered_names, tickers
                FROM relay_shared_hosts ORDER BY pools DESC, stake_ada DESC NULLS LAST LIMIT 15"""),
            "by_minting": rows("""
                SELECT minted_last_30_epochs AS minting, reachability_class AS class,
                       count(*) AS pools, sum(stake_ada) AS stake_ada
                FROM relay_pool_health GROUP BY 1, 2 ORDER BY 1 DESC, 3 DESC"""),
            "no_relay_minters": rows("""
                SELECT count(*) AS pools, sum(stake_ada) AS stake_ada,
                       sum(delegators) AS delegators, sum(blocks_last_30_epochs) AS blocks
                FROM relay_pool_health
                WHERE minted_last_30_epochs AND registration_class = 'NO_REGISTERED_RELAY'""")[0],
            "history": rows("""
                SELECT direction, count(*) AS certs,
                       count(DISTINCT pool_bech32) AS pools
                FROM relay_registration_changes GROUP BY 1 ORDER BY 2 DESC"""),
            "removed_all": rows("""
                SELECT ticker, stake_ada, delegators, blocks_last_30_epochs AS blocks,
                       removed_all_relays_on, registration_class
                FROM relay_pool_health
                WHERE ever_removed_all_relays AND registration_class = 'NO_REGISTERED_RELAY'
                  AND minted_last_30_epochs
                ORDER BY stake_ada DESC NULLS LAST LIMIT 10"""),
            "removed_all_totals": rows("""
                SELECT count(*) FILTER (WHERE ever_removed_all_relays) AS ever,
                       count(*) FILTER (WHERE ever_removed_all_relays
                                        AND registration_class <> 'NO_REGISTERED_RELAY') AS re_added,
                       count(*) FILTER (WHERE ever_removed_all_relays
                                        AND registration_class = 'NO_REGISTERED_RELAY') AS still_none
                FROM relay_pool_health""")[0],
            "asn": rows("""
                SELECT asn, as_name, country, pools, stake_ada,
                       pools_single_asn, stake_single_asn
                FROM relay_asn_concentration
                ORDER BY stake_single_asn DESC NULLS LAST LIMIT 12"""),
            "asn_totals": rows("""
                SELECT count(*) AS asns, sum(stake_single_asn) AS stake_single_asn
                FROM relay_asn_concentration""")[0],
            "failures": rows("""
                SELECT failure, count(*) AS endpoints
                FROM relay_endpoint_status WHERE failure IS NOT NULL AND failure <> ''
                GROUP BY 1 ORDER BY 2 DESC"""),
        }
        (OUT / "relays.json").write_text(json.dumps(relay, indent=2, default=str))
        print(f"  relays.json: {relay['totals']['pools']} pools")

    print(f"done. families={len(fams)}, findings={len(findings)}, tables={n_tables}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Build the compact NIGHT provenance module from the full spend-flow export.

The full NIGHT graph (1.36M UTxO nodes, 718K txs, ~2.5M edges, ~2 GB) is a
release-tier artifact, not committed. This script distills it into small,
clone-and-ask `night_*` tables that answer the headline questions — supply
conservation, holder concentration, custody type, flow depth, timing — and a
value-ranked top-cut of current-holding UTxOs.

Source: the unzipped export dir, default data/release/night_full/, override with
NIGHT_SRC. Expected files (from the warehouse extraction SQL):
  35_night_mint_events_abcde.csv        36_night_root_utxo_abcde.csv
  37_night_reachable_utxo_nodes_abcde.csv  41_night_current_leaves_abcde.csv
  43_night_flow_summary_abcde.csv

Outputs -> data/small/night_*.csv (loaded into the compact DuckDB by the build).
Verifies supply conservation (current leaves must sum to the minted total) and
fails loudly if it does not.
"""
from __future__ import annotations

import os
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
SRC = Path(os.environ.get("NIGHT_SRC", ROOT / "data/release/night_full"))
SMALL = ROOT / "data/small"
MINTED_NIGHT = 24_000_000_000  # 24B NIGHT genesis mint (verified against mint event)
HOLDER_TOP = 2000              # top holding addresses kept in the compact cut
LEAF_TOP = 10000              # top current-leaf UTxOs kept in the compact cut


def f(name: str) -> str:
    p = SRC / name
    if not p.exists():
        raise SystemExit(f"missing NIGHT source {p} — unzip the export into {SRC} "
                         f"or set NIGHT_SRC")
    return str(p)


def main() -> None:
    con = duckdb.connect()
    leaves = f("41_night_current_leaves_abcde.csv")
    unodes = f("37_night_reachable_utxo_nodes_abcde.csv")

    con.execute(f"CREATE VIEW leaves AS SELECT * FROM read_csv_auto('{leaves}')")
    total_leaf = con.execute("SELECT sum(qty_night) FROM leaves").fetchone()[0]
    if abs(float(total_leaf) - MINTED_NIGHT) > 1:
        raise SystemExit(f"CONSERVATION FAILED: leaves sum {total_leaf} != {MINTED_NIGHT}")
    print(f"conservation OK: {float(total_leaf):,.0f} NIGHT at current leaves == mint")

    def copy(sql: str, out: str):
        con.execute(f"COPY ({sql}) TO '{SMALL / out}' (FORMAT CSV, HEADER)")
        n = con.execute(f"SELECT count(*) FROM ({sql})").fetchone()[0]
        print(f"  {out}: {n} rows")

    # 1. summary (passthrough of the export's verified metrics)
    copy(f"SELECT * FROM read_csv_auto('{f('43_night_flow_summary_abcde.csv')}')",
         "night_summary.csv")

    # 2. mint event + 3. root UTxO (single rows, the provenance anchor)
    copy(f"SELECT tx_hash, block_no, block_time_utc, quantity_night "
         f"FROM read_csv_auto('{f('35_night_mint_events_abcde.csv')}')", "night_mint_event.csv")
    copy(f"SELECT utxo_node_id, tx_hash, address, address_has_script, payment_cred_hex, "
         f"qty_night, block_no, block_time_utc "
         f"FROM read_csv_auto('{f('36_night_root_utxo_abcde.csv')}')", "night_root_utxo.csv")

    # per-address current holdings (materialize once)
    con.execute("""CREATE TABLE holders AS
        SELECT address, bool_or(address_has_script) AS has_script,
               sum(qty_night) AS qty_night, count(*) AS utxos
        FROM leaves GROUP BY address""")
    g = float(total_leaf)

    # 4. top holding addresses (compact cut) + pct of supply
    copy(f"SELECT address, has_script, round(qty_night,8) AS qty_night, utxos, "
         f"round(100.0*qty_night/{g},4) AS pct_of_supply "
         f"FROM holders ORDER BY qty_night DESC LIMIT {HOLDER_TOP}",
         "night_holder_top.csv")

    # 5. concentration curve: cumulative % held by the top-N addresses
    con.execute("""CREATE TABLE ranked AS
        SELECT qty_night, row_number() OVER (ORDER BY qty_night DESC) AS rnk FROM holders""")
    rows = [(n, con.execute(f"SELECT sum(qty_night) FROM ranked WHERE rnk<={n}").fetchone()[0])
            for n in (1, 5, 10, 25, 50, 100, 250, 500, 1000, 2000, 5000, 10000)]
    total_addr = con.execute("SELECT count(*) FROM holders").fetchone()[0]
    con.execute("CREATE TABLE conc(top_n BIGINT, cumulative_night DOUBLE, cumulative_pct DOUBLE)")
    for n, s in rows:
        con.execute("INSERT INTO conc VALUES (?,?,?)", [n, round(float(s), 6), round(100*float(s)/g, 4)])
    con.execute("INSERT INTO conc VALUES (?,?,?)", [total_addr, round(g, 6), 100.0])
    copy("SELECT * FROM conc ORDER BY top_n", "night_concentration_curve.csv")

    # 6. custody type split (script vs enterprise)
    copy(f"SELECT has_script, round(sum(qty_night),6) AS qty_night, count(*) AS addresses, "
         f"round(100.0*sum(qty_night)/{g},4) AS pct_of_supply "
         f"FROM holders GROUP BY has_script ORDER BY qty_night DESC",
         "night_holder_type_split.csv")

    # 7. flow-level distribution: how deep current holdings sit in the spend graph
    copy(f"SELECT flow_level, count(*) AS leaf_utxos, round(sum(qty_night),6) AS qty_night, "
         f"round(100.0*sum(qty_night)/{g},4) AS pct_of_supply "
         f"FROM leaves GROUP BY flow_level ORDER BY flow_level",
         "night_flow_level_dist.csv")

    # 8. current holdings by month (when value last landed)
    copy(f"SELECT strftime(block_time_utc, '%Y-%m') AS month, count(*) AS leaf_utxos, "
         f"round(sum(qty_night),6) AS qty_night "
         f"FROM leaves GROUP BY 1 ORDER BY 1", "night_leaves_by_month.csv")

    # 9. top current-leaf UTxOs (the queryable holder-UTxO table, top-cut)
    copy(f"SELECT utxo_node_id, address, address_has_script, round(qty_night,8) AS qty_night, "
         f"block_no, block_time_utc, flow_level "
         f"FROM leaves ORDER BY qty_night DESC LIMIT {LEAF_TOP}", "night_current_leaves_top.csv")

    print(f"done. {total_addr:,} holding addresses, {g:,.0f} NIGHT total.")


if __name__ == "__main__":
    main()

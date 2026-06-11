#!/usr/bin/env python3
"""Render a Genesis ADA confidence analytics report from published rollups."""
from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports/genesis_ada_confidence_analysis.md"


def fmt(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:,.6f}".rstrip("0").rstrip(".")
    if isinstance(value, Decimal):
        return f"{value:,.6f}".rstrip("0").rstrip(".")
    if isinstance(value, int):
        return f"{value:,}"
    text = str(value)
    if len(text) > 42 and (text.startswith("stake") or text.startswith("drep")):
        return f"`{text[:18]}...`"
    return text


def table(con: duckdb.DuckDBPyConnection, sql: str) -> list[str]:
    cur = con.execute(sql)
    rows = cur.fetchall()
    cols = [d[0] for d in cur.description]
    lines = [
        "| " + " | ".join(cols) + " |",
        "| " + " | ".join("---" for _ in cols) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(fmt(v) for v in row) + " |")
    return lines


def scalar(con: duckdb.DuckDBPyConnection, sql: str) -> object:
    return con.execute(sql).fetchone()[0]


def main() -> None:
    release_inputs = [
        "data/release/genesis_current_governance_surface.csv",
        "data/release/governance_genesis_behavior_signals_full.csv",
    ]
    missing = [p for p in release_inputs if not Path(p).exists()]
    if missing:
        raise SystemExit(
            "Missing release inputs (not committed to git):\n  "
            + "\n  ".join(missing)
            + "\nRebuild them with scripts/build_genesis_drep_behavior_surface_remote.sh "
            "or download the release assets (scripts/fetch_db.py)."
        )
    con = duckdb.connect()
    con.execute("CREATE OR REPLACE VIEW surface AS SELECT * FROM read_csv_auto('data/release/genesis_current_governance_surface.csv', union_by_name=true)")
    con.execute("CREATE OR REPLACE VIEW signals AS SELECT * FROM read_csv_auto('data/release/governance_genesis_behavior_signals_full.csv', union_by_name=true)")
    con.execute("CREATE OR REPLACE VIEW by_drep AS SELECT * FROM read_csv_auto('data/small/governance_genesis_behavior_by_drep.csv', union_by_name=true)")
    con.execute("CREATE OR REPLACE VIEW by_root_drep AS SELECT * FROM read_csv_auto('data/small/governance_genesis_behavior_by_root_drep.csv', union_by_name=true)")
    con.execute("CREATE OR REPLACE VIEW by_proposal AS SELECT * FROM read_csv_auto('data/small/governance_genesis_behavior_by_proposal.csv', union_by_name=true)")

    con.execute("""
        CREATE OR REPLACE VIEW dedup_current AS
        SELECT
          tx_id,
          tx_out_index,
          max(value_lovelace) AS value_lovelace,
          min(min_depth) AS min_depth,
          max(output_block_time_utc) AS output_block_time_utc,
          max(output_block_no) AS output_block_no,
          string_agg(DISTINCT root_seed_id, '+' ORDER BY root_seed_id) AS root_combo,
          max(stake_address_id) AS stake_address_id,
          max(stake_address) AS stake_address,
          max(latest_drep_id_bech32) AS latest_drep_id_bech32
        FROM surface
        GROUP BY tx_id, tx_out_index
    """)

    snapshot = scalar(con, "SELECT max(snapshot_utc) FROM surface")
    tip = scalar(con, "SELECT max(dbsync_tip_utc) FROM surface")
    epoch = scalar(con, "SELECT max(dbsync_tip_epoch) FROM surface")
    rows = scalar(con, "SELECT count(*) FROM surface")
    dedup_utxos = scalar(con, "SELECT count(*) FROM dedup_current")
    dedup_ada = scalar(con, "SELECT round(sum(value_lovelace)/1000000.0, 6) FROM dedup_current")
    staked_ada = scalar(con, "SELECT round(sum(current_lovelace)/1000000.0, 6) FROM signals")
    no_stake_ada = scalar(con, "SELECT round(sum(value_lovelace)/1000000.0, 6) FROM dedup_current WHERE stake_address_id IS NULL")
    delegated_ada = scalar(con, "SELECT round(sum(value_lovelace)/1000000.0, 6) FROM dedup_current WHERE latest_drep_id_bech32 IS NOT NULL")

    lines: list[str] = [
        "# Genesis ADA Confidence Analysis",
        "",
        "This report summarizes the founder depth-14 Genesis trace surface, confidence signals, DRep exposure, and proposal-alignment cuts.",
        "",
        "## Evidence boundary",
        "",
        "- FACT: trace membership, live-unspent status at db-sync tip, output creation time, latest DRep delegation, DRep votes, and deterministic confidence-score components.",
        "- INFERENCE: `weak_behavior_signal`, `coordinated_like`, `probable_retained_like`, and `high_confidence_retained_like` are audit-prioritization classes.",
        "- UNKNOWN: beneficial ownership, legal identity, custody, intent, or off-chain coordination.",
        "",
        "## Snapshot",
        "",
        f"- Surface snapshot UTC: `{snapshot}`",
        f"- db-sync tip UTC: `{tip}`",
        f"- db-sync tip epoch: `{epoch}`",
        f"- Trace rows: `{fmt(rows)}`",
        f"- Deduped current UTxOs: `{fmt(dedup_utxos)}`",
        f"- Deduped current ADA: `{fmt(dedup_ada)}`",
        f"- Stake-credential ADA in confidence signal table: `{fmt(staked_ada)}`",
        f"- No-stake / Byron ADA: `{fmt(no_stake_ada)}`",
        f"- Deduped current ADA with latest DRep delegation: `{fmt(delegated_ada)}`",
        "",
        "## Confidence Bands",
        "",
    ]
    lines += table(con, """
        SELECT
          confidence_class,
          count(*) AS clusters,
          round(sum(current_lovelace)/1000000.0, 6) AS current_ada,
          round(avg(behavior_score), 3) AS avg_score,
          max(behavior_score) AS max_score
        FROM signals
        GROUP BY confidence_class
        ORDER BY current_ada DESC
    """)

    lines += [
        "",
        "## Depth And Time",
        "",
        "Depth is UTxO-hop depth from the founder seed output. The rows below are current live-unspent outputs at db-sync tip.",
        "",
    ]
    lines += table(con, """
        SELECT
          min_depth,
          count(*) AS dedup_utxos,
          round(sum(value_lovelace)/1000000.0, 6) AS current_ada,
          min(output_block_time_utc) AS earliest_output_utc,
          max(output_block_time_utc) AS latest_output_utc,
          min(output_block_no) AS min_block,
          max(output_block_no) AS max_block
        FROM dedup_current
        GROUP BY min_depth
        ORDER BY min_depth
    """)

    lines += ["", "## Root And Overlap", ""]
    lines += table(con, """
        SELECT
          root_seed_id,
          count(*) AS trace_rows,
          count(DISTINCT (tx_id, tx_out_index)) AS current_utxos,
          round(sum(value_lovelace)/1000000.0, 6) AS root_trace_ada,
          count(DISTINCT stake_address_id) FILTER (WHERE stake_address_id IS NOT NULL) AS stake_credentials
        FROM surface
        GROUP BY root_seed_id
        ORDER BY root_trace_ada DESC
    """)
    lines += ["", "### Current UTxO Root Combos", ""]
    lines += table(con, """
        SELECT
          root_combo,
          count(*) AS dedup_utxos,
          round(sum(value_lovelace)/1000000.0, 6) AS current_ada
        FROM dedup_current
        GROUP BY root_combo
        ORDER BY current_ada DESC
    """)

    lines += ["", "## DRep Exposure By Confidence Class", ""]
    lines += table(con, """
        SELECT
          behavior_class,
          count(*) AS drep_rows,
          round(sum(dedup_current_lovelace)/1000000.0, 6) AS current_ada,
          sum(dedup_current_utxos) AS current_utxos
        FROM by_drep
        GROUP BY behavior_class
        ORDER BY current_ada DESC
    """)

    lines += ["", "### Top DRep Targets By Traced Current ADA", ""]
    lines += table(con, """
        SELECT
          latest_drep_id_bech32 AS drep,
          behavior_class,
          round(sum(dedup_current_lovelace)/1000000.0, 6) AS current_ada,
          sum(dedup_current_utxos) AS current_utxos,
          max(trace_value_to_drep_power_ratio) AS max_trace_to_power_ratio
        FROM by_drep
        GROUP BY latest_drep_id_bech32, behavior_class
        ORDER BY current_ada DESC
        LIMIT 25
    """)

    lines += ["", "### Top DRep Targets For Probable/High Retained-Like Signals", ""]
    lines += table(con, """
        SELECT
          latest_drep_id_bech32 AS drep,
          confidence_class,
          count(*) AS clusters,
          round(sum(current_lovelace)/1000000.0, 6) AS current_ada,
          max(behavior_score) AS max_score
        FROM signals
        WHERE confidence_class IN ('probable_retained_like', 'high_confidence_retained_like')
        GROUP BY latest_drep_id_bech32, confidence_class
        ORDER BY current_ada DESC
        LIMIT 20
    """)

    lines += ["", "## High-Value Clusters To Review", ""]
    lines += table(con, """
        SELECT
          confidence_class,
          behavior_score,
          behavior_flags,
          root_combo,
          current_ada,
          current_utxos,
          latest_drep_id_bech32 AS drep,
          stake_address
        FROM signals
        WHERE confidence_class IN ('coordinated_like', 'probable_retained_like', 'high_confidence_retained_like')
        ORDER BY current_lovelace DESC
        LIMIT 25
    """)

    lines += ["", "## Proposal Exposure", ""]
    lines += table(con, """
        SELECT
          behavior_class,
          vote,
          count(*) AS rows,
          round(sum(dedup_current_lovelace)/1000000.0, 6) AS current_ada
        FROM by_proposal
        GROUP BY behavior_class, vote
        ORDER BY current_ada DESC
    """)

    lines += ["", "### Top Proposals By Probable/High Retained-Like Exposure", ""]
    lines += table(con, """
        SELECT
          proposal_type,
          proposal_tx_hash,
          proposal_index,
          vote,
          behavior_class,
          round(sum(dedup_current_lovelace)/1000000.0, 6) AS current_ada,
          count(*) AS rows
        FROM by_proposal
        WHERE behavior_class IN ('probable_retained_like', 'high_confidence_retained_like')
        GROUP BY proposal_type, proposal_tx_hash, proposal_index, vote, behavior_class
        ORDER BY current_ada DESC
        LIMIT 25
    """)

    lines += ["", "## Root x DRep Concentration", ""]
    lines += table(con, """
        SELECT
          root_seed_id,
          latest_drep_id_bech32 AS drep,
          behavior_class,
          round(sum(current_lovelace)/1000000.0, 6) AS current_ada,
          sum(current_utxos) AS current_utxos
        FROM by_root_drep
        GROUP BY root_seed_id, latest_drep_id_bech32, behavior_class
        ORDER BY current_ada DESC
        LIMIT 30
    """)

    lines += [
        "",
        "## Interpretation",
        "",
        "- The largest current ADA buckets are still `trace_only` and `weak_behavior_signal`; they should not be used as influence claims.",
        "- `coordinated_like` is large enough to matter for prioritization, but it is still a behavior pattern, not ownership.",
        "- `probable_retained_like` and `high_confidence_retained_like` are small by ADA compared with the full trace surface, which is good: the stricter flags are not swallowing the whole graph.",
        "- Proposal exposure rows show where delegated DReps voted, not how the traced stake owners would have voted directly.",
        "",
        "## Next Audit Work",
        "",
        "1. Validate top high-confidence clusters manually with transaction-level receipts.",
        "2. Add known service/custodian labels where public evidence supports them.",
        "3. Compare the new confidence bands against the earlier IOG confidence-band cut.",
        "4. Regenerate top-DRep profile exposure from this scored surface instead of preserved legacy receipts.",
        "",
    ]

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {REPORT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

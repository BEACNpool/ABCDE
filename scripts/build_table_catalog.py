#!/usr/bin/env python3
"""Generate the table → family → finding → grade catalog.

This is the grounding layer for "clone it and let an AI query it": for every
table in the shipped DuckDB it answers *what is this, where did it come from,
which finding uses it, and at what evidence grade* — so an assistant can cite
provenance without guessing.

Inputs (all committed, no warehouse needed):
  - data/schema_catalog.json          (tables, row counts, source CSV)
  - data/small/data_freshness_catalog.csv (snapshot_sensitive flag)
  - findings/F*.md                    (title, grade, and Evidence file lists)

Outputs:
  - data/table_catalog.json           (machine-readable)
  - docs/TABLE_CATALOG.md             (human-readable)

Run after build_genesis_db.py (needs the schema catalog) and before the hash
indexes so the outputs are hashed. Deterministic and idempotent.
"""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "data/schema_catalog.json"
FRESH = ROOT / "data/small/data_freshness_catalog.csv"
FINDINGS_DIR = ROOT / "findings"
OUT_JSON = ROOT / "data/table_catalog.json"
OUT_MD = ROOT / "docs/TABLE_CATALOG.md"

# table-name prefix -> family label (longest prefix wins)
FAMILY = [
    ("seed", "Genesis seeds"),
    ("seeds", "Genesis seeds"),
    ("fourth_entry", "Fourth entry"),
    ("bounded_trace", "Traces"),
    ("staged_trace", "Traces"),
    ("staged_cross", "Traces"),
    ("cross_merge", "Traces"),
    ("legacy_cross_merge", "Traces"),
    ("trace_stake_credentials", "Traces"),
    ("iog_current_bag", "IOG current bag"),
    ("iog_pool_state", "IOG current bag"),
    ("governance_genesis_behavior", "Genesis→DRep behavior"),
    ("governance_genesis", "Genesis→DRep behavior"),
    ("governance_top_drep", "Governance rollups"),
    ("governance_spo", "Governance rollups"),
    ("governance_drep", "Governance rollups"),
    ("governance_pool", "Governance rollups"),
    ("governance_actions", "Governance rollups"),
    ("iogp", "IOGP / voucher"),
    ("iog_voucher", "IOGP / voucher"),
    ("voucher", "IOGP / voucher"),
    ("genesis_trail", "Genesis Trail"),
    ("genesis_control", "Control indicators"),
    ("fleet_control", "Control indicators"),
    ("component_control", "Control indicators"),
    ("f11_", "Reward-plumbing receipts"),
    ("f15_", "Reward-plumbing receipts"),
    ("f16_", "NIGHT token"),
    ("tracer_", "Exchange tracers"),
    ("emurgo_", "EMURGO DRep genesis"),
    ("secondfi_incident_", "SecondFi incident"),
    ("night_incident_", "NIGHT bridge incident"),
    ("night_", "NIGHT token"),
    ("build_info", "Meta"),
    ("db_tip_receipt", "Meta"),
    ("epoch_context", "Meta"),
    ("data_freshness_catalog", "Meta"),
]


def family_of(table: str) -> str:
    best = ("", "Other")
    for prefix, label in FAMILY:
        if table.startswith(prefix) and len(prefix) > len(best[0]):
            best = (prefix, label)
    return best[1]


def parse_findings() -> dict[str, list[dict]]:
    """table stem -> [{finding, title, grade}] from the finding markdown."""
    h1 = re.compile(r"^#\s+(F\d+\w*)\s+—\s+(.+)$")
    ev_csv = re.compile(r"data/small/([A-Za-z0-9_]+)\.csv")
    out: dict[str, list[dict]] = {}
    for md in sorted(FINDINGS_DIR.glob("F*.md")):
        text = md.read_text(encoding="utf-8")
        fid, title = md.stem.split("_")[0], ""
        m = h1.search(text.splitlines()[0]) if text else None
        if m:
            fid, title = m.group(1), m.group(2).strip()
        # grade line: first bullet under "## Grade"
        grade = ""
        gm = re.search(r"##\s+Grade\s*\n+(.+)", text)
        if gm:
            grade = re.sub(r"[*`\-]", "", gm.group(1)).strip()[:80]
        # evidence tables: CSV paths anywhere in the Evidence section
        em = re.search(r"##\s+Evidence(.+?)(?:\n##\s|\Z)", text, re.S)
        stems = set(ev_csv.findall(em.group(1))) if em else set()
        for stem in stems:
            out.setdefault(stem, []).append(
                {"finding": fid, "title": title, "grade_hint": grade}
            )
    return out


def main() -> None:
    schema = json.loads(SCHEMA.read_text())
    tables = schema["tables"]  # {name: {source,row_count,columns,...}}
    snapshot = {}
    if FRESH.exists():
        for r in csv.DictReader(FRESH.open()):
            snapshot[r["table_name"]] = r.get("snapshot_sensitive", "") in ("True", "true", "1")
    findings = parse_findings()

    rows = []
    for name in sorted(tables):
        info = tables[name]
        # map by the source CSV stem when present, else the table name
        src = (info.get("source") or "").split("/")[-1].replace(".csv", "")
        fk = findings.get(src) or findings.get(name) or []
        rows.append({
            "table": name,
            "family": family_of(name),
            "row_count": info.get("row_count"),
            "source": info.get("source"),
            "snapshot_sensitive": snapshot.get(name, False),
            "findings": sorted({f["finding"] for f in fk}),
            "grade": (fk[0]["grade_hint"] if fk else ""),
        })

    OUT_JSON.write_text(json.dumps(
        {"generated_from": "schema_catalog.json + findings/F*.md + data_freshness_catalog.csv",
         "table_count": len(rows), "tables": rows}, indent=2) + "\n")

    by_family: dict[str, list[dict]] = {}
    for r in rows:
        by_family.setdefault(r["family"], []).append(r)

    lines = [
        "# Table Catalog",
        "",
        "Auto-generated by `scripts/build_table_catalog.py` (run in "
        "`finalize_cut.sh`). One row per shipped table: its family, size, source, "
        "whether it is snapshot-sensitive, and which finding(s) it backs at what "
        "grade. Per-column detail is in [`SCHEMA.md`](SCHEMA.md).",
        "",
        "> **Snapshot-sensitive** tables describe *current* chain state and are "
        "only accurate as of the `build_info` tip. Non-sensitive tables are "
        "historical facts that do not decay. See "
        "[`22_DATA_TOPOLOGY_AND_FRESHNESS.md`](22_DATA_TOPOLOGY_AND_FRESHNESS.md).",
        "",
    ]
    for family in sorted(by_family):
        lines.append(f"## {family}")
        lines.append("")
        lines.append("| table | rows | snapshot? | finding(s) |")
        lines.append("|---|---:|:---:|---|")
        for r in sorted(by_family[family], key=lambda x: x["table"]):
            snap = "🕒" if r["snapshot_sensitive"] else "—"
            fnd = ", ".join(r["findings"]) if r["findings"] else ""
            lines.append(f"| `{r['table']}` | {r['row_count']:,} | {snap} | {fnd} |")
        lines.append("")
    OUT_MD.write_text("\n".join(lines))
    print(f"wrote {OUT_JSON.relative_to(ROOT)} and {OUT_MD.relative_to(ROOT)} "
          f"({len(rows)} tables)")


if __name__ == "__main__":
    main()

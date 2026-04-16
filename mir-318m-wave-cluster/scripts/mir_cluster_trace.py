#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import shlex
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

DEFAULT_HOST = "abcde@192.168.86.118"
DEFAULT_DB = "cexplorer_replica"
DEFAULT_MIN_ADA = 49000
DEFAULT_DEPTH = 2
DEFAULT_MAX_NEW_ENTITIES = 500
DEFAULT_LABEL_PATHS = [
    "/home/ubuntudesktop/Desktop/genesisADA/data/address_labels_full.csv",
    "/home/ubuntudesktop/Desktop/genesisADA/data/labels.csv",
]


def sql_literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def values_block(column: str, values: Sequence[str]) -> str:
    if not values:
        return f"select null::{column} where false"
    return "values\n" + ",\n".join(f"({sql_literal(v)})" for v in values)


def run_sql(host: str, db: str, sql: str) -> str:
    normalized = " ".join(line.strip() for line in sql.splitlines() if line.strip())
    remote = (
        f"sudo -u postgres psql -d {shlex.quote(db)} -P pager=off -F '\\t' -A -t -c {shlex.quote(normalized)}"
    )
    proc = subprocess.run(["ssh", host, remote], text=True, capture_output=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip())
    return proc.stdout


def parse_tsv(text: str, columns: Sequence[str]) -> List[dict]:
    rows: List[dict] = []
    for line in text.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) != len(columns):
            raise RuntimeError(
                f"TSV column mismatch: expected {len(columns)} columns {list(columns)}, got {len(parts)} values: {line!r}"
            )
        rows.append(dict(zip(columns, parts)))
    return rows


def load_lines(path: Path) -> List[str]:
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip() and not line.strip().startswith("#")]


def load_labels(paths: Sequence[str]) -> Dict[str, dict]:
    labels: Dict[str, dict] = {}
    for raw_path in paths:
        path = Path(raw_path)
        if not path.exists():
            continue
        with path.open(encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                addr = (row.get("address") or "").strip()
                if not addr:
                    continue
                if addr not in labels or (row.get("confidence") or "") == "high":
                    labels[addr] = row
    return labels


def fetch_hop(host: str, db: str, frontier_stakes: Sequence[str], frontier_addresses: Sequence[str], min_lovelace: int) -> List[dict]:
    if frontier_stakes:
        if len(frontier_stakes) != 1:
            raise RuntimeError("stake single-hop queries require exactly one frontier stake")
        frontier = frontier_stakes[0]
        sql = f"""
with frontier_id as materialized (
  select sa.id
  from stake_address sa
  where sa.view = {sql_literal(frontier)}
),
frontier_utxos as materialized (
  select
    txo.id,
    txo.tx_id,
    txo.index as tx_index,
    txo.value
  from tx_out txo
  where txo.stake_address_id = (select id from frontier_id)
    and txo.value >= {int(min_lovelace)}
),
spend_summary as materialized (
  select
    txi.tx_in_id as spend_tx_id,
    count(*) as frontier_input_count,
    sum(fu.value) as frontier_input_lovelace
  from frontier_utxos fu
  join tx_in txi on txi.tx_out_id = fu.id
  group by txi.tx_in_id
),
dests as materialized (
  select
    ss.spend_tx_id,
    ss.frontier_input_count,
    ss.frontier_input_lovelace,
    txo.index as dest_index,
    txo.address as dest_address,
    txo.value as dest_lovelace,
    sa.view as dest_stake_address,
    case
      when txo.stake_address_id = (select id from frontier_id) then 'internal_stake'
      when sa.view is not null then 'external_stake'
      else 'enterprise'
    end as dest_type
  from spend_summary ss
  join tx_out txo on txo.tx_id = ss.spend_tx_id
  left join stake_address sa on sa.id = txo.stake_address_id
),
shape as materialized (
  select
    spend_tx_id,
    count(*) as total_output_count,
    count(*) filter (where dest_type = 'internal_stake') as internal_output_count,
    count(*) filter (where dest_type = 'external_stake') as external_stake_output_count,
    count(*) filter (where dest_type = 'enterprise') as enterprise_output_count,
    coalesce(sum(dest_lovelace) filter (where dest_type = 'internal_stake'), 0) as internal_output_lovelace,
    coalesce(sum(dest_lovelace) filter (where dest_type = 'external_stake'), 0) as external_stake_output_lovelace,
    coalesce(sum(dest_lovelace) filter (where dest_type = 'enterprise'), 0) as enterprise_output_lovelace
  from dests
  group by spend_tx_id
)
select
  d.frontier_input_count,
  d.frontier_input_lovelace,
  d.spend_tx_id,
  d.dest_index,
  d.dest_type,
  d.dest_address,
  d.dest_stake_address,
  d.dest_lovelace,
  s.total_output_count,
  s.internal_output_count,
  s.external_stake_output_count,
  s.enterprise_output_count,
  s.internal_output_lovelace,
  s.external_stake_output_lovelace,
  s.enterprise_output_lovelace
from dests d
join shape s on s.spend_tx_id = d.spend_tx_id
where d.dest_type <> 'internal_stake'
  and d.dest_lovelace >= {int(min_lovelace)}
order by d.dest_lovelace desc, d.spend_tx_id, d.dest_index;
"""
    else:
        if len(frontier_addresses) != 1:
            raise RuntimeError("enterprise single-hop queries require exactly one frontier address")
        frontier = frontier_addresses[0]
        sql = f"""
with frontier_utxos as materialized (
  select
    txo.id,
    txo.tx_id,
    txo.index as tx_index,
    txo.value
  from tx_out txo
  where txo.address = {sql_literal(frontier)}
    and txo.value >= {int(min_lovelace)}
),
spend_summary as materialized (
  select
    txi.tx_in_id as spend_tx_id,
    count(*) as frontier_input_count,
    sum(fu.value) as frontier_input_lovelace
  from frontier_utxos fu
  join tx_in txi on txi.tx_out_id = fu.id
  group by txi.tx_in_id
),
dests as materialized (
  select
    ss.spend_tx_id,
    ss.frontier_input_count,
    ss.frontier_input_lovelace,
    txo.index as dest_index,
    txo.address as dest_address,
    txo.value as dest_lovelace,
    sa.view as dest_stake_address,
    case
      when txo.address = {sql_literal(frontier)} then 'internal_address'
      when sa.view is not null then 'external_stake'
      else 'enterprise'
    end as dest_type
  from spend_summary ss
  join tx_out txo on txo.tx_id = ss.spend_tx_id
  left join stake_address sa on sa.id = txo.stake_address_id
),
shape as materialized (
  select
    spend_tx_id,
    count(*) as total_output_count,
    count(*) filter (where dest_type = 'internal_address') as internal_output_count,
    count(*) filter (where dest_type = 'external_stake') as external_stake_output_count,
    count(*) filter (where dest_type = 'enterprise') as enterprise_output_count,
    coalesce(sum(dest_lovelace) filter (where dest_type = 'internal_address'), 0) as internal_output_lovelace,
    coalesce(sum(dest_lovelace) filter (where dest_type = 'external_stake'), 0) as external_stake_output_lovelace,
    coalesce(sum(dest_lovelace) filter (where dest_type = 'enterprise'), 0) as enterprise_output_lovelace
  from dests
  group by spend_tx_id
)
select
  d.frontier_input_count,
  d.frontier_input_lovelace,
  d.spend_tx_id,
  d.dest_index,
  d.dest_type,
  d.dest_address,
  d.dest_stake_address,
  d.dest_lovelace,
  s.total_output_count,
  s.internal_output_count,
  s.external_stake_output_count,
  s.enterprise_output_count,
  s.internal_output_lovelace,
  s.external_stake_output_lovelace,
  s.enterprise_output_lovelace
from dests d
join shape s on s.spend_tx_id = d.spend_tx_id
where d.dest_type <> 'internal_address'
  and d.dest_lovelace >= {int(min_lovelace)}
order by d.dest_lovelace desc, d.spend_tx_id, d.dest_index;
"""
    raw = run_sql(host, db, sql)
    rows = parse_tsv(raw, [
        'frontier_input_count',
        'frontier_input_lovelace',
        'spend_tx_id',
        'dest_index',
        'dest_type',
        'dest_address',
        'dest_stake_address',
        'dest_lovelace',
        'total_output_count',
        'internal_output_count',
        'external_stake_output_count',
        'enterprise_output_count',
        'internal_output_lovelace',
        'external_stake_output_lovelace',
        'enterprise_output_lovelace',
    ])
    tx_ids = sorted({row['spend_tx_id'] for row in rows if row.get('spend_tx_id')})
    tx_meta = fetch_tx_context(host, db, tx_ids)
    for row in rows:
        meta = tx_meta.get(row['spend_tx_id'], {})
        row['spend_tx_hash'] = meta.get('spend_tx_hash') or None
        row['epoch_no'] = meta.get('epoch_no') or None
        row['block_time'] = meta.get('block_time') or None
    return rows


def fetch_tx_context(host: str, db: str, tx_ids: Sequence[str]) -> Dict[str, dict]:
    if not tx_ids:
        return {}
    sql = f"""
with target(id) as materialized (
  {values_block('bigint', tx_ids)}
)
select
  t.id as spend_tx_id,
  encode(t.hash,'hex') as spend_tx_hash,
  b.epoch_no,
  b.time as block_time
from tx t
join block b on b.id = t.block_id
join target x on x.id = t.id
order by t.id;
"""
    rows = parse_tsv(run_sql(host, db, sql), [
        'spend_tx_id',
        'spend_tx_hash',
        'epoch_no',
        'block_time',
    ])
    return {row["spend_tx_id"]: row for row in rows}


def fetch_stake_status(host: str, db: str, stake_addresses: Sequence[str]) -> Dict[str, dict]:
    if not stake_addresses:
        return {}
    sql = f"""
with target(view) as materialized (
  {values_block('text', stake_addresses)}
),
latest_pool as materialized (
  select distinct on (d.addr_id)
    d.addr_id,
    d.pool_hash_id,
    d.active_epoch_no,
    d.tx_id,
    d.slot_no,
    d.cert_index
  from delegation d
  join stake_address sa on sa.id = d.addr_id
  join target t on t.view = sa.view
  order by d.addr_id, d.active_epoch_no desc, d.slot_no desc, d.tx_id desc, d.cert_index desc
),
latest_vote as materialized (
  select distinct on (dv.addr_id)
    dv.addr_id,
    dv.drep_hash_id,
    tx.block_id,
    dv.tx_id,
    dv.cert_index
  from delegation_vote dv
  join tx on tx.id = dv.tx_id
  join stake_address sa on sa.id = dv.addr_id
  join target t on t.view = sa.view
  order by dv.addr_id, tx.block_id desc, dv.tx_id desc, dv.cert_index desc
)
select
  sa.view as stake_address,
  ph.view as pool_view,
  lp.active_epoch_no as pool_epoch_no,
  dh.view as drep_view
from target t
join stake_address sa on sa.view = t.view
left join latest_pool lp on lp.addr_id = sa.id
left join pool_hash ph on ph.id = lp.pool_hash_id
left join latest_vote lv on lv.addr_id = sa.id
left join drep_hash dh on dh.id = lv.drep_hash_id
order by sa.view;
"""
    rows = parse_tsv(run_sql(host, db, sql), [
        'stake_address',
        'pool_view',
        'pool_epoch_no',
        'drep_view',
    ])
    return {row["stake_address"]: row for row in rows}


def classify_label(labels: Dict[str, dict], stake_address: str | None, address: str | None) -> dict:
    for key in [stake_address, address]:
        if key and key in labels:
            row = labels[key]
            return {
                "label": row.get("label") or None,
                "label_category": row.get("category") or None,
                "label_confidence": row.get("confidence") or None,
                "label_source": row.get("source") or None,
            }
    return {"label": None, "label_category": None, "label_confidence": None, "label_source": None}


def as_int(row: dict, key: str) -> int:
    v = row.get(key)
    return int(v) if v not in (None, "") else 0


def write_csv(path: Path, rows: List[dict]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, obj) -> None:
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Trace high-value exits from a stake-cluster across stake and enterprise destinations.")
    ap.add_argument("--stake-file", help="Text file with one stake address per line")
    ap.add_argument("--frontier", help="Single frontier value, either a stake address or an enterprise/payment address")
    ap.add_argument("--host", default=DEFAULT_HOST)
    ap.add_argument("--db", default=DEFAULT_DB)
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--min-ada", type=int, default=DEFAULT_MIN_ADA)
    ap.add_argument("--depth", type=int, default=DEFAULT_DEPTH)
    ap.add_argument("--max-new-entities", type=int, default=DEFAULT_MAX_NEW_ENTITIES)
    ap.add_argument("--no-follow-enterprise", action="store_true")
    ap.add_argument("--no-follow-external-stake", action="store_true")
    ap.add_argument("--single-hop", action="store_true", help="Trace exactly one hop from the provided frontier set, with no recursive expansion")
    args = ap.parse_args()

    if not args.stake_file and not args.frontier:
        print("must provide --stake-file or --frontier", file=sys.stderr)
        return 2
    if args.stake_file and args.frontier:
        print("provide only one of --stake-file or --frontier", file=sys.stderr)
        return 2

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    input_frontier = args.frontier.strip() if args.frontier else None
    initial_seed_stakes: List[str] = []
    frontier_stakes: List[str] = []
    frontier_addresses: List[str] = []
    if args.frontier:
        frontier = args.frontier.strip()
        if frontier.startswith("stake1"):
            frontier_stakes = [frontier]
        else:
            frontier_addresses = [frontier]
    else:
        initial_seed_stakes = load_lines(Path(args.stake_file))
        if not initial_seed_stakes:
            print("stake-file was empty", file=sys.stderr)
            return 2
        frontier_stakes = list(initial_seed_stakes)

    labels = load_labels(DEFAULT_LABEL_PATHS)
    min_lovelace = args.min_ada * 1_000_000

    visited_stakes = set(frontier_stakes)
    visited_addresses: set[str] = set(frontier_addresses)
    all_rows: List[dict] = []
    truncated_steps: List[dict] = []

    max_depth = 1 if args.single_hop else args.depth
    for depth in range(1, max_depth + 1):
        if not frontier_stakes and not frontier_addresses:
            break

        hop_rows = fetch_hop(args.host, args.db, frontier_stakes, frontier_addresses, min_lovelace)
        enriched = []
        new_stakes: Dict[str, int] = defaultdict(int)
        new_addresses: Dict[str, int] = defaultdict(int)

        for row in hop_rows:
            row = dict(row)
            row["depth"] = depth
            row["frontier_kind"] = "stake" if frontier_stakes else "enterprise"
            row["frontier"] = frontier_stakes[0] if frontier_stakes else frontier_addresses[0]
            for key in [
                "frontier_input_count", "frontier_input_lovelace", "dest_index", "dest_lovelace",
                "total_output_count", "internal_output_count", "external_stake_output_count", "enterprise_output_count",
                "internal_output_lovelace", "external_stake_output_lovelace", "enterprise_output_lovelace",
            ]:
                row[key] = as_int(row, key)
            row["dest_ada"] = row["dest_lovelace"] / 1_000_000
            row["frontier_input_ada"] = row["frontier_input_lovelace"] / 1_000_000
            row["covert_pattern_hint"] = ", ".join(x for x in [
                "fanout" if row["total_output_count"] >= 10 else "",
                "has_internal_change" if row["internal_output_count"] > 0 else "",
                "enterprise_exit" if row["dest_type"] == "enterprise" else "",
                "fresh_stake_exit" if row["dest_type"] == "external_stake" else "",
            ] if x) or None
            row.update(classify_label(labels, row.get("dest_stake_address"), row.get("dest_address")))
            if row.get("label_category") == "CEX":
                row["destination_assessment"] = "likely_exchange_or_custody"
            elif row["dest_type"] == "external_stake":
                row["destination_assessment"] = "tracked_stake_destination"
            elif row["dest_type"] == "enterprise":
                row["destination_assessment"] = "enterprise_destination_unlabeled"
            else:
                row["destination_assessment"] = "other"
            enriched.append(row)

            if row["dest_type"] == "external_stake" and not args.no_follow_external_stake and row.get("dest_stake_address"):
                dest = row["dest_stake_address"]
                if dest not in visited_stakes:
                    new_stakes[dest] += row["dest_lovelace"]
            if row["dest_type"] == "enterprise" and not args.no_follow_enterprise and row.get("dest_address"):
                dest = row["dest_address"]
                if dest not in visited_addresses:
                    new_addresses[dest] += row["dest_lovelace"]

        all_rows.extend(enriched)

        next_stakes = [k for k, _ in sorted(new_stakes.items(), key=lambda kv: (-kv[1], kv[0]))]
        next_addresses = [k for k, _ in sorted(new_addresses.items(), key=lambda kv: (-kv[1], kv[0]))]
        if len(next_stakes) > args.max_new_entities:
            truncated_steps.append({
                "depth": depth,
                "entity_type": "stake",
                "kept": args.max_new_entities,
                "discarded": len(next_stakes) - args.max_new_entities,
            })
            next_stakes = next_stakes[: args.max_new_entities]
        if len(next_addresses) > args.max_new_entities:
            truncated_steps.append({
                "depth": depth,
                "entity_type": "enterprise_address",
                "kept": args.max_new_entities,
                "discarded": len(next_addresses) - args.max_new_entities,
            })
            next_addresses = next_addresses[: args.max_new_entities]

        visited_stakes.update(next_stakes)
        visited_addresses.update(next_addresses)
        frontier_stakes = next_stakes
        frontier_addresses = next_addresses

    unique_exit_stakes = sorted({row["dest_stake_address"] for row in all_rows if row.get("dest_stake_address")})
    stake_status = fetch_stake_status(args.host, args.db, unique_exit_stakes)
    for row in all_rows:
        status = stake_status.get(row.get("dest_stake_address") or "", {})
        row["current_pool_view"] = status.get("pool_view") or None
        row["current_pool_epoch_no"] = int(status["pool_epoch_no"]) if status.get("pool_epoch_no") else None
        row["current_drep_view"] = status.get("drep_view") or None

    all_rows.sort(key=lambda r: (-int(r["dest_lovelace"]), int(r["depth"]), r["spend_tx_hash"], int(r["dest_index"])))

    by_assessment = defaultdict(lambda: {"count": 0, "lovelace": 0})
    by_pool = defaultdict(lambda: {"count": 0, "lovelace": 0})
    by_drep = defaultdict(lambda: {"count": 0, "lovelace": 0})
    by_label = defaultdict(lambda: {"count": 0, "lovelace": 0})
    for row in all_rows:
        val = int(row["dest_lovelace"])
        by_assessment[row["destination_assessment"]]["count"] += 1
        by_assessment[row["destination_assessment"]]["lovelace"] += val
        if row.get("current_pool_view"):
            by_pool[row["current_pool_view"]]["count"] += 1
            by_pool[row["current_pool_view"]]["lovelace"] += val
        if row.get("current_drep_view"):
            by_drep[row["current_drep_view"]]["count"] += 1
            by_drep[row["current_drep_view"]]["lovelace"] += val
        if row.get("label"):
            by_label[row["label"]]["count"] += 1
            by_label[row["label"]]["lovelace"] += val

    summary = {
        "seed_stake_addresses": initial_seed_stakes,
        "input_frontier": input_frontier,
        "input_stake_file": args.stake_file,
        "host": args.host,
        "db": args.db,
        "min_ada": args.min_ada,
        "depth": 1 if args.single_hop else args.depth,
        "single_hop": args.single_hop,
        "rows": len(all_rows),
        "unique_exit_stake_addresses": len(unique_exit_stakes),
        "unique_labeled_destinations": len(by_label),
        "tracked_destination_ada": sum(int(r["dest_lovelace"]) for r in all_rows) / 1_000_000,
        "truncated_steps": truncated_steps,
        "assessment_summary": [
            {"destination_assessment": k, **v, "ada": v["lovelace"] / 1_000_000}
            for k, v in sorted(by_assessment.items(), key=lambda kv: (-kv[1]["lovelace"], kv[0]))
        ],
        "top_current_pools": [
            {"pool_view": k, **v, "ada": v["lovelace"] / 1_000_000}
            for k, v in sorted(by_pool.items(), key=lambda kv: (-kv[1]["lovelace"], kv[0]))[:25]
        ],
        "top_current_dreps": [
            {"drep_view": k, **v, "ada": v["lovelace"] / 1_000_000}
            for k, v in sorted(by_drep.items(), key=lambda kv: (-kv[1]["lovelace"], kv[0]))[:25]
        ],
        "top_labels": [
            {"label": k, **v, "ada": v["lovelace"] / 1_000_000}
            for k, v in sorted(by_label.items(), key=lambda kv: (-kv[1]["lovelace"], kv[0]))[:25]
        ],
        "notes": [
            "This is a stake-cluster / enterprise-address boundary tracer, not a mathematically perfect reserve-to-final-owner proof engine.",
            "It is designed to keep tracing large exits even when funds are split across fresh stake credentials or enterprise addresses.",
            "Exact attribution weakens when funds merge with unrelated inputs in later transactions, especially after withdrawals/rewards mix into the same wallet activity.",
            "Use the highest-confidence rows first: large exits, labeled CEX/custody destinations, and fresh stake exits with current pool/DRep state resolved.",
        ],
    }

    write_json(output_dir / "trace_summary.json", summary)
    write_json(output_dir / "trace_rows.json", all_rows)
    write_csv(output_dir / "trace_rows.csv", all_rows)

    md = []
    md.append("# MIR cluster trace report\n")
    if input_frontier:
        md.append(f"- input frontier: **`{input_frontier}`**")
    elif args.stake_file:
        md.append(f"- seed stake addresses: **{len(initial_seed_stakes)}**")
    md.append(f"- min tracked exit: **{args.min_ada:,} ADA**")
    md.append(f"- depth attempted: **{1 if args.single_hop else args.depth}**")
    md.append(f"- exit rows captured: **{len(all_rows)}**")
    md.append(f"- unique exit stake addresses: **{len(unique_exit_stakes)}**")
    md.append(f"- total tracked destination ADA (not de-overlapped): **{summary['tracked_destination_ada']:,.6f}**")
    md.append("")
    md.append("## Assessment summary\n")
    if summary["assessment_summary"]:
        for row in summary["assessment_summary"]:
            md.append(f"- `{row['destination_assessment']}` — {row['ada']:,.6f} ADA across {row['count']} rows")
    else:
        md.append("- no rows met the threshold")
    md.append("")
    md.append("## Top current pools\n")
    if summary["top_current_pools"]:
        for row in summary["top_current_pools"][:15]:
            md.append(f"- `{row['pool_view']}` — {row['ada']:,.6f} ADA across {row['count']} rows")
    else:
        md.append("- none resolved")
    md.append("")
    md.append("## Top current DReps\n")
    if summary["top_current_dreps"]:
        for row in summary["top_current_dreps"][:15]:
            md.append(f"- `{row['drep_view']}` — {row['ada']:,.6f} ADA across {row['count']} rows")
    else:
        md.append("- none resolved")
    md.append("")
    md.append("## Top labeled destinations\n")
    if summary["top_labels"]:
        for row in summary["top_labels"][:15]:
            md.append(f"- `{row['label']}` — {row['ada']:,.6f} ADA across {row['count']} rows")
    else:
        md.append("- none labeled yet")
    md.append("")
    md.append("## Notes\n")
    for note in summary["notes"]:
        md.append(f"- {note}")
    if truncated_steps:
        md.append("")
        md.append("## Frontier truncation\n")
        for row in truncated_steps:
            md.append(f"- depth {row['depth']} {row['entity_type']}: kept {row['kept']}, discarded {row['discarded']}")
    (output_dir / "trace_report.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    print(json.dumps({
        "output_dir": str(output_dir),
        "rows": len(all_rows),
        "tracked_destination_ada": summary["tracked_destination_ada"],
        "top_labels": summary["top_labels"][:10],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

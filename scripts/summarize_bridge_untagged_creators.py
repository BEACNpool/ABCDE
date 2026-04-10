#!/usr/bin/env python3
"""
summarize_bridge_untagged_creators.py

Build an address-cluster summary for bridge creator feeder rows whose creator
transactions are entirely seedless (`seed_labels == none` on every feeder row).

Inputs:
  - outputs/cross_entity_evidence/bridge_creator_feeders_tagged_2026-04-08.csv
  - datasets/genesis-founders/exchange-analysis/*_current_unspent_categorized.csv

Output:
  - outputs/cross_entity_evidence/bridge_untagged_creator_address_clusters_2026-04-08.csv
"""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent

TAGGED_CSV = REPO_ROOT / "outputs" / "cross_entity_evidence" / "bridge_creator_feeders_tagged_2026-04-08.csv"
SUMMARY_CSV = REPO_ROOT / "outputs" / "cross_entity_evidence" / "bridge_creator_summary_result_c_2026-04-08.csv"
EXCHANGE_DIR = REPO_ROOT / "datasets" / "genesis-founders" / "exchange-analysis"
OUTPUT_CSV = REPO_ROOT / "outputs" / "cross_entity_evidence" / "bridge_untagged_creator_address_clusters_2026-04-08.csv"
TOP_UNION_CSV = REPO_ROOT / "outputs" / "cross_entity_evidence" / "bridge_untagged_creator_top_exchange_union_2026-04-08.csv"
EXCHANGE_LIKE_UNION_CSV = REPO_ROOT / "outputs" / "cross_entity_evidence" / "bridge_untagged_creator_exchange_like_union_2026-04-08.csv"
RESIDUAL_CREATORS_CSV = REPO_ROOT / "outputs" / "cross_entity_evidence" / "bridge_untagged_residual_creators_2026-04-08.csv"
RESIDUAL_LARGE_BATCH_CSV = REPO_ROOT / "outputs" / "cross_entity_evidence" / "bridge_untagged_residual_large_batch_cluster_2026-04-08.csv"

TOP_CLUSTER_ADDRS = [
    "Ae2tdPwUPEZJCGuAQyPGCMUXS4XH9DZdH5sfPPruHi6WRtmKAw79bH25nF6",
    "Ae2tdPwUPEZ3144Xnww5Et54apKUr9go5s3pL9SUdAU4E5igRZPj1Gfa66o",
]


def load_creator_rows(path: Path) -> dict[str, list[dict[str, str]]]:
    creator_rows: dict[str, list[dict[str, str]]] = defaultdict(list)
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            creator_rows[row["creator_tx_hash"]].append(row)
    return creator_rows


def build_untagged_summary(
    creator_rows: dict[str, list[dict[str, str]]],
) -> dict[str, dict[str, object]]:
    summary: dict[str, dict[str, object]] = defaultdict(
        lambda: {"creators": set(), "total_ada": 0.0, "epochs": []}
    )

    for creator, rows in creator_rows.items():
        if not all(row["seed_labels"] == "none" for row in rows):
            continue
        for row in rows:
            addr = row["feeder_address"]
            summary[addr]["creators"].add(creator)
            summary[addr]["total_ada"] += float(row["feeder_ada"] or 0)
            summary[addr]["epochs"].append(int(row["creator_epoch"]))

    return summary


def load_exchange_hits(addresses: set[str]) -> dict[str, dict[str, set[str]]]:
    hits: dict[str, dict[str, set[str]]] = defaultdict(
        lambda: {"entities": set(), "likelihoods": set(), "categories": set()}
    )

    for csv_path in EXCHANGE_DIR.glob("*_current_unspent_categorized.csv"):
        with csv_path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                addr = row.get("dest_address", "")
                if addr not in addresses:
                    continue
                hits[addr]["entities"].add(row.get("seed", ""))
                hits[addr]["likelihoods"].add(row.get("exchange_likelihood", ""))
                hits[addr]["categories"].add(row.get("final_category", ""))

    return hits


def load_creator_summary(path: Path) -> dict[str, dict[str, str]]:
    rows: dict[str, dict[str, str]] = {}
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows[row["creator_tx_hash"]] = row
    return rows


def write_summary(
    path: Path,
    summary: dict[str, dict[str, object]],
    exchange_hits: dict[str, dict[str, set[str]]],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for addr, stats in summary.items():
        rows.append(
            {
                "feeder_address": addr,
                "untagged_creator_count": len(stats["creators"]),
                "total_feeder_ada": f"{stats['total_ada']:.6f}",
                "first_creator_epoch": min(stats["epochs"]),
                "last_creator_epoch": max(stats["epochs"]),
                "exchange_entities": "|".join(sorted(x for x in exchange_hits[addr]["entities"] if x)),
                "exchange_likelihoods": "|".join(
                    sorted(x for x in exchange_hits[addr]["likelihoods"] if x)
                ),
                "exchange_categories": "|".join(
                    sorted(x for x in exchange_hits[addr]["categories"] if x)
                ),
            }
        )

    rows.sort(
        key=lambda row: (
            -int(row["untagged_creator_count"]),
            -float(row["total_feeder_ada"]),
            row["feeder_address"],
        )
    )

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    return rows


def write_top_union(
    path: Path,
    creator_rows: dict[str, list[dict[str, str]]],
    creator_summary: dict[str, dict[str, str]],
) -> None:
    union_rows: list[dict[str, object]] = []

    for creator, rows in creator_rows.items():
        if not all(row["seed_labels"] == "none" for row in rows):
            continue
        feeder_addrs = {row["feeder_address"] for row in rows}
        if not feeder_addrs.intersection(TOP_CLUSTER_ADDRS):
            continue

        summary = creator_summary[creator]
        union_rows.append(
            {
                "creator_tx_hash": creator,
                "creator_epoch": summary["creator_epoch"],
                "creator_time_utc": summary["creator_time_utc"],
                "total_to_bridge_ada": summary["total_to_bridge_ada"],
                "bridge_outputs_created": summary["bridge_outputs_created"],
                "has_addr_jcgu": "1" if TOP_CLUSTER_ADDRS[0] in feeder_addrs else "0",
                "has_addr_3144": "1" if TOP_CLUSTER_ADDRS[1] in feeder_addrs else "0",
                "distinct_feeder_addresses": len(feeder_addrs),
            }
        )

    union_rows.sort(
        key=lambda row: (
            int(row["creator_epoch"]),
            row["creator_time_utc"],
            row["creator_tx_hash"],
        )
    )

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(union_rows[0].keys()))
        writer.writeheader()
        writer.writerows(union_rows)


def write_exchange_like_union(
    path: Path,
    creator_rows: dict[str, list[dict[str, str]]],
    creator_summary: dict[str, dict[str, str]],
    exchange_hits: dict[str, dict[str, set[str]]],
) -> None:
    exchange_like_addrs = {
        addr
        for addr, hit in exchange_hits.items()
        if any(label and label != "NOT_EXCHANGE" and "EXCHANGE" in label for label in hit["likelihoods"])
    }

    union_rows: list[dict[str, object]] = []
    for creator, rows in creator_rows.items():
        if not all(row["seed_labels"] == "none" for row in rows):
            continue
        feeder_addrs = {row["feeder_address"] for row in rows}
        matching = sorted(feeder_addrs.intersection(exchange_like_addrs))
        if not matching:
            continue

        summary = creator_summary[creator]
        union_rows.append(
            {
                "creator_tx_hash": creator,
                "creator_epoch": summary["creator_epoch"],
                "creator_time_utc": summary["creator_time_utc"],
                "total_to_bridge_ada": summary["total_to_bridge_ada"],
                "bridge_outputs_created": summary["bridge_outputs_created"],
                "matching_exchange_like_feeders": "|".join(matching),
                "matching_feeder_count": len(matching),
            }
        )

    union_rows.sort(
        key=lambda row: (
            int(row["creator_epoch"]),
            row["creator_time_utc"],
            row["creator_tx_hash"],
        )
    )

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(union_rows[0].keys()))
        writer.writeheader()
        writer.writerows(union_rows)


def bucket_for_creator(total_to_bridge_ada: float, distinct_feeders: int) -> str:
    if distinct_feeders >= 30:
        return "large_multi_30plus"
    if distinct_feeders >= 8:
        return "mid_multi_8_13"
    if distinct_feeders >= 2:
        return "small_multi_2_6"
    if total_to_bridge_ada < 10000:
        return "single_feeder_lt10k"
    return "single_feeder"


def write_residual_outputs(
    residual_csv: Path,
    residual_large_csv: Path,
    creator_rows: dict[str, list[dict[str, str]]],
    creator_summary: dict[str, dict[str, str]],
    exchange_hits: dict[str, dict[str, set[str]]],
) -> tuple[int, int]:
    exchange_like_addrs = {
        addr
        for addr, hit in exchange_hits.items()
        if any(label and label != "NOT_EXCHANGE" and "EXCHANGE" in label for label in hit["likelihoods"])
    }

    residual_rows: list[dict[str, object]] = []
    large_rows: list[dict[str, object]] = []

    for creator, rows in creator_rows.items():
        if not all(row["seed_labels"] == "none" for row in rows):
            continue
        feeder_addrs = sorted({row["feeder_address"] for row in rows})
        if set(feeder_addrs).intersection(exchange_like_addrs):
            continue

        summary = creator_summary[creator]
        total_to_bridge_ada = float(summary["total_to_bridge_ada"])
        distinct_feeders = len(feeder_addrs)
        row = {
            "creator_tx_hash": creator,
            "creator_epoch": summary["creator_epoch"],
            "creator_time_utc": summary["creator_time_utc"],
            "total_to_bridge_ada": summary["total_to_bridge_ada"],
            "bridge_outputs_created": summary["bridge_outputs_created"],
            "distinct_feeder_addresses": distinct_feeders,
            "residual_bucket": bucket_for_creator(total_to_bridge_ada, distinct_feeders),
            "sample_feeders": "|".join(feeder_addrs[:5]),
        }
        residual_rows.append(row)
        if distinct_feeders >= 30:
            large_rows.append(row)

    residual_rows.sort(
        key=lambda row: (
            int(row["creator_epoch"]),
            row["creator_time_utc"],
            row["creator_tx_hash"],
        )
    )
    large_rows.sort(
        key=lambda row: (
            int(row["creator_epoch"]),
            row["creator_time_utc"],
            row["creator_tx_hash"],
        )
    )

    with residual_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(residual_rows[0].keys()))
        writer.writeheader()
        writer.writerows(residual_rows)

    with residual_large_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(large_rows[0].keys()))
        writer.writeheader()
        writer.writerows(large_rows)

    return len(residual_rows), len(large_rows)


def main() -> None:
    if not TAGGED_CSV.exists():
        raise SystemExit(f"Missing tagged bridge feeder CSV: {TAGGED_CSV}")
    if not SUMMARY_CSV.exists():
        raise SystemExit(f"Missing bridge creator summary CSV: {SUMMARY_CSV}")

    creator_rows = load_creator_rows(TAGGED_CSV)
    summary = build_untagged_summary(creator_rows)
    exchange_hits = load_exchange_hits(set(summary.keys()))
    creator_summary = load_creator_summary(SUMMARY_CSV)
    rows = write_summary(OUTPUT_CSV, summary, exchange_hits)
    write_top_union(TOP_UNION_CSV, creator_rows, creator_summary)
    write_exchange_like_union(EXCHANGE_LIKE_UNION_CSV, creator_rows, creator_summary, exchange_hits)
    residual_count, residual_large_count = write_residual_outputs(
        RESIDUAL_CREATORS_CSV,
        RESIDUAL_LARGE_BATCH_CSV,
        creator_rows,
        creator_summary,
        exchange_hits,
    )

    print(f"Wrote {len(rows)} rows to {OUTPUT_CSV}")
    print(f"Wrote top-cluster union rows to {TOP_UNION_CSV}")
    print(f"Wrote exchange-like union rows to {EXCHANGE_LIKE_UNION_CSV}")
    print(f"Wrote {residual_count} residual creator rows to {RESIDUAL_CREATORS_CSV}")
    print(f"Wrote {residual_large_count} large residual batch rows to {RESIDUAL_LARGE_BATCH_CSV}")
    print("Top 10 feeder clusters:")
    for row in rows[:10]:
        print(row)


if __name__ == "__main__":
    main()

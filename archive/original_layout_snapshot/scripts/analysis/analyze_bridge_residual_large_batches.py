#!/usr/bin/env python3
"""
analyze_bridge_residual_large_batches.py

Profile the 12 late residual bridge creator transactions that sit outside the
current exchange-like screen. Produces:

  - per-creator batch-pattern metrics
  - feeder addresses reused across creators
  - exact feeder values reused across creators
"""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent

LARGE_CLUSTER_CSV = (
    REPO_ROOT
    / "outputs"
    / "cross_entity_evidence"
    / "bridge_untagged_residual_large_batch_cluster_2026-04-08.csv"
)
TAGGED_FEEDERS_CSV = (
    REPO_ROOT
    / "outputs"
    / "cross_entity_evidence"
    / "bridge_creator_feeders_tagged_2026-04-08.csv"
)
CREATOR_SUMMARY_CSV = (
    REPO_ROOT
    / "outputs"
    / "cross_entity_evidence"
    / "bridge_creator_summary_result_c_2026-04-08.csv"
)

PATTERN_CSV = (
    REPO_ROOT
    / "outputs"
    / "cross_entity_evidence"
    / "bridge_residual_large_batch_patterns_2026-04-08.csv"
)
SHARED_ADDRS_CSV = (
    REPO_ROOT
    / "outputs"
    / "cross_entity_evidence"
    / "bridge_residual_large_batch_shared_addresses_2026-04-08.csv"
)
RECURRING_VALUES_CSV = (
    REPO_ROOT
    / "outputs"
    / "cross_entity_evidence"
    / "bridge_residual_large_batch_recurring_values_2026-04-08.csv"
)

VALUE_TARGETS = [10.0, 100.0, 1000.0, 5000.0]


def load_large_cluster() -> list[dict[str, str]]:
    with LARGE_CLUSTER_CSV.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_tagged_rows(creator_hashes: set[str]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    with TAGGED_FEEDERS_CSV.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["creator_tx_hash"] in creator_hashes:
                rows.append(row)
    return rows


def load_creator_summary(creator_hashes: set[str]) -> dict[str, dict[str, str]]:
    summary: dict[str, dict[str, str]] = {}
    with CREATOR_SUMMARY_CSV.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["creator_tx_hash"] in creator_hashes:
                summary[row["creator_tx_hash"]] = row
    return summary


def format_float(value: float) -> str:
    return f"{value:.6f}"


def write_pattern_csv(
    large_cluster: list[dict[str, str]],
    tagged_rows: list[dict[str, str]],
    creator_summary: dict[str, dict[str, str]],
) -> None:
    by_creator: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in tagged_rows:
        by_creator[row["creator_tx_hash"]].append(row)

    output_rows: list[dict[str, object]] = []
    for cluster_row in large_cluster:
        creator = cluster_row["creator_tx_hash"]
        rows = by_creator[creator]
        values = sorted((float(row["feeder_ada"]) for row in rows), reverse=True)

        total_input_ada = float(creator_summary[creator]["creator_total_input_lovelace"]) / 1_000_000
        total_to_bridge_ada = float(creator_summary[creator]["total_to_bridge_ada"])
        fee_ada = total_input_ada - total_to_bridge_ada

        top1 = values[0]
        top5 = sum(values[:5])
        top10 = sum(values[:10])

        row = {
            "creator_tx_hash": creator,
            "creator_epoch": cluster_row["creator_epoch"],
            "creator_time_utc": cluster_row["creator_time_utc"],
            "input_count": len(rows),
            "total_to_bridge_ada": format_float(total_to_bridge_ada),
            "creator_total_input_ada": format_float(total_input_ada),
            "fee_ada": format_float(fee_ada),
            "fee_bps": f"{(fee_ada / total_input_ada) * 10000:.3f}",
            "top1_input_ada": format_float(top1),
            "top1_pct": f"{(top1 / total_input_ada) * 100:.2f}",
            "top5_pct": f"{(top5 / total_input_ada) * 100:.2f}",
            "top10_pct": f"{(top10 / total_input_ada) * 100:.2f}",
            "lt_100_count": sum(1 for value in values if value < 100),
            "lt_1000_count": sum(1 for value in values if value < 1000),
            "lt_10000_count": sum(1 for value in values if value < 10000),
            "between_10k_100k_count": sum(1 for value in values if 10000 <= value < 100000),
            "gte_100k_count": sum(1 for value in values if value >= 100000),
        }
        for target in VALUE_TARGETS:
            row[f"exact_{int(target)}_count"] = sum(1 for value in values if value == target)
        output_rows.append(row)

    output_rows.sort(key=lambda row: (int(row["creator_epoch"]), row["creator_time_utc"], row["creator_tx_hash"]))

    with PATTERN_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(output_rows[0].keys()))
        writer.writeheader()
        writer.writerows(output_rows)


def write_shared_addresses_csv(tagged_rows: list[dict[str, str]]) -> None:
    address_creators: dict[str, set[str]] = defaultdict(set)
    for row in tagged_rows:
        address_creators[row["feeder_address"]].add(row["creator_tx_hash"])

    output_rows: list[dict[str, object]] = []
    for address, creators in address_creators.items():
        if len(creators) < 2:
            continue
        output_rows.append(
            {
                "feeder_address": address,
                "creator_count": len(creators),
                "creators": "|".join(sorted(creators)),
            }
        )

    output_rows.sort(key=lambda row: (-int(row["creator_count"]), row["feeder_address"]))

    with SHARED_ADDRS_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(output_rows[0].keys()))
        writer.writeheader()
        writer.writerows(output_rows)


def write_recurring_values_csv(tagged_rows: list[dict[str, str]]) -> None:
    value_rows: Counter[float] = Counter()
    value_creators: dict[float, set[str]] = defaultdict(set)

    for row in tagged_rows:
        value = round(float(row["feeder_ada"]), 6)
        value_rows[value] += 1
        value_creators[value].add(row["creator_tx_hash"])

    output_rows: list[dict[str, object]] = []
    for value, occurrence_count in value_rows.items():
        creator_count = len(value_creators[value])
        if creator_count < 2:
            continue
        output_rows.append(
            {
                "feeder_ada": format_float(value),
                "creator_count": creator_count,
                "occurrence_count": occurrence_count,
                "creators": "|".join(sorted(value_creators[value])),
            }
        )

    output_rows.sort(
        key=lambda row: (
            -int(row["creator_count"]),
            -int(row["occurrence_count"]),
            -float(row["feeder_ada"]),
        )
    )

    with RECURRING_VALUES_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(output_rows[0].keys()))
        writer.writeheader()
        writer.writerows(output_rows)


def main() -> None:
    large_cluster = load_large_cluster()
    creator_hashes = {row["creator_tx_hash"] for row in large_cluster}
    tagged_rows = load_tagged_rows(creator_hashes)
    creator_summary = load_creator_summary(creator_hashes)

    write_pattern_csv(large_cluster, tagged_rows, creator_summary)
    write_shared_addresses_csv(tagged_rows)
    write_recurring_values_csv(tagged_rows)

    print(f"Wrote: {PATTERN_CSV.name}")
    print(f"Wrote: {SHARED_ADDRS_CSV.name}")
    print(f"Wrote: {RECURRING_VALUES_CSV.name}")


if __name__ == "__main__":
    main()

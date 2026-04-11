#!/usr/bin/env python3
"""
tag_creator_feeders_with_seed_traces.py

Post-processing step for bridge_input_creator_table_step1.sql Result B.

Reads:
  - outputs/cross_entity_evidence/bridge_creator_feeders_result_b_2026-04-08.csv
      (psql output of Result B from bridge_input_creator_table_step1.sql)
  - datasets/genesis-founders/iog/iog_trace_edges_part1.csv
  - datasets/genesis-founders/iog/iog_trace_edges_part2.csv
  - datasets/genesis-founders/emurgo/emurgo_trace_edges_part1.csv
  - datasets/genesis-founders/emurgo/emurgo_trace_edges_part2.csv
  - datasets/genesis-founders/cf/   (cf_trace_edges_*.csv files)

For each (creator_tx_hash, feeder_tx_out_id) row in Result B, checks whether:
  - feeder_tx_out_id appears as dest_tx_out_id in the IOG trace edges     -> iog_tagged
  - feeder_tx_out_id appears as dest_tx_out_id in the EMURGO trace edges  -> emurgo_tagged
  - feeder_tx_out_id appears as dest_tx_out_id in the CF trace edges      -> cf_tagged

Writes:
  - outputs/cross_entity_evidence/bridge_creator_feeders_tagged_2026-04-08.csv

Usage:
  cd C:/Users/david/ABCDE
  python scripts/tag_creator_feeders_with_seed_traces.py
"""

import csv
import glob
import os
import sys
from collections import defaultdict

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RESULT_B_CSV = os.path.join(
    REPO_ROOT,
    "outputs/cross_entity_evidence/bridge_creator_feeders_result_b_2026-04-08.csv",
)
OUTPUT_CSV = os.path.join(
    REPO_ROOT,
    "outputs/cross_entity_evidence/bridge_creator_feeders_tagged_2026-04-08.csv",
)

TRACE_EDGE_GLOBS = {
    "iog":    os.path.join(REPO_ROOT, "datasets/genesis-founders/iog/iog_trace_edges_part*.csv"),
    "emurgo": os.path.join(REPO_ROOT, "datasets/genesis-founders/emurgo/emurgo_trace_edges_part*.csv"),
    "cf":     os.path.join(REPO_ROOT, "datasets/genesis-founders/cf/cf_trace_edges_part*.csv"),
}

CURRENT_UNSPENT_GLOBS = {
    "iog":    os.path.join(REPO_ROOT, "datasets/genesis-founders/iog/current_unspent.csv"),
    "emurgo": os.path.join(REPO_ROOT, "datasets/genesis-founders/emurgo/current_unspent.csv"),
    "cf":     os.path.join(REPO_ROOT, "datasets/genesis-founders/cf/current_unspent.csv"),
}


def load_dest_tx_out_ids(pattern_dict):
    """
    Returns a dict: entity -> set of dest_tx_out_id (as int) from trace-edge files.
    Also tries current_unspent.csv files for any UTxOs that are still unspent
    (those are present as dest_tx_out_id in the frontier export).
    """
    result = {}
    for entity, pattern in pattern_dict.items():
        ids = set()
        files = sorted(glob.glob(pattern))
        if not files:
            print(f"  [WARN] No trace-edge files found for {entity}: {pattern}", file=sys.stderr)
        for f in files:
            with open(f, newline="", encoding="utf-8") as fh:
                reader = csv.DictReader(fh)
                for row in reader:
                    try:
                        ids.add(int(row["dest_tx_out_id"]))
                    except (KeyError, ValueError):
                        pass
        result[entity] = ids
        print(f"  {entity}: {len(ids):,} dest_tx_out_ids loaded from trace edges", file=sys.stderr)
    return result


def load_frontier_ids(pattern_dict):
    """
    Load dest_tx_out_id from current_unspent.csv files (unspent frontier).
    Merged into the trace-edge sets.
    """
    result = {}
    for entity, path in pattern_dict.items():
        ids = set()
        if os.path.exists(path):
            with open(path, newline="", encoding="utf-8") as fh:
                reader = csv.DictReader(fh)
                for row in reader:
                    try:
                        ids.add(int(row["dest_tx_out_id"]))
                    except (KeyError, ValueError):
                        pass
            print(f"  {entity} frontier: {len(ids):,} dest_tx_out_ids loaded", file=sys.stderr)
        result[entity] = ids
    return result


def main():
    print("Loading trace-edge ID sets...", file=sys.stderr)
    edge_ids = load_dest_tx_out_ids(TRACE_EDGE_GLOBS)
    frontier_ids = load_frontier_ids(CURRENT_UNSPENT_GLOBS)

    # Merge frontier IDs into edge sets
    combined = {}
    for entity in edge_ids:
        combined[entity] = edge_ids[entity] | frontier_ids.get(entity, set())
        print(
            f"  {entity} combined: {len(combined[entity]):,} total tagged tx_out_ids",
            file=sys.stderr,
        )

    print(f"\nReading Result B from: {RESULT_B_CSV}", file=sys.stderr)
    if not os.path.exists(RESULT_B_CSV):
        print(f"ERROR: Result B CSV not found at {RESULT_B_CSV}", file=sys.stderr)
        print("Run bridge_input_creator_table_step1.sql first and save Result B to that path.", file=sys.stderr)
        sys.exit(1)

    rows = []
    with open(RESULT_B_CSV, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            rows.append(row)

    print(f"  {len(rows):,} rows loaded", file=sys.stderr)

    tagged_rows = []
    for row in rows:
        try:
            fid = int(row["feeder_tx_out_id"])
        except (KeyError, ValueError):
            fid = None

        iog_tagged    = (fid in combined["iog"])    if fid is not None else False
        emurgo_tagged = (fid in combined["emurgo"]) if fid is not None else False
        cf_tagged     = (fid in combined["cf"])     if fid is not None else False

        seed_labels = []
        if iog_tagged:    seed_labels.append("IOG")
        if emurgo_tagged: seed_labels.append("EMURGO")
        if cf_tagged:     seed_labels.append("CF")

        tagged_row = dict(row)
        tagged_row["iog_tagged"]    = "1" if iog_tagged    else "0"
        tagged_row["emurgo_tagged"] = "1" if emurgo_tagged else "0"
        tagged_row["cf_tagged"]     = "1" if cf_tagged     else "0"
        tagged_row["seed_labels"]   = "|".join(seed_labels) if seed_labels else "none"
        tagged_rows.append(tagged_row)

    # Summary
    iog_count    = sum(1 for r in tagged_rows if r["iog_tagged"]    == "1")
    emurgo_count = sum(1 for r in tagged_rows if r["emurgo_tagged"] == "1")
    cf_count     = sum(1 for r in tagged_rows if r["cf_tagged"]     == "1")
    none_count   = sum(1 for r in tagged_rows if r["seed_labels"]   == "none")
    print(f"\nTagging summary:", file=sys.stderr)
    print(f"  IOG-tagged feeder rows:    {iog_count:,}", file=sys.stderr)
    print(f"  EMURGO-tagged feeder rows: {emurgo_count:,}", file=sys.stderr)
    print(f"  CF-tagged feeder rows:     {cf_count:,}", file=sys.stderr)
    print(f"  Untagged (none):           {none_count:,}", file=sys.stderr)

    # Write output
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    if tagged_rows:
        fieldnames = list(tagged_rows[0].keys())
        with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(tagged_rows)
        print(f"\nOutput written to: {OUTPUT_CSV}", file=sys.stderr)
    else:
        print("No rows to write.", file=sys.stderr)


if __name__ == "__main__":
    main()

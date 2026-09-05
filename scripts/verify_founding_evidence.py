#!/usr/bin/env python3
"""Verify founding-entity CSV evidence locally using exact lovelace arithmetic.

Expected snapshot metrics live in the manifest. With --db, check database/CSV
fidelity and execute every public example through the repository read-only guard.
No network access or production queries are used.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import itertools
import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data/manifests/founding-evidence-manifest.json"
RECEIPTS = "founding_query_receipts"

def require(ok, message):
    if not ok:
        raise ValueError(message)

def integer(value):
    require(bool(re.fullmatch(r"-?\d+", str(value))), f"not an exact integer: {value!r}")
    return int(value)

def utc(value):
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    # db-sync's block.time is UTC, even when serialized without a suffix.
    return result.replace(tzinfo=timezone.utc) if result.tzinfo is None else result.astimezone(timezone.utc)

def safe_path(relative):
    path = (ROOT / relative).resolve()
    require(path.is_relative_to(ROOT.resolve()), f"path escapes repository: {relative}")
    return path

def read_csv(path):
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        require(bool(reader.fieldnames), f"missing CSV header: {path.name}")
        require(len(reader.fieldnames) == len(set(reader.fieldnames)), f"duplicate header: {path.name}")
        result = list(reader)
    require(all(None not in row and None not in row.values() for row in result), f"malformed CSV: {path.name}")
    return result

def unique(rows, fields, label):
    keys = [tuple(row[field] for field in fields) for row in rows]
    require(len(keys) == len(set(keys)), f"duplicate {label} keys: {fields}")

def latest_valid_votes(rows):
    latest = {}
    for row in rows:
        # A non-NULL invalid field is invalid, including a serialized false.
        if row["invalid"] != "":
            continue
        require(row["vote"] in {"Yes", "No", "Abstain"}, f"unknown vote: {row['vote']}")
        key = (row["drep_id"], row["gov_action_tx_hash"], row["gov_action_index"])
        order = (integer(row["ballot_tx_id"]), integer(row["ballot_index"]))
        if key not in latest or order > latest[key][0]:
            latest[key] = (order, row)
    return {key: ordered[1] for key, ordered in latest.items()}

def vote_pair(latest, a, b):
    av = {key[1:]: row["vote"] for key, row in latest.items() if key[0] == a}
    bv = {key[1:]: row["vote"] for key, row in latest.items() if key[0] == b}
    common = av.keys() & bv.keys()
    return {
        "joint_actions": len(common),
        "same_votes": sum(av[key] == bv[key] for key in common),
        "opposing_yes_no": sum({av[key], bv[key]} == {"Yes", "No"} for key in common),
    }

def verify_manifest(payload):
    require(payload["schema_version"] == 1, "unsupported founding manifest version")
    require(payload["boundary_kind"] == "repeatable_read_snapshot", "unknown chain boundary")
    tip = payload["chain_tip"]
    require(integer(tip["block_no"]) > 0 and integer(tip["epoch_no"]) > 0, "invalid chain tip")
    require(bool(re.fullmatch(r"[0-9a-f]{64}", tip["hash"])), "invalid chain tip hash")
    utc(tip["time"])
    items = payload["files"]
    paths = {item["path"] for item in items}
    require(len(items) == len(paths), "duplicate manifest paths")
    tables, metadata = {}, {}
    for item in items:
        path = safe_path(item["path"])
        require(path.is_file(), f"missing artifact: {item['path']}")
        require(path.stat().st_size == integer(item["bytes"]), f"byte count mismatch: {item['path']}")
        require(hashlib.sha256(path.read_bytes()).hexdigest() == item["sha256"], f"hash mismatch: {item['path']}")
        if path.suffix == ".csv" and path.parent == (ROOT / "data/small").resolve():
            rows = read_csv(path)
            require(len(rows) == integer(item["row_count"]), f"row count mismatch: {path.stem}")
            for row in rows:
                for column, value in row.items():
                    if column.endswith("_lovelace") and value != "":
                        integer(value)
            tables[path.stem], metadata[path.stem] = rows, item
    found = {p.stem for p in (ROOT / "data/small").glob("founding_*.csv")}
    require(found == set(tables), f"founding CSV manifest coverage mismatch: {found ^ set(tables)}")
    unique(tables[RECEIPTS], ("table_name",), "collection receipt")
    receipts = {r["table_name"]: r for r in tables[RECEIPTS]}
    require(set(receipts) == set(tables) - {RECEIPTS}, "every founding table needs exactly one receipt")
    chain_windows = {
        (r["collection_started_utc"], r["collection_finished_utc"])
        for r in receipts.values() if r["source_kind"] == "dbsync_atomic_snapshot"
    }
    require(len(chain_windows) == 1, "chain receipts do not share one collection window")
    require(len(tables["founding_chain_tip"]) == 1, "expected one founding chain tip")
    tip_row = tables["founding_chain_tip"][0]
    for key in ("block_no", "epoch_no", "hash"):
        require(str(tip_row[key]) == str(tip[key]), f"chain tip table differs from manifest: {key}")
    require(utc(tip_row["time"]) == utc(tip["time"]), "chain tip time differs from manifest")
    for name, receipt in receipts.items():
        require(integer(receipt["row_count"]) == len(tables[name]), f"receipt row count mismatch: {name}")
        require(receipt["csv_sha256"] == metadata[name]["sha256"], f"receipt hash mismatch: {name}")
        require(utc(receipt["collection_started_utc"]) <= utc(receipt["collection_finished_utc"]), f"collection clock reversed: {name}")
        require(receipt["source_kind"] in {"dbsync_atomic_snapshot", "public_sources", "historical_selection"}, f"unknown source kind: {name}")
        if receipt["source_kind"] == "dbsync_atomic_snapshot":
            for field, key in [("db_tip_block", "block_no"), ("db_tip_epoch", "epoch_no"), ("db_tip_hash", "hash")]:
                require(str(receipt[field]) == str(tip[key]), f"mixed snapshot {field}: {name}")
            require(utc(receipt["db_tip_time"]) == utc(tip["time"]), f"mixed snapshot time: {name}")
            require(receipt["query_path"], f"missing extraction query: {name}")
        else:
            require(all(not receipt[f] for f in ("db_tip_block", "db_tip_epoch", "db_tip_time", "db_tip_hash")), f"nonchain receipt carries tip: {name}")
        if receipt["query_path"]:
            require(safe_path(receipt["query_path"]).is_file(), f"missing extraction query: {name}")
            require(receipt["query_path"] in paths, f"query not hash-pinned: {name}")
    return tables

def verify_evidence(tables, payload):
    expected = payload["expected_claims"]
    identities = tables["founding_drep_identity"]
    unique(identities, ("drep_id",), "DRep identity")
    unique(identities, ("drep_hash_id",), "typed DRep identity")
    names = {row["drep_id"]: row["entity"] for row in identities}
    typed = {row["drep_hash_id"]: row for row in identities}
    require(all(row["has_script"] in {"t", "f", "true", "false", "True", "False"} for row in identities), "missing named credential type")
    votes = tables["founding_votes"]
    unique(votes, ("drep_id", "gov_action_tx_hash", "gov_action_index", "ballot_tx_id", "ballot_index"), "ballot")
    require({row["drep_id"] for row in votes} <= names.keys(), "ballot DRep absent from identities")
    for row in votes:
        identity = typed.get(row["drep_hash_id"])
        require(identity is not None, "ballot credential outside named scope")
        require((row["drep_id"], row["has_script"]) == (identity["drep_id"], identity["has_script"]), "ballot typed identity mismatch")
        require(integer(row["block_no"]) <= integer(payload["chain_tip"]["block_no"]), "ballot exceeds snapshot tip")
        require(utc(row["block_time"]) <= utc(payload["chain_tip"]["time"]), "ballot time exceeds snapshot tip")
    proposals = tables["founding_proposals"]
    unique(proposals, ("gov_action_tx_hash", "gov_action_index"), "governance action")
    action_types = {(r["gov_action_tx_hash"], r["gov_action_index"]): r["type"] for r in proposals}
    require(all(action_types.get((r["gov_action_tx_hash"], r["gov_action_index"])) == r["gov_action_type"] for r in votes), "ballot action absent from proposal receipt or type differs")
    latest = latest_valid_votes(votes)
    pairs = [{"a": a, "b": b, **vote_pair(latest, a, b)} for a, b in itertools.combinations(sorted(names), 2)]
    stored_pairs = tables["founding_vote_pairs"]
    unique(stored_pairs, ("a", "b"), "stored vote pair")
    require({(r["a"], r["b"]) for r in stored_pairs} == {(r["a"], r["b"]) for r in pairs}, "stored vote-pair coverage differs from named cohort")
    for claim in expected["vote_pairs"] + stored_pairs:
        require(claim["a"] in names and claim["b"] in names, "unknown expected vote-pair identity")
        actual = vote_pair(latest, claim["a"], claim["b"])
        for metric in ("joint_actions", "same_votes", "opposing_yes_no"):
            require(actual[metric] == integer(claim[metric]), f"vote claim mismatch: {claim['a']} / {claim['b']} {metric}")

    distribution = tables["founding_drep_distribution"]
    unique(distribution, ("epoch_no", "drep_hash_id"), "DRep distribution")
    unique(distribution, ("epoch_no", "drep_id", "has_script"), "typed DRep distribution")
    epoch = max(integer(row["epoch_no"]) for row in distribution)
    require(epoch <= integer(payload["chain_tip"]["epoch_no"]), "distribution epoch exceeds tip")
    require(all(integer(r["amount_lovelace"]) >= 0 for r in distribution), "negative voting power")
    named_distribution = []
    for row in distribution:
        if row["drep_hash_id"] in typed:
            identity = typed[row["drep_hash_id"]]
            require((row["drep_id"], row["has_script"]) == (identity["drep_id"], identity["has_script"]), "distribution typed identity mismatch")
            named_distribution.append(row)
    power = {r["drep_id"]: integer(r["amount_lovelace"]) for r in named_distribution if integer(r["epoch_no"]) == epoch}
    for drep, value in expected["latest_voting_power_by_drep"].items():
        require(power.get(drep) == integer(value), f"latest voting-power claim mismatch: {drep}")
    groups = defaultdict(int)
    for row in identities:
        require(row["drep_id"] in power, f"named DRep missing latest epoch: {row['drep_id']}")
        groups[row["group_name"]] += power[row["drep_id"]]

    inputs, outputs = tables["founding_early_merge_inputs"], tables["founding_early_merge_outputs"]
    unique(inputs, ("tx_hash", "input_tx_hash", "input_index"), "transaction input")
    unique(outputs, ("tx_hash", "output_index"), "transaction output")
    tx_hash = expected["early_merge_transaction_hash"]
    require({r["tx_hash"] for r in inputs} == {tx_hash} == {r["tx_hash"] for r in outputs}, "unexpected early transaction")
    fees = {integer(r["fee_lovelace"]) for r in outputs}
    require(len(fees) == 1, "inconsistent transaction fee")
    input_sum = sum(integer(r["value_lovelace"]) for r in inputs)
    output_sum = sum(integer(r["value_lovelace"]) for r in outputs)
    fee = fees.pop()
    require(all(integer(r["value_lovelace"]) >= 0 for r in inputs + outputs) and fee >= 0, "negative transaction value")
    require(input_sum == output_sum + fee, "early transaction fails input = output + fee conservation")

    credits = tables["founding_reserve_credits"]
    unique(credits, ("tx_hash", "cert_index", "stake_address"), "reserve credit")
    require(len({r["tx_hash"] for r in credits}) == 1, "reserve receipt includes multiple transactions")
    reserve_total = sum(integer(r["value_lovelace"]) for r in credits)
    require(all(integer(r["value_lovelace"]) >= 0 for r in credits), "negative reserve credit")
    require(reserve_total == integer(expected["reserve_credit_lovelace"]), "reserve credit claim mismatch")

    keys, stake = tables["founding_cohort_keys"], tables["founding_cohort_stake"]
    unique(keys, ("stake_address",), "cohort selector")
    unique(stake, ("stake_address", "epoch_no"), "cohort stake")
    require({r["stake_address"] for r in keys} == {r["stake_address"] for r in stake}, "cohort receipt differs from frozen selector")
    require({integer(r["epoch_no"]) for r in stake} == {epoch}, "cohort uses a different epoch")
    require(all(r["selection_source"] and r["selection_snapshot_utc"] for r in keys), "cohort selection provenance missing")
    require(all(integer(r["amount_lovelace"]) >= 0 for r in stake), "negative cohort stake")
    for row in keys:
        utc(row["selection_snapshot_utc"])
    return {
        "latest_epoch": epoch, "latest_valid_ballots": len(latest), "vote_pairs": pairs,
        "group_delegated_voting_lovelace_not_ownership": dict(groups),
        "early_transaction": {"inputs_lovelace": input_sum, "outputs_lovelace": output_sum, "fee_lovelace": fee},
        "reserve_credits_lovelace": reserve_total, "cohort_credentials": len(keys),
        "cohort_active_stake_lovelace_not_ownership": sum(integer(r["amount_lovelace"]) for r in stake),
    }

def verify_database(db, tables):
    import duckdb
    sys.path.insert(0, str(ROOT))
    from mcp_server.readonly import assert_read_only
    con = duckdb.connect(str(db), read_only=True)
    try:
        for name in tables:
            require(bool(re.fullmatch(r"founding_[a-z0-9_]+", name)), "unsafe table identifier")
            path = ROOT / "data/small" / f"{name}.csv"
            differences = con.execute(
                f'SELECT count(*) FROM ((SELECT * FROM "{name}" EXCEPT ALL SELECT * FROM read_csv_auto(?, header=true, sample_size=-1)) '
                f'UNION ALL (SELECT * FROM read_csv_auto(?, header=true, sample_size=-1) EXCEPT ALL SELECT * FROM "{name}"))',
                [str(path), str(path)],
            ).fetchone()[0]
            require(differences == 0, f"database differs from committed CSV: {name}")
            for column, kind, *_ in con.execute(f'DESCRIBE "{name}"').fetchall():
                if column.endswith("_lovelace"):
                    require(kind not in {"DOUBLE", "FLOAT", "REAL"}, f"inexact money type: {name}.{column}: {kind}")
        examples = sorted((ROOT / "sql/35_founding_entities").glob("*.duckdb.sql"))
        require(bool(examples), "missing public founding SQL examples")
        for path in examples:
            sql = assert_read_only(path.read_text())
            require(sql.lstrip().lower().startswith(("select", "with")), f"example is not SELECT/WITH: {path.name}")
            require(bool(con.execute(sql).fetchall()), f"example returned no rows: {path.name}")
            print(f"PASS {path.relative_to(ROOT)}")
    finally:
        con.close()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--db", type=Path, help="also verify a rebuilt DuckDB and execute public SQL")
    args = parser.parse_args()
    try:
        payload = json.loads(args.manifest.read_text())
        tables = verify_manifest(payload)
        summary = verify_evidence(tables, payload)
        if args.db:
            verify_database(args.db, tables)
        print(json.dumps(summary, indent=2))
        print(f"PASS founding evidence: {len(tables)} CSVs, exact arithmetic and collection receipts verified")
    except (ValueError, KeyError, OSError) as error:
        raise SystemExit(f"FAIL founding evidence: {error}") from error

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Deterministic custody-pattern classifier for genesis control indicators.

Reads:
  data/small/genesis_control_indicators_raw.csv   (warehouse extraction)
  data/small/genesis_control_cert_cohorts.csv     (shared-certificate txs)
  data/small/governance_genesis_behavior_clusters.csv (behavior class carry-over)
  data/small/db_tip_receipt.csv                   (tip time = "now" reference)

Writes:
  data/small/genesis_control_indicators.csv  (final table: raw + flags + classes)
  data/small/genesis_control_summary.csv     (per-class rollup)
  data/manifests/genesis-control-indicators-manifest.json

Grading (docs/02_GRADING.md):
  - Every raw indicator column is FACT (directly queryable at the recorded tip).
  - `batch_operated` rests on shared-certificate txs: multiple stake keys
    certified in ONE transaction were managed by one wallet/tool at that
    moment — that linkage is FACT; who runs the wallet is not established.
  - `fe_control_consistency` is a WORKING_HYPOTHESIS label: it says the
    on-chain pattern is consistent with the original custodian still holding
    the keys. It never asserts legal ownership or real-world identity.

All thresholds are fixed constants below so the classification is reproducible.
"""
from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import os

ROOT = Path(__file__).resolve().parents[1]
SMALL = ROOT / "data/small"
# Output/input prefix. Default = genesis_control; set ABCDE_CONTROL_PREFIX to
# classify a different key set through the same logic (e.g. fleet_control for
# the F13 operator fleet), producing <prefix>_indicators/_summary and a
# matching manifest without touching the genesis set.
PREFIX = os.environ.get("ABCDE_CONTROL_PREFIX", "genesis_control")
RAW = SMALL / f"{PREFIX}_indicators_raw.csv"
COHORTS = SMALL / f"{PREFIX}_cert_cohorts.csv"
CLUSTERS = SMALL / "governance_genesis_behavior_clusters.csv"
TIP = SMALL / "db_tip_receipt.csv"
OUT = SMALL / f"{PREFIX}_indicators.csv"
OUT_SUMMARY = SMALL / f"{PREFIX}_summary.csv"
MANIFEST = ROOT / f"data/manifests/{PREFIX.replace('_', '-')}-indicators-manifest.json"

# Fixed classification thresholds (change = new data_version).
HOLDING_MIN_ADA = 1_000.0          # "currently holding" floor
DRAINED_MAX_ADA = 1.0              # "exited/dispersed" ceiling
DORMANT_YEARS = 2.0                # principal considered static after this
RECENT_CERT_YEARS = 2.0            # cert newer than this proves live keys
RECENT_SPEND_DAYS = 180            # outgoing newer than this = actively managed
PASSIVITY_MIN_REWARDS_ADA = 1_000.0  # meaningful never-withdrawn rewards
BATCH_MIN_MEMBERS = 3              # cohort size that flags batch operation


def parse_ts(v: str) -> datetime | None:
    v = (v or "").strip()
    if not v:
        return None
    return datetime.fromisoformat(v).replace(tzinfo=timezone.utc)


def years_between(a: datetime, b: datetime) -> float:
    return (b - a).total_seconds() / (365.25 * 24 * 3600)


def main() -> None:
    tip_row = next(csv.DictReader(TIP.open()))
    tip_time = parse_ts(tip_row["db_tip_time"])
    if tip_time is None:
        raise SystemExit("db_tip_receipt.csv has no db_tip_time")

    batch_members: set[str] = set()
    for row in csv.DictReader(COHORTS.open()):
        if int(row["set_member_count"]) >= BATCH_MIN_MEMBERS:
            batch_members.update(row["set_members"].split(";"))

    behavior: dict[str, dict[str, str]] = {}
    for row in csv.DictReader(CLUSTERS.open()):
        behavior[row["stake_address"]] = {
            "behavior_class": row.get("behavior_class", ""),
            "root_combo": row.get("root_combo", ""),
        }

    rows_out: list[dict[str, object]] = []
    for row in csv.DictReader(RAW.open()):
        ada = float(row["current_ada"] or 0)
        rewards = float(row["rewards_earned_ada"] or 0)
        withdrawals = int(row["withdrawal_count"] or 0)
        last_out = parse_ts(row["last_outgoing_time"])
        cert_times = [
            t for t in (parse_ts(row["latest_pool_cert_time"]),
                        parse_ts(row["latest_drep_cert_time"])) if t
        ]

        never_spent = last_out is None and int(row["total_output_rows"] or 0) > 0
        dormant_years = (
            years_between(last_out, tip_time) if last_out else
            (years_between(parse_ts(row["first_received_time"]), tip_time)
             if row["first_received_time"] else None)
        )
        principal_static = never_spent or (
            dormant_years is not None and last_out is not None
            and dormant_years >= DORMANT_YEARS
        )
        keys_alive_recent_cert = any(
            years_between(t, tip_time) <= RECENT_CERT_YEARS for t in cert_times
        )
        recently_active = (
            last_out is not None
            and (tip_time - last_out).days <= RECENT_SPEND_DAYS
        )
        rewards_never_withdrawn = rewards > 0 and withdrawals == 0
        institutional_passivity = (
            rewards >= PASSIVITY_MIN_REWARDS_ADA and withdrawals == 0
        )
        batch_operated = row["stake_address"] in batch_members
        currently_holding = ada >= HOLDING_MIN_ADA
        drained = ada < DRAINED_MAX_ADA

        if drained:
            custody = "DRAINED"
        elif never_spent:
            custody = "NEVER_SPENT_COLD"
        elif recently_active:
            custody = "ACTIVE_MANAGED"
        elif principal_static and keys_alive_recent_cert:
            custody = "CERT_ACTIVE_PRINCIPAL_STATIC"
        elif principal_static:
            custody = "DORMANT_2Y_PLUS"
        else:
            custody = "MIXED"

        if drained:
            fe = "EXITED_OR_DISPERSED"
        elif currently_holding and batch_operated and (
            keys_alive_recent_cert or institutional_passivity
        ):
            fe = "HIGH"
        elif currently_holding and (
            keys_alive_recent_cert or institutional_passivity or batch_operated
        ):
            fe = "MEDIUM"
        elif currently_holding:
            fe = "LOW"
        else:
            fe = "INDETERMINATE"

        b = behavior.get(row["stake_address"], {})
        rows_out.append(row | {
            "behavior_class": b.get("behavior_class", ""),
            "root_combo": b.get("root_combo", ""),
            "dormant_years": f"{dormant_years:.2f}" if dormant_years is not None else "",
            "never_spent": never_spent,
            "principal_static": principal_static,
            "keys_alive_recent_cert": keys_alive_recent_cert,
            "recently_active": recently_active,
            "rewards_never_withdrawn": rewards_never_withdrawn,
            "institutional_passivity": institutional_passivity,
            "batch_operated": batch_operated,
            "currently_holding": currently_holding,
            "custody_pattern": custody,
            "fe_control_consistency": fe,
        })

    rows_out.sort(key=lambda r: -float(r["current_ada"] or 0))
    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows_out[0].keys()))
        w.writeheader()
        w.writerows(rows_out)

    summary: dict[tuple[str, str], dict[str, float]] = {}
    for r in rows_out:
        key = (str(r["fe_control_consistency"]), str(r["custody_pattern"]))
        s = summary.setdefault(key, {"stake_addresses": 0, "current_ada": 0.0})
        s["stake_addresses"] += 1
        s["current_ada"] += float(r["current_ada"] or 0)
    with OUT_SUMMARY.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["fe_control_consistency", "custody_pattern",
                    "stake_addresses", "current_ada"])
        for (fe, cp), s in sorted(summary.items(),
                                  key=lambda kv: -kv[1]["current_ada"]):
            w.writerow([fe, cp, int(s["stake_addresses"]),
                        f"{s['current_ada']:.6f}"])

    def sha(p: Path) -> str:
        return hashlib.sha256(p.read_bytes()).hexdigest()

    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps({
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "db_tip_block": tip_row["db_tip_block"],
        "db_tip_time": tip_row["db_tip_time"],
        "thresholds": {
            "holding_min_ada": HOLDING_MIN_ADA,
            "drained_max_ada": DRAINED_MAX_ADA,
            "dormant_years": DORMANT_YEARS,
            "recent_cert_years": RECENT_CERT_YEARS,
            "recent_spend_days": RECENT_SPEND_DAYS,
            "passivity_min_rewards_ada": PASSIVITY_MIN_REWARDS_ADA,
            "batch_min_members": BATCH_MIN_MEMBERS,
        },
        "inputs": {p.name: sha(p) for p in (RAW, COHORTS, CLUSTERS, TIP)},
        "outputs": {p.name: sha(p) for p in (OUT, OUT_SUMMARY)},
        "grading_note": (
            "Indicator columns are FACT at the recorded tip; "
            "fe_control_consistency is a WORKING_HYPOTHESIS classification of "
            "custody-pattern consistency, not an ownership or identity claim."
        ),
    }, indent=2) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)} ({len(rows_out)} rows), "
          f"{OUT_SUMMARY.relative_to(ROOT)}, manifest")


if __name__ == "__main__":
    main()

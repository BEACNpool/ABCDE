#!/usr/bin/env python3
"""Derive tracers/labels/exchange_labels.csv from the method tables.

Labels are mechanically derived from the study's canonical reconstruction
(docs/26_EXCHANGE_TRACER_METHOD.md), never hand-entered, so the grade of every
row is reproducible from the committed CSVs.

Two row types:

* ``custody_cluster`` — a terminus wallet-cluster whose name RESOLVED: a unique
  participant-count lead of at least 2 distinct pre-deposit wallet keys.
* ``deposit_address`` — an address a participant deposited a tracer to, carrying
  that participant's claim.

Grading rule. A deposit address cannot be corroborated by other participants —
an exchange hands each user their own deposit address, so its claim count is
always thin by construction. Its support therefore comes from the terminus its
tracers reach: STRONG_INFERENCE when that terminus resolved to the same name,
WORKING_HYPOTHESIS otherwise. Counting claim messages per address is NOT
corroboration and is never used here.
"""
from __future__ import annotations

import csv
import pathlib
from collections import defaultdict

TRACERS_DIR = pathlib.Path(__file__).resolve().parents[1]
DATA = TRACERS_DIR / "data"
OUT = TRACERS_DIR / "labels" / "exchange_labels.csv"

EVIDENCE_URL = "https://tracer.adagenesistransparency.com"
SUBMITTED_BY = "the_red_or_blue_pill_study_participants"

FIELDS = [
    "address",
    "stake_address",
    "claimed_entity",
    "label_type",
    "evidence",
    "evidence_url",
    "submitted_by",
    "submitted_date",
    "grade",
]


def read(name: str) -> list[dict]:
    with (DATA / f"{name}.csv").open(newline="") as fh:
        return list(csv.DictReader(fh))


def main() -> None:
    deposits = read("valid_deposits")
    clusters = {c["terminus_key"]: c for c in read("terminus_clusters")}
    votes = read("name_votes")

    split: dict[str, list[str]] = defaultdict(list)
    for v in sorted(votes, key=lambda r: (-int(r["participants"]), -int(r["tracers"]))):
        name = v["claimed_exchange"] or "(unnamed)"
        split[v["terminus_key"]].append(f"{name} {v['tracers']}t/{v['participants']}p")

    rows: list[dict] = []

    # 1. resolved custody clusters
    for key, c in sorted(clusters.items()):
        if c["resolution_status"] != "resolved":
            continue
        stake = key[2:] if key.startswith("s:") else ""
        addr = c["terminus_address_if_no_stake"] if key.startswith("a:") else ""
        if key.startswith("a:") and not addr:
            addr = key[2:]
        rows.append(
            {
                "address": addr,
                "stake_address": stake,
                "claimed_entity": c["resolved_exchange"],
                "label_type": "custody_cluster",
                "evidence": (
                    f"study method: {c['tracers']} tracer(s) from "
                    f"{c['participants']} distinct participant wallet(s); "
                    f"vote split: {'; '.join(split.get(key, []))}"
                ),
                "evidence_url": EVIDENCE_URL,
                "submitted_by": SUBMITTED_BY,
                "submitted_date": c["last_deposit"][:10],
                "grade": "STRONG_INFERENCE",
            }
        )

    # 2. deposit addresses, graded by the terminus their tracers reach
    by_addr: dict[str, list[dict]] = defaultdict(list)
    for d in deposits:
        by_addr[d["deposit_address"]].append(d)

    for addr, ds in sorted(by_addr.items()):
        names = sorted({d["claimed_exchange"] for d in ds if d["claimed_exchange"]})
        termini = sorted({d["terminus_key"] for d in ds})
        resolved = {
            clusters[t]["resolved_exchange"]
            for t in termini
            if t in clusters and clusters[t]["resolution_status"] == "resolved"
        }
        supported = bool(names) and len(names) == 1 and names[0] in resolved
        status = "; ".join(
            f"terminus {t[:14]}… {clusters[t]['resolution_status']}"
            + (
                f" -> {clusters[t]['resolved_exchange']}"
                if clusters[t]["resolved_exchange"]
                else ""
            )
            for t in termini
            if t in clusters
        )
        rows.append(
            {
                "address": addr,
                "stake_address": ds[0]["deposit_stake_address"],
                "claimed_entity": "|".join(names) if names else "(unparsed message)",
                "label_type": "deposit_address",
                "evidence": (
                    f"study method: {len(ds)} validated deposit(s) from "
                    f"{len({d['participant_key'] for d in ds})} participant wallet(s); "
                    f"{status}"
                ),
                "evidence_url": EVIDENCE_URL,
                "submitted_by": SUBMITTED_BY,
                "submitted_date": max(d["deposit_time"] for d in ds)[:10],
                "grade": "STRONG_INFERENCE" if supported else "WORKING_HYPOTHESIS",
            }
        )

    with OUT.open("w", newline="\n") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)

    strong = sum(1 for r in rows if r["grade"] == "STRONG_INFERENCE")
    print(
        f"wrote {OUT} — {len(rows)} labels "
        f"({strong} STRONG_INFERENCE, {len(rows) - strong} WORKING_HYPOTHESIS)"
    )


if __name__ == "__main__":
    main()

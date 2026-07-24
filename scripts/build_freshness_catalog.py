#!/usr/bin/env python3
"""Refresh the db tip receipt and build the per-table freshness catalog.

Answers "how accurate/fresh is each committed table?" quantitatively:

  data/small/db_tip_receipt.csv        — the warehouse tip this refresh saw
  data/small/data_freshness_catalog.csv — one row per committed data/small CSV:
      rows, bytes, sha256, last git commit time, age in days at refresh,
      snapshot_sensitive (does the table describe *current* chain state,
      making it stale-able, vs a historical fact receipt that never decays).

Historical receipts (mints, past txs, anchor verifications) stay correct
forever; only snapshot_sensitive tables decay as the chain advances. This
catalog is committed so a plain clone can quantify what it is looking at.

Requires ABCDE_SSH for the tip query (skips receipt refresh if unset).
"""
from __future__ import annotations

import csv
import hashlib
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SMALL = ROOT / "data/small"
TIP = SMALL / "db_tip_receipt.csv"
OUT = SMALL / "data_freshness_catalog.csv"

# Name fragments that mark a table as describing current chain state.
SNAPSHOT_HINTS = (
    "current", "latest", "profiles", "receipt", "top_stake",
    "control_indicators", "control_summary", "freshness",
    # tracer method tables: every one is keyed on where a tracer sits NOW
    "terminus", "asset_path", "valid_deposits", "name_votes",
)


def refresh_tip_receipt() -> None:
    ssh_target = os.environ.get("ABCDE_SSH")
    if not ssh_target:
        print("ABCDE_SSH unset — keeping existing db_tip_receipt.csv")
        return
    sql = ("select max(block_no), max(time), max(epoch_no) "
           "from public.block")
    out = subprocess.run(
        ["ssh", ssh_target,
         "sudo -n -u postgres psql -d cexplorer_replica -qtA -c \"" + sql + "\""],
        check=True, capture_output=True, text=True).stdout.strip()
    block, tip_time, epoch = out.split("|")
    with TIP.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["generated_utc", "db_tip_block", "db_tip_time",
                    "db_tip_epoch", "source", "staleness_note"])
        w.writerow([
            datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            block, tip_time, epoch, "abcde:cexplorer_replica",
            "live_replication_current_at_refresh",
        ])
    print(f"tip receipt refreshed: block {block} @ {tip_time}")


def git_commit_utc(path: Path) -> str:
    out = subprocess.run(
        ["git", "log", "-1", "--format=%cI", "--", str(path)],
        cwd=ROOT, capture_output=True, text=True).stdout.strip()
    return out  # empty for not-yet-committed files


def main() -> None:
    refresh_tip_receipt()
    now = datetime.now(timezone.utc)
    rows = []
    import sys as _sys
    _sys.path.insert(0, str(ROOT / "scripts"))
    from build_genesis_db import SKIP_TABLE_STEMS  # keep catalog == shipped DB
    for p in sorted(SMALL.glob("*.csv")):
        if p.name == OUT.name or p.stem in SKIP_TABLE_STEMS:
            continue
        data = p.read_bytes()
        n_rows = max(data.count(b"\n") - 1, 0)
        commit_iso = git_commit_utc(p)
        if commit_iso:
            age_days = (now - datetime.fromisoformat(commit_iso)).days
        else:
            commit_iso, age_days = "uncommitted", 0
        rows.append([
            p.stem, n_rows, len(data),
            hashlib.sha256(data).hexdigest(),
            commit_iso, age_days,
            any(h in p.stem for h in SNAPSHOT_HINTS),
        ])
    with OUT.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["table_name", "data_rows", "bytes", "sha256",
                    "last_commit_utc", "age_days_at_refresh",
                    "snapshot_sensitive"])
        w.writerows(rows)
    print(f"wrote {OUT.relative_to(ROOT)} ({len(rows)} tables)")


if __name__ == "__main__":
    main()

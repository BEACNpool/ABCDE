#!/usr/bin/env python3
"""Build standardized top-DRep profile report artifacts.

The db-sync CSVs provide current governance distribution and delegator
profiles. This script adds local ABCDE genesis-trace exposure/stickiness
rollups from preserved trace receipts and renders a public report.
"""
from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
LEGACY = ROOT / "legacy/2026-05-20-pre-v2-import/data/raw"
OUT_DIR = ROOT / "data/small"
MANIFEST = ROOT / "data/manifests/top-drep-profiles-manifest.json"
REPORT = ROOT / "reports/top_drep_profiles.md"

PROFILE_CSV = OUT_DIR / "governance_top_drep_profiles_current.csv"
STAKE_BUCKET_CSV = OUT_DIR / "governance_top_drep_stake_buckets.csv"
AGE_BUCKET_CSV = OUT_DIR / "governance_top_drep_delegation_age_buckets.csv"
POOL_AFFILIATION_CSV = OUT_DIR / "governance_top_drep_pool_affiliations.csv"
KOIOS_CROSSCHECK_CSV = OUT_DIR / "governance_top_drep_koios_crosscheck.csv"
TRACE_EXPOSURE_CSV = OUT_DIR / "governance_top_drep_genesis_trace_exposure.csv"
TRACE_ROOT_EXPOSURE_CSV = OUT_DIR / "governance_top_drep_genesis_trace_exposure_by_root.csv"
TRACE_STICKINESS_CSV = OUT_DIR / "governance_top_drep_genesis_trace_stickiness.csv"

SEED_MAP = {
    "cf": "cf",
    "emurgo": "emurgo",
    "emurgo2": "fourth_entry_781m",
    "iog": "iog",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def ada(lovelace: int | Decimal) -> Decimal:
    return (Decimal(lovelace) / Decimal(1_000_000)).quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)


def display_ada(value: str | Decimal) -> str:
    n = Decimal(str(value))
    return f"{n:,.6f}".rstrip("0").rstrip(".")


def short_id(value: str, prefix: int = 14) -> str:
    if len(value) <= prefix + 3:
        return value
    return value[:prefix] + "..."


def anchor_label(url: str) -> str:
    if not url:
        return ""
    parsed = urlparse(url)
    if not parsed.netloc:
        return url[:48]
    path = parsed.path.strip("/")
    if len(path) > 34:
        path = path[:31] + "..."
    return f"{parsed.netloc}/{path}" if path else parsed.netloc


def row_key(row: dict[str, str], epoch_col: str = "epoch_no") -> tuple[int, str, str]:
    epoch = int(row.get(epoch_col) or 0)
    return (epoch, row.get("block_time") or "", row.get("tx_hash") or "")


def build_trace_rollups(profiles: list[dict[str, str]]) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    top_ids = [r["drep_id_bech32"] for r in profiles]
    top_set = set(top_ids)
    rank_by_drep = {r["drep_id_bech32"]: r["rank_overall"] for r in profiles}
    class_by_drep = {r["drep_id_bech32"]: r["profile_class"] for r in profiles}
    snapshot = profiles[0]["query_timestamp_utc"]
    drep_epoch = profiles[0]["drep_distribution_epoch"]

    latest_by_root_stake: dict[str, dict[str, dict[str, str]]] = defaultdict(dict)
    ever_by_root_drep: dict[tuple[str, str], set[str]] = defaultdict(set)

    for legacy_seed, root_seed in SEED_MAP.items():
        path = LEGACY / legacy_seed / "drep_delegation.csv"
        for row in read_csv(path):
            stake = row["stake_address"]
            drep = row["drep_id_bech32"] or "ABSTAIN_OR_NO_CONFIDENCE_OR_UNKNOWN"
            ever_by_root_drep[(root_seed, drep)].add(stake)
            prev = latest_by_root_stake[root_seed].get(stake)
            if prev is None or row_key(row) > row_key(prev):
                latest_by_root_stake[root_seed][stake] = row

    current_by_root_stake: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    root_exposure: dict[tuple[str, str], dict[str, object]] = {}
    txout_by_drep: dict[str, dict[str, dict[str, object]]] = defaultdict(dict)

    for legacy_seed, root_seed in SEED_MAP.items():
        path = LEGACY / legacy_seed / "current_unspent.csv"
        for row in read_csv(path):
            stake = row.get("dest_stake_address") or ""
            if not stake:
                continue
            lovelace = int(row["lovelace"])
            current_by_root_stake[root_seed][stake] += lovelace
            latest = latest_by_root_stake[root_seed].get(stake)
            if latest is None:
                continue
            drep = latest["drep_id_bech32"] or "ABSTAIN_OR_NO_CONFIDENCE_OR_UNKNOWN"
            if drep not in top_set:
                continue

            key = (root_seed, drep)
            g = root_exposure.setdefault(key, {
                "stakes": set(),
                "utxos": 0,
                "lovelace": 0,
            })
            g["stakes"].add(stake)  # type: ignore[union-attr]
            g["utxos"] = int(g["utxos"]) + 1
            g["lovelace"] = int(g["lovelace"]) + lovelace

            txout = row["dest_tx_out_id"]
            entry = txout_by_drep[drep].setdefault(txout, {
                "lovelace": lovelace,
                "stakes": set(),
                "roots": set(),
            })
            entry["lovelace"] = max(int(entry["lovelace"]), lovelace)
            entry["stakes"].add(stake)  # type: ignore[union-attr]
            entry["roots"].add(root_seed)  # type: ignore[union-attr]

    root_rows: list[dict[str, object]] = []
    for root_seed in sorted(SEED_MAP.values()):
        for drep in top_ids:
            g = root_exposure.get((root_seed, drep), {"stakes": set(), "utxos": 0, "lovelace": 0})
            lovelace = int(g["lovelace"])
            root_rows.append({
                "query_timestamp_utc": snapshot,
                "drep_distribution_epoch": drep_epoch,
                "rank_overall": rank_by_drep[drep],
                "profile_class": class_by_drep[drep],
                "drep_id_bech32": drep,
                "root_seed_id": root_seed,
                "latest_stake_credentials_with_current_value": len(g["stakes"]),  # type: ignore[arg-type]
                "current_utxos": g["utxos"],
                "current_lovelace": lovelace,
                "current_ada": ada(lovelace),
            })

    exposure_rows: list[dict[str, object]] = []
    for drep in top_ids:
        entries = txout_by_drep.get(drep, {})
        lovelace = sum(int(v["lovelace"]) for v in entries.values())
        stakes: set[str] = set()
        combo_counts: dict[str, dict[str, int]] = defaultdict(lambda: {"utxos": 0, "lovelace": 0})
        for v in entries.values():
            stakes.update(v["stakes"])  # type: ignore[arg-type]
            combo = "+".join(sorted(v["roots"]))  # type: ignore[arg-type]
            combo_counts[combo]["utxos"] += 1
            combo_counts[combo]["lovelace"] += int(v["lovelace"])
        combo_summary = "; ".join(
            f"{combo}:{stats['utxos']} utxos/{ada(stats['lovelace'])} ADA"
            for combo, stats in sorted(combo_counts.items())
        )
        exposure_rows.append({
            "query_timestamp_utc": snapshot,
            "drep_distribution_epoch": drep_epoch,
            "rank_overall": rank_by_drep[drep],
            "profile_class": class_by_drep[drep],
            "drep_id_bech32": drep,
            "dedup_current_utxos": len(entries),
            "dedup_current_stake_credentials": len(stakes),
            "dedup_current_lovelace": lovelace,
            "dedup_current_ada": ada(lovelace),
            "root_overlap_summary": combo_summary,
        })

    stickiness_rows: list[dict[str, object]] = []
    for root_seed in sorted(SEED_MAP.values()):
        latest_for_root = latest_by_root_stake[root_seed]
        for drep in top_ids:
            ever = ever_by_root_drep.get((root_seed, drep), set())
            still = 0
            moved = 0
            unknown = 0
            still_lovelace = 0
            moved_lovelace = 0
            for stake in ever:
                latest = latest_for_root.get(stake)
                current_lovelace = current_by_root_stake[root_seed].get(stake, 0)
                if latest is None:
                    unknown += 1
                elif (latest["drep_id_bech32"] or "ABSTAIN_OR_NO_CONFIDENCE_OR_UNKNOWN") == drep:
                    still += 1
                    still_lovelace += current_lovelace
                else:
                    moved += 1
                    moved_lovelace += current_lovelace
            stickiness_rows.append({
                "query_timestamp_utc": snapshot,
                "drep_distribution_epoch": drep_epoch,
                "rank_overall": rank_by_drep[drep],
                "profile_class": class_by_drep[drep],
                "drep_id_bech32": drep,
                "root_seed_id": root_seed,
                "ever_trace_stake_credentials": len(ever),
                "latest_still_this_drep": still,
                "latest_moved_away": moved,
                "latest_unknown": unknown,
                "latest_still_ratio": "" if not ever else Decimal(still) / Decimal(len(ever)),
                "current_lovelace_latest_still": still_lovelace,
                "current_ada_latest_still": ada(still_lovelace),
                "current_lovelace_moved_away": moved_lovelace,
                "current_ada_moved_away": ada(moved_lovelace),
            })

    return exposure_rows, root_rows, stickiness_rows


def render_report(
    profiles: list[dict[str, str]],
    exposure_rows: list[dict[str, object]],
    stake_rows: list[dict[str, str]],
    age_rows: list[dict[str, str]],
    pool_rows: list[dict[str, str]],
    koios_rows: list[dict[str, str]],
) -> None:
    exposure_by_drep = {r["drep_id_bech32"]: r for r in exposure_rows}
    stake_by_drep_bucket = {(r["drep_id_bech32"], r["active_stake_bucket"]): r for r in stake_rows}
    age_by_drep = defaultdict(list)
    for row in age_rows:
        age_by_drep[row["drep_id_bech32"]].append(row)
    pools_by_drep = defaultdict(list)
    for row in pool_rows:
        pools_by_drep[row["drep_id_bech32"]].append(row)

    first = profiles[0]
    koios_registered = [r for r in koios_rows if r.get("profile_class") == "registered"]
    koios_amount_matches = sum(1 for r in koios_registered if r.get("amount_matches_dbsync") == "true")
    koios_summary = f"{koios_amount_matches}/{len(koios_registered)} registered rows amount-matched Koios" if koios_registered else "not run"
    lines = [
        "# Top DRep Profiles",
        "",
        "This report profiles the current top DReps as a set. It is intentionally not a one-person dossier.",
        "",
        "## Data snapshot",
        "",
        f"- Query timestamp UTC: `{first['query_timestamp_utc']}`",
        f"- db-sync tip UTC: `{first['dbsync_tip_utc']}`",
        f"- db-sync tip epoch: `{first['dbsync_tip_epoch']}`",
        f"- DRep distribution epoch: `{first['drep_distribution_epoch']}`",
        f"- Active stake epoch: `{first['epoch_stake_epoch']}`",
        "- Sources: ABCDE PostgreSQL/cardano-db-sync, preserved ABCDE genesis trace receipts, on-chain DRep registration anchors where present.",
        f"- Koios cross-check: `{koios_summary}`",
        "",
        "## Evidence boundaries",
        "",
        "- FACT: current voting power, delegation counts, active stake buckets, DRep registration anchors, and pool affiliations are db-sync-derived.",
        "- FACT: genesis-trace exposure is derived from preserved ABCDE trace receipts joined to latest observed DRep delegation for those traced stake credentials.",
        "- STRONG INFERENCE: high latest-retention ratios indicate sticky DRep delegation behavior by stake credential.",
        "- UNKNOWN: beneficial ownership, nationality, legal identity, intent, and off-chain demographics are not inferred from delegation data.",
        "- Caveat: DRep delegation is voting power, not custody or control of delegated funds.",
        "",
        "## Current top DReps",
        "",
        "| Rank | Class | DRep | Voting ADA | Current delegators | Historical delegators | Retention | Genesis-trace ADA | Anchor |",
        "|---:|---|---|---:|---:|---:|---:|---:|---|",
    ]

    for row in profiles:
        drep = row["drep_id_bech32"]
        exposure = exposure_by_drep[drep]
        retention = row["latest_retention_ratio"] or ""
        retention_display = "" if retention == "" else f"{Decimal(retention) * Decimal(100):.2f}%"
        lines.append(
            "| {rank} | {cls} | `{drep}` | {voting} | {cur} | {hist} | {ret} | {trace} | {anchor} |".format(
                rank=row["rank_overall"],
                cls=row["profile_class"],
                drep=short_id(drep, 18),
                voting=display_ada(row["voting_power_ada"]),
                cur=row["current_delegator_count"],
                hist=row["historical_delegator_count"],
                ret=retention_display,
                trace=display_ada(str(exposure["dedup_current_ada"])),
                anchor=anchor_label(row["voting_anchor_url"]),
            )
        )

    lines.extend([
        "",
        "## Stake-size profile",
        "",
        "Buckets are based on latest active stake for stake credentials whose latest DRep delegation points to the DRep.",
        "",
        "| Rank | DRep | >=50M | 10M-50M | 1M-10M | 100k-1M | 10k-100k | 1k-10k | <1k | 0/no active stake |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    bucket_order = [">=50M", "10M-50M", "1M-10M", "100k-1M", "10k-100k", "1k-10k", "<1k", "0/no active stake"]
    for row in profiles:
        drep = row["drep_id_bech32"]
        counts = [stake_by_drep_bucket.get((drep, b), {}).get("current_delegator_count", "0") for b in bucket_order]
        lines.append(f"| {row['rank_overall']} | `{short_id(drep, 18)}` | " + " | ".join(str(c) for c in counts) + " |")

    lines.extend([
        "",
        "## Latest-delegation age profile",
        "",
        "This shows when current delegators last delegated to the DRep. Older buckets with large stake are a useful stickiness signal.",
        "",
        "| Rank | DRep | Largest age bucket by ADA | Bucket ADA | Bucket delegators |",
        "|---:|---|---|---:|---:|",
    ])
    for row in profiles:
        drep = row["drep_id_bech32"]
        buckets = age_by_drep[drep]
        top_bucket = max(buckets, key=lambda r: Decimal(r["active_stake_ada"])) if buckets else {}
        lines.append(
            "| {rank} | `{drep}` | {bucket} | {ada_value} | {delegators} |".format(
                rank=row["rank_overall"],
                drep=short_id(drep, 18),
                bucket=top_bucket.get("latest_vote_epoch_bucket", ""),
                ada_value=display_ada(top_bucket.get("active_stake_ada", "0")),
                delegators=top_bucket.get("current_delegator_count", "0"),
            )
        )

    lines.extend([
        "",
        "## Top pool affiliations",
        "",
        "For each DRep, this lists the top active SPO pool among current DRep delegators by active stake. Full top-10 pool rows are in the CSV.",
        "",
        "| Rank | DRep | Top pool ticker | Pool ADA | Delegators |",
        "|---:|---|---|---:|---:|",
    ])
    for row in profiles:
        drep = row["drep_id_bech32"]
        top_pool = pools_by_drep[drep][0] if pools_by_drep[drep] else {}
        lines.append(
            "| {rank} | `{drep}` | {ticker} | {ada_value} | {delegators} |".format(
                rank=row["rank_overall"],
                drep=short_id(drep, 18),
                ticker=top_pool.get("ticker_name") or short_id(top_pool.get("pool_id_bech32", ""), 12),
                ada_value=display_ada(top_pool.get("active_stake_ada", "0")),
                delegators=top_pool.get("current_delegator_count", "0"),
            )
        )

    lines.extend([
        "",
        "## Generated artifacts",
        "",
        "- `data/small/governance_top_drep_profiles_current.csv`",
        "- `data/small/governance_top_drep_stake_buckets.csv`",
        "- `data/small/governance_top_drep_delegation_age_buckets.csv`",
        "- `data/small/governance_top_drep_pool_affiliations.csv`",
        "- `data/small/governance_top_drep_koios_crosscheck.csv`",
        "- `data/small/governance_top_drep_genesis_trace_exposure.csv`",
        "- `data/small/governance_top_drep_genesis_trace_exposure_by_root.csv`",
        "- `data/small/governance_top_drep_genesis_trace_stickiness.csv`",
        "- `data/manifests/top-drep-profiles-manifest.json`",
    ])

    REPORT.write_text("\n".join(lines) + "\n")


def build_manifest(paths: list[Path], profiles: list[dict[str, str]]) -> None:
    outputs = {
        str(path.relative_to(ROOT)): {
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        }
        for path in paths
    }
    payload = {
        "schema_version": 1,
        "query_timestamp_utc": profiles[0]["query_timestamp_utc"],
        "dbsync_tip_utc": profiles[0]["dbsync_tip_utc"],
        "dbsync_tip_epoch": profiles[0]["dbsync_tip_epoch"],
        "drep_distribution_epoch": profiles[0]["drep_distribution_epoch"],
        "epoch_stake_epoch": profiles[0]["epoch_stake_epoch"],
        "top_drep_count": len(profiles),
        "inputs": [
            "sql/20_profiles/top_drep_profiles_current.sql",
            "sql/20_profiles/top_drep_stake_buckets.sql",
            "sql/20_profiles/top_drep_delegation_age_buckets.sql",
            "sql/20_profiles/top_drep_pool_affiliations.sql",
            "legacy/2026-05-20-pre-v2-import/data/raw/*/drep_delegation.csv",
            "legacy/2026-05-20-pre-v2-import/data/raw/*/current_unspent.csv",
        ],
        "outputs": outputs,
        "notes": [
            "DRep delegation is voting power, not custody or beneficial ownership.",
            "Genesis trace exposure is deduped by dest_tx_out_id across overlapping ABCDE trace roots.",
            "Profiles are generated for the top DReps as a set to avoid selective one-off framing.",
        ],
    }
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(payload, indent=2) + "\n")


def main() -> None:
    profiles = read_csv(PROFILE_CSV)
    if not profiles:
        raise SystemExit(f"no profiles in {PROFILE_CSV}")
    stake_rows = read_csv(STAKE_BUCKET_CSV)
    age_rows = read_csv(AGE_BUCKET_CSV)
    pool_rows = read_csv(POOL_AFFILIATION_CSV)
    koios_rows = read_csv(KOIOS_CROSSCHECK_CSV) if KOIOS_CROSSCHECK_CSV.exists() else []

    exposure_rows, root_rows, stickiness_rows = build_trace_rollups(profiles)

    write_csv(TRACE_EXPOSURE_CSV, exposure_rows, [
        "query_timestamp_utc",
        "drep_distribution_epoch",
        "rank_overall",
        "profile_class",
        "drep_id_bech32",
        "dedup_current_utxos",
        "dedup_current_stake_credentials",
        "dedup_current_lovelace",
        "dedup_current_ada",
        "root_overlap_summary",
    ])
    write_csv(TRACE_ROOT_EXPOSURE_CSV, root_rows, [
        "query_timestamp_utc",
        "drep_distribution_epoch",
        "rank_overall",
        "profile_class",
        "drep_id_bech32",
        "root_seed_id",
        "latest_stake_credentials_with_current_value",
        "current_utxos",
        "current_lovelace",
        "current_ada",
    ])
    write_csv(TRACE_STICKINESS_CSV, stickiness_rows, [
        "query_timestamp_utc",
        "drep_distribution_epoch",
        "rank_overall",
        "profile_class",
        "drep_id_bech32",
        "root_seed_id",
        "ever_trace_stake_credentials",
        "latest_still_this_drep",
        "latest_moved_away",
        "latest_unknown",
        "latest_still_ratio",
        "current_lovelace_latest_still",
        "current_ada_latest_still",
        "current_lovelace_moved_away",
        "current_ada_moved_away",
    ])
    render_report(profiles, exposure_rows, stake_rows, age_rows, pool_rows, koios_rows)
    build_manifest([
        PROFILE_CSV,
        STAKE_BUCKET_CSV,
        AGE_BUCKET_CSV,
        POOL_AFFILIATION_CSV,
        KOIOS_CROSSCHECK_CSV,
        TRACE_EXPOSURE_CSV,
        TRACE_ROOT_EXPOSURE_CSV,
        TRACE_STICKINESS_CSV,
        REPORT,
    ], profiles)

    print(f"wrote {TRACE_EXPOSURE_CSV.relative_to(ROOT)} rows={len(exposure_rows)}")
    print(f"wrote {TRACE_ROOT_EXPOSURE_CSV.relative_to(ROOT)} rows={len(root_rows)}")
    print(f"wrote {TRACE_STICKINESS_CSV.relative_to(ROOT)} rows={len(stickiness_rows)}")
    print(f"wrote {REPORT.relative_to(ROOT)}")
    print(f"wrote {MANIFEST.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

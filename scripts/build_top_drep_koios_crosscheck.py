#!/usr/bin/env python3
"""Cross-check top registered DRep rows against Koios drep_info."""
from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
PROFILE_CSV = ROOT / "data/small/governance_top_drep_profiles_current.csv"
OUT = ROOT / "data/small/governance_top_drep_koios_crosscheck.csv"
KOIOS_URL = "https://api.koios.rest/api/v1/drep_info"


def read_profiles() -> list[dict[str, str]]:
    with PROFILE_CSV.open(newline="") as f:
        return list(csv.DictReader(f))


def bool_text(value: bool | None) -> str:
    if value is None:
        return ""
    return "true" if value else "false"


def fetch_koios(drep_ids: list[str]) -> tuple[dict[str, dict[str, object]], str]:
    if not drep_ids:
        return {}, ""
    body = json.dumps({"_drep_ids": drep_ids}).encode()
    req = Request(KOIOS_URL, data=body, headers={"Content-Type": "application/json"})
    try:
        with urlopen(req, timeout=30) as resp:
            rows = json.load(resp)
    except Exception as exc:  # noqa: BLE001 - this should degrade, not break rebuilds.
        return {}, f"koios_unavailable: {exc}"
    return {str(row.get("hex", "")).lower(): row for row in rows}, ""


def main() -> None:
    profiles = read_profiles()
    registered = [r for r in profiles if r["profile_class"] == "registered" and r["drep_id_bech32"].startswith("drep1")]
    koios_by_hex, fetch_status = fetch_koios([r["drep_id_bech32"] for r in registered])
    query_timestamp = datetime.now(timezone.utc).replace(tzinfo=None).isoformat(sep=" ")

    fields = [
        "query_timestamp_utc",
        "profile_query_timestamp_utc",
        "rank_overall",
        "profile_class",
        "drep_id_bech32",
        "drep_hash_hex",
        "koios_status",
        "koios_drep_id",
        "koios_active",
        "koios_expires_epoch_no",
        "dbsync_voting_power_lovelace",
        "koios_amount_lovelace",
        "amount_matches_dbsync",
        "dbsync_voting_anchor_url",
        "koios_meta_url",
        "meta_url_matches_dbsync",
        "dbsync_voting_anchor_data_hash_hex",
        "koios_meta_hash",
        "meta_hash_matches_dbsync",
    ]
    rows = []
    for profile in profiles:
        drep_hash_hex = profile.get("drep_hash_hex", "").lower()
        koios = koios_by_hex.get(drep_hash_hex, {})
        if profile["profile_class"] == "system":
            status = "not_applicable"
        elif fetch_status:
            status = fetch_status
        elif koios:
            status = str(koios.get("drep_status") or "returned")
        else:
            status = "missing_from_koios_response"
        amount_match = None
        url_match = None
        hash_match = None
        if koios:
            amount_match = str(koios.get("amount") or "") == profile["voting_power_lovelace"]
            url_match = str(koios.get("meta_url") or "") == profile.get("voting_anchor_url", "")
            hash_match = str(koios.get("meta_hash") or "").lower() == profile.get("voting_anchor_data_hash_hex", "").lower()
        rows.append({
            "query_timestamp_utc": query_timestamp,
            "profile_query_timestamp_utc": profile["query_timestamp_utc"],
            "rank_overall": profile["rank_overall"],
            "profile_class": profile["profile_class"],
            "drep_id_bech32": profile["drep_id_bech32"],
            "drep_hash_hex": profile.get("drep_hash_hex", ""),
            "koios_status": status,
            "koios_drep_id": koios.get("drep_id", "") if koios else "",
            "koios_active": koios.get("active", "") if koios else "",
            "koios_expires_epoch_no": koios.get("expires_epoch_no", "") if koios else "",
            "dbsync_voting_power_lovelace": profile["voting_power_lovelace"],
            "koios_amount_lovelace": koios.get("amount", "") if koios else "",
            "amount_matches_dbsync": bool_text(amount_match),
            "dbsync_voting_anchor_url": profile.get("voting_anchor_url", ""),
            "koios_meta_url": koios.get("meta_url", "") if koios else "",
            "meta_url_matches_dbsync": bool_text(url_match),
            "dbsync_voting_anchor_data_hash_hex": profile.get("voting_anchor_data_hash_hex", ""),
            "koios_meta_hash": koios.get("meta_hash", "") if koios else "",
            "meta_hash_matches_dbsync": bool_text(hash_match),
        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {OUT.relative_to(ROOT)} rows={len(rows)}")


if __name__ == "__main__":
    main()

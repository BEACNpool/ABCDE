#!/usr/bin/env python3
"""Venue catalog and open-position merge for the match scoreboard.

Logos on https://beacnpool.github.io/ABCDE/match.html are data-driven: a mark
renders only when an agent actually has an open position with that protocol.
The page is unofficial and unsponsored — tagging a protocol on a post is a
choice at post time, not a partnership.

New DeFi types: pin the venue here (script hash and/or receipt policy) AND drop
its mark in ``web/dist/match-venues/``, OR write an overlay JSON the snapshot
job already reads. Overlay venues may ship a ``logo`` path or a data URI so a
new protocol can appear without waiting on a catalog edit.

Overlay search order (first file that exists):

  1. $MATCH_POSITIONS_OVERLAY
  2. <repo>/web/dist/data/match_positions.overlay.json
  3. ~/.openclaw/workspace/state/beacnbot/match_positions.overlay.json
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

# Minswap V2 order script. An order address is this hash + the orderer's stake
# credential. Same pin as match_snapshot.py — keep them identical.
MINSWAP_ORDER_SCRIPT = "c3e28c36c3447315ba5a56f33da6a6ddc1770a876a8d9f0cb3a97c4c"

# Liqwid V2 qToken minting policies, live GraphQL 2026-08-30. Detect by policy
# only (hexName is empty on every current market). Refresh when a new market
# is listed; overlay can add a policy without a code change.
LIQWID_RECEIPT_POLICIES = (
    "a04ce7a52545e5e33c2867e148898d9e667a69602285f6a1298f9d68",  # ADA
    "d753e0d193680fe32710379d3a1ec48087ce94f3831505b922c2894b",  # AGIX
    "f72166e9fac8297aeb553c19ffab14f51ae271c2cb26783ba289a3a5",  # wanBTC
    "dd55119962ca550cdd4219999b9e6d25fc9128f96c7dcb5e485286eb",  # COPI
    "8996bb07509defe0be6f0c39845a736b266c85a70d87ebfb66454a78",  # wanDAI
    "6df63e2fdde8b2c3b3396265b0cc824aa4fb999396b1c154280f6b0c",  # DJED
    "b122b2fc62557df9c3fd0b5c62a4b2c970a0d711560e0a8dd7b264f3",  # rsERG
    "5f42994532b04f9f5bd4141c69364c5b7d33c85036146ee321799702",  # wanETH
    "85fa65407b5321fa0e2ef9a3ec98e12a00c35871d7a620be3132003c",  # wanEURC
    "f60b7232837203d335cd77494d25c1cc0b218b9a8f3459730c521d13",  # IAG
    "d15c36d6dec655677acb3318294f116ce01d8d9def3cc54cdd78909b",  # iUSD
    "3883e3e6a24e092d4c14e757fa8ef5c887853060def087d6cf5603f5",  # LQ
    "a4430a085f45bca6399bec6bd7514eb8c2fce1ed75c7554739cfc32b",  # MIN
    "c45fa8aefc662c003a32be67f6a4652d8ce56bd9e54d7696efd40c86",  # NIGHT
    "6f7d8e31d9256ec27f35d25659dd053cfec098032a5669b2b56798d0",  # POL
    "b8a327951d579d3537ea175078256bdf9f9899b5387b099d0b58f066",  # wanPYUSD
    "e1ff3557106fe13042ba0f772af6a2e43903ccfaaf03295048882c93",  # SHEN
    "4e8c49d610335d139ad7711e0f50315006e29b5221da531e365b4ef8",  # SNEK
    "7cc27c4d862d0d8c7ded84405836f275c921a5a73f2e0d4f46802013",  # SNEK2
    "7a35cf17f7d4fc14e9b5ba99cf9be338d0e05a9df3841de767728ae5",  # SNEK-ADA
    "c0b2cfe96c71a73447011a0b6195eee756fe1747dcf06579b69564bb",  # SNEK-USDCx
    "12c8a522ca40065bc742b2d9733338a67e6ee7baa7adb73291a4222f",  # STRIKE
    "7cc5b5e85b03b9dc18ee93162a13a911a5bedad39053506d669465e8",  # STRIKE-ADA
    "6907b42c607019522d93701d8bf4377e13e78a2dfcf17764118902fb",  # STRIKE-USDCx
    "aa280c98c5b07fdfc8d7a93fb5ba84510b421388e4a18e16efa8eb5f",  # USDA
    "aebcb6eaba17dea962008a9d693e39a3160b02b5b89b1c83e537c599",  # wanUSDC
    "d3ff4ac09b0978b1ef7f830fd04d79c4246b53b8bcb08108f4ac5d98",  # USDCx
    "2dbe1daa1522e5640331909fbe7458e082fe22cbc047e3c7575fcc8b",  # LPS-USDCx-USDM
    "9e00df0615de0a7b121a7f961d43e23165b8e81b64786c6eb708d370",  # USDM
    "fcd2d1b8a86cd6dda70553f17e67ba36f8ab0090b5ffbbfa8b2bb8d1",  # LPM-USDM-USDA
    "7a4d45e6b4e6835c4cea3968f291fab3704949cfd2f2dc1997c4eeec",  # wanUSDT
    "f2636c8280e49e7ed7a7b1151341130989631b45a08d1b320f016981",  # WMT
)

LIQWID_MARKET_BY_POLICY = {
    "a04ce7a52545e5e33c2867e148898d9e667a69602285f6a1298f9d68": "ADA",
    "d753e0d193680fe32710379d3a1ec48087ce94f3831505b922c2894b": "AGIX",
    "f72166e9fac8297aeb553c19ffab14f51ae271c2cb26783ba289a3a5": "wanBTC",
    "dd55119962ca550cdd4219999b9e6d25fc9128f96c7dcb5e485286eb": "COPI",
    "8996bb07509defe0be6f0c39845a736b266c85a70d87ebfb66454a78": "wanDAI",
    "6df63e2fdde8b2c3b3396265b0cc824aa4fb999396b1c154280f6b0c": "DJED",
    "b122b2fc62557df9c3fd0b5c62a4b2c970a0d711560e0a8dd7b264f3": "rsERG",
    "5f42994532b04f9f5bd4141c69364c5b7d33c85036146ee321799702": "wanETH",
    "85fa65407b5321fa0e2ef9a3ec98e12a00c35871d7a620be3132003c": "wanEURC",
    "f60b7232837203d335cd77494d25c1cc0b218b9a8f3459730c521d13": "IAG",
    "d15c36d6dec655677acb3318294f116ce01d8d9def3cc54cdd78909b": "iUSD",
    "3883e3e6a24e092d4c14e757fa8ef5c887853060def087d6cf5603f5": "LQ",
    "a4430a085f45bca6399bec6bd7514eb8c2fce1ed75c7554739cfc32b": "MIN",
    "c45fa8aefc662c003a32be67f6a4652d8ce56bd9e54d7696efd40c86": "NIGHT",
    "6f7d8e31d9256ec27f35d25659dd053cfec098032a5669b2b56798d0": "POL",
    "b8a327951d579d3537ea175078256bdf9f9899b5387b099d0b58f066": "wanPYUSD",
    "e1ff3557106fe13042ba0f772af6a2e43903ccfaaf03295048882c93": "SHEN",
    "4e8c49d610335d139ad7711e0f50315006e29b5221da531e365b4ef8": "SNEK",
    "7cc27c4d862d0d8c7ded84405836f275c921a5a73f2e0d4f46802013": "SNEK2",
    "7a35cf17f7d4fc14e9b5ba99cf9be338d0e05a9df3841de767728ae5": "SNEK-ADA",
    "c0b2cfe96c71a73447011a0b6195eee756fe1747dcf06579b69564bb": "SNEK-USDCx",
    "12c8a522ca40065bc742b2d9733338a67e6ee7baa7adb73291a4222f": "STRIKE",
    "7cc5b5e85b03b9dc18ee93162a13a911a5bedad39053506d669465e8": "STRIKE-ADA",
    "6907b42c607019522d93701d8bf4377e13e78a2dfcf17764118902fb": "STRIKE-USDCx",
    "aa280c98c5b07fdfc8d7a93fb5ba84510b421388e4a18e16efa8eb5f": "USDA",
    "aebcb6eaba17dea962008a9d693e39a3160b02b5b89b1c83e537c599": "wanUSDC",
    "d3ff4ac09b0978b1ef7f830fd04d79c4246b53b8bcb08108f4ac5d98": "USDCx",
    "2dbe1daa1522e5640331909fbe7458e082fe22cbc047e3c7575fcc8b": "LPS-USDCx-USDM",
    "9e00df0615de0a7b121a7f961d43e23165b8e81b64786c6eb708d370": "USDM",
    "fcd2d1b8a86cd6dda70553f17e67ba36f8ab0090b5ffbbfa8b2bb8d1": "LPM-USDM-USDA",
    "7a4d45e6b4e6835c4cea3968f291fab3704949cfd2f2dc1997c4eeec": "wanUSDT",
    "f2636c8280e49e7ed7a7b1151341130989631b45a08d1b320f016981": "WMT",
}

POSITION_DISCLAIMER = (
    "Unofficial and unsponsored. Logos appear only when an agent has an open "
    "position with that protocol."
)

# Public fields copied into match.json. Script hashes and policies stay here.
_PUBLIC_KEYS = ("id", "name", "product", "kind", "x", "url", "logo")


def _venue(
    vid: str, name: str, *, product: str, kind: str, x: str, url: str, logo: str,
    order_script_hashes: tuple[str, ...] = (),
    receipt_policies: tuple[str, ...] = (),
) -> dict[str, Any]:
    return {
        "id": vid, "name": name, "product": product, "kind": kind,
        "x": x, "url": url, "logo": logo,
        "order_script_hashes": list(order_script_hashes),
        "receipt_policies": list(receipt_policies),
    }


BASE_VENUES: dict[str, dict[str, Any]] = {
    "minswap_v2": _venue(
        "minswap_v2", "Minswap", product="V2", kind="dex_order",
        x="@MinswapDEX", url="https://minswap.org",
        logo="match-venues/minswap.svg",
        order_script_hashes=(MINSWAP_ORDER_SCRIPT,),
    ),
    "liqwid_v2": _venue(
        "liqwid_v2", "Liqwid", product="V2", kind="lending",
        x="@liqwidfinance", url="https://liqwid.finance",
        logo="match-venues/liqwid.png",
        receipt_policies=LIQWID_RECEIPT_POLICIES,
    ),
    "cswap_v1": _venue(
        "cswap_v1", "CSwap", product="V1", kind="dex_order",
        x="@CswapDEX", url="https://www.cswap.fi",
        logo="match-venues/cswap.png",
        # No official validator pin yet. Overlay or a later script-hash pin
        # is what makes a CSwap order show up.
    ),
}


def overlay_paths(root: Path | None = None) -> list[Path]:
    root = root or ROOT
    env = os.environ.get("MATCH_POSITIONS_OVERLAY", "").strip()
    paths: list[Path] = []
    if env:
        paths.append(Path(env).expanduser())
    paths.append(root / "web" / "dist" / "data" / "match_positions.overlay.json")
    paths.append(Path.home() / ".openclaw" / "workspace" / "state" / "beacnbot"
                 / "match_positions.overlay.json")
    return paths


def load_overlay(paths: list[Path] | None = None) -> dict[str, Any]:
    """Return the first readable overlay, or an empty schema. Never raises."""
    for path in (paths or overlay_paths()):
        try:
            if not path.is_file():
                continue
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(data, dict):
            continue
        data.setdefault("venues", {})
        data.setdefault("positions", [])
        data["_path"] = str(path)
        return data
    return {"venues": {}, "positions": []}


def merge_catalog(overlay: dict[str, Any] | None = None) -> dict[str, dict[str, Any]]:
    catalog = {k: dict(v) for k, v in BASE_VENUES.items()}
    extra = (overlay or {}).get("venues") or {}
    if not isinstance(extra, dict):
        return catalog
    for vid, raw in extra.items():
        if not isinstance(vid, str) or not vid.strip() or not isinstance(raw, dict):
            continue
        vid = vid.strip()
        base = catalog.get(vid, {"id": vid, "name": vid, "kind": "overlay",
                                 "product": "", "x": "", "url": "", "logo": "",
                                 "order_script_hashes": [], "receipt_policies": []})
        merged = dict(base)
        for key in ("name", "product", "kind", "x", "url", "logo"):
            val = raw.get(key)
            if isinstance(val, str) and val.strip():
                merged[key] = val.strip()
        for key in ("order_script_hashes", "receipt_policies"):
            val = raw.get(key)
            if isinstance(val, list) and all(isinstance(x, str) and x for x in val):
                merged[key] = list(dict.fromkeys([*(merged.get(key) or []), *val]))
        merged["id"] = vid
        catalog[vid] = merged
    return catalog


def indexes(catalog: dict[str, dict[str, Any]]) -> tuple[dict[str, str], dict[str, str]]:
    """script_hash -> venue id, receipt_policy -> venue id."""
    by_script: dict[str, str] = {}
    by_policy: dict[str, str] = {}
    for vid, v in catalog.items():
        for h in v.get("order_script_hashes") or []:
            if isinstance(h, str) and h:
                by_script[h.lower()] = vid
        for p in v.get("receipt_policies") or []:
            if isinstance(p, str) and p:
                by_policy[p.lower()] = vid
    return by_script, by_policy


def venue_public(v: dict[str, Any]) -> dict[str, Any]:
    return {k: v.get(k) or "" for k in _PUBLIC_KEYS}


def _qty(raw) -> float:
    try:
        return int(raw) / 1e6
    except (TypeError, ValueError):
        return 0.0


def position_from_orders(venue_id: str, *, count: int, ada: float, usdm: float,
                         source: str = "chain") -> dict[str, Any] | None:
    if count <= 0 and ada <= 0 and usdm <= 0:
        return None
    unit = "order" if count == 1 else "orders"
    return {
        "venue": venue_id,
        "kind": "dex_order",
        "label": f"{count} unfilled {unit}",
        "count": int(count),
        "ada": round(ada, 6),
        "usdm": round(usdm, 6),
        "source": source,
    }


LIQWID_VALUATION_CAVEAT = (
    "Valued at Liqwid's own posted exchangeRate and oracle price. This is a "
    "live protocol mark, not an independently executed exit -- a real "
    "redemption still pays network/batcher fees and can be delayed by "
    "batching or thin market liquidity."
)


def price_receipt_holdings(
    holdings: list[tuple[str, float]],
    rates: dict[str, dict[str, float]] | None,
) -> tuple[float, float, bool]:
    """(ada, usdm_eq, fully_priced) for qToken holdings, from each market's
    live exchangeRate and underlying asset price (both reported by the
    protocol itself -- never a guess). ADA-market receipts convert to ADA;
    every other market converts to a USD amount, folded into usdm_eq because
    the scoreboard already treats USDM as USD marked 1:1. A market missing
    from ``rates`` (feed down, or a market this catalog does not yet map)
    stays unpriced rather than assumed to be worth zero -- callers must
    surface that, not report it as a real zero.
    """
    if not rates:
        return 0.0, 0.0, False
    ada = usdm_eq = 0.0
    fully_priced = True
    for market, qty in holdings:
        rate = rates.get(market)
        if not rate:
            fully_priced = False
            continue
        underlying = qty * rate["exchange_rate"]
        if market == "ADA":
            ada += underlying
        else:
            usdm_eq += underlying * rate["price_usd"]
    return ada, usdm_eq, fully_priced


def position_from_receipts(venue_id: str, holdings: list[tuple[str, float]],
                           source: str = "chain",
                           rates: dict[str, dict[str, float]] | None = None,
                           ) -> dict[str, Any] | None:
    holdings = [(m, q) for m, q in holdings if q > 0]
    if not holdings:
        return None
    ada, usdm_eq, fully_priced = price_receipt_holdings(holdings, rates)
    priced = bool(rates)
    bits = []
    for m, q in holdings:
        qty_str = f"{q:.4f}".rstrip("0").rstrip(".")
        entry = f"{qty_str} q{m}"
        rate = (rates or {}).get(m)
        if rate:
            underlying = q * rate["exchange_rate"]
            entry += f" (~{underlying:.2f} {m}, live rate)"
        bits.append(entry)
    pos: dict[str, Any] = {
        "venue": venue_id,
        "kind": "supply",
        "label": ", ".join(bits),
        "count": len(holdings),
        "ada": round(ada, 6),
        "usdm": round(usdm_eq, 6),
        "source": source,
        "markets": [m for m, _ in holdings],
        "priced": priced,
    }
    if priced:
        pos["fully_priced"] = fully_priced
        pos["valuation_note"] = LIQWID_VALUATION_CAVEAT
    return pos


def receipts_in_utxos(utxos: list[dict[str, Any]], by_policy: dict[str, str],
                      venue_id: str) -> dict[str, float]:
    """policy-market name -> quantity, for one venue."""
    found: dict[str, float] = {}
    for u in utxos or []:
        for asset in u.get("asset_list") or []:
            policy = str(asset.get("policy_id") or "").lower()
            if by_policy.get(policy) != venue_id:
                continue
            qty = _qty(asset.get("quantity"))
            if qty <= 0:
                continue
            market = LIQWID_MARKET_BY_POLICY.get(policy, policy[:8])
            found[market] = found.get(market, 0.0) + qty
    return found


def overlay_positions_for(overlay: dict[str, Any], agent_id: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    rows = overlay.get("positions") or []
    if not isinstance(rows, list):
        return out
    for raw in rows:
        if not isinstance(raw, dict):
            continue
        if raw.get("agent") != agent_id:
            continue
        venue = raw.get("venue")
        if not isinstance(venue, str) or not venue.strip():
            continue
        count = raw.get("count", 1)
        try:
            count = int(count)
        except (TypeError, ValueError):
            count = 1
        ada = float(raw.get("ada") or 0)
        usdm = float(raw.get("usdm") or 0)
        if count <= 0 and ada <= 0 and usdm <= 0 and not raw.get("label"):
            continue
        kind = raw.get("kind") if isinstance(raw.get("kind"), str) else "overlay"
        label = raw.get("label") if isinstance(raw.get("label"), str) and raw["label"].strip() \
            else f"open {kind.replace('_', ' ')}"
        row = {
            "venue": venue.strip(),
            "kind": kind,
            "label": label.strip(),
            "count": max(count, 1),
            "ada": round(ada, 6),
            "usdm": round(usdm, 6),
            "source": "overlay",
        }
        ref = raw.get("ref")
        if isinstance(ref, str) and ref.strip():
            row["ref"] = ref.strip()
        out.append(row)
    return out


def merge_positions(chain: list[dict[str, Any]], overlay: list[dict[str, Any]]
                    ) -> list[dict[str, Any]]:
    """Overlay adds a venue the chain missed; same venue prefers chain numbers."""
    by_id: dict[str, dict[str, Any]] = {}
    for row in chain:
        if row and row.get("venue"):
            by_id[row["venue"]] = dict(row)
    for row in overlay:
        vid = row.get("venue")
        if not vid:
            continue
        if vid in by_id:
            # Chain already proved the position. Keep chain sizes; overlay may
            # supply a clearer label.
            if row.get("label") and by_id[vid].get("source") == "chain":
                if row.get("kind") and row["kind"] not in {"overlay", by_id[vid].get("kind")}:
                    pass
            continue
        by_id[vid] = dict(row)
    return list(by_id.values())


def used_venues(catalog: dict[str, dict[str, Any]],
                positions_by_agent: dict[str, list[dict[str, Any]]]
                ) -> dict[str, dict[str, Any]]:
    """Only venues that currently have a position — so unused logos never ship
    as 'open'. The page still has the files on disk for the next position."""
    used: dict[str, dict[str, Any]] = {}
    for rows in positions_by_agent.values():
        for row in rows:
            vid = row.get("venue")
            if not vid:
                continue
            v = catalog.get(vid)
            if not v:
                v = {"id": vid, "name": vid, "product": "", "kind": row.get("kind") or "",
                     "x": "", "url": "", "logo": ""}
            used[vid] = venue_public(v)
    return used

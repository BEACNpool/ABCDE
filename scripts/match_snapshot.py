#!/usr/bin/env python3
"""Build the data layer for the BEACN vs grokbot live scoreboard.

Two AI agents were funded with identical stakes on Cardano mainnet on
2026-08-29 and told to beat each other. This script reconstructs both books
from chain, scores them under the scoreboard both agents agreed to, and writes
``web/dist/match.json`` for the static page to render. There is no server: the
page reads this file and nothing else.

Everything here comes from Koios (public, keyless) plus one price feed. Nothing
is read from either agent's own claims about itself.

Run:  python3 scripts/match_snapshot.py [--out PATH] [--quiet]

--------------------------------------------------------------------------
The traps this script exists to not fall into. Each one was hit for real.
--------------------------------------------------------------------------
1. Koios ``tx_info`` returns NO inputs unless you pass ``_inputs: true``. It
   fails SILENTLY with an empty list, so every sender resolves to nobody.
   Same for ``_metadata`` and ``_assets``.
2. USDM IS ALREADY DENOMINATED IN USD. Never divide a stablecoin balance by
   the ADA/USDM rate to "convert it to dollars" -- that valued 47.21 USDM at
   $9.52 and caused a real 180 ADA mistransfer. To express USDM in ADA,
   MULTIPLY by ADA-per-USDM. Every cross-asset total below is computed in BOTH
   denominations and asserted to agree.
3. Sixteen different mainnet assets are named ``0014df105553444d`` ("USDM").
   Always filter on the full policy id. Never match on the token name.
4. The 2 ADA stake-key deposit is refundable and is still the agent's asset.
   Count it for BOTH agents or neither. It is READ FROM CHAIN per agent here
   (``account_info.deposit``) rather than hardcoded, so the symmetry cannot
   drift.
5. Do not fabricate a price. If the feed is unreachable the ADA and USDM legs
   are reported separately and the USD mark is marked unavailable.
6. An agent is not one address. BEACN spent from an enterprise address before
   it registered a stake key and from a base address after, and funds sitting
   in an unfilled DEX order still belong to it. Books are reconstructed by
   PAYMENT CREDENTIAL plus any script address carrying the agent's own stake
   credential -- never by a single bech32 string.
7. Fees are attributed only where the agent's own payment credential funded
   the transaction. A DEX batcher pays the fee on the fill transaction; that
   fee is the batcher's, not the agent's.
8. Moving USDM into a Liqwid supply is not a loss. It swaps wallet USDM for a
   qUSDM receipt, and that receipt is priced back into the score via Liqwid's
   own live exchangeRate + oracle price (fetch_liqwid_rates). This was
   discovered 2026-09-02: grokbot supplied its whole starting USDM sleeve to
   Liqwid and the published score dropped ~402 ADA-eq to zero because the
   receipt was (by design, at the time) never marked. If the Liqwid feed is
   unreachable, the receipt stays unpriced exactly as before this fix -- never
   fabricate a rate, and never let a feed outage look like a real zero.
   ⚠️ 2026-09-03: this exact fix was applied uncommitted on 2026-09-02, then
   silently wiped by a routine `reset: moving to origin/main` on this working
   tree, and the bug ran live on the public page for ~8 hours before being
   caught and reapplied+committed. NEVER leave a fix to this file (or
   match_positions.py) as an uncommitted working-tree edit -- commit and push
   to origin/main in the same sitting, or the next reset erases it silently.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from match_positions import (
    LIQWID_MARKET_BY_POLICY,
    MINSWAP_ORDER_SCRIPT,
    POSITION_DISCLAIMER,
    indexes,
    load_overlay,
    merge_catalog,
    merge_positions,
    overlay_positions_for,
    position_from_orders,
    position_from_receipts,
    receipts_in_utxos,
    used_venues,
)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "web" / "dist" / "data" / "match.json"
DEFAULT_HISTORY = ROOT / "web" / "dist" / "data" / "match_history.json"

KOIOS = "https://api.koios.rest/api/v1"
COINGECKO = ("https://api.coingecko.com/api/v3/simple/price"
             "?ids=cardano&vs_currencies=usd")
# 5-minute ADA/USD samples for the last 24h. Used only to BACKFILL the lead
# history before live polling started -- an independent market feed, never a
# rate implied by either agent's own trades.
COINGECKO_CHART = ("https://api.coingecko.com/api/v3/coins/cardano/market_chart"
                   "?vs_currency=usd&days=1")
LIQWID_GRAPHQL = "https://v2.api.liqwid.finance/graphql"
LIQWID_RATES_QUERY = json.dumps({"query": """
query Markets {
  liqwid { data { markets(input: {perPage: 100}) { results {
    displayName exchangeRate asset { price }
  } } } }
}
"""})

# Moneta USDM. Trap 3: the name is ambiguous, the policy is not.
USDM_POLICY = "c48cbb3d5e57ed56e276bc45f99ab39abe94e6cd7ac39fb402da47ad"
USDM_NAME_HEX = "0014df105553444d"

# Minswap V2 order script lives in match_positions.MINSWAP_ORDER_SCRIPT — an
# order address is that hash + the ORDERER'S OWN stake credential.

EXPLORER_ADDR = "https://cardanoscan.io/address/"
EXPLORER_TX = "https://cardanoscan.io/transaction/"
EXPLORER_POOL = "https://cardanoscan.io/pool/"

AGENTS = [
    {
        "id": "beacn",
        "name": "BEACN",
        "engine": "Codex",
        "payment_cred": "570d2bf8e4f649a70d38ce0a50693ec4d0e2946341c0e452f495cf67",
        "address": ("addr1q9ts62lcunmynfcd8r8q55rf8mzdpc55vdqupezj7j2u7e69ujeu9gg"
                    "e3h9ffh8r95lsqfyzejra4sd43njhvsymsemsdergt3"),
        "stake_address": "stake1u9z7fv7z5yvcmj55mn3j60cqyjpvep76cx6ceetkgzdcvacqgqkle",
        # Belt: discovery from tx outputs can miss a stake_addr field. This is
        # the Minswap V2 order address (script + our stake) holding STOP/LIMIT.
        "known_order_addresses": [
            "addr1z8p79rpkcdz8x9d6tft0x0dx5mwuzac2sa4gm8cvkw5hcnz9ujeu9gge3h9ffh8r95lsqfyzejra4sd43njhvsymsemsppzjm5",
        ],
    },
    {
        "id": "grokbot",
        "name": "grokbot",
        "engine": "Grok",
        "payment_cred": "846d6074a250739cf308e49949f6f3cadd2b8cf7f63622d2281c41e1",
        "address": ("addr1qxzx6cr55fg8888nprjfjj0k709d62uv7lmrvgkj9qwyrcvk8ppx"
                    "w7knmq5wclh4fz77tjfpg44yn0mwngw6qyg8ghrqa0epfs"),
        "stake_address": "stake1uxtrssn80tfas28v0m653009eys526jfhahf58dqzyr5t3snt4wdm",
    },
]

# Both books were set to this at the first levelling. Kept only to identify the
# transactions in the move log; every number on the site is recomputed.
T0_TX = "dd6044785447a37ad79df29993ce12805810fcd40ec3338a75a76dd058e60be7"
LEVEL_TX = "91bc070637b33c2fb392bf3ea1defca8dd52d595792ae30c0721bef29e5c7acd"

# NOTE: this file is public. The only addresses hardcoded here are the two
# agents' own, which the match publishes deliberately. The wallet that funded
# them is a private third party -- it is described structurally ("an external
# wallet") and never named, even though a reader following a transaction hash
# to an explorer can of course see it there.


# --------------------------------------------------------------------------
# transport
# --------------------------------------------------------------------------
def _curl(args: list[str], timeout: int = 45) -> str:
    r = subprocess.run(["curl", "-s", "--max-time", str(timeout), *args],
                       capture_output=True, text=True)
    return r.stdout


def koios(endpoint: str, body: dict, tries: int = 3):
    """POST to Koios and return parsed JSON, retrying transient failures."""
    last = ""
    for attempt in range(tries):
        out = _curl(["-X", "POST", f"{KOIOS}/{endpoint}",
                     "-H", "Content-Type: application/json",
                     "-d", json.dumps(body)])
        try:
            parsed = json.loads(out)
        except json.JSONDecodeError:
            last = out[:200]
        else:
            if isinstance(parsed, list):
                return parsed
            last = str(parsed)[:200]
        time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"koios/{endpoint} failed after {tries} tries: {last}")


def lovelace(x) -> float:
    return int(x or 0) / 1e6


def usdm_of(utxo) -> float:
    """USDM in one UTxO/output. Trap 3: match the full policy, never the name."""
    return sum(int(a["quantity"]) for a in (utxo.get("asset_list") or [])
               if a.get("policy_id") == USDM_POLICY) / 1e6


# --------------------------------------------------------------------------
# price
# --------------------------------------------------------------------------
def get_price() -> dict:
    """Live ADA/USD. Trap 5: on failure this returns unavailable, never a guess.

    Deliberately does NOT fall back to a rate implied by either agent's own
    swaps. You cannot score a trader using the prices they transacted at.
    """
    out = _curl([COINGECKO], timeout=12)
    try:
        usd = float(json.loads(out)["cardano"]["usd"])
        if usd <= 0:
            raise ValueError("non-positive price")
    except Exception as exc:  # noqa: BLE001 - any failure means "no mark"
        return {"available": False, "reason": str(exc)[:120],
                "source": "CoinGecko simple/price (unreachable)"}
    return {
        "available": True,
        "usd_per_ada": usd,
        # USDM is a USD stablecoin marked 1:1, so ADA-per-USDM is 1/(ADA in USD).
        "ada_per_usdm": 1.0 / usd,
        "source": "CoinGecko simple/price?ids=cardano&vs_currencies=usd",
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def fetch_liqwid_rates(timeout: int = 12) -> dict[str, dict[str, float]] | None:
    """Live {market displayName: {exchange_rate, price_usd}} from Liqwid's own
    GraphQL API, or None if the feed is unreachable/empty.

    Trap 5 applies here too: never fabricate a rate. An unreachable feed means
    every qToken holding stays unpriced (as it always was before this
    adapter) -- callers must say so, never silently show it as a real zero.
    """
    out = _curl(["-X", "POST", LIQWID_GRAPHQL,
                "-H", "Content-Type: application/json",
                "-d", LIQWID_RATES_QUERY], timeout=timeout)
    try:
        payload = json.loads(out)
        if payload.get("errors"):
            raise RuntimeError(str(payload["errors"])[:200])
        results = payload["data"]["liqwid"]["data"]["markets"]["results"]
        rates: dict[str, dict[str, float]] = {}
        for m in results:
            name = m.get("displayName")
            rate = m.get("exchangeRate")
            price = (m.get("asset") or {}).get("price")
            if not name or rate is None or price is None:
                continue
            rates[name] = {"exchange_rate": float(rate), "price_usd": float(price)}
        if not rates:
            raise ValueError("empty market list")
        return rates
    except Exception:  # noqa: BLE001 - any failure means "no rates", never a guess
        return None


def mark_book(ada_total: float, usdm_total: float, usd_per_ada: float) -> dict:
    """Mark one book in both score denominations from one independent price.

    USDM is already denominated in dollars. Multiplying it by ADA-per-USDM is
    load-bearing; dividing by that rate recreates the conversion error this
    scoreboard was built to prevent.
    """
    if not all(math.isfinite(v) for v in (ada_total, usdm_total, usd_per_ada)):
        raise ValueError("book values and usd_per_ada must be finite")
    if usd_per_ada <= 0:
        raise ValueError("usd_per_ada must be positive")
    ada_per_usdm = 1.0 / usd_per_ada
    score_ada = ada_total + usdm_total * ada_per_usdm
    score_usd = ada_total * usd_per_ada + usdm_total
    return {
        "ada_per_usdm": ada_per_usdm,
        "score_ada_eq": score_ada,
        "score_usd": score_usd,
    }


def equalized_performance(score_ada_eq: float, baseline_ada_eq: float,
                          usd_per_ada: float) -> dict:
    """Return performance from the match's one shared ADA-equivalent start."""
    if not all(math.isfinite(v) for v in
               (score_ada_eq, baseline_ada_eq, usd_per_ada)):
        raise ValueError("score, baseline and usd_per_ada must be finite")
    if baseline_ada_eq <= 0:
        raise ValueError("baseline_ada_eq must be positive")
    if usd_per_ada <= 0:
        raise ValueError("usd_per_ada must be positive")
    delta = score_ada_eq - baseline_ada_eq
    return {
        "ada_eq": delta,
        "pct": 100.0 * delta / baseline_ada_eq,
        "usd_at_current_mark": delta * usd_per_ada,
    }


# --------------------------------------------------------------------------
# books
# --------------------------------------------------------------------------
def order_scripts(agent: dict, txs: list[dict]) -> dict[str, str]:
    """Script addresses holding this agent's funds mid-trade, mapped to hash.

    Trap 6: a DEX order address is the order script hash + the agent's OWN
    stake credential. Funds parked there between order and fill are still the
    agent's book. A snapshot taken in that window would otherwise show ~390 ADA
    vanishing. Known Minswap addresses are pinned because discovery from tx
    outputs can miss a stake_addr field.
    """
    found: dict[str, str] = {}
    for tx in txs:
        for out in tx.get("outputs") or []:
            pa = out.get("payment_addr") or {}
            if (out.get("stake_addr") == agent["stake_address"]
                    and pa.get("cred") and pa["cred"] != agent["payment_cred"]):
                found[pa["bech32"]] = pa["cred"]
    for addr in agent.get("known_order_addresses") or []:
        found.setdefault(addr, MINSWAP_ORDER_SCRIPT)
    return found


def read_book(agent: dict, scripts: dict[str, str], by_script: dict[str, str],
              by_policy: dict[str, str],
              liqwid_rates: dict[str, dict[str, float]] | None = None) -> dict:
    """Current holdings, from chain, across every address form the agent uses."""
    utxos = koios("credential_utxos",
                  {"_payment_credentials": [agent["payment_cred"]], "_extended": True})
    ada = sum(lovelace(u["value"]) for u in utxos)
    usdm = sum(usdm_of(u) for u in utxos)

    flight_ada = flight_usdm = 0.0
    open_orders = 0
    by_venue: dict[str, dict[str, float]] = {}
    for addr, script in scripts.items():
        info = koios("address_info", {"_addresses": [addr]})
        vid = by_script.get((script or "").lower())
        for row in info:
            for u in row.get("utxo_set") or []:
                flight_ada += lovelace(u["value"])
                flight_usdm += usdm_of(u)
                open_orders += 1
                if not vid:
                    continue
                bucket = by_venue.setdefault(vid, {"count": 0, "ada": 0.0, "usdm": 0.0})
                bucket["count"] += 1
                bucket["ada"] += lovelace(u["value"])
                bucket["usdm"] += usdm_of(u)

    positions: list[dict] = []
    for vid, agg in by_venue.items():
        pos = position_from_orders(vid, count=int(agg["count"]),
                                   ada=agg["ada"], usdm=agg["usdm"])
        if pos:
            positions.append(pos)

    # Receipt tokens (Liqwid qTokens today, more later) live on the agent's
    # own payment credential. Liqwid receipts ARE marked into the score below,
    # using Liqwid's own live exchangeRate + oracle price (never a guess) --
    # see position_from_receipts/price_receipt_holdings. Any other receipt
    # venue without a rate source stays unpriced, same as before this adapter.
    existing = {p["venue"]: p for p in positions}
    receipt_ada = receipt_usdm_eq = 0.0
    receipts_fully_priced = True
    for vid in sorted(set(by_policy.values())):
        found = receipts_in_utxos(utxos, by_policy, vid)
        rates = liqwid_rates if vid == "liqwid_v2" else None
        pos = position_from_receipts(vid, list(found.items()), rates=rates)
        if not pos:
            continue
        receipt_ada += pos["ada"]
        receipt_usdm_eq += pos["usdm"]
        if pos.get("priced") and not pos.get("fully_priced", True):
            receipts_fully_priced = False
        if vid in existing:
            existing[vid]["label"] = existing[vid]["label"] + "; " + pos["label"]
            existing[vid]["kind"] = "mixed"
        else:
            positions.append(pos)

    acct = koios("account_info", {"_stake_addresses": [agent["stake_address"]]})
    acct = acct[0] if acct else {}
    return {
        "ada": ada,
        "usdm": usdm,
        "in_flight_ada": flight_ada,
        "in_flight_usdm": flight_usdm,
        "receipt_ada": receipt_ada,
        "receipt_usdm_eq": receipt_usdm_eq,
        "receipts_fully_priced": receipts_fully_priced,
        "open_orders": open_orders,
        "positions": positions,
        # Trap 4: read per agent, so it is counted for both or neither by
        # construction rather than by remembering to.
        "deposit": lovelace(acct.get("deposit")),
        "rewards": lovelace(acct.get("rewards_available")),
        "rewards_lifetime": lovelace(acct.get("rewards")),
        "stake_status": acct.get("status"),
        "pool": acct.get("delegated_pool"),
        "utxo_count": len(utxos),
    }


# --------------------------------------------------------------------------
# move log
# --------------------------------------------------------------------------
def owned(node: dict, agent: dict, order_addrs: set[str]) -> bool:
    pa = node.get("payment_addr") or {}
    return pa.get("cred") == agent["payment_cred"] or pa.get("bech32") in order_addrs


def find_pool(tx: dict, agent_usdm_delta: float):
    """The AMM pool in a swap: present on both sides, USDM moving the other way.

    Distinguishes the pool from the batcher, which is also present on both
    sides but whose stablecoin balance does not move.
    """
    ins = {}
    for i in tx.get("inputs") or []:
        b = i["payment_addr"]["bech32"]
        a, u = ins.get(b, (0.0, 0.0))
        ins[b] = (a + lovelace(i["value"]), u + usdm_of(i))
    outs = {}
    for o in tx.get("outputs") or []:
        b = o["payment_addr"]["bech32"]
        a, u = outs.get(b, (0.0, 0.0))
        outs[b] = (a + lovelace(o["value"]), u + usdm_of(o))
    best = None
    for addr in set(ins) & set(outs):
        d_usdm = outs[addr][1] - ins[addr][1]
        if abs(d_usdm) < 1e-9:
            continue
        # A shared batch moves the whole pool for several orderers. Only an
        # exact opposite USDM delta can identify this agent's single swap.
        if abs(agent_usdm_delta + d_usdm) < 1e-6:
            d_ada = outs[addr][0] - ins[addr][0]
            if best is None or abs(d_usdm) > abs(best[2]):
                best = (addr, d_ada, d_usdm)
    return best


MINSWAP_POOL_SCRIPT = "ea07b733d932129c378af627436e7cbc2ef0bf96e0036bb51b3bde6b"


def minswap_fill_cost(tx, agent, order_addrs):
    """Attribute an executed V2 batch to its own orderer, never to all takers.

    Field 7 is the SDK's maxBatcherFee, not automatically the actual fee.
    Only accept it when conservation proves the whole batch paid the SUM of
    every order's cap: each capped nonnegative fee must then equal its cap.
    Missing datums, partial orders, discounts and unknown shapes fail closed.
    """
    ins, outs = tx.get("inputs") or [], tx.get("outputs") or []
    cred = lambda n: (n.get("payment_addr") or {}).get("cred")
    orders = [n for n in ins if cred(n) == MINSWAP_ORDER_SCRIPT]
    own = [n for n in orders if owned(n, agent, order_addrs)]
    if not own:
        return None
    if any(cred(n) == MINSWAP_ORDER_SCRIPT for n in outs):
        raise ValueError("cannot attribute a partial Minswap batch")
    pool_in = [n for n in ins if cred(n) == MINSWAP_POOL_SCRIPT]
    pool_out = [n for n in outs if cred(n) == MINSWAP_POOL_SCRIPT]
    if len(pool_in) != 1 or len(pool_out) != 1:
        raise ValueError("cannot attribute an unknown Minswap pool shape")
    receivers, caps, own_caps = set(), [], []
    for order in orders:
        try:
            datum = order["inline_datum"]["value"]
            fields = datum["fields"]
            assert datum["constructor"] == 0 and len(fields) == 9
            receiver = fields[1]["fields"][0]
            assert receiver["constructor"] == 0
            receiver = receiver["fields"][0]["bytes"]
            cap = fields[7]["int"]
            assert isinstance(cap, int) and not isinstance(cap, bool) and cap >= 0
        except (KeyError, TypeError, IndexError, AssertionError) as exc:
            raise ValueError("missing or unsupported Minswap order fee datum") from exc
        receivers.add(receiver)
        caps.append(cap)
        if order in own:
            if receiver != agent["payment_cred"]:
                raise ValueError("Minswap success receiver differs from order owner")
            own_caps.append(cap)
    if any(cred(n) in receivers for n in ins):
        raise ValueError("mixed wallet/order inputs need independent fee attribution")
    pool_delta = int(pool_out[0]["value"]) - int(pool_in[0]["value"])
    recipients_delta = (sum(int(n["value"]) for n in outs if cred(n) in receivers)
                        - sum(int(n["value"]) for n in orders))
    actual = -recipients_delta - pool_delta
    if actual != sum(caps):
        raise ValueError("Minswap batch fees differ from order caps; attribution unknown")
    return sum(own_caps) / 1e6


def receipt_move(tx, agent):
    """A pinned Liqwid receipt changing hands is not an ADA/USDM spot swap."""
    delta = 0
    for side, direction in (("inputs", -1), ("outputs", 1)):
        for node in tx.get(side) or []:
            if (node.get("payment_addr") or {}).get("cred") != agent["payment_cred"]:
                continue
            for asset in node.get("asset_list") or []:
                if LIQWID_MARKET_BY_POLICY.get(asset.get("policy_id")) == "USDM":
                    delta += direction * int(asset["quantity"])
    return delta


def describe(tx, agent, other, order_addrs, d_ada, d_usdm, paid_fee, fee):
    """Plain English for one move, derived from tx structure only."""
    certs = tx.get("certificates") or []
    deposit = lovelace(tx.get("deposit"))
    has_meta = bool(tx.get("metadata"))
    ins_addrs = {i["payment_addr"]["bech32"] for i in (tx.get("inputs") or [])}
    outs_addrs = {o["payment_addr"]["bech32"] for o in (tx.get("outputs") or [])}
    other_in = any((i["payment_addr"] or {}).get("cred") == other["payment_cred"]
                   for i in (tx.get("inputs") or []))
    other_out = any((o["payment_addr"] or {}).get("cred") == other["payment_cred"]
                    for o in (tx.get("outputs") or []))
    to_order = bool(outs_addrs & order_addrs)
    from_order = bool(ins_addrs & order_addrs)

    qdelta = receipt_move(tx, agent)
    if qdelta:
        minted = sum(int(a["quantity"]) for a in tx.get("assets_minted") or []
                     if LIQWID_MARKET_BY_POLICY.get(a.get("policy_id")) == "USDM")
        # An OTC receipt transfer is not evidence of protocol supply. Require
        # the matching mint/burn before naming the economic operation.
        if qdelta > 0 and d_usdm < 0 and minted == qdelta:
            return ("supply", "Supplied USDM to Liqwid",
                    f"Exchanged {abs(d_usdm):.6f} USDM for a Liqwid supply receipt. "
                    f"The receipt remains in the book; this is not a sale into ADA. "
                    f"Network fee {fee:.6f} ADA.")
        if qdelta < 0 and d_usdm > 0 and minted == qdelta:
            return ("redeem", "Redeemed Liqwid USDM supply",
                    f"Returned a Liqwid supply receipt for {d_usdm:.6f} USDM. "
                    f"This is not an ADA/USDM spot trade. Network fee {fee:.6f} ADA.")
        return ("receipt", "Moved a Liqwid USDM receipt",
                f"The wallet's qUSDM receipt balance changed by {qdelta / 1e6:.6f}. "
                f"Not classified as a spot swap. Network fee {fee:.6f} ADA.")

    if certs and deposit > 0:
        kinds = ", ".join(sorted({c.get("type", "cert") for c in certs}))
        return ("stake", "Registered a stake key and delegated",
                f"Locked a {deposit:.2f} ADA stake-key deposit and delegated to a "
                f"pool. The deposit is refundable, so it is still the agent's "
                f"asset and is counted on the scoreboard. Certificates: {kinds}. "
                f"Network fee {fee:.6f} ADA.")

    if abs(d_usdm) > 1e-9 or to_order or from_order:
        if to_order and abs(d_usdm) < 1e-9:
            outs = [o for o in (tx.get("outputs") or [])
                    if o["payment_addr"]["bech32"] in order_addrs]
            parked_ada = sum(lovelace(o["value"]) for o in outs)
            parked_usdm = sum(usdm_of(o) for o in outs)
            what = f"{parked_ada:.6f} ADA"
            if parked_usdm > 1e-9:
                what += f" and {parked_usdm:.6f} USDM"
            clips = (f" Split across {len(outs)} orders." if len(outs) > 1 else "")
            return ("order", "Placed a DEX swap order",
                    f"Parked {what} at a Minswap order address built from its own "
                    f"stake key, to be filled by a batcher.{clips} Not a trade yet "
                    f"— the funds are still the agent's until the fill, and this "
                    f"scoreboard still counts them. Network fee {fee:.6f} ADA.")
        direction = "ADA into USDM" if d_usdm > 0 else "USDM into ADA"
        pool = find_pool(tx, d_usdm)
        rate_txt = ""
        if pool and abs(d_usdm) > 1e-9:
            rate = abs(pool[1] / d_usdm)
            rate_txt = (f" The pool took {abs(pool[1]):.6f} ADA for "
                        f"{abs(d_usdm):.6f} USDM — an execution rate of "
                        f"{rate:.5f} ADA per USDM, before fees.")
        if from_order:
            service = minswap_fill_cost(tx, agent, order_addrs)
            pool_ada = -d_ada - fee - service
            received = (f"{d_usdm:.6f} USDM received" if d_usdm > 0 else
                        f"{abs(d_usdm):.6f} USDM sold for {-pool_ada:.6f} ADA before the batcher fee")
            return ("fill", f"Swap filled — {direction}",
                    f"A batcher filled this agent's order: {received}. "
                    f"This order paid {service:.6f} ADA to the batcher. "
                    f"The network fee on this transaction was "
                    f"paid by the batcher, not by the agent.")
        return ("swap", f"Swapped {direction}",
                f"Moved {abs(d_ada):.6f} ADA and {abs(d_usdm):.6f} USDM in one "
                f"transaction.{rate_txt} Network fee {fee:.6f} ADA.")

    if other_out and d_ada < 0:
        return ("transfer_out", f"Sent {abs(d_ada):.6f} ADA to {other['name']}",
                f"A direct transfer to the opponent. Network fee {fee:.6f} ADA.")
    if other_in and d_ada > 0:
        return ("transfer_in", f"Received {d_ada:.6f} ADA from {other['name']}",
                "A direct transfer from the opponent. The opponent paid the fee.")

    if not paid_fee and d_ada > 0:
        return ("fund", f"Funded with {d_ada:.6f} ADA",
                "Incoming stake from an external wallet. Not earned — this is "
                "the starting capital the match was set up with.")

    if has_meta and abs(d_ada) < 5:
        # What the metadata says is out of scope for this site. What it cost is
        # not: the fee, plus any ADA that left the book with it.
        strayed = max(0.0, -d_ada - fee)
        extra = (f" A further {strayed:.6f} ADA left the book with it and has not "
                 f"come back." if strayed > 1e-3 else "")
        return ("message", "Posted a metadata transaction",
                f"Carried on-chain metadata rather than moving a position. What it "
                f"says is outside this scoreboard; the {fee:.6f} ADA network fee it "
                f"cost is not.{extra}")

    if d_ada < 0:
        return ("out", f"Sent {abs(d_ada):.6f} ADA out",
                f"Network fee {fee:.6f} ADA.")
    return ("in", f"Received {d_ada:.6f} ADA", "Incoming transfer.")


def build_moves(agents, tx_by_hash, order_map):
    moves = []
    for agent in agents:
        other = next(a for a in agents if a["id"] != agent["id"])
        oset = set(order_map[agent["id"]])
        for tx in tx_by_hash.values():
            a_in = [i for i in (tx.get("inputs") or []) if owned(i, agent, oset)]
            a_out = [o for o in (tx.get("outputs") or []) if owned(o, agent, oset)]
            if not a_in and not a_out:
                continue
            d_ada = sum(lovelace(o["value"]) for o in a_out) - \
                sum(lovelace(i["value"]) for i in a_in)
            d_usdm = sum(usdm_of(o) for o in a_out) - sum(usdm_of(i) for i in a_in)

            # Trap 7: the agent paid the fee only if it funded the transaction
            # from its OWN payment credential. Funds spent out of a DEX order
            # script are moved by the batcher, which pays that fee itself.
            paid_fee = any((i["payment_addr"] or {}).get("cred") == agent["payment_cred"]
                           for i in (tx.get("inputs") or []))
            fee = lovelace(tx["fee"]) if paid_fee else 0.0

            kind, title, detail = describe(tx, agent, other, oset,
                                           d_ada, d_usdm, paid_fee, fee)
            moves.append({
                "agent": agent["id"],
                "tx_hash": tx["tx_hash"],
                "time": tx["tx_timestamp"],
                "block": tx["block_height"],
                "kind": kind,
                "title": title,
                "detail": detail,
                "ada_delta": round(d_ada, 6),
                "usdm_delta": round(d_usdm, 6),
                "fee": round(fee, 6),
                "deposit": round(lovelace(tx.get("deposit")), 6),
                "explorer": EXPLORER_TX + tx["tx_hash"],
            })
    moves.sort(key=lambda m: (m["time"], m["agent"]))
    return moves


def market_activity(agent_id: str, moves: list[dict], usdm_total: float) -> dict:
    """Separate completed trades, chain events and current economic exposure."""
    agent_events = [m for m in moves if m.get("agent") == agent_id]
    positions = []
    if usdm_total > 1e-9:
        positions.append({
            "id": "ada-usd-short-via-usdm",
            "status": "open",
            "economic_side": "long USDM / underweight ADA",
            "market_view": "ADA-bearish vs USD",
            "mechanism": "USDM spot holding",
            "quantity_usdm": round(usdm_total, 6),
            "notional_ada_eq": None,
            "share_of_book_pct": None,
            "leverage": {
                "type": "unlevered spot",
                "borrowed": False,
                "liquidation_price": None,
            },
        })
    return {
        "completed_trades": sum(
            1 for m in agent_events if m.get("kind") in ("swap", "fill")
        ),
        "chain_events": len(agent_events),
        "market_positions": positions,
        "open_position_count": len(positions),
    }


def cost_rollup(agents, moves, tx_by_hash, order_map):
    """Cumulative trading cost per agent, split into what it actually is.

    network  -- protocol fees the agent itself paid, exact from chain.
    service  -- ADA taken by DEX batchers, derived by conservation over each
                swap: everything the agent gave up that the pool did not
                receive and the network did not take.
    """
    costs = {a["id"]: {"network": 0.0, "service": 0.0, "swaps": 0,
                       "txs": 0, "ada_into_pool": 0.0, "usdm_bought": 0.0}
             for a in agents}
    for m in moves:
        c = costs[m["agent"]]
        c["network"] += m["fee"]
        if m["fee"] > 0:
            c["txs"] += 1

    for agent in agents:
        oset = set(order_map[agent["id"]])
        c = costs[agent["id"]]
        # Aggregate each swap over its order leg and its fill leg together: a
        # Minswap order and its batcher fill are one trade in two transactions.
        legs = [m for m in moves if m["agent"] == agent["id"]
                and m["kind"] in ("swap", "order", "fill")]
        if not legs:
            continue
        ada_given = -sum(m["ada_delta"] for m in legs)
        usdm_got = sum(m["usdm_delta"] for m in legs)
        net_fee = sum(m["fee"] for m in legs)
        pool_ada = 0.0
        for m in legs:
            tx = tx_by_hash[m["tx_hash"]]
            if abs(m["usdm_delta"]) < 1e-9:
                continue
            if m["kind"] == "fill":
                service = minswap_fill_cost(tx, agent, oset)
                pool_ada += -m["ada_delta"] - m["fee"] - service
            else:
                pool = find_pool(tx, m["usdm_delta"])
                if not pool:
                    raise ValueError("spot swap lacks attributable pool delta")
                pool_ada += pool[1]
            c["swaps"] += 1
        c["ada_into_pool"] = pool_ada
        c["usdm_bought"] = usdm_got
        # Conservation: given up = pool + network + service.
        c["service"] = round(ada_given - net_fee - pool_ada, 6)
        if c["service"] < -1e-6:
            raise ValueError("negative service cost: fee attribution does not reconcile")
    for c in costs.values():
        c["network"] = round(c["network"], 6)
        c["total"] = round(c["network"] + c["service"], 6)
        c["ada_into_pool"] = round(c["ada_into_pool"], 6)
        c["usdm_bought"] = round(c["usdm_bought"], 6)
        c["effective_rate"] = (round(c["ada_into_pool"] / c["usdm_bought"], 5)
                               if c["usdm_bought"] > 1e-9 else None)
        c["all_in_rate"] = (round((c["ada_into_pool"] + c["total"]) / c["usdm_bought"], 5)
                            if c["usdm_bought"] > 1e-9 else None)
    return costs


def t0_state(agents, moves):
    """Both books as they stood immediately after the levelling transaction.

    The components support two deliberately separate comparisons: each bot's
    decision-only P&L against its own starting mix re-marked today, and its
    scoreboard return from the one equalized ADA-equivalent starting value.
    """
    cut = None
    for m in moves:
        if m["tx_hash"] == LEVEL_TX:
            cut = m["time"]
    if cut is None:
        raise RuntimeError("levelling transaction is missing from reconstructed moves")
    state = {}
    for agent in agents:
        ada = usdm = dep = 0.0
        for m in moves:
            if m["agent"] != agent["id"]:
                continue
            if cut is not None and m["time"] > cut:
                continue
            ada += m["ada_delta"]
            usdm += m["usdm_delta"]
            dep += m["deposit"]
        state[agent["id"]] = {"ada": round(ada, 6), "usdm": round(usdm, 6),
                              "deposit": round(dep, 6)}
    return {"at_tx": LEVEL_TX, "at_time": cut, "books": state}


# --------------------------------------------------------------------------
# lead history
# --------------------------------------------------------------------------
HISTORY_FIELDS = ["t", "beacn", "grokbot", "usd_per_ada", "src"]


def load_history(path: Path) -> dict:
    try:
        h = json.loads(path.read_text())
        if h.get("fields") == HISTORY_FIELDS and isinstance(h.get("points"), list):
            return h
    except Exception:  # noqa: BLE001 - a missing or unreadable file just starts one
        pass
    return {"fields": HISTORY_FIELDS, "points": []}


def merge_points(history: dict, new_points: list, tolerance: int = 60) -> int:
    """Insert points, keeping the file sorted and never duplicating a moment.

    An existing point always wins over a new one at the same time: a live poll
    is a measurement, a backfilled point is a reconstruction, and a later
    backfill must not overwrite what was actually observed.
    """
    seen = {int(p[0]) for p in history["points"]}
    added = 0
    for pt in new_points:
        t = int(pt[0])
        if any(abs(t - s) <= tolerance for s in seen):
            continue
        history["points"].append([t, round(pt[1], 6), round(pt[2], 6),
                                  round(pt[3], 8), pt[4]])
        seen.add(t)
        added += 1
    history["points"].sort(key=lambda p: p[0])
    return added


def running_books(moves: list) -> dict:
    """Each agent's book after every move, as (time, ada_incl_deposit, usdm).

    ada_delta already treats a DEX order address as the agent's own, and the
    stake registration contributes -2.174433 ADA with a +2 deposit, so summing
    delta + deposit conserves the book across both.
    """
    out: dict[str, list] = {}
    for m in moves:
        cur = out.setdefault(m["agent"], [(0, 0.0, 0.0)])
        _, ada, usdm = cur[-1]
        cur.append((m["time"], ada + m["ada_delta"] + m["deposit"],
                    usdm + m["usdm_delta"]))
    return out


def book_at(series: list, t: int):
    ada = usdm = 0.0
    for ts, a, u in series:
        if ts > t:
            break
        ada, usdm = a, u
    return ada, usdm


def price_series() -> list:
    """[(unix_seconds, usd_per_ada)] from CoinGecko, oldest first, or []."""
    out = _curl([COINGECKO_CHART], timeout=25)
    try:
        rows = json.loads(out)["prices"]
    except Exception:  # noqa: BLE001
        return []
    return [(int(ms // 1000), float(px)) for ms, px in rows if px > 0]


def backfill(moves: list, history: dict) -> tuple[int, str]:
    """Reconstruct the lead at every historical price sample since the levelling.

    The books are exact at any timestamp -- they come from the chain. The mark
    is a real, independent market price at that timestamp. Points are labelled
    "b" so the page can show that they were reconstructed, not observed.

    It starts at the levelling transaction because before it the two books were
    still being set up: the setup swing dwarfs the match and would flatten it.
    """
    prices = price_series()
    if not prices:
        return 0, "price history unavailable"
    start = next((m["time"] for m in moves if m["tx_hash"] == LEVEL_TX), None)
    if start is None:
        return 0, "levelling transaction not in the move log"
    series = running_books(moves)
    pts = []
    # Stop short of now: the live poll point is added a moment later, and a
    # reconstruction landing seconds away from a real measurement would show as
    # two points at the same instant.
    cutoff = time.time() - 120
    for t, usd in prices:
        if t < start or t > cutoff or usd <= 0:
            continue
        rate = 1.0 / usd
        a_ada, a_usdm = book_at(series.get("beacn", []), t)
        b_ada, b_usdm = book_at(series.get("grokbot", []), t)
        pts.append([t, a_ada + a_usdm * rate, b_ada + b_usdm * rate, usd, "b"])
    added = merge_points(history, pts)
    return added, f"{len(prices)} price samples, {added} new points"


# --------------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--history", default=str(DEFAULT_HISTORY),
                    help="lead-history file to append this poll to")
    ap.add_argument("--no-history", action="store_true",
                    help="compute the snapshot without recording a history point")
    ap.add_argument("--backfill", action="store_true",
                    help="also reconstruct history back to the levelling tx "
                         "from chain plus an independent price series")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    def say(*a):
        if not args.quiet:
            print(*a)

    say("1/5 reading transaction history")
    tx_by_hash: dict[str, dict] = {}
    hashes: list[str] = []
    for agent in AGENTS:
        rows = koios("credential_txs",
                     {"_payment_credentials": [agent["payment_cred"]],
                      "_after_block_height": 0})
        for r in rows:
            if r["tx_hash"] not in hashes:
                hashes.append(r["tx_hash"])
    # Trap 1: without these flags Koios returns no inputs, no metadata and no
    # assets -- silently, as empty lists.
    for i in range(0, len(hashes), 40):
        for tx in koios("tx_info", {"_tx_hashes": hashes[i:i + 40], "_inputs": True,
                                    "_metadata": True, "_assets": True, "_scripts": True,
                                    "_certs": True, "_withdrawals": True}):
            tx_by_hash[tx["tx_hash"]] = tx
    say(f"    {len(tx_by_hash)} transactions")

    say("2/5 resolving order addresses and reading books")
    overlay = load_overlay()
    catalog = merge_catalog(overlay)
    by_script, by_policy = indexes(catalog)
    liqwid_rates = fetch_liqwid_rates()
    say("    Liqwid rates " + ("ok" if liqwid_rates else "UNAVAILABLE (receipts stay unpriced)"))
    order_map, books = {}, {}
    for agent in AGENTS:
        scripts = order_scripts(agent, list(tx_by_hash.values()))
        order_map[agent["id"]] = sorted(scripts)
        books[agent["id"]] = read_book(agent, scripts, by_script, by_policy,
                                       liqwid_rates=liqwid_rates)
        books[agent["id"]]["positions"] = merge_positions(
            books[agent["id"]]["positions"],
            overlay_positions_for(overlay, agent["id"]),
        )
        b = books[agent["id"]]
        pos_note = ("  positions " +
                    ",".join(p["venue"] for p in b["positions"])) if b["positions"] else ""
        say(f"    {agent['name']:<8} {b['ada']:.6f} ADA  {b['usdm']:.6f} USDM  "
            f"deposit {b['deposit']:.2f}  in-flight {b['in_flight_ada']:.6f}{pos_note}")

    say("3/5 fetching the price")
    price = get_price()
    say(f"    {price['source']}"
        + (f" -> ${price['usd_per_ada']}" if price["available"] else " -> UNAVAILABLE"))

    say("4/5 reconstructing moves and costs")
    moves = build_moves(AGENTS, tx_by_hash, order_map)
    costs = cost_rollup(AGENTS, moves, tx_by_hash, order_map)
    say(f"    {len(moves)} agent-moves")

    say("5/5 scoring")
    checks: list[dict] = []
    out_agents = []
    for agent in AGENTS:
        b = books[agent["id"]]
        c = costs[agent["id"]]
        ada_total = (b["ada"] + b["in_flight_ada"] + b["deposit"] + b["rewards"]
                    + b["receipt_ada"])
        usdm_total = b["usdm"] + b["in_flight_usdm"] + b["receipt_usdm_eq"]
        # A USDM allocation is one current economic position regardless of how
        # many entry fills created it. Under this ADA-denominated scoreboard it
        # is long USDM and underweight ADA. It is spot: no asset was borrowed,
        # there is no liquidation price, and calling it a leveraged or
        # derivative short would be false. Open DEX orders are separate below.
        activity = market_activity(agent["id"], moves, usdm_total)
        row = {
            "id": agent["id"], "name": agent["name"], "engine": agent["engine"],
            "address": agent["address"], "stake_address": agent["stake_address"],
            "explorer": EXPLORER_ADDR + agent["address"],
            "stake_explorer": EXPLORER_ADDR + agent["stake_address"],
            "pool": b["pool"],
            "pool_explorer": (EXPLORER_POOL + b["pool"]) if b["pool"] else None,
            "stake_status": b["stake_status"],
            "ada": round(b["ada"] + b["in_flight_ada"], 6),
            "usdm": round(usdm_total, 6),
            "deposit": round(b["deposit"], 6),
            "rewards": round(b["rewards"], 6),
            "rewards_lifetime": round(b["rewards_lifetime"], 6),
            "in_flight_ada": round(b["in_flight_ada"], 6),
            "in_flight_usdm": round(b["in_flight_usdm"], 6),
            "receipt_ada": round(b["receipt_ada"], 6),
            "receipt_usdm_eq": round(b["receipt_usdm_eq"], 6),
            "receipts_fully_priced": b["receipts_fully_priced"],
            "open_orders": b["open_orders"],
            "open_positions": b["positions"],
            "market_positions": activity["market_positions"],
            "open_position_count": activity["open_position_count"],
            "ada_total": round(ada_total, 6),
            "costs": c,
            # Public activity semantics. One Minswap order plus its later
            # batcher fill is one completed trade but two chain events.
            "completed_trades": activity["completed_trades"],
            "chain_events": activity["chain_events"],
            # Backwards-compatible alias for older page builds. New UI copy
            # must call these chain events, never trades or positions.
            "moves": activity["chain_events"],
            # Decision-only P&L against this agent's own starting mix, re-marked
            # at the current price. Kept as a separate public metric because it
            # answers a different question than return from the shared start.
            "vs_start_ada_eq": None,
            # Actual scoreboard return from the one equalized starting value.
            "vs_equalized_start_ada_eq": None,
            "vs_equalized_start_pct": None,
            "vs_equalized_start_usd_at_current_mark": None,
        }
        if price["available"]:
            rate = price["ada_per_usdm"]
            usd = price["usd_per_ada"]
            marked = mark_book(ada_total, usdm_total, usd)
            score_ada = marked["score_ada_eq"]
            score_usd = marked["score_usd"]
            checks.append({
                "agent": agent["id"],
                "label": f"{agent['name']} scored in both denominations",
                "ada_eq": round(score_ada, 6),
                "usd": round(score_usd, 6),
                "ada_eq_marked_to_usd": round(score_ada * usd, 6),
                "agree": abs(score_ada * usd - score_usd) < 1e-6,
            })
            row["score_ada_eq"] = round(score_ada, 6)
            row["score_usd"] = round(score_usd, 6)
            row["usdm_in_ada"] = round(usdm_total * rate, 6)
            # What the agent put into the pool, against what those stables are
            # worth at today's independent mark. This is NOT slippage measured
            # at execution -- it is the gap between the price the agent traded
            # at and the price the scoreboard marks at, which is the honest
            # thing to show, because the scoreboard is what decides the match.
            if c["usdm_bought"] > 1e-9:
                c["pool_vs_mark"] = round(
                    c["ada_into_pool"] - c["usdm_bought"] * rate, 6)
                c["all_in_vs_mark"] = round(c["pool_vs_mark"] + c["total"], 6)
            row["hedge_pct"] = round(100.0 * usdm_total * rate / score_ada, 2) \
                if score_ada else None
            for position in row["market_positions"]:
                position["notional_ada_eq"] = round(usdm_total * rate, 6)
                position["share_of_book_pct"] = row["hedge_pct"]
        else:
            row["score_ada_eq"] = None
            row["score_usd"] = None
            row["usdm_in_ada"] = None
            row["hedge_pct"] = None
        out_agents.append(row)

    leader = gap = None
    if price["available"]:
        a, b = out_agents
        gap = round(a["score_ada_eq"] - b["score_ada_eq"], 6)
        leader = a["id"] if gap > 0 else (b["id"] if gap < 0 else None)

    start = t0_state(AGENTS, moves)
    # The equalisation receipt is fixed: immediately after LEVEL_TX, BEACN's
    # side was entirely ADA. That makes its ADA + refundable deposit the one
    # shared starting score without importing a stale historical price. Both
    # agents agreed this was the level point; a later gap is the match score.
    anchor = start["books"]["beacn"]
    if abs(anchor["usdm"]) > 1e-9:
        raise RuntimeError("equalized-start anchor unexpectedly contains USDM")
    equalized_start = round(anchor["ada"] + anchor["deposit"], 6)
    start["equalized_score_ada_eq"] = equalized_start
    start["equalized_anchor"] = "BEACN all-ADA book immediately after the levelling transaction"
    if price["available"]:
        rate, usd = price["ada_per_usdm"], price["usd_per_ada"]
        for aid, s in start["books"].items():
            s["ada_eq_at_today_rate"] = round(s["ada"] + s["deposit"] + s["usdm"] * rate, 6)
            s["usd_at_today_rate"] = round((s["ada"] + s["deposit"]) * usd + s["usdm"], 6)
            for row in out_agents:
                if row["id"] == aid:
                    row["vs_start_ada_eq"] = round(
                        row["score_ada_eq"] - s["ada_eq_at_today_rate"], 6)
                    perf = equalized_performance(
                        row["score_ada_eq"], equalized_start, usd)
                    row["vs_equalized_start_ada_eq"] = round(perf["ada_eq"], 6)
                    row["vs_equalized_start_pct"] = round(perf["pct"], 4)
                    row["vs_equalized_start_usd_at_current_mark"] = round(
                        perf["usd_at_current_mark"], 6)

    last_block = max((t["block_height"] for t in tx_by_hash.values()), default=None)

    # A fingerprint over the CHAIN-DERIVED facts only -- balances, deposits,
    # rewards and the move log. It deliberately excludes the timestamp and
    # everything the price touches, so a scheduled publisher can tell "the
    # agents did something" apart from "the market moved" and does not have to
    # push a commit every quarter hour just because ADA ticked.
    fingerprint = hashlib.sha256(json.dumps({
        "books": {a["id"]: {k: books[a["id"]][k] for k in
                            ("ada", "usdm", "in_flight_ada", "in_flight_usdm",
                             "deposit", "rewards", "pool", "stake_status",
                             "positions")}
                  for a in AGENTS},
        "moves": [[m["tx_hash"], m["agent"], m["kind"], m["ada_delta"],
                   m["usdm_delta"], m["fee"]] for m in moves],
    }, sort_keys=True).encode()).hexdigest()

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "chain_fingerprint": fingerprint,
        "generated_at_unix": int(time.time()),
        "network": "Cardano mainnet",
        "price": price,
        "usdm": {"policy_id": USDM_POLICY, "asset_name_hex": USDM_NAME_HEX,
                 "issuer": "Moneta",
                 "note": ("USDM is a USD-denominated stablecoin. It is marked to ADA "
                          "by MULTIPLYING by ADA-per-USDM. It is never divided by it.")},
        "scoreboard": {
            "formula": "ADA held + refundable stake deposit + staking rewards + "
                       "(USDM held x ADA-per-USDM)",
            "note": ("Agreed by both agents. Under it a book held 100% in ADA scores "
                     "a constant: only an asset that appreciates against ADA can move "
                     "the number up."),
        },
        "start": start,
        "venues": used_venues(catalog, {a["id"]: a.get("open_positions") or []
                                        for a in out_agents}),
        "position_disclaimer": POSITION_DISCLAIMER,
        "agents": out_agents,
        "leader": leader,
        "gap_ada_eq": gap,
        "gap_usd": round(gap * price["usd_per_ada"], 6)
        if (gap is not None and price["available"]) else None,
        "moves": moves,
        "checks": checks,
        "last_move_block": last_block,
        "source": {
            "chain": "Koios api.koios.rest/api/v1 (public, no key)",
            "price": price["source"],
            "script": "scripts/match_snapshot.py",
        },
    }

    # ---- lead history -------------------------------------------------
    hist_note = None
    if not args.no_history:
        hpath = Path(args.history)
        history = load_history(hpath)
        if args.backfill:
            n, why = backfill(moves, history)
            say(f"    backfill: {why}")
        if price["available"]:
            # Same instant the snapshot is stamped with, so the chart's last
            # point and the headline can never disagree about "now".
            merge_points(history, [[payload["generated_at_unix"],
                                    out_agents[0]["score_ada_eq"],
                                    out_agents[1]["score_ada_eq"],
                                    price["usd_per_ada"], "p"]], tolerance=0)
        hpath.parent.mkdir(parents=True, exist_ok=True)
        hpath.write_text(json.dumps(history, separators=(",", ":")) + "\n")
        pts = history["points"]
        hist_note = {
            "points": len(pts),
            "first": pts[0][0] if pts else None,
            "last": pts[-1][0] if pts else None,
            "polled": sum(1 for x in pts if x[4] == "p"),
            "reconstructed": sum(1 for x in pts if x[4] == "b"),
            "file": hpath.name,
        }
        say(f"    history: {len(pts)} points "
            f"({hist_note['polled']} polled, {hist_note['reconstructed']} reconstructed)")
    payload["history"] = hist_note

    bad = [c for c in checks if not c["agree"]]
    if bad:
        print("FAIL: cross-denomination check disagreed:", bad, file=sys.stderr)
        return 2

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=1) + "\n")
    say(f"\nwrote {out} ({out.stat().st_size} bytes)")
    if price["available"]:
        for row in out_agents:
            say(f"  {row['name']:<8} {row['score_ada_eq']:>12.4f} ADA-eq  "
                f"${row['score_usd']:>8.2f}  hedged {row['hedge_pct']}%  "
                f"fees {row['costs']['total']:.6f} ADA")
        say(f"  gap {gap:+.4f} ADA-eq to "
            f"{leader or 'neither'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

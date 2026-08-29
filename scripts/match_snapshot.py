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
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "web" / "dist" / "data" / "match.json"

KOIOS = "https://api.koios.rest/api/v1"
COINGECKO = ("https://api.coingecko.com/api/v3/simple/price"
             "?ids=cardano&vs_currencies=usd")

# Moneta USDM. Trap 3: the name is ambiguous, the policy is not.
USDM_POLICY = "c48cbb3d5e57ed56e276bc45f99ab39abe94e6cd7ac39fb402da47ad"
USDM_NAME_HEX = "0014df105553444d"

# Minswap V2 order script. An order address is this hash + the ORDERER'S OWN
# stake credential, so it is unique per agent and its balance is still theirs.
MINSWAP_ORDER_SCRIPT = "c3e28c36c3447315ba5a56f33da6a6ddc1770a876a8d9f0cb3a97c4c"

EXPLORER_ADDR = "https://cardanoscan.io/address/"
EXPLORER_TX = "https://cardanoscan.io/transaction/"
EXPLORER_POOL = "https://cardanoscan.io/pool/"

AGENTS = [
    {
        "id": "beacn",
        "name": "BEACN",
        "engine": "Claude",
        "payment_cred": "570d2bf8e4f649a70d38ce0a50693ec4d0e2946341c0e452f495cf67",
        "address": ("addr1q9ts62lcunmynfcd8r8q55rf8mzdpc55vdqupezj7j2u7e69ujeu9gg"
                    "e3h9ffh8r95lsqfyzejra4sd43njhvsymsemsdergt3"),
        "stake_address": "stake1u9z7fv7z5yvcmj55mn3j60cqyjpvep76cx6ceetkgzdcvacqgqkle",
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


# --------------------------------------------------------------------------
# books
# --------------------------------------------------------------------------
def order_addresses(agent: dict, txs: list[dict]) -> list[str]:
    """Script addresses holding this agent's funds mid-trade.

    Trap 6: a DEX order address is the order script hash + the agent's OWN
    stake credential. Funds parked there between order and fill are still the
    agent's book. A snapshot taken in that window would otherwise show ~390 ADA
    vanishing.
    """
    found: set[str] = set()
    for tx in txs:
        for out in tx.get("outputs") or []:
            pa = out.get("payment_addr") or {}
            if (out.get("stake_addr") == agent["stake_address"]
                    and pa.get("cred") and pa["cred"] != agent["payment_cred"]):
                found.add(pa["bech32"])
    return sorted(found)


def read_book(agent: dict, order_addrs: list[str]) -> dict:
    """Current holdings, from chain, across every address form the agent uses."""
    utxos = koios("credential_utxos",
                  {"_payment_credentials": [agent["payment_cred"]], "_extended": True})
    ada = sum(lovelace(u["value"]) for u in utxos)
    usdm = sum(usdm_of(u) for u in utxos)

    flight_ada = flight_usdm = 0.0
    open_orders = 0
    for addr in order_addrs:
        info = koios("address_info", {"_addresses": [addr]})
        for row in info:
            for u in row.get("utxo_set") or []:
                flight_ada += lovelace(u["value"])
                flight_usdm += usdm_of(u)
                open_orders += 1

    acct = koios("account_info", {"_stake_addresses": [agent["stake_address"]]})
    acct = acct[0] if acct else {}
    return {
        "ada": ada,
        "usdm": usdm,
        "in_flight_ada": flight_ada,
        "in_flight_usdm": flight_usdm,
        "open_orders": open_orders,
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
        if agent_usdm_delta * d_usdm < 0:          # moved opposite the agent
            d_ada = outs[addr][0] - ins[addr][0]
            if best is None or abs(d_usdm) > abs(best[2]):
                best = (addr, d_ada, d_usdm)
    return best


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

    if certs and deposit > 0:
        kinds = ", ".join(sorted({c.get("type", "cert") for c in certs}))
        return ("stake", "Registered a stake key and delegated",
                f"Locked a {deposit:.2f} ADA stake-key deposit and delegated to a "
                f"pool. The deposit is refundable, so it is still the agent's "
                f"asset and is counted on the scoreboard. Certificates: {kinds}. "
                f"Network fee {fee:.6f} ADA.")

    if abs(d_usdm) > 1e-9 or to_order or from_order:
        if to_order and abs(d_usdm) < 1e-9:
            parked = sum(lovelace(o["value"]) for o in (tx.get("outputs") or [])
                         if o["payment_addr"]["bech32"] in order_addrs)
            return ("order", "Placed a DEX swap order",
                    f"Parked {parked:.6f} ADA at a Minswap order address built from "
                    f"its own stake key, to be filled by a batcher. Not a trade yet "
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
            return ("fill", f"Swap filled — {direction}",
                    f"A batcher filled the order: {abs(d_usdm):.6f} USDM landed in "
                    f"the wallet.{rate_txt} The network fee on this transaction was "
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
            pool = find_pool(tx, m["usdm_delta"])
            if pool:
                pool_ada += pool[1]
            c["swaps"] += 1
        c["ada_into_pool"] = pool_ada
        c["usdm_bought"] = usdm_got
        # Conservation: given up = pool + network + service.
        c["service"] = round(ada_given - net_fee - pool_ada, 6)
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

    Reported as ADA and USDM components, not a single figure: the levelling was
    computed at a rate that no longer holds, and marking the start at today's
    rate is the only comparison that does not smuggle in a stale price.
    """
    cut = None
    for m in moves:
        if m["tx_hash"] == LEVEL_TX:
            cut = m["time"]
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
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=str(DEFAULT_OUT))
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
                                    "_metadata": True, "_assets": True,
                                    "_certs": True, "_withdrawals": True}):
            tx_by_hash[tx["tx_hash"]] = tx
    say(f"    {len(tx_by_hash)} transactions")

    say("2/5 resolving order addresses and reading books")
    order_map, books = {}, {}
    for agent in AGENTS:
        oaddrs = order_addresses(agent, list(tx_by_hash.values()))
        order_map[agent["id"]] = oaddrs
        books[agent["id"]] = read_book(agent, oaddrs)
        b = books[agent["id"]]
        say(f"    {agent['name']:<8} {b['ada']:.6f} ADA  {b['usdm']:.6f} USDM  "
            f"deposit {b['deposit']:.2f}  in-flight {b['in_flight_ada']:.6f}")

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
        ada_total = b["ada"] + b["in_flight_ada"] + b["deposit"] + b["rewards"]
        usdm_total = b["usdm"] + b["in_flight_usdm"]
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
            "open_orders": b["open_orders"],
            "ada_total": round(ada_total, 6),
            "costs": c,
            "moves": sum(1 for m in moves if m["agent"] == agent["id"]),
        }
        if price["available"]:
            rate = price["ada_per_usdm"]
            usd = price["usd_per_ada"]
            # Trap 2: USDM is already dollars. To reach ADA you MULTIPLY.
            score_ada = ada_total + usdm_total * rate
            # The same total computed the other way round, in dollars. If these
            # two disagree the conversion has been applied the wrong way.
            score_usd = ada_total * usd + usdm_total
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
    if price["available"]:
        rate, usd = price["ada_per_usdm"], price["usd_per_ada"]
        for aid, s in start["books"].items():
            s["ada_eq_at_today_rate"] = round(s["ada"] + s["deposit"] + s["usdm"] * rate, 6)
            s["usd_at_today_rate"] = round((s["ada"] + s["deposit"]) * usd + s["usdm"], 6)
            for row in out_agents:
                if row["id"] == aid:
                    row["vs_start_ada_eq"] = round(
                        row["score_ada_eq"] - s["ada_eq_at_today_rate"], 6)

    last_block = max((t["block_height"] for t in tx_by_hash.values()), default=None)

    # A fingerprint over the CHAIN-DERIVED facts only -- balances, deposits,
    # rewards and the move log. It deliberately excludes the timestamp and
    # everything the price touches, so a scheduled publisher can tell "the
    # agents did something" apart from "the market moved" and does not have to
    # push a commit every quarter hour just because ADA ticked.
    fingerprint = hashlib.sha256(json.dumps({
        "books": {a["id"]: {k: books[a["id"]][k] for k in
                            ("ada", "usdm", "in_flight_ada", "in_flight_usdm",
                             "deposit", "rewards", "pool", "stake_status")}
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

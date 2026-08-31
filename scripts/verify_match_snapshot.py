#!/usr/bin/env python3
"""Fail closed if a generated match snapshot violates the public data contract."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def finite(value) -> bool:
    return not isinstance(value, bool) and isinstance(value, (int, float)) \
        and math.isfinite(value)


def verify(path: Path) -> None:
    data = json.loads(path.read_text())
    require(data.get("network") == "Cardano mainnet", "wrong or missing network")
    agents = data.get("agents") or []
    require([a.get("id") for a in agents] == ["beacn", "grokbot"],
            "agent order/identities changed")
    require(finite(data.get("generated_at_unix")), "missing generation timestamp")
    moves = data.get("moves") or []
    require(isinstance(moves, list), "moves must be a list")

    price = data.get("price") or {}
    require(isinstance(price.get("available"), bool), "price.available must be boolean")
    start = data.get("start") or {}
    baseline = start.get("equalized_score_ada_eq")
    require(finite(baseline) and baseline > 0, "missing shared equalized baseline")
    require(start.get("at_tx"), "missing levelling transaction")
    require(finite(start.get("at_time")), "missing levelling transaction time")
    books = start.get("books") or {}
    anchor = books.get("beacn") or {}
    for key in ("ada", "usdm", "deposit"):
        require(finite(anchor.get(key)), f"beacn start book missing {key}")
    require(abs(anchor["usdm"]) < 1e-9,
            "equalized-start anchor must be the all-ADA BEACN book")
    require(abs(baseline - anchor["ada"] - anchor["deposit"]) < 2e-6,
            "shared baseline does not reconcile to the levelling receipt")

    for agent in agents:
        aid = agent["id"]
        agent_events = [m for m in moves if m.get("agent") == aid]
        completed = sum(1 for m in agent_events
                        if m.get("kind") in ("swap", "fill"))
        require(agent.get("chain_events") == len(agent_events),
                f"{aid}.chain_events does not reconcile to the event log")
        require(agent.get("moves") == len(agent_events),
                f"{aid}.moves compatibility alias does not reconcile")
        require(agent.get("completed_trades") == completed,
                f"{aid}.completed_trades does not reconcile to fills")
        require((agent.get("costs") or {}).get("swaps") == completed,
                f"{aid}.costs.swaps does not reconcile to completed trades")
        require(isinstance(agent.get("open_orders"), int) and
                agent["open_orders"] >= 0, f"{aid}.open_orders is invalid")
        positions = agent.get("market_positions") or []
        expected_positions = 1 if agent.get("usdm", 0) > 1e-9 else 0
        require(agent.get("open_position_count") == expected_positions == len(positions),
                f"{aid} open-position count does not reconcile to holdings")
        if positions:
            position = positions[0]
            require(position.get("status") == "open" and
                    position.get("economic_side") == "long USDM / underweight ADA" and
                    position.get("market_view") == "ADA-bearish vs USD" and
                    position.get("mechanism") == "USDM spot holding",
                    f"{aid} market position is not explicitly classified")
            require(abs(position.get("quantity_usdm", 0) - agent["usdm"]) < 1e-6,
                    f"{aid} position quantity does not reconcile to USDM")
            leverage = position.get("leverage") or {}
            require(leverage.get("type") == "unlevered spot" and
                    leverage.get("borrowed") is False and
                    leverage.get("liquidation_price") is None,
                    f"{aid} leverage classification is not fail-closed")

    if price["available"]:
        usd = price.get("usd_per_ada")
        require(finite(usd) and usd > 0, "invalid ADA/USD mark")
        ada_per_usdm = price.get("ada_per_usdm")
        require(finite(ada_per_usdm) and ada_per_usdm > 0,
                "invalid ADA-per-USDM mark")
        require(abs(ada_per_usdm * usd - 1.0) < 1e-9,
                "reciprocal price marks do not reconcile")
        for agent in agents:
            aid = agent["id"]
            positions = agent.get("market_positions") or []
            for key in ("score_ada_eq", "score_usd", "vs_start_ada_eq",
                        "vs_equalized_start_ada_eq", "vs_equalized_start_pct",
                        "vs_equalized_start_usd_at_current_mark"):
                require(finite(agent.get(key)), f"{aid}.{key} missing or non-finite")
            expected = agent["score_ada_eq"] - baseline
            require(abs(expected - agent["vs_equalized_start_ada_eq"]) < 2e-6,
                    f"{aid} shared-start delta does not reconcile")
            expected_pct = 100.0 * expected / baseline
            require(abs(expected_pct - agent["vs_equalized_start_pct"]) < 6e-5,
                    f"{aid} shared-start percentage does not reconcile")
            expected_delta_usd = expected * usd
            require(abs(expected_delta_usd -
                        agent["vs_equalized_start_usd_at_current_mark"]) < 2e-6,
                    f"{aid} shared-start USD delta does not reconcile")
            require(finite(agent.get("ada_total")) and finite(agent.get("usdm")),
                    f"{aid} marked holdings missing or non-finite")
            expected_score_ada = agent["ada_total"] + agent["usdm"] / usd
            expected_score_usd = agent["ada_total"] * usd + agent["usdm"]
            require(abs(expected_score_ada - agent["score_ada_eq"]) < 1e-5,
                    f"{aid} ADA-equivalent score does not reconcile to holdings")
            require(abs(expected_score_usd - agent["score_usd"]) < 2e-6,
                    f"{aid} USD score does not reconcile to holdings")
            require(abs(agent["score_ada_eq"] * usd - agent["score_usd"]) < 2e-5,
                    f"{aid} ADA/USD marks do not reconcile")
            if positions:
                position = positions[0]
                require(abs(position.get("notional_ada_eq", 0) - agent["usdm"] / usd) < 1e-5,
                        f"{aid} position notional does not reconcile")
                require(abs(position.get("share_of_book_pct", 0) - agent["hedge_pct"]) < 1e-6,
                        f"{aid} position share does not reconcile")
            start_book = books.get(aid) or {}
            for key in ("ada", "usdm", "deposit", "ada_eq_at_today_rate",
                        "usd_at_today_rate"):
                require(finite(start_book.get(key)),
                        f"{aid} start book missing or invalid {key}")
            expected_start_ada = (start_book["ada"] + start_book["deposit"] +
                                  start_book["usdm"] / usd)
            expected_start_usd = ((start_book["ada"] + start_book["deposit"]) * usd +
                                  start_book["usdm"])
            require(abs(expected_start_ada - start_book["ada_eq_at_today_rate"]) < 1e-5,
                    f"{aid} start ADA mark does not reconcile")
            require(abs(expected_start_usd - start_book["usd_at_today_rate"]) < 2e-6,
                    f"{aid} start USD mark does not reconcile")
            require(abs(agent["score_ada_eq"] - expected_start_ada -
                        agent["vs_start_ada_eq"]) < 1e-5,
                    f"{aid} decision-only P&L does not reconcile")

        gap = agents[0]["score_ada_eq"] - agents[1]["score_ada_eq"]
        require(abs(gap - data.get("gap_ada_eq")) < 2e-6, "gap does not reconcile")
        require(finite(data.get("gap_usd")) and
                abs(gap * usd - data["gap_usd"]) < 2e-6,
                "USD gap does not reconcile")
        expected_leader = "beacn" if gap > 0 else ("grokbot" if gap < 0 else None)
        require(data.get("leader") == expected_leader, "leader disagrees with gap")
        checks = data.get("checks") or []
        require([c.get("agent") for c in checks] == ["beacn", "grokbot"],
                "cross-denomination checks missing or out of order")
        require(all(c.get("agree") is True for c in checks),
                "cross-denomination check failed")
    else:
        for agent in agents:
            for key in ("score_ada_eq", "score_usd", "vs_start_ada_eq",
                        "vs_equalized_start_ada_eq", "vs_equalized_start_pct",
                        "vs_equalized_start_usd_at_current_mark"):
                require(agent.get(key) is None, f"{agent['id']}.{key} must be null without a price")
        require(data.get("leader") is None and data.get("gap_ada_eq") is None
                and data.get("gap_usd") is None,
                "leader/gaps must be null without a price")


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("web/dist/data/match.json")
    try:
        verify(path)
    except Exception as exc:  # noqa: BLE001 - verifier must surface all contract failures
        print(f"FAIL {path}: {exc}", file=sys.stderr)
        return 1
    print(f"PASS {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

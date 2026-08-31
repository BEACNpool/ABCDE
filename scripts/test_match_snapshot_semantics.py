#!/usr/bin/env python3
"""Regression tests for the public match-count semantics."""

from __future__ import annotations

import unittest

from match_snapshot import market_activity


class MatchSnapshotSemanticsTest(unittest.TestCase):
    def test_events_orders_and_trades_are_separate(self):
        moves = [
            {"agent": "beacn", "kind": "fund"},
            {"agent": "beacn", "kind": "order"},
            {"agent": "beacn", "kind": "fill"},
            {"agent": "beacn", "kind": "swap"},
            {"agent": "grokbot", "kind": "swap"},
        ]
        summary = market_activity("beacn", moves, 126.687161)
        self.assertEqual(summary["chain_events"], 4)
        self.assertEqual(summary["completed_trades"], 2)
        self.assertEqual(summary["open_position_count"], 1)

    def test_multiple_fills_roll_into_one_unlevered_position(self):
        moves = [
            {"agent": "beacn", "kind": "fill"},
            {"agent": "beacn", "kind": "fill"},
        ]
        summary = market_activity("beacn", moves, 126.687161)
        self.assertEqual(summary["completed_trades"], 2)
        self.assertEqual(summary["open_position_count"], 1)
        position = summary["market_positions"][0]
        self.assertEqual(position["economic_side"], "short ADA/USD")
        self.assertEqual(position["quantity_usdm"], 126.687161)
        self.assertEqual(position["leverage"], {
            "type": "unlevered spot",
            "borrowed": False,
            "liquidation_price": None,
        })

    def test_zero_usdm_is_flat(self):
        summary = market_activity("beacn", [{"agent": "beacn", "kind": "fund"}], 0.0)
        self.assertEqual(summary["open_position_count"], 0)
        self.assertEqual(summary["market_positions"], [])


if __name__ == "__main__":
    unittest.main()

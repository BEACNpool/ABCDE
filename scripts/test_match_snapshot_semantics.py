#!/usr/bin/env python3
"""Regression tests for the public match-count semantics."""

from __future__ import annotations

import json
import unittest
from unittest.mock import patch

from match_snapshot import fetch_liqwid_rates, market_activity


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
        self.assertEqual(position["economic_side"], "long USDM / underweight ADA")
        self.assertEqual(position["market_view"], "ADA-bearish vs USD")
        self.assertEqual(position["mechanism"], "USDM spot holding")
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


class LiqwidRateFetchTests(unittest.TestCase):
    """Trap 5 still applies to this feed: never fabricate a rate."""

    def _payload(self, results):
        return json.dumps({"data": {"liqwid": {"data": {"markets": {
            "results": results}}}}})

    @patch("match_snapshot._curl")
    def test_parses_displayname_rate_and_price(self, curl):
        curl.return_value = self._payload([
            {"displayName": "USDM", "exchangeRate": 0.025051388,
             "asset": {"price": 1.0}},
            {"displayName": "ADA", "exchangeRate": 0.021145346,
             "asset": {"price": 0.19592}},
        ])
        rates = fetch_liqwid_rates()
        self.assertEqual(rates["USDM"], {"exchange_rate": 0.025051388,
                                         "price_usd": 1.0})
        self.assertAlmostEqual(rates["ADA"]["price_usd"], 0.19592)

    @patch("match_snapshot._curl")
    def test_unreachable_feed_returns_none_not_a_guess(self, curl):
        curl.return_value = ""
        self.assertIsNone(fetch_liqwid_rates())

    @patch("match_snapshot._curl")
    def test_graphql_errors_return_none(self, curl):
        curl.return_value = json.dumps({"errors": [{"message": "boom"}]})
        self.assertIsNone(fetch_liqwid_rates())

    @patch("match_snapshot._curl")
    def test_market_missing_a_field_is_skipped_not_fabricated(self, curl):
        curl.return_value = self._payload([
            {"displayName": "USDM", "exchangeRate": None, "asset": {"price": 1.0}},
            {"displayName": "ADA", "exchangeRate": 0.021145346,
             "asset": {"price": 0.19592}},
        ])
        rates = fetch_liqwid_rates()
        self.assertNotIn("USDM", rates)
        self.assertIn("ADA", rates)


if __name__ == "__main__":
    unittest.main()

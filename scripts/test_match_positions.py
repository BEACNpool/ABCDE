#!/usr/bin/env python3
"""Unit tests for the match open-position catalog. No network."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from match_positions import (
    BASE_VENUES, LIQWID_RECEIPT_POLICIES, MINSWAP_ORDER_SCRIPT,
    indexes, load_overlay, merge_catalog, merge_positions,
    overlay_positions_for, position_from_orders, position_from_receipts,
    receipts_in_utxos, used_venues, venue_public,
)


class CatalogTests(unittest.TestCase):
    def test_minswap_script_maps(self):
        by_script, _ = indexes(BASE_VENUES)
        self.assertEqual(by_script[MINSWAP_ORDER_SCRIPT], "minswap_v2")

    def test_unknown_script_is_absent(self):
        by_script, _ = indexes(BASE_VENUES)
        self.assertNotIn("deadbeef" * 7, by_script)

    def test_liqwid_ada_receipt_maps(self):
        _, by_policy = indexes(BASE_VENUES)
        ada = "a04ce7a52545e5e33c2867e148898d9e667a69602285f6a1298f9d68"
        self.assertEqual(by_policy[ada], "liqwid_v2")
        self.assertEqual(len(LIQWID_RECEIPT_POLICIES), 32)

    def test_cswap_is_catalogued_without_a_script_pin(self):
        v = BASE_VENUES["cswap_v1"]
        self.assertEqual(v["logo"], "match-venues/cswap.png")
        self.assertEqual(v["x"], "@CswapDEX")
        self.assertFalse(v["order_script_hashes"])

    def test_public_record_strips_pins(self):
        pub = venue_public(BASE_VENUES["liqwid_v2"])
        self.assertEqual(pub["name"], "Liqwid")
        self.assertNotIn("receipt_policies", pub)
        self.assertNotIn("order_script_hashes", pub)


class OverlayTests(unittest.TestCase):
    def test_missing_overlay_is_empty(self):
        data = load_overlay([Path("/no/such/file.json")])
        self.assertEqual(data["positions"], [])

    def test_overlay_adds_cswap_and_new_venue(self):
        overlay = {
            "venues": {
                "splash_v3": {
                    "name": "Splash", "x": "@splashprotocol",
                    "logo": "match-venues/splash.svg", "kind": "dex_order",
                },
                "cswap_v1": {"order_script_hashes": ["abc123"]},
            },
            "positions": [
                {"agent": "beacn", "venue": "cswap_v1", "kind": "dex_order",
                 "label": "limit ADA/NIGHT", "count": 1, "ada": 20, "usdm": 0},
                {"agent": "grokbot", "venue": "splash_v3", "kind": "dex_order",
                 "count": 1, "ada": 5},
            ],
        }
        catalog = merge_catalog(overlay)
        self.assertIn("abc123", catalog["cswap_v1"]["order_script_hashes"])
        self.assertEqual(catalog["splash_v3"]["name"], "Splash")
        beacn = overlay_positions_for(overlay, "beacn")
        self.assertEqual(len(beacn), 1)
        self.assertEqual(beacn[0]["venue"], "cswap_v1")
        grok = overlay_positions_for(overlay, "grokbot")
        self.assertEqual(grok[0]["venue"], "splash_v3")
        self.assertEqual(overlay_positions_for(overlay, "nobody"), [])

    def test_corrupt_overlay_is_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "overlay.json"
            bad.write_text("{not json", encoding="utf-8")
            data = load_overlay([bad])
            self.assertEqual(data["positions"], [])

    def test_load_first_readable_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            good = Path(tmp) / "ok.json"
            good.write_text(json.dumps({
                "positions": [{"agent": "beacn", "venue": "liqwid_v2",
                               "kind": "supply", "label": "qADA", "count": 1,
                               "ada": 81}],
            }), encoding="utf-8")
            data = load_overlay([Path(tmp) / "missing.json", good])
            self.assertEqual(data["positions"][0]["venue"], "liqwid_v2")


class MergeTests(unittest.TestCase):
    def test_catalog_alone_emits_no_positions(self):
        self.assertEqual(used_venues(BASE_VENUES, {"beacn": [], "grokbot": []}), {})

    def test_only_open_venues_are_published(self):
        pos = [position_from_orders("minswap_v2", count=2, ada=8, usdm=48)]
        used = used_venues(BASE_VENUES, {"beacn": pos, "grokbot": []})
        self.assertEqual(set(used), {"minswap_v2"})
        self.assertNotIn("liqwid_v2", used)
        self.assertNotIn("cswap_v1", used)

    def test_overlay_does_not_override_chain_size(self):
        chain = [position_from_orders("minswap_v2", count=2, ada=8, usdm=48)]
        overlay = [{"venue": "minswap_v2", "kind": "dex_order", "label": "x",
                    "count": 99, "ada": 1, "usdm": 0, "source": "overlay"}]
        merged = merge_positions(chain, overlay)
        self.assertEqual(len(merged), 1)
        self.assertEqual(merged[0]["count"], 2)
        self.assertEqual(merged[0]["ada"], 8)

    def test_overlay_adds_liqwid_when_chain_has_none(self):
        overlay = overlay_positions_for({
            "positions": [{"agent": "beacn", "venue": "liqwid_v2",
                           "kind": "supply", "label": "qADA 81", "count": 1,
                           "ada": 81, "usdm": 0}],
        }, "beacn")
        merged = merge_positions([], overlay)
        self.assertEqual(merged[0]["venue"], "liqwid_v2")
        self.assertEqual(merged[0]["source"], "overlay")

    def test_empty_order_position_is_none(self):
        self.assertIsNone(position_from_orders("minswap_v2", count=0, ada=0, usdm=0))

    def test_receipt_scan(self):
        _, by_policy = indexes(BASE_VENUES)
        utxos = [{
            "asset_list": [{
                "policy_id": "a04ce7a52545e5e33c2867e148898d9e667a69602285f6a1298f9d68",
                "quantity": "81000000",
            }],
        }]
        found = receipts_in_utxos(utxos, by_policy, "liqwid_v2")
        self.assertEqual(found, {"ADA": 81.0})
        pos = position_from_receipts("liqwid_v2", list(found.items()))
        self.assertIn("qADA", pos["label"])
        # Unrelated policy is ignored.
        other = [{"asset_list": [{"policy_id": "c48cbb3d5e57ed56e276bc45f99ab39abe94e6cd7ac39fb402da47ad",
                                  "quantity": "1000000"}]}]
        self.assertEqual(receipts_in_utxos(other, by_policy, "liqwid_v2"), {})


if __name__ == "__main__":
    unittest.main()

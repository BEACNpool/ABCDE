import copy
import json
import math
import tempfile
import unittest
from pathlib import Path

from scripts.match_snapshot import (
    LEVEL_TX,
    equalized_performance,
    mark_book,
    market_activity,
    t0_state,
)
from scripts.verify_match_snapshot import verify


class MatchMathTests(unittest.TestCase):
    def test_usdm_is_multiplied_by_ada_per_usdm(self):
        marked = mark_book(ada_total=500.0, usdm_total=80.0, usd_per_ada=0.20)
        self.assertAlmostEqual(marked["ada_per_usdm"], 5.0)
        self.assertAlmostEqual(marked["score_ada_eq"], 900.0)
        self.assertAlmostEqual(marked["score_usd"], 180.0)
        self.assertAlmostEqual(
            marked["score_ada_eq"] * 0.20,
            marked["score_usd"],
        )

    def test_equalized_performance_uses_one_shared_baseline(self):
        result = equalized_performance(
            score_ada_eq=900.0,
            baseline_ada_eq=907.241205,
            usd_per_ada=0.20,
        )
        self.assertAlmostEqual(result["ada_eq"], -7.241205)
        self.assertAlmostEqual(result["pct"], -0.798153, places=5)
        self.assertAlmostEqual(result["usd_at_current_mark"], -1.448241)

    def test_t0_state_includes_level_transaction_and_excludes_later_moves(self):
        agents = [{"id": "beacn"}, {"id": "grokbot"}]
        moves = [
            {"agent": "beacn", "tx_hash": "fund", "time": 10,
             "ada_delta": 790.0, "usdm_delta": 0.0, "deposit": 0.0},
            {"agent": "grokbot", "tx_hash": "fund", "time": 10,
             "ada_delta": 500.0, "usdm_delta": 58.0, "deposit": 0.0},
            {"agent": "beacn", "tx_hash": LEVEL_TX, "time": 20,
             "ada_delta": 117.0, "usdm_delta": 0.0, "deposit": 2.0},
            {"agent": "grokbot", "tx_hash": LEVEL_TX, "time": 20,
             "ada_delta": 407.0, "usdm_delta": -58.0, "deposit": 2.0},
            {"agent": "beacn", "tx_hash": "later", "time": 30,
             "ada_delta": -200.0, "usdm_delta": 40.0, "deposit": 0.0},
        ]
        start = t0_state(agents, moves)
        self.assertEqual(start["at_time"], 20)
        self.assertEqual(start["books"]["beacn"], {
            "ada": 907.0, "usdm": 0.0, "deposit": 2.0,
        })
        self.assertEqual(start["books"]["grokbot"], {
            "ada": 907.0, "usdm": 0.0, "deposit": 2.0,
        })

    def test_invalid_marks_fail_closed(self):
        with self.assertRaises(ValueError):
            mark_book(1.0, 1.0, 0.0)
        with self.assertRaises(ValueError):
            mark_book(1.0, math.nan, 0.20)
        with self.assertRaises(ValueError):
            equalized_performance(1.0, 0.0, 0.20)
        with self.assertRaises(ValueError):
            equalized_performance(1.0, 1.0, math.inf)

    def test_missing_level_transaction_fails_closed(self):
        with self.assertRaisesRegex(RuntimeError, "levelling transaction"):
            t0_state(
                [{"id": "beacn"}, {"id": "grokbot"}],
                [{"agent": "beacn", "tx_hash": "not-level", "time": 10,
                  "ada_delta": 907.0, "usdm_delta": 0.0, "deposit": 2.0}],
            )


class SnapshotVerifierTests(unittest.TestCase):
    @staticmethod
    def valid_snapshot():
        usd = 0.20
        baseline = 907.0

        def agent(aid, ada, usdm):
            score_ada = ada + usdm / usd
            score_usd = ada * usd + usdm
            delta = score_ada - baseline
            activity = market_activity(aid, [], usdm)
            for position in activity["market_positions"]:
                position["notional_ada_eq"] = usdm / usd
                position["share_of_book_pct"] = 100 * (usdm / usd) / score_ada
            return {
                **activity,
                "id": aid,
                "moves": 0,
                "open_orders": 0,
                "costs": {"swaps": 0, "network": 0, "service": 0, "total": 0},
                "hedge_pct": 100 * (usdm / usd) / score_ada,
                "ada_total": ada,
                "usdm": usdm,
                "score_ada_eq": score_ada,
                "score_usd": score_usd,
                "vs_start_ada_eq": delta,
                "vs_equalized_start_ada_eq": delta,
                "vs_equalized_start_pct": round(100.0 * delta / baseline, 4),
                "vs_equalized_start_usd_at_current_mark": delta * usd,
            }

        return {
            "network": "Cardano mainnet",
            "generated_at_unix": 1_788_000_000,
            "price": {"available": True, "usd_per_ada": usd,
                      "ada_per_usdm": 1.0 / usd},
            "start": {
                "at_tx": LEVEL_TX,
                "at_time": 1_788_000_000,
                "equalized_score_ada_eq": baseline,
                "books": {
                    "beacn": {"ada": 905.0, "usdm": 0.0, "deposit": 2.0,
                              "ada_eq_at_today_rate": 907.0,
                              "usd_at_today_rate": 181.4},
                    "grokbot": {"ada": 505.0, "usdm": 80.0, "deposit": 2.0,
                                "ada_eq_at_today_rate": 907.0,
                                "usd_at_today_rate": 181.4},
                },
            },
            "agents": [agent("beacn", 500.0, 80.0),
                       agent("grokbot", 510.0, 80.0)],
            "leader": "grokbot",
            "gap_ada_eq": -10.0,
            "gap_usd": -2.0,
            "checks": [{"agent": "beacn", "agree": True},
                       {"agent": "grokbot", "agree": True}],
        }

    def verify_snapshot(self, data):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "match.json"
            path.write_text(json.dumps(data))
            verify(path)

    def test_valid_priced_snapshot_passes(self):
        self.verify_snapshot(self.valid_snapshot())

    def test_corrupt_shared_baseline_fails(self):
        data = self.valid_snapshot()
        data["start"]["equalized_score_ada_eq"] = 1.0
        with self.assertRaisesRegex(ValueError, "baseline"):
            self.verify_snapshot(data)

    def test_negative_or_inconsistent_fees_fail(self):
        for fields in ({"service": -1, "total": -1}, {"network": 1, "total": 1},
                       {"total": 9845}):
            data = self.valid_snapshot()
            data["agents"][0]["costs"].update(fields)
            with self.assertRaisesRegex(ValueError, "costs"):
                self.verify_snapshot(data)

    def test_corrupt_shared_start_derivatives_fail(self):
        for field in ("vs_equalized_start_pct",
                      "vs_equalized_start_usd_at_current_mark"):
            with self.subTest(field=field):
                data = self.valid_snapshot()
                data["agents"][0][field] = 999.0
                with self.assertRaisesRegex(ValueError, "does not reconcile"):
                    self.verify_snapshot(data)

    def test_scores_must_reconcile_to_holdings(self):
        data = self.valid_snapshot()
        agent = data["agents"][0]
        agent["score_ada_eq"] += 1.0
        agent["score_usd"] += 0.2
        agent["vs_equalized_start_ada_eq"] += 1.0
        agent["vs_equalized_start_pct"] = round(
            100.0 * agent["vs_equalized_start_ada_eq"] /
            data["start"]["equalized_score_ada_eq"], 4)
        agent["vs_equalized_start_usd_at_current_mark"] += 0.2
        data["gap_ada_eq"] += 1.0
        data["gap_usd"] += 0.2
        with self.assertRaisesRegex(ValueError, "score does not reconcile to holdings"):
            self.verify_snapshot(data)

    def test_unpriced_snapshot_requires_null_score_fields(self):
        data = self.valid_snapshot()
        data["price"] = {"available": False}
        for agent in data["agents"]:
            for field in ("score_ada_eq", "score_usd", "vs_start_ada_eq",
                          "vs_equalized_start_ada_eq", "vs_equalized_start_pct",
                          "vs_equalized_start_usd_at_current_mark"):
                agent[field] = None
        data["leader"] = data["gap_ada_eq"] = data["gap_usd"] = None
        self.verify_snapshot(data)


if __name__ == "__main__":
    unittest.main()

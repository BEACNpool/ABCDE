"""Failure-oriented tests for public realized spot results; no network or DB."""
import copy
import unittest
from decimal import Decimal, localcontext

from match_fight import (Q_USDM_NAME, Q_USDM_POLICY, USDM_MARKET,
                         annotate_moves, raw_fight_evidence)
from match_snapshot import USDM_NAME_HEX, USDM_POLICY, build_moves


def move(n, kind, ada=0, usdm=0, fee=0, **kw):
    def raw(x):
        return str(Decimal(str(x)) * 1_000_000)
    m = {"agent": "beacn", "tx_hash": str(n), "block": n, "time": n,
         "kind": kind, "ada_delta": ada, "usdm_delta": usdm, "fee": fee,
         "fight_evidence": {"version": 2, "spot_assets_only": True, "accounting_assets_only": True,
             "spot_trade_eligible": True, "zero_usdm_origin": kind == "fund",
             "order_fee_status": "verified" if kind in {"order", "cancel"} else "not_applicable",
             "ada_delta_raw": raw(ada), "usdm_delta_raw": raw(usdm),
             "qtoken_delta_raw": "0", "input_qtoken_raw": "0",
             "input_usdm_raw": raw(abs(usdm) if usdm < 0 else 0),
             "network_fee_raw": raw(fee), "tx_block_index": 0}}
    m.update(kw)
    return m


def current_sale():
    # Public chain values, including all three explicit order placement fees.
    return [move(1, "fund", 971.361094),
            move(2, "order", -.185697, fee=.185697),
            move(3, "fill", -392.78, 78.509894),
            move(4, "order", -.185697, fee=.185697),
            move(5, "fill", -242, 48.177267),
            move(6, "order", -.213329, fee=.213329),
            move(7, "out", -.169945, fee=.169945),
            move(8, "out", -.169945, fee=.169945),
            move(9, "out", -.169945, fee=.169945),
            move(10, "fill", 104.157137, -24.088633)]


class FightTests(unittest.TestCase):
    def test_current_sale_exact_and_scope(self):
        rows = current_sale()
        before = copy.deepcopy(rows)
        effect = annotate_moves(rows, expected_liquid_usdm={"beacn": "102.598528"})[-1]["effect"]
        self.assertEqual(effect["ada"], "-16.6527975875598159469371959")
        self.assertEqual(effect["cost_basis_ada"], "120.8099345875598159469371959")
        self.assertEqual(effect["net_proceeds_ada"], "104.157137")
        self.assertEqual(effect["status"], "verified")
        self.assertEqual(effect["source_tx_hashes"], ["2", "3", "4", "5", "6", "10"])
        self.assertIn("not total-book P&L", effect["claim_scope"])
        self.assertEqual(rows, before)

    def test_decimal_context_is_reproducible(self):
        rows = current_sale()
        with localcontext() as ctx:
            ctx.prec = 6
            result = annotate_moves(rows)[-1]["effect"]["ada"]
        self.assertEqual(result, "-16.6527975875598159469371959")

    def test_profit_and_break_even_are_actual_numbers(self):
        for proceeds, expected in [(12, "2"), (10, "0")]:
            effect = annotate_moves([move(1, "fund", 100), move(2, "swap", -10, 2),
                                     move(3, "swap", proceeds, -2)])[-1]["effect"]
            self.assertEqual(effect["ada"], expected)
            self.assertEqual(effect["type"], "realized_spot_pnl")

    def test_setup_buy_and_supply_have_no_points(self):
        rows = [move(1, "fund", 100), move(2, "swap", -10, 2),
                move(3, "supply", -.4, -2, .4)]
        out = annotate_moves(rows)
        self.assertEqual([m["effect"]["ada"] for m in out], [None, None, None])
        self.assertEqual(out[-1]["effect"]["type"], "position_conversion")

    def test_receipt_invalidates_future_not_past_and_never_resets(self):
        rows = current_sale() + [move(11, "supply", -.4, -78.509894, .4),
            move(12, "redeem", -.4, 78.6, .4),
            move(13, "swap", 500, -102.688634), move(14, "fund", 100),
            move(15, "swap", -10, 2), move(16, "swap", 12, -2)]
        out = annotate_moves(rows)
        self.assertEqual(out[9]["effect"]["status"], "verified")
        for m in out[10:]:
            self.assertEqual(m["effect"]["status"], "unknown")
            self.assertIsNone(m["effect"]["ada"])

    def test_unknown_asset_even_zero_net_delta_stops_basis(self):
        rows = current_sale()
        rows[6]["fight_evidence"]["spot_assets_only"] = False
        rows[6]["fight_evidence"]["accounting_assets_only"] = False
        self.assertEqual(annotate_moves(rows)[-1]["effect"]["status"], "unknown")

    def test_duplicate_identity_invalidates_agent_but_not_opponent(self):
        rows = current_sale()
        rows.append(copy.deepcopy(rows[-1]))
        opponent = [move(1, "fund", 100, agent="grokbot"),
                    move(2, "swap", -10, 2, agent="grokbot"),
                    move(3, "swap", 12, -2, agent="grokbot")]
        out = annotate_moves(rows + opponent)
        self.assertEqual(out[9]["effect"]["status"], "unknown")
        self.assertEqual(out[-1]["effect"]["ada"], "2")
        self.assertNotEqual(out[0]["event_id"], out[-3]["event_id"])

    def test_missing_origin_and_oversold_inventory(self):
        for rows in [current_sale()[1:], [move(1, "fund", 100), move(2, "swap", 20, -2)]]:
            self.assertIsNone(annotate_moves(rows)[-1]["effect"]["ada"])

    def test_same_block_order_is_by_index_not_input_list_or_timestamp(self):
        rows = [move(1, "fund", 100), move(2, "swap", -10, 2), move(3, "swap", 12, -2)]
        rows[1].update(block=2, time=2)
        rows[2].update(block=2, time=2)
        rows[2]["fight_evidence"]["tx_block_index"] = 1
        out = annotate_moves([rows[0], rows[2], rows[1]])
        self.assertEqual(out[1]["effect"]["ada"], "2")
        for value in [None, 0, "1"]:
            rows[2]["fight_evidence"]["tx_block_index"] = value
            self.assertIsNone(annotate_moves(rows)[-1]["effect"]["ada"])

    def test_same_second_different_blocks_are_ordered(self):
        rows = [move(1, "fund", 100), move(2, "swap", -10, 2), move(3, "swap", 12, -2)]
        rows[2]["time"] = 2
        rows[1]["fight_evidence"]["tx_block_index"] = None
        rows[2]["fight_evidence"]["tx_block_index"] = None
        self.assertEqual(annotate_moves(rows[::-1])[0]["effect"]["ada"], "2")

    def test_bad_raw_display_and_reconciliation_fail_closed(self):
        for mutation in [lambda m: m.update(ada_delta="NaN"),
                         lambda m: m.update(ada_delta=999),
                         lambda m: m["fight_evidence"].pop("network_fee_raw"),
                         lambda m: m["fight_evidence"].update(usdm_delta_raw="1.5")]:
            rows = current_sale()
            mutation(rows[-1])
            self.assertIsNone(annotate_moves(rows)[-1]["effect"]["ada"])
        self.assertIsNone(annotate_moves(current_sale(), expected_liquid_usdm={"beacn": "0"})[-1]["effect"]["ada"])

    def test_missing_buy_detected_by_input_inventory(self):
        rows = current_sale()
        rows[9]["fight_evidence"]["input_usdm_raw"] = "500000000"
        self.assertIsNone(annotate_moves(rows)[-1]["effect"]["ada"])

    def test_verified_cancel_fee_counted_once_and_unknown_cancellation_halts(self):
        rows = [move(1, "fund", 100), move(2, "swap", -10, 2),
                move(3, "cancel", -.2, fee=.2), move(4, "swap", 12, -2)]
        self.assertEqual(annotate_moves(rows)[-1]["effect"]["ada"], "1.8")
        rows[2]["fight_evidence"]["order_fee_status"] = "unknown"
        self.assertIsNone(annotate_moves(rows)[-1]["effect"]["ada"])


def node(address, value, quantity=None, *, policy=USDM_POLICY, name=USDM_NAME_HEX):
    return {"payment_addr": {"bech32": address, "cred": address}, "value": str(value),
            "asset_list": [] if quantity is None else [{"policy_id": policy,
                "asset_name": name, "quantity": str(quantity)}]}


def conversion_tx(du, dq):
    """du is signed wallet USDM in whole units; dq signed raw qtokens."""
    du_raw = int(Decimal(str(du)) * 1_000_000)
    wallet_in = node("owner", 10_000_000, -du_raw if du_raw < 0 else None)
    wallet_out = node("owner", 9_800_000, du_raw if du_raw > 0 else None)
    qnode = wallet_out if dq > 0 else wallet_in
    qnode["asset_list"].append({"policy_id": Q_USDM_POLICY, "asset_name": Q_USDM_NAME,
                               "quantity": str(abs(dq))})
    market_in = node(USDM_MARKET, 5_000_000, 1_000_000_000)
    market_out = node(USDM_MARKET, 5_000_000, 1_000_000_000 - du_raw)
    market_in["inline_datum"] = {"value": {"list": [{"list": [
        {"int": 1_000_000_000}, {"int": 10_000_000_000}, {"int": -9}]}, {"bytes": "unchanged"}]}}
    market_out["inline_datum"] = copy.deepcopy(market_in["inline_datum"])
    values = market_out["inline_datum"]["value"]["list"][0]["list"]
    values[0]["int"] -= du_raw; values[1]["int"] += dq
    return {"inputs": [wallet_in, market_in], "outputs": [wallet_out, market_out],
            "fee": "200000", "deposit": "0", "withdrawals": [], "certificates": [],
            "assets_minted": [{"policy_id": Q_USDM_POLICY, "asset_name": Q_USDM_NAME,
                               "quantity": str(dq)}]}


def conversion_move(n, du, dq):
    tx = conversion_tx(du, dq)
    ev = raw_fight_evidence(tx, {"payment_cred": "owner"}, set(),
                           usdm_policy=USDM_POLICY, usdm_name=USDM_NAME_HEX)
    m = move(n, "supply" if dq > 0 else "redeem", -.2, du, .2)
    m["fight_evidence"] = ev
    return m


class ReceiptAccountingTests(unittest.TestCase):
    def base(self):
        return [move(1, "fund", 200), move(2, "swap", -100, 20),
                conversion_move(3, -10, 100_000_000)]

    def test_supply_proof_and_separate_basis_preserve_future_rail_profit(self):
        rows = self.base() + [move(4, "fill", 60, -10)]
        out = annotate_moves(rows, expected_liquid_usdm={"beacn": "0"},
                             expected_q_usdm_raw={"beacn": "100000000"})
        self.assertEqual(out[2]["effect"]["status"], "verified")
        self.assertIsNone(out[2]["effect"]["ada"])
        accounting = out[2]["effect"]["conversion_accounting"]
        self.assertEqual(Decimal(accounting["liquid_basis_ada_after"]), Decimal("50"))
        self.assertEqual(Decimal(accounting["qtoken_basis_ada_after"]), Decimal("50.2"))
        self.assertEqual(Decimal(out[-1]["effect"]["ada"]), Decimal("10"))

    def test_partial_redemption_and_interest_units_then_sale(self):
        rows = self.base() + [move(4, "fill", 60, -10),
            conversion_move(5, 6, -50_000_000), move(6, "swap", 30, -6),
            conversion_move(7, 6, -50_000_000), move(8, "swap", 31, -6)]
        out = annotate_moves(rows, expected_liquid_usdm={"beacn": "0"},
                             expected_q_usdm_raw={"beacn": "0"})
        self.assertEqual(Decimal(out[5]["effect"]["ada"]), Decimal("4.7"))
        self.assertEqual(Decimal(out[-1]["effect"]["ada"]), Decimal("5.7"))
        a = out[4]["effect"]["conversion_accounting"]
        self.assertEqual(Decimal(a["basis_transferred_ada"]), Decimal("25.1"))
        self.assertEqual(Decimal(a["liquid_basis_ada_after"]), Decimal("25.3"))
        self.assertEqual(Decimal(a["qtoken_basis_ada_after"]), Decimal("25.1"))

    def test_current_stop_unchanged_after_proved_supply(self):
        rows = current_sale() + [conversion_move(11, -78.509894, 3_131_243_117),
                                move(12, "fill", 130, -24.088634)]
        out = annotate_moves(rows)
        self.assertEqual(out[9]["effect"]["ada"], "-16.6527975875598159469371959")
        self.assertEqual(out[10]["effect"]["status"], "verified")
        self.assertEqual(out[-1]["effect"]["status"], "verified")
        self.assertGreater(Decimal(out[-1]["effect"]["ada"]), 0)

    def test_unknown_history_cannot_be_repaired_by_valid_conversion(self):
        rows = self.base()
        rows[1]["fight_evidence"]["accounting_assets_only"] = False
        rows += [conversion_move(4, 12, -100_000_000), move(5, "swap", 100, -12)]
        self.assertTrue(all(m["effect"]["status"] == "unknown" for m in annotate_moves(rows)[1:]))

    def test_over_redemption_and_qtoken_reconciliation_fail_closed(self):
        rows = self.base() + [conversion_move(4, 12, -101_000_000), move(5, "swap", 100, -12)]
        self.assertIsNone(annotate_moves(rows)[-1]["effect"]["ada"])
        rows = self.base() + [move(4, "fill", 60, -10)]
        self.assertIsNone(annotate_moves(rows, expected_q_usdm_raw={"beacn": "0"})[-1]["effect"]["ada"])

    def test_plain_conversion_rejects_script_mint_datum_borrow_and_foreign_receipt(self):
        mutations = [
            lambda t: t["inputs"][1]["payment_addr"].update(bech32="wrong-market"),
            lambda t: t["assets_minted"][0].update(quantity="99999999"),
            lambda t: t["assets_minted"][0].update(asset_name="wrong-name"),
            lambda t: t["outputs"][0]["asset_list"][-1].update(asset_name="wrong-name"),
            lambda t: t["outputs"].append(node("foreign", 0, 1, policy=Q_USDM_POLICY, name="")),
            lambda t: t["inputs"].append(node("loan-contract", 2_000_000)),
            lambda t: t["outputs"][1]["inline_datum"]["value"]["list"][0]["list"][2].update(int=10),
            lambda t: t["outputs"][1]["inline_datum"]["value"]["list"][0]["list"][0].update(int=4),
            lambda t: t["outputs"][1].update(value="5000001"),
            lambda t: t["outputs"][0].update(value="9800001"),
        ]
        for mutate in mutations:
            tx = conversion_tx(-10, 100_000_000); mutate(tx)
            ev = raw_fight_evidence(tx, {"payment_cred": "owner"}, set(),
                                   usdm_policy=USDM_POLICY, usdm_name=USDM_NAME_HEX)
            self.assertNotEqual(ev["receipt_conversion"]["status"], "verified")

    def test_plain_borrow_cashflow_is_not_a_spot_acquisition(self):
        tx = {"inputs": [node("owner", 10_000_000), node("loan", 5_000_000, 10_000_000)],
              "outputs": [node("owner", 9_800_000, 10_000_000), node("loan", 5_000_000)],
              "fee": "200000", "assets_minted": [], "withdrawals": [], "certificates": []}
        ev = raw_fight_evidence(tx, {"payment_cred": "owner"}, set(),
                               usdm_policy=USDM_POLICY, usdm_name=USDM_NAME_HEX)
        self.assertFalse(ev["spot_trade_eligible"])
        borrowed = move(2, "swap", -.2, 10, .2); borrowed["fight_evidence"] = ev
        out = annotate_moves([move(1, "fund", 100), borrowed, move(3, "swap", 50, -10)])
        self.assertIsNone(out[-1]["effect"]["ada"])


class RawEvidenceTests(unittest.TestCase):
    def evidence(self, tx):
        return raw_fight_evidence(tx, {"payment_cred": "owner"}, {"order"},
                                 usdm_policy=USDM_POLICY, usdm_name=USDM_NAME_HEX)

    def cancel(self):
        return {"inputs": [node("owner", 2_000_000), node("order", 4_000_000, 2_000_000)],
                "outputs": [node("owner", 5_800_000, 2_000_000)], "fee": "200000"}

    def test_cancel_fee_requires_whole_book_conservation_and_no_foreign_payer(self):
        tx = self.cancel()
        self.assertEqual(self.evidence(tx)["order_fee_status"], "verified")
        tx["inputs"].append(node("foreign", 1_000_000))
        self.assertEqual(self.evidence(tx)["order_fee_status"], "unknown")
        tx = self.cancel(); tx["outputs"][0]["value"] = "5800001"
        self.assertEqual(self.evidence(tx)["order_fee_status"], "unknown")

    def test_exact_asset_identity_missing_lists_and_duplicate_assets(self):
        for mutate in [lambda n: n.pop("asset_list"),
                       lambda n: n["asset_list"][0].update(asset_name="other"),
                       lambda n: n["asset_list"][0].update(policy_id="other"),
                       lambda n: n["asset_list"].append(copy.deepcopy(n["asset_list"][0])),
                       lambda n: n["asset_list"][0].update(quantity="NaN")]:
            tx = self.cancel(); mutate(tx["outputs"][0])
            self.assertFalse(self.evidence(tx)["spot_assets_only"])

    def test_zero_origin_requires_no_owned_inputs_and_no_usdm(self):
        tx = {"inputs": [node("external", 101)], "outputs": [node("owner", 100)], "fee": "1"}
        self.assertTrue(self.evidence(tx)["zero_usdm_origin"])
        tx["outputs"][0] = node("owner", 100, 1)
        self.assertFalse(self.evidence(tx)["zero_usdm_origin"])

    def test_mint_mixed_with_trade_is_ineligible(self):
        tx = self.cancel(); tx["assets_minted"] = [{"quantity": "1"}]
        self.assertFalse(self.evidence(tx)["spot_trade_eligible"])

    def test_zero_script_withdrawals_are_not_reward_income(self):
        tx = self.cancel(); tx["withdrawals"] = [{"amount": "0", "stake_addr": "script"}]
        self.assertTrue(self.evidence(tx)["spot_trade_eligible"])
        self.assertEqual(self.evidence(tx)["order_fee_status"], "verified")
        for withdrawals in [[{"amount": "1"}], [{}], [{"amount": "NaN"}], "unknown"]:
            tx["withdrawals"] = withdrawals
            self.assertFalse(self.evidence(tx)["spot_trade_eligible"])
        tx = self.cancel(); tx["certificates"] = [{"type": "stake_deregistration"}]
        self.assertFalse(self.evidence(tx)["spot_trade_eligible"])
        tx = self.cancel(); tx["deposit"] = "2000000"
        self.assertFalse(self.evidence(tx)["spot_trade_eligible"])

    def test_publisher_classifies_cancellation_without_fake_fill(self):
        tx = self.cancel(); tx.update(tx_hash="cancel", tx_timestamp=2, block_height=2)
        agents = [{"id": "beacn", "name": "BEACN", "payment_cred": "owner"},
                  {"id": "grokbot", "name": "grokbot", "payment_cred": "other"}]
        result = build_moves(agents, {"cancel": tx}, {"beacn": ["order"], "grokbot": []})
        self.assertEqual(result[0]["kind"], "cancel")
        self.assertEqual(result[0]["fight_evidence"]["order_fee_status"], "verified")


if __name__ == "__main__":
    unittest.main()

"""Conservative, public-data-only realized spot P&L for the match animation.

This is a named average-cost accounting convention, not total-book P&L or a
score change. No prices, network calls, wallet access, or receipt valuation.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from copy import deepcopy
from decimal import Decimal, InvalidOperation, localcontext
from match_positions import LIQWID_MARKET_BY_POLICY, MINSWAP_ORDER_SCRIPT

METHOD = "separate_liquid_and_qUSDM_average_cost_including_fees"
SCOPE = "realized spot P&L; includes entry, order and allocated protocol fees, not total-book P&L"
SCALE = Decimal(1_000_000)
Q_USDM_POLICY = "9e00df0615de0a7b121a7f961d43e23165b8e81b64786c6eb708d370"
Q_USDM_NAME = ""
USDM_MARKET = "addr1wxd35v2m3fff5ah6rqq4stamqpp6n4fd7d2v5mq2fcrcl3s3kkuk7"
# The first is the publisher's pinned Minswap V2 pool. The second is the
# observed direct USDM pool script in all four current Grok acquisitions.
# A new venue requires an evidence-backed adapter; a borrow is not a spot buy.
MINSWAP_POOL_SCRIPT = "ea07b733d932129c378af627436e7cbc2ef0bf96e0036bb51b3bde6b"
DIRECT_USDM_POOL_SCRIPT = "d8b69fc53637bcfadbc4469083f706bc293f4d9d2296646c5ca167bb"
assert LIQWID_MARKET_BY_POLICY.get(Q_USDM_POLICY) == "USDM"


def _decimal(value):
    if isinstance(value, bool) or value is None:
        raise ValueError("missing or invalid monetary value")
    try:
        out = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError("invalid monetary value") from exc
    if not out.is_finite():
        raise ValueError("nonfinite monetary value")
    return out


def _raw(value):
    out = _decimal(value)
    if out != out.to_integral_value() or out < 0:
        raise ValueError("raw quantities must be nonnegative integers")
    return out


def _signed_raw(value):
    out = _decimal(value)
    if out != out.to_integral_value():
        raise ValueError("raw quantities must be integers")
    return out


def _assets(node):
    if not isinstance(node.get("asset_list"), list):
        raise ValueError("missing raw asset list")
    out = {}
    for a in node["asset_list"]:
        identity = (a["policy_id"], a["asset_name"])
        if identity in out:
            raise ValueError("duplicate asset identity")
        out[identity] = _raw(a["quantity"])
    return out


def _plain_conversion(tx, agent, ins, outs, *, usdm, da, du, dq, fee, zero_withdrawals):
    """Prove a plain supply/withdraw, excluding any loan/collateral leg."""
    def wallet(n):
        return (n.get("payment_addr") or {}).get("cred") == agent["payment_cred"]
    def market(n):
        return (n.get("payment_addr") or {}).get("bech32") == USDM_MARKET
    mi = [n for n in tx["inputs"] if market(n)]
    mo = [n for n in tx["outputs"] if market(n)]
    if (not ins or not outs or not all(wallet(n) for n in ins + outs) or
        len(mi) != 1 or len(mo) != 1 or
        any(not (wallet(n) or market(n)) for n in tx["inputs"] + tx["outputs"]) or
        da != -fee or fee <= 0 or du * dq >= 0 or tx.get("certificates") or
        not zero_withdrawals or _signed_raw(tx.get("deposit", 0)) != 0):
        raise ValueError("conversion is not plain wallet + pinned market with fee-only ADA loss")
    mint = tx.get("assets_minted")
    qid = (Q_USDM_POLICY, Q_USDM_NAME)
    if not isinstance(mint, list) or len(mint) != 1:
        raise ValueError("conversion requires exactly the pinned qUSDM mint/burn")
    if (mint[0].get("policy_id"), mint[0].get("asset_name")) != qid or _signed_raw(mint[0]["quantity"]) != dq:
        raise ValueError("conversion qUSDM mint/burn differs from owned qtoken change")
    before_assets, after_assets = _assets(mi[0]), _assets(mo[0])
    market_du = after_assets.get(usdm, Decimal(0)) - before_assets.get(usdm, Decimal(0))
    if market_du != -du or before_assets.get(qid, 0) or after_assets.get(qid, 0):
        raise ValueError("underlying flow or qUSDM destination fails market conservation")
    before_assets.pop(usdm, None); after_assets.pop(usdm, None)
    if before_assets != after_assets or _raw(mi[0]["value"]) != _raw(mo[0]["value"]):
        raise ValueError("conversion changes another market asset or market ADA")
    before = deepcopy(mi[0]["inline_datum"]["value"])
    after = mo[0]["inline_datum"]["value"]
    bi, ai = before["list"][0]["list"], after["list"][0]["list"]
    if len(bi) < 2 or len(bi) != len(ai):
        raise ValueError("unsupported market datum shape")
    # Only supplied underlying and qtoken supply may change. Every other
    # datum field must remain byte-for-byte structurally equal.
    if _signed_raw(ai[0]["int"]) - _signed_raw(bi[0]["int"]) != -du or \
       _signed_raw(ai[1]["int"]) - _signed_raw(bi[1]["int"]) != dq:
        raise ValueError("market supplied/qtoken datum deltas do not match conversion")
    bi[0] = deepcopy(ai[0]); bi[1] = deepcopy(ai[1])
    if before != after:
        raise ValueError("conversion changes a non-supply market datum field")
    return {"status": "verified", "action": "supply" if dq > 0 else "redeem",
            "market_address": USDM_MARKET, "qtoken_policy": Q_USDM_POLICY,
            "qtoken_name": Q_USDM_NAME, "market_usdm_delta_raw": str(market_du),
            "minted_qtoken_raw": str(dq), "market_datum_conserved": True}


def _spot_source(tx, order_addrs, *, usdm, da, du):
    if du == 0:
        return True
    pins = {MINSWAP_POOL_SCRIPT, DIRECT_USDM_POOL_SCRIPT}
    pi = [n for n in tx["inputs"] if (n.get("payment_addr") or {}).get("cred") in pins]
    po = [n for n in tx["outputs"] if (n.get("payment_addr") or {}).get("cred") in pins]
    if len(pi) != 1 or len(po) != 1 or pi[0]["payment_addr"] != po[0]["payment_addr"]:
        return False
    before, after = _assets(pi[0]), _assets(po[0])
    pu = after.pop(usdm, Decimal(0)) - before.pop(usdm, Decimal(0))
    pa = _raw(po[0]["value"]) - _raw(pi[0]["value"])
    if before != after or du * pu >= 0 or da * pa >= 0:
        return False
    our_minswap_order = pi[0]["payment_addr"]["cred"] == MINSWAP_POOL_SCRIPT and any(
        (n.get("payment_addr") or {}).get("bech32") in order_addrs and
        (n.get("payment_addr") or {}).get("cred") == MINSWAP_ORDER_SCRIPT for n in tx["inputs"])
    # Shared Minswap fills still pass the publisher's independent full-batch
    # fee/receiver checks. A direct trade must match the entire opposite pool leg.
    return our_minswap_order or pu == -du


def _effect(kind, *, status="not_applicable", reason="No realized spot disposal."):
    typ = ("position_conversion" if kind in {"supply", "redeem", "receipt"}
           else "trade_activity" if kind in {"swap", "fill"} else "none")
    return {"type": typ, "status": status, "ada": None,
            "cost_basis_ada": None, "net_proceeds_ada": None,
            "basis_method": METHOD, "claim_scope": SCOPE,
            "source_tx_hashes": [], "reason": reason}


def raw_fight_evidence(tx, agent, order_addrs, *, usdm_policy, usdm_name):
    """Extract integer cashflows and eligibility from the public raw tx.

    Only ADA, exact USDM and the pinned qUSDM receipt are supported. Receipt
    basis moves only through the proved plain conversion below.
    """
    def own(n):
        pa = n.get("payment_addr") or {}
        return pa.get("cred") == agent["payment_cred"] or pa.get("bech32") in order_addrs

    ev = {"version": 2, "spot_assets_only": False, "accounting_assets_only": False,
          "spot_trade_eligible": False,
          "zero_usdm_origin": False, "order_fee_status": "unknown",
          "receipt_conversion": {"status": "not_applicable"},
          "tx_block_index": tx.get("tx_block_index")}
    try:
        if not isinstance(tx.get("inputs"), list) or not isinstance(tx.get("outputs"), list):
            return ev
        ins = [n for n in tx["inputs"] if own(n)]
        outs = [n for n in tx["outputs"] if own(n)]
        if not tx["inputs"] or not tx["outputs"] or not (ins or outs):
            return ev
        def amounts(nodes):
            ada = usdm = q = Decimal(0)
            supported = True
            for n in nodes:
                ada += _raw(n["value"])
                for identity, qty in _assets(n).items():
                    if identity == (usdm_policy, usdm_name):
                        usdm += qty
                    elif identity == (Q_USDM_POLICY, Q_USDM_NAME):
                        q += qty
                    else:
                        supported = False
            return ada, usdm, q, supported
        ia, iu, iq, iok = amounts(ins)
        oa, ou, oq, ook = amounts(outs)
        paid = any((n.get("payment_addr") or {}).get("cred") == agent["payment_cred"] for n in ins)
        txfee = _raw(tx["fee"])
        # Cardano DEX scripts use zero-ADA withdrawals as validation hooks.
        # They are not reward income. Parse every amount; unknown is not zero.
        withdrawals = tx.get("withdrawals", [])
        zero_withdrawals = isinstance(withdrawals, list) and all(
            _raw(w["amount"]) == 0 for w in withdrawals)
        da, du, dq = oa - ia, ou - iu, oq - iq
        involves_order = any((n.get("payment_addr") or {}).get("bech32") in order_addrs for n in ins + outs)
        receipt_at_order = any((n.get("payment_addr") or {}).get("bech32") in order_addrs and
                               _assets(n).get((Q_USDM_POLICY, Q_USDM_NAME), 0) > 0 for n in ins + outs)
        fee_status = "not_applicable"
        if involves_order and du == 0:
            fee_status = ("verified" if iok and ook and not receipt_at_order and paid and txfee > 0 and
                          da == -txfee and dq == 0 and all(own(n) for n in tx["inputs"])
                          and not tx.get("certificates") and zero_withdrawals
                          and not tx.get("assets_minted") else "unknown")
        ev.update({"spot_assets_only": iok and ook and iq == 0 and oq == 0,
            "accounting_assets_only": iok and ook and not receipt_at_order,
            "spot_trade_eligible": iok and ook and not tx.get("certificates") and
                 zero_withdrawals and not tx.get("assets_minted") and
                 dq == 0 and _decimal(tx.get("deposit", 0)) == 0 and
                 _spot_source(tx, order_addrs, usdm=(usdm_policy, usdm_name), da=da, du=du),
            "zero_usdm_origin": not ins and bool(outs) and iok and ook and ou == 0 and oq == 0,
            "order_fee_status": fee_status,
            "ada_delta_raw": str(da), "usdm_delta_raw": str(du),
            "qtoken_delta_raw": str(dq), "input_qtoken_raw": str(iq),
            "input_usdm_raw": str(iu), "network_fee_raw": str(txfee if paid else Decimal(0))})
        if dq:
            try:
                if not (iok and ook and paid):
                    raise ValueError("unsupported owned asset or conversion payer")
                ev["receipt_conversion"] = _plain_conversion(tx, agent, ins, outs,
                    usdm=(usdm_policy, usdm_name), da=da, du=du, dq=dq,
                    fee=txfee, zero_withdrawals=zero_withdrawals)
            except (ValueError, KeyError, TypeError, AttributeError, IndexError) as exc:
                ev["receipt_conversion"] = {"status": "unknown", "reason": str(exc)}
    except (ValueError, KeyError, TypeError, AttributeError, IndexError):
        # Evidence failure only disables P&L. The existing move log remains.
        ev["spot_assets_only"] = False
        ev["accounting_assets_only"] = False
    return ev


def annotate_moves(moves, *, expected_liquid_usdm=None, expected_q_usdm_raw=None):
    """Return new move dicts, preserving input order and adding event_id/effect.

    ``fight_evidence`` is produced from the publisher's raw transaction inputs
    and outputs. Missing evidence fails closed. A zero-USDM funding origin is
    required. Unsupported movement permanently invalidates subsequent basis;
    an apparently empty wallet does not reset it. Earlier verified disposals
    remain valid, except whole-history corruption/reconciliation failure.
    """
    with localcontext() as ctx:
        ctx.prec = 28  # stable public output, independent of caller context
        return _annotate(moves, expected_liquid_usdm=expected_liquid_usdm,
                         expected_q_usdm_raw=expected_q_usdm_raw)


def _annotate(moves, *, expected_liquid_usdm, expected_q_usdm_raw):
    result = [dict(m, event_id=f"{m.get('agent')}:{m.get('tx_hash')}",
                   effect=_effect(m.get("kind"))) for m in moves]
    groups = defaultdict(list)
    for m in result:
        groups[m.get("agent")].append(m)
    for aid, rows in groups.items():
        fatal = None
        ids = [m.get("tx_hash") for m in rows]
        if any(not isinstance(v, str) or not v for v in ids) or len(set(ids)) != len(ids):
            fatal = "Missing or duplicate transaction identity in agent history."
        if any(type(m.get("block")) is not int or m["block"] < 1 or
               type(m.get("time")) is not int or m["time"] < 1 for m in rows):
            fatal = "Missing chain chronology in agent history."
        if fatal is None and expected_liquid_usdm is not None:
            try:
                expected = _decimal(expected_liquid_usdm[aid])
                observed = sum((_decimal(m["fight_evidence"]["usdm_delta_raw"])
                                for m in rows), Decimal(0)) / SCALE
                if expected < 0 or observed != expected:
                    fatal = "Replayed liquid USDM does not reconcile to the live book."
            except (ValueError, KeyError, TypeError):
                fatal = "Missing liquid-USDM reconciliation evidence."
        if fatal is None and expected_q_usdm_raw is not None:
            try:
                expected = _raw(expected_q_usdm_raw[aid])
                observed = sum((_signed_raw(m["fight_evidence"]["qtoken_delta_raw"])
                                for m in rows), Decimal(0))
                if observed != expected:
                    fatal = "Replayed qUSDM does not reconcile to the live wallet."
            except (ValueError, KeyError, TypeError):
                fatal = "Missing qUSDM reconciliation evidence."
        if fatal:
            for m in rows:
                m["effect"] = _effect(m.get("kind"), status="unknown", reason=fatal)
            continue

        block_counts = Counter(m["block"] for m in rows)
        block_indices = defaultdict(list)
        for m in rows:
            block_indices[m["block"]].append(m.get("fight_evidence", {}).get("tx_block_index"))
        ambiguous = {b for b, xs in block_indices.items() if block_counts[b] > 1 and
                     (any(type(x) is not int or x < 0 for x in xs) or len(set(xs)) != len(xs))}
        ordered = sorted(rows, key=lambda m: (m["block"],
                         m.get("fight_evidence", {}).get("tx_block_index")
                         if type(m.get("fight_evidence", {}).get("tx_block_index")) is int else -1))
        held = cost = qheld = qcost = Decimal(0)
        sources = []
        broken = None
        previous_time = 0
        for index, m in enumerate(ordered):
            kind, txid = m.get("kind"), m["tx_hash"]
            evidence = m.get("fight_evidence") or {}
            if m["block"] in ambiguous:
                broken = broken or "Transaction order within the same block is unproved."
            if m["time"] < previous_time:
                broken = broken or "Block and timestamp chronology disagree."
            previous_time = m["time"]
            if index == 0 and (kind != "fund" or evidence.get("zero_usdm_origin") is not True):
                broken = broken or "History does not begin with a proved zero-USDM funding origin."
            if evidence.get("version") != 2 or evidence.get("accounting_assets_only") is not True:
                broken = broken or "Owned raw assets are incomplete or outside ADA/USDM/pinned-qUSDM scope."
            if evidence.get("order_fee_status") not in {"verified", "unknown", "not_applicable"}:
                broken = broken or "Missing order-fee classification."
            if kind in {"swap", "fill"} and evidence.get("spot_trade_eligible") is not True:
                broken = broken or "Trade mixes an unsupported mint, withdrawal, certificate, or asset."
            try:
                da = _signed_raw(evidence["ada_delta_raw"]) / SCALE
                du = _signed_raw(evidence["usdm_delta_raw"]) / SCALE
                dq = _signed_raw(evidence["qtoken_delta_raw"])
                fee = _raw(evidence["network_fee_raw"]) / SCALE
                input_usdm = _raw(evidence["input_usdm_raw"]) / SCALE
                input_q = _raw(evidence["input_qtoken_raw"])
                # Public display values must agree with the raw evidence too.
                if da != _decimal(m["ada_delta"]) or du != _decimal(m["usdm_delta"]) or fee != _decimal(m["fee"]):
                    raise ValueError("display and raw evidence disagree")
                if input_usdm > held:
                    broken = broken or "Transaction spends more USDM than reconstructed history contains."
                if input_q > qheld:
                    broken = broken or "Transaction spends more qUSDM than reconstructed history contains."
            except (ValueError, KeyError, TypeError):
                broken = broken or "Missing or inconsistent raw monetary evidence."
            if broken:
                m["effect"] = _effect(kind, status="unknown", reason=broken)
                continue

            if dq != 0 or kind in {"supply", "redeem", "receipt"}:
                conversion = evidence.get("receipt_conversion") or {}
                action = "supply" if dq > 0 else "redeem"
                if (conversion.get("status") != "verified" or kind != action or
                    conversion.get("action") != action or dq == 0 or du * dq >= 0 or
                    da != -fee or fee <= 0):
                    broken = "Receipt movement is not a proved plain USDM/qUSDM conversion."
                elif dq > 0:
                    if held <= 0 or -du > held:
                        broken = "Supply exceeds supported liquid USDM."
                    else:
                        allocated = cost * (-du / held)
                        held += du; cost -= allocated
                        qheld += dq; qcost += allocated + fee
                elif qheld <= 0 or -dq > qheld:
                    broken = "Redemption exceeds supported qUSDM."
                else:
                    allocated = qcost * (-dq / qheld)
                    qheld += dq; qcost -= allocated
                    held += du; cost += allocated + fee
                if not broken:
                    sources.append(txid)
                    m["effect"] = _effect(kind, status="verified",
                        reason="Proved plain USDM/qUSDM conversion; basis transfers between positions, not realized ADA profit.")
                    m["effect"]["source_tx_hashes"] = list(dict.fromkeys(sources))
                    m["effect"]["conversion_accounting"] = {
                        "basis_transferred_ada": str(allocated), "protocol_fee_ada": str(fee),
                        "liquid_usdm_after": str(held), "liquid_basis_ada_after": str(cost),
                        "qtoken_raw_after": str(qheld), "qtoken_basis_ada_after": str(qcost)}
            elif evidence.get("order_fee_status") == "unknown":
                broken = "Order placement/cancellation fee attribution is unproved."
            elif evidence.get("order_fee_status") == "verified":
                if du != 0 or da != -fee or fee <= 0:
                    broken = "Order fee does not conserve the supported book."
                else:
                    cost += fee
                    sources.append(txid)
                    m["effect"]["reason"] = "Order fee added to spot basis; no trade has completed."
            elif kind in {"swap", "fill"} and du > 0 and da < 0:
                held += du
                cost -= da  # already includes paid network/batcher fees
                sources.append(txid)
                m["effect"] = _effect(kind, status="verified",
                    reason="Opened/increased a spot position; cash spent is not realized profit.")
            elif kind in {"swap", "fill"} and du < 0 and da > 0:
                if -du > held or held <= 0:
                    broken = "Disposal exceeds the supported USDM inventory."
                else:
                    basis = cost * (-du / held)
                    pnl = da - basis
                    m["effect"] = {**_effect(kind), "type": "realized_spot_pnl",
                        "status": "verified", "ada": str(pnl),
                        "cost_basis_ada": str(basis), "net_proceeds_ada": str(da),
                        "source_tx_hashes": list(dict.fromkeys(sources + [txid])),
                        "reason": "Net ADA proceeds minus allocated average spot basis; not match points."}
                    held += du
                    cost -= basis
                    sources.append(txid)
            elif du != 0 or kind in {"swap", "fill", "order"}:
                broken = "Unsupported transfer, trade shape, or unproved order fee."
            if broken:
                m["effect"] = _effect(kind, status="unknown", reason=broken)
    return result

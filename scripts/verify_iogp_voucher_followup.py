#!/usr/bin/env python3
"""Verify the committed IOGP/voucher follow-up receipts."""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SMALL = ROOT / "data" / "small"


def rows(name: str) -> list[dict[str, str]]:
    path = SMALL / name
    if not path.exists():
        raise SystemExit(f"ERROR: missing {path.relative_to(ROOT)}")
    return list(csv.DictReader(path.open(newline="")))


def one(items: list[dict[str, str]], **wanted: str) -> dict[str, str]:
    matched = [
        row for row in items
        if all(row.get(key) == value for key, value in wanted.items())
    ]
    if len(matched) != 1:
        raise SystemExit(f"ERROR: expected one row for {wanted}, found {len(matched)}")
    return matched[0]


def main() -> None:
    registration = rows("iogp_pool_registration.csv")
    reg = one(
        registration,
        pool_id_bech32="pool1x5ge78ks6jc0j8nsfwyqqhk2ukxlkvz7zxlm9utgk6405hh490n",
    )
    assert reg["ticker_name"] == "IOGP"
    assert reg["declared_pledge_lovelace"] == "1000000000000"
    assert reg["registration_tx_hash"] == (
        "17765cd5600e70becc1356b48f370e8623f9a3b89e247b94e77b141a54254ac9"
    )

    stake = rows("iogp_pool_epoch_stake.csv")
    assert one(stake, epoch_no="250", stake_role="reward_account")[
        "active_stake_lovelace"
    ] == "66360281121632"
    assert one(stake, epoch_no="255", stake_role="reward_account")[
        "active_stake_lovelace"
    ] == "64363477004344"
    assert one(stake, epoch_no="290", stake_role="reward_account")[
        "active_stake_lovelace"
    ] == "0"

    profile = rows("voucher_wallet_profile.csv")
    if len(profile) != 1:
        raise SystemExit(f"ERROR: expected one voucher profile row, found {len(profile)}")
    p = profile[0]
    assert p["stake_address"] == (
        "stake1u9c07x9z7w35zmm5tumm5lpltdjpma8gx95y9vw7e35j67gz7r8a7"
    )
    assert p["address_utxos"] == "519"
    assert p["stake_address_count"] == "6"
    assert p["stake_received_lovelace"] == "176449088336762"

    delegations = rows("voucher_wallet_delegations.csv")
    delegation = one(
        delegations,
        pool_id_bech32="pool1mxqjlrfskhd5kql9kak06fpdh8xjwc76gec76p3taqy2qmfzs5z",
    )
    assert delegation["ticker_name"] == "IOG1"
    assert delegation["certificate_tx_hash"] == (
        "816507d47b5b6ca9b414fcab11e730e719b59e8b24f941f631353fa97d8a5eee"
    )

    flows = rows("voucher_wallet_counterparty_summary.csv")
    assert one(
        flows,
        direction="inbound",
        counterparty="stake1uy6yzwsxxc28lfms0qmpxvyz9a7y770rtcqx9y96m42cttqwvp4m5",
    )["associated_lovelace"] == "52196773895086"
    assert one(
        flows,
        direction="outbound",
        counterparty="addr1vymu4620q8vqf4xsstfrk6dy72787syvezet8ujsdj2k3jsfvlx47",
    )["associated_lovelace"] == "60000003141590"
    assert one(
        flows,
        direction="inbound",
        counterparty="stake1u90z89xl6qkgt0lpn79svmpmz9evstxy4wfp8wgpyfcgg5seurw78",
    )["associated_lovelace"] == "13280311000000"
    assert one(
        flows,
        direction="outbound",
        counterparty="stake1u90z89xl6qkgt0lpn79svmpmz9evstxy4wfp8wgpyfcgg5seurw78",
    )["associated_lovelace"] == "13280301175115"

    traces = rows("iog_voucher_dominant_traces.csv")
    genesis = "0ae3da29711600e94a33fb7441d2e76876a9a1e98b5ebdefbf2e3bc535617616"
    expected_depths = {
        "voucher_funding_1": "27",
        "voucher_funding_2": "26",
        "voucher_funding_3": "64",
    }
    for label, depth in expected_depths.items():
        terminal = max(
            (r for r in traces if r["seed_label"] == label),
            key=lambda r: int(r["depth"]),
        )
        assert terminal["depth"] == depth
        assert terminal["hop_tx_hash"] == genesis

    destinations = rows("iogp_reward_wallet_destinations.csv")
    burst = one(
        destinations,
        destination="stake1uycla9q3glrugp48cq2r7awemjxepvj4lxs4emw5qmpsclc4tpe52",
    )
    assert burst["transaction_count"] == "32"
    assert burst["output_lovelace"] == "925000100000000"

    funder_sources = rows("voucher_funder_source_summary.csv")
    assert one(
        funder_sources,
        funder_stake_address="stake1u8nynuagsfkjfsjfhm57dnyzfae8e5szh4rfdxjk2drt53qwhz039",
        source="stake1ux9vw6azy95waz9l3e8dme7pwmhcn68f77kqd245uxw57nqr9upaa",
    )["associated_lovelace"] == "1793844822538"
    assert one(
        funder_sources,
        funder_stake_address="stake1u8nynuagsfkjfsjfhm57dnyzfae8e5szh4rfdxjk2drt53qwhz039",
        source="stake1u8tl8t5pdr9qn488vc9dpehklntt55au96fkqpd8nr28qyqzr7lax",
    )["associated_lovelace"] == "1775775359025"

    tips = {
        row["source_tip_block"]
        for name in (
            "iogp_pool_registration.csv",
            "iogp_pool_epoch_stake.csv",
            "voucher_wallet_profile.csv",
            "voucher_wallet_delegations.csv",
            "voucher_wallet_counterparty_summary.csv",
            "iog_voucher_dominant_traces.csv",
            "iogp_reward_wallet_destinations.csv",
            "voucher_funder_delegations.csv",
            "voucher_funder_source_summary.csv",
        )
        for row in rows(name)
    }
    assert tips == {"13520244"}

    total_rows = sum(
        len(rows(name))
        for name in (
            "iogp_pool_registration.csv",
            "iogp_pool_epoch_stake.csv",
            "voucher_wallet_profile.csv",
            "voucher_wallet_delegations.csv",
            "voucher_wallet_counterparty_summary.csv",
            "iog_voucher_dominant_traces.csv",
            "iogp_reward_wallet_destinations.csv",
            "voucher_funder_delegations.csv",
            "voucher_funder_source_summary.csv",
        )
    )
    print(f"IOGP/voucher receipts OK: 9 tables, {total_rows} rows")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Verify the committed Genesis Trail case receipts."""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SMALL = ROOT / "data" / "small"
GENESIS_TX = "0ae3da29711600e94a33fb7441d2e76876a9a1e98b5ebdefbf2e3bc535617616"


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
    outputs = rows("genesis_trail_recipient_outputs.csv")
    assert len(outputs) == 11
    payment_sized = [r for r in outputs if r["is_payment_sized"] == "t"]
    assert len(payment_sized) == 9
    assert sum(int(r["value_lovelace"]) for r in outputs) == 184837022651928

    inputs = rows("genesis_trail_payment_inputs.csv")
    assert len({r["payment_tx_hash"] for r in inputs}) == 9
    assert {r["payer"] for r in inputs} == {
        "stake1uy807crqvtpr0qq0ccvptgsvfvpaul2x3ae4vxlgcegrwgs4mltrr",
        "stake1u9hvz2uxyt75fk470k9r2zy54puk90q729f8gnte8dl5k4g30c5zh",
        "stake1uxt2ggq005kfm3uwe89emy3ka2zgdtrpxfarvz6033l3fqgve6ku2",
        "stake1u8wh6mjgfxhlvq3fn2mzzcds8l3cps0hmhh48ktp8lcfjhsmrsyww",
    }

    forwarding = rows("genesis_trail_recipient_forwarding.csv")
    assert len(forwarding) == 10
    assert sum(int(r["value_lovelace"]) for r in forwarding) == 184837020994894

    hub_rows = rows("genesis_trail_hub_summary.csv")
    if len(hub_rows) != 1:
        raise SystemExit(f"ERROR: expected one hub row, found {len(hub_rows)}")
    hub = hub_rows[0]
    assert hub["deposit_outputs"] == "807"
    assert hub["received_lovelace"] == "9849508503491169"

    bridges = rows("genesis_trail_stream_bridges.csv")
    expected = {
        "iogp_reward_to_burst": ("32", "925000100000000"),
        "burst_to_hub": ("33", "925000294515631"),
        "recipient_to_hub": ("10", "184837020994894"),
        "same_hub_stream_54m": ("4", "53999997336236"),
        "same_hub_stream_2m": ("4", "2200009336236"),
    }
    for label, (tx_count, lovelace) in expected.items():
        row = one(bridges, stream_label=label)
        assert row["transaction_count"] == tx_count
        assert row["output_lovelace"] == lovelace

    traces = rows("genesis_trail_payment_dominant_traces.csv")
    expected_depths = {
        "payment_2021_04_02": 28,
        "payment_2021_04_26": 28,
        "payment_2021_05_24": 26,
        "payment_2021_06_28": 28,
        "payment_2021_07_26": 29,
        "payment_2021_08_29": 25,
        "payment_2021_09_27": 27,
        "payment_2021_10_25": 28,
        "payment_2021_11_22": 26,
    }
    for label, depth in expected_depths.items():
        terminal = max(
            (r for r in traces if r["seed_label"] == label),
            key=lambda r: int(r["depth"]),
        )
        assert int(terminal["depth"]) == depth
        assert terminal["hop_tx_hash"] == GENESIS_TX

    table_names = (
        "genesis_trail_recipient_outputs.csv",
        "genesis_trail_payment_inputs.csv",
        "genesis_trail_recipient_forwarding.csv",
        "genesis_trail_hub_summary.csv",
        "genesis_trail_stream_bridges.csv",
        "genesis_trail_payment_dominant_traces.csv",
    )
    tips = {
        row["source_tip_block"]
        for name in table_names
        for row in rows(name)
    }
    assert tips == {"13520244"}
    total_rows = sum(len(rows(name)) for name in table_names)
    print(f"Genesis Trail receipts OK: 6 tables, {total_rows} rows")


if __name__ == "__main__":
    main()

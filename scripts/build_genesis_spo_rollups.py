#!/usr/bin/env python3
"""Build committed SPO-side rollups from the Genesis-to-SPO surface export.

Inputs:
  data/release/genesis_current_spo_surface.csv   (release asset, not committed)
  data/small/governance_pool_metadata.csv        (committed; ticker/name enrichment)

Outputs (committed):
  data/small/governance_genesis_spo_by_pool.csv      root x pool rollup of traced
                                                     current value, deduped by UTxO
  data/small/governance_genesis_pool_drep_matrix.csv pool x DRep cross-tab, top rows
                                                     by deduped traced current value

Evidence boundary: delegation targets are on-chain observations, not custody,
ownership, identity, or intent claims.
"""
from __future__ import annotations

from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
SURFACE = ROOT / "data/release/genesis_current_spo_surface.csv"
POOL_META = ROOT / "data/small/governance_pool_metadata.csv"
BY_POOL = ROOT / "data/small/governance_genesis_spo_by_pool.csv"
POOL_DREP = ROOT / "data/small/governance_genesis_pool_drep_matrix.csv"

MATRIX_TOP_N = 500


def main() -> None:
    if not SURFACE.exists():
        raise SystemExit(
            f"Missing release input: {SURFACE.relative_to(ROOT)}\n"
            "Rebuild it with scripts/build_genesis_spo_surface_remote.sh "
            "or download the release assets."
        )
    con = duckdb.connect()
    con.execute(
        f"CREATE VIEW surface AS SELECT * FROM read_csv_auto('{SURFACE.as_posix()}', header=true, "
        "types={'snapshot_utc': 'VARCHAR'})"
    )
    con.execute(
        f"CREATE VIEW pool_meta AS SELECT * FROM read_csv_auto('{POOL_META.as_posix()}', header=true)"
    )

    # Dedup by UTxO before summing: a UTxO reached by several roots keeps one
    # value row, with the root combination preserved for provenance.
    con.execute("""
        CREATE VIEW dedup AS
        SELECT
          max(snapshot_utc) AS snapshot_utc,
          max(trace_schema) AS trace_schema,
          tx_id,
          tx_out_index,
          string_agg(DISTINCT root_seed_id, '+' ORDER BY root_seed_id) AS root_combo,
          max(value_lovelace) AS value_lovelace,
          min(min_depth) AS min_depth,
          max(stake_address) AS stake_address,
          max(latest_pool_id_bech32) AS latest_pool_id_bech32,
          max(pool_active_epoch_no) AS pool_active_epoch_no,
          max(latest_drep_id_bech32) AS latest_drep_id_bech32
        FROM surface
        GROUP BY tx_id, tx_out_index
    """)

    con.execute(f"""
        COPY (
          SELECT
            max(d.snapshot_utc) AS snapshot_utc,
            max(d.trace_schema) AS trace_schema,
            d.root_combo,
            coalesce(d.latest_pool_id_bech32, 'NOT_DELEGATED_OR_NO_STAKE') AS latest_pool_id_bech32,
            max(m.ticker_name) AS ticker_name,
            max(m.pool_name) AS pool_name,
            count(*) AS dedup_current_utxos,
            count(DISTINCT d.stake_address) AS distinct_stake_addresses,
            sum(d.value_lovelace) AS dedup_current_lovelace,
            round(sum(d.value_lovelace) / 1000000.0, 6) AS dedup_current_ada,
            min(d.min_depth) AS min_trace_depth,
            max(d.pool_active_epoch_no) AS latest_pool_active_epoch
          FROM dedup d
          LEFT JOIN pool_meta m ON m.pool_id_bech32 = d.latest_pool_id_bech32
          GROUP BY d.root_combo, coalesce(d.latest_pool_id_bech32, 'NOT_DELEGATED_OR_NO_STAKE')
          ORDER BY dedup_current_lovelace DESC
        ) TO '{BY_POOL.as_posix()}' (HEADER, DELIMITER ',')
    """)

    con.execute(f"""
        COPY (
          SELECT
            max(d.snapshot_utc) AS snapshot_utc,
            max(d.trace_schema) AS trace_schema,
            coalesce(d.latest_pool_id_bech32, 'NOT_DELEGATED_OR_NO_STAKE') AS latest_pool_id_bech32,
            max(m.ticker_name) AS ticker_name,
            coalesce(d.latest_drep_id_bech32, 'NO_DREP_DELEGATION') AS latest_drep_id_bech32,
            count(*) AS dedup_current_utxos,
            count(DISTINCT d.stake_address) AS distinct_stake_addresses,
            sum(d.value_lovelace) AS dedup_current_lovelace,
            round(sum(d.value_lovelace) / 1000000.0, 6) AS dedup_current_ada
          FROM dedup d
          LEFT JOIN pool_meta m ON m.pool_id_bech32 = d.latest_pool_id_bech32
          GROUP BY coalesce(d.latest_pool_id_bech32, 'NOT_DELEGATED_OR_NO_STAKE'),
                   coalesce(d.latest_drep_id_bech32, 'NO_DREP_DELEGATION')
          ORDER BY dedup_current_lovelace DESC
          LIMIT {MATRIX_TOP_N}
        ) TO '{POOL_DREP.as_posix()}' (HEADER, DELIMITER ',')
    """)

    for path in (BY_POOL, POOL_DREP):
        rows = con.execute(
            "SELECT count(*) FROM read_csv_auto(?, header=true)", [str(path)]
        ).fetchone()[0]
        print(f"wrote {path.relative_to(ROOT)} rows={rows}")


if __name__ == "__main__":
    main()

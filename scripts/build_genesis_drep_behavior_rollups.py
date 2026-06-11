#!/usr/bin/env python3
"""Build public rollups from the Genesis governance surface export."""
from __future__ import annotations

import json
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
RELEASE = ROOT / "data/release"
SMALL = ROOT / "data/small"
SURFACE = RELEASE / "genesis_current_governance_surface.csv"
VOTES = RELEASE / "governance_drep_votes.csv"
SIGNALS_FULL_CSV = RELEASE / "governance_genesis_behavior_signals_full.csv"
SIGNALS_TOP_CSV = SMALL / "governance_genesis_behavior_signals_top.csv"


def run_copy(con: duckdb.DuckDBPyConnection, sql: str, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    con.execute(f"COPY ({sql}) TO ? (HEADER, DELIMITER ',')", [str(out)])
    print(f"wrote {out.relative_to(ROOT)}")


def sql_string(value: Path) -> str:
    return "'" + str(value).replace("'", "''") + "'"


def main() -> None:
    if not SURFACE.exists():
        raise SystemExit(f"missing {SURFACE.relative_to(ROOT)}")

    con = duckdb.connect()
    con.execute(f"CREATE OR REPLACE VIEW surface AS SELECT * FROM read_csv_auto({sql_string(SURFACE)}, union_by_name=true)")

    if VOTES.exists():
        con.execute(f"CREATE OR REPLACE VIEW votes AS SELECT * FROM read_csv_auto({sql_string(VOTES)}, union_by_name=true)")
    else:
        con.execute("""
            CREATE OR REPLACE VIEW votes AS
            SELECT
              NULL::BIGINT AS gov_action_proposal_id,
              NULL::BIGINT AS drep_hash_id,
              NULL::VARCHAR AS vote
            WHERE false
        """)

    con.execute("""
        CREATE OR REPLACE VIEW block_events AS
        SELECT
          min_depth,
          output_block_no,
          count(DISTINCT stake_address_id) FILTER (WHERE stake_address_id IS NOT NULL) AS block_stake_peers,
          count(*) AS block_trace_rows,
          sum(value_lovelace) AS block_lovelace
        FROM surface
        WHERE output_block_no IS NOT NULL
        GROUP BY min_depth, output_block_no
    """)

    con.execute("""
        CREATE OR REPLACE VIEW epoch_drep_events AS
        SELECT
          min_depth,
          output_epoch_no,
          latest_drep_hash_id,
          count(DISTINCT stake_address_id) FILTER (WHERE stake_address_id IS NOT NULL) AS epoch_drep_stake_peers,
          count(*) AS epoch_drep_trace_rows,
          sum(value_lovelace) AS epoch_drep_lovelace
        FROM surface
        WHERE output_epoch_no IS NOT NULL
          AND latest_drep_hash_id IS NOT NULL
        GROUP BY min_depth, output_epoch_no, latest_drep_hash_id
    """)

    con.execute("""
        CREATE OR REPLACE VIEW drep_vote_activity AS
        SELECT
          drep_hash_id,
          count(DISTINCT gov_action_proposal_id) AS voted_proposal_count,
          count(*) AS vote_row_count,
          count(*) FILTER (WHERE vote = 'Yes') AS yes_vote_count,
          count(*) FILTER (WHERE vote = 'No') AS no_vote_count,
          count(*) FILTER (WHERE vote = 'Abstain') AS abstain_vote_count
        FROM votes
        WHERE drep_hash_id IS NOT NULL
        GROUP BY drep_hash_id
    """)

    con.execute("""
        CREATE OR REPLACE VIEW stake_roots AS
        SELECT
          stake_address_id,
          count(DISTINCT root_seed_id) AS root_count,
          string_agg(DISTINCT root_seed_id, '+' ORDER BY root_seed_id) AS root_combo
        FROM surface
        WHERE stake_address_id IS NOT NULL
        GROUP BY stake_address_id
    """)

    con.execute("""
        CREATE OR REPLACE VIEW stake_utxos AS
        SELECT
          stake_address_id,
          stake_address,
          latest_drep_id_bech32,
          latest_drep_hash_id,
          latest_vote_epoch,
          tx_id,
          tx_out_index,
          max(value_lovelace) AS value_lovelace,
          min(min_depth) AS min_depth,
          max(min_depth) AS max_depth,
          max(output_block_no) AS output_block_no,
          max(output_block_time_utc) AS output_block_time_utc
        FROM surface
        WHERE stake_address_id IS NOT NULL
        GROUP BY
          stake_address_id,
          stake_address,
          latest_drep_id_bech32,
          latest_drep_hash_id,
          latest_vote_epoch,
          tx_id,
          tx_out_index
    """)

    con.execute("""
        CREATE OR REPLACE VIEW stake_base AS
        SELECT
          (SELECT max(snapshot_utc) FROM surface) AS snapshot_utc,
          (SELECT max(trace_schema) FROM surface) AS trace_schema,
          u.stake_address_id,
          u.stake_address,
          u.latest_drep_id_bech32,
          u.latest_drep_hash_id,
          u.latest_vote_epoch,
          r.root_count,
          r.root_combo,
          count(*) AS current_utxos,
          sum(u.value_lovelace) AS current_lovelace,
          round(sum(u.value_lovelace) / 1000000.0, 6) AS current_ada,
          min(u.min_depth) AS min_depth,
          max(u.max_depth) AS max_depth,
          count(DISTINCT u.output_block_no) FILTER (WHERE u.output_block_no IS NOT NULL) AS output_block_count,
          min(u.output_block_no) AS first_output_block_no,
          max(u.output_block_no) AS latest_output_block_no,
          min(u.output_block_time_utc) AS first_output_time_utc,
          max(u.output_block_time_utc) AS latest_output_time_utc
        FROM stake_utxos u
        JOIN stake_roots r ON r.stake_address_id = u.stake_address_id
        GROUP BY
          u.stake_address_id,
          u.stake_address,
          u.latest_drep_id_bech32,
          u.latest_drep_hash_id,
          u.latest_vote_epoch,
          r.root_count,
          r.root_combo
    """)

    con.execute("""
        CREATE OR REPLACE VIEW stake_block_stats AS
        SELECT
          s.stake_address_id,
          count(DISTINCT s.output_block_no) FILTER (WHERE b.block_stake_peers >= 2) AS same_block_event_count,
          max(b.block_stake_peers) AS max_same_block_stake_peers,
          max(b.block_trace_rows) AS max_same_block_trace_rows,
          max(b.block_lovelace) AS max_same_block_lovelace
        FROM surface s
        JOIN block_events b
          ON b.min_depth = s.min_depth
         AND b.output_block_no = s.output_block_no
        WHERE s.stake_address_id IS NOT NULL
        GROUP BY s.stake_address_id
    """)

    con.execute("""
        CREATE OR REPLACE VIEW stake_epoch_drep_stats AS
        SELECT
          s.stake_address_id,
          count(DISTINCT (s.output_epoch_no, s.min_depth, s.latest_drep_hash_id))
            FILTER (WHERE e.epoch_drep_stake_peers >= 2) AS same_epoch_drep_event_count,
          max(e.epoch_drep_stake_peers) AS max_same_epoch_drep_stake_peers,
          max(e.epoch_drep_trace_rows) AS max_same_epoch_drep_trace_rows
        FROM surface s
        JOIN epoch_drep_events e
          ON e.min_depth = s.min_depth
         AND e.output_epoch_no = s.output_epoch_no
         AND e.latest_drep_hash_id = s.latest_drep_hash_id
        WHERE s.stake_address_id IS NOT NULL
        GROUP BY s.stake_address_id
    """)

    con.execute("""
        CREATE OR REPLACE VIEW raw_signals AS
        SELECT
          b.*,
          coalesce(bs.same_block_event_count, 0) AS same_block_event_count,
          coalesce(bs.max_same_block_stake_peers, 0) AS max_same_block_stake_peers,
          coalesce(bs.max_same_block_trace_rows, 0) AS max_same_block_trace_rows,
          coalesce(bs.max_same_block_lovelace, 0) AS max_same_block_lovelace,
          coalesce(es.same_epoch_drep_event_count, 0) AS same_epoch_drep_event_count,
          coalesce(es.max_same_epoch_drep_stake_peers, 0) AS max_same_epoch_drep_stake_peers,
          coalesce(es.max_same_epoch_drep_trace_rows, 0) AS max_same_epoch_drep_trace_rows,
          coalesce(va.voted_proposal_count, 0) AS voted_proposal_count,
          coalesce(va.vote_row_count, 0) AS drep_vote_row_count,
          coalesce(va.yes_vote_count, 0) AS drep_yes_vote_count,
          coalesce(va.no_vote_count, 0) AS drep_no_vote_count,
          coalesce(va.abstain_vote_count, 0) AS drep_abstain_vote_count,
          CASE WHEN coalesce(bs.same_block_event_count, 0) >= 2 THEN 3
               WHEN coalesce(bs.same_block_event_count, 0) = 1 THEN 2
               ELSE 0 END AS same_block_points,
          CASE WHEN coalesce(es.same_epoch_drep_event_count, 0) >= 1 THEN 2 ELSE 0 END AS delegation_sync_points,
          CASE WHEN b.root_count >= 2 THEN 4 ELSE 0 END AS cross_root_points,
          CASE WHEN b.latest_drep_hash_id IS NOT NULL THEN 1 ELSE 0 END AS current_drep_points,
          CASE WHEN coalesce(va.voted_proposal_count, 0) > 0 THEN 1 ELSE 0 END AS governance_activity_points,
          CASE WHEN coalesce(bs.max_same_block_trace_rows, 0) >= 1000
                  OR coalesce(bs.max_same_block_stake_peers, 0) >= 100
               THEN -5 ELSE 0 END AS service_like_penalty,
          CASE WHEN b.current_utxos >= 100 AND b.root_count = 1 THEN -3 ELSE 0 END AS fragmentation_penalty
        FROM stake_base b
        LEFT JOIN stake_block_stats bs ON bs.stake_address_id = b.stake_address_id
        LEFT JOIN stake_epoch_drep_stats es ON es.stake_address_id = b.stake_address_id
        LEFT JOIN drep_vote_activity va ON va.drep_hash_id = b.latest_drep_hash_id
    """)

    con.execute("""
        CREATE OR REPLACE VIEW scored_signals AS
        WITH scored AS (
          SELECT
            *,
            same_block_points + delegation_sync_points + cross_root_points + current_drep_points + governance_activity_points AS positive_signal_score,
            service_like_penalty + fragmentation_penalty AS negative_signal_score,
            same_block_points + delegation_sync_points + cross_root_points + current_drep_points + governance_activity_points
              + service_like_penalty + fragmentation_penalty AS behavior_score
          FROM raw_signals
        )
        SELECT
          *,
          concat_ws(';',
            CASE WHEN same_block_points > 0 THEN 'same_block_hop' ELSE NULL END,
            CASE WHEN delegation_sync_points > 0 THEN 'same_epoch_drep_cohort' ELSE NULL END,
            CASE WHEN cross_root_points > 0 THEN 'cross_root_current_cluster' ELSE NULL END,
            CASE WHEN current_drep_points > 0 THEN 'current_drep_delegation' ELSE NULL END,
            CASE WHEN governance_activity_points > 0 THEN 'drep_has_proposal_votes' ELSE NULL END,
            CASE WHEN service_like_penalty < 0 THEN 'service_like_batch_penalty' ELSE NULL END,
            CASE WHEN fragmentation_penalty < 0 THEN 'fragmentation_penalty' ELSE NULL END
          ) AS behavior_flags,
          CASE
            WHEN service_like_penalty <= -5 THEN 'custodian_or_service_like'
            WHEN behavior_score >= 10 AND cross_root_points > 0 AND same_block_points > 0 THEN 'high_confidence_retained_like'
            WHEN behavior_score >= 8 AND cross_root_points > 0 THEN 'probable_retained_like'
            WHEN behavior_score >= 5 THEN 'coordinated_like'
            WHEN behavior_score >= 2 THEN 'weak_behavior_signal'
            ELSE 'trace_only'
          END AS confidence_class,
          CASE
            WHEN service_like_penalty <= -5 THEN 90
            WHEN behavior_score >= 10 AND cross_root_points > 0 AND same_block_points > 0 THEN 80
            WHEN behavior_score >= 8 AND cross_root_points > 0 THEN 70
            WHEN behavior_score >= 5 THEN 60
            WHEN behavior_score >= 2 THEN 50
            ELSE 10
          END AS confidence_rank,
          'heuristic_v1_public_signals' AS scoring_model
        FROM scored
    """)

    signals_sql = """
        SELECT
          snapshot_utc,
          trace_schema,
          stake_address_id,
          stake_address,
          latest_drep_id_bech32,
          latest_drep_hash_id,
          latest_vote_epoch,
          root_count,
          root_combo,
          current_utxos,
          current_lovelace,
          current_ada,
          min_depth,
          max_depth,
          output_block_count,
          first_output_block_no,
          latest_output_block_no,
          first_output_time_utc,
          latest_output_time_utc,
          same_block_event_count,
          max_same_block_stake_peers,
          max_same_block_trace_rows,
          same_epoch_drep_event_count,
          max_same_epoch_drep_stake_peers,
          voted_proposal_count,
          drep_vote_row_count,
          same_block_points,
          delegation_sync_points,
          cross_root_points,
          current_drep_points,
          governance_activity_points,
          service_like_penalty,
          fragmentation_penalty,
          positive_signal_score,
          negative_signal_score,
          behavior_score,
          behavior_flags,
          confidence_class,
          confidence_rank,
          scoring_model
        FROM scored_signals
        ORDER BY behavior_score DESC, current_lovelace DESC, stake_address
    """
    run_copy(con, signals_sql, SIGNALS_FULL_CSV)
    run_copy(con, f"SELECT * FROM ({signals_sql}) WHERE behavior_score >= 5", SIGNALS_TOP_CSV)

    con.execute("""
        CREATE OR REPLACE VIEW current_dedup AS
        SELECT
          max(s.snapshot_utc) AS snapshot_utc,
          max(s.trace_schema) AS trace_schema,
          s.latest_drep_id_bech32,
          s.latest_drep_hash_id,
          s.drep_distribution_epoch,
          s.drep_voting_power_lovelace,
          s.tx_id,
          s.tx_out_index,
          max(s.stake_address_id) AS stake_address_id,
          max(s.stake_address) AS stake_address,
          max(s.value_lovelace) AS dedup_lovelace,
          count(DISTINCT s.root_seed_id) AS root_count,
          string_agg(DISTINCT s.root_seed_id, '+' ORDER BY s.root_seed_id) AS root_combo,
          count(DISTINCT s.stake_address_id) FILTER (WHERE s.stake_address_id IS NOT NULL) AS stake_credentials,
          min(s.min_depth) AS min_depth,
          max(s.min_depth) AS max_depth,
          CASE
            WHEN bool_or(s.behavior_class = 'no_stake_or_byron') THEN 'no_stake_or_byron'
            ELSE coalesce(arg_max(sig.confidence_class, sig.confidence_rank), 'trace_only')
          END AS behavior_class
        FROM surface s
        LEFT JOIN scored_signals sig ON sig.stake_address_id = s.stake_address_id
        GROUP BY
          s.latest_drep_id_bech32,
          s.latest_drep_hash_id,
          s.drep_distribution_epoch,
          s.drep_voting_power_lovelace,
          s.tx_id,
          s.tx_out_index
    """)

    run_copy(con, """
        SELECT
          max(snapshot_utc) AS snapshot_utc,
          max(trace_schema) AS trace_schema,
          latest_drep_id_bech32,
          latest_drep_hash_id,
          drep_distribution_epoch,
          drep_voting_power_lovelace,
          round(drep_voting_power_lovelace / 1000000.0, 6) AS drep_voting_power_ada,
          behavior_class,
          count(*) AS dedup_current_utxos,
          sum(stake_credentials) AS dedup_current_stake_credentials,
          sum(dedup_lovelace) AS dedup_current_lovelace,
          round(sum(dedup_lovelace) / 1000000.0, 6) AS dedup_current_ada,
          round(
            CASE
              WHEN drep_voting_power_lovelace IS NULL OR drep_voting_power_lovelace = 0 THEN NULL
              ELSE sum(dedup_lovelace) / drep_voting_power_lovelace
            END,
            8
          ) AS trace_value_to_drep_power_ratio,
          min(min_depth) AS min_depth,
          max(max_depth) AS max_depth,
          string_agg(DISTINCT root_combo, '; ' ORDER BY root_combo) AS root_overlap_summary
        FROM current_dedup
        GROUP BY
          latest_drep_id_bech32,
          latest_drep_hash_id,
          drep_distribution_epoch,
          drep_voting_power_lovelace,
          behavior_class
        ORDER BY dedup_current_lovelace DESC NULLS LAST, latest_drep_id_bech32 NULLS LAST, behavior_class
    """, SMALL / "governance_genesis_behavior_by_drep.csv")

    run_copy(con, """
        SELECT
          max(s.snapshot_utc) AS snapshot_utc,
          max(s.trace_schema) AS trace_schema,
          s.root_seed_id,
          s.latest_drep_id_bech32,
          s.latest_drep_hash_id,
          s.drep_distribution_epoch,
          s.drep_voting_power_lovelace,
          round(s.drep_voting_power_lovelace / 1000000.0, 6) AS drep_voting_power_ada,
          coalesce(sig.confidence_class, s.behavior_class) AS behavior_class,
          count(*) AS current_trace_rows,
          count(DISTINCT (s.tx_id, s.tx_out_index)) AS current_utxos,
          count(DISTINCT s.stake_address_id) FILTER (WHERE s.stake_address_id IS NOT NULL) AS current_stake_credentials,
          sum(s.value_lovelace) AS current_lovelace,
          round(sum(s.value_lovelace) / 1000000.0, 6) AS current_ada,
          min(s.min_depth) AS min_depth,
          max(s.min_depth) AS max_depth
        FROM surface s
        LEFT JOIN scored_signals sig ON sig.stake_address_id = s.stake_address_id
        GROUP BY
          s.root_seed_id,
          s.latest_drep_id_bech32,
          s.latest_drep_hash_id,
          s.drep_distribution_epoch,
          s.drep_voting_power_lovelace,
          coalesce(sig.confidence_class, s.behavior_class)
        ORDER BY current_lovelace DESC NULLS LAST, root_seed_id, latest_drep_id_bech32 NULLS LAST, behavior_class
    """, SMALL / "governance_genesis_behavior_by_root_drep.csv")

    run_copy(con, """
        SELECT
          snapshot_utc,
          trace_schema,
          stake_address_id,
          stake_address,
          latest_drep_id_bech32,
          latest_drep_hash_id,
          latest_vote_epoch,
          confidence_class AS behavior_class,
          behavior_score,
          behavior_flags,
          root_count,
          root_combo,
          current_utxos,
          current_lovelace,
          current_ada,
          min_depth,
          max_depth,
          output_block_count,
          same_block_event_count,
          max_same_block_stake_peers,
          same_epoch_drep_event_count,
          max_same_epoch_drep_stake_peers,
          voted_proposal_count
        FROM scored_signals
        ORDER BY behavior_score DESC, current_lovelace DESC, current_utxos DESC, stake_address
        LIMIT 1000
    """, SMALL / "governance_genesis_behavior_clusters.csv")

    if VOTES.exists():
        run_copy(con, """
            SELECT
              max(d.snapshot_utc) AS snapshot_utc,
              max(d.trace_schema) AS trace_schema,
              v.gov_action_proposal_id,
              v.proposal_tx_hash,
              v.proposal_index,
              v.proposal_type,
              v.proposal_expiration_epoch,
              d.latest_drep_id_bech32,
              v.vote,
              v.vote_epoch,
              v.vote_time_utc,
              v.vote_tx_hash,
              d.behavior_class,
              count(*) AS dedup_current_utxos,
              sum(d.dedup_lovelace) AS dedup_current_lovelace,
              round(sum(d.dedup_lovelace) / 1000000.0, 6) AS dedup_current_ada,
              string_agg(DISTINCT d.root_combo, '; ' ORDER BY d.root_combo) AS root_overlap_summary
            FROM current_dedup d
            JOIN votes v ON v.drep_hash_id = d.latest_drep_hash_id
            WHERE d.latest_drep_hash_id IS NOT NULL
            GROUP BY
              v.gov_action_proposal_id,
              v.proposal_tx_hash,
              v.proposal_index,
              v.proposal_type,
              v.proposal_expiration_epoch,
              d.latest_drep_id_bech32,
              v.vote,
              v.vote_epoch,
              v.vote_time_utc,
              v.vote_tx_hash,
              d.behavior_class
            ORDER BY v.vote_time_utc DESC, dedup_current_lovelace DESC, d.latest_drep_id_bech32
        """, SMALL / "governance_genesis_behavior_by_proposal.csv")

    manifest = {
        "schema_version": 1,
        "surface": SURFACE.relative_to(ROOT).as_posix(),
        "proposal_votes": VOTES.relative_to(ROOT).as_posix() if VOTES.exists() else None,
        "scoring_model": {
            "name": "heuristic_v1_public_signals",
            "unit": "stake credential cluster",
            "positive_points": {
                "same_block_hop_once": 2,
                "same_block_hop_repeated": 3,
                "same_epoch_drep_cohort": 2,
                "cross_root_current_cluster": 4,
                "current_drep_delegation": 1,
                "drep_has_proposal_votes": 1
            },
            "negative_points": {
                "service_like_batch_penalty": -5,
                "fragmentation_penalty": -3
            },
            "confidence_classes": {
                "trace_only": "trace membership with no behavior score",
                "weak_behavior_signal": "behavior_score >= 2",
                "coordinated_like": "behavior_score >= 5",
                "probable_retained_like": "behavior_score >= 8 and cross-root current cluster",
                "high_confidence_retained_like": "behavior_score >= 10 plus cross-root and same-block signals",
                "custodian_or_service_like": "service-like batching penalty triggered"
            }
        },
        "rollups": [
            "data/small/governance_genesis_behavior_signals_top.csv",
            "data/small/governance_genesis_behavior_by_drep.csv",
            "data/small/governance_genesis_behavior_by_root_drep.csv",
            "data/small/governance_genesis_behavior_clusters.csv",
            "data/small/governance_genesis_behavior_by_proposal.csv",
        ],
        "release_artifacts": [
            "data/release/governance_genesis_behavior_signals_full.csv"
        ],
        "classification_default": "trace_only unless positive/negative public behavior signals are present; no-stake rows remain no_stake_or_byron",
        "ownership_boundary": "DRep delegation is voting power, not custody or beneficial ownership.",
    }
    out = ROOT / "data/manifests/genesis-drep-behavior-manifest.json"
    out.write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"wrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

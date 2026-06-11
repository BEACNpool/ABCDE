# Limitations and Non-Attribution

This project maps on-chain flows. It does not prove legal ownership, intent, misconduct, or contractual breach.

Byron-era shared infrastructure is a major confounder. Co-spends and shared routing may indicate shared administration or custody without proving shared beneficial ownership.

Exchange and custodian labels must be treated as heuristic unless backed by explicit public/on-chain evidence.

## Snapshot Freshness

The committed clone-and-query database is a reproducible snapshot, not a live
chain index. Check `data/small/db_tip_receipt.csv` or the `build_info` table
before answering any question about "current" DRep voting power, live-unspent
status, proposal votes, stake pool delegation, or epoch-specific state.

The current receipt records the abcde warehouse at block `13520244`, epoch `635`,
time `2026-06-07 18:44:37`. The replica was known to be stalled there pending
relay db-sync recovery. Until a newer receipt is committed, all current-state
surfaces must be described as that snapshot.

## Depth-Bounded Traces

Depth-14 staged traces are lineage surfaces, not identity surfaces. A row being
reached by a founder trace means the on-chain lineage reached that row under the
published depth and filter rules. It does not prove custody, beneficial
ownership, legal control, or intent.

## Behavior Scores

`heuristic_v1_public_signals` is an audit-prioritization model over public
signals such as same-block events, same-epoch DRep cohorts, cross-root current
clusters, current DRep delegation, and proposal vote activity. These scores rank
rows for review; they are not conclusions.

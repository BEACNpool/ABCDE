# Findings Index

Findings are audit artifacts, not standalone narratives. Each finding must carry a claim grade and be reproducible from committed receipts, generated DuckDB tables, or release-artifact manifests.

Labels are defined in `docs/02_GRADING.md`.

## Verified / current v2 findings

1. [F01 — Named founder allocations](F01_named_founder_allocations.md) — `VERIFIED`, `FACT`
2. [F02 — Fourth-entry first-spend operational convergence](F02_fourth_entry_first_spend_convergence.md) — `VERIFIED`, `FACT + STRONG_INFERENCE`
3. [F02b — Fourth-entry direct co-spend](F02b_fourth_entry_direct_cospend.md) — `VERIFIED`, `FACT`
4. [F03 — Fourth-entry sale-ticket origin signal](F03_fourth_entry_sale_ticket_origin_signal.md) — `VERIFIED`, `FACT + STRONG_INFERENCE`
5. [F06 — SPO and DRep delegation targets](F06_governance_delegation_targets.md) — `VERIFIED`, `FACT`
6. [F09 — IOGP pledge and voucher-address follow-up](F09_iogp_voucher_followup.md) — `VERIFIED`, `FACT + STRONG_INFERENCE`
7. [F10 — Genesis Trail monthly stream and consolidation hub](F10_genesis_trail_monthly_stream.md) — `VERIFIED`, `FACT + STRONG_INFERENCE`
8. [F11 — Eight-key 35M-ADA custody cohort](F11_eight_key_35m_custody_cohort.md) — `VERIFIED`, `FACT + STRONG_INFERENCE`
9. [F12 — High-throughput unstaked 213.8M-ADA bag](F12_high_throughput_unstaked_bag.md) — `VERIFIED`, `FACT + STRONG_INFERENCE`
10. [F13 — Reward-plumbing fleet, exchange-scale hubs, and genesis→tracer-mapped-exchange bridge](F13_reward_plumbing_downstream_and_tracer_bridge.md) — `VERIFIED`, `FACT + STRONG_INFERENCE`
11. [F14 — Fleet is the same 35M-parcel institutional custody structure (~50 keys, ~1.69B ADA)](F14_fleet_is_same_35m_parcel_structure.md) — `VERIFIED`, `FACT + STRONG_INFERENCE`
12. [F15 — Reward-plumbing operation is a closed 115-key component; ~1.694B ADA floor](F15_plumbing_component_is_closed_floor.md) — `VERIFIED`, `FACT + STRONG_INFERENCE`

### Companion module — NIGHT token

13. [F16 — NIGHT genesis mint provenance and supply concentration](F16_night_mint_provenance_and_concentration.md) — `VERIFIED`, `FACT + STRONG_INFERENCE`

## Review cuts / candidate sets

8. [F04 — Bounded depth-3 trace overlap review cut](F04_bounded_trace_overlap_pilot.md) — `REVIEW_CUT`, `FACT within bounded scope`
9. [F05 — Bounded depth-3 merge inventory review cut](F05_bounded_trace_merge_inventory_pilot.md) — `REVIEW_CUT`, `FACT within bounded scope`
10. [F07 — Staged trace extraction and founder merge candidate set](F07_staged_trace_extraction.md) — `CANDIDATE_SET`, requires classification before stronger claims
11. [F08 — IOG current bag audit cut](F08_iog_current_bag_audit_cut.md) — `REVIEW_CUT`, `FACT within depth-14 trace scope`

## Audit backlog

Open questions and refutation tests live in `AUDIT_BACKLOG.md`. They should graduate into findings only after receipt-backed classification.

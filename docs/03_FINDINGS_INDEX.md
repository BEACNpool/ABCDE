# Findings Index

| ID | Grade | Canonical file | Primary evidence | Query |
|---|---|---|---|---|
| F01 | FACT | `findings/F01_emurgo2_operational_convergence.md` | `evidence/markdown/emurgo2_convergence_evidence_2026-04-08.md` | `queries/validation/emurgo2_direct_merge_checks.sql` |
| F02 | FACT | `findings/F02_founder_redemption_timeline.md` | `evidence/csv/emurgo2_anchor_metadata_2026-04-08.csv` | `queries/validation/emurgo2_classification_checks.sql` |
| F03 | FACT | `findings/F03_cross_seed_consuming_transactions.md` | `evidence/csv/cross_seed_consuming_transactions_2026-04-06.csv` | `queries/validation/cross_entity_merge_validation.sql` |
| F04 | FACT | `findings/F04_clean_three_way_merge.md` | `evidence/csv/triply_shared_tx_inputs_2026-04-08.csv` | `queries/validation/cross_entity_merge_validation.sql` |
| F05 | FACT | `findings/F05_shared_58_output_splitter.md` | `evidence/csv/byron_splitter_evidence.csv` | `queries/core/bridge_input_creator_table_step1.sql` |
| F06 | FACT | `findings/F06_synchronized_delegation_swarm.md` | `evidence/reports/cross_entity_summary_amended_2026-04-06.md` | `queries/core/iog_epoch_245_252_routing.sql` |
| F07 | HEURISTIC | `findings/F07_exchange_liquidation.md` | `investigation/archived_notes/genesis_exchange_liquidation_report.md` | `data/raw/exchange-analysis/README.md` |
| F08 | STRONG INFERENCE | `findings/F08_558b_mystery_exchange_address.md` | `investigation/worklog/NEXT_STEPS.md` | `investigation/open_questions/02_hub1_operator.md` |
| F09 | FACT | `findings/F09_genesis_concentration.md` | `investigation/archived_findings/MASTER_FINDINGS.md` | `data/raw/iog/trace_summary.json` |
| A01 | FACT | `findings/A01_emurgo2_frontier_identity.md` | `evidence/overlaps/emurgo2_frontier_overlap_2026-04-08.csv` | `queries/validation/emurgo2_direct_merge_checks.sql` |
| A02 | FACT | `findings/A02_emurgo2_direct_merge_epoch4.md` | `evidence/csv/emurgo2_first_spend_2026-04-08.csv` | `queries/validation/emurgo2_direct_merge_checks.sql` |
| A03 | FACT | `findings/A03_convergence_transaction_c8596b9c.md` | `evidence/csv/emurgo2_first_spend_2026-04-08.csv` | `queries/validation/emurgo2_direct_merge_checks.sql` |
| A04 | FACT | `findings/A04_epoch250_iog_emurgo_merge_batch.md` | `evidence/csv/cross_seed_consuming_transactions_annotated_2026-04-08.csv` | `queries/validation/cross_entity_merge_validation.sql` |
| A05 | FACT | `findings/A05_twenty_two_three_way_stake_credentials.md` | `evidence/overlaps/all_three_stake_credential_detail_2026-04-08.csv` | `queries/validation/cross_entity_merge_validation.sql` |
| A06 | FACT | `findings/A06_primary_beneficiary_stake1uxttvx739.md` | `evidence/csv/triply_shared_tx_outputs_2026-04-08.csv` | `queries/validation/cross_entity_merge_validation.sql` |
| A07 | FACT | `findings/A07_shared_1376b_utxo.md` | `evidence/csv/focal_source_outputs_in_571f_2026-04-06.csv` | `queries/validation/cross_entity_merge_validation.sql` |
| A08 | FACT | `findings/A08_iog_emurgo_merge_span.md` | `evidence/csv/cross_seed_consuming_transactions_2026-04-06.csv` | `queries/validation/cross_entity_merge_validation.sql` |
| A09 | FACT | `findings/A09_bridge_accumulator_before_three_way_merge.md` | `investigation/archived_notes/bridge_path_to_three_way_merge_2026-04-08.md` | `scripts/analysis/tag_creator_feeders_with_seed_traces.py` |
| A10 | FACT | `findings/A10_f907b625_structured_peel_chain.md` | `investigation/archived_notes/f907b625_cf_emurgo_peel_chain_2026-04-08.md` | `queries/validation/f907b625_peel_chain_checks.sql` |
| A11 | FACT | `findings/A11_corrected_named_pool_overlap.md` | `evidence/overlaps/pool_overlap_chain_wide_2026-04-08.csv` | `queries/core/iog_epoch_245_252_routing.sql` |
| B01 | FACT | `findings/B01_f907b625_2b_disbursement_chain.md` | `evidence/csv/trace_150m_disbursements_2026-04-10.csv` | `queries/core/trace_150m_disbursements.sql` |
| B02 | FACT | `findings/B02_200m_unspent_branch.md` | `evidence/dossiers/disbursement_recipients_attribution_2026-04-10.csv` | `queries/validation/disbursement_recipients_attribution.sql` |
| B03 | FACT | `findings/B03_non_bridge_inputs_to_571f776c.md` | `evidence/csv/clean_three_way_direct_input_breakdown_2026-04-06.csv` | `queries/validation/cross_entity_merge_validation.sql` |
| B04 | FACT | `findings/B04_emurgo2_anchor_confirmation.md` | `evidence/csv/emurgo2_anchor_metadata_2026-04-08.csv` | `queries/validation/emurgo2_classification_checks.sql` |
| B05 | FACT | `findings/B05_bridge_creator_single_seed_pattern.md` | `evidence/csv/bridge_creator_summary_result_c_2026-04-08.csv` | `scripts/analysis/tag_creator_feeders_with_seed_traces.py` |
| B06 | FACT | `findings/B06_first_clean_pairwise_merge_details.md` | `evidence/csv/first_clean_merges_metadata_2026-04-08.csv` | `queries/validation/cross_entity_merge_validation.sql` |
| B07 | FACT | `findings/B07_2b_residual_to_known_splitter.md` | `evidence/csv/trace_150m_agg_2026-04-10.csv` | `queries/core/trace_150m_disbursements_agg.sql` |
| B08 | FACT | `findings/B08_emurgo_pool_ticker_confirmation.md` | `evidence/csv/named_pool_ticker_list_2026-04-08.csv` | `queries/core/iog_epoch_245_252_routing.sql` |
| B09 | FACT | `findings/B09_stake1uxztgcgh_merge_orchestrator.md` | `evidence/dossiers/stake1uxztgcgh_dossier_2026-04-10.csv` | `queries/validation/stake1uxztgcgh_dossier.sql` |
| B10 | FACT | `findings/B10_emurgo_cf_first_clean_merge_is_dust.md` | `evidence/csv/first_clean_merges_metadata_2026-04-08.csv` | `queries/validation/cross_entity_merge_validation.sql` |
| B11 | FACT | `findings/B11_stake1u9zjr6e37_exchange_routing.md` | `evidence/dossiers/disbursement_recipients_attribution_2026-04-10.csv` | `queries/validation/disbursement_recipients_attribution.sql` |
| B12 | FACT | `findings/B12_staging_wallet_count_correction.md` | `investigation/archived_findings/FULL_FINDINGS_2026-04-10_ADDENDUM.md` | `queries/core/trace_150m_disbursements.sql` |
| B13 | FACT | `findings/B13_simultaneous_epoch237_sweep.md` | `evidence/csv/trace_150m_disbursements_2026-04-10.csv` | `queries/core/trace_150m_disbursements.sql` |
| B14 | FACT | `findings/B14_terminal_exchange_hot_wallet.md` | `evidence/dossiers/disbursement_recipients_attribution_2026-04-10.csv` | `queries/validation/disbursement_recipients_attribution.sql` |
| B15 | FACT | `findings/B15_master_disbursement_node.md` | `investigation/archived_findings/FULL_FINDINGS_2026-04-10_ADDENDUM.md` | `queries/core/trace_150m_disbursements.sql` |
| B16 | FACT | `findings/B16_f907b625_output_correction.md` | `investigation/archived_findings/FULL_FINDINGS_2026-04-10_ADDENDUM.md` | `queries/core/trace_150m_correct_joins.sql` |
| B17 | FACT | `findings/B17_fourteenth_staging_wallet.md` | `investigation/archived_findings/FULL_FINDINGS_2026-04-10_ADDENDUM.md` | `queries/core/trace_150m_disbursements.sql` |
| B18 | FACT | `findings/B18_binance_on_chain_delegation_confirmation.md` | `investigation/archived_findings/MASTER_FINDINGS.md` | `queries/validation/disbursement_recipients_attribution.sql` |

# Evidence Index

## F01 , EMURGO_2 operational convergence
- Canonical finding: `findings/F01_emurgo2_operational_convergence.md`
- Primary evidence: `evidence/markdown/emurgo2_convergence_evidence_2026-04-08.md`
- Primary SQL: `queries/validation/emurgo2_direct_merge_checks.sql`

## F02 , Founder redemption timeline
- Canonical finding: `findings/F02_founder_redemption_timeline.md`
- Primary evidence: `evidence/csv/emurgo2_anchor_metadata_2026-04-08.csv`
- Primary SQL: `queries/validation/emurgo2_classification_checks.sql`

## F03 , Cross-seed consuming transactions
- Canonical finding: `findings/F03_cross_seed_consuming_transactions.md`
- Primary evidence: `evidence/csv/cross_seed_consuming_transactions_2026-04-06.csv`
- Primary SQL: `queries/validation/cross_entity_merge_validation.sql`

## F04 , Clean three-way merge
- Canonical finding: `findings/F04_clean_three_way_merge.md`
- Primary evidence: `evidence/csv/triply_shared_tx_inputs_2026-04-08.csv`
- Primary SQL: `queries/validation/cross_entity_merge_validation.sql`

## F05 , Shared 58-output splitter
- Canonical finding: `findings/F05_shared_58_output_splitter.md`
- Primary evidence: `evidence/csv/byron_splitter_evidence.csv`
- Primary SQL: `queries/core/bridge_input_creator_table_step1.sql`

## F06 , Synchronized delegation swarm
- Canonical finding: `findings/F06_synchronized_delegation_swarm.md`
- Primary evidence: `evidence/reports/cross_entity_summary_amended_2026-04-06.md`
- Primary SQL: `queries/core/iog_epoch_245_252_routing.sql`

## F07 , Exchange liquidation
- Canonical finding: `findings/F07_exchange_liquidation.md`
- Primary evidence: `investigation/archived_notes/genesis_exchange_liquidation_report.md`
- Primary SQL: `data/raw/exchange-analysis/README.md`

## F08 , 558B mystery exchange address
- Canonical finding: `findings/F08_558b_mystery_exchange_address.md`
- Primary evidence: `investigation/worklog/NEXT_STEPS.md`
- Primary SQL: `investigation/open_questions/02_hub1_operator.md`

## F09 , Genesis concentration
- Canonical finding: `findings/F09_genesis_concentration.md`
- Primary evidence: `investigation/archived_findings/MASTER_FINDINGS.md`
- Primary SQL: `data/raw/iog/trace_summary.json`

## A01 , EMURGO_2 frontier identity
- Canonical finding: `findings/A01_emurgo2_frontier_identity.md`
- Primary evidence: `evidence/overlaps/emurgo2_frontier_overlap_2026-04-08.csv`
- Primary SQL: `queries/validation/emurgo2_direct_merge_checks.sql`

## A02 , EMURGO_2 direct merge epoch 4
- Canonical finding: `findings/A02_emurgo2_direct_merge_epoch4.md`
- Primary evidence: `evidence/csv/emurgo2_first_spend_2026-04-08.csv`
- Primary SQL: `queries/validation/emurgo2_direct_merge_checks.sql`

## A03 , Convergence transaction c8596b9c
- Canonical finding: `findings/A03_convergence_transaction_c8596b9c.md`
- Primary evidence: `evidence/csv/emurgo2_first_spend_2026-04-08.csv`
- Primary SQL: `queries/validation/emurgo2_direct_merge_checks.sql`

## A04 , Epoch 250 IOG and EMURGO merge batch
- Canonical finding: `findings/A04_epoch250_iog_emurgo_merge_batch.md`
- Primary evidence: `evidence/csv/cross_seed_consuming_transactions_annotated_2026-04-08.csv`
- Primary SQL: `queries/validation/cross_entity_merge_validation.sql`

## A05 , Twenty-two three-way stake credentials
- Canonical finding: `findings/A05_twenty_two_three_way_stake_credentials.md`
- Primary evidence: `evidence/overlaps/all_three_stake_credential_detail_2026-04-08.csv`
- Primary SQL: `queries/validation/cross_entity_merge_validation.sql`

## A06 , Primary beneficiary stake1uxttvx739
- Canonical finding: `findings/A06_primary_beneficiary_stake1uxttvx739.md`
- Primary evidence: `evidence/csv/triply_shared_tx_outputs_2026-04-08.csv`
- Primary SQL: `queries/validation/cross_entity_merge_validation.sql`

## A07 , Shared 1.376B UTxO
- Canonical finding: `findings/A07_shared_1376b_utxo.md`
- Primary evidence: `evidence/csv/focal_source_outputs_in_571f_2026-04-06.csv`
- Primary SQL: `queries/validation/cross_entity_merge_validation.sql`

## A08 , IOG and EMURGO merge span
- Canonical finding: `findings/A08_iog_emurgo_merge_span.md`
- Primary evidence: `evidence/csv/cross_seed_consuming_transactions_2026-04-06.csv`
- Primary SQL: `queries/validation/cross_entity_merge_validation.sql`

## A09 , Bridge accumulator before three-way merge
- Canonical finding: `findings/A09_bridge_accumulator_before_three_way_merge.md`
- Primary evidence: `investigation/archived_notes/bridge_path_to_three_way_merge_2026-04-08.md`
- Primary SQL: `scripts/analysis/tag_creator_feeders_with_seed_traces.py`

## A10 , f907b625 structured peel chain
- Canonical finding: `findings/A10_f907b625_structured_peel_chain.md`
- Primary evidence: `investigation/archived_notes/f907b625_cf_emurgo_peel_chain_2026-04-08.md`
- Primary SQL: `queries/validation/f907b625_peel_chain_checks.sql`

## A11 , Corrected named pool overlap
- Canonical finding: `findings/A11_corrected_named_pool_overlap.md`
- Primary evidence: `evidence/overlaps/pool_overlap_chain_wide_2026-04-08.csv`
- Primary SQL: `queries/core/iog_epoch_245_252_routing.sql`

## B01 , f907b625 2B disbursement chain
- Canonical finding: `findings/B01_f907b625_2b_disbursement_chain.md`
- Primary evidence: `evidence/csv/trace_150m_disbursements_2026-04-10.csv`
- Primary SQL: `queries/core/trace_150m_disbursements.sql`

## B02 , 200M unspent branch
- Canonical finding: `findings/B02_200m_unspent_branch.md`
- Primary evidence: `evidence/dossiers/disbursement_recipients_attribution_2026-04-10.csv`
- Primary SQL: `queries/validation/disbursement_recipients_attribution.sql`

## B03 , Non-bridge inputs to 571f776c
- Canonical finding: `findings/B03_non_bridge_inputs_to_571f776c.md`
- Primary evidence: `evidence/csv/clean_three_way_direct_input_breakdown_2026-04-06.csv`
- Primary SQL: `queries/validation/cross_entity_merge_validation.sql`

## B04 , EMURGO_2 anchor confirmation
- Canonical finding: `findings/B04_emurgo2_anchor_confirmation.md`
- Primary evidence: `evidence/csv/emurgo2_anchor_metadata_2026-04-08.csv`
- Primary SQL: `queries/validation/emurgo2_classification_checks.sql`

## B05 , Bridge creator single-seed pattern
- Canonical finding: `findings/B05_bridge_creator_single_seed_pattern.md`
- Primary evidence: `evidence/csv/bridge_creator_summary_result_c_2026-04-08.csv`
- Primary SQL: `scripts/analysis/tag_creator_feeders_with_seed_traces.py`

## B06 , First clean pairwise merge details
- Canonical finding: `findings/B06_first_clean_pairwise_merge_details.md`
- Primary evidence: `evidence/csv/first_clean_merges_metadata_2026-04-08.csv`
- Primary SQL: `queries/validation/cross_entity_merge_validation.sql`

## B07 , 2B residual to known splitter
- Canonical finding: `findings/B07_2b_residual_to_known_splitter.md`
- Primary evidence: `evidence/csv/trace_150m_agg_2026-04-10.csv`
- Primary SQL: `queries/core/trace_150m_disbursements_agg.sql`

## B08 , EMURGO pool ticker confirmation
- Canonical finding: `findings/B08_emurgo_pool_ticker_confirmation.md`
- Primary evidence: `evidence/csv/named_pool_ticker_list_2026-04-08.csv`
- Primary SQL: `queries/core/iog_epoch_245_252_routing.sql`

## B09 , stake1uxztgcgh merge orchestrator
- Canonical finding: `findings/B09_stake1uxztgcgh_merge_orchestrator.md`
- Primary evidence: `evidence/dossiers/stake1uxztgcgh_dossier_2026-04-10.csv`
- Primary SQL: `queries/validation/stake1uxztgcgh_dossier.sql`

## B10 , EMURGO and CF first clean merge is dust
- Canonical finding: `findings/B10_emurgo_cf_first_clean_merge_is_dust.md`
- Primary evidence: `evidence/csv/first_clean_merges_metadata_2026-04-08.csv`
- Primary SQL: `queries/validation/cross_entity_merge_validation.sql`

## B11 , stake1u9zjr6e37 exchange routing
- Canonical finding: `findings/B11_stake1u9zjr6e37_exchange_routing.md`
- Primary evidence: `evidence/dossiers/disbursement_recipients_attribution_2026-04-10.csv`
- Primary SQL: `queries/validation/disbursement_recipients_attribution.sql`

## B12 , Staging wallet count correction
- Canonical finding: `findings/B12_staging_wallet_count_correction.md`
- Primary evidence: `investigation/archived_findings/FULL_FINDINGS_2026-04-10_ADDENDUM.md`
- Primary SQL: `queries/core/trace_150m_disbursements.sql`

## B13 , Simultaneous epoch 237 sweep
- Canonical finding: `findings/B13_simultaneous_epoch237_sweep.md`
- Primary evidence: `evidence/csv/trace_150m_disbursements_2026-04-10.csv`
- Primary SQL: `queries/core/trace_150m_disbursements.sql`

## B14 , Terminal exchange hot wallet
- Canonical finding: `findings/B14_terminal_exchange_hot_wallet.md`
- Primary evidence: `evidence/dossiers/disbursement_recipients_attribution_2026-04-10.csv`
- Primary SQL: `queries/validation/disbursement_recipients_attribution.sql`

## B15 , Master disbursement node
- Canonical finding: `findings/B15_master_disbursement_node.md`
- Primary evidence: `investigation/archived_findings/FULL_FINDINGS_2026-04-10_ADDENDUM.md`
- Primary SQL: `queries/core/trace_150m_disbursements.sql`

## B16 , f907b625 output correction
- Canonical finding: `findings/B16_f907b625_output_correction.md`
- Primary evidence: `investigation/archived_findings/FULL_FINDINGS_2026-04-10_ADDENDUM.md`
- Primary SQL: `queries/core/trace_150m_correct_joins.sql`

## B17 , Fourteenth staging wallet
- Canonical finding: `findings/B17_fourteenth_staging_wallet.md`
- Primary evidence: `investigation/archived_findings/FULL_FINDINGS_2026-04-10_ADDENDUM.md`
- Primary SQL: `queries/core/trace_150m_disbursements.sql`

## B18 , Binance on-chain delegation confirmation
- Canonical finding: `findings/B18_binance_on_chain_delegation_confirmation.md`
- Primary evidence: `investigation/archived_findings/MASTER_FINDINGS.md`
- Primary SQL: `queries/validation/disbursement_recipients_attribution.sql`

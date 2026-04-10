-- ============================================================
-- Refresh EMURGO_2 wording after 2026-04-08 reclassification
-- Run as a table owner or admin role.
--
-- Purpose:
--   Update the already-loaded reference tables so they match the
--   revised investigation framing:
--   - 781,381,495 ADA entry fully converged with EMURGO cluster
--   - amount was public pre-launch
--   - current best classification is sale-ticket-sized entry,
--     not proven second founder allocation
-- ============================================================

BEGIN;

UPDATE public.genesis_investigation_findings
SET
    title = '781,381,495 ADA Genesis Entry Fully Converged With EMURGO Cluster',
    grade = 'FACT',
    summary = 'A 781,381,495 ADA genesis entry redeemed by tx 5ec95a53... later became operationally indistinguishable from the main EMURGO cluster. The first downstream spend is already a direct co-spend with an EMURGO-derived UTxO in tx c8596b9c..., and the line later shows 100% downstream Shelley stake-address overlap (6,216 / 6,216) plus an identical current-unspent frontier (49,089 / 49,089 shared dest_tx_out_id values).',
    evidence = 'Anchor TX: 5ec95a53fa3bb7dc56864bb6e75f369f00aa20e8d8cdc3b66b2fb88ec1b225ef | Redeemed to: DdzFFzCqrhspiThx6UaeJASmHTbwbXp2FtdCkF9AU9QXPF9D8sUC7Fqrv9bmYkxradBbqMrSxukTTsqCPNPwRh5PHazdiwWTuJYVMMaf | direct_merge_tx: c8596b9cd81f734f8129604ff86f23bd4a910465acb84ad9e9d1ac223ccb4a76 | emurgo_input_branch: 743fd051...#0 | earliest_shared_address_with_emurgo: DdzFFzCqrhsu3iF6JfUTaapdWq2mXVRFukkS28WFYVDEqkgaaYttH8cT32credS99L5GaoUsEquqEPNH7ae88eKuDL6XsK5ZL56jkfLi | shared_current_unspent_dest_tx_out_id_count: 49089/49089'
WHERE finding_id = 'F01';

UPDATE public.genesis_investigation_findings
SET
    title = 'Named Founder Redemptions Occurred Within 24 Hours; 781M Entry Followed 5 Minutes After EMURGO',
    grade = 'FACT',
    summary = 'IOG, EMURGO, and CF redeemed their named allocations on Sept 27–28 2017, the first 24 hours of mainnet. A separate 781,381,495 ADA genesis entry (5ec95a53...) redeemed 5 minutes after the main EMURGO redemption.',
    evidence = 'IOG: fa2d2a70... epoch 0 2017-09-27 16:20 UTC | CF: 208c7d54... epoch 0 2017-09-28 09:33 | EMURGO: 242608fc... epoch 0 2017-09-28 10:04 | 781M entry: 5ec95a53... epoch 0 2017-09-28 10:09'
WHERE finding_id = 'F02';

UPDATE public.genesis_entity_allocations
SET
    notes = 'Tracked separately for clustering. Exact amount was public in sale/genesis data pre-launch and matches the published maximum single ticket amount. First downstream spend is a direct co-spend with an EMURGO-derived UTxO in tx c8596b9c..., and the later trace fully converges with EMURGO (6216/6216 stake addrs, 49089/49089 current frontier outputs).'
WHERE entity = 'EMURGO_2';

UPDATE public.genesis_key_transactions
SET
    label = '781M Genesis Entry Redemption',
    notes = '781,381,495 ADA entry redeemed 5 min after EMURGO. Public amount was visible pre-launch; current best classification is a sale-ticket-sized genesis entry whose first downstream spend directly co-spends with an EMURGO-derived branch before later becoming fully merged with the EMURGO pipeline'
WHERE tx_hash = '5ec95a53fa3bb7dc56864bb6e75f369f00aa20e8d8cdc3b66b2fb88ec1b225ef';

UPDATE public.genesis_investigation_notes
SET
    title = 'Identify the original holder of the 781,381,495 ADA entry',
    body = 'Public-source review now indicates the 781,381,495 ADA amount was visible pre-launch in official sale stats and genesis files, and that it matches the published maximum single ticket amount. Its first downstream spend directly co-spends with an EMURGO-derived branch, but original beneficial ownership at redemption is still unresolved. The live question is whether the original holder was EMURGO, an affiliate, or an unrelated buyer whose funds entered the same custody stack almost immediately. Anchor TX: 5ec95a53...',
    updated_at = NOW()
WHERE category = 'NEXT_STEP'
  AND title = 'Cross-reference EMURGO_2 against public disclosures';

UPDATE public.genesis_investigation_notes
SET
    body = 'Create a timeline diagram showing: genesis (Sept 2017) → 781M entry redemption (5 min after EMURGO) → hop-1 shared EMURGO address (2017-10-18) → first IOG+EMURGO merge (Jan 2019) → first CF merges (May 2020) → synchronized delegation swarm (Jan–Mar 2021) → clean 3-way merge (Feb 2021) → ongoing hub activity (2025). This is the most accessible summary of the findings.',
    updated_at = NOW()
WHERE category = 'NEXT_STEP'
  AND title = 'Produce visual merge timeline for public publication';

UPDATE public.genesis_investigation_notes
SET
    body = 'Before publishing, document the strongest alternative explanations: (1) shared exchange/custody infrastructure accounts for all merges without founder coordination; (2) the 781M entry was a sale-distributed ticket rather than a founder allocation; (3) the synchronized delegation reflects automated Daedalus behavior not unique to founders. Grade each alternative against the evidence.',
    updated_at = NOW()
WHERE category = 'NEXT_STEP'
  AND title = 'Add null-hypothesis section to public write-up';

UPDATE public.genesis_investigation_notes
SET
    title = 'Who originally controlled the 781,381,495 ADA entry later merged with EMURGO?',
    body = 'The 781,381,495 ADA entry shares 100% of downstream stake addresses with EMURGO and has an identical current-unspent frontier. Public source review indicates the amount itself was visible pre-launch and consistent with the maximum published sale-ticket size. What remains unresolved is original beneficial ownership at genesis redemption.',
    updated_at = NOW()
WHERE category = 'OPEN_QUESTION'
  AND title = 'Was EMURGO_2 publicly disclosed anywhere?';

COMMIT;

SELECT finding_id, title, grade
FROM public.genesis_investigation_findings
WHERE finding_id IN ('F01', 'F02')
ORDER BY finding_id;

SELECT entity, notes
FROM public.genesis_entity_allocations
WHERE entity = 'EMURGO_2';

SELECT tx_hash, label, notes
FROM public.genesis_key_transactions
WHERE tx_hash = '5ec95a53fa3bb7dc56864bb6e75f369f00aa20e8d8cdc3b66b2fb88ec1b225ef';

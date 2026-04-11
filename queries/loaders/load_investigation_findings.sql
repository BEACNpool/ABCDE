-- ============================================================
-- ABCDE: Genesis Investigation Findings — Database Load Script
-- Run as: psql -U postgres -d cexplorer_replica -f load_investigation_findings.sql
-- Generated: 2026-04-06
-- ============================================================

-- -------------------------------------------------------
-- TABLE 1: genesis_investigation_findings
-- Key findings with evidence grade
-- -------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.genesis_investigation_findings (
    id              SERIAL PRIMARY KEY,
    finding_id      TEXT NOT NULL UNIQUE,
    title           TEXT NOT NULL,
    grade           TEXT NOT NULL CHECK (grade IN ('FACT','STRONG_INFERENCE','HEURISTIC','UNRESOLVED')),
    summary         TEXT NOT NULL,
    evidence        TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

INSERT INTO public.genesis_investigation_findings (finding_id, title, grade, summary, evidence) VALUES

('F01','781,381,495 ADA Genesis Entry Fully Converged With EMURGO Cluster','FACT',
'A 781,381,495 ADA genesis entry redeemed by tx 5ec95a53... later became operationally indistinguishable from the main EMURGO cluster. The first downstream spend is already a direct co-spend with an EMURGO-derived UTxO in tx c8596b9c..., and the line later shows 100% downstream Shelley stake-address overlap (6,216 / 6,216) plus an identical current-unspent frontier (49,089 / 49,089 shared dest_tx_out_id values).',
'Anchor TX: 5ec95a53fa3bb7dc56864bb6e75f369f00aa20e8d8cdc3b66b2fb88ec1b225ef | Redeemed to: DdzFFzCqrhspiThx6UaeJASmHTbwbXp2FtdCkF9AU9QXPF9D8sUC7Fqrv9bmYkxradBbqMrSxukTTsqCPNPwRh5PHazdiwWTuJYVMMaf | direct_merge_tx: c8596b9cd81f734f8129604ff86f23bd4a910465acb84ad9e9d1ac223ccb4a76 | emurgo_input_branch: 743fd051...#0 | earliest_shared_address_with_emurgo: DdzFFzCqrhsu3iF6JfUTaapdWq2mXVRFukkS28WFYVDEqkgaaYttH8cT32credS99L5GaoUsEquqEPNH7ae88eKuDL6XsK5ZL56jkfLi | shared_current_unspent_dest_tx_out_id_count: 49089/49089'),

('F02','Named Founder Redemptions Occurred Within 24 Hours; 781M Entry Followed 5 Minutes After EMURGO','FACT',
'IOG, EMURGO, and CF redeemed their named allocations on Sept 27–28 2017, the first 24 hours of mainnet. A separate 781,381,495 ADA genesis entry (5ec95a53...) redeemed 5 minutes after the main EMURGO redemption.',
'IOG: fa2d2a70... epoch 0 2017-09-27 16:20 UTC | CF: 208c7d54... epoch 0 2017-09-28 09:33 | EMURGO: 242608fc... epoch 0 2017-09-28 10:04 | 781M entry: 5ec95a53... epoch 0 2017-09-28 10:09'),

('F03','Earliest Clean IOG+EMURGO Direct Merge — Epoch 95','FACT',
'Transaction a71578ec... at epoch 95 (2019-01-15 21:50:51 UTC) directly consumed 60 inputs including 2 IOG-exclusive and 1 EMURGO-exclusive source UTxO, routing 71,134 ADA to the VERY_HIGH confidence exchange hub DdzFFzCqrhstmqBka... Live db-sync validated.',
'TX: a71578ec01f6cf39dbcf31351631159e3dd6fb99dd475783effbc65b90b8f0f9 | Epoch: 95 | Inputs: 60 | IOG-exclusive UTxOs: 2042611, 2042772 | EMURGO-exclusive UTxO: 2040117'),

('F04','Clean Three-Way IOG+EMURGO+CF Merge — Epoch 250','FACT',
'Transaction 571f776c... at epoch 250 (2021-02-25 12:58:28 UTC) consumed 384 inputs including 2 IOG-exclusive, 1 EMURGO-exclusive, and 1 CF-exclusive source UTxOs — no pair overlaps. Routed 50,000,000 ADA to addr1qxtrqdumg8... Live db-sync validated.',
'TX: 571f776c0698c576ddecae145f97e7f284b82ebea70fbc924fa4e2a4a6258020 | Epoch: 250 | Inputs: 384 | IOG UTxOs: 8926255, 9036401 | EMURGO UTxO: 8064253 | CF UTxO: 10748217 | Output: 50M ADA to addr1qxtrqdumg8dleqcra3myptlq6n43m8s0mver0pwgqrr8awvkkcdaz26hglgm4qvc6fdy0rr4ck6q5q249drqc4fzyrgq68vuva'),

('F05','521 Direct Cross-Seed Consuming Transactions Identified','FACT',
'Full scan of all six founder trace-edge exports yielded 521 transactions that directly consumed UTxOs from more than one founder lineage. IOG+EMURGO: 216 (205 clean). IOG+CF: 49 (48 clean). EMURGO+CF: 253 (54 clean). Three-way: 3 (1 clean).',
'Source: outputs/cross_entity_evidence/cross_seed_consuming_transactions_2026-04-06.csv | Summary: outputs/cross_entity_evidence/cross_seed_consuming_transactions_summary_2026-04-06.json'),

('F06','Shared Byron 58-Output Splitter Hub','FACT',
'Address Ae2tdPwUPEZ6xYrxCgRDM2NQFM5oajHEoJN3i9ZVV2AbsbvxoJBjVu3yP7W executed 1,170 transactions with exactly 58 outputs (40,876 total spend txs, epochs 202–299). It sourced 2,890 IOG trace rows and 1,688 EMURGO trace rows — confirmed shared automated infrastructure across both founder traces.',
'Hub address: Ae2tdPwUPEZ6xYrxCgRDM2NQFM5oajHEoJN3i9ZVV2AbsbvxoJBjVu3yP7W | 58-output tx count: 1170 | IOG trace rows: 2890 | EMURGO trace rows: 1688 | Active epochs: 202–299'),

('F07','Synchronized Cross-Founder Delegation Event Epochs 245–251','FACT',
'~56,000 sub-50K ADA UTxOs were created from the IOG trace in epochs 245–252 and immediately delegated. 63/64 swarmed pools also received EMURGO delegations (98%), 50/64 received CF delegations (78%), 49/64 received all three (77%). Zero pools were exclusive to IOG.',
'IOG pool swarm threshold: >=20 delegations per pool in epoch window | Cross-genesis validation: datasets/genesis-founders/cross_entity_epoch_245_251_analysis.md | Fee extraction: observations/genesis_fee_extraction_report.md'),

('F08','~25M ADA Operator Fees Extracted From Swarmed Pools','FACT',
'Total operator fees earned by the 64 swarmed pools from epoch 245 through 619: 24,972,527.63 ADA. IOG1 (IOG-operated pool) was the second-largest beneficiary at 1,570,982.24 ADA. Garden Pool (EDEN) led at 2,078,914.64 ADA. 63/64 pools still active.',
'Source: observations/genesis_fee_extraction_report.md | Top pool: EDEN 2.08M ADA | IOG1: 1.57M ADA | Everstake combined (4 pools): ~1.85M ADA'),

('F09','16.54B ADA From Founder Traces Reached Exchange-Classified Addresses','FACT',
'Exchange intersection of combined IOG+EMURGO+CF traced frontiers (54.35B total): EMURGO 41.4% (10.74B), CF 32.0% (4.61B), IOG 8.5% (1.19B). Top 3 unidentified Byron hub addresses absorbed 11.26B ADA combined from all three founder lineages.',
'Source: observations/genesis_exchange_liquidation_report.md | Exchange roster: 1,858 addresses (explicit CEX + ABCDE classifier + Byron heuristic HIGH/VERY_HIGH)'),

('F10','1,996 Exact Shared UTxO Destinations IOG∩EMURGO, 711 EMURGO∩CF, 263 IOG∩CF, 7 All-Three','FACT',
'Pairwise overlap of exact dest_tx_out_id values in current_unspent.csv frontier exports. Seven triply-shared outputs currently visible in all three frontiers, including outputs from epoch-196 tx 197f9d27..., epoch-239 tx 34147ef4..., and epoch-250 tx 571f776c...',
'Source: outputs/cross_entity_evidence/cross_entity_summary_amended_2026-04-06.md | Three-way shared tx_out_ids: 10748946, 10748947, 10748948, 7835688, 7835689, 5064341, 5064342'),

('F11','Hub 1 (Ae2tdPwUPEYwFx4d...) Still Active June 2025 With 116M ADA','FACT',
'Byron hub address Ae2tdPwUPEYwFx4dmJheyNPPYXtvHbJLeCaA96o6Y2iiUL18cAt7AizN2zG absorbed 6.64B ADA from CF and EMURGO traces. Hub 2 (Ae2tdPwUPEZ5ZFno...) feeds into it (~241B ADA total feeder relationship). Hub 1 remains active at epoch 566 with ~116M ADA. Primary outbound destination classified EXCHANGE.',
'Hub 1: Ae2tdPwUPEYwFx4dmJheyNPPYXtvHbJLeCaA96o6Y2iiUL18cAt7AizN2zG | Hub 2 feeder: Ae2tdPwUPEZ5ZFnojZ5yuoAAp2U3f3Ntkghw2GUXgmA4kAh73Tv4bFkjmXy | Primary destination: addr1vy4nmtfc4jfftgqg369hs2ku6kvcncgzhkemq6mh0u3zgpslf59wr (~51.9B ADA, EXCHANGE)'),

('F12','Mystery Address 558B ADA Throughput — Unidentified Large Exchange','STRONG_INFERENCE',
'addr1q9ukkxqf7cwdfgzshltrrmqj0skmv0s8f7s22cvysucug8jgfzwl8zg88xl6z4e6q0sdgeqrhgqq8aa3zj2nuqqvntcs6utve7 received/sent 558.16B ADA. First receive and send 4 minutes apart (hot wallet sweep). Stake key registered but never delegated. 7/10 top destinations classified EXCHANGE. Bidirectional with Hub 3 (Byron predecessor). Active epochs 209–388, fully drained. Best hypothesis: large Asian CEX (Huobi/OKX class).',
'Stake: stake1u9yy380n3yrnn0ap2uaq8cx5vspm5qqr77c3f9f7qqxf4ugev3aru | First recv: 2020-08-07 epoch 209 (Shelley HF) | Last active: 2022-11-10 epoch 374 | Byron predecessor: Ae2tdPwUPEZ5faoeL9oL2wHadcQo3mJLi68M4eep8wo45BFnk46sMkvCmM9 (Hub 3)'),

('F13','Genesis Supply Concentration — Top 1% Held 36.4%','FACT',
'Genesis distribution across 14,505 addresses: top 1% (145 addresses) held 36.4% of supply; top 10% held 64.1%; top 10 addresses held 22.1%. 465 addresses (318.2M ADA, 1.02%) were never redeemed and are permanently locked. Total genesis supply: 31,112,484,745 ADA.',
'Query: SELECT percentile analysis on tx_out WHERE block_id=1 | Unredeemed: 465 addresses, 318,200,635 ADA')

ON CONFLICT (finding_id) DO UPDATE SET
    title = EXCLUDED.title,
    grade = EXCLUDED.grade,
    summary = EXCLUDED.summary,
    evidence = EXCLUDED.evidence;


-- -------------------------------------------------------
-- TABLE 2: genesis_entity_allocations
-- Verified tracked genesis anchors
-- -------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.genesis_entity_allocations (
    id                  SERIAL PRIMARY KEY,
    entity              TEXT NOT NULL,
    anchor_tx_hash      TEXT NOT NULL UNIQUE,
    genesis_ada         NUMERIC NOT NULL,
    redeemed_epoch      INTEGER,
    redeemed_at         TIMESTAMPTZ,
    redeemed_to_address TEXT,
    pct_of_genesis      NUMERIC GENERATED ALWAYS AS (genesis_ada / 31112484745.0 * 100) STORED,
    notes               TEXT
);

INSERT INTO public.genesis_entity_allocations
    (entity, anchor_tx_hash, genesis_ada, redeemed_epoch, redeemed_at, redeemed_to_address, notes)
VALUES
    ('IOG',      'fa2d2a70c0b5fd45cb6c3989f02813061f9d27f15f30ecddd38780c59f413c62', 2463071701, 0, '2017-09-27 16:20:51+00', 'DdzFFzCqrhsytyf2oUxqFNXDX9MfAFBWk9pTBXViZbSwxEi7PYcq9LSjBDcW6BVcA7KxgeixYWospQKn68P9PaviM2FvhTFvsEezT8qg', 'Publicly disclosed. Redeemed day 1.'),
    ('EMURGO',   '242608fc18552a4ac83adabcef7155f3b909e83d469ce89735db8f11d3637e38', 2074165643, 0, '2017-09-28 10:04:11+00', 'DdzFFzCqrhsi4ogKmCFQwBUWqtS18UBL3SrdDoNuSxHSiqKAgbn2zCfDsdv2hbTDN8mgwT3C84uQ3EKazbUtPMPFKDzNxrLKBeWqKqvy', 'Publicly disclosed stated amount.'),
    ('EMURGO_2', '5ec95a53fa3bb7dc56864bb6e75f369f00aa20e8d8cdc3b66b2fb88ec1b225ef', 781381495,  0, '2017-09-28 10:09:11+00', 'DdzFFzCqrhspiThx6UaeJASmHTbwbXp2FtdCkF9AU9QXPF9D8sUC7Fqrv9bmYkxradBbqMrSxukTTsqCPNPwRh5PHazdiwWTuJYVMMaf', 'Tracked separately for clustering. Exact amount was public in sale/genesis data pre-launch and matches the published maximum single ticket amount. First downstream spend is a direct co-spend with an EMURGO-derived UTxO in tx c8596b9c..., and the later trace fully converges with EMURGO (6216/6216 stake addrs, 49089/49089 current frontier outputs).'),
    ('CF',       '208c7d54c1c24059c9314ddbe866edc80adcb8894539b27b6a1430d5c078b998', 648176763,  0, '2017-09-28 09:33:11+00', 'DdzFFzCqrht1RAzCsYyTHZJymt4qj65bV41TyufbmpTr9nGh2VS3zY25tJHu718QACd7xpKENCGfK8wnQhZXNJmnmCvxPHJfuwk3BzrP', 'Publicly disclosed.')
ON CONFLICT (anchor_tx_hash) DO UPDATE SET
    entity = EXCLUDED.entity,
    genesis_ada = EXCLUDED.genesis_ada,
    redeemed_epoch = EXCLUDED.redeemed_epoch,
    redeemed_at = EXCLUDED.redeemed_at,
    redeemed_to_address = EXCLUDED.redeemed_to_address,
    notes = EXCLUDED.notes;


-- -------------------------------------------------------
-- TABLE 3: genesis_key_transactions
-- Flagged transactions for investigation
-- -------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.genesis_key_transactions (
    id              SERIAL PRIMARY KEY,
    tx_hash         TEXT NOT NULL UNIQUE,
    epoch_no        INTEGER,
    block_time      TIMESTAMPTZ,
    label           TEXT NOT NULL,
    significance    TEXT NOT NULL,
    entities        TEXT[],
    input_count     INTEGER,
    output_count    INTEGER,
    notes           TEXT
);

INSERT INTO public.genesis_key_transactions
    (tx_hash, epoch_no, block_time, label, significance, entities, input_count, output_count, notes)
VALUES
    ('fa2d2a70c0b5fd45cb6c3989f02813061f9d27f15f30ecddd38780c59f413c62', 0, '2017-09-27 16:20:51+00',
     'IOG Genesis Redemption', 'CRITICAL', ARRAY['IOG'], 1, 1, '2,463,071,701 ADA — first founder to redeem, same day as genesis'),

    ('242608fc18552a4ac83adabcef7155f3b909e83d469ce89735db8f11d3637e38', 0, '2017-09-28 10:04:11+00',
     'EMURGO Genesis Redemption', 'CRITICAL', ARRAY['EMURGO'], 1, 1, '2,074,165,643 ADA — redeemed 18 hours after genesis'),

    ('5ec95a53fa3bb7dc56864bb6e75f369f00aa20e8d8cdc3b66b2fb88ec1b225ef', 0, '2017-09-28 10:09:11+00',
     '781M Genesis Entry Redemption', 'CRITICAL', ARRAY['EMURGO','EMURGO_2'], 1, 1, '781,381,495 ADA entry redeemed 5 min after EMURGO. Public amount was visible pre-launch; current best classification is a sale-ticket-sized genesis entry whose first downstream spend directly co-spends with an EMURGO-derived branch before later becoming fully merged with the EMURGO pipeline'),

    ('208c7d54c1c24059c9314ddbe866edc80adcb8894539b27b6a1430d5c078b998', 0, '2017-09-28 09:33:11+00',
     'CF Genesis Redemption', 'CRITICAL', ARRAY['CF'], 1, 1, '648,176,763 ADA — Cardano Foundation allocation'),

    ('a71578ec01f6cf39dbcf31351631159e3dd6fb99dd475783effbc65b90b8f0f9', 95, '2019-01-15 21:50:51+00',
     'First Clean IOG+EMURGO Merge', 'HIGH', ARRAY['IOG','EMURGO'], 60, 2, '71,134 ADA routed to VERY_HIGH confidence exchange hub DdzFFzCqrhstmqBka...'),

    ('f9951db326893e5c6cd94407e3d75be4928442aaf5809e435ca3e82c1983949d', 193, '2020-05-18 02:50:31+00',
     'First Clean IOG+CF Merge', 'HIGH', ARRAY['IOG','CF'], 2, 2, 'Output routes to same DdzFFzCqrhstmqBka... exchange hub'),

    ('11c0765f430ecfffbdd1fb400d34bcd61d13af4c2e9332ce215f33de7e48d394', 195, '2020-05-27 20:09:51+00',
     'First Clean EMURGO+CF Merge', 'HIGH', ARRAY['EMURGO','CF'], 4, 2, '1 EMURGO-exclusive + 3 CF-exclusive inputs'),

    ('197f9d27e49345cc085c9a2951d96c77f57f1cd82a71c095b7b7a3b36e74855d', 196, '2020-06-02 09:58:31+00',
     'Earliest Three-Way Lineage Merge', 'HIGH', ARRAY['IOG','EMURGO','CF'], 15, 2, 'Not fully clean — EMURGO and CF lineages pre-mixed in one input. Outputs: 5064341 (157.8 ADA), 5064342 (10,000 ADA)'),

    ('34147ef46fd105ed39e3be63ac194e79622fb1bf9ea6e50313a0c3e0e6fd20c3', 239, '2021-01-01 10:17:58+00',
     'Intermediate Three-Way Merge', 'HIGH', ARRAY['IOG','EMURGO','CF'], 58, 2, 'Outputs: 7835688 (50,000 ADA), 7835689 (8,356.37 ADA)'),

    ('571f776c0698c576ddecae145f97e7f284b82ebea70fbc924fa4e2a4a6258020', 250, '2021-02-25 12:58:28+00',
     'CLEAN Three-Way IOG+EMURGO+CF Merge', 'CRITICAL', ARRAY['IOG','EMURGO','CF'], 384, 3, '⚠ Strongest merge evidence. 2 IOG-exclusive + 1 EMURGO-exclusive + 1 CF-exclusive inputs. 50,000,000 ADA output to addr1qxtrqdumg8...')

ON CONFLICT (tx_hash) DO UPDATE SET
    epoch_no = EXCLUDED.epoch_no,
    block_time = EXCLUDED.block_time,
    label = EXCLUDED.label,
    significance = EXCLUDED.significance,
    entities = EXCLUDED.entities,
    input_count = EXCLUDED.input_count,
    output_count = EXCLUDED.output_count,
    notes = EXCLUDED.notes;


-- -------------------------------------------------------
-- TABLE 4: genesis_investigation_notes
-- Open questions and next steps
-- -------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.genesis_investigation_notes (
    id          SERIAL PRIMARY KEY,
    category    TEXT NOT NULL CHECK (category IN ('NEXT_STEP','OPEN_QUESTION','HYPOTHESIS','COMPLETED')),
    priority    INTEGER DEFAULT 5 CHECK (priority BETWEEN 1 AND 10),
    title       TEXT NOT NULL,
    body        TEXT,
    assigned_to TEXT,
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    updated_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS genesis_investigation_notes_category_title_key
    ON public.genesis_investigation_notes (category, title);

INSERT INTO public.genesis_investigation_notes (category, priority, title, body) VALUES

('NEXT_STEP', 10, 'Identify the original holder of the 781,381,495 ADA entry',
'Public-source review now indicates the 781,381,495 ADA amount was visible pre-launch in official sale stats and genesis files, and that it matches the published maximum single ticket amount. Its first downstream spend directly co-spends with an EMURGO-derived branch, but original beneficial ownership at redemption is still unresolved. The live question is whether the original holder was EMURGO, an affiliate, or an unrelated buyer whose funds entered the same custody stack almost immediately. Anchor TX: 5ec95a53...'),

('NEXT_STEP', 9, 'Identify the Byron hub operator (Hub 1 — still active 2025)',
'Hub 1 address Ae2tdPwUPEYwFx4dmJheyNPPYXtvHbJLeCaA96o6Y2iiUL18cAt7AizN2zG has ~116M ADA remaining as of epoch 566 (June 2025). Its primary outbound destination addr1vy4nmtfc4jfftgqg369hs2ku6kvcncgzhkemq6mh0u3zgpslf59wr received ~51.9B ADA and is classified EXCHANGE. Submit to Chainalysis/Elliptic for named-exchange attribution.'),

('NEXT_STEP', 9, 'Build full backtrace of every clean pairwise merge',
'For each of the 205 clean IOG+EMURGO, 48 clean IOG+CF, and 54 clean EMURGO+CF merges: trace every direct input back one hop to determine the last address each lineage held before merging. Classify each merge point as founder-controlled, exchange, custody, OTC, or unknown. This narrows the "who was in control" question at each merge event.'),

('NEXT_STEP', 8, 'Submit Binance-confirmed address to community for named-exchange chain',
'DdzFFzCqrhskEmdNPvFCgyLFqufz8nkJ3yY1DZPykgMcEmCzxjAjUNtggfZP42MJoD3BMqV9vui21HdpbqZJuFSFEyZ9tApuKbP9uv8K is confirmed Binance. It received 215M ADA from EMURGO and IOG lineages. Use this anchor to identify other Binance-connected addresses in the hub network.'),

('NEXT_STEP', 8, 'Re-run 12-address chain-wide pool overlap with explicit genesis filter',
'The current SQL for stake credentials delegating to named IOG + EMURGO + CF pools is chain-wide. Restrict it to stake credentials present in the seed-trace delegation exports. Publish chain-wide and genesis-constrained counts side by side.'),

('NEXT_STEP', 7, 'Identify the mystery 558B ADA address entity',
'addr1q9ukkxqf7cwdfgzshltrrmqj0skmv0s8f7s22cvysucug8jgfzwl8zg88xl6z4e6q0sdgeqrhgqq8aa3zj2nuqqvntcs6utve7 processed 558.16B ADA (epochs 209–388). Best hypothesis: Huobi or OKX. Check against known Huobi ADA deposit addresses. Bidirectional with Hub 3 (Byron predecessor Ae2tdPwUPEZ5faoe...) confirms same operator.'),

('NEXT_STEP', 7, 'Produce visual merge timeline for public publication',
'Create a timeline diagram showing: genesis (Sept 2017) → 781M entry redemption (5 min after EMURGO) → hop-1 shared EMURGO address (2017-10-18) → first IOG+EMURGO merge (Jan 2019) → first CF merges (May 2020) → synchronized delegation swarm (Jan–Mar 2021) → clean 3-way merge (Feb 2021) → ongoing hub activity (2025). This is the most accessible summary of the findings.'),

('NEXT_STEP', 6, 'Add null-hypothesis section to public write-up',
'Before publishing, document the strongest alternative explanations: (1) shared exchange/custody infrastructure accounts for all merges without founder coordination; (2) the 781M entry was a sale-distributed ticket rather than a founder allocation; (3) the synchronized delegation reflects automated Daedalus behavior not unique to founders. Grade each alternative against the evidence.'),

('NEXT_STEP', 6, 'Extend trace to EMURGO_2 hub classification',
'The emurgo2/deoverlap_analysis.csv file tracks the overlap separation. Run a full hub-classification pass on the EMURGO_2 trace specifically to determine if it routes through the same automated splitter infrastructure as EMURGO.'),

('NEXT_STEP', 5, 'Document the 100 × 1 ADA dust genesis allocations',
'100 genesis addresses received exactly 1 ADA each. Determine if these are marker/activation addresses for a known entity, and whether they were subsequently used for any purpose or remain unspent.'),

('OPEN_QUESTION', 10, 'Who originally controlled the 781,381,495 ADA entry later merged with EMURGO?',
'The 781,381,495 ADA entry shares 100% of downstream stake addresses with EMURGO and has an identical current-unspent frontier. Public source review indicates the amount itself was visible pre-launch and consistent with the maximum published sale-ticket size. What remains unresolved is original beneficial ownership at genesis redemption.'),

('OPEN_QUESTION', 9, 'Who controls Hub 1 (Ae2tdPwUPEYwFx4d...) in 2025?',
'Hub 1 remains active with 116M ADA as of epoch 566. Its operator has been active since epoch 130 (July 2019). This is a living entity with significant ADA. Is it Binance, another CEX, or could it be a founder-controlled treasury address?'),

('OPEN_QUESTION', 8, 'Did the epoch 245–251 delegation swarm represent coordinated founder action or automated wallet software?',
'The synchronized delegation of sub-50K UTxOs from all three founder traces to the same 49 pools could reflect: (a) coordinated insider action, (b) shared custody provider managing all three allocations, or (c) exchange-side automation handling customer ADA. The 98% EMURGO pool overlap is the hardest fact to explain by coincidence.'),

('HYPOTHESIS', 8, 'Hub 1 and Hub 2 are operated by Binance',
'Binance is the only named exchange confirmed in this dataset (via DdzFFzCqrhskEmd...). Hub 2 feeds Hub 1 (~241B ADA). Hub 1''s primary outbound is classified EXCHANGE. The feeder relationship and operational pattern are consistent with Binance cold/warm wallet architecture. Confidence: MEDIUM — requires independent on-chain confirmation.'),

('HYPOTHESIS', 7, 'The 58-output splitter is operated by the same entity that controls both IOG and EMURGO post-redemption funds',
'The mechanical 58-output pattern across 1,170 transactions sourcing from both IOG and EMURGO traces implies a single automated system managed both. This could be a shared custody provider, an exchange, or an internal IOHK/Emurgo treasury system. The epoch 202–299 operational window (Byron era, pre-Shelley) limits the operators to entities with Byron-era wallet infrastructure.')

ON CONFLICT (category, title) DO UPDATE SET
    priority = EXCLUDED.priority,
    body = EXCLUDED.body,
    updated_at = NOW();

-- -------------------------------------------------------
-- Grant read access to codex_audit
-- -------------------------------------------------------
GRANT SELECT ON public.genesis_investigation_findings   TO codex_audit;
GRANT SELECT ON public.genesis_entity_allocations       TO codex_audit;
GRANT SELECT ON public.genesis_key_transactions         TO codex_audit;
GRANT SELECT ON public.genesis_investigation_notes      TO codex_audit;

-- -------------------------------------------------------
-- Verify load
-- -------------------------------------------------------
SELECT 'genesis_investigation_findings' as table_name, COUNT(*) as rows FROM genesis_investigation_findings
UNION ALL
SELECT 'genesis_entity_allocations',  COUNT(*) FROM genesis_entity_allocations
UNION ALL
SELECT 'genesis_key_transactions',    COUNT(*) FROM genesis_key_transactions
UNION ALL
SELECT 'genesis_investigation_notes', COUNT(*) FROM genesis_investigation_notes;

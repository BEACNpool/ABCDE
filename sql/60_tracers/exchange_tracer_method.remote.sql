\timing on
\set ON_ERROR_STOP on

-- The Red (or Blue) Pill Study — canonical exchange-tracer reconstruction.
--
-- Standalone reproduction of the method tables shipped in the compact cut
-- (tracer_asset_path / tracer_valid_deposits / tracer_name_votes /
-- tracer_terminus_clusters / tracer_terminus_census). Runs read-only apart from
-- session-local TEMP tables, against any cardano-db-sync database.
--
-- Rules and limits: docs/26_EXCHANGE_TRACER_METHOD.md
-- Maintainer CSV export: tracers/scripts/export_tracers_from_abcde.sh (11-16)
--
-- Liveness uses a tx_in anti-join on purpose: tx_out.consumed_by_tx_id is not
-- populated on a logical-replication subscriber such as ABCDE.

SET statement_timeout = '600s';

\set policy_id 'd8d5539ee11f21a6748735aeb69d3ed935bb14570f57709279031119'
\set script_expiry_slot 223391762
\set participant_threshold 2

\echo '0. Snapshot receipt: tip, and whether the mint window is closed'
SELECT MAX(block_no) AS tip_block,
       MAX(time) AS tip_time_utc,
       MAX(slot_no) AS tip_slot,
       :script_expiry_slot AS native_script_expiry_slot,
       MAX(slot_no) > :script_expiry_slot AS mint_window_closed
FROM block;

\echo '1. Exact holder path of every tracer (one row per asset-bearing output)'
CREATE TEMP TABLE pos AS
SELECT p.*,
       row_number() OVER w AS hop,
       lag(cluster_key) OVER w AS prev_cluster_key
FROM (
  SELECT ma.id                                   AS ma_id,
         encode(ma.name, 'escape')               AS asset_name,
         encode(ma.name, 'hex')                  AS asset_name_hex,
         ma.fingerprint,
         txo.index                               AS tx_out_index,
         txo.address,
         COALESCE(sa.view, '')                   AS stake_address,
         -- node key: stake credential when present, else payment address
         CASE WHEN COALESCE(sa.view, '') <> '' THEN 's:' || sa.view
              ELSE 'a:' || txo.address END       AS cluster_key,
         tx.id                                   AS tx_id,
         encode(tx.hash, 'hex')                  AS tx_hash,
         tx.block_index,
         b.block_no,
         b.time                                  AS block_time,
         NOT EXISTS (
           SELECT 1 FROM tx_in i
           WHERE i.tx_out_id = tx.id AND i.tx_out_index = txo.index
         )                                       AS is_unspent
  FROM multi_asset ma
  JOIN ma_tx_out mto ON mto.ident = ma.id
  JOIN tx_out txo    ON txo.id = mto.tx_out_id
  JOIN tx             ON tx.id = txo.tx_id
  JOIN block b        ON b.id = tx.block_id
  LEFT JOIN stake_address sa ON sa.id = txo.stake_address_id
  WHERE ma.policy = decode(:'policy_id', 'hex')
    AND mto.quantity = 1              -- non-fungible only
) p
WINDOW w AS (PARTITION BY asset_name ORDER BY block_no, block_index, tx_out_index);
ANALYZE pos;

SELECT count(DISTINCT asset_name) AS tracers,
       count(*)                   AS asset_bearing_outputs,
       count(*) FILTER (WHERE is_unspent) AS live_utxos,
       count(DISTINCT cluster_key) AS distinct_cluster_keys,
       max(hop)                   AS longest_path
FROM pos;

\echo '2. Valid tagged deposits — all four rules must hold'
CREATE TEMP TABLE dep AS
SELECT p.asset_name,
       p.tx_hash                                  AS deposit_tx,
       p.block_no                                 AS deposit_block_no,
       p.block_time                               AS deposit_time,
       p.hop                                      AS deposit_hop,
       p.cluster_key                              AS deposit_cluster_key,
       p.address                                  AS deposit_address,
       p.prev_cluster_key                         AS participant_key,
       btrim(COALESCE(tm.json->'msg'->>1, ''))    AS claimed_exchange,
       lower(btrim(COALESCE(tm.json->'msg'->>1, ''))) AS claimed_exchange_norm,
       tm.json::text                              AS deposit_msg_json
FROM pos p
JOIN tx_metadata tm ON tm.tx_id = p.tx_id AND tm.key = 674   -- rule 1
WHERE tm.json::text ILIKE '%Red (or Blue) Pill%'             -- rule 2
  AND p.tx_out_index = 0                                     -- rule 3
  AND p.prev_cluster_key IS NOT NULL                         -- rule 4 ...
  AND p.prev_cluster_key <> p.cluster_key;                   -- ... new cluster

CREATE TEMP TABLE term AS
SELECT asset_name, cluster_key AS terminus_key, address AS terminus_address,
       stake_address AS terminus_stake_address, tx_hash AS terminus_tx,
       block_time AS terminus_time, hop AS terminus_hop
FROM pos WHERE is_unspent;

SELECT count(*) AS valid_deposits,
       count(DISTINCT participant_key) AS participant_wallets,
       count(DISTINCT deposit_tx) AS deposit_txs,
       count(DISTINCT claimed_exchange_norm) FILTER (WHERE claimed_exchange_norm <> '')
         AS distinct_names_claimed
FROM dep;

\echo '3. Name votes per terminus cluster (participants = the vote unit)'
CREATE TEMP TABLE votes AS
SELECT t.terminus_key,
       d.claimed_exchange_norm,
       min(d.claimed_exchange)          AS claimed_exchange,
       count(DISTINCT d.asset_name)     AS tracers,
       count(DISTINCT d.participant_key) AS participants
FROM dep d
JOIN term t ON t.asset_name = d.asset_name
GROUP BY t.terminus_key, d.claimed_exchange_norm;

SELECT * FROM votes ORDER BY participants DESC, tracers DESC;

\echo '4. Resolution — unique participant lead clearing the threshold, or unresolved'
WITH ranked AS (
  SELECT v.*,
         max(participants) FILTER (WHERE claimed_exchange_norm <> '')
           OVER (PARTITION BY terminus_key) AS top_participants,
         count(*) FILTER (WHERE claimed_exchange_norm <> '')
           OVER (PARTITION BY terminus_key) AS named_claims
  FROM votes v
), resolution AS (
  SELECT terminus_key,
         max(top_participants) AS top_participants,
         max(named_claims)     AS named_claims,
         count(*) FILTER (WHERE claimed_exchange_norm <> ''
                            AND participants = top_participants) AS leaders,
         min(claimed_exchange) FILTER (WHERE claimed_exchange_norm <> ''
                            AND participants = top_participants) AS leader_name
  FROM ranked GROUP BY terminus_key
)
SELECT t.terminus_key,
       count(DISTINCT d.asset_name)      AS tracers,
       count(DISTINCT d.participant_key) AS participants,
       max(r.named_claims) > 1           AS conflicted,
       CASE WHEN max(r.named_claims) = 0 THEN 'unresolved_no_named_claim'
            WHEN max(r.top_participants) < :participant_threshold THEN 'unresolved_below_threshold'
            WHEN max(r.leaders) > 1 THEN 'unresolved_tie'
            ELSE 'resolved' END          AS resolution_status,
       CASE WHEN max(r.named_claims) > 0
             AND max(r.top_participants) >= :participant_threshold
             AND max(r.leaders) = 1 THEN max(r.leader_name) END AS resolved_exchange
FROM dep d
JOIN term t ON t.asset_name = d.asset_name
JOIN resolution r ON r.terminus_key = t.terminus_key
GROUP BY t.terminus_key
ORDER BY tracers DESC, participants DESC;

\echo '5. Denominator — where ALL tracers sit now, tagged or not'
SELECT t.terminus_key,
       count(*)                AS tracers_now,
       count(d.asset_name)     AS tracers_from_validated_deposit,
       min(t.terminus_time)    AS first_arrival,
       max(t.terminus_time)    AS last_arrival
FROM term t
LEFT JOIN dep d ON d.asset_name = t.asset_name
GROUP BY t.terminus_key
ORDER BY tracers_now DESC
LIMIT 25;

-- Reminder for whoever reads the output: an exact NFT edge is FACT; a cluster
-- key is an on-chain heuristic; an exchange name is the depositor's claim; and
-- ADA value paths are a separate, indicative-only measurement.

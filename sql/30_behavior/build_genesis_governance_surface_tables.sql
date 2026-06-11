-- Build staged tables for Genesis trace -> current governance analysis.
--
-- psql variables:
--   stage_schema: staged trace schema containing trace_utxos
\set ON_ERROR_STOP on

DROP TABLE IF EXISTS :"stage_schema".current_governance_surface;
DROP TABLE IF EXISTS :"stage_schema".current_latest_vote;
DROP TABLE IF EXISTS :"stage_schema".current_live_utxos;

CREATE UNLOGGED TABLE :"stage_schema".current_live_utxos AS
SELECT
  u.root_seed_id,
  u.tx_id,
  u.tx_hash,
  u.tx_out_index,
  u.min_depth,
  u.value_lovelace,
  u.address,
  u.stake_address_id,
  u.stake_address,
  u.epoch_no,
  u.block_no,
  u.block_time_utc
FROM :"stage_schema".trace_utxos u
LEFT JOIN public.tx_in spent
  ON spent.tx_out_id = u.tx_id
 AND spent.tx_out_index = u.tx_out_index
WHERE spent.tx_in_id IS NULL;

CREATE INDEX current_live_utxos_stake_idx ON :"stage_schema".current_live_utxos(stake_address_id);
CREATE INDEX current_live_utxos_utxo_idx ON :"stage_schema".current_live_utxos(tx_id, tx_out_index);
ANALYZE :"stage_schema".current_live_utxos;

CREATE UNLOGGED TABLE :"stage_schema".current_latest_vote AS
WITH wanted_stake AS (
  SELECT DISTINCT stake_address_id
  FROM :"stage_schema".current_live_utxos
  WHERE stake_address_id IS NOT NULL
)
SELECT DISTINCT ON (dv.addr_id)
  dv.addr_id,
  dv.drep_hash_id,
  dh.view AS drep_id_bech32,
  b.epoch_no AS latest_vote_epoch,
  b.time AS latest_vote_time_utc,
  encode(tx.hash, 'hex') AS latest_vote_tx_hash
FROM public.delegation_vote dv
JOIN wanted_stake ws ON ws.stake_address_id = dv.addr_id
JOIN public.tx tx ON tx.id = dv.tx_id
JOIN public.block b ON b.id = tx.block_id
JOIN public.drep_hash dh ON dh.id = dv.drep_hash_id
ORDER BY dv.addr_id, b.time DESC, tx.id DESC, dv.cert_index DESC;

CREATE INDEX current_latest_vote_addr_idx ON :"stage_schema".current_latest_vote(addr_id);
CREATE INDEX current_latest_vote_drep_idx ON :"stage_schema".current_latest_vote(drep_hash_id);
ANALYZE :"stage_schema".current_latest_vote;

CREATE UNLOGGED TABLE :"stage_schema".current_governance_surface AS
WITH latest_dd AS (
  SELECT max(epoch_no) AS epoch_no FROM public.drep_distr
), tip AS (
  SELECT max(time) AS dbsync_tip_utc, max(epoch_no) AS dbsync_tip_epoch FROM public.block
)
SELECT
  now() AT TIME ZONE 'UTC' AS snapshot_utc,
  :'stage_schema' AS trace_schema,
  tip.dbsync_tip_utc,
  tip.dbsync_tip_epoch,
  ct.root_seed_id,
  ct.tx_id,
  ct.tx_hash,
  ct.tx_out_index,
  ct.min_depth,
  ct.value_lovelace,
  round(ct.value_lovelace / 1000000.0, 6) AS value_ada,
  ct.address,
  ct.stake_address_id,
  ct.stake_address,
  ct.epoch_no AS output_epoch_no,
  ct.block_no AS output_block_no,
  ct.block_time_utc AS output_block_time_utc,
  lv.drep_id_bech32 AS latest_drep_id_bech32,
  lv.drep_hash_id AS latest_drep_hash_id,
  lv.latest_vote_epoch,
  lv.latest_vote_time_utc,
  lv.latest_vote_tx_hash,
  dd.epoch_no AS drep_distribution_epoch,
  dd.amount AS drep_voting_power_lovelace,
  round(dd.amount / 1000000.0, 6) AS drep_voting_power_ada,
  CASE
    WHEN ct.stake_address_id IS NULL THEN 'no_stake_or_byron'
    ELSE 'unknown'
  END AS behavior_class,
  CASE
    WHEN ct.stake_address_id IS NULL THEN 'high'
    ELSE 'unclassified'
  END AS behavior_confidence,
  CASE
    WHEN ct.stake_address_id IS NULL THEN 'current traced UTxO has no stake credential and cannot be mapped to DRep delegation'
    ELSE 'default pending public classification receipts'
  END AS classification_reason,
  CASE
    WHEN ct.stake_address_id IS NULL THEN 'db-sync tx_out.stake_address_id is null'
    ELSE 'unclassified scaffold'
  END AS classification_source
FROM :"stage_schema".current_live_utxos ct
CROSS JOIN tip
LEFT JOIN :"stage_schema".current_latest_vote lv ON lv.addr_id = ct.stake_address_id
LEFT JOIN latest_dd ldd ON true
LEFT JOIN public.drep_distr dd
  ON dd.hash_id = lv.drep_hash_id
 AND dd.epoch_no = ldd.epoch_no;

CREATE INDEX current_governance_surface_drep_idx ON :"stage_schema".current_governance_surface(latest_drep_hash_id);
CREATE INDEX current_governance_surface_utxo_idx ON :"stage_schema".current_governance_surface(tx_id, tx_out_index);
ANALYZE :"stage_schema".current_governance_surface;

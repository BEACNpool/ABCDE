-- Skeleton for durable trace edge storage.
-- Extraction implementation will batch BFS from seed outputs using the db-sync tx_in rule documented in docs/01_METHOD.md.

CREATE TABLE IF NOT EXISTS genesis.trace_edges (
  run_id text NOT NULL,
  root_seed_id text NOT NULL REFERENCES genesis.seed_registry(seed_id),
  depth integer NOT NULL,
  source_tx_id bigint NOT NULL,
  source_tx_index integer NOT NULL,
  spend_tx_id bigint,
  dest_tx_id bigint NOT NULL,
  dest_tx_index integer NOT NULL,
  dest_tx_out_id bigint NOT NULL,
  dest_address text NOT NULL,
  dest_stake_address text,
  value_lovelace bigint NOT NULL,
  block_no integer,
  epoch_no integer,
  block_time_utc timestamp,
  provenance_state text NOT NULL DEFAULT 'UNCLASSIFIED',
  PRIMARY KEY (run_id, root_seed_id, dest_tx_id, dest_tx_index, depth)
);

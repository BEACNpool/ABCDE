-- Planned enrichment: identify transactions consuming pure descendants from multiple seeds.
-- Output target: genesis.cross_entity_merges.

CREATE TABLE IF NOT EXISTS genesis.cross_entity_merges (
  run_id text NOT NULL,
  spend_tx_id bigint NOT NULL,
  spend_tx_hash text NOT NULL,
  epoch_no integer,
  block_time_utc timestamp,
  seed_combo text NOT NULL,
  input_count integer,
  output_count integer,
  total_input_lovelace numeric,
  evidence_grade text NOT NULL DEFAULT 'FACT',
  PRIMARY KEY (run_id, spend_tx_id, seed_combo)
);

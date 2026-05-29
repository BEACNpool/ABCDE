-- Load anchors.yaml into a relational seed registry before running this query.
-- Target server-side schema: genesis.seed_registry.

CREATE SCHEMA IF NOT EXISTS genesis;
CREATE SCHEMA IF NOT EXISTS evidence;

CREATE TABLE IF NOT EXISTS genesis.seed_registry (
  seed_id text PRIMARY KEY,
  label text NOT NULL,
  tx_hash_hex text NOT NULL UNIQUE,
  amount_lovelace bigint,
  source_type text NOT NULL,
  evidence_grade text NOT NULL,
  notes text
);

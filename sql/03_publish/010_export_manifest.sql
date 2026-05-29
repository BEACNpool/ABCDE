-- Planned publish step: record source tip, SQL hashes, row counts, and artifact hashes.

CREATE TABLE IF NOT EXISTS evidence.query_runs (
  run_id text PRIMARY KEY,
  git_commit text,
  source_tip_block integer,
  source_tip_time timestamp,
  started_at timestamp DEFAULT now(),
  completed_at timestamp,
  status text NOT NULL,
  notes text
);

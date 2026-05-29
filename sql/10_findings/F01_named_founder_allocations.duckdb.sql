-- Runs against the published ABCDE Genesis DuckDB cut.
SELECT seed_id, label, tx_hash, amount_ada, source_type, evidence_grade
FROM seed_registry
ORDER BY amount_ada DESC;

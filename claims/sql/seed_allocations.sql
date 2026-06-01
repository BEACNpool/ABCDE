SELECT
  seed_id,
  label,
  amount_ada,
  source_type,
  evidence_grade
FROM seeds
ORDER BY amount_ada DESC, seed_id;

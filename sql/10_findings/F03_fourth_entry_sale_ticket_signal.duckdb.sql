-- Runs against data/abcde_genesis_seed_registry.duckdb.
WITH fourth AS (
  SELECT amount_ada
  FROM seed_registry
  WHERE seed_id = 'fourth_entry_781m'
)
SELECT
  s.slice,
  s.metric,
  s.amount_ada,
  s.amount_ada = fourth.amount_ada AS matches_fourth_entry_amount
FROM fourth_entry_sale_ticket_signal s
CROSS JOIN fourth
ORDER BY s.slice;

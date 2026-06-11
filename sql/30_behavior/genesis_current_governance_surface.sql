-- Export shared Genesis trace -> current governance surface.
--
-- psql variables:
--   stage_schema: staged trace schema where build_genesis_governance_surface_tables.sql ran
SELECT *
FROM :"stage_schema".current_governance_surface
ORDER BY root_seed_id, min_depth, tx_id, tx_out_index;

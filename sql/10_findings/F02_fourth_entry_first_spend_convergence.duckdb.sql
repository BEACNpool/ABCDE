-- Runs against data/abcde_genesis.duckdb.
-- Shows the first-spend timing/input pattern for EMURGO and the fourth entry.
SELECT
  seed_id,
  label,
  first_spend_tx_hash,
  round(dormant_hours, 3) AS dormant_hours,
  spend_input_count,
  spend_output_count,
  spend_output_lovelace
FROM seed_first_spends_db
WHERE seed_id IN ('emurgo', 'fourth_entry_781m')
ORDER BY first_spend_time_utc;

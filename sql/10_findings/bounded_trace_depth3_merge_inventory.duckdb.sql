-- Runs against data/abcde_genesis_seed_registry.duckdb.
-- Pilot cross-seed merge inventory from bounded_trace_depth3.
WITH input_membership AS (
  SELECT
    tx_hash,
    tx_out_index,
    count(DISTINCT seed_id) AS input_seed_membership_count,
    string_agg(DISTINCT seed_id, '+' ORDER BY seed_id) AS input_seed_ids
  FROM bounded_trace_depth3
  GROUP BY tx_hash, tx_out_index
), traced_inputs AS (
  SELECT
    fs.first_spend_tx_hash AS spend_tx_hash,
    i.input_source_tx_hash AS source_tx_hash,
    i.input_source_tx_out_index AS source_tx_out_index,
    i.input_value_lovelace,
    bt.seed_id,
    im.input_seed_membership_count
  FROM seed_first_spend_inputs i
  JOIN seed_first_spends fs
    ON fs.first_spend_tx_hash = i.first_spend_tx_hash
  JOIN bounded_trace_depth3 bt
    ON bt.tx_hash = i.input_source_tx_hash
   AND bt.tx_out_index = i.input_source_tx_out_index
  JOIN input_membership im
    ON im.tx_hash = i.input_source_tx_hash
   AND im.tx_out_index = i.input_source_tx_out_index
), merge_inputs AS (
  SELECT * FROM traced_inputs
), merge_summary AS (
  SELECT
    spend_tx_hash,
    count(DISTINCT seed_id) AS seed_count,
    string_agg(DISTINCT seed_id, '+' ORDER BY seed_id) AS seed_combo,
    count(DISTINCT source_tx_hash || '#' || source_tx_out_index) AS unique_source_inputs_total,
    count(DISTINCT CASE WHEN input_seed_membership_count > 1 THEN source_tx_hash || '#' || source_tx_out_index END) AS overlapping_source_inputs_total,
    count(DISTINCT CASE WHEN seed_id = 'emurgo' AND input_seed_membership_count = 1 THEN source_tx_hash || '#' || source_tx_out_index END) AS exclusive_inputs_emurgo,
    count(DISTINCT CASE WHEN seed_id = 'fourth_entry_781m' AND input_seed_membership_count = 1 THEN source_tx_hash || '#' || source_tx_out_index END) AS exclusive_inputs_fourth_entry_781m,
    sum(DISTINCT input_value_lovelace) AS total_input_lovelace
  FROM merge_inputs
  GROUP BY spend_tx_hash
  HAVING count(DISTINCT seed_id) > 1
)
SELECT
  *,
  CASE
    WHEN exclusive_inputs_emurgo > 0 AND exclusive_inputs_fourth_entry_781m > 0 THEN 'PAIRWISE_CLEAN'
    ELSE 'PAIRWISE_INHERITED'
  END AS merge_class
FROM merge_summary
ORDER BY spend_tx_hash;

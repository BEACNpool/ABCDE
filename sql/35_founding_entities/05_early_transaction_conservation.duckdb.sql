-- FACT: one early transaction combines these on-chain input paths.
-- Conservation proves the receipt balances. The input paths do not establish
-- beneficial ownership, purchaser identity, or subsequent control.
WITH inputs AS (
  SELECT tx_hash, count(*) AS input_count,
         sum(CAST(value_lovelace AS DECIMAL(38,0))) AS inputs_lovelace
  FROM founding_early_merge_inputs GROUP BY tx_hash
), outputs AS (
  SELECT tx_hash, count(*) AS output_count,
         sum(CAST(value_lovelace AS DECIMAL(38,0))) AS outputs_lovelace,
         max(CAST(fee_lovelace AS DECIMAL(38,0))) AS fee_lovelace,
         count(DISTINCT fee_lovelace) AS distinct_fee_values
  FROM founding_early_merge_outputs GROUP BY tx_hash
)
SELECT i.tx_hash, i.input_count, o.output_count,
       i.inputs_lovelace, o.outputs_lovelace, o.fee_lovelace,
       i.inputs_lovelace - o.outputs_lovelace - o.fee_lovelace
         AS conservation_difference_lovelace,
       o.distinct_fee_values
FROM inputs i JOIN outputs o ON i.tx_hash = o.tx_hash;

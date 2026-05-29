#!/usr/bin/env python3
"""Emit read-only db-sync SQL proving fourth-entry first-spend co-spends an EMURGO-descended UTxO."""
print(r"""
WITH RECURSIVE params AS (
  SELECT
    decode('242608fc18552a4ac83adabcef7155f3b909e83d469ce89735db8f11d3637e38','hex') AS emurgo_seed_hash,
    decode('5ec95a53fa3bb7dc56864bb6e75f369f00aa20e8d8cdc3b66b2fb88ec1b225ef','hex') AS fourth_seed_hash
), emurgo_seed AS (
  SELECT tx.id AS tx_id, encode(tx.hash,'hex') AS tx_hash, txo.index AS tx_out_index, txo.value
  FROM params p
  JOIN public.tx tx ON tx.hash = p.emurgo_seed_hash
  JOIN public.tx_out txo ON txo.tx_id = tx.id
), emurgo_trace AS (
  SELECT
    0 AS depth,
    es.tx_id,
    es.tx_hash,
    es.tx_out_index,
    es.value,
    ARRAY[es.tx_hash]::text[] AS path
  FROM emurgo_seed es

  UNION ALL

  SELECT
    et.depth + 1 AS depth,
    child_tx.id AS tx_id,
    encode(child_tx.hash, 'hex') AS tx_hash,
    child_out.index AS tx_out_index,
    child_out.value,
    et.path || encode(child_tx.hash, 'hex')
  FROM emurgo_trace et
  JOIN public.tx_in spend
    ON spend.tx_out_id = et.tx_id
   AND spend.tx_out_index = et.tx_out_index
  JOIN public.tx child_tx
    ON child_tx.id = spend.tx_in_id
  JOIN public.tx_out child_out
    ON child_out.tx_id = child_tx.id
  WHERE et.depth < 3
), fourth_first_spend AS (
  SELECT spend_tx.id, encode(spend_tx.hash,'hex') AS tx_hash
  FROM params p
  JOIN public.tx seed_tx ON seed_tx.hash = p.fourth_seed_hash
  JOIN public.tx_out seed_out ON seed_out.tx_id = seed_tx.id
  JOIN public.tx_in seed_spend
    ON seed_spend.tx_out_id = seed_tx.id
   AND seed_spend.tx_out_index = seed_out.index
  JOIN public.tx spend_tx ON spend_tx.id = seed_spend.tx_in_id
), fourth_inputs AS (
  SELECT
    ffs.tx_hash AS fourth_first_spend_tx_hash,
    src_tx.id AS input_source_tx_id,
    encode(src_tx.hash, 'hex') AS input_source_tx_hash,
    txi.tx_out_index AS input_source_tx_out_index,
    src_out.value AS input_value_lovelace,
    src_out.address AS input_address
  FROM fourth_first_spend ffs
  JOIN public.tx_in txi ON txi.tx_in_id = ffs.id
  JOIN public.tx src_tx ON src_tx.id = txi.tx_out_id
  JOIN public.tx_out src_out ON src_out.tx_id = src_tx.id AND src_out.index = txi.tx_out_index
)
SELECT
  fi.fourth_first_spend_tx_hash,
  fi.input_source_tx_hash,
  fi.input_source_tx_out_index,
  fi.input_value_lovelace,
  CASE WHEN et.tx_hash IS NULL THEN NULL ELSE 'emurgo' END AS descendant_of_seed_id,
  et.depth AS emurgo_trace_depth,
  array_to_string(et.path, ' > ') AS emurgo_path
FROM fourth_inputs fi
LEFT JOIN emurgo_trace et
  ON et.tx_id = fi.input_source_tx_id
 AND et.tx_out_index = fi.input_source_tx_out_index
ORDER BY fi.input_value_lovelace DESC;
""")

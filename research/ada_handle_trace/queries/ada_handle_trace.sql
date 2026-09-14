-- ADA Handle resolution + first-hop trace helper for ABCDE
--
-- Usage examples:
--   psql -d cexplorer_replica -v handle='bob' -f queries/ada_handle_trace.sql
--   psql -d cexplorer_replica -v handle='ada' -f queries/ada_handle_trace.sql
--
-- Notes:
-- - Input handle should be WITHOUT the leading '$'.
-- - This stays strictly on-chain and relies on explorer.handle_search.
-- - Current output includes:
--   1) resolved current owner
--   2) the tx output row(s) that currently hold the handle owner's address in the resolved tx
--   3) all inputs that funded that tx (the immediate previous hop set)

\if :{?handle}
\else
\echo 'ERROR: pass -v handle=<name> (without leading $)'
\quit 1
\endif

WITH resolved AS (
  SELECT
    h.handle,
    h.handle_display,
    h.current_owner_address,
    h.current_owner_stake,
    h.tx_hash,
    h.block_no,
    h.slot_no,
    h.epoch_no,
    h.observed_at
  FROM explorer.handle_search h
  WHERE lower(h.handle) = lower(:'handle')
), owner_tx AS (
  SELECT
    r.*,
    t.id AS tx_id,
    t.block_id
  FROM resolved r
  JOIN public.tx t
    ON t.hash = decode(r.tx_hash, 'hex')
), owner_outputs AS (
  SELECT
    ot.*,
    txo.id AS tx_out_id,
    txo.index AS tx_out_index,
    txo.value::text AS owner_output_lovelace,
    txo.consumed_by_tx_id
  FROM owner_tx ot
  JOIN public.tx_out txo
    ON txo.tx_id = ot.tx_id
   AND txo.address = ot.current_owner_address
), funding_inputs AS (
  SELECT DISTINCT
    oo.handle,
    oo.handle_display,
    oo.current_owner_address,
    oo.current_owner_stake,
    encode(t_target.hash::bytea, 'hex') AS owner_tx_hash,
    b_target.block_no AS owner_block_no,
    txo_prev.tx_id AS source_tx_id,
    encode(t_prev.hash::bytea, 'hex') AS source_tx_hash,
    txo_prev.index AS source_tx_out_index,
    txo_prev.address AS source_address,
    sa_prev.view AS source_stake,
    txo_prev.value::text AS source_lovelace,
    b_prev.block_no AS source_block_no,
    b_prev.time AS source_block_time
  FROM owner_outputs oo
  JOIN public.tx t_target
    ON t_target.id = oo.tx_id
  JOIN public.block b_target
    ON b_target.id = oo.block_id
  JOIN public.tx_in ti
    ON ti.tx_in_id = oo.tx_id
  JOIN public.tx_out txo_prev
    ON txo_prev.tx_id = ti.tx_out_id
   AND txo_prev.index = ti.tx_out_index
  JOIN public.tx t_prev
    ON t_prev.id = txo_prev.tx_id
  JOIN public.block b_prev
    ON b_prev.id = t_prev.block_id
  LEFT JOIN public.stake_address sa_prev
    ON sa_prev.id = txo_prev.stake_address_id
)
SELECT
  'handle_resolution' AS section,
  r.handle,
  r.handle_display,
  r.current_owner_address,
  r.current_owner_stake,
  r.tx_hash,
  r.block_no,
  r.slot_no,
  r.epoch_no,
  r.observed_at,
  NULL::text AS owner_tx_out_index,
  NULL::text AS owner_output_lovelace,
  NULL::text AS source_tx_hash,
  NULL::text AS source_tx_out_index,
  NULL::text AS source_address,
  NULL::text AS source_stake,
  NULL::text AS source_lovelace,
  NULL::text AS source_block_no,
  NULL::timestamp AS source_block_time
FROM resolved r

UNION ALL

SELECT
  'owner_output' AS section,
  oo.handle,
  oo.handle_display,
  oo.current_owner_address,
  oo.current_owner_stake,
  oo.tx_hash,
  oo.block_no,
  oo.slot_no,
  oo.epoch_no,
  oo.observed_at,
  oo.tx_out_index::text AS owner_tx_out_index,
  oo.owner_output_lovelace,
  NULL::text AS source_tx_hash,
  NULL::text AS source_tx_out_index,
  NULL::text AS source_address,
  NULL::text AS source_stake,
  NULL::text AS source_lovelace,
  NULL::text AS source_block_no,
  NULL::timestamp AS source_block_time
FROM owner_outputs oo

UNION ALL

SELECT
  'first_hop_inputs' AS section,
  fi.handle,
  fi.handle_display,
  fi.current_owner_address,
  fi.current_owner_stake,
  fi.owner_tx_hash AS tx_hash,
  fi.owner_block_no AS block_no,
  NULL::bigint AS slot_no,
  NULL::integer AS epoch_no,
  NULL::timestamp AS observed_at,
  NULL::text AS owner_tx_out_index,
  NULL::text AS owner_output_lovelace,
  fi.source_tx_hash,
  fi.source_tx_out_index::text,
  fi.source_address,
  fi.source_stake,
  fi.source_lovelace,
  fi.source_block_no::text,
  fi.source_block_time
FROM funding_inputs fi
ORDER BY section, block_no NULLS LAST, source_block_no NULLS LAST;

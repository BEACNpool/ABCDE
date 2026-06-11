-- Pools whose registered owner or reward stake address is itself reached by
-- a Genesis trace. This is the pool-operator linkage surface: it shows where
-- trace-reached credentials appear in pool registration certificates, which
-- is stronger evidence of operational linkage than delegation alone.
--
-- psql variables:
--   stage_schema: staged trace schema (uses all-time trace_utxos membership)
--
-- Evidence boundary: registration linkage is an on-chain observation about
-- certificates. It is not custody, beneficial-ownership, identity, or intent
-- evidence on its own.
WITH traced_creds AS (
  SELECT
    stake_address_id,
    min(min_depth) AS min_trace_depth,
    string_agg(DISTINCT root_seed_id, '+' ORDER BY root_seed_id) AS root_combo
  FROM :"stage_schema".trace_utxos
  WHERE stake_address_id IS NOT NULL
  GROUP BY stake_address_id
),
latest_update AS (
  SELECT DISTINCT ON (pu.hash_id)
    pu.id,
    pu.hash_id,
    pu.active_epoch_no,
    pu.pledge,
    pu.margin,
    pu.fixed_cost,
    pu.reward_addr_id,
    pu.registered_tx_id
  FROM public.pool_update pu
  ORDER BY pu.hash_id, pu.registered_tx_id DESC, pu.cert_index DESC
),
links AS (
  SELECT
    lu.hash_id,
    'owner' AS link_role,
    po.addr_id AS linked_stake_address_id,
    lu.active_epoch_no,
    lu.pledge,
    lu.registered_tx_id
  FROM latest_update lu
  JOIN public.pool_owner po ON po.pool_update_id = lu.id
  JOIN traced_creds tc ON tc.stake_address_id = po.addr_id
  UNION ALL
  SELECT
    lu.hash_id,
    'reward_address' AS link_role,
    lu.reward_addr_id AS linked_stake_address_id,
    lu.active_epoch_no,
    lu.pledge,
    lu.registered_tx_id
  FROM latest_update lu
  JOIN traced_creds tc ON tc.stake_address_id = lu.reward_addr_id
)
SELECT
  to_char(now() AT TIME ZONE 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS"Z"') AS snapshot_utc,
  :'stage_schema' AS trace_schema,
  ph.view AS pool_id_bech32,
  l.link_role,
  sa.view AS linked_stake_address,
  tc.min_trace_depth,
  tc.root_combo,
  l.active_epoch_no AS pool_active_epoch_no,
  l.pledge AS pledge_lovelace,
  encode(rtx.hash, 'hex') AS registration_tx_hash
FROM links l
JOIN public.pool_hash ph ON ph.id = l.hash_id
JOIN public.stake_address sa ON sa.id = l.linked_stake_address_id
JOIN traced_creds tc ON tc.stake_address_id = l.linked_stake_address_id
LEFT JOIN public.tx rtx ON rtx.id = l.registered_tx_id
ORDER BY ph.view, l.link_role, sa.view;

-- liquidity_intel_detect.sql — standing detection of dormant/genesis ADA
-- awakenings, and whether they head toward tagged exchange-deposit addresses.
-- Runs ON abcde (local intel schema; public.* read-only). Idempotent 24h-window
-- upsert; safe to run hourly with overlap. SPEND DETECTION USES tx_in — never
-- consumed_by_tx_id (0%-populated on this db-sync).
\set ON_ERROR_STOP on
SET work_mem = '512MB';

CREATE SCHEMA IF NOT EXISTS intel;

CREATE TABLE IF NOT EXISTS intel.dormant_moves (
  from_tx_id        bigint    NOT NULL,
  from_index        smallint  NOT NULL,
  spend_tx_hash     text      NOT NULL,
  spend_time        timestamptz NOT NULL,
  spend_date        date      NOT NULL,
  from_created      timestamptz,
  dormancy_years    numeric,
  tier              text      NOT NULL,          -- 'genesis' | '7y' | '5y'
  ada               numeric   NOT NULL,
  from_address      text      NOT NULL,
  to_exchange_tag   text,                        -- null unless toward a tagged deposit addr
  toward_liquidity  boolean   NOT NULL DEFAULT false,
  first_ever_genesis boolean  NOT NULL DEFAULT false,
  detected_at       timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (from_tx_id, from_index)           -- an output is spent exactly once
);
CREATE INDEX IF NOT EXISTS dormant_moves_spend_date_idx ON intel.dormant_moves (spend_date);
CREATE INDEX IF NOT EXISTS dormant_moves_tier_idx       ON intel.dormant_moves (tier);
CREATE INDEX IF NOT EXISTS dormant_moves_liq_idx        ON intel.dormant_moves (toward_liquidity) WHERE toward_liquidity;

CREATE TABLE IF NOT EXISTS intel.liquidity_daily (
  spend_date           date    NOT NULL,
  tier                 text    NOT NULL,
  events               bigint  NOT NULL,
  ada_awakened         numeric NOT NULL,
  ada_toward_liquidity numeric NOT NULL,
  distinct_exchanges   int     NOT NULL,
  largest_single_ada   numeric NOT NULL,
  PRIMARY KEY (spend_date, tier)
);

CREATE TABLE IF NOT EXISTS intel.build_receipt (
  run_at       timestamptz NOT NULL DEFAULT now(),
  tip_block    bigint,
  tip_time     timestamptz,
  window_hours int,
  new_events   bigint,
  run_seconds  numeric
);

-- ---- detection (24h lookback) --------------------------------------------
WITH recent_spends AS (
  SELECT ti.tx_out_id, ti.tx_out_index,
         stx.id AS spend_tx_id, encode(stx.hash,'hex') AS spend_tx_hash, sb.time AS spend_time
  FROM public.block sb
  JOIN public.tx stx   ON stx.block_id = sb.id
  JOIN public.tx_in ti ON ti.tx_in_id = stx.id
  WHERE sb.time > now() - interval '24 hours'
),
awakened AS (
  SELECT rs.spend_tx_id, rs.spend_tx_hash, rs.spend_time,
         o.tx_id AS from_tx_id, o.index AS from_index, o.value AS lovelace, o.address AS from_address,
         cb.time AS from_created, (cb.id = 1) AS is_genesis
  FROM recent_spends rs
  JOIN public.tx_out o ON o.tx_id = rs.tx_out_id AND o.index = rs.tx_out_index
  JOIN public.tx ct    ON ct.id = o.tx_id
  JOIN public.block cb ON cb.id = ct.block_id
  WHERE cb.id = 1 OR cb.time < now() - interval '5 years'
),
liq AS (   -- does the spending tx pay any tagged exchange-deposit address?
  SELECT a.spend_tx_id, string_agg(DISTINCT t.tag, ',' ORDER BY t.tag) AS tags
  FROM awakened a
  JOIN public.tx_out so ON so.tx_id = a.spend_tx_id
  JOIN governance.genesis_address_tags t
    ON t.address = so.address AND t.tag LIKE 'claimed_deposit:%'
  GROUP BY a.spend_tx_id
)
INSERT INTO intel.dormant_moves
  (from_tx_id, from_index, spend_tx_hash, spend_time, spend_date, from_created,
   dormancy_years, tier, ada, from_address, to_exchange_tag, toward_liquidity, first_ever_genesis)
SELECT a.from_tx_id, a.from_index, a.spend_tx_hash, a.spend_time, a.spend_time::date, a.from_created,
       round(extract(epoch FROM (a.spend_time - a.from_created)) / 31557600.0, 2),
       CASE WHEN a.is_genesis THEN 'genesis'
            WHEN a.from_created < now() - interval '7 years' THEN '7y'
            ELSE '5y' END,
       a.lovelace / 1e6, a.from_address,
       liq.tags, liq.tags IS NOT NULL, a.is_genesis
FROM awakened a
LEFT JOIN liq ON liq.spend_tx_id = a.spend_tx_id
ON CONFLICT (from_tx_id, from_index) DO UPDATE
  SET to_exchange_tag = EXCLUDED.to_exchange_tag,
      toward_liquidity = EXCLUDED.toward_liquidity;

-- ---- rollup (recent days) -------------------------------------------------
INSERT INTO intel.liquidity_daily
  (spend_date, tier, events, ada_awakened, ada_toward_liquidity, distinct_exchanges, largest_single_ada)
SELECT spend_date, tier, count(*), sum(ada),
       COALESCE(sum(ada) FILTER (WHERE toward_liquidity), 0),
       count(DISTINCT to_exchange_tag), max(ada)
FROM intel.dormant_moves
WHERE spend_date >= current_date - 2
GROUP BY spend_date, tier
ON CONFLICT (spend_date, tier) DO UPDATE
  SET events = EXCLUDED.events, ada_awakened = EXCLUDED.ada_awakened,
      ada_toward_liquidity = EXCLUDED.ada_toward_liquidity,
      distinct_exchanges = EXCLUDED.distinct_exchanges,
      largest_single_ada = EXCLUDED.largest_single_ada;

INSERT INTO intel.build_receipt (tip_block, tip_time, window_hours, new_events, run_seconds)
SELECT (SELECT max(block_no) FROM public.block),
       (SELECT max(time) FROM public.block),
       24,
       (SELECT count(*) FROM intel.dormant_moves WHERE detected_at > now() - interval '2 minutes'),
       extract(epoch FROM clock_timestamp() - now());

GRANT USAGE ON SCHEMA intel TO web_anon;
GRANT SELECT ON ALL TABLES IN SCHEMA intel TO web_anon;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA intel GRANT SELECT ON TABLES TO web_anon;

\echo === last run ===
SELECT * FROM intel.build_receipt ORDER BY run_at DESC LIMIT 1;
SELECT tier, count(*) events, round(sum(ada)) ada, count(*) FILTER (WHERE toward_liquidity) to_exchange
FROM intel.dormant_moves WHERE spend_time > now() - interval '24 hours' GROUP BY tier ORDER BY tier;

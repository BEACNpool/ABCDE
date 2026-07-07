-- build_scrolls_schema.sql — Ledger Scrolls on-chain index (scrolls schema on abcde).
-- Seeded from the AUTHORITATIVE published registry (ledger-scrolls
-- registry/published/registry-list.json), then verified against the chain.
-- Scrolls are identified by their registry pointer, NEVER by asset-name pattern
-- (which matches unrelated tokens). Two pointer kinds resolve two ways:
--   * tx pointers (manifest-chain-v2, utxo-inline-datum-bytes-v1) -> pointer_tx in public.tx
--   * cip25-pages-v1 -> policyId + manifestAsset via the asset mint (ma_tx_mint)
-- Read-only on public.*. Grading: on-chain presence is FACT; content trust is the sha256.
\set ON_ERROR_STOP on

CREATE SCHEMA IF NOT EXISTS scrolls;

DROP VIEW IF EXISTS scrolls.onchain;
DROP TABLE IF EXISTS scrolls.registry CASCADE;
CREATE TABLE scrolls.registry (
  name           text PRIMARY KEY,
  pointer_tx     text,
  pointer_ix     int,
  pointer_kind   text,
  content_type   text,
  sha256         text,
  size_bytes     bigint,
  pointer_policy text,
  pointer_asset  text
);

INSERT INTO scrolls.registry
  (name, pointer_tx, pointer_ix, pointer_kind, content_type, sha256, size_bytes, pointer_policy, pointer_asset)
VALUES
('ledger-scrolls-000','d8875be1a21dffca56252ddd22e701ae088645518e48c49f873449b87802e96d',0,'manifest-chain-v2','text/html','19ba8fccd3bd7e5ac997c3a4a0ff768a2699959bfd3bcf9db2ae073c09fe5013',5055,'',''),
('beacn-leaks-000','f3ee01c1e742c27c205867de4cfa8836e4ab541b9da0d5652aa4d269c73255c7',0,'manifest-chain-v2','text/html','025a81aeffe8aed98868b89b8f04a1f137f698362cfebafd2f8b5a56312d49b2',10304,'',''),
('beacn-leaks-001','08c707b3ab7880f983be7f78bd56c4de38461d514c6597d95cd5da1abc307565',0,'manifest-chain-v2','text/html','5917a884f449fd1c76fc0241791468a37b2b54883c0b8b98022a9f372f7d68b9',9794,'',''),
('beacn-leaks-002','1b465d3f9368cf6e1a36ae536631ffed9ca12b35c3bd2843bc423398140174fc',0,'manifest-chain-v2','text/html','16612dfb6cef652e23014fecba3108996edb76c1d62d37562a2d799cb7165a55',7500,'',''),
('the-spec','e4845deed98471b29b35689cfdb76f18add189c8d8f5c61b2ef32ea7ce6d5cf9',0,'manifest-chain-v2','text/markdown','4793c38349cca60d552c52d68dfd950f3dd945db55c8a6a87f05ca6d98e3b242',5518,'',''),
('the-reader','9a564165ebdc4e0c4a2e1163b5cf9355604ecb8e163b425d834570e5b9007de2',0,'manifest-chain-v2','text/html','a824298dc5ced0aad1954c7d8d40bb6dda09debf402f062ab402dcebbb6a9215',16634,'',''),
('legal-0001','ceced54b2bd462b1ed41864f2583309666010ce1fb96b9f3dc9968174d958bc9',0,'manifest-chain-v2','text/html','8c95db4bb4248d82d3d5c4bb49dfe0200d779f4b6905cd3b5649fcb847378bc1',11192,'',''),
('eternal-scroll','ef8dce1c6359c7ae6cc44f04d60b32e6bc26987ebf30a78259c65b2063ba3b18',0,'manifest-chain-v2','text/html','65824f624bc58140a33123d3e2383ea408135e5db666fcb8a0759b2846447dd2',18182,'',''),
('genesis-scroll','a19f64fba94abdc37b50012d5d602c75a1ca73c82520ae030fc6b4e82274ceb2',0,'utxo-inline-datum-bytes-v1','text/plain','',0,'',''),
('architects-scroll','076d6800d8ccafbaa31c32a6e23eecfc84f7d1e35c31a9128ec53736d5395747',0,'utxo-inline-datum-bytes-v1','text/plain','531a1eba80b297f8822b1505d480bb1c7f1bad2878ab29d8be01ba0e1fc67e12',3010,'',''),
('hosky-png','728660515c6d9842d9f0ffd273f2b487a4070fd9f4bd5455a42e3a56880389be',0,'utxo-inline-datum-bytes-v1','image/png','798e3296d45bb42e7444dbf64e1eb16b02c86a233310407e7d8baf97277f642f',0,'',''),
('first-words','',0,'cip25-pages-v1','text/plain','',0,'beec4b31f21ae4567f9c849eada2f23f4f0b76c7949a1baaef623cba','FIRST_WORDS_MANIFEST'),
('first-video','',0,'cip25-pages-v1','video/mp4','aebd63a8cdeb7aeb0a64733ab3ecd4d98557b4b337a0af60dbc1f59c7de65814',0,'38fbd56d7de6eb9df88599b5b102304df4c817aee53e4fb9c59cbed2','CM_MANIFEST'),
('bible','',0,'cip25-pages-v1','text/html','b226867233fbaf06495b1fe6974c37f4547b19f57e49d7f64701cf40f86c5dc5',4680000,'2f0c8b54ef86ffcdd95ba87360ca5b485a8da4f085ded7988afc77e0','BIBLE_MANIFEST'),
('bitcoin-whitepaper','',0,'cip25-pages-v1','text/html','6693c86312b7125666760d316572c9db984c6e2bae9fca344dafde77efc9253a',0,'8dc3cb836ab8134c75e369391b047f5c2bf796df10d9bf44a33ef6d1','BITCOIN_MANIFEST'),
('constitution-e608','',0,'cip25-pages-v1','text/plain','98a29aec8664b62912c1c0355ebae1401b7c0e53d632e8f05479e7821935abf1',0,'ef91a425ef57d92db614085ef03718407fb293cb4b770bc6e03f9750','CONSTITUTION_E608_MANIFEST'),
('constitution-e541','',0,'cip25-pages-v1','text/plain','1939c1627e49b5267114cbdb195d4ac417e545544ba6dcb47e03c679439e9566',0,'d7559bbfa87f53674570fd01f564687c2954503b510ead009148a31d','CONSTITUTION_E541_MANIFEST')
;

-- On-chain verification, unifying both pointer resolution paths.
CREATE VIEW scrolls.onchain AS
WITH tx_path AS (
  SELECT r.name, b.block_no, b.time AS published_at, b.epoch_no
  FROM scrolls.registry r
  JOIN public.tx t    ON r.pointer_tx <> '' AND t.hash = decode(r.pointer_tx, 'hex')
  JOIN public.block b ON b.id = t.block_id
),
cip25_path AS (
  SELECT r.name, min(b.block_no) AS block_no, min(b.time) AS published_at, min(b.epoch_no) AS epoch_no
  FROM scrolls.registry r
  JOIN public.multi_asset ma
    ON r.pointer_policy <> '' AND ma.policy = decode(r.pointer_policy, 'hex')
   AND ma.name = convert_to(r.pointer_asset, 'UTF8')
  JOIN public.ma_tx_mint mtm ON mtm.ident = ma.id
  JOIN public.tx t           ON t.id = mtm.tx_id
  JOIN public.block b        ON b.id = t.block_id
  GROUP BY r.name
)
SELECT r.name, r.pointer_kind, r.content_type, r.sha256, r.size_bytes,
       r.pointer_tx, r.pointer_policy, r.pointer_asset,
       COALESCE(tp.block_no, cp.block_no)                        AS published_block,
       COALESCE(tp.published_at, cp.published_at)                AS published_at,
       COALESCE(tp.epoch_no, cp.epoch_no)                        AS published_epoch,
       (COALESCE(tp.block_no, cp.block_no) IS NOT NULL)          AS present_onchain
FROM scrolls.registry r
LEFT JOIN tx_path tp    ON tp.name = r.name
LEFT JOIN cip25_path cp ON cp.name = r.name;

GRANT USAGE ON SCHEMA scrolls TO web_anon;
GRANT SELECT ON scrolls.registry, scrolls.onchain TO web_anon;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA scrolls GRANT SELECT ON TABLES TO web_anon;
NOTIFY pgrst, 'reload schema';

\echo === registry vs on-chain ===
SELECT count(*) AS registered,
       count(*) FILTER (WHERE present_onchain) AS verified_onchain,
       min(published_at)::date AS first_published,
       max(published_at)::date AS last_published
FROM scrolls.onchain;

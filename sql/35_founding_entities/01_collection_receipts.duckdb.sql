-- FACT: table-specific collection boundaries. Historical selectors and
-- public-source assertions carry their own source kind, not the chain tip.
SELECT table_name, source_kind, collection_started_utc, collection_finished_utc,
       db_tip_block, db_tip_epoch, db_tip_time, db_tip_hash,
       query_path, row_count, csv_sha256
FROM founding_query_receipts
ORDER BY source_kind, table_name;

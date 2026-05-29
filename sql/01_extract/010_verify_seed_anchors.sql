-- Verify seed tx hashes against db-sync.
-- Requires genesis.seed_registry populated.

SELECT
  sr.seed_id,
  sr.label,
  sr.tx_hash_hex,
  encode(tx.hash, 'hex') AS db_tx_hash,
  b.epoch_no,
  b.time AS block_time_utc,
  tx.id AS tx_id,
  (SELECT count(*) FROM public.tx_in  WHERE tx_in_id = tx.id) AS input_count,
  (SELECT count(*) FROM public.tx_out WHERE tx_id    = tx.id) AS output_count,
  (SELECT sum(value) FROM public.tx_out WHERE tx_id  = tx.id) AS output_lovelace
FROM genesis.seed_registry sr
LEFT JOIN public.tx tx
  ON tx.hash = decode(sr.tx_hash_hex, 'hex')
LEFT JOIN public.block b
  ON b.id = tx.block_id
ORDER BY sr.seed_id;

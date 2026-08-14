-- Warehouse extract for F20 (read-only). Run on abcde:
--   sudo -n -u postgres psql -d cexplorer_replica -f sql/10_findings/F20_emurgo_genesis_drep_removal.remote.sql
-- Then copy the /tmp/emurgo_*.csv files into data/small/.
-- Identity hashes are the CIP-105 payloads EMURGO published on 2025-06-02
-- plus the official / Yoroi db-sync hashes.

-- See findings/F20_emurgo_genesis_drep_removal.md for the committed CSVs
-- already produced from this procedure at tip epoch 649 / block 13808619.
SELECT
  'see committed data/small/emurgo_*.csv and emurgo_f20_receipt.csv' AS note,
  now() AT TIME ZONE 'UTC' AS now_utc,
  max(time) AT TIME ZONE 'UTC' AS tip_utc,
  max(block_no) AS tip_block,
  max(epoch_no) AS tip_epoch
FROM block;

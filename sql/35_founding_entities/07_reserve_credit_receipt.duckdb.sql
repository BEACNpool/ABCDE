-- FACT: reserve credits in this transaction, not reconstructed spending or
-- independent proof of any off-chain payment beneficiary.
SELECT tx_hash, cert_index, stake_address, epoch_no, block_time,
       CAST(value_lovelace AS DECIMAL(38,0)) AS credited_lovelace,
       sum(CAST(value_lovelace AS DECIMAL(38,0))) OVER (PARTITION BY tx_hash)
         AS transaction_credited_lovelace
FROM founding_reserve_credits
ORDER BY tx_hash, cert_index, stake_address;

# db-sync Schema Notes

## Critical join note
`tx_in.tx_out_id` references `tx.id` for the producing transaction, not `tx_out.id`.

Correct spend join pattern:
```sql
JOIN tx_in txi ON txi.tx_out_id = producing_tx.id AND txi.tx_out_index = txo.index
JOIN tx spend_tx ON spend_tx.id = txi.tx_in_id
```

Correct unspent check:
```sql
LEFT JOIN tx_in txi ON txi.tx_out_id = producing_tx.id AND txi.tx_out_index = txo.index
WHERE txi.tx_in_id IS NULL
```

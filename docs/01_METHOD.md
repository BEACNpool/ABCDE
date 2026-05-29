# Method

## Source database

Maintainer builds use the ABCDE db-sync replica. `public.*` is treated as read-only replicated chain data.

Derived tables should live in dedicated schemas such as `genesis`, `labels`, and `evidence`.

## Critical db-sync join rule

`tx_in.tx_out_id` references the producing transaction id (`tx.id`), **not** `tx_out.id`.

Correct spend join:

```sql
JOIN public.tx_in txi
  ON txi.tx_out_id = producing_tx.id
 AND txi.tx_out_index = produced_output.index
JOIN public.tx spend_tx
  ON spend_tx.id = txi.tx_in_id
```

Correct unspent check:

```sql
LEFT JOIN public.tx_in txi
  ON txi.tx_out_id = producing_tx.id
 AND txi.tx_out_index = produced_output.index
WHERE txi.tx_in_id IS NULL
```

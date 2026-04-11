# Method and Data Provenance

- Source: Cardano db-sync PostgreSQL replica `cexplorer_replica`
- Sync state documented in archived findings: block `13,215,210` at `2026-03-28 00:27:10 UTC`
- Trace runs documented in archived findings: IOG `run_id=7`, CF `run_id=8`, EMURGO `run_id=9`, EMURGO_2 `run_id=10`
- Method: direct SQL against replicated chain data and exported artifacts preserved in the repository

## Critical db-sync schema note
`tx_in.tx_out_id` references `tx.id` for the producing transaction, not `tx_out.id`.

Correct join pattern:
```sql
JOIN tx_in txi ON txi.tx_out_id = producing_tx.id AND txi.tx_out_index = txo.index
JOIN tx spend_tx ON spend_tx.id = txi.tx_in_id
```

Correct unspent check:
```sql
LEFT JOIN tx_in txi ON txi.tx_out_id = producing_tx.id AND txi.tx_out_index = txo.index
WHERE txi.tx_in_id IS NULL
```

# F02b — Fourth-Entry First Spend Directly Co-Spends EMURGO-Descended UTxO

## Claim

The fourth-entry first spend transaction `c8596b9cd81f734f8129604ff86f23bd4a910465acb84ad9e9d1ac223ccb4a76` consumed two inputs:

1. the fourth-entry seed output, and
2. an EMURGO-descended UTxO at trace depth 2.

This establishes direct first-spend operational convergence. It does **not** prove beneficial ownership.

## Grade

FACT for the co-spend and EMURGO-descended input path.

## Evidence

- `data/small/fourth_entry_direct_cospend_db.csv`
- `data/abcde_genesis_seed_registry.duckdb`

## Reproduce

```sql
SELECT
  fourth_first_spend_tx_hash,
  input_source_tx_hash,
  input_value_lovelace,
  descendant_of_seed_id,
  emurgo_trace_depth,
  emurgo_path
FROM fourth_entry_direct_cospend_db
ORDER BY input_value_lovelace DESC;
```

Expected current result includes one row where:

- `descendant_of_seed_id = 'emurgo'`
- `emurgo_trace_depth = 2`
- path begins with EMURGO seed tx `242608fc...` and ends at `743fd051...`

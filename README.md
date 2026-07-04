# NIGHT full spend-flow graph (release bundle)

Parquet+ZSTD, split into <45 MB parts so it fits GitHub's per-file push limit.
Fetch with `python scripts/fetch_night_full.py`; query with DuckDB, e.g.

```sql
SELECT count(*) FROM parquet_scan('utxo_nodes/*.parquet');
```

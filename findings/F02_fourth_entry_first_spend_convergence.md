# F02 — Fourth-Entry First-Spend Operational Convergence

## Claim

The fourth-entry seed output and the named EMURGO seed output both activated after roughly `475.1` hours of dormancy. The fourth-entry first spend used a two-input transaction, making it an immediate convergence point rather than a later frontier-only overlap.

## Grade

FACT for timing, transaction hashes, and input counts. Interpretation remains bounded: this is operational convergence / shared administration signal, not proof of beneficial ownership.

## Evidence

Source receipt:

- `data/small/seed_first_spends_db.csv`

Published local artifact:

- `data/abcde_genesis_seed_registry.duckdb`

## Reproduce

```sql
SELECT
  seed_id,
  label,
  first_spend_tx_hash,
  round(dormant_hours, 3) AS dormant_hours,
  spend_input_count,
  spend_output_count,
  spend_output_lovelace
FROM seed_first_spends
WHERE seed_id IN ('emurgo', 'fourth_entry_781m')
ORDER BY first_spend_time_utc;
```

Expected current result:

| seed_id | dormant_hours | spend_input_count |
| --- | ---: | ---: |
| emurgo | 475.094 | 1 |
| fourth_entry_781m | 475.111 | 2 |

## Limitation

Byron-era shared infrastructure can indicate common custody or administration without proving common legal/beneficial ownership.

# Genesis Founders Dataset — Methodology

**Data source:** PostgreSQL db-sync replica  
**Sync state:** Block 13,215,210 (2026-03-28 00:27:10 UTC)  
**Execution:** All queries read-only, no data modification

---

## Database Schema

Relevant db-sync tables:
- `tx` — Transactions
- `tx_out` — Transaction outputs
- `tx_in` — Transaction inputs (spends)
- `stake_address` — Stake addresses (Shelley era)
- `delegation` — Pool delegation history
- `delegation_vote` — DRep delegation history
- `block` — Block metadata (time, epoch)
- `pool_hash` — Pool identifiers

---

## Trace Algorithm

### Step 1: Verify Genesis Anchor

```sql
-- Example for IOG
SELECT 
  tx.id,
  tx.hash,
  encode(tx.hash, 'hex') as tx_hash_hex,
  tx_out.id as tx_out_id,
  tx_out.value,
  b.time
FROM tx
JOIN tx_out ON tx.id = tx_out.tx_id
JOIN block b ON tx.block_id = b.id
WHERE tx.hash = decode('fa2d2a70c0b5fd45cb6c3989f02813061f9d27f15f30ecddd38780c59f413c62', 'hex');
```

### Step 2: Find Spending Transactions

```sql
-- For each output in frontier, find its spend
SELECT 
  tx_in.tx_out_id as source_tx_out_id,
  tx_in.tx_in_id as spending_tx_id,
  encode(tx.hash, 'hex') as spending_tx_hash
FROM tx_in
JOIN tx ON tx_in.tx_in_id = tx.id
WHERE tx_in.tx_out_id = [source_tx_out_id];
```

### Step 3: Extract Descendant Outputs

```sql
-- For each spending transaction, get all outputs
SELECT 
  tx_out.id as descendant_tx_out_id,
  tx_out.address as descendant_address,
  tx_out.value as descendant_value,
  tx_out.stake_address_id,
  sa.view as stake_address,
  b.time as block_time,
  b.epoch_no
FROM tx_out
LEFT JOIN stake_address sa ON tx_out.stake_address_id = sa.id
JOIN tx ON tx_out.tx_id = tx.id
JOIN block b ON tx.block_id = b.id
WHERE tx.id = [spending_tx_id];
```

### Step 4: Repeat Until Frontier Empty

Continue steps 2-3 for each unspent output until:
- All branches reach Shelley era (stake_address_id IS NOT NULL)
- All branches reach current unspent state (no tx_in record)
- All branches reach dust threshold (<1 ADA)

### Step 5: Extract Delegation History

```sql
-- For all Shelley stake addresses found
SELECT 
  d.addr_id,
  sa.view as stake_address,
  ph.view as pool_id_bech32,
  d.active_epoch_no,
  encode(tx.hash, 'hex') as tx_hash,
  b.time as block_time,
  b.epoch_no
FROM delegation d
JOIN stake_address sa ON d.addr_id = sa.id
JOIN pool_hash ph ON d.pool_hash_id = ph.id
JOIN tx ON d.tx_id = tx.id
JOIN block b ON tx.block_id = b.id
WHERE d.addr_id IN ([stake_address_ids])
ORDER BY d.active_epoch_no;
```

### Step 6: Extract DRep Delegation

```sql
-- For all Shelley stake addresses found
SELECT 
  sa.view as stake_address,
  dv.addr_id,
  drep.view as drep_id_bech32,
  b.epoch_no,
  encode(tx.hash, 'hex') as tx_hash,
  b.time as block_time
FROM delegation_vote dv
JOIN stake_address sa ON dv.addr_id = sa.id
LEFT JOIN drep_hash drep ON dv.drep_hash_id = drep.id
JOIN tx ON dv.tx_id = tx.id
JOIN block b ON tx.block_id = b.id
WHERE dv.addr_id IN ([stake_address_ids])
ORDER BY b.epoch_no;
```

---

## Current Unspent State

```sql
-- Find all outputs not yet spent
SELECT 
  tx_out.id as dest_tx_out_id,
  tx_out.address as dest_address,
  sa.view as dest_stake_address,
  tx_out.value as lovelace,
  tx_out.value / 1000000.0 as ada,
  b.time as block_time,
  b.epoch_no,
  encode(tx.hash, 'hex') as dest_tx_hash,
  CASE 
    WHEN tx_out.stake_address_id IS NULL THEN 'BYRON'
    ELSE 'SHELLEY'
  END as era
FROM tx_out
LEFT JOIN stake_address sa ON tx_out.stake_address_id = sa.id
JOIN tx ON tx_out.tx_id = tx.id
JOIN block b ON tx.block_id = b.id
WHERE tx_out.id NOT IN (
  SELECT tx_out_id FROM tx_in
)
AND tx_out.id IN ([traced_output_ids]);
```

---

## De-Overlap Analysis (EMURGO vs EMURGO_2)

```sql
-- Find stake addresses appearing in both lineages
WITH emurgo_stakes AS (
  SELECT DISTINCT stake_address_id 
  FROM [emurgo_traced_outputs]
  WHERE stake_address_id IS NOT NULL
),
emurgo2_stakes AS (
  SELECT DISTINCT stake_address_id 
  FROM [emurgo2_traced_outputs]
  WHERE stake_address_id IS NOT NULL
)
SELECT 
  sa.view as stake_address,
  'BOTH_EMURGO_SEEDS' as overlap_type,
  COUNT(DISTINCT e1.id) as emurgo_outputs,
  COUNT(DISTINCT e2.id) as emurgo2_outputs,
  SUM(DISTINCT e1.value) / 1000000.0 as emurgo_ada,
  SUM(DISTINCT e2.value) / 1000000.0 as emurgo2_ada
FROM stake_address sa
JOIN emurgo_stakes es1 ON sa.id = es1.stake_address_id
JOIN emurgo2_stakes es2 ON sa.id = es2.stake_address_id
LEFT JOIN [emurgo_outputs] e1 ON e1.stake_address_id = sa.id
LEFT JOIN [emurgo2_outputs] e2 ON e2.stake_address_id = sa.id
GROUP BY sa.view;
```

---

## Reproducibility Instructions

### Prerequisites
- Access to Cardano db-sync PostgreSQL database (synced to at least block 13,215,210)
- PostgreSQL client (`psql` or equivalent)
- Sufficient disk space for intermediate results

### Execution Steps

1. **Verify anchor transactions exist:**
   ```bash
   psql -h [db-host] -U [user] -d cexplorer -c "SELECT encode(hash, 'hex') FROM tx WHERE hash = decode('[anchor_hash]', 'hex');"
   ```

2. **Run trace algorithm** (iterative, depth-first or breadth-first):
   - Start with anchor tx_out
   - Apply Step 2 (find spends)
   - Apply Step 3 (extract descendants)
   - Record edges to CSV
   - Repeat for new frontier

3. **Extract delegation histories** once Shelley stakes identified

4. **Calculate unspent state** from final frontier

5. **Export to CSV** with provided column headers

### Expected Runtime
- IOG: ~5-10 minutes (102K edges)
- EMURGO: ~5-10 minutes (102K edges)
- EMURGO_2: ~5-10 minutes (86K edges)
- CF: ~10-15 minutes (115K edges)

Runtime varies based on db-sync hardware and query optimization.

---

## Verification Checklist

- [ ] All anchor transaction hashes resolve in db-sync
- [ ] All traced tx_out IDs exist in database
- [ ] All stake addresses are valid bech32
- [ ] Delegation events match db-sync records
- [ ] Unspent outputs have no tx_in records
- [ ] Row counts match documented totals
- [ ] Timestamp range matches earliest_tx → latest_tx

---

## Notes

- **Byron vs Shelley:** Byron-era outputs have `stake_address_id = NULL`
- **Dust threshold:** Outputs <1 ADA may be excluded from further tracing
- **Hop depth:** Distance from Genesis anchor (anchor = hop 0)
- **Edge definition:** One edge = one output descended from one spend
- **Unspent definition:** `tx_out.id NOT IN (SELECT tx_out_id FROM tx_in)`

---

## Contact

For questions about methodology or reproducibility:
- Open issue at: https://github.com/BEACNpool/ABCDE/issues
- Include: block height, query, expected vs actual result

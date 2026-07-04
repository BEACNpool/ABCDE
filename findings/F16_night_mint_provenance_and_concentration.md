# F16 — NIGHT genesis mint: complete spend-flow provenance and supply concentration

## Claim

The entire supply of the **NIGHT** token
(policy `0691b2fecca1ac4f53cb6dfb00b7013e561d1f34403b957cbb5af1fa`, asset name
`NIGHT`) is traced from its single genesis mint to every current holder, and the
distribution is highly concentrated:

- **Single mint:** tx `ce75b0e1e203c66d5dbce3b37865114163f577a58d3d12b0ae2593f8d3a64eb2`
  on 2025-11-25, **24,000,000,000 NIGHT** into one script UTxO (`…#0`).
- **Complete, conserved graph:** the spend flow expands to fixpoint across
  **1,358,841 UTxO nodes, 717,947 transactions, ~2.55M edges, 3,349 levels
  deep**. The full 24,000,000,000 NIGHT is accounted for at **167,728 current
  (unspent) leaf UTxOs**, with **0 unreachable** — supply conservation holds
  exactly.
- **Concentration (current holdings across 117,671 addresses):**
  - **one address holds exactly 25.00%** (6,000,000,001 NIGHT) in a **single UTxO**;
  - top 10 addresses hold **65.27%**; top 50 hold **83.43%**; top 100 hold
    **86.04%**; top 1,000 hold **92.79%**.
- **Custody type:** 51.78% of NIGHT sits at enterprise (non-staked) addresses,
  48.22% at script addresses.

## Grade

- **FACT:** the mint, the root UTxO, the complete spend-flow graph and its node/
  edge/level counts, the exact supply conservation (leaves sum to the mint,
  zero unreachable), every concentration figure, and the custody-type split —
  all directly queryable from the committed `night_*` tables and reproducible
  from the extraction SQL against db-sync.
- **STRONG_INFERENCE:** the shape (a few very large holders plus a long thin
  tail) reflects an airdrop/distribution structure plus early exchange/DEX
  market formation. Most of the largest holders are **script** addresses,
  consistent with distribution contracts, custody, bridges, or liquidity pools.
- **WORKING_HYPOTHESIS:** what any specific top address *is*. The 25%
  single-UTxO holder is an **unidentified script address**; it is most likely a
  programmatic distribution/treasury/custody contract, but that is not proven
  here.
- **UNKNOWN:** real-world ownership, identity, or control of any address.

### The wording rule applied

This finding proves *where the NIGHT went on-chain* and *how concentrated it is*
— not who owns it. "An unidentified script address holds 25% in a single UTxO"
is FACT; naming that entity is not established. Script-vs-enterprise is a
custody-*type* signal from the address structure, not an identity.

### Counterexamples / cautions

- **Script ≠ single owner.** A script address can be a shared contract (a DEX
  pool, a distribution escrow, a bridge) holding many parties' value. High
  script concentration is therefore not automatically "one whale."
- **Leaves are a snapshot.** Current holdings are as of the export tip; the
  graph structure and mint are historical facts that do not decay, but the
  concentration numbers move as tokens trade.
- **Enterprise addresses** (no stake credential) here are the majority of value
  — common for exchange deposit/custody and for holders who never delegated a
  non-ADA token; it is not itself evidence of anything beyond address structure.

### Snapshot-boundary notes

Current-holding figures are as of the NIGHT export tip (current leaves span
2025-12 → 2026-04). Mint, root, graph topology, and conservation are historical
facts. `night_summary` carries the export's own metrics.

## Evidence

- `data/small/night_summary.csv` (mint total, node/edge counts, conservation, max depth)
- `data/small/night_mint_event.csv`, `data/small/night_root_utxo.csv`
- `data/small/night_holder_top.csv` (top 2,000 holding addresses)
- `data/small/night_concentration_curve.csv` (cumulative % by top-N)
- `data/small/night_holder_type_split.csv` (script vs enterprise)
- `data/small/night_flow_level_dist.csv`, `data/small/night_leaves_by_month.csv`
- `data/small/night_current_leaves_top.csv` (top 10,000 current-leaf UTxOs)
- extraction: `sql/40_night/night_full_spend_flow_export.remote.sql`
- rollups: `scripts/build_night_rollups.py`
- **full graph** (1.36M nodes / 2.55M edges, ~2 GB) is a **release-tier**
  artifact — see `docs/25_NIGHT_TOKEN_PROVENANCE.md`.

## Reproduce

From a clone (DuckDB):

```sql
-- supply conservation
SELECT metric, value FROM night_summary
WHERE metric IN ('net_minted_night','reachable_current_leaf_qty_night','unreachable_current_leaf_qty_night');

-- concentration curve
SELECT top_n, cumulative_pct FROM night_concentration_curve ORDER BY top_n;

-- the 25% single-UTxO holder
SELECT address, has_script, qty_night, utxos, pct_of_supply
FROM night_holder_top ORDER BY qty_night DESC LIMIT 5;
```

Maintainers (warehouse) rebuild the full graph + compact cut:

```bash
# 1. run sql/40_night/night_full_spend_flow_export.remote.sql against db-sync,
#    export the result CSVs into data/release/night_full/
# 2. NIGHT_SRC=data/release/night_full python scripts/build_night_rollups.py
```

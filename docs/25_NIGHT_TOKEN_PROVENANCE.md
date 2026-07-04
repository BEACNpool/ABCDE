# NIGHT token provenance (companion module)

Added 2026-07-04. ABCDE's core mission is genesis **ADA**; this is the first
companion module extending the same forensic-provenance method to another
foundational Cardano-ecosystem token distribution — **NIGHT** (the Midnight
token, policy `0691b2fecca1ac4f53cb6dfb00b7013e561d1f34403b957cbb5af1fa`).

It is deliberately scoped and clearly separated from the genesis-ADA tables so
the core focus stays sharp. See finding
[`F16`](../findings/F16_night_mint_provenance_and_concentration.md).

## What was traced

The **complete spend-flow graph** of the entire NIGHT supply, from its single
24,000,000,000-NIGHT genesis mint (2025-11-25) to every current holder:
1,358,841 UTxO nodes, 717,947 transactions, ~2.55M edges, 3,349 levels deep.
Supply conserves exactly — 24B minted → 24B at 167,728 current leaf UTxOs →
**0 unreachable**.

## Two tiers (same model as the genesis data — see `22_DATA_TOPOLOGY_AND_FRESHNESS.md`)

**1. Compact, committed `night_*` tables** (clone-and-ask, a few MB):

| table | what it answers |
|---|---|
| `night_summary` | mint total, node/edge counts, conservation, max flow depth |
| `night_mint_event`, `night_root_utxo` | the single mint tx and root UTxO (provenance anchor) |
| `night_holder_top` | top 2,000 current holding addresses + % of supply |
| `night_concentration_curve` | cumulative % held by the top-N addresses |
| `night_holder_type_split` | script vs enterprise (custody type) |
| `night_flow_level_dist` | how deep in the spend graph current holdings sit |
| `night_leaves_by_month` | when current holdings last landed |
| `night_current_leaves_top` | the top 10,000 current-leaf UTxOs (queryable holder cut) |

**2. Release-tier full graph** (~2 GB, not committed): the complete node and
edge lists —
`3{5..43}_night_*_abcde.csv` (mint, root, reachable UTxO/tx nodes, UTxO→tx and
tx→UTxO edges, current leaves, summary). This is the reproducible full artifact.
Place the unzipped export in `data/release/night_full/` (gitignored) to rebuild
the compact cut, or publish it as a GitHub Release asset for public download.

## Reproducing

Full graph is a single deterministic warehouse extraction:

```bash
# maintainer, against db-sync:
psql ... -f sql/40_night/night_full_spend_flow_export.remote.sql   # -> CSVs
# then distill the compact cut:
NIGHT_SRC=data/release/night_full python scripts/build_night_rollups.py
python scripts/build_genesis_db.py   # loads night_* into the compact DuckDB
```

`build_night_rollups.py` **fails loudly if supply does not conserve** (current
leaves must sum to the 24,000,000,000 mint), so a broken or partial export can't
silently produce wrong concentration numbers.

## Grading

The graph, conservation, and every concentration figure are **FACT**. What any
specific top address *is* stays **WORKING_HYPOTHESIS** — script addresses are a
custody-*type* signal (contract / DEX / bridge / custody), never a real-world
identity. The hard wording rule applies exactly as for genesis ADA: on-chain
linkage is not ownership.

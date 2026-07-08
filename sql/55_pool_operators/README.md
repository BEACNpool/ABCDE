# 55_pool_operators — operator fingerprinting by KES-rotation timing

Who *operates* Cardano's stake, as distinct from how many pools appear to exist.
Every block header carries the minting pool's operational certificate, so KES-key
**rotation timing** is a public, unfakeable operational fingerprint. Pools that
rotate in lockstep — cycle after cycle, for years — are run by the same hands or
the same automation, whatever their branding says.

See the graded write-up: [`findings/F10_kes_corotation_pool_operators.md`](../../findings/F10_kes_corotation_pool_operators.md).

## Evidence grade (read first)

Synchronized rotation is **FACT** and indicates shared **operational control**
(one admin / automation / managed host). It is **NOT** proof of shared ownership:
white-label infra providers (Kiln, Figment) run pools for many clients and appear
here identically to a concealed multi-pool operator. Per the repo wording rule,
on-chain co-behaviour is on-chain linkage, never real-world identity or control.
Rarely-minting pools have wide timing windows and are missed — every count is a
floor, not a ceiling.

## Reproduce

```bash
# 1. build rotation events + corroboration tables on the warehouse
psql -d cexplorer_replica -f build_kes_corotation.sql

# 2. export the clustering inputs
psql -d cexplorer_replica -c "\copy (select pool_hash_id,first_seen,gap from poolsync.tight order by first_seen) to 'tight.csv' csv header"
psql -d cexplorer_replica -c "\copy (select * from poolsync.pool_info) to 'pool_info.csv' csv header"

# 3. score pairs (empirical-null Poisson test) + connected components
python ../../scripts/kes_corotation_cluster.py --indir . --out cluster.csv

# 4. load membership + build the enrichment/alert view
psql -d cexplorer_replica -c "create table poolsync.cluster(cluster_id int, pool_hash_id bigint primary key)"
psql -d cexplorer_replica -c "\copy poolsync.cluster from 'cluster.csv' csv header"
psql -d cexplorer_replica -f build_kes_corotation_summary.sql
```

## Tables (schema `poolsync`, warehouse-local)

| table / view | what |
|---|---|
| `rotation` | every op-cert change in a block header, per pool, with timing gap |
| `tight` | rotation events with <=48h uncertainty — the clustering input |
| `pool_info` | ticker / name / current-epoch stake / delegators per pool |
| `same_tx`, `shared_reward`, `shared_owner`, `shared_relay` | on-chain corroboration, independent of timing |
| `cluster` | membership (cluster_id, pool_hash_id) — loaded from the Python step |
| `cluster_summary` | per-cluster stake, 30-epoch block share, DRep overlay, active window |
| `cluster_time` | first/last synchronized rotation per cluster |
| `entity` | cluster-or-self mapping, for Nakamoto-coefficient math |
| `cluster_alert` (view) | stable member-set fingerprint + on-chain-links flag; read by BEACN Monitor |

## Data receipts

`data/` holds the committed snapshot cut (dated). `cluster_membership_*.csv` is the
full 480-pool→cluster map; `cluster_summary_*.csv` the per-cluster rollup. Both are
a snapshot at the recorded tip — treat current-state claims as of that date.

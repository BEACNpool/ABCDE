# Cross-Entity Merge Inventory Milestone

This is the next major v2 target after the seed-cut proof.

## Legacy regression baseline

The preserved v1 direct cross-seed consuming transaction inventory is summarized in:

- `data/manifests/legacy-cross-merge-baseline.json`
- `data/small/legacy_cross_merge_baseline_counts.csv`

Baseline counts from v1:

| metric | count |
| --- | ---: |
| total direct cross-seed consuming txs | 521 |
| clean total | 308 |
| EMURGO+IOG | 216 |
| CF+IOG | 49 |
| CF+EMURGO | 253 |
| CF+EMURGO+IOG | 3 |
| clean EMURGO+IOG | 205 |
| clean CF+IOG | 48 |
| clean CF+EMURGO | 54 |
| clean CF+EMURGO+IOG | 1 |

Known exemplar txs the v2 rebuild must reproduce:

- `a71578ec01f6cf39dbcf31351631159e3dd6fb99dd475783effbc65b90b8f0f9` — earliest clean IOG+EMURGO
- `f9951db326893e5c6cd94407e3d75be4928442aaf5809e435ca3e82c1983949d` — earliest clean IOG+CF
- `11c0765f430ecfffbdd1fb400d34bcd61d13af4c2e9332ce215f33de7e48d394` — earliest clean EMURGO+CF
- `197f9d27e49345cc085c9a2951d96c77f57f1cd82a71c095b7b7a3b36e74855d` — three-way inherited
- `34147ef46fd105ed39e3be63ac194e79622fb1bf9ea6e50313a0c3e0e6fd20c3` — three-way inherited
- `571f776c0698c576ddecae145f97e7f284b82ebea70fbc924fa4e2a4a6258020` — clean three-way bridge

## V2 implementation contract

The v2 inventory should be generated from trace membership, not copied from the legacy CSV.

Target tables/artifacts:

1. `trace_edges` / published trace membership table
   - `(run_id, root_seed_id, tx_hash, tx_out_index, value_lovelace, depth, address, stake_address, block metadata)`
2. `cross_entity_merge_inputs`
   - one row per traced input consumed by a cross-seed transaction
   - includes seed membership count for the input
3. `cross_entity_merges`
   - one row per consuming tx + seed combo
   - includes per-seed input counts, overlap counts, clean/inherited classification, tx input/output counts, value totals
4. `cross_entity_merge_outputs`
   - one row per output of each merge tx

## Clean vs inherited rule

A merge is **clean** when every seed in the combo has at least one consumed input whose seed membership count is exactly `1`.

A merge is **inherited** when cross-seed presence is caused by an input already tagged with multiple seeds.

## Performance rules

- Do not use one unbounded recursive CTE for the full trace.
- Batch by seed and frontier depth.
- Deduplicate to min depth per `(run_id, root_seed_id, tx_hash, tx_out_index)`.
- Avoid path arrays in the hot extraction table; keep path receipts separate.
- Use correct db-sync join:
  `tx_in.tx_out_id = producing_tx.id AND tx_in.tx_out_index = produced_output.index`.

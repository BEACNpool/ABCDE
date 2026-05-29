# F08 — IOG Current Bag Audit Cut

## Claim

A depth-14 staged trace from the IOG genesis root currently resolves to approximately **506.9M ADA** in unspent IOG-descended UTxOs at ABCDE/db-sync tip time.

This is an **audit cut**, not a proof of current legal ownership by IOG, IOHK, or Charles Hoskinson.

## Audit labels

- **Finding status:** REVIEW_CUT
- **Claim grade:** FACT for depth-14 staged trace membership and live unspent status; UNKNOWN for beneficial ownership
- **Artifact class:** AUDIT_REVIEW_CUT

## Receipts

- `data/small/iog_current_bag_depth14_summary.csv`
- `data/small/iog_current_bag_depth14_by_depth.csv`
- `data/small/iog_current_bag_depth14_top_stake.csv`
- `data/small/iog_pool_state_validation.csv`
- generator: `scripts/build_iog_current_bag_audit_remote.sh`

## Current depth-14 result

From `abcde_forensics_stage_founders_depth14.trace_utxos`, filtered to `root_seed_id='iog'` and live-unspent by db-sync `tx_in` anti-join:

- current unspent rows: **75,989**
- current ADA: **506,900,169.148536**
- depth range: **4–14**
- distinct Shelley stake addresses: **48,581**
- Shelley/stake-address ADA: **499,318,774.765035**
- Byron/no-stake ADA: **7,581,394.383501**

## Pool-state correction

Do **not** use trace-derived latest-delegation rollups as live pool-stake facts.

Direct pool-state validation shows:

- `IOG1` is active with latest epoch active stake around **10.03M ADA**.
- `IOG2` retired at epoch **237** and has no latest-epoch active stake row.

Therefore the earlier shortcut claim that IOG1/IOG2 implied ~1.8B current active stake is rejected.

## Interpretation

The clean current audit statement is:

> At depth 14, the staged IOG genesis trace resolves to about **506.9M ADA** in currently unspent descendant UTxOs. This supports a “large surviving IOG-descended bag” claim at the trace-membership level, but does not prove current beneficial ownership.

## Open audit work

- Classify the top current stake clusters as direct retained, exchange/custodian, shared infrastructure, or unknown.
- Extend or selectively deepen trace paths where high-value depth-14 outputs are themselves later spent in future snapshots.
- Produce confidence bands only after classification, not from pool-delegation shortcuts.

## Confidence bands

| band | ADA | confidence | interpretation |
| --- | ---: | --- | --- |
| live IOG pool stake sanity check | 10,027,028.166516 | HIGH for pool state only | IOG1 live active stake; IOG2 retired; not an IOG bag estimate |
| high-confidence coordinated retained-like core | 247,261,951.770785 | MEDIUM-HIGH | IOG-descended current UTxOs in synchronized `drep_always_abstain` / epoch-329 pool-delegation cluster, restricted to clusters >=100k ADA |
| probable retained-like abstain surface | 278,747,238.425299 | MEDIUM | Coordinated core plus other IOG-descended current UTxOs whose latest DRep is always-abstain |
| trace-membership current upper bound | 506,900,169.148536 | MEDIUM-HIGH for trace/unspent; LOW for beneficial ownership | All depth-14 IOG-descended live-unspent UTxOs before custodian/unknown classification |
| known service/custodian-like subset | 13,610,854.635725 | MEDIUM | Delegated to recognizable service/custodian pools; should not be counted as retained without more evidence |
| unclassified/no-latest-pool subset | 214,346,954.711814 | UNKNOWN | Requires classification before retained-bag use |

## Current best estimate

For public audit language, the clean estimate is:

> IOG-descended current live-unspent ADA is **506.9M ADA** at depth 14. The strongest retained-like core is **~247.3M ADA**, with a broader probable retained-like abstain surface of **~278.7M ADA**. Anything above that remains unclassified until custodian/exchange/shared-infrastructure filtering is complete.

This supports “not depleted” with high confidence at the trace-membership level and medium confidence at the retained-like-cluster level.

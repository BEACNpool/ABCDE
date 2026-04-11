# Cross-Entity Merge Validation
## Live db-sync confirmation of exemplar merge transactions

**Validation date:** 2026-04-06  
**Database:** `cexplorer_replica` on `${DB_HOST}`  
**Role used:** `codex_audit` (read-only)  
**Companion SQL:** `queries/cross_entity_merge_validation.sql`

---

## What was validated

The local founder-trace CSVs already showed exact downstream output convergence across the three founder allocations. This supplemental pass validates three exemplar transactions directly against a live Cardano db-sync replica:

1. `197f9d27e49345cc085c9a2951d96c77f57f1cd82a71c095b7b7a3b36e74855d`
2. `34147ef46fd105ed39e3be63ac194e79622fb1bf9ea6e50313a0c3e0e6fd20c3`
3. `571f776c0698c576ddecae145f97e7f284b82ebea70fbc924fa4e2a4a6258020`

These were selected because their output IDs are among the exact `dest_tx_out_id`s shared by multiple founder-trace exports, including the full three-way overlap set.

---

## Live-db results

| Tx hash | Epoch | UTC time | Inputs | Output IDs |
| --- | ---: | --- | ---: | --- |
| `197f9d27...e74855d` | 196 | 2020-06-02 09:58:31 | 15 | `5064341`, `5064342` |
| `34147ef4...fd20c3` | 239 | 2021-01-01 10:17:58 | 58 | `7835688`, `7835689` |
| `571f776c...258020` | 250 | 2021-02-25 12:58:28 | 384 | `10748946`, `10748947`, `10748948` |

### Output values confirmed in db-sync

- `197f9d27...e74855d` created:
  - `5064341` = `157,848,089` lovelace
  - `5064342` = `10,000,000,000` lovelace
- `34147ef4...fd20c3` created:
  - `7835688` = `50,000,000,000,000` lovelace
  - `7835689` = `8,356,376,525,206` lovelace
- `571f776c...258020` created:
  - `10748946` = `50,000,000,000,000` lovelace
  - `10748947` = `40,000,000` lovelace
  - `10748948` = `244,596,263,181` lovelace

---

## Trace-to-db match

The live db-sync queries confirm that the focal source UTxOs implicated by the local founder-trace exports are real direct inputs to the same consuming transactions.

### Transaction `197f9d27...e74855d`

- Live db-sync confirms input `5034850` was consumed by `197f9d27...e74855d`.
- Local traces show `5034850` feeding this transaction in the IOG trace export.
- Live db-sync confirms input `5035023` was consumed by the same transaction.
- Local traces show `5035023` feeding this transaction in both the EMURGO and CF trace exports.
- Result: the earliest currently confirmed three-way shared-output exemplar, at epoch 196, consumes at least one direct IOG-traced input and one direct EMURGO/CF-traced input, then emits outputs `5064341` and `5064342` that appear in all three published downstream sets.

### Transaction `34147ef4...fd20c3`

- Live db-sync confirms input `6273746` was consumed by `34147ef4...fd20c3`.
- Local traces show `6273746` feeding this transaction in the EMURGO trace export.
- Live db-sync confirms input `6337983` was consumed by the same transaction.
- Local traces show `6337983` feeding this transaction in both the IOG and CF trace exports.
- Live db-sync confirms input `6742421` was consumed by the same transaction.
- Local traces show `6742421` feeding this transaction in the CF trace export.
- Result: by epoch 239, the shared-output pattern is reproduced at much larger scale in a 58-input transaction that emits `7835688` and `7835689`, both present in the three-way overlap set.

### Transaction `571f776c...258020`

- Live db-sync confirms input `8064253` was consumed by `571f776c...258020`.
- Local traces show `8064253` feeding this transaction in the EMURGO trace export.
- Live db-sync confirms inputs `8926255` and `9036401` were consumed by the same transaction.
- Local traces show both inputs feeding this transaction in the IOG trace export.
- Live db-sync confirms input `10748217` was consumed by the same transaction.
- Local traces show `10748217` feeding this transaction in the CF trace export.
- Result: this is the cleanest exemplar in the current set. A single transaction at epoch 250 directly consumes focal source UTxOs from all three founder-trace branches and emits outputs `10748946`, `10748947`, and `10748948`, all of which appear in the three-way overlap set.

---

## Interpretation

- This moves the case beyond simple "same downstream addresses show up later." The live replica confirms concrete consuming transactions where source UTxOs tied to different founder traces feed the same transaction.
- The strongest of the three validated exemplars is `571f776c...258020`, because the local trace exports place direct inputs from IOG, EMURGO, and CF into the same consuming transaction.
- This is still evidence of shared transaction flow, not by itself legal proof of common beneficial ownership or intent. Exchange, custody, treasury operations, or shared service providers remain live alternative explanations unless the merge points are traced further upstream and operationally classified.

---

## Recommended next steps

1. Build a full "cross-seed consuming transaction" table by scanning every traced `source_tx_out_id` and grouping by `tx_in.tx_in_id`, then flagging transactions that consume inputs from more than one founder seed.
2. Separate pairwise from three-way merges and rank them by earliest block time. The current exemplar set is strong, but the next report should state the earliest pairwise merge and earliest direct three-way merge explicitly.
3. Classify each merge point as likely founder-controlled, exchange, custodian, or common service infrastructure by combining address reuse, transaction shape, pool behavior, and known public labels.
4. Re-run the delegation overlap section with a strict genesis-trace filter so the report can distinguish chain-wide pool overlap from founder-traced overlap without ambiguity.
5. Export an evidence bundle for each highlighted merge transaction:
   - db-sync input/output query results
   - matching founder-trace CSV rows
   - Cardanoscan or Koios verification links

---

## Evidence paths

- `datasets/genesis-founders/iog/iog_trace_edges_part1.csv`
- `datasets/genesis-founders/emurgo/emurgo_trace_edges_part2.csv`
- `datasets/genesis-founders/cf/cf_trace_edges_part2.csv`
- `queries/cross_entity_merge_validation.sql`

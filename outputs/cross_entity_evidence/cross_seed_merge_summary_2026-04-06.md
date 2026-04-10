# Cross-Seed Merge Summary
## Full direct consuming-transaction scan across the founder trace exports

**Analysis date:** 2026-04-06  
**Primary dataset:** `outputs/cross_entity_evidence/cross_seed_consuming_transactions_2026-04-06.csv`  
**Machine-generated summary:** `outputs/cross_entity_evidence/cross_seed_consuming_transactions_summary_2026-04-06.json`  
**Live-db validation references:** `outputs/cross_entity_evidence/first_merge_validation_2026-04-06.md`

---

## Scope

This pass groups the six published founder trace-edge exports by `dest_tx_hash` and asks a narrower question than the earlier overlap work:

- Which transactions directly consume source UTxOs traced from more than one founder allocation?
- Of those, which are "clean" merges where each represented founder seed contributes at least one exclusive source input, rather than merely inheriting a source UTxO that was already mixed earlier?

This matters because later downstream overlap can be caused by prior convergence. The strongest merge evidence is a consuming transaction where the founder lineages are simultaneously present as distinct direct inputs.

---

## Headline results

- Total direct cross-seed consuming transactions in the published trace exports: `521`
- Direct IOG+EMURGO consuming transactions: `216`
- Direct IOG+CF consuming transactions: `49`
- Direct EMURGO+CF consuming transactions: `253`
- Direct three-way IOG+EMURGO+CF consuming transactions: `3`

### Clean-merge subset

- Clean IOG+EMURGO merges: `205` of `216`
- Clean IOG+CF merges: `48` of `49`
- Clean EMURGO+CF merges: `54` of `253`
- Clean three-way merges: `1` of `3`

The EMURGO+CF branch is the noisiest by far. Most of its direct consuming transactions are not clean new pairwise merges; they are later transactions that already contain source UTxOs seen in both trace branches. That pattern is consistent with an earlier EMURGO+CF convergence propagating forward.

---

## Earliest clean pairwise merges

### IOG + EMURGO

- Earliest clean direct merge: `a71578ec01f6cf39dbcf31351631159e3dd6fb99dd475783effbc65b90b8f0f9`
- Epoch: `95`
- Time: `2019-01-15 21:50:51+00`
- Unique direct source inputs: `3`
- Input split: `2` IOG-exclusive, `1` EMURGO-exclusive
- Dest outputs: `2048665`, `2048666`
- Live-db validated source inputs:
  - IOG: `2042611`, `2042772`
  - EMURGO: `2040117`

Live db-sync confirms this transaction consumed distinct direct source UTxOs from the IOG and EMURGO trace branches with no overlap. One resulting output, `2048666`, pays the Byron address `DdzFFzCqrhstmqBkaU98vdHu6PdqjqotmgudToWYEeRmQKDrn4cAgGv9EZKtu1DevLrMA1pdVazufUCK4zhFkUcQZ5Gm88mVHnrwmXvT`, the same high-volume hub that appears elsewhere in the investigation.

### IOG + CF

- Earliest clean direct merge: `f9951db326893e5c6cd94407e3d75be4928442aaf5809e435ca3e82c1983949d`
- Epoch: `193`
- Time: `2020-05-18 02:50:31+00`
- Unique direct source inputs: `2`
- Input split: `1` IOG-exclusive, `1` CF-exclusive
- Dest outputs: `4857107`, `4857108`
- Live-db validated source inputs:
  - IOG: `4855509`
  - CF: `4856552`

This is a clean two-input founder-lineage merge. Output `4857107` again pays the same high-volume Byron hub `DdzFFzCqrhstmqBka...nrwmXvT`.

### EMURGO + CF

- Earliest clean direct merge: `11c0765f430ecfffbdd1fb400d34bcd61d13af4c2e9332ce215f33de7e48d394`
- Epoch: `195`
- Time: `2020-05-27 20:09:51+00`
- Unique direct source inputs: `4`
- Input split: `1` EMURGO-exclusive, `3` CF-exclusive
- Dest outputs: `4966317`, `4966318`
- Live-db validated source inputs:
  - EMURGO: `4677119`
  - CF: `4835275`, `4844092`, `4846322`

This is the earliest clean EMURGO+CF direct merge and it does not rely on any already-overlapping source input IDs.

---

## Three-way direct merges

Only `3` direct consuming transactions in the current published trace exports contain all three founder lineages:

1. `197f9d27e49345cc085c9a2951d96c77f57f1cd82a71c095b7b7a3b36e74855d`
2. `34147ef46fd105ed39e3be63ac194e79622fb1bf9ea6e50313a0c3e0e6fd20c3`
3. `571f776c0698c576ddecae145f97e7f284b82ebea70fbc924fa4e2a4a6258020`

### Earliest three-way lineage merge

- Tx: `197f9d27...`
- Epoch: `196`
- Unique direct source inputs: `2`
- Input structure:
  - `1` IOG-exclusive source input
  - `1` source input that appears in both EMURGO and CF trace branches
- Pair overlap:
  - EMURGO+CF overlap count: `1`

This is the earliest direct transaction where all three founder lineages are present, but it is not the cleanest three-way example because the EMURGO and CF lineages are already co-mingled in one source UTxO before entering the transaction.

### Intermediate three-way merge

- Tx: `34147ef4...`
- Epoch: `239`
- Unique direct source inputs: `3`
- Input structure:
  - `1` EMURGO-exclusive
  - `1` CF-exclusive
  - `1` source input that appears in both IOG and CF traces

This transaction strengthens the three-way case but still contains one already-overlapping source input across two branches.

### Earliest clean three-way merge

- Tx: `571f776c...`
- Epoch: `250`
- Time: `2021-02-25 12:58:28+00`
- Unique direct source inputs: `4`
- Input split:
  - `2` IOG-exclusive
  - `1` EMURGO-exclusive
  - `1` CF-exclusive
- Pair overlaps: `0` across all three pairs
- Dest outputs: `10748946`, `10748947`, `10748948`

This is the strongest direct three-way merge currently identified in the published trace set. Live db-sync confirms that the transaction directly consumes focal source UTxOs from all three founder branches with no overlapping source IDs across pairs.

---

## Interpretation

- The founder traces do not just converge downstream in some abstract sense. There are at least `521` direct consuming transactions in which more than one founder lineage is present at input time.
- The earliest clean direct pairwise merge is IOG+EMURGO at epoch `95` on `2019-01-15 21:50:51+00`. That predates the earliest clean CF-involving merges by more than a year.
- The clean three-way story is much narrower than the raw overlap story. There are only `3` direct three-way transactions in the current published traces, and only `1` of them is clean in the strict sense.
- The repeated appearance of the Byron hub `DdzFFzCqrhstmqBka...nrwmXvT` in validated early pairwise merges strengthens the alternative explanation that at least some of this convergence could reflect common exchange, custody, or treasury-routing infrastructure rather than a simple one-wallet insider story.
- At the same time, the clean three-way epoch-250 merge remains a serious finding. It shows distinct direct source inputs from all three founder branches entering the same transaction.

---

## Recommended next steps

1. Backtrace the earliest clean pairwise merges to the last pre-merge transaction for every direct input so the report can show exactly where each branch remained separate immediately before convergence.
2. Build a hub-classification appendix for the recurring Byron infrastructure, starting with `DdzFFzCqrhstmqBka...nrwmXvT` and the `Ae2tdPwUPEZHiXix...` cluster.
3. Produce a visual timeline of merge onsets:
   - earliest IOG+EMURGO clean merge
   - earliest IOG+CF clean merge
   - earliest EMURGO+CF clean merge
   - earliest three-way lineage merge
   - earliest clean three-way merge
4. Re-run the founder-delegation claims with the same clean-vs-overlapping discipline used here so the report does not mix direct founder-trace evidence with chain-wide behavioral overlap.
5. Extend the query pack so any suspect transaction can be classified automatically as:
   - pairwise clean
   - pairwise inherited-overlap
   - three-way clean
   - three-way inherited-overlap

---

## Output files

- `outputs/cross_entity_evidence/cross_seed_consuming_transactions_2026-04-06.csv`
- `outputs/cross_entity_evidence/cross_seed_consuming_transactions_summary_2026-04-06.json`
- `outputs/cross_entity_evidence/first_merge_validation_2026-04-06.md`
- `queries/cross_entity_merge_validation.sql`

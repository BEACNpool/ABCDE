# ₳318M MIR WavePool Cluster Exit Trace

This folder contains the working evidence set and trace outputs for the epoch 298 MIR distribution of `318,199,980 ADA` from Cardano protocol reserves into a 6-stake recipient cluster later associated with WavePool-operated infrastructure.

## Core findings

- MIR tx `03b02cff29a5f2dfc827e00345eaab8b29a3d740e9878aa6e5dd2b52da0763c5` distributed `318,199,980 ADA` from reserve in epoch `298`.
- Raw witness decoding confirmed signatures from the full Shelley genesis delegate set, `7/7`, plus one additional fee-paying escrow payment key.
- All 6 MIR recipient stake credentials delegate to WavePool pools (`meta.wavepool.digital`).
- WavePool is operated by Wave Financial LLC, which manages cFund, where IOG is the controlling interest-holder.
- Two of the MIR cluster stakes resolve to the WavePool DRep committee (`drep1r497...` in db-sync form, Koios canonical metadata resolving to Wavepool DRep Co).
- The withdrawal pattern looks like managed drip behavior, not a simple one-shot exchange cashout.
- Dominant observed exit behavior is circular return into the original MIR cluster.
- Non-circular exits either land in parked holdings or fragment through enterprise relay addresses below practical threshold tracing floors.
- Zero exchange/custody label hits were observed in the traced paths.
- The enterprise relay layer appears deliberately structured to defeat threshold-based tracing. That evasion pattern is itself a material finding.

## Methodological corrections

### CF0 retraction

An earlier investigation thread included a CF0-related attribution hit that did not survive receipt-based verification. It is retracted and intentionally excluded from the final findings set.

## Findings headline grading

- `TRUE`: MIR reserve distribution, full genesis-delegate witness set, WavePool pool alignment, WavePool DRep alignment on two stakes, managed-drip withdrawal behavior, dominant circular return behavior, enterprise fragmentation below standard tracing floors.
- `FALSE`: funds went to exchanges.
- Reason for `FALSE`: zero exchange or custody hits were observed through all traced depths.

## Folder layout

- `reports/` trace outputs, summaries, lane reports, witness report, and continuation work
- `sql/` boundary-exit SQL templates used in the investigation
- `scripts/` tracing helper used during iterative frontier analysis

## Recommended reading order

1. `reports/mir_03b02cff_witness_report.md`
2. `reports/mir_trace_49000ada_firstpass/report_49k_summary.md`
3. `reports/mir_trace_49000ada_secondpass_top5_by_lane/report.md`
4. `reports/mir_trace_depth3/report.md`

## Important methodological note

Later single-hop frontier tracing was intentionally tightened to require that the frontier's own spent UTxOs clear the active threshold before onward outputs were followed. That stricter rule is useful for honest warehouse-safe tracing, but it also means some earlier large-path observations from balance-level frontier attribution will not reproduce at the same threshold once the query is narrowed to actual spent UTxOs.

That is not necessarily a contradiction. It is part of the finding: the relay layer fragments onward movement aggressively enough that stricter frontier-UTxO tracing quickly loses visibility unless the threshold is lowered, at which point query cost rises sharply.

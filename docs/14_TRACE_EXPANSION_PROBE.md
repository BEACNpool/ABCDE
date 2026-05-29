# Trace Expansion Probe

A count-only recursive trace probe was run against ABCDE/db-sync to estimate safe bounded depths before exporting larger trace artifacts.

| max depth | total rows |
| ---: | ---: |
| 3 | 53 |
| 4 | 103 |
| 5 | 195 |
| 6 | 370 |
| 7 | 744 |
| 8 | 1,638 |
| 9 | 4,709 |
| 10 | 20,319 |
| 11 | 129,433 |
| 12 | 1,044,672 |

## Decision

Depth 10 is a reasonable next committed/portable cut. Depth 11+ should be treated as a larger artifact or staged server-side table, not casually committed to git.

## Implication for cross-merge rebuild

The full 521-row legacy cross-merge inventory likely requires deeper/staged tracing, but v2 should scale in controlled cuts:

1. depth 3 proof artifact — already committed
2. depth 10 review artifact — next candidate
3. staged server-side trace table with min-depth dedupe
4. exported release artifact, not git, once row counts grow beyond small-review scale

## Depth-10 merge probe

A depth-10 count-only merge probe shows this cut is still not deep enough to reproduce the legacy founder-only 521-row inventory.

| scope | max depth | seed combo | merge txs |
| --- | ---: | --- | ---: |
| named founders only | 10 | emurgo+iog | 8 |
| including fourth entry | 10 | emurgo+fourth_entry_781m | 952 |
| including fourth entry | 10 | emurgo+fourth_entry_781m+iog | 8 |

Decision: do not commit the 19 MB depth-10 CSV as a normal source artifact. Use depth-10 as a scratch/probe cut; build full cross-merge inventory via staged server-side extraction with dedupe and exported release artifacts.

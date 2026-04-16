# Findings memo

## Executive summary

This investigation traced an epoch 298 MIR reserve distribution of `318,199,980 ADA` into a 6-stake cluster whose downstream governance and delegation posture is tightly aligned with WavePool infrastructure.

The strongest conclusions are:

1. the MIR itself was co-signed by the full Shelley genesis delegate set,
2. the recipient cluster is operationally tied to WavePool,
3. the observed withdrawal behavior is structured and managed rather than resembling immediate exchange liquidation,
4. the dominant large-value flow pattern is circular return back into the cluster,
5. non-circular exits move into parked holdings or enterprise relay layers that fragment below practical threshold-tracing floors,
6. no traced lane hit a known exchange or custody label,
7. the enterprise relay layer appears deliberately structured below standard tracing thresholds, which is itself evidence of concealment-oriented design.

## Confirmed facts

### MIR transaction and signers

- Transaction: `03b02cff29a5f2dfc827e00345eaab8b29a3d740e9878aa6e5dd2b52da0763c5`
- Epoch: `298`
- Reserve distributed: `318,199,980 ADA`
- Witness decode result: all `7/7` Shelley genesis delegate keys signed, plus one extra fee-paying escrow payment key.

This is a full-genesis-governance signature pattern, not a single-party signer event and not evidence that seven independent institutions separately approved the MIR.

### Canonical MIR recipient stake set

The canonical 6 MIR recipient stake credentials are:

- `stake1uy86sf5xrzcpg2ncddkzz6z2ca2m59qsnu4qxar08g9rvkgwkpjjv`
- `stake1uykws5pmwjxktdhlkz0pac3cu2guw6fjys2zaanmdew6xrs5lgv4n`
- `stake1u80y77jjfcdymt38amg3na9w4p4d89ffw66xqsspdwsa2sqt8epdn`
- `stake1u8kgcfdpefrnf5570v47manyyg85jshlrg4p2hrsx3wdspccdda8v`
- `stake1u9mymn640v59n3mwyfdsg5t6yu34ut9ufvynavsn0ey40ugqdj6lh`
- `stake1u887jrylddch0vh4d2kx72h2ax8t7aeq49zvmry4g9wcj4g3gty8j`

These are the values that should be treated as canonical for this case.

### Recipient cluster alignment

All 6 MIR recipient stakes were observed delegating to WavePool-operated pools with metadata domain `meta.wavepool.digital`.

Two of the stakes also resolve to the same DRep family:
- db-sync DRep form: `drep1r497ue4s2pk737mmvy3erg49jlql3lzc9farq5hqevhfcrwmexm`
- resolved identity: `Wavepool DRep Committee`
- metadata URL: `https://meta.wavepool.digital/Wavepool%20DRep%20Co.jsonld`
- status: `registered`
- active: `false`
- expires epoch: `580`

### Entity attribution chain with source type

- MIR reserve distribution -> canonical MIR tx `03b02cff...` -> **on-chain / db-sync / witness decode**
- MIR recipient stakes -> WavePool pools (`meta.wavepool.digital`) -> **on-chain pool delegation + pool metadata domain**
- WavePool operations -> Wave Financial LLC -> **public record / public corporate and project materials**
- Wave Financial LLC -> cFund management role -> **public record / public project materials**
- cFund controlling interest-holder -> IOG -> **public record / public cFund disclosures**
- DRep `drep1r497...` -> Wavepool DRep Committee -> **Koios metadata resolution + public metadata URL**

This chain combines on-chain facts and public-record attribution. Those source types should not be blurred together.

### Withdrawal behavior

The cluster's wallets now hold dust balances, while aggregate withdrawals total roughly `344.85M ADA` across `469` withdrawal events including principal and rewards.

This pattern is far more consistent with managed drip behavior than with a one-shot exchange unload.

## Trace findings

### Large boundary exits at 49k ADA threshold

At depth 1, the trace found:
- `212` exits total
- about `101.9M ADA` to fresh stake credentials
- about `126.7M ADA` to enterprise addresses
- `0` exchange/custody label hits

### Depth-2 behavior

The strongest pattern at depth 2 is recirculation.

Examples:
- `stake1uxaertz...` routed `68.4M ADA` back to original MIR stake `stake1uy86sf5x...`
- `stake1u80fnwl4...` routed `50.6M ADA` back to original MIR stake `stake1uykws5p...`
- `addr1v98p...` routed `12.9M ADA` back to `stake1u887jry...`
- `addr1wxxaleu8...` routed `36.6M ADA` back to `stake1u8kgcfd...`

This is not a straightforward outward unwind. The cluster reabsorbs a large share of its own large-lane exits.

### Non-circular behavior

Non-circular destinations do exist, but the pattern changes:
- some land in very large parked stake holdings,
- some move through unlabeled enterprise relay addresses,
- onward frontier tracing quickly collapses below threshold because the relay layer fragments value into smaller spent UTxOs.

That is not just an inconvenience of tooling. It is a substantive finding. The enterprise relay behavior appears structured specifically to degrade threshold-based forensic continuity, which is consistent with concealment-oriented design.

## Grading table

| Claim | Grade | Basis |
|---|---|---|
| MIR distributed `318,199,980 ADA` from reserve in epoch 298 | TRUE | On-chain MIR tx and db-sync receipts |
| Full Shelley genesis delegate set signed the MIR | TRUE | Witness decode, `7/7` genesis delegate matches plus one fee-paying escrow key |
| Recipient cluster delegates to WavePool pools | TRUE | On-chain delegation and pool metadata domain receipts |
| WavePool DRep committee governs two MIR stakes | TRUE | db-sync DRep state plus Koios metadata resolution |
| Withdrawal pattern is managed drip, not simple cashout | TRUE | wallet dust end-state plus `469` withdrawal events and lane behavior |
| Dominant large-value exit flow is circular back to cluster | TRUE | depth-2 lane receipts |
| Non-circular exits land in parked holdings or fragment through enterprise relays | TRUE | depth-2 and continuation diagnostics |
| Enterprise relay layer is structured below standard thresholds | TRUE | single-hop frontier diagnostics and spent-UTxO distribution checks |
| Funds went to exchanges | FALSE | zero exchange/custody hits through all traced depths |
| Exchange use remains merely unproven | MISLEADING | the stronger receipt-based statement is that no exchange hit was observed in the traced data |

## Negative findings that matter

- No exchange or custody label hits were found in the traced paths.
- The strongest lanes do not support a simple "funds left for centralized exchange liquidation" story.
- Tightened single-hop frontier tracing at high thresholds repeatedly showed that later relay UTxOs fall below the active cutoff.

## Interpretation

The evidence supports a governance-aligned, operationally managed reserve-distribution cluster tied to WavePool-associated infrastructure, with downstream movement characterized by controlled withdrawals, strong recirculation, and relay-layer fragmentation that reduces naive outward traceability.

The absence of exchange hits does not prove funds never reached off-chain custody somewhere later. It does mean that, within the traced horizons and available labels, the observable pattern is dominated by cluster reuse, parked holdings, and enterprise relays rather than obvious liquidation endpoints.

## Best supporting artifacts

- `reports/mir_03b02cff_witness_report.md`
- `reports/mir_318m_recipient_stakes.txt`
- `reports/mir_trace_49000ada_firstpass/report_49k_summary.md`
- `reports/mir_trace_49000ada_secondpass_top5_by_lane/report.md`
- `reports/mir_trace_depth3/report.md`

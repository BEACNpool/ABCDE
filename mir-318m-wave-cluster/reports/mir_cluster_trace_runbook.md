# MIR cluster trace runbook

Goal: keep tracing large exits from the 6 MIR recipient stake credentials even if funds were split, re-staked under fresh credentials, or pushed through enterprise addresses.

## Seed set

Use `reports/mir_318m_recipient_stakes.txt` as the initial seed cluster.

## Tracing doctrine

1. **Do not trace by current wallet balance only.** Trace historical boundary exits.
2. **Treat fresh stake credentials as suspicious, not as a stop sign.** Follow them.
3. **Treat enterprise addresses as a concealment surface, not a dead end.** Follow them when they carry size.
4. **Start with size thresholds** so the graph stays useful.
   - primary filter: `>= 49,000 ADA`
   - secondary drill-down: `>= 10,000 ADA`
   - fine-grain pass only after the big lanes are mapped
5. **Classify exits into three buckets:**
   - fresh stake destination
   - enterprise destination
   - labeled exchange/custody destination
6. **Resolve current SPO + DRep** for every traced external stake credential.
7. **Assume adversarial intent.** Splits, merges, fresh stake creds, and enterprise hops are expected.
8. **Do not overclaim beneficial ownership** after heavy merging. Distinguish:
   - FACT: direct destination / current pool / current DRep / label hit
   - STRONG INFERENCE: coordinated cluster behavior
   - UNKNOWN: merged funds past clear provenance

## Built artifacts

- `ops/mir_cluster_trace.py`
  - first-pass reusable tracer
  - follows stake exits and enterprise exits by depth
  - overlays local labels from `Desktop/genesisADA/data/address_labels_full.csv`
  - resolves current pool + DRep for traced external stake credentials
- `reports/mir_318m_recipient_stakes.txt`
  - seed stake set for this MIR case

## Practical usage

### High-signal first pass

```bash
python3 ops/mir_cluster_trace.py \
  --stake-file reports/mir_318m_recipient_stakes.txt \
  --output-dir reports/mir_trace_49000ada_d2 \
  --min-ada 49000 \
  --depth 2
```

### Broader pass

```bash
python3 ops/mir_cluster_trace.py \
  --stake-file reports/mir_318m_recipient_stakes.txt \
  --output-dir reports/mir_trace_10000ada_d3 \
  --min-ada 10000 \
  --depth 3
```

### Stake-only pass

```bash
python3 ops/mir_cluster_trace.py \
  --stake-file reports/mir_318m_recipient_stakes.txt \
  --output-dir reports/mir_trace_stake_only \
  --min-ada 49000 \
  --depth 3 \
  --no-follow-enterprise
```

## What this should answer fast

- Did large value remain inside a coordinated stake cluster?
- Did it move to fresh stake credentials that are still delegated today?
- Which pools and DReps currently receive that traced stake weight?
- Do any high-value exits hit known CEX/custody labels?
- Which enterprise hops deserve a manual follow-on pass?

## Known limitation

This is a **boundary-exit tracer**, not a perfect reserve-to-final-owner proof system. Precision drops once large withdrawals merge with unrelated wallet activity. That is normal. The correct move is to preserve confidence tiers, not to pretend certainty.

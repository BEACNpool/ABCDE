# MIR cluster trace report

- input frontier: **`addr1wymztkhaekt7derv6ceu2xhkcw4zl92m68xyvmcpqlxy0kqggmn4s`**
- min tracked exit: **10,000 ADA**
- depth attempted: **1**
- exit rows captured: **0**
- unique exit stake addresses: **0**
- total tracked destination ADA (not de-overlapped): **0.000000**

## Assessment summary

- no rows met the threshold

## Top current pools

- none resolved

## Top current DReps

- none resolved

## Top labeled destinations

- none labeled yet

## Notes

- This is a stake-cluster / enterprise-address boundary tracer, not a mathematically perfect reserve-to-final-owner proof engine.
- It is designed to keep tracing large exits even when funds are split across fresh stake credentials or enterprise addresses.
- Exact attribution weakens when funds merge with unrelated inputs in later transactions, especially after withdrawals/rewards mix into the same wallet activity.
- Use the highest-confidence rows first: large exits, labeled CEX/custody destinations, and fresh stake exits with current pool/DRep state resolved.

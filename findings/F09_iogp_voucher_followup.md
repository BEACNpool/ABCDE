# F09 — IOGP Pledge and Voucher-Address Follow-up

## Claim

The IOGP-ticker pool declared a `1,000,000 ADA` pledge, while its reward
credential carried approximately `66.36M ADA` of active stake at epoch 250 and
`64.36M ADA` at epoch 255.

A separately cited voucher-program address:

- uses a stake credential that delegated to the IOG1-ticker pool;
- received `52,196,773.895086 ADA` on `2023-10-05 20:48:21 UTC` in a
  transaction whose inputs included the cited funding stake credential;
- sent `60,000,003.141590 ADA` to a previously identified forward endpoint in
  two transactions about an hour later;
- exchanged approximately `13.28M ADA` in each direction with the registered
  owner/reward credential of the WAV10-ticker pool; and
- has three selected funding transactions whose deterministic largest-input
  paths terminate at the `2,463,071,701 ADA` IOG genesis transaction.

The IOGP reward credential also sent `925,000,100 ADA` in 32 transactions to
the previously identified burst credential.

## Grade

- **FACT** for pool registration, pledge, epoch stake, delegation, transaction
  flows, and deterministic path existence.
- **STRONG_INFERENCE** that the voucher-address flows intersect the broader
  IOG-ticker/WAV/payer operational cluster.
- **UNKNOWN** for legal ownership, beneficial control, intent, or the external
  report's attribution of the address to any organization.

Dominant-input tracing follows one deterministic largest-input path. It is not
exclusive provenance, and hop counts can change when equal-valued inputs use a
different tie-break.

## Evidence

- `data/small/iogp_pool_registration.csv`
- `data/small/iogp_pool_epoch_stake.csv`
- `data/small/voucher_wallet_profile.csv`
- `data/small/voucher_wallet_delegations.csv`
- `data/small/voucher_wallet_counterparty_summary.csv`
- `data/small/iog_voucher_dominant_traces.csv`
- `data/small/iogp_reward_wallet_destinations.csv`
- `data/small/voucher_funder_delegations.csv`
- `data/small/voucher_funder_source_summary.csv`
- `reports/iogp_voucher_followup.md`
- `scripts/build_iogp_voucher_followup_remote.sh`
- `scripts/verify_iogp_voucher_followup.py`

All receipts record source tip block `13520244`, epoch `635`, and time
`2026-06-07 18:44:37 UTC`.

## Reproduce

From a clone:

```bash
python scripts/verify_iogp_voucher_followup.py
python scripts/query_duckdb.py claims/sql/iogp_voucher_followup.sql
```

Maintainers with warehouse access can rebuild the CSV receipts:

```bash
ABCDE_SSH=abcde scripts/build_iogp_voucher_followup_remote.sh
python scripts/build_genesis_db.py
python scripts/verify_iogp_voucher_followup.py
```

# F20 — EMURGO genesis ADA was removed from its DReps

## Claim

EMURGO's public 2025 statements that it removed Genesis ADA from its own DRep,
then parked ~35M ADA on seven named community DReps, then pulled that
delegation after epoch 576→577, are reproduced on Cardano mainnet.

As of warehouse tip **epoch 649 / block 13,808,619 / 2026-08-14 17:30:54 UTC**:

- Official EMURGO DRep `drep1m8mnpykcjfyax5mcs42whu3dt347u8aq43x45ucs6dv3ztw0lez`
  (GovTool `drep1ytvlwvyjmzfyn56n0zz4f6lj94wxhmsl5zky6knnzrf4jygpyahug`) still has
  **297,193,174.100085 ADA** of *voting power*. That is not its genesis bag.
- EMURGO-root leftover still delegated to that official DRep:
  **497.300000 ADA**, one stake, min-depth 14.
- Yoroi DRep `drep1qe2l8gw8v7ydswfp9twytxcc3wzwdq8npt55f3vnlgv2u8sx3nt`:
  **568,893,909.725040 ADA** voting power; **211,704.319893 ADA** EMURGO-root leftover
  (depths 12–14).
- The seven named community DReps lost **35,322,561.149334 ADA** of voting power
  between `drep_distr` epochs **577 and 578** (2025-08-17 → 2025-08-22), matching
  EMURGO's stated ~35M pull. Combined EMURGO-root leftover on those seven now:
  **9,298.077628 ADA**.
- Official EMURGO DRep voting power dropped **80,109,881.472102 ADA** between
  epochs **558 and 559** (2025-05-14 → 2025-05-19), the on-chain fingerprint of
  the May 23 “removed from our own DReps” post.
- Of the depth-14 EMURGO-root current bag still unspent today (**255,781,983.937857 ADA**),
  **252,201,152.484431 ADA (98.60%)** has **no DRep** (undeclared). Almost all of
  that undeclared pile is min-depth 14.

## DReps it moved from and to

Two hops. Names are EMURGO's published labels plus the on-chain `given_name`.
IDs are untruncated.

### Hop 1 — off their own DRep (May 2025)

**From** the official EMURGO DRep. Voting power dropped **80,109,881.472102 ADA**
at `drep_distr` epoch 558→559 (2025-05-14 → 2025-05-19).

| Published name | On-chain `given_name` | GovTool / CIP-105 | db-sync / CIP-129 |
|---|---|---|---|
| EMURGO | EMURGO | `drep1ytvlwvyjmzfyn56n0zz4f6lj94wxhmsl5zky6knnzrf4jygpyahug` | `drep1m8mnpykcjfyax5mcs42whu3dt347u8aq43x45ucs6dv3ztw0lez` |

They wrote “our own DReps” (plural). The other EMURGO-anchored DRep is **Yoroi
W₳llet** `drep1qe2l8gw8v7ydswfp9twytxcc3wzwdq8npt55f3vnlgv2u8sx3nt`. Its
`drep_distr` did **not** drop in that window; the measured 80.1M leave is the
official EMURGO DRep only.

**To** (June 2025, epoch 561→562, **+37,055,389.947138 ADA** across the seven):

| # | Published name (2 Jun 2025) | On-chain `given_name` | GovTool / CIP-105 | db-sync / CIP-129 |
|---|---|---|---|---|
| 1 | Waffle Capital (@Waffle_Capital) | WaffleCapital | `drep1yggcntj7vdc2l3j05w0ep84ay8qjz0fnrse6rl8gccd9fsqadw3qg` | `drep1zxy6uhnrwzhuvnarn7gfa0fpcysn6vcuxwsle6xxrf2vq3xvf38` |
| 2 | Socious (@SociousDAO) | Socious | `drep1ytcv4ax77s0enqef56qjflf4d8zjgxulukme9uf5p8cfaagysjppn` | `drep17r90fhh5r7vcx2dxsyj06dtfc5jph8l9k7f0zdqf7z002zj2ckn` |
| 3 | Chris-O (@TheOCcryptobro) | Chris-O | `drep1y25xtvu3d0gaf6cxktr9pkfgnywmqsh4fum93s8m3hlp4aqj3uqdp` | `drep14pjm8ytt682wkp4jcegdj2yerkcy9a20xevvp7udlcd0ggjxdud` |
| 4 | AdaStat (@ada_stat) | AdaStat | `drep1yfe9en4hsgc3r6nhtmwjeljh06hgnvt9yzzkwqcftvdj34cdxdg7u` | `drep1wfwvaduzxyg75a67m5k0u4m746ymzefqs4nsxz2mrv5dwm22ntt` |
| 5 | Ha-Nguyen (@Hahero7) | Ha-Nguyen | `drep1y2z8gktqj27kwmmxesd0y484f7p4z9tjf5xu8m4sucstm3gvtywlp` | `drep1s369jcyjh4nk7ekvrte9fa20sdg32ujdphp7av8xyz7u223jsa2` |
| 6 | Chile Stake Pool (@ChileStakepo) | Rodrigo-[CHIL] | `drep1y2j2q9pcl855969ea9csrhdta6slnamctgzuvuqnnkl6fusqyjy36` | `drep15jspgw8ea9pw3w0fwyqam2lw58ulw7z6qhr8qyuah7j0yj962w7` |
| 7 | Clarity (@clarity_dao) | Clarity Cofounder dRep | `drep1y204jqvq0hu4m26gsaskmaas8vju2ls30hh2s0dhpj03t9qafvuzl` | `drep1navsrqral9w6kjy8v9kl0vpmyhzhuytaa65rmdcvnu2eg9jac55` |

### Hop 2 — off those seven (August 2025)

**From** the same seven DReps. Voting power dropped **35,322,561.149334 ADA** at
epoch 577→578 (2025-08-17 → 2025-08-22), after they said the pull would land
on the 576→577 transition.

**To** no DRep. The 35M did not reappear on EMURGO or Yoroi. The remaining
EMURGO-root bag is 98.60% undeclared.

Identity rows: `emurgo_named_dreps`. Per-DRep deltas: `emurgo_drep_epoch_deltas`.

## Grade

- **FACT:** `drep_distr` time series, current voting-power amounts, DRep identity
  hashes / bech32 IDs / metadata names, live-unspent leftover amounts and the
  single official-DRep leftover UTxO. Receipt: `emurgo_f20_receipt`.
- **EXTERNAL_CORROBORATION:** the dated EMURGO blog/X posts and the seven DRep
  IDs they published (`emurgo_drep_public_events`).
- **STRONG_INFERENCE:** the epoch-558→559 80.1M drop *is* the on-chain
  counterpart of the May 23 removal post; the epoch-561→562 +37.1M and
  epoch-577→578 −35.3M moves on the seven named DReps *are* the park and the
  advertised pull. Voting-power deltas are not tagged “genesis” on-chain.
- **UNKNOWN:** beneficial ownership or custody of the 252M undeclared
  depth-14 descendants. Depth ≥5 commingles. Do not call that bag
  “EMURGO still holds this genesis.”

## Evidence

- `data/small/emurgo_named_dreps.csv`
- `data/small/emurgo_drep_voting_power_history.csv`
- `data/small/emurgo_drep_epoch_deltas.csv`
- `data/small/emurgo_genesis_leftover_by_drep_bucket.csv`
- `data/small/emurgo_genesis_leftover_on_named_dreps.csv`
- `data/small/emurgo_drep_public_events.csv`
- `data/small/emurgo_f20_receipt.csv`
- `sql/10_findings/F20_emurgo_genesis_drep_removal.duckdb.sql`
- `sql/10_findings/F20_emurgo_genesis_drep_removal.remote.sql`

## Reproduce

Against the committed DuckDB cut (no node):

```sql
SELECT metric, value FROM (
  SELECT 'official_leftover_ada' AS metric, ada AS value
  FROM emurgo_genesis_leftover_by_drep_bucket
  WHERE bucket = 'EMURGO official'
  UNION ALL
  SELECT 'community7_removal_ada', abs(delta_ada)
  FROM emurgo_drep_epoch_deltas
  WHERE "window" = 'community7_removal' AND label = 'community7_total'
  UNION ALL
  SELECT 'official_drop_may2025_ada', abs(delta_ada)
  FROM emurgo_drep_epoch_deltas
  WHERE "window" = 'own_drep_genesis_removal'
)
ORDER BY metric;
```

Ask the clone-and-ask MCP:

> Did EMURGO actually remove genesis ADA from its DRep, and how much is left there?

Warehouse rebuild of the CSVs: `sql/10_findings/F20_emurgo_genesis_drep_removal.remote.sql`.

## Limitations

- Leftover amounts join the **July 3 2026** founder depth-14 `current_live_utxos`
  snapshot to a **live** `tx_in` anti-join and **live** latest `delegation_vote`.
  UTxOs created after July 3 are not in the bag. 29 of 6,283 snapshot UTxOs
  had been spent by the live extract (~55k ADA).
- `drep_distr` is the protocol voting-power snapshot for that epoch. It does
  not label which lovelace is genesis-descended.
- Depth-14 reachability is not ownership, custody, or intent.

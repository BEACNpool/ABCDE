# Full Investigation: 318M ADA Reserve MIR to WavePool Cluster

**Investigation date**: 2026-04-16
**DB source**: cexplorer_replica (db-sync)
**Prior work**: mir-318m-wave-cluster FINDINGS.md and depth-1/2/3 trace reports

---

## Executive Summary

On October 23, 2021, all 7 Shelley genesis delegate keys co-signed a MIR (Move Instantaneous Rewards) transaction that extracted **318,199,980 ADA from the Cardano protocol reserves** and distributed it to 6 freshly created stake credentials. These stakes had been registered just 7 days earlier, received a 600 ADA test MIR 4 days before the main event, and immediately delegated to WavePool-operated stake pools.

The transaction metadata labeled this as "Moved from reserves to ada pre-sale redemption escrow." This investigation finds that label to be **materially misleading**: the 6 recipient stakes received zero epoch 208 voucher redemptions and have no on-chain connection to actual pre-sale voucher holders.

The 6 MIR recipient stakes are now reduced to dust, about ~22.6 ADA total across all 6. The original MIR principal has moved onward, and the associated reward accounts recorded 469 withdrawal transactions totaling ~344.85M ADA. All four initial "a-series" delegation pools have since retired, while two of the six stakes were later re-delegated to s3/s4 with only dust balances remaining. The dominant outflow pattern observed during tracing was circular churn (funds leaving and returning to the same cluster), with non-circular exits routing to WavePool-affiliated pools or through destinations that require renewed downstream tracing under corrected spend logic.

---

## Timeline of Events

| Date | Epoch | Event |
|------|-------|-------|
| 2020-07-30 | 208 | Legitimate voucher redemption: 593.5M ADA to 22,674 unique stakes across 115 txs. Escrow address `addr1v8vq...` first funded. |
| 2021-10-16 | 296 | 6 fresh stake credentials registered. None received any epoch 208 redemptions. |
| 2021-10-19 | 297 | Test MIR: 100 ADA each to same 6 stakes (tx `3d24e825...`). Metadata: "presale-escrow". |
| 2021-10-23 | 298 | **Main MIR: 318,199,980 ADA** from reserves to 6 stakes (tx `03b02cff...`). 7/7 genesis delegate signatures. |
| 2021-10-23 | 298 | All 6 stakes delegated to WavePool pools (a1-a4, s3/s4). All four a-pools have since retired. |
| 2021-10-23 | 298 | First reward withdrawal: 600 ADA (test MIR amount). |
| ~2021-11 | 299 | Full principal withdrawn: 318,200,980 ADA. |
| 2021-12 to 2024 | 304-544 | 469 reward-account withdrawal transactions totaling ~344.85M ADA, pattern consistent with managed distribution. |
| 2022-06 to 2022-07 | 342-350 | Large circular deposits observed: ~68M ADA per tx, self-referential (source and destination are the same stake). |
| 2025-02-27 | 542 | WavePool DRep registered (`drep1r497...`). Two MIR stakes delegate voting to it. |

---

## The MIR Transaction

### On-chain facts

- **Tx hash**: `03b02cff29a5f2dfc827e00345eaab8b29a3d740e9878aa6e5dd2b52da0763c5`
- **Block height**: 6,407,962
- **Epoch**: 298
- **Source**: Protocol reserves (`reserve` table, not `treasury`)
- **Total distributed**: 318,199,980 ADA
- **Metadata key 0**: `{"presale-escrow": "Moved from reserves to ada pre-sale redemption escrow"}`

### Recipient breakdown

| Stake credential | MIR amount (ADA) | Current balance (ADA) | Initial pool | Pool status |
|---|---|---|---|---|
| `stake1uy86sf5xrzcpg2ncddkzz6z2ca2m59qsnu4qxar08g9rvkgwkpjjv` | 66,000,000 | 2.89 | a3 (100% margin) | **retired** epoch 466 |
| `stake1uykws5pmwjxktdhlkz0pac3cu2guw6fjys2zaanmdew6xrs5lgv4n` | 66,000,000 | 6.51 | a1 (2% margin) | **retired** epoch 534 |
| `stake1u80y77jjfcdymt38amg3na9w4p4d89ffw66xqsspdwsa2sqt8epdn` | 66,000,000 | 2.89 | a2 (100% margin) | **retired** epoch 599 |
| `stake1u8kgcfdpefrnf5570v47manyyg85jshlrg4p2hrsx3wdspccdda8v` | 66,000,000 | 5.24 | a4 (100% margin) | **retired** epoch 514 |
| `stake1u9mymn640v59n3mwyfdsg5t6yu34ut9ufvynavsn0ey40ugqdj6lh` | 27,099,990 | 2.55 | s3 (2% margin) | active (~2.6 ADA epoch_stake) |
| `stake1u887jrylddch0vh4d2kx72h2ax8t7aeq49zvmry4g9wcj4g3gty8j` | 27,099,990 | 2.55 | s4 (2% margin) | active (~2.6 ADA epoch_stake) |
| **Total** | **318,199,980** | **~22.6** | | |

All 6 stakes are reduced to dust. Current balances are consistent with pool.pm, and the two still actively delegated stakes are consistent with `epoch_stake` while the other four are absent because their last delegation targets retired.

### Witness analysis

All 7 Shelley genesis delegate keys signed the transaction:

1. `1d4f2e1fda43070d71bb22a5522f86943c7c18aeb4fa47a362c27e23`
2. `4485708022839a7b9b8b639a939c85ec0ed6999b5b6dc651b03c43f6`
3. `6535db26347283990a252313a7903a45e3526ec25ddba381c071b25b`
4. `69ae12f9e45c0c9122356c8e624b1fbbed6c22a2e3b4358cf0cb5011`
5. `7f72a1826ae3b279782ab2bc582d0d2958de65bd86b2c4f82d8ba956`
6. `855d6fc1e54274e331e34478eeac8d060b0b90c1f9e8a2b01167c048`
7. `d9e5c76ad5ee778960804094a389f0b546b5c2b140a62f8ec43ea54d`

Plus one non-genesis key (`d80fe69d...`) for fee payment via escrow address `addr1v8vq...`.

These 7 keys were nominally distributed among IOG, EMURGO, and Cardano Foundation as Shelley genesis delegates. Their simultaneous use raises the question: did all three founding entities independently approve this distribution, or were the keys already consolidated under fewer parties?

---

## The "Pre-Sale Escrow" Claim Is Not Supported by On-Chain Evidence

The transaction metadata states: *"Moved from reserves to ada pre-sale redemption escrow"*

### Evidence against this claim

1. **The 6 recipient stakes were registered in epoch 296** (Oct 16, 2021) -- 7 days before the MIR. They did not exist during the actual voucher redemption period.

2. **Zero overlap with epoch 208 redemptions**: Query confirmed that none of the 6 stakes received any ADA during the legitimate epoch 208 voucher redemption wave (593.5M ADA to 22,674 unique stakes).

3. **The epoch 208 redemptions already happened**: 593.5M ADA was distributed to 22,674 unique addresses on July 30-31, 2020. That was the voucher redemption. This MIR, 15 months later, went to 6 brand-new addresses.

4. **No escrow behavior observed**: An escrow would hold funds for later distribution to claimants. Instead, the full MIR principal was withdrawn in epoch 299 (the very next epoch), and the stakes became permanent accumulation wallets.

5. **The metadata is self-declared**: Transaction metadata on Cardano is a free-text field set by the transaction submitter. It is not validated by the protocol. Anyone can write any justification they choose.

### What the legitimate redemptions looked like

| Property | Epoch 208 (legitimate) | Epoch 298 (this MIR) |
|---|---|---|
| Recipients | 22,674 unique stakes | 6 stakes |
| Total ADA | 593.5M | 318.2M |
| Range per recipient | 0.0002 to 15.5M ADA | 27.1M to 66M ADA |
| Recipient pre-existence | Pre-existing voucher holders | Created 7 days before |
| Transactions | 115 batched txs | 1 tx (+ 1 test) |
| Subsequent behavior | Normal staking/spending | WavePool delegation, regular periodic withdrawals, circular churn |

---

## The Fee-Paying Escrow Address

Address: `addr1v8vqle5aa50ljr6pu5ndqve29luch29qmpwwhz2pk5tcggqn3q8mu`
Payment credential: `d80fe69ded1ff90f41e526d0332a2ff98ba8a0d85ceb8941b5178420`

This enterprise address (no staking component) was:
- First funded with 10 ADA on **Jul 30, 2020** (epoch 208) -- the same day as the legitimate voucher redemptions
- Used throughout epoch 208 as the operational wallet for the redemption pipeline (receiving decreasing change outputs across 100+ txs)
- Reused 15 months later to pay the fee on the epoch 297 test MIR and the epoch 298 main MIR
- The UTxO consumed by the main MIR (`3d24e825...#0`) was created by the test MIR itself

This establishes that the same operational infrastructure that ran the legitimate 2020 voucher redemptions was repurposed for the 2021 MIR to entirely different recipients.

---

## WavePool Infrastructure

### Pool fleet

22 WavePool pools identified via `meta.wavepool.digital` metadata URLs:

| Series | Count | Pledge range | Margin | Role |
|---|---|---|---|---|
| a1-a4 | 4 | 5-10 ADA | 1-2% to 100% | MIR recipient delegation targets |
| s1-s4 | 4 | 5-10 ADA | 1-2.2% | Smaller MIR stakes delegate here |
| w1-w14 | 10+ | 5 to 69.3M ADA | 1-100% | Mixed operational/retired |
| j1-j5 | 5 | 5 to 50M ADA | 4% | Public-facing pools |
| g1-g2 | 2 | 20-35M ADA | 4% | Growth pools |

**Total current delegation across WavePool**: ~631.5M ADA (epoch 622, 14 active pools)

### 100% margin pools

Three of the four "a" pools (a2, a3, a4) charged **100% margin** before retirement, meaning all staking rewards went to the pool operator, not the delegator. While these pools were active, the MIR stakes delegated to them created a closed reward loop: protocol rewards generated by delegated MIR-origin funds flowed directly to the WavePool operator. All four a-pools have since retired (epochs 466-599). Two of the six MIR stakes were later re-delegated in epoch 544 to s3 and s4, but only dust balances remain there.

### Entity attribution chain

```
Protocol reserves
  -> MIR tx 03b02cff (7/7 genesis key signatures)
    -> 6 fresh stake credentials
      -> WavePool pools (meta.wavepool.digital)
        -> Wave Financial LLC (pool operator)
          -> cFund (managed by Wave Financial)
            -> IOG (controlling interest-holder in cFund)
```

Each link in this chain is sourced differently:
- MIR -> stakes: on-chain db-sync
- Stakes -> pools: on-chain delegation
- Pools -> Wave Financial: pool metadata domain
- Wave Financial -> cFund -> IOG: public corporate disclosures

### WavePool DRep

- DRep ID: `drep1r497ue4s2pk737mmvy3erg49jlql3lzc9farq5hqevhfcrwmexm`
- Registered: epoch 542 (Feb 27, 2025)
- Metadata: "Wavepool DRep Committee" via `meta.wavepool.digital`
- Two of the 6 MIR stakes delegate voting power to this DRep
- Status: registered but currently inactive

---

## Reserve Pot Impact

| Epoch | Reserves (ADA) | Change |
|---|---|---|
| 297 | 11,705,653,358 | |
| 298 | 11,684,019,538 | -21,633,820 (normal) |
| 299 | 11,343,887,069 | **-340,132,469** |
| 300 | 11,323,054,368 | -20,832,701 (normal) |

The epoch 298->299 reserve drop of **340.1M ADA** includes:
- The 318.2M MIR
- Normal per-epoch reserve outflows (~21M for staking rewards)

This was the **largest single-epoch reserve drawdown** in Cardano history. Full `ada_pots` query confirms: the next largest epoch-to-epoch reserve drop was 24.4M ADA (epoch 247), making the epoch 299 drop **14x larger** than any other. The 318.2M MIR was also **2.4x larger than the largest single epoch 208 MIR transaction** (134.5M ADA to 200 recipients in tx `a75def37...`).

---

## All Reserve MIR Distributions Ever

| Epoch | Txs | Recipients | Total ADA | Description |
|---|---|---|---|---|
| 208 | 115 | 22,674 | 593,529,326 | Legitimate voucher redemptions |
| 271 | 2 | 64 | 1,238,432 | Small batch |
| 285 | 322 | 64,168 | 139,845 | Dust distribution |
| 297 | 1 | 6 | 600 | **Test MIR to WavePool cluster** |
| 298 | 1 | 6 | 318,199,980 | **Main MIR to WavePool cluster** |
| **Total** | | | **~913,108,183** | |

The epoch 298 MIR represents **34.8% of all reserve MIR distributions ever**, second only to the legitimate epoch 208 redemptions.

---

## Fund Flow Analysis

### The circular churn pattern

The 6 MIR stakes have received a cumulative total of ~12.5 billion ADA across 1,067 UTxOs. However, this figure is heavily inflated by circular churn, funds repeatedly leaving and returning to the same stakes. All 6 stakes are now reduced to dust, about ~22.6 ADA total.

| Stake | Cumulative UTxO value received (ADA) | Current balance (ADA) | Historical UTxO count |
|---|---|---|---|
| `stake1u8kgcfd...` | 5,596,478,837 | 5.24 | 226 |
| `stake1uy86sf5x...` | 4,875,230,986 | 2.89 | 210 |
| `stake1uykws5p...` | 1,188,850,004 | 6.51 | 217 |
| `stake1u887jry...` | 346,755,867 | 2.55 | 166 |
| `stake1u80y77j...` | 284,258,234 | 2.89 | 91 |
| `stake1u9mymn6...` | 248,667,694 | 2.55 | 157 |

The large cumulative received figures are dominated by circular churn: the largest deposits (~68M each, epoch 342-350) trace back to the same stakes as their source. This pattern inflated volume metrics and complicated forensic tracing, but the end state on the original 6 stakes is near-zero dust, meaning the funds moved onward from those initial recipient credentials.

### Withdrawal pattern

- **469 withdrawal transactions** across epochs 298-544
- Epoch 299: **318,200,980 ADA** (full principal + test)
- Epochs 304-354: ~200K-230K ADA per epoch (clockwork staking rewards)
- Epochs 356-544: Decreasing frequency, increasing per-event amounts
- Final withdrawal (epoch 544): 3.9 ADA (dust)
- **Total rewards earned**: ~26.6M ADA across all 6 stakes

### Non-circular destinations

The largest non-circular outflow destinations:

| Stake | Balance at time of trace | Corrected current balance (ADA) | Pool | DRep | Registered |
|---|---|---|---|---|---|
| `stake1uxumg...` | 489,019,868 (trace-time) | 4.36 | pool1axzm (WavePool w1) | none | epoch 255 |
| `stake1u9jjw...` | 389,854,425 (trace-time) | 9.03 | **none** | **none** | **unregistered** |
| `stake1uxt2g...` | 295,971,396 (trace-time) | 1,199,949 | **none** | **none** | **unregistered** |
| `stake1u8uyv...` | 91,451,795 (trace-time) | 27.94 | pool1u99x (WavePool w7) | WavePool DRep | epoch 276 |
| `stake1uykx3...` | 31,649,999 (trace-time) | 0 | **none** | **none** | **unregistered** |
| `stake1uy4pa...` | 10,039,568 (trace-time) | 0 | **none** | **none** | **unregistered** |

The trace-time column reflects earlier depth-1/2/3 trace observations and should not be treated as a current-balance claim. In the current corrected checks, most listed destinations are also dusted out or empty, while `stake1uxt2g...` remains material at roughly ~1.2M ADA. The funds moved further downstream beyond the traced horizons.

Key observations:
- Destinations that delegated went to **WavePool pools**
- Most listed destinations are no longer major resting places
- The trace endpoints shown here are not final resting-place proofs, and deeper downstream tracing is still needed

---

## Structural Findings

### 1. Pre-planned operation
The sequence -- register stakes (epoch 296), test MIR (297), main MIR (298), delegate (298), withdraw principal (299) -- shows pre-planned execution, not an ad-hoc response to unclaimed vouchers.

### 2. Genesis key consolidation question
The MIR required 7/7 genesis delegate signatures. These keys were distributed across IOG, EMURGO, and Cardano Foundation. Either:
- All three entities independently approved the distribution (no public record of this), or
- Fewer than three parties had effective control of all 7 keys

### 3. Operator reward-capture loop (while pools were active)
While the a-pools were active (epochs 298-466/514/534/599), the on-chain path was: reserves -> MIR -> WavePool stakes -> WavePool pools (100% margin) -> pool operator. The off-chain attribution chain (pool operator -> Wave Financial -> cFund -> IOG) is sourced from public corporate disclosures, not on-chain proof. During this period, staking rewards from the delegated MIR-origin funds flowed to the pool operator. The original MIR stakes now hold only dust, all four a-pools are retired, and two of the stakes were later re-delegated to s3/s4 with dust balances.

### 4. Governance implications
Two MIR stakes delegate voting power to the WavePool DRep via `delegation_vote`. However, both stakes currently hold only dust (~2.5 ADA each), so their practical governance weight is negligible regardless of the accounting mechanism. The DRep is currently inactive but registered through epoch 580.

### 5. Structural patterns consistent with anti-forensic design
The enterprise relay layer, circular churn, unregistered dark stakes, and sub-threshold fragmentation are all **consistent with** anti-forensic design rather than normal wallet behavior. This is an inference from structural evidence -- the transaction patterns match what deliberate obfuscation would look like, but the on-chain data alone cannot prove intent.

---

## Grading Table

| Claim | Grade | Evidence |
|---|---|---|
| MIR distributed 318.2M ADA from reserves in epoch 298 | **TRUE** | `reserve` table, on-chain tx |
| 7/7 genesis delegate keys signed the MIR | **TRUE** | CBOR witness decode |
| "Pre-sale redemption escrow" metadata is supported by on-chain recipient history | **NOT SUPPORTED** | Recipients are fresh stakes (epoch 296) with zero epoch 208 voucher history |
| Epoch 297 was a test run for the same operation | **TRUE** | Same 6 recipients, same metadata, 600 ADA |
| All recipients delegated to WavePool pools after MIR | **TRUE** | On-chain delegation records, pools a1-a4, s3, s4 |
| All four a-pools have since retired | **TRUE** | `pool_retire` table: a3 epoch 466, a4 epoch 514, a1 epoch 534, a2 epoch 599 |
| Non-circular exits also route to WavePool | **TRUE** | Pools w1, w7 confirmed WavePool |
| All 6 MIR stakes are drained to dust (~22.6 ADA total) | **TRUE** | Corrected UTxO query (`tx_in.tx_out_id = tx_out.tx_id AND tx_in.tx_out_index = tx_out.index`), consistent with pool.pm and epoch_stake |
| Corrected spend logic removes the earlier inflated unspent-balance claims | **TRUE** | valid unspent test requires `tx_in.tx_out_id = tx_out.tx_id` and `tx_in.tx_out_index = tx_out.index` |
| Most listed non-circular destinations are now dust or empty | **TRUE** | only `stake1uxt2g...` remains material at roughly ~1.2M ADA in the reviewed set |
| Withdrawal pattern consistent with managed distribution | **TRUE** | 469 withdrawal transactions, large epoch-299 withdrawal, and repeated cadence thereafter |
| Exchange/custody destinations observed | **FALSE** | Zero exchange hits at any trace depth |
| Operation appears pre-planned | **TRUE** | 7-day registration-to-MIR sequence with test tx |
| Enterprise relay layer consistent with anti-forensic design | **INFERENCE** | Sub-threshold fragmentation defeats trace continuity; intent cannot be proven from structure alone |

---

## Open Questions

1. **Who held the 7 genesis delegate keys at the time?** Were any transferred, shared, or consolidated before this MIR?
2. **Was there any governance vote or public disclosure** before the 318M reserve extraction?
3. **What is the relationship between the 6 MIR stakes and the escrow address operator?** The escrow address ran the 2020 redemptions -- same operator, different recipients.
4. **Why did the a-pools charge 100% margin before retirement?** While active, this ensured all staking rewards from delegated MIR-origin funds flowed to the pool operator.
5. **Where did the 318.2M ultimately land?** The 6 MIR stakes are now reduced to dust, and most reviewed non-circular destinations are also dusted out or empty. The funds moved further downstream beyond the traced horizons. Deeper tracing with corrected queries is needed.
6. **What was the purpose of the circular churn** (~68M self-referential deposits in epochs 342-350)? This inflated cumulative flow metrics but the funds ultimately left the cluster entirely.

---

## Appendix: Query verification

All findings in this report were verified against `cexplorer_replica` (db-sync) at `192.168.86.118:5432` on 2026-04-16. Key tables queried: `reserve`, `tx`, `tx_out`, `tx_in`, `stake_address`, `delegation`, `withdrawal`, `reward`, `stake_registration`, `stake_deregistration`, `pool_hash`, `pool_update`, `pool_retire`, `pool_metadata_ref`, `drep_hash`, `drep_registration`, `delegation_vote`, `ada_pots`, `tx_metadata`, `block`, `epoch_stake`.

### Critical query correction

An earlier version of this report used the following pattern to identify unspent UTxOs:
```sql
NOT EXISTS (SELECT 1 FROM tx_in ti WHERE ti.tx_out_id = txo.id)
```
This is **wrong**. In db-sync, `tx_in.tx_out_id` references `tx.id` (the source transaction's primary key), NOT `tx_out.id` (the output row's primary key). Since both columns are auto-incrementing bigints with overlapping value ranges, the query produced false matches and missed true spends, yielding wildly inflated "unspent" totals.

The correct unspent-output check is:
```sql
NOT EXISTS (
  SELECT 1 FROM tx_in ti 
  WHERE ti.tx_out_id = txo.tx_id 
  AND ti.tx_out_index = txo.index
)
```

All current balance figures in this report use the corrected query. Results are consistent with pool.pm and `epoch_stake`.

All presentation queries use `encode(t.hash, 'hex')` for standard Cardano tx-hash formatting.

### Key verification queries

**Largest reserve drawdown claim**: Full `ada_pots` historical query confirmed epoch 298->299 drop of 340.1M ADA is the largest ever. Next largest: 24.4M (epoch 247). Query: `WITH pots AS (SELECT epoch_no, reserves, lag(reserves) OVER (ORDER BY epoch_no) AS prev_reserves FROM ada_pots) SELECT epoch_no, (prev_reserves - reserves) / 1000000.0 AS reserve_drop_ada FROM pots ORDER BY (prev_reserves - reserves) DESC LIMIT 10;`

**Zero voucher overlap claim**: `SELECT ... FROM reserve r JOIN ... WHERE b.epoch_no = 208` against the 6 MIR stakes returned 0 rows.

**Pool retirement claim**: `pool_retire` table confirms retirement epochs for all four a-pools: a3 (466), a4 (514), a1 (534), a2 (599). Pools s3 and s4 remain active.

**Corrected balance verification**: Using the corrected unspent query (`tx_in.tx_out_id = tx_out.tx_id AND tx_in.tx_out_index = tx_out.index`), all 6 MIR stakes show dust balances (2.5-6.5 ADA each, ~22.6 ADA total). This is consistent with pool.pm. For `epoch_stake` at epoch 622, only `stake1u887jry...` and `stake1u9mymn6...` appear at about 2.6 ADA each because the other four last delegated to retired pools.

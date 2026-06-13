# IOGP Pledge and Voucher-Address Follow-up

This report ports the June 10, 2026 follow-up into ABCDE's reproducible evidence
model. It corrects rounded figures, preserves full identifiers, and separates
chain facts from operational-cluster inference.

The source snapshot ends at block `13,520,244`, epoch `635`,
`2026-06-07 18:44:37 UTC`.

## Evidence boundary

The address examined here appears in the September 2, 2025
[Investigative Report and Forensic Audit](https://www.adaredemptiontransparency.com/investigative-report.pdf)
concerning the Voucher Program. Any statement that an organization controlled
the address is an external attribution. ABCDE does not adopt or independently
verify that identity claim.

ABCDE verifies only the on-chain records and deterministic trace paths below.

## IOGP pledge correction

**FACT.** Pool
`pool1x5ge78ks6jc0j8nsfwyqqhk2ukxlkvz7zxlm9utgk6405hh490n`
registered with ticker `IOGP` on `2021-02-04 18:53:24 UTC` in transaction
`17765cd5600e70becc1356b48f370e8623f9a3b89e247b94e77b141a54254ac9`.

Its declared pledge parameter was exactly `1,000,000 ADA`, not `64M ADA`.

The pool's reward credential was
`stake1uxnwfdn9samwjqj6n3sfgtflxmca47l4dns8snkz0tp9v6c5nnhs3`.
That credential's active stake in the pool was:

| Epoch | Active stake |
|---:|---:|
| 250 | 66,360,281.121632 ADA |
| 255 | 64,363,477.004344 ADA |
| 260 | 35,793,455.129878 ADA |
| 270 | 39,096,784.963490 ADA |
| 290 | 0 ADA |

The registered owner credential,
`stake1u8j97tdpg2m69dl9augnj9zqrh95t3dd6cuxuner6eypzpctfdkkx`,
carried approximately `1,000,002.806122 ADA` in epochs 250–270.

The defensible wording is therefore:

> The IOGP pool declared a 1M ADA pledge. Its reward credential carried roughly
> 64–66M ADA of active stake around epochs 250–255.

Calling the larger amount the registered pledge is incorrect. Calling the
reward credential an identified organization's wallet goes beyond the chain
evidence.

## Voucher-address profile

The reviewed address is:

`addr1qy2qmzemzpx4w3sz0z8fp0x2xwnttksn655uc5sxml2yaznsluv29uarg9hhghehhf7r7kmyrh6wsvtgg2caanrf94us0j0w0n`

**FACT.**

- Stake credential:
  `stake1u9c07x9z7w35zmm5tumm5lpltdjpma8gx95y9vw7e35j67gz7r8a7`
- Addresses sharing that credential: `6`
- Outputs at the reviewed address: `519`
- Lifetime received at the reviewed address: `176,252,311.282813 ADA`
- Lifetime received across the stake credential: `176,449,088.336762 ADA`
- Observed activity: `2023-04-05 19:27:16` through
  `2026-02-27 20:21:26 UTC`

On its first observed day, the stake credential delegated to the IOG1-ticker
pool:

- pool:
  `pool1mxqjlrfskhd5kql9kak06fpdh8xjwc76gec76p3taqy2qmfzs5z`
- certificate transaction:
  `816507d47b5b6ca9b414fcab11e730e719b59e8b24f941f631353fa97d8a5eee`
- time: `2023-04-05 19:51:12 UTC`

Delegation is an on-chain relationship. It does not prove custody or identity.

## Rounded audit figure and subsequent flow

**FACT.** On `2023-10-05 20:48:21 UTC`, the reviewed address received exactly
`52,196,773.895086 ADA` in a transaction whose inputs included
`stake1uy6yzwsxxc28lfms0qmpxvyz9a7y770rtcqx9y96m42cttqwvp4m5`.

Thus `52,196,774 ADA` is a correct whole-ADA rounding of the inflow, but it is
not the lovelace-exact amount and should not be described as an independently
verified end-of-day balance.

At `21:44:55` and `21:53:00 UTC` that evening, transactions spending outputs
from the reviewed address sent a combined `60,000,003.141590 ADA` to:

`addr1vymu4620q8vqf4xsstfrk6dy72787syvezet8ujsdj2k3jsfvlx47`

That address is a forward endpoint present in the earlier 2021 flow package.
The shared endpoint is a chain fact; common operation is an inference.

## WAV10 two-way flow

**FACT.** The reviewed address's transactions intersected in both directions
with:

`stake1u90z89xl6qkgt0lpn79svmpmz9evstxy4wfp8wgpyfcgg5seurw78`

This is the registered owner/reward credential of the WAV10-ticker pool in the
underlying pool receipts.

- inbound association: `13,280,311.000000 ADA` across two transactions;
- outbound outputs: `13,280,301.175115 ADA` in one transaction.

These are transaction-flow observations, not proof that one actor controlled
both credentials.

## Deterministic genesis paths

**FACT as path existence.** Deterministic largest-input traces from three
selected funding transactions terminate at the same IOG genesis transaction:

`0ae3da29711600e94a33fb7441d2e76876a9a1e98b5ebdefbf2e3bc535617616`

| Seed transaction | Deterministic depth |
|---|---:|
| `bd32485b5035d337e8ba5bcce02024a64c2062e9ce9c5f81be22e62a3da8987b` | 27 |
| `8d9d406cefb7831cc85933b23baf7179b884907d86f480134771d7e737957b4d` | 26 |
| `02c3a6b01b8bf3b20df3d41bc904ff4a22b0a67d2c561d386d34aaa9cd4b55be` | 64 |

The depth-64 path includes, in sequence, the WAV1 owner credential, payer 3, an
IOG17-ticker pledge/aggregation credential, and an IOG20-ticker pledge
credential before reaching the genesis chain.

This method follows one largest input at each transaction, with a deterministic
tie-break for equal values. It establishes a path, not exclusive provenance.
The older query omitted a tie-break and therefore produced method-dependent
depths of 39 and 38 for the first two seeds.

## IOGP reward-credential outflows

**FACT.** Transactions spending outputs from the IOGP reward credential sent:

- `925,000,100 ADA` across 32 transactions to the burst credential
  `stake1uycla9q3glrugp48cq2r7awemjxepvj4lxs4emw5qmpsclc4tpe52`;
- `154,564,895 ADA` across six transactions to the same forward endpoint
  later reached by the voucher address; and
- `182,000,000 ADA` across two transactions to
  `addr1vx9lp37m3xk7qhdw6uwp8crduqcwlm56wtf56yume76pwwqvtdsdu`.

The first line establishes that the IOGP reward credential was a direct
upstream source for nearly all of the previously identified 925M burst.

## Direct-funder context

**FACT.** The voucher address's 28M-class funder,
`stake1u8nynuagsfkjfsjfhm57dnyzfae8e5szh4rfdxjk2drt53qwhz039`,
has deposit transactions associated with inputs from:

- IOG19-ticker pledge credential
  `stake1ux9vw6azy95waz9l3e8dme7pwmhcn68f77kqd245uxw57nqr9upaa`:
  `1,793,844.822538 ADA`;
- IOG20-ticker pledge credential
  `stake1u8tl8t5pdr9qn488vc9dpehklntt55au96fkqpd8nr28qyqzr7lax`:
  `1,775,775.359025 ADA`.

Both direct funders have delegation records involving the IOG1-ticker pool.
The complete source summaries and delegation histories are committed as
queryable tables rather than reduced to these highlighted rows.

## Conclusion

The chain supports a **STRONG INFERENCE** that this 2023-era address intersects
the broader IOG-ticker/WAV/payer operational cluster through several independent
signals: delegation, shared endpoints, two-way pool-credential flows, direct
funder history, and a common deterministic genesis terminal.

It does not establish:

- legal or beneficial ownership of the address;
- that any named organization controlled it;
- intent behind any transfer;
- exclusive provenance under the dominant-input method.

## Reproduction

The nine committed receipt tables are generated by:

```bash
ABCDE_SSH=abcde scripts/build_iogp_voucher_followup_remote.sh
python scripts/build_genesis_db.py
python scripts/verify_iogp_voucher_followup.py
```

They are queryable in `data/abcde_genesis.duckdb`; table names begin with
`iogp_`, `iog_voucher_`, or `voucher_`.

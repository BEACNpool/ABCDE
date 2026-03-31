# IOG Genesis Allocation: Output Generation & Routing (Epochs 245-252)

**Query Reference:** `/queries/iog_epoch_245_252_routing.sql`

## Methodology
This data extract details the UTxO generation and subsequent delegation routing for the IOG genesis allocation between Epochs 245 and 252. The data was extracted by recursively tracing the IOG genesis allocation to depth 15 using a local Cardano `db-sync` PostgreSQL instance. The queries isolate generated outputs holding `< 50,000 ADA` and map their immediate delegation transactions.

## Data Output 1: UTxO Generation (< 50,000 ADA)
The following table shows the timeline of UTxO creation for outputs under 50,000 ADA within the traced IOG lineage.

| Epoch | Date Window | UTxOs Created |
| :--- | :--- | :--- |
| 244 | 2021-01-26 to 2021-01-30 | 91 |
| 245 | 2021-01-31 to 2021-02-04 | 4,140 |
| 246 | 2021-02-04 to 2021-02-09 | 10,224 |
| 247 | 2021-02-09 to 2021-02-14 | 16,446 |
| 248 | 2021-02-14 to 2021-02-19 | 8,455 |
| 249 | 2021-02-19 to 2021-02-24 | 5,704 |
| 250 | 2021-02-24 to 2021-03-01 | 6,053 |
| 251 | 2021-03-01 to 2021-03-06 | 3,587 |
| 252 | 2021-03-06 to 2021-03-11 | 1,481 |

**Total:** ~56,000 UTxOs created across epochs 245–252.

## Data Output 2: Delegation Routing
The following table maps the on-chain delegation events for the sub-50k ADA wallets generated in the timeline above.

| Epoch | Date Window | Pool ID | Wallets Delegating |
| :--- | :--- | :--- | :--- |
| 247 | 2021-02-09 to 2021-02-14 | `pool1uj4u73qgtprqre78q75fq2vkcrpfrcdreqcqkvn6u0m2k6nk2yp` | 357 |
| 248 | 2021-02-14 to 2021-02-19 | `pool1uj4u73qgtprqre78q75fq2vkcrpfrcdreqcqkvn6u0m2k6nk2yp` | 327 |
| 246 | 2021-02-05 to 2021-02-08 | `pool1g3ssnndd8e7lcmstkjl9ane9mup0eshv3aklg63u5tznwl4ch87` | 190 |
| 245 | 2021-01-30 to 2021-02-04 | `pool1zgxvcqf0dvh0ze56ev2ayjvuex3zdd3hgxzdrcezkx497mv3l7s` | 180 |
| 249 | 2021-02-19 to 2021-02-21 | `pool1uj4u73qgtprqre78q75fq2vkcrpfrcdreqcqkvn6u0m2k6nk2yp` | 102 |
| 250 | 2021-02-25 to 2021-03-01 | `pool1ng3vqzrhn3z45yjdscv3q37n26g2pj3vp99rfkgv6225y8lqg8j` | 193 |
| 251 | 2021-03-01 to 2021-03-06 | `pool1ng3vqzrhn3z45yjdscv3q37n26g2pj3vp99rfkgv6225y8lqg8j` | 145 |
| 246 | 2021-02-04 to 2021-02-09 | `pool1zmfpd5r5vfwjmwm4cgy53exe58h7plnecny3t4948yw7zumzp4c` | 77 |
| 246 | 2021-02-06 to 2021-02-09 | `pool1jst7rrhucnp93hepezv5yqy6fx982xs2v0udwfc5ea6my3kfak7` | 73 |
| 247 | 2021-02-09 to 2021-02-14 | `pool13annzt9hjfc822f0ejvxjf7fsmxd6cc28whpk5kagec6ggfmm7u` | 52 |

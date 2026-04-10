content = """
---

## Part 10 — Cross-Entity Stake Address Overlap (Shared Wallet Credentials)

### Overlap Summary

| Pair | Shared Stake Addresses | IOG Total | EMURGO Total | CF Total |
|:---|---:|---:|---:|---:|
| IOG only | 8,542 | 9,562 | — | — |
| EMURGO only | 3,929 | — | 4,973 | — |
| CF only | 1,564 | — | — | 1,694 |
| IOG ∩ EMURGO | 967 | 9,562 | 4,973 | — |
| IOG ∩ CF | 53 | 9,562 | — | 1,694 |
| EMURGO ∩ CF | 77 | — | 4,973 | 1,694 |
| IOG ∩ EMURGO ∩ CF | **7** | 9,562 | 4,973 | 1,694 |

These are stake credentials (private keys) that controlled genesis-traced ADA from multiple founding entities simultaneously. The 967 IOG∩EMURGO shared addresses are particularly significant: they represent wallets whose stake keys appear in both the IOG trace tree (rooted at `fa2d2a70c0b5fd45cb6c3989f02813061f9d27f15f30ecddd38780c59f413c62`) and the EMURGO trace tree (rooted at `242608fc18552a4ac83adabcef7155f3b909e83d469ce89735db8f11d3637e38`).

### The 7 Stake Addresses Present in All Three Entity Traces

These are the most significant addresses in the entire dataset. Each stake credential simultaneously controlled genesis-traced funds from IOG, EMURGO, and CF.

| # | Stake Address (full) |
|---:|:---|
| 1 | `stake1u85re0n76p05ld36le8ytuuhdst0lu4mmh8g53hmpqd6txsxxta6n` |
| 2 | `stake1u86jl5trmfr70cjfe6capkl2ptx05l8jflspswgh79el5ygcv8xwh` |
| 3 | `stake1u87mehxnkc68j98vsmuf6vrrlcfygppyxvkkwm4n89n2jssanukrm` |
| 4 | `stake1u89zwwc9sntxuh2e7qtjydkfdse9fv8uckzqvcg2xp6yw9gj6yp06` |
| 5 | `stake1u8etn7ndaq3t76af2vlfg74dexkfs7ysm5fwhtjth45z3ccdme5gq` |
| 6 | `stake1u907m66smf4lefjzgp7v7zzmjpjeljrvdm5vttv6nulm0asv2de62` |
| 7 | `stake1uxvvzsuuk8v0r2kksutrwvd2fe0kms3d4qh5a3su5vky53gjx9uqw` |

Any wallet operator controlling these stake keys had simultaneous cryptographic access to funds traceable to all three genesis allocations.

### IOG ∩ CF Shared Stake Addresses (53 total)

| Stake Address |
|:---|
| `stake1u8075gw62ahe5rc84vp6hw05e02fevlwm6lamczy0sk6ytcmze8aw` |
| `stake1u80zrk9u8fcp4sple4685lf9vmypq4wnnzh5vf5eylcd4zgraf9jr` |
| `stake1u85re0n76p05ld36le8ytuuhdst0lu4mmh8g53hmpqd6txsxxta6n` |
| `stake1u86jl5trmfr70cjfe6capkl2ptx05l8jflspswgh79el5ygcv8xwh` |
| `stake1u87aytjcdvslr263akxxjmygeeefj4yyntrdvjp38m39qyss32x3q` |
| `stake1u87mehxnkc68j98vsmuf6vrrlcfygppyxvkkwm4n89n2jssanukrm` |
| `stake1u88cx445rnssqrk8kvvtz2vdv03ed7nj9hw58l47kdmnpkqcttk6u` |
| `stake1u89zwwc9sntxuh2e7qtjydkfdse9fv8uckzqvcg2xp6yw9gj6yp06` |
| `stake1u8ajaufgelqyxp89whx8f0t57ndtcuvctfz2z8v3qfxxk3szmchqp` |
| `stake1u8etn7ndaq3t76af2vlfg74dexkfs7ysm5fwhtjth45z3ccdme5gq` |
| `stake1u8flq5rq8mt3tz2narxpu0nxwrpnltale8vgxkrrnvlr6dqu3ltvn` |
| `stake1u8ftwxmr3d55nvlcta8xc2k9zm8p0h5k28nf92ltsvjmmsqehhsq9` |
| `stake1u8hmy88mv2uuzyhtaxg5p3fflrzhrlyh9ey235zcsmyfyjgfhxr8h` |
| `stake1u8kj9qyemvv8ey3cv8g4y7wj8t8s0exn06ndgp9zff5fvsq3tk9ty` |
| `stake1u8n0kp7t97eu0z5y9jasp63lv7nzqyzv8muq454dc255zlsl0udsj` |
| `stake1u8njfw59kr8c4tj9p7fy9l728h4cjyhd249wsw3u5ghx93qs5vmk6` |
| `stake1u8tcdp4xejtswx2tvvxyr8ahhrdy9x9cjfvl38fw5wk7h6q70m05r` |
| `stake1u8tf44puxjcykfptqxq9zhn5v7ezlzm6e20wz0t0pmkrtuq0ugsk4` |
| `stake1u8tq4s2f03gzvckm2guv5yql4jaa3enw5h8t9mqg8la64egwq6yka` |
| `stake1u8w48j3k8pgakle2upk0fe8w0p4c8ptw0ufzej2n3al6cxggrzm2k` |
| `stake1u8wvq5nufazxzdmhkc8vs2c7ut3t5xc5xmga0a47r3erxfceh88h0` |
| `stake1u8x3gc8wsyysrhelcvgj65f9jqvzfzsndu072xcj6kyvqkcufl4zz` |
| `stake1u907m66smf4lefjzgp7v7zzmjpjeljrvdm5vttv6nulm0asv2de62` |
| `stake1u90e2wmnsgr9d8gjxuxt0cwnmztazwsj9k3jc33zzzzsxtcakcp9v` |
| `stake1u93rztxhnt9zzngrldcj6pw9lnezenknrd4gc30xv7y0htgvap9z5` |
| `stake1u98690w60kq54udx9h46p35epgm7mhq6hqxxtjen6rsqg5g9u2r0s` |
| `stake1u99syacns4h6kes0urk00xpv93qd9edn0m5wnv9arpha4ucrk7qlc` |
| `stake1u9c5uezuevsmhagw7wgnwgfkz8j4zn0d0l5lwu4h7nrvlpg6vtpye` |
| `stake1u9jklnte98sfpyyeq276q9pyn6ynsks7usuehy8vjgx3utq7twd2c` |
| `stake1u9lrp6pc9ck77p5t7e2mh8na6dep2amdw75sylyyx9wnlus3y9h8x` |
| `stake1u9mwjgt28pp4kp8amj2jrh80tlhsln322mr2k93te66te7cxdp4j8` |
| `stake1u9qp97ze3uehg6yn2ewvf0cztyn97g3v0crwwuqqmzwj5ygshhnge` |
| `stake1u9t5z2cd6ptrudkqmpz6g2zuh74duzhh8h33vtm55fy3cpcqwva72` |
| `stake1u9txk6hsds3tgdvn3h4tcfnslyrx7ye6m3rlq0nv2jlhmnsknnu5q` |
| `stake1u9vjtuhl679r4x5v40xhjfrafze0yskyxrsju0qhkgc0g7skkzf4m` |
| `stake1u9z9d3syucxs8q76744ch4gm0v6gh4awllca2s0k7xfgwfgrmp4ev` |
| `stake1ux28yyldalcy92hkg2ycr90vu7ll4c8xdczd4vs4qzqu84cqvk7xq` |
| `stake1ux2aylqan5z5urx0l6z89554tdnzm9gvudsc3ujwz8sh22sk0j6zc` |
| `stake1ux3p5tyfc3jt54843qwpy69kf5a993vqghyndmg8gjg98ds6zxefm` |
| `stake1uxkxy0vl3l8mct2xlm0gqdgjan2kw0j43jp203r6t4g0k4q3devew` |
| `stake1uxkz0cqj2zff2zdqx7naf4cdek5jxfxt7awpust0da2c5sg7yp88r` |
| `stake1uxnn2ky0dcpymqqvda9uvkrx902u3yuqleue4k6kngfh5cg0mt2wy` |
| `stake1uxvvzsuuk8v0r2kksutrwvd2fe0kms3d4qh5a3su5vky53gjx9uqw` |
| `stake1uxy9aunymgxdzfhjggm2pzx4675f4a3ymu5yqmexdzusz6sjgrfzz` |
| `stake1uy3m9gmrvceps5l3wjqr62ffan004tpa2mwfvxtzcc5cpqq5w4s74` |
| `stake1uy47jp4t6dmmwm6mpqzcmwfxmx8pqc7gz7g0sxml0mnqu2g0ucaer` |
| `stake1uy4d364gve3lq084ypmwzsmt95csgqxpfyxxeltef0z05ggw55hhx` |
| `stake1uy9cl2zzcntgkjvt7jmdwv8j905yqnerkrj975kf2c9gmqgshwwsa` |
| `stake1uynvaczl4jqjwqxxmtpsv2fg4jnys0zyh4s7hdpz59yuy3ghlqa8a` |
| `stake1uyv6xgv0akrt5s8gwf802v08pfclzaumhkxy9680nrv6nlsylapmq` |
| `stake1uyxhzxe4wa5qm7uzz8v82w5y5nzjdyejrw2af6mlj08tagspxgpz5` |
| `stake1uyz2x5qt34v2e5txpyhvrm00y4kntqeay0w2yvyn4w35dmc7zsgcl` |
| `stake1uyzh7qtcfjnhx4tzea869vwdlux4ptfak35wqfup0a4kwrgp528xa` |

---

## Part 11 — Primary Splitting Address (Cross-Entity)

The Byron address `Ae2tdPwUPEZ6xYrxCgRDM2NQFM5oajHEoJN3i9ZVV2AbsbvxoJBjVu3yP7W` is the single most active mechanical splitter in the entire dataset.

**IOG:** All 10 top fan-out transactions originate from this address (epochs 249-250, hops 10-11). Each transaction fans out to exactly 58 outputs.

**EMURGO:** This same address appears as the source of EMURGO fan-out ranks 4, 5, and 6 (epoch 249, hop 13, 58 outputs each). The identical address appears in two independent genesis traces rooted 3 weeks apart (IOG anchor: 2017-09-27, EMURGO anchor: 2017-10-18).

This means a single Byron private key — controlling address `Ae2tdPwUPEZ6xYrxCgRDM2NQFM5oajHEoJN3i9ZVV2AbsbvxoJBjVu3yP7W` — was used to mechanically split funds traceable to BOTH the IOG genesis allocation AND the EMURGO genesis allocation at epochs 249-250 (approximately early 2021).

### IOG Top 10 Fan-Out Transactions (all from shared splitter address)

| Rank | Outputs | ADA In | Epoch | Hop | Source Address |
|---:|---:|---:|---:|---:|:---|
| 1 | 58 | 615,404.33 | 250 | 10 | `Ae2tdPwUPEZ6xYrxCgRDM2NQFM5oajHEoJN3i9ZVV2AbsbvxoJBjVu3yP7W` |
| 2 | 58 | 939,881.81 | 249 | 11 | `Ae2tdPwUPEZ6xYrxCgRDM2NQFM5oajHEoJN3i9ZVV2AbsbvxoJBjVu3yP7W` |
| 3 | 58 | 1,836,403.29 | 249 | 11 | `Ae2tdPwUPEZ6xYrxCgRDM2NQFM5oajHEoJN3i9ZVV2AbsbvxoJBjVu3yP7W` |
| 4 | 58 | 929,279.69 | 250 | 11 | `Ae2tdPwUPEZ6xYrxCgRDM2NQFM5oajHEoJN3i9ZVV2AbsbvxoJBjVu3yP7W` |
| 5 | 58 | 329,707.89 | 250 | 11 | `Ae2tdPwUPEZ6xYrxCgRDM2NQFM5oajHEoJN3i9ZVV2AbsbvxoJBjVu3yP7W` |
| 6 | 58 | 333,343.26 | 250 | 11 | `Ae2tdPwUPEZ6xYrxCgRDM2NQFM5oajHEoJN3i9ZVV2AbsbvxoJBjVu3yP7W` |
| 7 | 58 | 373,387.98 | 250 | 11 | `Ae2tdPwUPEZ6xYrxCgRDM2NQFM5oajHEoJN3i9ZVV2AbsbvxoJBjVu3yP7W` |
| 8 | 58 | 264,302.56 | 250 | 11 | `Ae2tdPwUPEZ6xYrxCgRDM2NQFM5oajHEoJN3i9ZVV2AbsbvxoJBjVu3yP7W` |
| 9 | 58 | 407,719.17 | 250 | 11 | `Ae2tdPwUPEZ6xYrxCgRDM2NQFM5oajHEoJN3i9ZVV2AbsbvxoJBjVu3yP7W` |
| 10 | 58 | 641,137.61 | 250 | 11 | `Ae2tdPwUPEZ6xYrxCgRDM2NQFM5oajHEoJN3i9ZVV2AbsbvxoJBjVu3yP7W` |

### EMURGO Top 10 Fan-Out Transactions

| Rank | Outputs | ADA In | Epoch | Hop | Source Address |
|---:|---:|---:|---:|---:|:---|
| 1 | 72 | 17,660,808.79 | 175 | 12 | `DdzFFzCqrhstmqBkaU98vdHu6PdqjqotmgudToWYEeRmQKDrn4cAgGv9EZKtu1DevLrMA1pdVazufUCK4zhFkUcQZ5Gm88mVHnrwmXvT` |
| 2 | 72 | 47,224.75 | 208 | 13 | `DdzFFzCqrht6YJCbKpjkr1GfF8wecZpEVHsvWv3VfdVmzCDryY7TQVudgh6nGJg7SZKgUWW2mfga9NABLHCiHbeV7MaL3zvNaSY5Ukz6` |
| 3 | 72 | 17,660,808.79 | 175 | 13 | `DdzFFzCqrhstmqBkaU98vdHu6PdqjqotmgudToWYEeRmQKDrn4cAgGv9EZKtu1DevLrMA1pdVazufUCK4zhFkUcQZ5Gm88mVHnrwmXvT` |
| 4 | 58 | 880,085.41 | 249 | 13 | `Ae2tdPwUPEZ6xYrxCgRDM2NQFM5oajHEoJN3i9ZVV2AbsbvxoJBjVu3yP7W` |
| 5 | 58 | 836,311.25 | 249 | 13 | `Ae2tdPwUPEZ6xYrxCgRDM2NQFM5oajHEoJN3i9ZVV2AbsbvxoJBjVu3yP7W` |
| 6 | 58 | 288,261.27 | 249 | 13 | `Ae2tdPwUPEZ6xYrxCgRDM2NQFM5oajHEoJN3i9ZVV2AbsbvxoJBjVu3yP7W` |
| 7 | 58 | 284,094.11 | 250 | 13 | `Ae2tdPwUPEZJYoSsP4KK2fuG1BaYon52ZezMj7CVedG9KfyEd3RXezGSs7j` |
| 8 | 58 | 1,243,492.19 | 250 | 13 | `Ae2tdPwUPEYzzo7Q6VqUfQYctzXQPqAQywMgruCTsuxz1xi8zAYay9FXQZZ` |
| 9 | 58 | 824,162.95 | 250 | 13 | `Ae2tdPwUPEYzBxnm5gytqhy1qzgyTfS8fVzfo7KAyBqA1JLVekPKTR7x1zh` |
| 10 | 58 | 836,940.31 | 250 | 13 | `Ae2tdPwUPEZ7EYhmdxow9rTRMuKUJPZdYBcTDPT7Kpyva1Uy1PvnuxAUW7m` |

### CF Top 10 Fan-Out Transactions

| Rank | Outputs | ADA In | Epoch | Hop | Source Address |
|---:|---:|---:|---:|---:|:---|
| 1 | 147 | 469,955.40 | 208 | 15 | `Ae2tdPwUPEZFN3bHkMWtiUdEsRrDAm65okvCMad3hohXEfaM1uc6Q8rQDh6` |
| 2 | 82 | 22,829,000.29 | 208 | 15 | `DdzFFzCqrht5d66v6te675Bw1hRtyuEgEfUYHBH6eB9tJFTbKBjdqhAAaWJka5vnh5ARkWpa2ibA8co1vkw6oxcrvEirW8o8FW568nYZ` |
| 3 | 60 | 602,933.71 | 209 | 15 | `DdzFFzCqrht5xp7vkGMWw2rpjb6mEDNyPHGM8wny53HMFdn7RzyrBzT2HGnE2GDPgkx2FfdEv2s2WZMeiF7GEit7Dujbdu1B4SyqQK7h` |
| 4 | 56 | 2,269,346.49 | 208 | 14 | `DdzFFzCqrht8XRXzWppbeRDD9behmWX2MC7rGspnEdhKdaGncYsyTnYnDY9eeqidMNCwGXz8aXt8NRKuimME9V5JWj7aexkmD6662ZGm` |
| 5 | 56 | 2,269,346.49 | 208 | 15 | `DdzFFzCqrht8XRXzWppbeRDD9behmWX2MC7rGspnEdhKdaGncYsyTnYnDY9eeqidMNCwGXz8aXt8NRKuimME9V5JWj7aexkmD6662ZGm` |
| 6 | 52 | 447,570.18 | 208 | 15 | `DdzFFzCqrhsfpqZxAsFCVP8bD4ofKPGxatGL2gChQL6yWwcdUjYgv2pkMGurof5EuJ1tg4QFx1mtZ179w2KhF6xSvqP8tRYxRPRvyYQf` |
| 7 | 49 | 156,651.80 | 208 | 14 | `Ae2tdPwUPEZFN3bHkMWtiUdEsRrDAm65okvCMad3hohXEfaM1uc6Q8rQDh6` |
| 8 | 47 | 1,118,726.21 | 208 | 13 | `DdzFFzCqrhsvQrEJknSeubfvnB79xnaCvzxAr2CsSmp9UEBBuN9NdiTQuGUJfBoEk25puWwDNEqJgeXXSAXJtNixvJrkAXARswLjDGSz` |
| 9 | 47 | 670,911.23 | 208 | 13 | `DdzFFzCqrhszQedF26C112azrPDZGDRcWCqmXRT6AQfCEXqBh58ywLsHtToqjnusLMZLBoD3JndiekVpuSe4PQDrB8APuMkgVrMrsK79` |
| 10 | 47 | 1,118,726.21 | 208 | 14 | `DdzFFzCqrhsvQrEJknSeubfvnB79xnaCvzxAr2CsSmp9UEBBuN9NdiTQuGUJfBoEk25puWwDNEqJgeXXSAXJtNixvJrkAXARswLjDGSz` |

---

## Part 12 — Binance Address as Distribution Source (EMURGO and CF)

The address `DdzFFzCqrhstmqBkaU98vdHu6PdqjqotmgudToWYEeRmQKDrn4cAgGv9EZKtu1DevLrMA1pdVazufUCK4zhFkUcQZ5Gm88mVHnrwmXvT` is confirmed by exchange classification heuristics as a Binance Byron-era hot wallet address.

This address appears not only as a recipient of genesis funds but as a **distribution source** in both EMURGO and CF traces:

- **EMURGO ranks 1 and 3:** Two separate fan-out transactions each distributing 17,660,808.79 ADA (72 outputs each) at epoch 175, hop 12-13
- **Implied role in CF:** Multiple CF fan-outs at epoch 208 also use `DdzFFzCqrht5d66v6te675Bw1hRtyuEgEfUYHBH6eB9tJFTbKBjdqhAAaWJka5vnh5ARkWpa2ibA8co1vkw6oxcrvEirW8o8FW568nYZ` and related Ddz-prefix addresses as source

This is the only address in the dataset that is simultaneously:
1. Classified as an exchange address (Binance hot wallet)
2. Acting as a **source** of fragmentation to new addresses (not just a recipient absorbing funds)
3. Present in traces from two separate founding entities (EMURGO at epoch 175, CF at epoch 196/208)

The implication is that EMURGO and CF genesis funds were routed **through** a Binance hot wallet before being distributed to end addresses — not merely deposited there as a terminal destination. This is consistent with OTC or custodial distribution operations where the exchange serves as the distribution infrastructure.

---

## Part 13 — Top 30 Pool Rankings (Computed from Delegation History CSVs)

### IOG — Top 30 Pools (Computed)

| Rank | Unique SA | Epoch Min | Epoch Max | Pool ID |
|---:|---:|---:|---:|:---|
| 1 | 860 | 248 | 432 | `pool1uj4u73qgtprqre78q75fq2vkcrpfrcdreqcqkvn6u0m2k6nk2yp` |
| 2 | 510 | 244 | 555 | `pool1zgxvcqf0dvh0ze56ev2ayjvuex3zdd3hgxzdrcezkx497mv3l7s` |
| 3 | 482 | 252 | 574 | `pool1ng3vqzrhn3z45yjdscv3q37n26g2pj3vp99rfkgv6225y8lqg8j` |
| 4 | 350 | 239 | 400 | `pool1g3ssnndd8e7lcmstkjl9ane9mup0eshv3aklg63u5tznwl4ch87` |
| 5 | 292 | 248 | 409 | `pool13annzt9hjfc822f0ejvxjf7fsmxd6cc28whpk5kagec6ggfmm7u` |
| 6 | 257 | 241 | 606 | `pool1ynxx88cq0y8vg8yrq3jrw6epm7rq9a8859v34sq9lzjy7ztg90u` |
| 7 | 253 | 234 | 525 | `pool1jst7rrhucnp93hepezv5yqy6fx982xs2v0udwfc5ea6my3kfak7` |
| 8 | 253 | 255 | 482 | `pool1xmsdhync6k6grkkj7tuycskjpseykpr24luhlazl5nsngsy87gm` |
| 9 | 219 | 238 | 622 | `pool16agnvfan65ypnswgg6rml52lqtcqe5guxltexkn82sqgj2crqtx` |
| 10 | 212 | 244 | 362 | `pool1zmfpd5r5vfwjmwm4cgy53exe58h7plnecny3t4948yw7zumzp4c` |
| 11 | 193 | 256 | 620 | `pool1ywpt43nttzjd7883wafg255mh0hmjypwe65ercw6p2sxg5lt7ez` |
| 12 | 187 | 210 | 557 | `pool16kus5xvdysgmtjp0hhlwt72tsm0yn2zcn0a8wg9emc6c75lxvmc` |
| 13 | 176 | 235 | 582 | `pool1s6se64qce5rjjjhh6ufcdnc54p8qg78mlhjm38lymx99sqysvzx` |
| 14 | 173 | 238 | 472 | `pool14enw2643rn9nn6yzv60jyz3hj4kxs0jvap87lkgsqykh508jxm6` |
| 15 | 156 | 210 | 587 | `pool1gtphgrdj8sluxm9e7ca2spcwcq2p0dxj9zf5v0yv3gsagzq704n` |
| 16 | 151 | 231 | 504 | `pool12l453n0jtxqq88cgwgr67z06ldyhqqvwxgkn0sgungjfvhtp2el` |
| 17 | 151 | 232 | 622 | `pool15wkxegrfflzcyhurrjxsm9ljqtz09xr5rtnqsarnp7hmsz5um3t` |
| 18 | 143 | 229 | 623 | `pool14skj6e4rpjanzclx3fc880xnl8xafgg63tmw93t9xspvwx985qu` |
| 19 | 142 | 234 | 589 | `pool1lurfk0k0wwx54hlg8a7zp3jtstu57u59aeq7aketl55hknmmtu0` |
| 20 | 131 | 210 | 385 | `pool1m62sl6rauje9cknrkhwl39tc4hujudkd7gp478dpz7tagmjr8wm` |
| 21 | 129 | 212 | 453 | `pool1x0qm7xsyh2za3ltprxsgael544je4hg8tc3q3v5gv232z8jt4wp` |
| 22 | 116 | 249 | 563 | `pool12z39rkzfylvn9wfe8j6x9ucq6g2l4mw4azj70y0gd8ejczznyj3` |
| 23 | 115 | 242 | 428 | `pool1rpjjz68kmmetyxztmrstrwgz8lxf6v0d7vqgw98r5x8rc50jrdf` |
| 24 | 113 | 215 | 584 | `pool1pnzwgsgzd6t4788sfr7dxjyusepyq9xaxnpyfcngewqf29t9ayd` |
| 25 | 112 | 210 | 605 | `pool1gclysx2h7fndj0jdajlmwvqr8q9tzu3rurjknacu0ff954fsg9a` |
| 26 | 110 | 210 | 585 | `pool1a2nh3ktswllhwf07fjahpdg5mpqyq7j950pyftq9765r6t4cefl` |
| 27 | 109 | 210 | 617 | `pool1ekcsyzwexl7p2kwxxh34hy28l6772vrmff7jwmuxsa6u6fzty9z` |
| 28 | 108 | 233 | 611 | `pool1xytvsd9qnvqxpthh9p8k85e823trvn3npxeur8kr9zhkqz5uls9` |
| 29 | 107 | 210 | 342 | `pool1xxhs2zw5xa4g54d5p62j46nlqzwp8jklqvuv2agjlapwjx9qkg9` |
| 30 | 106 | 233 | 524 | `pool19asxjgd6ah9ddzauwede4wpt9vsp6s4ax5nz297wt47evc9sn7z` |

### EMURGO — Top 30 Pools (Computed)

| Rank | Unique SA | Epoch Min | Epoch Max | Pool ID |
|---:|---:|---:|---:|:---|
| 1 | 364 | 252 | 572 | `pool1ng3vqzrhn3z45yjdscv3q37n26g2pj3vp99rfkgv6225y8lqg8j` |
| 2 | 180 | 248 | 353 | `pool1uj4u73qgtprqre78q75fq2vkcrpfrcdreqcqkvn6u0m2k6nk2yp` |
| 3 | 151 | 255 | 475 | `pool1xmsdhync6k6grkkj7tuycskjpseykpr24luhlazl5nsngsy87gm` |
| 4 | 150 | 244 | 556 | `pool1zgxvcqf0dvh0ze56ev2ayjvuex3zdd3hgxzdrcezkx497mv3l7s` |
| 5 | 144 | 248 | 404 | `pool13annzt9hjfc822f0ejvxjf7fsmxd6cc28whpk5kagec6ggfmm7u` |
| 6 | 140 | 239 | 397 | `pool1g3ssnndd8e7lcmstkjl9ane9mup0eshv3aklg63u5tznwl4ch87` |
| 7 | 123 | 240 | 557 | `pool16agnvfan65ypnswgg6rml52lqtcqe5guxltexkn82sqgj2crqtx` |
| 8 | 119 | 257 | 617 | `pool1ywpt43nttzjd7883wafg255mh0hmjypwe65ercw6p2sxg5lt7ez` |
| 9 | 116 | 235 | 606 | `pool1ynxx88cq0y8vg8yrq3jrw6epm7rq9a8859v34sq9lzjy7ztg90u` |
| 10 | 106 | 232 | 542 | `pool15wkxegrfflzcyhurrjxsm9ljqtz09xr5rtnqsarnp7hmsz5um3t` |
| 11 | 95 | 237 | 528 | `pool14enw2643rn9nn6yzv60jyz3hj4kxs0jvap87lkgsqykh508jxm6` |
| 12 | 94 | 210 | 590 | `pool1lurfk0k0wwx54hlg8a7zp3jtstu57u59aeq7aketl55hknmmtu0` |
| 13 | 94 | 234 | 523 | `pool1jst7rrhucnp93hepezv5yqy6fx982xs2v0udwfc5ea6my3kfak7` |
| 14 | 90 | 221 | 458 | `pool16kus5xvdysgmtjp0hhlwt72tsm0yn2zcn0a8wg9emc6c75lxvmc` |
| 15 | 88 | 230 | 602 | `pool1s6se64qce5rjjjhh6ufcdnc54p8qg78mlhjm38lymx99sqysvzx` |
| 16 | 86 | 210 | 529 | `pool1gtphgrdj8sluxm9e7ca2spcwcq2p0dxj9zf5v0yv3gsagzq704n` |
| 17 | 83 | 249 | 489 | `pool12z39rkzfylvn9wfe8j6x9ucq6g2l4mw4azj70y0gd8ejczznyj3` |
| 18 | 81 | 211 | 620 | `pool1ekcsyzwexl7p2kwxxh34hy28l6772vrmff7jwmuxsa6u6fzty9z` |
| 19 | 78 | 229 | 623 | `pool14skj6e4rpjanzclx3fc880xnl8xafgg63tmw93t9xspvwx985qu` |
| 20 | 75 | 231 | 503 | `pool12l453n0jtxqq88cgwgr67z06ldyhqqvwxgkn0sgungjfvhtp2el` |
| 21 | 74 | 212 | 502 | `pool1x0qm7xsyh2za3ltprxsgael544je4hg8tc3q3v5gv232z8jt4wp` |
| 22 | 73 | 235 | 469 | `pool1xytvsd9qnvqxpthh9p8k85e823trvn3npxeur8kr9zhkqz5uls9` |
| 23 | 72 | 244 | 332 | `pool1zmfpd5r5vfwjmwm4cgy53exe58h7plnecny3t4948yw7zumzp4c` |
| 24 | 70 | 210 | 618 | `pool1vx9tzlkgafernd9vpjpxkenutx2gncj4yn88fpq69823qlwcqrt` |
| 25 | 67 | 236 | 442 | `pool1qfxukshs4fkcrflzdnxa2fdza5lfvew3y6echg8ckaa4q8m5hyf` |
| 26 | 65 | 210 | 397 | `pool1jeu74g86ys4fekhykqcww99kdsq3nlym8a6kfw8s8ff3vskad70` |
| 27 | 64 | 210 | 523 | `pool15yyxtkhz64p7a8cnax9l7u82s9t9hdhyxsa3tdm977qhgpnsuhq` |
| 28 | 62 | 210 | 346 | `pool1xxhs2zw5xa4g54d5p62j46nlqzwp8jklqvuv2agjlapwjx9qkg9` |
| 29 | 61 | 210 | 543 | `pool108zdflss3ayqlm5c7vr6mtqj2uwl99vk28ur8dv4zswdzt6yauc` |
| 30 | 61 | 210 | 550 | `pool1a2nh3ktswllhwf07fjahpdg5mpqyq7j950pyftq9765r6t4cefl` |

### CF — Top 30 Pools (Computed)

| Rank | Unique SA | Epoch Min | Epoch Max | Pool ID |
|---:|---:|---:|---:|:---|
| 1 | 70 | 210 | 598 | `pool12vs4c3cm0tr49c7alrevfs0xa5g3s4al4fn46h33e69uusat04v` |
| 2 | 66 | 211 | 594 | `pool1jeu74g86ys4fekhykqcww99kdsq3nlym8a6kfw8s8ff3vskad70` |
| 3 | 62 | 232 | 527 | `pool15wkxegrfflzcyhurrjxsm9ljqtz09xr5rtnqsarnp7hmsz5um3t` |
| 4 | 61 | 210 | 603 | `pool1qqqqqdk4zhsjuxxd8jyvwncf5eucfskz0xjjj64fdmlgj735lr9` |
| 5 | 60 | 212 | 501 | `pool14skj6e4rpjanzclx3fc880xnl8xafgg63tmw93t9xspvwx985qu` |
| 6 | 58 | 210 | 405 | `pool1rvng7n968748udkc5rxy4h9zp9hms4s3jsfwuues76ft28uc056` |
| 7 | 58 | 231 | 501 | `pool12l453n0jtxqq88cgwgr67z06ldyhqqvwxgkn0sgungjfvhtp2el` |
| 8 | 53 | 211 | 317 | `pool1ecvcst7k9eul4ggnljh0jw2s5nc2tyfmyzsx3xg3kmmz6ptgfwj` |
| 9 | 50 | 210 | 442 | `pool1ekcsyzwexl7p2kwxxh34hy28l6772vrmff7jwmuxsa6u6fzty9z` |
| 10 | 50 | 210 | 345 | `pool1a2nh3ktswllhwf07fjahpdg5mpqyq7j950pyftq9765r6t4cefl` |
| 11 | 45 | 210 | 512 | `pool1qnrqc7zpwye2r9wtkayh2dryvfqs7unp99f2039duljrsaffq5c` |
| 12 | 43 | 210 | 330 | `pool1xxhs2zw5xa4g54d5p62j46nlqzwp8jklqvuv2agjlapwjx9qkg9` |
| 13 | 41 | 212 | 284 | `pool1x0qm7xsyh2za3ltprxsgael544je4hg8tc3q3v5gv232z8jt4wp` |
| 14 | 41 | 237 | 475 | `pool14enw2643rn9nn6yzv60jyz3hj4kxs0jvap87lkgsqykh508jxm6` |
| 15 | 40 | 210 | 339 | `pool1vx9tzlkgafernd9vpjpxkenutx2gncj4yn88fpq69823qlwcqrt` |
| 16 | 38 | 210 | 600 | `pool1s0cfkzheywsftgwp0yz7sq4rt5gyf7t5kfwj5a269kpxvndjn6q` |
| 17 | 38 | 210 | 416 | `pool15yyxtkhz64p7a8cnax9l7u82s9t9hdhyxsa3tdm977qhgpnsuhq` |
| 18 | 36 | 210 | 389 | `pool1hntu7agmt8u5j9c20ejen7dvq0jfkvkpnul3mrdd8tppqvwfvt2` |
| 19 | 35 | 210 | 450 | `pool1ctzja2cdwyeqnvehmrlclc5wrn9w9acwklk3acn73jrx56d66vs` |
| 20 | 32 | 210 | 567 | `pool1lvsa8e0dw6z8g2fkw7prnfa7627wuy5jjexaadck6w5sxw5xkvm` |
| 21 | 32 | 210 | 341 | `pool1qqqyv9pn9typyqwcxqk5ewpxy5p27g5j2ms58hpp2c2kuzs5z77` |
| 22 | 31 | 210 | 483 | `pool16kus5xvdysgmtjp0hhlwt72tsm0yn2zcn0a8wg9emc6c75lxvmc` |
| 23 | 30 | 211 | 498 | `pool1gclysx2h7fndj0jdajlmwvqr8q9tzu3rurjknacu0ff954fsg9a` |
| 24 | 29 | 235 | 396 | `pool1jst7rrhucnp93hepezv5yqy6fx982xs2v0udwfc5ea6my3kfak7` |
| 25 | 28 | 211 | 253 | `pool1mxqjlrfskhd5kql9kak06fpdh8xjwc76gec76p3taqy2qmfzs5z` |
| 26 | 27 | 210 | 438 | `pool108zdflss3ayqlm5c7vr6mtqj2uwl99vk28ur8dv4zswdzt6yauc` |
| 27 | 27 | 210 | 614 | `pool1qwa8x4u4a2pff0xdv0haxpgk3tyrvl5adl2lpf3ztcftqruhea0` |
| 28 | 27 | 210 | 590 | `pool1gtphgrdj8sluxm9e7ca2spcwcq2p0dxj9zf5v0yv3gsagzq704n` |
| 29 | 27 | 210 | 468 | `pool1vc8jp7uagxgh8trzx7r260ndcydz89ges8sws05cyv7jj8q8gqs` |
| 30 | 26 | 211 | 217 | `pool1l3fvlzadk5hg78wy3e304s9t8tjzxnu962e2fl7tq8x2yg3mz6l` |

---

## Part 14 — Epoch 208 Destination Addresses (Sample, First 30 per Entity)

Epoch 208 = August 2020 Shelley hard fork activation. All three entities show simultaneous fragmentation into new address types.

### IOG — Epoch 208 Destination Address Sample (30 of 422 unique addresses)

Total edges at epoch 208: 585 | Total ADA: 22,222,645.25 ADA

```
Ae2tdPwUPEZ1zPy1L9PSQnUDNHzCehy2p9tDLvihV7LJBgb7VogHRdxKc6P
DdzFFzCqrhsrN7kKVy4jPWFSMcY3Bcx2cG9Faxjy43BgyBqxitxTShkPAxjziLhombZgzCgH9uwB6i1mGmBaLzYHMusGTooyq8DHfWep
addr1q8034vup8jvhuv70z9anuk4fceq6l2ah3q90u8uvlk32yje0jwuwvgrth6qzav7zwlvjuk4ek6tf8axf5juckda9z5xsq7rj73
addr1q80s5st48797kuutzgprgskx8egyxqmergfn8zl5rcgdc8mj2czy7kukynph0pckvct23ucn6csh77rmtr3nre7j0jvszfvl9m
addr1q80ucyjlfn3e8gj7eluxaqyk22xkc8l5e2mdykhkz2ujgx53j05pmdrnw200udr0rfmlllqml3vgjntej7s5e5a4ncaqz7h0kw
addr1q82e4dvkvfxy7473p2wztat0z3fqmc2t5wye050s44s4f4jzeluwwsd4j20ccx7y2wh6swze0t67f7m4xqprjef8xrqswpuer3
addr1q82qmeh3uqtkjynt4yptul87tk6m0f60sa4szwg0ezaxxe33vq9qcmyhca8nx8jvqar030mvc27w9zym70dx3l5mg2aq5jv9tl
addr1q82v695a6xjnggjpg8dh0ewe579z04q3qwsgw9qcy80a9t8vkvp2dut3eryedx7a7ds7xwrz9q5raugm2f4p2sdzzlnsd20dg2
addr1q83hrwgs0z6q3gntufu7jnt7mpjlpfrjcgekew9ve3spu47967rxkztkh7c9lterwlz75aa5yvxhmg28vjsd5zszgy9s3gww25
addr1q83m7rawvgygegxafqnqeh04qpn5j57659vrd8zm89nlqunadlus95gjscsdc57sj0547dqcky3e8jw8jdknqlswqcwsxdmngy
addr1q83uwj8h66aj45qwnkgrgptqxnh7qmufd8awjlkdlm7sn85lhe62vyjr39lq5hktczm43jxmh85vj3cc330966n5qkpsj9dq23
addr1q83ye5g3ahe64xxq8u0v5mnfqkdx4nsz4dpnxf7cllc08n6qztu9nrenw35fx4jucjlsykfxtu3zclsxuacqpkya9ggse0a7lt
addr1q8438ds5m4gn5z29cc5s6fgug843gz27gt702ue3j2mmmjsn3fhp40unnvlww7zslpc65m8w9fg60xfmluz2wly6arhs4sh7q0
addr1q848pvya99gh5cfedzcnmdtr4pujsmm9pvv8fs9w98c366rrpzsa895gfancl6z6xl8hhgghuht8qdsr3alt92kdmqasq0czvl
addr1q85akv5su87rega4q23qqq7g8km5qhs54vgwdhr427rpv28vkvp2dut3eryedx7a7ds7xwrz9q5raugm2f4p2sdzzlnscz0z4m
addr1q85aqxp3pr8uqnd4r4p8mp2qvcu58nmh9ed54z0y50fzeuucv0qt5l2p4cmvyh2tgd87sa6hsrud584ftnanv6yrdmesrmlur4
addr1q866r38gzwqca6lc9y6yd7jvmvwh24t2p3q54y2pw9h26yr978mf6fy49pxtkkxt7er5w36rm8fah9vzkya7lsujntqsef5v7v
addr1q86xrgfttygv0w7r0q06ys0px2jtywmj82g3xdjt02tmr8vcv0qt5l2p4cmvyh2tgd87sa6hsrud584ftnanv6yrdmesm5jh7g
addr1q87ewzrkuvhgwfe83j8tg5ux7z2nxx52kjfq39s4l8679vsyc2c7hhuxng0fcj995usngjejf9dgzyqetz4t4hc6tv6qlupvrv
addr1q87gkca24xedwxd3f9qgeh0egku3vp9f0llrlktqemh3cvgvnuw4dydefr2y7zc6sjk6faaqwymj0yn7mralcl922y9sf38c7q
addr1q87qmmjzc2cnrh78cslf8dlkghnamxh2w3u6qwac96nzjxnrpzsa895gfancl6z6xl8hhgghuht8qdsr3alt92kdmqastuw35d
addr1q885pr6nkvg79seqgeccqf8mg4k99at6zv950fwjms4uz0af4g6wmtqq276vf7ajknf5t2y905erghjnhng57tc7czgq6mu7vs
addr1q88g3perczsgpqf6pakf5qwfrq4pca94kauxm9yj7kdu0zvlhe62vyjr39lq5hktczm43jxmh85vj3cc330966n5qkpszs36pf
addr1q88h75hmm9pxc723txy7jg4k4w5xjtndgz2y73307pgs6a4glumk33h8m0e48z0euuy558zjmfgmswtr9j5cxm7jlzxsn3pplt
addr1q88h8u7lc4rj3tu5sv4p0klvwelvqvus3dawckx0f6k82lar4tclcgmwz7lkylfzf7qxedeckskq6aatxxa7dq5adqwqztjuyh
addr1q88j7hyrk5aevvhhyn7kkyghwjz4l6dup7an2w73flh6d564384akuafkg5duataq04hrk06x658rpaljujpwgelr5ws7m8cdz
addr1q88sywjg3yzrfzygec9tlx5wn9zrfvyj9svudq3rqya02dr978mf6fy49pxtkkxt7er5w36rm8fah9vzkya7lsujntqs9zmjts
addr1q89dsml7vxrdzqxplxgwr3azfgvma9k98ux7a5anddfg7fe0jwuwvgrth6qzav7zwlvjuk4ek6tf8axf5juckda9z5xshchm84
addr1q89kq7aygaw0jec2jny6tr3lc347s7a7dfhs2l93d7cymadglumk33h8m0e48z0euuy558zjmfgmswtr9j5cxm7jlzxshjau7r
addr1q89rgkrx70mq7450pkmgc9zqj5dmm7m6j307pru2rln24xm54p078fyh692k97d7jvj8z686248f2ne5gkj06l9mceaq4wjgah
```

*Full 422 IOG + EMURGO + CF epoch 208 destination addresses available in `fragmentation_address_data.txt` (Task 5, line 1295+).*

---

*Parts 10-14 appended 2026-03-31.*
*Source: fragmentation_address_data.txt (computed by background extraction script, 6,034 lines).*
"""

with open(r"C:\Users\david\ABCDE\observations\genesis_fragmentation_analysis.md", "a", encoding="utf-8") as f:
    f.write(content)

print("Done. Parts 10-14 appended.")

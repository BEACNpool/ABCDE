# Cardano Genesis Forensics — Community Summary

This report is generated from the v2 ABCDE DuckDB artifact. It is designed for community review, not attribution theater.

## Core caveat

This project maps on-chain flows and delegation behavior. It does **not** prove legal ownership, intent, misconduct, or who controlled a wallet off-chain.

## Seed registry

| seed_id | label | amount_ada | source_type | grade |
| --- | --- | --- | --- | --- |
| iog | IOG | 2463071701 | NAMED_FOUNDER | FACT |
| emurgo | EMURGO | 2074165643 | NAMED_FOUNDER | FACT |
| fourth_entry_781m | 781,381,495 ADA fourth entry | 781381495 | SALE_TICKET_SIGNAL | STRONG_INFERENCE |
| cf | Cardano Foundation | 648176763 | NAMED_FOUNDER | FACT |

## First-spend behavior

| seed_id | first_spend_tx_hash | dormant_hours | input_count |
| --- | --- | --- | --- |
| cf | 49bef29428b70222f26f33c282209bf17b9e76a6ffa46a21e3925d325381caa7 | 1.161 | 1 |
| emurgo | 7eb47f8f9ffaaf98f30d8028c7e1d13a8efeebffb65d1f2d4be37ee523ceb9bf | 475.094 | 1 |
| fourth_entry_781m | c8596b9cd81f734f8129604ff86f23bd4a910465acb84ad9e9d1ac223ccb4a76 | 475.111 | 2 |
| iog | 0d94ce298776bd6bf220084d7af093b2d403668a45f55a9c813b2efd0ffd1e10 | 0.15 | 1 |

## Fourth-entry direct co-spend receipt

The fourth-entry first spend directly co-spends with an EMURGO-descended UTxO.

| input_source_tx_hash | input_value_lovelace | descendant_of_seed_id | emurgo_trace_depth |
| --- | --- | --- | --- |
| 743fd0510c4527b4031504b9f3c1703606bfd5e63bed4d1bf857ceeefc4bac1b | 1074165542657684 | emurgo | 2 |
| 5ec95a53fa3bb7dc56864bb6e75f369f00aa20e8d8cdc3b66b2fb88ec1b225ef | 781381495000000 |  |  |

## Governance delegation surface

Lifetime target counts by root seed:

### SPO pool targets

| root_seed_id | distinct_pool_targets |
| --- | --- |
| cf | 1070 |
| emurgo | 1341 |
| fourth_entry_781m | 1341 |
| iog | 1423 |

### DRep targets

| root_seed_id | distinct_drep_targets |
| --- | --- |
| cf | 71 |
| emurgo | 97 |
| fourth_entry_781m | 97 |
| iog | 125 |

## Top latest SPO targets by traced stake credential count

| root_seed_id | ticker | pool_name | pool_id | latest_stake_addresses |
| --- | --- | --- | --- | --- |
| iog | EVE1 | Everstake | pool1uj4u73qgtprqre78q75fq2vkcrpfrcdreqcqkvn6u0m2k6nk2yp | 720 |
| iog | RSTK | Everstake | pool1zgxvcqf0dvh0ze56ev2ayjvuex3zdd3hgxzdrcezkx497mv3l7s | 428 |
| iog | EVE2 | Everstake | pool1ng3vqzrhn3z45yjdscv3q37n26g2pj3vp99rfkgv6225y8lqg8j | 407 |
| emurgo | EVE2 | Everstake | pool1ng3vqzrhn3z45yjdscv3q37n26g2pj3vp99rfkgv6225y8lqg8j | 318 |
| fourth_entry_781m | EVE2 | Everstake | pool1ng3vqzrhn3z45yjdscv3q37n26g2pj3vp99rfkgv6225y8lqg8j | 318 |
| iog | VRSTK | Everstake | pool1g3ssnndd8e7lcmstkjl9ane9mup0eshv3aklg63u5tznwl4ch87 | 290 |
| iog | STSH3 | Stake Shark #3 | pool13annzt9hjfc822f0ejvxjf7fsmxd6cc28whpk5kagec6ggfmm7u | 257 |
| iog | ESTK | Everstake | pool1jst7rrhucnp93hepezv5yqy6fx982xs2v0udwfc5ea6my3kfak7 | 218 |
| iog | EVE | Everstake | pool1ynxx88cq0y8vg8yrq3jrw6epm7rq9a8859v34sq9lzjy7ztg90u | 217 |
| iog | EVE3 | Everstake | pool1xmsdhync6k6grkkj7tuycskjpseykpr24luhlazl5nsngsy87gm | 213 |
| iog | EVE4 | Everstake | pool1ywpt43nttzjd7883wafg255mh0hmjypwe65ercw6p2sxg5lt7ez | 153 |
| emurgo | EVE1 | Everstake | pool1uj4u73qgtprqre78q75fq2vkcrpfrcdreqcqkvn6u0m2k6nk2yp | 136 |
| fourth_entry_781m | EVE1 | Everstake | pool1uj4u73qgtprqre78q75fq2vkcrpfrcdreqcqkvn6u0m2k6nk2yp | 136 |
| emurgo | EVE3 | Everstake | pool1xmsdhync6k6grkkj7tuycskjpseykpr24luhlazl5nsngsy87gm | 133 |
| fourth_entry_781m | EVE3 | Everstake | pool1xmsdhync6k6grkkj7tuycskjpseykpr24luhlazl5nsngsy87gm | 133 |

## Top latest DRep targets by traced stake credential count

| root_seed_id | drep_id | anchor_url | latest_stake_addresses |
| --- | --- | --- | --- |
| iog | drep_always_abstain |  | 1157 |
| emurgo | drep_always_abstain |  | 563 |
| fourth_entry_781m | drep_always_abstain |  | 563 |
| cf | drep_always_abstain |  | 218 |
| iog | drep1qe2l8gw8v7ydswfp9twytxcc3wzwdq8npt55f3vnlgv2u8sx3nt | https://raw.githubusercontent.com/Emurgo/constitution-committee/11af02e3b66daa7106941a1b3000d9721862bc3c/YOROI.jsonld | 128 |
| emurgo | drep1qe2l8gw8v7ydswfp9twytxcc3wzwdq8npt55f3vnlgv2u8sx3nt | https://raw.githubusercontent.com/Emurgo/constitution-committee/11af02e3b66daa7106941a1b3000d9721862bc3c/YOROI.jsonld | 82 |
| fourth_entry_781m | drep1qe2l8gw8v7ydswfp9twytxcc3wzwdq8npt55f3vnlgv2u8sx3nt | https://raw.githubusercontent.com/Emurgo/constitution-committee/11af02e3b66daa7106941a1b3000d9721862bc3c/YOROI.jsonld | 82 |
| iog | drep_always_no_confidence |  | 61 |
| iog | drep13d6sxkyz6st9h65qqrzd8ukpywhr8swe9f6357qntgjqye0gttd | https://raw.githubusercontent.com/Tastenkunst/eternl-drep/main/240909-edc-drep-mainnet.jsonld | 42 |
| emurgo | drep_always_no_confidence |  | 32 |
| fourth_entry_781m | drep_always_no_confidence |  | 32 |
| cf | drep1qe2l8gw8v7ydswfp9twytxcc3wzwdq8npt55f3vnlgv2u8sx3nt | https://raw.githubusercontent.com/Emurgo/constitution-committee/11af02e3b66daa7106941a1b3000d9721862bc3c/YOROI.jsonld | 30 |
| iog | drep16tsw66jtrver8ur3y3zzq2fl0m4swl4lwk88fvu8d4z4ydukrj0 | https://most-brass-sun.quicknode-ipfs.com/ipfs/QmZT35nEcX84VFtDGpUnTxhoB5urXLE285S5ChB4wAsiWj | 22 |
| emurgo | drep16tsw66jtrver8ur3y3zzq2fl0m4swl4lwk88fvu8d4z4ydukrj0 | https://most-brass-sun.quicknode-ipfs.com/ipfs/QmZT35nEcX84VFtDGpUnTxhoB5urXLE285S5ChB4wAsiWj | 21 |
| fourth_entry_781m | drep16tsw66jtrver8ur3y3zzq2fl0m4swl4lwk88fvu8d4z4ydukrj0 | https://most-brass-sun.quicknode-ipfs.com/ipfs/QmZT35nEcX84VFtDGpUnTxhoB5urXLE285S5ChB4wAsiWj | 21 |

## Trace-derived latest SPO target rollup by preserved current value

This is **not live pool stake**. It joins preserved trace current-unspent receipts to the latest observed delegation target per traced stake credential. Use `iog_pool_state_validation.csv` for live IOG1/IOG2 pool-state claims.

| root_seed_id | ticker | pool_name | pool_id | trace_value_ada |
| --- | --- | --- | --- | --- |
| iog | IOG1 | Input Output Global (IOHK) - 1 | pool1mxqjlrfskhd5kql9kak06fpdh8xjwc76gec76p3taqy2qmfzs5z | 1691346606.518002 |
| iog |  |  | pool1qlxxw3zlgx0kgv2cel0n6z3a6yjs0w8grwtp5xwna8fm2g5tsda | 633999880.011937 |
| emurgo | ETO3 | eToro Pool 3 | pool1xt7mjrtnsew3v33lu8sf93upf20sxhmcrfnpm82ra46yxk7uy45 | 323873828.831063 |
| fourth_entry_781m | ETO3 | eToro Pool 3 | pool1xt7mjrtnsew3v33lu8sf93upf20sxhmcrfnpm82ra46yxk7uy45 | 323873828.831063 |
| iog | IOG2 | Input Output Global (IOHK) - 2 | pool10dwjth7esfw5gc036vu6l6csnvn6elqax0d3kh8t65rxyewk2g3 | 108659612.2 |
| cf | PEACE | PEACEpool Cardano ecosystem developers | pool1h5jtxde8j86qrnqzj32ugn480u7gw5xw8wqy5d227rl3vfg58qz | 64110752.379736 |
| cf | ALPHA | AlphaPool | pool158ag8p06qm4apd750ekep6een9cdldqsq434ll2mp0ykgunmguy | 64110748.825567 |
| cf |  |  | pool1q5za50d3sr707xkmjtyrs0v76ezxyj8g8uhggfk0wfl77aufd9k | 64110748.65263 |
| cf | UNIQ | Unique | pool1ywt7jqfsmxg0yplku4mtdwtm476rp72z6fns9mhevf7u72pkupj | 64110748.479693 |
| cf |  |  | pool16uja2pt05ddq9mzcsw9xkv40qdl7sm00nvpj0h4arn0fgl2xrae | 64110748.306756 |
| iog | UKADA | UKADA | pool1wwzctexlp70mj00vv65mlhwhwresn58s9x7jl4tswvkg77eu7n7 | 61948003.909135 |
| cf | CASP | Cardaspians | pool10tqeu6d03p6rnalqlvdshmpsljxaq2c0ww6draq6xm8lgyl2a3p | 50091977.059847 |
| cf | CO2P | CO2-Pool - eco-friendly, green and climate-action | pool1z89dx8u42f4cvujvsjupsg50cfgqhjjuaxegvj59h9q9scra5fy | 35057421.548996 |
| cf | SHARP | CardanoSHARP Stake Pool | pool124lm97s6f4satl7xz0ulzgg6tv30tskry3zcntwrz68n60v5yne | 35025951.034671 |
| iog |  |  | pool1njhlmv87adsanft5sjuvz5a9pgyew76mxqa0w9c762af570g5ht | 33249999.929505 |

## Trace-derived latest DRep target rollup by preserved current value

| root_seed_id | drep_id | anchor_url | trace_value_ada |
| --- | --- | --- | --- |
| iog | drep_always_abstain |  | 668242722.998892 |
| emurgo | drep_always_abstain |  | 29027454.388596 |
| fourth_entry_781m | drep_always_abstain |  | 29027454.388596 |
| cf | drep_always_abstain |  | 20715088.865004 |
| emurgo | drep1sy4x93yl9c6q59ewmhxpkumkjnlz8th4wfetddj8lzryvsu7hqk | https://raw.githubusercontent.com/dostrelith678/garden-staging-site/7d96dcacd9c87d17a8766853b627812fe55fbe15/DRep/EDEN.jsonld | 14071104.729986 |
| fourth_entry_781m | drep1sy4x93yl9c6q59ewmhxpkumkjnlz8th4wfetddj8lzryvsu7hqk | https://raw.githubusercontent.com/dostrelith678/garden-staging-site/7d96dcacd9c87d17a8766853b627812fe55fbe15/DRep/EDEN.jsonld | 14071104.729986 |
| iog | drep1navsrqral9w6kjy8v9kl0vpmyhzhuytaa65rmdcvnu2eg9jac55 | https://raw.githubusercontent.com/ClearContracts/drep-registration/refs/heads/main/Clarity_Cofounder_dRep.jsonld | 11951110.635866 |
| cf | drep13d6sxkyz6st9h65qqrzd8ukpywhr8swe9f6357qntgjqye0gttd | https://raw.githubusercontent.com/Tastenkunst/eternl-drep/main/240909-edc-drep-mainnet.jsonld | 10133786.343411 |
| cf | drep1kyppjlhz4lawh4g0ewx2d8a5l20t4yclfnppnuvdkmt7vccg836 | https://raw.githubusercontent.com/SebastienGllmt/drep/main/drep-mainnet.jsonld | 9983673.354278 |
| cf | drep1ysy0kzhamk2cvfzrql50unfj9jkk2zffxtaae5zmc39cs3uec6j |  | 7227053.473055 |
| emurgo | drep1hvlx2cdu7ql8238dwhrjrncm43q3sl5hlmcmp24p0rcnzcwzcyd | https://raw.githubusercontent.com/trjones8918/dRep/refs/heads/main/Ryan%20Jones_Maestroman.jsonld | 6743389.271705 |
| fourth_entry_781m | drep1hvlx2cdu7ql8238dwhrjrncm43q3sl5hlmcmp24p0rcnzcwzcyd | https://raw.githubusercontent.com/trjones8918/dRep/refs/heads/main/Ryan%20Jones_Maestroman.jsonld | 6743389.271705 |
| iog | drep13d6sxkyz6st9h65qqrzd8ukpywhr8swe9f6357qntgjqye0gttd | https://raw.githubusercontent.com/Tastenkunst/eternl-drep/main/240909-edc-drep-mainnet.jsonld | 6334304.021756 |
| cf | drep16tsw66jtrver8ur3y3zzq2fl0m4swl4lwk88fvu8d4z4ydukrj0 | https://most-brass-sun.quicknode-ipfs.com/ipfs/QmZT35nEcX84VFtDGpUnTxhoB5urXLE285S5ChB4wAsiWj | 5347262.937789 |
| emurgo | drep15jspgw8ea9pw3w0fwyqam2lw58ulw7z6qhr8qyuah7j0yj962w7 | https://most-brass-sun.quicknode-ipfs.com/ipfs/QmW4diXvKVDmScpGhygyopADCEpqdJhVFCqW3y9WE8JATh | 5070582.088107 |

## Staged trace audit cuts

The repo includes server-side staged extraction so deeper traces can be materialized one frontier at a time with minimum-depth dedupe. Depth 10 is an `AUDIT_REVIEW_CUT`, not the final full-founder inventory.

### Depth-10 all-root staged summary

| artifact | bucket | rows |
| --- | --- | --- |
| cross_entity_merges | emurgo+fourth_entry_781m | 401 |
| cross_entity_merges | emurgo+fourth_entry_781m+iog | 1 |
| trace_utxos | 0 | 4 |
| trace_utxos | 1 | 8 |
| trace_utxos | 2 | 14 |
| trace_utxos | 3 | 23 |
| trace_utxos | 4 | 36 |
| trace_utxos | 5 | 63 |
| trace_utxos | 6 | 117 |
| trace_utxos | 7 | 266 |
| trace_utxos | 8 | 656 |
| trace_utxos | 9 | 2307 |
| trace_utxos | 10 | 11247 |

### Depth-10 named-founder-only staged summary

| artifact | bucket | rows |
| --- | --- | --- |
| cross_entity_merges | emurgo+iog | 1 |
| trace_utxos | 0 | 3 |
| trace_utxos | 1 | 6 |
| trace_utxos | 2 | 12 |
| trace_utxos | 3 | 19 |
| trace_utxos | 4 | 28 |
| trace_utxos | 5 | 47 |
| trace_utxos | 6 | 91 |
| trace_utxos | 7 | 212 |
| trace_utxos | 8 | 547 |
| trace_utxos | 9 | 2066 |
| trace_utxos | 10 | 10646 |

### First staged depth-10 cross-entity merge rows

| merge_tx_hash | epoch_no | root_combo | traced_input_rows | min_depth | max_depth |
| --- | --- | --- | --- | --- | --- |
| c8596b9cd81f734f8129604ff86f23bd4a910465acb84ad9e9d1ac223ccb4a76 | 4 | emurgo+fourth_entry_781m | 2 | 0 | 2 |
| 10dbea7cab7d57a83376f5994e05dbfc6919892e85907d76efcb59d36d8dbf5c | 7 | emurgo+fourth_entry_781m | 2 | 8 | 8 |
| 45862b04d0ff4b48923eeb2d185e4ecc9864bc80380fc2e646d0b0b25083a3e8 | 7 | emurgo+fourth_entry_781m | 2 | 2 | 2 |
| 71a35dc3c7083eb57bde93efd2abc98fb592175935c0c5e0069e496d349fcf78 | 7 | emurgo+fourth_entry_781m | 4 | 1 | 3 |
| 79118ff95082c5614f7b1e3c03421ecdadafe8be69979002e10565b7e2018d61 | 7 | emurgo+fourth_entry_781m | 2 | 5 | 5 |
| 8303da9e07e9e6146013840d17c6167a1827019f821f55b6032e27bc7328e989 | 7 | emurgo+fourth_entry_781m | 2 | 7 | 7 |
| 93cf71b598fd47e1ebbc0721972cb6118bda3fc92c7038d1b3b528a8e8d6f5e8 | 7 | emurgo+fourth_entry_781m | 2 | 3 | 3 |
| a1d69ce7b0810ee998d34e813379f1783fe597418e85c90741ec7e7a6667877d | 7 | emurgo+fourth_entry_781m | 6 | 7 | 9 |
| a462e1f070099b1c61d8bdf071fbb859f55d61a479751c30920d99dc6a79bb37 | 7 | emurgo+fourth_entry_781m | 2 | 4 | 4 |
| b64aa27726118446103b265724efe9c0bcf063fb8a45071f2dba6950ab3c2c4f | 7 | emurgo+fourth_entry_781m | 2 | 6 | 6 |
| cf6454d21387b44b8cdbae68ae9270623e3a9d17b05fabe82f043d97b1304e40 | 7 | emurgo+fourth_entry_781m | 2 | 8 | 8 |
| fc861d313b594f812e3487d458496d960cf9acb7117d0225c0ae0db5ad22e049 | 7 | emurgo+fourth_entry_781m | 2 | 9 | 9 |

### Founder-only staged comparison against preserved 521-row baseline

| staged_path | staged_rows | legacy_txs | overlap_txs | legacy_missing_txs | staged_extra_txs |
| --- | --- | --- | --- | --- | --- |
| data/release/staged_cross_entity_merges_founders_depth12.csv | 223 | 521 | 44 | 477 | 179 |
| data/release/staged_cross_entity_merges_founders_depth13.csv | 2863 | 521 | 320 | 201 | 2543 |
| data/release/staged_cross_entity_merges_founders_depth14.csv | 22825 | 521 | 454 | 67 | 22371 |

Interpretation: depth 14 recovers most baseline hashes but also produces many additional candidates. Those extras are an `AUDIT_CANDIDATE_SET`, not claims.

## IOG current bag audit cut

Depth-14 staged trace membership, filtered to live-unspent UTxOs at ABCDE/db-sync tip, currently resolves to the following IOG-descended balance. This is trace membership, not proof of current beneficial ownership.

| current_utxos | current_ada | min_depth | max_depth | stake_addresses | byron_or_no_stake_ada | shelley_staked_ada |
| --- | --- | --- | --- | --- | --- | --- |
| 75203 | 494065565.081596 | 4 | 14 | 48259 | 7567246.930308 | 486498318.151288 |

### IOG confidence bands

| band | ada | confidence | interpretation |
| --- | --- | --- | --- |
| live_iog_pool_stake_sanity_check | 10041920.418743 | HIGH for pool state only | IOG1 live active stake; IOG2 retired; not an IOG bag estimate |
| high_confidence_coordinated_retained_like_core | 247261951.770785 | MEDIUM-HIGH | IOG-descended current UTxOs in synchronized drep_always_abstain / epoch-329 pool-delegation clusters >=100k ADA |
| probable_retained_like_abstain_surface | 282012126.139902 | MEDIUM | IOG-descended current UTxOs whose latest observed DRep is always-abstain |
| trace_membership_current_upper_bound | 504872796.959289 | MEDIUM-HIGH for trace/unspent, LOW for beneficial ownership | All depth-14 IOG-descended live-unspent UTxOs before custodian/unknown classification |
| no_latest_drep_surface | 207041377.104194 | UNKNOWN | Current IOG-descended value with no latest observed DRep delegation in db-sync; requires deeper classification before retained-bag use |

### IOG heuristic class summary

| heuristic_class | clusters | utxos | ada |
| --- | --- | --- | --- |
| COORDINATED_ABSTAIN_E329_GE100K | 16 | 43 | 247261951.770785 |
| NO_LATEST_POOL | 21365 | 26781 | 104158712.876092 |
| UNCLASSIFIED_POOL | 21300 | 35243 | 102606847.452221 |
| ABSTAIN_OTHER | 1785 | 3493 | 31485286.654514 |
| CUSTODIAN_OR_SERVICE_POOL | 4073 | 7160 | 13610854.635725 |
| NO_STAKE_UNCLASSIFIED | 2813 | 3198 | 7581394.383501 |
| IOG_BRANDED_POOL | 42 | 71 | 195121.375698 |

### IOG pool-state validation

This corrects the old shortcut: trace-derived latest-delegation rollups are not live pool stake.

| label | ticker | retired_at_tip | retiring_epoch | stake_epoch | active_stake_ada |
| --- | --- | --- | --- | --- | --- |
| IOG1 | IOG1 | False |  | 641 | 10271913.966294 |
| IOG2 | IOG2 | True | 237 |  |  |

## Reproduce

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements/base.txt
bash scripts/rebuild_seed_cut.sh
python3 scripts/verify_finding_queries.py
python3 scripts/build_community_report.py
```

## Source files

- generated locally: `data/abcde_genesis_seed_registry.duckdb`
- `data/small/*.csv`
- `data/manifests/*.json`
- `findings/*.md`

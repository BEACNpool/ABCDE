# Starter Questions

Grounded example questions for the genesis ADA database. Ask them through the
MCP server (in Claude Desktop / Claude Code) or with `python ask.py "..."`.
Every answer should carry an evidence grade (FACT / STRONG_INFERENCE /
WORKING_HYPOTHESIS / UNKNOWN) and cite the tables used — see `docs/02_GRADING.md`.

## Seeds and named founders

- Which named founder entities are in the `seeds` table, and how much genesis ADA did each receive?
- What is the evidence grade attached to the fourth genesis entry (the 781,381,495 ADA entry)?
- What are the first-spend transactions for each genesis seed?

## Where the genesis ADA went

- Where did EMURGO's genesis ADA end up — which SPOs and DReps does the bounded trace reach?
- Where did IOG's genesis ADA flow, by trace depth?
- Which cross-entity merges appear between founder seeds in the staged trace?

## IOG current bag

- How much IOG-descended ADA is still unspent, and what are the confidence bands?
- Which IOG depth-14 current UTxOs are largest, and what are their exact creation epochs/blocks/times?
- What are the top stake holders in the IOG depth-14 current bag, and how are they classified?
- Is there a coordinated-abstain cluster in the IOG current bag around epoch 329?

## Relay health and pool infrastructure

Bound by `docs/27_RELAY_HEALTH_METHOD.md`. Registration is FACT; reachability is
an OBSERVATION from one vantage point at one moment, and is never a verdict on a
pool. `unreachable` is not `offline`.

- How many current pools registered no relay at all, and how much stake is delegated to them (`relay_pool_health`)?
- Which relay endpoints are advertised by the most pools, and how much stake sits behind each (`relay_shared_endpoints`)?
- Which pools registered a single relay endpoint, ranked by stake?
- How many pools had at least two distinct reachable hosts in the last sweep, and how many had none?
- Which pools share a resolved relay host despite registering different hostnames (`relay_shared_hosts`)?
- Which registered endpoints failed to resolve in DNS at all (`relay_endpoint_status`)?
- How does a pool's relay registration compare with its KES-rotation operator cluster (`pool_operator_kes_clusters`)?

## Control indicators and custody patterns

- Which genesis-descended stake addresses score HIGH on `fe_control_consistency`, and which signals drive each score?
- How much genesis-descended ADA sits with stake keys whose rewards have never been withdrawn?
- Which certificate transactions certified 3+ genesis-descended stake keys at once (`genesis_control_cert_cohorts`), and what grade of linkage is that?
- Which stake keys show recent certificate activity while their principal has not moved in 2+ years?

## Exchange tracers

- Which exchanges are named in the on-chain tracer deposit claims, and how many transactions name each?
- Which addresses received the most tracer NFTs and swept them onward (`tracer_address_summary`, `tracer_transfer_edges`)?
- Where do the 505 tracer NFTs currently sit, and which stake keys consolidate the most of them?

## Freshness and accuracy

- How fresh is each table I am about to cite (`data_freshness_catalog`, `db_tip_receipt`), and which of them are snapshot-sensitive?

## IOGP and voucher-address follow-up

- Was the IOGP pool's registered pledge 64M ADA, or was that its reward credential's active stake?
- Which on-chain flows connect the cited voucher-program address to previously identified endpoints?
- What do the deterministic dominant-input paths establish, and what provenance claims remain unsupported?

## Governance: DReps and SPOs

- Did EMURGO actually remove genesis ADA from its DRep, and how much is left there?
- Which DReps hold the most genesis-traced stake?
- Which stake pools (SPOs) received the most genesis-descended delegation?
- For the top DReps, what is their genesis trace exposure by root seed, and how sticky is it?
- How do the top DReps' delegations break down by stake age bucket?
- Do the top-DRep numbers cross-check against Koios?

## Genesis-to-DRep behavior surface

- What does `build_info` say about the db tip and freshness of this snapshot?
- Which DReps receive the most depth-14 founder-traced voting power by behavior class?
- Which stake-credential clusters have the strongest public behavior signals?
- Which proposal-vote rows have the largest genesis-traced exposure by vote choice?
- How much of each root seed's traced current value is delegated to each DRep behavior class?

## Genesis-to-SPO delegation surface

- Which stake pools receive the most founder-traced current value, and what are their tickers?
- How much traced current value is not delegated to any pool at all?
- Which pool/DRep combinations hold the most traced value (`governance_genesis_pool_drep_matrix`)?
- Which pools have an owner or reward address that is itself trace-reached, and at what minimum depth (`governance_genesis_pool_operator_links`)?
- Which governance actions were enacted, and which proposal types appear most (`governance_actions_catalog`)?

## Tips

- Call `list_tables()` first, then `describe_table(name)` on anything relevant,
  before writing SQL.
- Value-weighted rollups live in `governance_*_latest_value_targets`; count-based
  rollups live in `governance_*_delegation_targets`.
- Behavior-score rollups live in `governance_genesis_behavior_*`; the committed
  signal table is a top cut, with the full table intended for release assets.
- The fourth seed's internal legacy label was "EMURGO_2" — this is **not** an
  ownership attribution; treat it as a STRONG_INFERENCE sale-ticket signal.
- For the IOGP/voucher follow-up, start with `iogp_pool_registration`,
  `iogp_pool_epoch_stake`, `voucher_wallet_profile`, and
  `voucher_wallet_counterparty_summary`; use the report for method limits.

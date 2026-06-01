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

## Governance: DReps and SPOs

- Which DReps hold the most genesis-traced stake?
- Which stake pools (SPOs) received the most genesis-descended delegation?
- For the top DReps, what is their genesis trace exposure by root seed, and how sticky is it?
- How do the top DReps' delegations break down by stake age bucket?
- Do the top-DRep numbers cross-check against Koios?

## Tips

- Call `list_tables()` first, then `describe_table(name)` on anything relevant,
  before writing SQL.
- Value-weighted rollups live in `governance_*_latest_value_targets`; count-based
  rollups live in `governance_*_delegation_targets`.
- The fourth seed's internal legacy label was "EMURGO_2" — this is **not** an
  ownership attribution; treat it as a STRONG_INFERENCE sale-ticket signal.

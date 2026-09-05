# Founder accountability: evidence and open questions

**Purpose:** make the important records easy to inspect, reproduce and challenge.
This guide covers concentrated governance influence, overlapping institutional
roles, large fund movements and wallet-incident accountability involving
Cardano's founding organizations. Readers should be able to test concerns about
abuse or fraud without treating the concern itself as the conclusion.

The three named founding organizations are Input Output (IO/IOG/IOHK in
historical material), EMURGO and the Cardano Foundation (CF). The separate
781,381,495 ADA genesis entry is **not a fourth established founder allocation**;
its beneficial owner remains unresolved.

A plain clone includes compact CSV evidence and a DuckDB database. It does not
include the full chain, all of the maintainer's warehouse, private research
notes or the full-resolution version of every historical trace.

## What the September 5 cut shows

These are **FACT** claims within the committed rows and their stated scope.
Governance distribution is **epoch 653**; the exact vote-extraction block and
time are in [`founding_chain_tip.csv`](../data/small/founding_chain_tip.csv).

| Observation | Result | Reproduce / interpretation boundary |
|---|---:|---|
| EMURGO DRep delegated voting power | 301,958,521.565201 ADA | [Voting-power query](../sql/35_founding_entities/04_delegated_voting_power.duckdb.sql); delegated influence, not an owned balance. |
| Yoroi DRep delegated voting power | 469,671,268.300191 ADA | Same query. Their combined represented power is 771,629,789.865392 ADA; affiliation is documented separately from delegation. |
| CF DRep delegated voting power | 164,748,353.912119 ADA | Same query, preserving the official script credential's identity. This does not include every community DRep to which CF may delegate. |
| EMURGO / Yoroi latest valid choices | 140 matches / 142 shared actions; 0 opposing Yes/No votes | [Pair query](../sql/35_founding_entities/02_vote_pair_agreement.duckdb.sql). Includes explicit Abstain as a choice; no inference about absent ballots. |
| CF / EMURGO latest valid choices | 87 matches / 142 shared actions; 9 opposing Yes/No votes | [Disagreement query](../sql/35_founding_entities/03_vote_disagreements.duckdb.sql). The 55 nonmatching choices include Abstain differences as well as direct opposition. |
| Selected historical parcel cohort | 14 credentials; 489,541,253.993397 ADA of epoch stake | [Cohort query](../sql/35_founding_entities/06_cohort_current_delegation.duckdb.sql). Latest recorded vote-delegation certificates all name always-abstain. This is neither a current UTxO balance nor the full F15 graph. |
| Voucher-related reserve-credit transaction | 318,199,980 ADA credited across 6 rows | [Reserve query](../sql/35_founding_entities/07_reserve_credit_receipt.duckdb.sql). Historical chain credit, not proof of every later use or recipient. |

The cut includes **453 raw ballot rows**, resolving to **432 latest valid
DRep/proposal choices**, and **155 proposal records**. Readers can inspect
revisions, rationales, action types and recorded outcomes.
The extraction selects three identified DReps; it does not measure every form
of institutional influence or determine wrongdoing.

## What to inspect first

| Question | Public evidence | What it establishes / what it leaves open |
|---|---|---|
| How much formal voting influence do named founder-related DReps have? | `founding_drep_identity`, `founding_drep_distribution`, `founding_votes`, `founding_proposals` | Published identity evidence, epoch-specific delegated voting power, ballots and recorded proposal lifecycle. DRep delegation is not custody or beneficial ownership of the ADA. |
| Are affiliated DReps voting together? Are all founders one bloc? | Latest valid ballots in `founding_votes`, paired by proposal transaction hash and action index | Agreement, abstention and disagreement rates over shared actions. Missing votes are not Abstain. Matching choices do not alone establish an agreement, motive or concealed coordination. |
| Do organizations vote on their own institutional roles or funding? | `founding_votes`, `founding_proposals`, original disclosures in `founding_public_sources` | A ballot and proposal can show an overlapping role. Procurement records, conflict policies, recusal decisions and independent review are needed to assess its handling. |
| What happened to the separate 781M entry? | `founding_early_merge_inputs`, `founding_early_merge_outputs`; [F02b](../findings/F02b_fourth_entry_direct_cospend.md), [F03](../findings/F03_fourth_entry_sale_ticket_origin_signal.md) | Direct early co-spend with a depth-2 EMURGO-descended input and a separate historical sale-ticket signal. The buyer, custodian and legal owner are not identified by those facts. |
| What can be checked about voucher assets and development funding? | `founding_reserve_credits`; [F09](../findings/F09_iogp_voucher_followup.md); report and contract sources in `founding_public_sources` | The reserve-credit transaction is independently queryable. Later recipient, purpose, approval and delivery assertions require their own evidence; one chain credit does not verify the report's entire narrative. |
| What do the repeated large parcels and reward sweeps show? | `founding_cohort_keys`, `founding_cohort_stake`; [F11](../findings/F11_eight_key_35m_custody_cohort.md), [F13](../findings/F13_reward_plumbing_downstream_and_tracer_bridge.md), [F15](../findings/F15_plumbing_component_is_closed_floor.md) | A selected historical key set, its published linkage method and refreshed epoch stake. Common custody tooling remains an alternative to a single beneficial owner; the operator is not identified. |
| What is known about recurring large payments? | [F10](../findings/F10_genesis_trail_monthly_stream.md), `genesis_trail_*`, [worked case](../reports/genesis_trail_case.md) | Payment outputs, forwarding and one deterministic largest-input path are reproducible. Gross throughput is not a balance; a selected path does not allocate every input's economic provenance. Recipient and contractual purpose remain open. |
| What failed in SecondFi, and were users made whole? | [F18](../findings/F18_secondfi_incident.md), `secondfi_incident_*`, original security/recovery/winddown sources | Chain-side transfers and dated balances are distinct from the operator's theft/rescue classifications. A recovery fund, a promised recovery process and completed user restitution are different observations. |
| What can NIGHT data tell us about IO's other interests? | [NIGHT method](25_NIGHT_TOKEN_PROVENANCE.md), [F16](../findings/F16_night_mint_provenance_and_concentration.md), [F17](../findings/F17_night_wanchain_bridge_incident.md), `night_*` | Supply, concentration and transaction paths at the module boundary. These do not identify all beneficial holders, prove founder responsibility for a bridge incident, or measure value accruing to ADA. |
| What have the organizations disclosed themselves? | [`founding_public_sources.csv`](../data/small/founding_public_sources.csv) | An index of original financial, governance, investment, organizational and incident publications, with retrieval limits. A published assertion is not automatically an independently established fact. |

## Reproduce the founder cut

From the clone root, after installing `requirements/base.txt`:

```bash
python scripts/build_genesis_db.py
python scripts/verify_founding_evidence.py --db data/abcde_genesis.duckdb
```

The verifier checks the bundle's internal integrity and consistency. Inspect
its checks and the extraction SQL as well: passing checks do not establish a
real-world identity, honest intent, complete disclosure or the truth of an
organization's financial claims.

Read and run the public DuckDB queries in
[`sql/35_founding_entities/`](../sql/35_founding_entities/), for example:

```bash
python scripts/query_duckdb.py sql/35_founding_entities/02_vote_pair_agreement.duckdb.sql
python scripts/query_duckdb.py sql/35_founding_entities/04_delegated_voting_power.duckdb.sql
```

The directory also contains receipt, disagreement, transaction-conservation,
cohort and reserve-credit queries. The same tables are available through the
read-only MCP tools `list_tables`, `describe_table` and `run_sql`. Start with the actual schema in [`SCHEMA.md`](SCHEMA.md); do not
invent columns from a table's name.

The audit trail is
[`founding-evidence-manifest.json`](../data/manifests/founding-evidence-manifest.json)
and [`founding_query_receipts.csv`](../data/small/founding_query_receipts.csv).
The new extraction uses a read-only, repeatable-read database snapshot. Exact
extraction SQL, the source boundary, CSV row counts and hashes make the cut
reviewable independently of any written interpretation. The raw monetary unit
is integer **lovelace**; divide by 1,000,000 only for ADA presentation.

### How to read governance comparisons

1. Establish identity from `founding_drep_identity` and its public source.
   Preserve the credential type: legacy DRep display strings can be identical
   for a script credential and a key credential. Use the published
   `drep_hash_id` and `has_script` fields when joining the cut, not the display
   string alone. This is a selected group of explicitly identified DReps, not
   a census of every possible founder-affiliated representative.
2. Use a common, complete recorded epoch for `founding_drep_distribution`.
   Report delegated voting power and its epoch. Do not call it the DRep's wallet
   balance, founder-owned ADA or a percentage of all eligible voting power
   without a matching denominator. The latest distribution also includes the
   automatic always-abstain and always-no-confidence targets; blindly summing
   all rows does not establish an action's eligible approval denominator.
   Delegating to an automatic target is different from a DRep casting an
   explicit Abstain ballot.
3. Retain raw ballot history. For a comparison of final recorded choices,
   select the latest valid ballot for each DRep and proposal, identified by
   **proposal transaction hash plus action index**. Preserve the order and
   validity fields; counting every revision overstates participation.
4. Pair only actions on which both representatives have a qualifying ballot.
   Report that shared-action denominator, matching choices, opposing Yes/No
   votes and explicit Abstain combinations. Also report unpaired actions;
   absence of a ballot is not abstention or opposition.
5. Read the proposal's type, timing and recorded lifecycle alongside the
   vote. `founding_epoch_parameters` contains selected parameters for the
   extraction's latest epoch, not the full historical rule set. Historical
   ratification additionally requires the rules and eligible denominators at
   that action's evaluation time, other voting groups and timing. A simple
   Yes sum does not reproduce ratification.
6. Compare both affiliated DReps and organizations that disagree. A finding of
   EMURGO/Yoroi alignment and a finding of CF/EMURGO disagreement can both be
   true. Neither should be suppressed to fit a single-bloc hypothesis.

## Freshness and scope: the traps that change the answer

**The September founder cut does not refresh every table in ABCDE.** The older
traces, custody graph, monthly stream, incident balances, NIGHT graph and relay
observations retain their own receipts. `build_info` is build/global context;
`data_freshness_catalog` inventories files. A recent commit timestamp or global
tip does not make all the underlying rows current.

The cohort refresh measures epoch stake for **14 selected historical stake
credentials**, with the selection source and date in `founding_cohort_keys`.
It is a different scope from F15's historical 115-key component and does not
rediscover the entire graph or establish an updated balance for
every wallet potentially sharing a custodian. Epoch stake, an unspent-output
balance and DRep distribution are different quantities. An older approximately
1.694B ADA custody-graph headline must be attributed to its historical cut,
not silently carried forward as a current founder balance.

Broad genesis traces can follow the whole output of a transaction after one
linked input appears. Those outputs may include unrelated money. A row reached
from two roots is still one output; adding root rollups can double-count it.
Deduplicate at the UTxO or stake-credential level required by the question and
state the trace depth and filters. A confidence or custody score is a
heuristic classification, not a calibrated probability of continued founder
ownership.

Shared exchanges, custodians, fee sponsors and infrastructure providers can
connect many independent customers. Follow a concrete transaction path while
keeping those alternatives visible. Neither a shared service nor a long
ancestry path identifies the person who economically owns an endpoint.

## Original publications: what readers should check

The queryable [source index](../data/small/founding_public_sources.csv) records
URL, organization, topic, document date when available, retrieval time,
observation and limits. Follow the original URL and retain the distinction
between the publisher's statement and independent corroboration.

- **Cardano Foundation:** financial statements, board/governance explanations,
  Catalyst management votes and Summit funding outcomes. The 2025 audited
  statutory foundation accounts are useful financial disclosure, but their
  scope is not automatically a consolidated account of every related entity.
  Check the notes and the reporting perimeter. A rejected funding request is
  evidence that institutional influence can face opposition.
- **IO/IOG, vouchers and development contracts:** compare the voucher
  investigation's commissioned scope and cited records with the chain
  transaction and the published CDH contract register. The source index flags
  incomplete PDF retrieval; indexed excerpts cannot substitute for a verified
  reading of the full report and annexes. Recipient approvals, pricing,
  milestones, acceptance and beneficial ownership are separate checks.
- **IO and other organizations/businesses:** inspect the BlockPQR transition
  announcement and Midnight materials for contractual roles, personnel and
  product economics. An organizational or personnel overlap is checkable;
  hidden ownership or a financial benefit to ADA requires further evidence.
- **EMURGO:** compare the investment commitment with any later reconciled
  deployment, recipient and outcome records. A pledge is not demonstrated
  deployment; failure to find a reconciliation in this source set is not proof
  that no investment occurred. The Yoroi delegation interface is also an
  observable distribution channel; its actual causal contribution to voting
  power is not measured by vote correlation.
- **SecondFi:** the indexed historical incident disclosure separates roughly
  **16.1M ADA reported stolen** from roughly **129M ADA reported rescued**.
  The currently retrieved incident page does not retain the same full timeline.
  Treat those historical figures as attributed operator statements, not a
  present balance or independently verified restitution total. The recovery
  FAQ and winddown notice must be read at their own dates. A projected start
  date conditional on an audit does not prove payments happened.

The existing chain-only F18 intentionally left the large sweep's intent
unresolved. The later operator description supplies an attributed rescue
claim; it does not change what those original transaction rows alone prove.
The aggregate exposure census remains aggregate-only: no exposed-key material
or victim targeting list is published.

## Testable hypotheses and missing evidence

| Hypothesis to test | Supporting observations to examine | Alternatives / evidence that could weaken it | Most useful next evidence |
|---|---|---|---|
| Founder-related wallet distribution concentrates governance influence | Identified DRep distributions, UI placement and shared-action vote alignment | Voluntary delegation, ordinary agreement on proposals, independent voting and redelegation | Time series around interface changes; verified delegation flows; comparison with unaffected wallets |
| An overlapping institutional role creates a poorly managed conflict | Votes on own funding/management roles; contract recipients and personnel links | Disclosed interests, competitive tender, recusal, independent review, rejected proposals | Conflict register, approval minutes, bids, ownership disclosures and delivery acceptance |
| Early merged assets had a common administrator | Exact 781M co-spend inputs and early source path | A custodian processing holdings for separate buyers | Subscription, custody and settlement records identifying the economic principals |
| Uniform parcels share custody tooling | Certificate timing, withdrawal edges, funding patterns and cohort stake | A service operating accounts for unrelated clients | Public custodian attestation or independently verified service records; counterexamples using the same service |
| A large development or investment commitment lacks adequate accountability | Published commitment, recipient contracts and available financial disclosures | Delivery and investment records outside the currently examined source set | Reconciliation of committed, paid, returned and remaining amounts; deliverables and independent acceptance |
| Incident users have not received the promised restitution | Dated recovery statements and scoped on-chain fund movements | Repayment through other disclosed wallets or off-chain channels; eligibility checks still in progress | Audited liabilities, completed payout totals, dated reconciliation and privacy-preserving confirmation |

These are questions the evidence can narrow. The bundle does **not** establish
fraud, theft by a founding organization, deliberate sabotage, a concealed
single controlling entity, or the beneficial ownership of every trace-reached
wallet. Strong findings require direct evidence for the specific assertion,
including evidence that could refute it. Use ABCDE's
[grading standard](02_GRADING.md) and cite the exact table, query and boundary
for every numerical claim.

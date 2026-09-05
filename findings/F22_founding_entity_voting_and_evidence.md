# F22 — Founder-related voting alignment and accountability evidence

**Snapshot:** epoch 653 / block 13,899,964 / 2026-09-05 04:39:55 UTC.
Method and interpretation boundaries:
[Founder accountability evidence guide](../docs/28_FOUNDER_ACCOUNTABILITY_EVIDENCE.md).

## Claim

The three explicitly identified DReps have the following **delegated voting
power at epoch 653**, measured in the committed distribution rows:

| DRep | Delegated voting power, ADA |
|---|---:|
| EMURGO | 301,958,521.565201 |
| Yoroi Wallet | 469,671,268.300191 |
| Cardano Foundation | 164,748,353.912119 |

EMURGO and Yoroi together represent **771,629,789.865392 ADA**. These are
represented voting amounts, including delegation by other holders; they are
not a calculation of assets owned by the organizations.

Selecting the latest valid ballot per DRep and governance action from
**453 raw ballots** yields **432 choices**. Pairing only shared actions gives:

| Pair | Shared actions | Same choice | Different choice | Opposing Yes/No |
|---|---:|---:|---:|---:|
| EMURGO / Yoroi | 142 | 140 | 2 | 0 |
| CF / EMURGO | 142 | 87 | 55 | 9 |
| CF / Yoroi | 142 | 89 | 53 | 9 |

EMURGO and Yoroi each have 142 qualifying actions, all shared. CF has 148,
including **six actions without a qualifying ballot from either of the other
two**. Explicit Abstain is a recorded choice; an absent ballot is not Abstain.
The nine directly opposing CF votes are observable counter-evidence to a
claim that these three representatives always vote as a uniform bloc.

## Grade

- **FACT:** credential identifiers and types, epoch distributions, ballot
  history, latest-choice counts, and pairwise agreement within this cut.
- **EXTERNAL_CORROBORATION:** the identity anchors and EMURGO's own
  [Yoroi delegation instructions](https://www.emurgo.io/press-news/delegating-your-vote-just-got-easier-one-click-yoroi-drep-delegation-is-here/)
  document affiliation and the top-button, user-confirmed delegation flow.
- **WORKING_HYPOTHESIS:** wallet interface placement contributes to concentrated
  voting influence. The interface and represented power are observable; the
  causal contribution is not measured here.
- **UNKNOWN:** a binding voting agreement, concealed coordination, beneficial
  ownership of delegated ADA, motives, decisive control over proposal outcomes,
  or fraud. Matching choices alone establish none of these.

## Evidence

- `data/small/founding_chain_tip.csv`
- `data/small/founding_drep_identity.csv`
- `data/small/founding_drep_distribution.csv`
- `data/small/founding_votes.csv`
- `data/small/founding_vote_pairs.csv`
- `data/small/founding_proposals.csv`
- `data/small/founding_public_sources.csv`
- `data/small/founding_query_receipts.csv`
- `data/manifests/founding-evidence-manifest.json`
- `sql/35_founding_entities/02_vote_pair_agreement.duckdb.sql`
- `sql/35_founding_entities/03_vote_disagreements.duckdb.sql`
- `sql/35_founding_entities/04_delegated_voting_power.duckdb.sql`
- `docs/28_FOUNDER_ACCOUNTABILITY_EVIDENCE.md`

The [original-source register](../data/small/founding_public_sources.csv)
preserves evidence both for scrutiny and against stronger allegations:

- `CF_CATALYST_SELF_VOTE` records CF's disclosed vote on its own management
  appointment; `CF_SUMMIT_2026` records its failed funding request.
- `CF_ACCOUNTS_2025` links audited statutory financial statements;
  `CF_RETURNS_2026` and `IO_REFUNDS` preserve reported treasury returns.
- `IO_VOUCHER_REPORT` preserves the commissioned investigation's reported
  transfers, delivery evidence and rejection of allegations within its scope.
- `SECOND_FI_INCIDENT_HISTORY` separates operator-reported theft from rescue;
  `SECOND_FI_RECOVERY_FAQ` preserves the dated, conditional recovery forecast.

These are attributed publications. This voting comparison does not independently
audit their accounts, verify every reported return, or establish restitution.

## Reproduce

Recompute the pair counts from raw ballots and the epoch voting amounts:

```bash
python scripts/query_duckdb.py sql/35_founding_entities/02_vote_pair_agreement.duckdb.sql
python scripts/query_duckdb.py sql/35_founding_entities/04_delegated_voting_power.duckdb.sql
python scripts/verify_founding_evidence.py --db data/abcde_genesis.duckdb
```

Inspect the stored pair receipt alongside the raw-ballot recomputation:

```sql
SELECT * FROM founding_vote_pairs;
```

## Limitations

The selected representatives are not a census of every founder-affiliated
DRep or every form of institutional influence. Join credentials using both
`drep_hash_id` and `has_script`: a legacy display string can collide between
a key and a script. The CF row identifies the published script credential.

Current epoch power cannot simply be assigned retrospectively to historical
votes. Reproducing ratification requires proposal-specific rules, historical
eligible denominators, timing and other voting groups. This finding does not
calculate a counterfactual result with founder votes removed.

The source register distinguishes live pages from indexed historical text.
The full voucher PDF was not retrieved; the CDH register's later body extraction
failed; SecondFi's live incident page omits the indexed historical timeline.
CF's audited 2025 statutory accounts are dated and do not automatically provide
consolidated visibility of every related entity. The new chain receipt does
not refresh older custody, incident-balance or genesis-trace tables.

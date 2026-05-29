# DRep Profile Pack

The DRep profile pack is a standardized, timestamped profile surface for the current top DReps.

It exists so community members can clone ABCDE and ask their own governance questions without running a Cardano relay, node, or db-sync instance.

## Public entry points

- DRep folder: `profiles/dreps/`
- Summary report: `reports/top_drep_profiles.md`
- Query examples: `docs/19_QUERY_COOKBOOK.md`
- Raw CSVs: `data/small/governance_top_drep_*.csv`
- SQL source: `sql/20_profiles/`
- Manifest: `data/manifests/top-drep-profiles-manifest.json`

## What data is provided

### Current profile rows

File: `data/small/governance_top_drep_profiles_current.csv`

This answers:

- Who are the current top DReps by voting power?
- What is each DRep's overall rank?
- What is each registered DRep's rank excluding system targets?
- How much voting power does each DRep currently have?
- How many current stake credentials have this as their latest DRep delegation?
- How many stake credentials have ever delegated to this DRep?
- What is the latest-retention ratio?
- What registration anchor URL/hash is available?
- What db-sync timestamp, DRep distribution epoch, and active stake epoch were used?

### Stake-size buckets

File: `data/small/governance_top_drep_stake_buckets.csv`

This answers:

- Is a DRep's power concentrated in a few large delegators or spread across many small delegators?
- How many current delegators fall into each active-stake bucket?
- How much active stake sits in each bucket?

Buckets:

- `>=50M`
- `10M-50M`
- `1M-10M`
- `100k-1M`
- `10k-100k`
- `1k-10k`
- `<1k`
- `0/no active stake`

### Delegation-age buckets

File: `data/small/governance_top_drep_delegation_age_buckets.csv`

This answers:

- Did the DRep's current support arrive early or recently?
- How sticky does the support look by latest vote-delegation epoch?
- How much active stake belongs to old delegation cohorts?

### Pool affiliations

File: `data/small/governance_top_drep_pool_affiliations.csv`

This answers:

- Which SPO pools are current DRep delegators also staking to?
- Are there obvious pool-community concentrations?
- How much active stake sits behind the top pool affiliations for each DRep?

This is an affiliation view, not proof of identity or coordination.

### Koios cross-check

File: `data/small/governance_top_drep_koios_crosscheck.csv`

This answers:

- Does Koios return the same voting-power amount as db-sync for registered DReps?
- Does the metadata URL match?
- Does the metadata hash match?
- What CIP-129 DRep ID does Koios return?

System DRep targets such as `drep_always_abstain` are marked `not_applicable`.

### Genesis-trace exposure

Files:

- `data/small/governance_top_drep_genesis_trace_exposure.csv`
- `data/small/governance_top_drep_genesis_trace_exposure_by_root.csv`

This answers:

- How much current ABCDE trace-derived value sits under stake credentials whose latest observed DRep delegation points to each top DRep?
- Which root seeds contribute to that trace-derived value?
- Where do root overlaps require deduplication?

This is an audit signal, not an ownership claim.

### Genesis-trace stickiness

File: `data/small/governance_top_drep_genesis_trace_stickiness.csv`

This answers:

- Among traced stake credentials that ever delegated to a DRep, how many still have that DRep as the latest observed target?
- How many moved away?
- What current trace-derived value stayed with or moved away from the DRep target?

## How it is built

Maintainers can rebuild the pack with:

```bash
bash scripts/build_top_drep_profiles_remote.sh
```

The full project rebuild also includes the profile pack:

```bash
bash scripts/rebuild_seed_cut.sh
```

The profile pack uses:

- ABCDE PostgreSQL/cardano-db-sync for current DRep distribution, vote delegations, active stake, DRep registrations, and pool affiliations.
- Koios `drep_info` for independent registered-DRep cross-checks.
- Preserved ABCDE trace receipts for genesis-trace exposure and stickiness.

## Evidence boundary

Use these labels when discussing the profile pack:

- `FACT`: DRep voting power, ranks, current/historical delegation counts, active stake buckets, DRep anchors, pool affiliations, Koios comparison rows.
- `STRONG_INFERENCE`: high retention ratios and older latest-delegation cohorts are evidence of sticky delegation behavior.
- `UNKNOWN`: beneficial ownership, legal identity, custody, nationality, off-chain demographics, and voter intent.

Do not use this data to claim that a DRep controls delegated funds. DRep delegation assigns voting power; it does not transfer custody.

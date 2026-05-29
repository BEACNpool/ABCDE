# DRep Profiles

This is the public entry folder for ABCDE DRep profile work.

The current profile pack is generated for the top DReps as a set. This keeps the analysis consistent and avoids selective one-off framing.

## Start here

- Summary report: `../../reports/top_drep_profiles.md`
- DRep profile guide: `../../docs/18_DREP_PROFILE_PACK.md`
- Query cookbook: `../../docs/19_QUERY_COOKBOOK.md`
- Generation SQL: `../../sql/20_profiles/`
- Generation scripts:
  - `../../scripts/build_top_drep_profiles_remote.sh`
  - `../../scripts/build_top_drep_profiles_report.py`
  - `../../scripts/build_top_drep_koios_crosscheck.py`

## Queryable files

The profile pack publishes committed CSVs under `data/small/`:

| file | what it answers |
| --- | --- |
| `governance_top_drep_profiles_current.csv` | Current top DRep rank, voting power, delegator counts, retention, anchors, and db-sync timestamps |
| `governance_top_drep_stake_buckets.csv` | Current DRep delegators grouped by active stake-size bucket |
| `governance_top_drep_delegation_age_buckets.csv` | Current DRep delegators grouped by latest vote-delegation epoch bucket |
| `governance_top_drep_pool_affiliations.csv` | Top active SPO pool affiliations among each DRep's current delegators |
| `governance_top_drep_koios_crosscheck.csv` | Koios `drep_info` comparison against db-sync amount, metadata URL, and metadata hash |
| `governance_top_drep_genesis_trace_exposure.csv` | Deduped current genesis-trace value whose latest observed DRep target is the profiled DRep |
| `governance_top_drep_genesis_trace_exposure_by_root.csv` | Genesis-trace exposure split by ABCDE root seed |
| `governance_top_drep_genesis_trace_stickiness.csv` | For traced stake credentials, whether the latest observed DRep delegation stayed with or moved away from the DRep |

## Evidence boundary

These profiles describe on-chain voting delegation and trace-derived audit signals.

They do not establish beneficial ownership, custody, legal identity, nationality, voter intent, or off-chain demographics. DRep delegation is voting power, not control of delegated funds.

## Future generated pages

Per-DRep pages can be added here later, for example:

```text
profiles/dreps/yuta.md
profiles/dreps/yoroi.md
```

Those pages should be generated from the same profile pack, not written as ad hoc dossiers.

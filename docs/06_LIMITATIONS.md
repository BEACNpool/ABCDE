# Limitations and Non-Attribution

This project maps on-chain flows. It does not prove legal ownership, intent, misconduct, or contractual breach.

Byron-era shared infrastructure is a major confounder. Co-spends and shared routing may indicate shared administration or custody without proving shared beneficial ownership.

Exchange and custodian labels must be treated as heuristic unless backed by explicit public/on-chain evidence.

## Snapshot Freshness

The committed clone-and-query database contains multiple snapshots, not a live
chain index. For each table, inspect its module receipt or manifest, then
`data_freshness_catalog`, `db_tip_receipt` and `build_info`. Always name the
source tip and epoch used for live-unspent status, DRep distribution, stake
delegation and governance lifecycle claims.

A recent build, commit, global receipt or new module does **not** refresh older
extracts. `data_freshness_catalog` helps inventory files and age, but a source
file's commit time is not necessarily its chain boundary. Historical findings
retain their original scope unless their actual supporting rows are refreshed
and reverified. The founding-accountability cut has a separate
`founding_query_receipts` table and
[`founding-evidence-manifest.json`](../data/manifests/founding-evidence-manifest.json);
see the [evidence guide](28_FOUNDER_ACCOUNTABILITY_EVIDENCE.md).

## Depth-Bounded Traces

Depth-14 staged traces are lineage surfaces, not identity surfaces. A row being
reached by a founder trace means the on-chain lineage reached that row under the
published depth and filter rules. It does not prove custody, beneficial
ownership, legal control, or intent.

## Behavior Scores

`heuristic_v1_public_signals` is an audit-prioritization model over public
signals such as same-block events, same-epoch DRep cohorts, cross-root current
clusters, current DRep delegation, and proposal vote activity. These scores rank
rows for review; they are not conclusions.

## Totals, custody and independent corroboration

- A transaction can mix trace-reached and unrelated inputs. Following every
  output gives a reachability surface, not a conservation-based allocation of
  each founder's value. Overlapping root totals must not be added as if disjoint.
- UTxO balances, epoch stake and DRep voting-power distributions measure
  different things. Label the quantity and its boundary before comparing them.
- Shared signing, withdrawal plumbing, transaction ancestry or a common
  service can support a custody hypothesis without identifying the beneficial
  owners or the number of independent customers. Heuristic scores have not
  been calibrated as probabilities of ownership or misconduct.
- An organization publishing a statement is evidence of what it said. The
  source index records retrieval limitations and does not convert corporate
  claims into independently audited facts. A hash verifies a preserved
  artifact; it does not validate the publisher's underlying assertions.
- On-chain incident balances do not establish user liabilities, eligibility
  or completed restitution. Do not publish victim targeting lists or exposed
  signing material.

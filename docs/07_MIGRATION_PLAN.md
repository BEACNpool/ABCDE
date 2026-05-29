# Migration Plan

The rebuild is intentionally conservative: preserve first, migrate only what earns its place.

## Keep / migrate first

- Corrected seed anchors and labels from archived backlog notes, `docs/02_METHOD_AND_DATA_PROVENANCE.md`, and `findings/F01*`.
- Fourth-entry operational convergence evidence, rewritten with non-attribution language.
- Fourth-entry sale-ticket origin signal.
- Cross-entity merge inventory and clean three-way merge receipts.
- Shelley-era delegation / DRep overlap analysis.
- The db-sync `tx_in` join warning.

## Rewrite before publishing

- Thin canonical findings that only point back to archives.
- Any claim using `EMURGO_2 == EMURGO` wording; replace with operational convergence / shared administration framing.
- Any runner that hardcodes paths, `${DB_HOST}` in public docs, or WSL/Windows-specific fallback paths.

## Keep in legacy only

- MIR-318M/WavePool material until it becomes a separate case/repo.
- NIGHT material already removed from `main`; any legacy remnants remain historical only.
- Raw one-off CSV exports that should become release artifacts, not source files.
- Archived duplicate snapshots.

## Drop later, after review

Nothing is dropped in the first v2 commit. After the public data model and rebuilt findings exist, legacy material can be reduced or moved to a tag/release archive.

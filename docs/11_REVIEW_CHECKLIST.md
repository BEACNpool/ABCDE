# Review Checklist Before Replacing `main`

Do not merge this branch over `main` until these are true.

## Already true in current v2 branch

- Old material is preserved under `legacy/2026-05-20-pre-v2-import/`.
- Genesis-only scope is explicit.
- `anchors.yaml` is the seed source of truth.
- Small seed registry DuckDB cut is generated and committed.
- Seed tx hashes are verified against ABCDE/db-sync.
- Seed outputs are verified against ABCDE/db-sync.
- First spends are verified against ABCDE/db-sync.
- Fourth-entry direct EMURGO-descended co-spend is rebuilt as a focused FACT receipt.
- F03 sale-ticket origin signal is re-derived from archived `main2.json`.
- One-command maintainer rebuild exists: `scripts/rebuild_seed_cut.sh`.

## Still needed before main replacement

- Decide whether the tiny DuckDB artifact stays committed or moves to GitHub Releases once larger cuts exist.
- Rebuild cross-entity merge inventory beyond first-spend receipts.
- Add a real full/partial UTxO trace extractor with bounded depth/run manifest.
- Remove or shrink `legacy/` if the PR diff is too noisy for review.
- Confirm GitHub Actions passes on the branch.

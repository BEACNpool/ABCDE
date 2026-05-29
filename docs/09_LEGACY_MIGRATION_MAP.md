# Legacy Migration Map

This map decides what v2 may depend on, what must be rewritten, and what remains historical only.

## Preserve as source receipts

These legacy paths are closest to immutable audit receipts and should be migrated into the v2 data model with checksums before any claim depends on them:

- `legacy/2026-05-20-pre-v2-import/data/raw/iog/`
- `legacy/2026-05-20-pre-v2-import/data/raw/emurgo/`
- `legacy/2026-05-20-pre-v2-import/data/raw/emurgo2/`
- `legacy/2026-05-20-pre-v2-import/data/raw/cf/`
- `legacy/2026-05-20-pre-v2-import/data/reference/README.md`
- `legacy/2026-05-20-pre-v2-import/data/reference/METHODOLOGY.md`

## Preserve as derived evidence, with manifests

These may support continuity, but must be labeled as derived artifacts rather than primary chain facts:

- `legacy/2026-05-20-pre-v2-import/data/raw/exchange-analysis/`
- `legacy/2026-05-20-pre-v2-import/evidence/csv/`
- `legacy/2026-05-20-pre-v2-import/evidence/overlaps/`
- `legacy/2026-05-20-pre-v2-import/evidence/dossiers/`
- `legacy/2026-05-20-pre-v2-import/evidence/reports/`
- `legacy/2026-05-20-pre-v2-import/evidence/timelines/`

## Rewrite for v2

- `README.md`
- `docs/*`
- `findings/*`
- `AUDIT_BACKLOG.md`
- query/script READMEs

The old versions are unstructured audit prose. v2 needs deterministic rebuild instructions, published data dictionary, claim grading, limitations, and one local-query path.

## Normalize heavily before reuse

- legacy `queries/core/*`
- legacy `queries/validation/*`
- legacy `sql/falsification_tests/*`
- legacy `scripts/runners/*`
- legacy `scripts/analysis/*`

Known issues to audit:

- mixed database assumptions and query styles
- possible stale `tx_in.tx_out_id = tx_out.id` patterns
- hardcoded/stale paths such as `datasets/genesis-founders/...`
- runner root detection that can resolve to `scripts/` instead of the repo root

## Keep historical only

- `legacy/2026-05-20-pre-v2-import/archive/original_layout_snapshot/`
- `legacy/2026-05-20-pre-v2-import/investigation/archived_findings/`
- `legacy/2026-05-20-pre-v2-import/investigation/archived_notes/`
- `legacy/2026-05-20-pre-v2-import/investigation/worklog/`
- `legacy/2026-05-20-pre-v2-import/investigation/open_questions/`
- `legacy/2026-05-20-pre-v2-import/outputs/`

## Exclude from genesis-only v2 surface

- MIR-318M/WavePool material — separate case/repo.
- `DEPLOY.sh` — stale deployment script targeting branch replacement directly.
- `append_parts.py` — ad hoc prose append, not reproducible.
- `tmp_*` SQL — one-off historical scratch unless promoted into a named falsification or validation query.

#!/usr/bin/env bash
# Finalize a cut before committing. Run this AFTER all data and doc edits are
# done — it regenerates every derived artifact in dependency order and then
# verifies. The hash indexes (public-artifacts-manifest, findings.json) are
# built LAST because they fingerprint everything else; regenerating them
# earlier leaves stale hashes in the commit (this happened on 2026-07-03).
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"
PY="$REPO_ROOT/.venv/bin/python3"
[[ -x "$PY" ]] || PY=python3

"$PY" scripts/build_freshness_catalog.py          # per-table freshness (tip refresh only if ABCDE_SSH set)
"$PY" scripts/build_genesis_db.py                 # DuckDB + schema catalog + docs/SCHEMA.md
"$PY" scripts/build_community_report.py           # reports/ (fingerprinted below)
"$PY" scripts/build_public_artifact_manifest.py   # hash index — after everything above
"$PY" scripts/build_findings_json.py              # joins hashes from the manifest

"$PY" scripts/verify_claim_receipts.py
"$PY" scripts/build_findings_json.py --check
"$PY" scripts/selftest.py
"$PY" scripts/check_file_sizes.py

echo "finalize_cut: all green — safe to commit"

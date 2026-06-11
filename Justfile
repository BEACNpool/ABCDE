set dotenv-load := true

# List available tasks
_default:
    just --list

# Validate lightweight repo structure
check:
    python3 scripts/verify.py --structure-only

# Install the public query dependencies
bootstrap:
    python3 -m pip install -r requirements/base.txt

# Build the compact, query-ready genesis DuckDB + schema catalog
build-db:
    python3 scripts/build_genesis_db.py

# Run the read-only MCP server (stdio transport)
serve-mcp:
    python3 -m mcp_server.server

# Ask a question via the CLI fallback, e.g. just ask Q="where did EMURGO ADA go?"
ask Q:
    python3 ask.py "{{Q}}"

# Download + checksum-verify the full dataset from the latest GitHub Release
fetch-db:
    python3 scripts/fetch_db.py

# Alias for public instructions
fetch-full:
    python3 scripts/fetch_db.py

# Verify the clone-and-query public data path
test:
    python3 scripts/selftest.py
    python3 scripts/verify_claim_receipts.py
    python3 scripts/verify_public_artifacts.py

# Verify headline claim SQL receipts
verify-claims:
    python3 scripts/verify_claim_receipts.py

# Verify public artifact manifest hashes
verify-public-artifacts:
    python3 scripts/verify_public_artifacts.py

# Build GitHub Release assets locally under dist/release/
release-bundle:
    python3 scripts/build_release_bundle.py

# Placeholder: extract from db-sync/ABCDE warehouse
extract:
    python3 scripts/extract.py

# Placeholder: publish DuckDB/Parquet bundle
publish:
    python3 scripts/publish.py

# Verify findings/data bundle
verify:
    python3 scripts/verify.py

# Build local seed registry CSV/DuckDB artifacts from anchors.yaml
seed-artifacts:
    python3 scripts/build_seed_artifacts.py

# Verify generated seed registry CSV/DuckDB artifacts
verify-seed-artifacts:
    python3 scripts/verify_seed_artifacts.py

# Verify anchors.yaml against remote db-sync and write CSV receipt
verify-seed-anchors-remote:
    bash scripts/verify_seed_anchors_remote.sh

# Build first-spend receipt from remote db-sync
seed-first-spends-remote:
    bash scripts/build_seed_first_spends_remote.sh

# Build direct co-spend receipt for fourth-entry first spend
fourth-cospend-remote:
    bash scripts/build_fourth_entry_direct_cospend_remote.sh

# Build input-composition receipt for all seed first-spend txs
seed-first-spend-inputs-remote:
    bash scripts/build_seed_first_spend_inputs_remote.sh

# Rebuild seed cut end-to-end from ABCDE/db-sync receipts
rebuild-seed-cut:
    bash scripts/rebuild_seed_cut.sh

# Build bounded trace receipt from ABCDE/db-sync (default TRACE_DEPTH=3)
bounded-trace-remote:
    bash scripts/build_bounded_trace_remote.sh

# Execute all finding reproduce SQL against local DuckDB artifact
verify-finding-queries:
    python3 scripts/verify_finding_queries.py

# Run a DuckDB SQL file with Python duckdb, e.g. just query sql/10_findings/F01_named_founder_allocations.duckdb.sql
query sql_file:
    python3 scripts/query_duckdb.py {{sql_file}}

# Derive fourth-entry sale-ticket signal from archived ada-sale stats JSON
sale-ticket-signal:
    python3 scripts/build_sale_ticket_signal.py

# Build SPO/DRep delegation target rollups from preserved trace receipts
governance-rollups:
    python3 scripts/build_governance_rollups.py
    python3 scripts/verify_governance_rollups.py

# Build pool/DRep metadata enrichment from db-sync
governance-metadata:
    bash scripts/build_governance_metadata_remote.sh

# Build community-facing summary report from local DuckDB artifact
community-report:
    python3 scripts/build_community_report.py

# Build value-weighted latest SPO/DRep governance rollups
governance-value-rollups:
    python3 scripts/build_governance_value_rollups.py
    python3 scripts/verify_governance_value_rollups.py

# Build Genesis-to-DRep behavior surface from ABCDE/db-sync
genesis-drep-behavior-remote:
    bash scripts/build_genesis_drep_behavior_surface_remote.sh

# Rebuild local Genesis-to-DRep behavior rollups from data/release exports
genesis-drep-behavior-rollups:
    python3 scripts/build_genesis_drep_behavior_rollups.py

# Build Genesis-to-SPO surface, pool operator links, gov actions catalog
genesis-spo-surface-remote:
    bash scripts/build_genesis_spo_surface_remote.sh

# Rebuild local Genesis-to-SPO rollups from data/release exports
genesis-spo-rollups:
    python3 scripts/build_genesis_spo_rollups.py

# Build SHA-256 manifest for public docs/findings/reports/data/small artifacts
public-artifact-manifest:
    python3 scripts/build_public_artifact_manifest.py

# Regenerate machine-readable findings/findings.json claim map
findings-json:
    python3 scripts/build_findings_json.py

# Enforce committed file-size policy (warn 10 MiB, fail 50 MiB)
check-sizes:
    python3 scripts/check_file_sizes.py

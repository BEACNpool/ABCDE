#!/usr/bin/env bash
# Overnight live-tip refresh of the founders depth-14 staged trace and the
# two surfaces that read from it. Run with ABCDE_SSH set; expect hours.
#
#   1. staged trace (repopulates abcde_forensics_stage_founders_depth14)
#   2. genesis-DRep behavior surface + rollups
#   3. IOG current-bag depth-14 audit cut
#
# Each stage logs a timestamp so runtime per stage is auditable.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"
: "${ABCDE_SSH:?Set ABCDE_SSH to the warehouse SSH target}"

export TRACE_STAGE_SCHEMA=abcde_forensics_stage_founders_depth14
export TRACE_MAX_DEPTH=14
export FOUNDERS_ONLY=1

stamp() { echo "=== $(date -u +%FT%TZ) $*"; }

stamp "stage 1/3: staged founders trace to depth 14"
bash scripts/build_staged_trace_remote.sh \
  data/small/staged_trace_founders_depth14_summary.csv

stamp "stage 2/3: genesis-DRep behavior surface"
bash scripts/build_genesis_drep_behavior_surface_remote.sh

stamp "stage 3/3: IOG current-bag depth-14 audit"
bash scripts/build_iog_current_bag_audit_remote.sh

stamp "done"

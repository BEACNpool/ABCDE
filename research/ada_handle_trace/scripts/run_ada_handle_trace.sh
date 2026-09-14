#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<'EOF'
usage:
  run_ada_handle_trace.sh <handle-without-dollar> [depth]
  run_ada_handle_trace.sh <handle-without-dollar> summary
  run_ada_handle_trace.sh <handle-without-dollar> footprint

notes:
- numeric depth keeps the existing raw hop-trace behavior (depth 1..5)
- summary prints a human-readable handle summary
- footprint prints a human-readable owner footprint summary
EOF
}

if [[ $# -lt 1 ]]; then
  usage
  exit 1
fi

HANDLE="$1"
MODE="${2:-1}"
OUT_DIR="${OUT_DIR:-/tmp/abcde-handle-traces}"
mkdir -p "$OUT_DIR"
STAMP="$(date +%Y%m%d-%H%M%S)"

DB="${DB:-cexplorer_replica}"
PSQL_BASE=(sudo -u postgres psql -d "$DB" -v ON_ERROR_STOP=1)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
if [[ -n "${QUERY_DIR:-}" ]]; then
  QUERY_DIR="$QUERY_DIR"
elif [[ -d "$REPO_ROOT/queries" ]]; then
  QUERY_DIR="$REPO_ROOT/queries"
elif [[ -d "/usr/local/share/abcde/queries" ]]; then
  QUERY_DIR="/usr/local/share/abcde/queries"
else
  QUERY_DIR="$REPO_ROOT/queries"
fi

run_psql() {
  "${PSQL_BASE[@]}" "$@"
}

resolve_handle_tsv() {
  run_psql -At -F $'\t' -v handle="$HANDLE" <<'SQL'
with resolved as (
  select
    h.handle,
    h.handle_display,
    h.current_owner_address,
    coalesce(h.current_owner_stake, '-') as current_owner_stake,
    h.tx_hash,
    h.block_no,
    h.slot_no,
    h.epoch_no,
    h.observed_at,
    t.id as tx_id
  from explorer.handle_search h
  join public.tx t
    on t.hash = decode(h.tx_hash, 'hex')
  where lower(h.handle) = lower(:'handle')
)
select handle, handle_display, current_owner_address, current_owner_stake, tx_hash, block_no, slot_no, epoch_no, observed_at, tx_id
from resolved;
SQL
}

run_summary_mode() {
  local out_file="$OUT_DIR/handle-${HANDLE}-summary-${STAMP}.txt"
  mapfile -t resolved_rows < <(resolve_handle_tsv)
  if (( ${#resolved_rows[@]} == 0 )); then
    echo "no handle resolution found for: $HANDLE" >&2
    exit 4
  fi

  IFS=$'\t' read -r res_handle res_display res_addr res_stake res_tx_hash res_block_no res_slot_no res_epoch_no res_observed_at res_tx_id <<< "${resolved_rows[0]}"

  mapfile -t summary_rows < <(run_psql -At -F $'\t' -v handle="$HANDLE" -f "$QUERY_DIR/ada_handle_summary.sql")

  {
    printf 'ADA Handle Summary\n'
    printf '==================\n'
    printf 'Handle: %s\n' "$res_display"
    printf 'Canonical handle: %s\n' "$res_handle"
    printf 'Resolved owner address: %s\n' "$res_addr"
    printf 'Resolved stake address: %s\n' "$res_stake"
    printf 'Resolved tx hash: %s\n' "$res_tx_hash"
    printf 'Block / slot / epoch: %s / %s / %s\n' "$res_block_no" "$res_slot_no" "$res_epoch_no"
    printf 'Observed at: %s\n' "$res_observed_at"
    printf '\n'

    local first_hop_count="0"
    local first_hop_total="0"
    local first_hop_unique_addresses="0"
    local first_hop_unique_stakes="0"
    local first_hop_min_block='-'
    local first_hop_max_block='-'
    local sample_lines=()

    for row in "${summary_rows[@]}"; do
      [[ -z "$row" ]] && continue
      IFS=$'\t' read -r section c1 c2 c3 c4 c5 c6 <<< "$row"
      case "$section" in
        stats)
          first_hop_count="$c1"
          first_hop_total="$c2"
          first_hop_unique_addresses="$c3"
          first_hop_unique_stakes="$c4"
          first_hop_min_block="$c5"
          first_hop_max_block="$c6"
          ;;
        sample)
          sample_lines+=("  - tx=${c1} idx=${c2} lovelace=${c3} block=${c4} addr=${c5} stake=${c6}")
          ;;
      esac
    done

    printf 'First-hop input stats\n'
    printf '%s\n' '---------------------'
    printf 'Input rows: %s\n' "$first_hop_count"
    printf 'Total lovelace across first-hop inputs: %s\n' "$first_hop_total"
    printf 'Distinct source addresses: %s\n' "$first_hop_unique_addresses"
    printf 'Distinct source stake addresses: %s\n' "$first_hop_unique_stakes"
    printf 'Source block range: %s -> %s\n' "$first_hop_min_block" "$first_hop_max_block"
    printf '\n'
    printf 'First-hop sample (up to 5 rows)\n'
    printf '%s\n' '-------------------------------'
    if (( ${#sample_lines[@]} == 0 )); then
      printf '  (none)\n'
    else
      printf '%s\n' "${sample_lines[@]}"
    fi
  } > "$out_file"

  echo "$out_file"
}

run_footprint_mode() {
  local out_file="$OUT_DIR/handle-${HANDLE}-footprint-${STAMP}.txt"
  mapfile -t rows < <(run_psql -At -F $'\t' -v handle="$HANDLE" -f "$QUERY_DIR/ada_handle_owner_footprint.sql")
  if (( ${#rows[@]} == 0 )); then
    echo "no handle resolution found for: $HANDLE" >&2
    exit 4
  fi

  {
    printf 'ADA Handle Owner Footprint\n'
    printf '==========================\n'

    local summary_done=0
    local recent_lines=()

    for row in "${rows[@]}"; do
      [[ -z "$row" ]] && continue
      IFS=$'\t' read -r section c1 c2 c3 c4 c5 c6 c7 c8 c9 c10 <<< "$row"
      case "$section" in
        owner)
          printf 'Handle: %s\n' "$c2"
          printf 'Canonical handle: %s\n' "$c1"
          printf 'Resolved owner address: %s\n' "$c3"
          printf 'Resolved stake address: %s\n' "$c4"
          printf 'Resolved tx hash: %s\n' "$c5"
          printf 'Resolved block / slot / epoch: %s / %s / %s\n' "$c6" "$c7" "$c8"
          printf 'Observed at: %s\n' "$c9"
          printf '\n'
          summary_done=1
          ;;
        counts)
          printf 'On-chain footprint counts\n'
          printf '%s\n' '-------------------------'
          printf 'tx_out rows linked to identity: %s\n' "$c1"
          printf 'Distinct tx producing those tx_out rows: %s\n' "$c2"
          printf 'Distinct consuming tx involving those outputs: %s\n' "$c3"
          printf 'tx_in rows involving those outputs: %s\n' "$c4"
          printf 'Total lovelace ever received on matched outputs: %s\n' "$c5"
          printf 'Earliest matched block: %s\n' "$c6"
          printf 'Latest matched block: %s\n' "$c7"
          printf '\n'
          ;;
        recent)
          recent_lines+=("  - block=${c1} tx=${c2} idx=${c3} lovelace=${c4} consumed_by_tx_id=${c5}")
          ;;
      esac
    done

    if (( summary_done == 0 )); then
      printf 'No resolved owner identity found.\n'
    fi

    printf 'Recent matched outputs (up to 5 rows)\n'
    printf '%s\n' '-------------------------------------'
    if (( ${#recent_lines[@]} == 0 )); then
      printf '  (none)\n'
    else
      printf '%s\n' "${recent_lines[@]}"
    fi
  } > "$out_file"

  echo "$out_file"
}

if [[ "$MODE" == "summary" ]]; then
  run_summary_mode
  exit 0
fi

if [[ "$MODE" == "footprint" ]]; then
  run_footprint_mode
  exit 0
fi

DEPTH="$MODE"
OUT_FILE="$OUT_DIR/handle-${HANDLE}-depth${DEPTH}-${STAMP}.txt"

if [[ "$DEPTH" == "1" ]]; then
  QUERY_FILE="${QUERY_FILE:-$QUERY_DIR/ada_handle_trace.sql}"
  if [[ ! -f "$QUERY_FILE" ]]; then
    echo "missing query file: $QUERY_FILE" >&2
    exit 2
  fi
  run_psql -v handle="$HANDLE" -f "$QUERY_FILE" > "$OUT_FILE"
  echo "$OUT_FILE"
  exit 0
fi

if ! [[ "$DEPTH" =~ ^[0-9]+$ ]] || (( DEPTH < 1 )); then
  echo "depth must be a positive integer, or use: summary | footprint" >&2
  exit 3
fi

if (( DEPTH > 5 )); then
  DEPTH=5
fi

mapfile -t RESOLVED < <(resolve_handle_tsv)

if (( ${#RESOLVED[@]} == 0 )); then
  echo "no handle resolution found for: $HANDLE" >&2
  exit 4
fi

IFS=$'\t' read -r RES_HANDLE RES_DISPLAY RES_ADDR RES_STAKE RES_TX_HASH RES_BLOCK_NO RES_SLOT_NO RES_EPOCH_NO RES_OBSERVED_AT RES_TX_ID <<< "${RESOLVED[0]}"

{
  printf 'depth\thandle\thandle_display\tcurrent_owner_address\tcurrent_owner_stake\ttarget_tx_hash\tsource_tx_hash\tsource_tx_out_index\tsource_address\tsource_stake\tsource_lovelace\tsource_block_no\tsource_block_time\n'

  frontier=("$RES_TX_ID")
  current_depth=1
  while (( current_depth <= DEPTH )) && (( ${#frontier[@]} > 0 )); do
    tx_id_csv=$(IFS=,; echo "${frontier[*]}")
    mapfile -t ROWS < <(run_psql -At -F $'\t' -v tx_ids="$tx_id_csv" <<'SQL'
with frontier as (
  select unnest(string_to_array(:'tx_ids', ','))::bigint as tx_id
)
select distinct
  encode(t_target.hash::bytea, 'hex') as target_tx_hash,
  encode(t_prev.hash::bytea, 'hex') as source_tx_hash,
  txo_prev.index as source_tx_out_index,
  txo_prev.address as source_address,
  coalesce(sa_prev.view, '-') as source_stake,
  txo_prev.value::text as source_lovelace,
  b_prev.block_no as source_block_no,
  b_prev.time as source_block_time,
  txo_prev.tx_id as source_tx_id
from frontier f
join public.tx_in ti
  on ti.tx_in_id = f.tx_id
join public.tx t_target
  on t_target.id = f.tx_id
join public.tx_out txo_prev
  on txo_prev.tx_id = ti.tx_out_id
 and txo_prev.index = ti.tx_out_index
join public.tx t_prev
  on t_prev.id = txo_prev.tx_id
join public.block b_prev
  on b_prev.id = t_prev.block_id
left join public.stake_address sa_prev
  on sa_prev.id = txo_prev.stake_address_id
order by b_prev.block_no desc, source_tx_hash;
SQL
)

    frontier=()
    for row in "${ROWS[@]}"; do
      [[ -z "$row" ]] && continue
      IFS=$'\t' read -r target_tx_hash source_tx_hash source_tx_out_index source_address source_stake source_lovelace source_block_no source_block_time source_tx_id <<< "$row"
      printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
        "$current_depth" "$RES_HANDLE" "$RES_DISPLAY" "$RES_ADDR" "$RES_STAKE" \
        "$target_tx_hash" "$source_tx_hash" "$source_tx_out_index" "$source_address" "$source_stake" \
        "$source_lovelace" "$source_block_no" "$source_block_time"
      frontier+=("$source_tx_id")
    done

    current_depth=$(( current_depth + 1 ))
  done
} > "$OUT_FILE"

echo "$OUT_FILE"

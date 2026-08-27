#!/usr/bin/env bash
# Build the relay registration + reachability surface end to end.
#
#   ABCDE_SSH   ssh target for the db-sync warehouse            (required)
#   PROBE_SSH   ssh target that runs the handshake sweep        (default: local)
#   PROBE_DIR   working dir on the probe host                   (default: ~/tools/relay-probe)
#   CARDANO_CLI path to cardano-cli ON THE PROBE HOST           (default: cardano-cli)
#
# Run the sweep from a host with NO Cardano production role. Do not point it at
# a block producer's relay: 4,000-odd outbound handshakes from the identity your
# pool is known by is a needless thing to explain to anyone.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
: "${ABCDE_SSH:?Set ABCDE_SSH to the warehouse SSH target}"
PROBE_SSH="${PROBE_SSH:-}"
PROBE_DIR="${PROBE_DIR:-~/tools/relay-probe}"
CARDANO_CLI="${CARDANO_CLI:-cardano-cli}"
DB_NAME="${DB_NAME:-cexplorer_replica}"
PSQL="sudo -n -u postgres psql -v ON_ERROR_STOP=1 -d '$DB_NAME'"
SQL_DIR="$REPO_ROOT/sql/56_relay_health"
OUT="$SQL_DIR/data"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

echo "1/5 building on-chain registration surface"
ssh "$ABCDE_SSH" "$PSQL -f -" < "$SQL_DIR/build_relay_registration.sql" > /dev/null

echo "2/5 exporting probe targets"
ssh "$ABCDE_SSH" "$PSQL -Atc \"\\copy (select distinct endpoint, endpoint_kind, endpoint_host, port from relay.endpoint where endpoint is not null order by 1,4) to stdout csv header\"" \
  > "$WORK/targets.csv"
echo "    $(( $(wc -l < "$WORK/targets.csv") - 1 )) endpoints"

echo "3/5 probing (single vantage point -- results are observations, not verdicts)"
if [[ -n "$PROBE_SSH" ]]; then
  ssh "$PROBE_SSH" "mkdir -p $PROBE_DIR"
  scp -q "$REPO_ROOT/scripts/relay_probe.py" "$WORK/targets.csv" "$PROBE_SSH:$PROBE_DIR/"
  ssh "$PROBE_SSH" "cd $PROBE_DIR && python3 relay_probe.py --targets targets.csv \
      --out observations.csv --cli '$CARDANO_CLI' --timeout 20 --workers 40"
  scp -q "$PROBE_SSH:$PROBE_DIR/observations.csv" "$WORK/observations.csv"
else
  python3 "$REPO_ROOT/scripts/relay_probe.py" --targets "$WORK/targets.csv" \
      --out "$WORK/observations.csv" --cli "$CARDANO_CLI" --timeout 20 --workers 40
fi

echo "4/5 loading observations + building reachability"
ssh "$ABCDE_SSH" "$PSQL -f -" < "$SQL_DIR/build_relay_reachability.sql" > /dev/null
ssh "$ABCDE_SSH" "$PSQL -c 'TRUNCATE relay.observation_stage'" > /dev/null
ssh "$ABCDE_SSH" "$PSQL -c \"\\copy relay.observation_stage (endpoint,endpoint_kind,endpoint_host,registered_port,target_host,target_port,resolved_ip,handshake_ok,block_no,slot_no,rtt_ms,failure,error_detail,attempts,checked_at) from stdin csv header\"" \
  < "$WORK/observations.csv" > /dev/null
ssh "$ABCDE_SSH" "$PSQL -c 'INSERT INTO relay.observation (endpoint,endpoint_kind,endpoint_host,registered_port,target_host,target_port,resolved_ip,handshake_ok,block_no,slot_no,rtt_ms,failure,error_detail,attempts,checked_at) SELECT endpoint,endpoint_kind,endpoint_host,registered_port,target_host,target_port,resolved_ip,handshake_ok,block_no,slot_no,rtt_ms,failure,error_detail,attempts,checked_at FROM relay.observation_stage'" > /dev/null
ssh "$ABCDE_SSH" "$PSQL -f -" < "$SQL_DIR/build_relay_reachability.sql" > /dev/null

echo "5/5 exporting public CSVs"
mkdir -p "$OUT"
export_csv() {  # $1 = out file, $2 = query
  ssh "$ABCDE_SSH" "$PSQL --csv -c \"$2\"" > "$REPO_ROOT/$1"
  echo "    wrote $1 ($(( $(wc -l < "$REPO_ROOT/$1") - 1 )) rows)"
}

export_csv data/small/relay_pool_health.csv "
  select pool_bech32, ticker, stake_ada, delegators, relay_entries, distinct_endpoints,
         registration_class, endpoints_probed, reachable_hosts, at_tip_hosts,
         endpoints_untested, best_rtt_ms, shares_endpoint_with_other_pool,
         reachability_class, last_checked
  from relay.pool_health order by stake_ada desc nulls last, pool_bech32"

export_csv data/small/relay_shared_endpoints.csv "
  select endpoint, endpoint_kind, pools, stake_ada, delegators,
         array_to_string(tickers, ' ') as tickers,
         array_to_string(pool_bech32s, ' ') as pool_bech32s
  from relay.endpoint_shared order by pools desc, stake_ada desc nulls last, endpoint"

export_csv data/small/relay_shared_hosts.csv "
  select resolved_ip, target_port, pools, stake_ada, delegators, distinct_registered_names,
         array_to_string(tickers, ' ') as tickers,
         array_to_string(pool_bech32s, ' ') as pool_bech32s
  from relay.shared_resolved_host order by pools desc, stake_ada desc nulls last, resolved_ip"

export_csv data/small/relay_shared_domains.csv "
  select domain, pools, stake_ada, delegators, array_to_string(tickers, ' ') as tickers
  from relay.shared_domain order by pools desc, stake_ada desc nulls last, domain"

export_csv data/small/relay_endpoint_status.csv "
  select endpoint, endpoint_kind, target_host, target_port, resolved_ip,
         handshake_ok, failure, error_detail, rtt_ms, block_no, slots_behind_best,
         at_tip, checked_at
  from relay.endpoint_status order by endpoint, target_host, target_port"

export_csv sql/56_relay_health/data/relay_build_receipt.csv "
  select run_at, stage, tip_block_no, tip_epoch_no, tip_time, stake_epoch, rows_out, notes
  from relay.build_receipt order by run_at desc limit 20"

( cd "$OUT" && sha256sum ./*.csv > SHA256SUMS )
echo "done. Regenerate the DuckDB + manifest before committing:"
echo "  python3 scripts/build_genesis_db.py"
echo "  python3 scripts/build_findings_json.py"
echo "  python3 scripts/build_public_artifact_manifest.py"

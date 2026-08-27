# 56_relay_health — registered relays, shared endpoints, observed reachability

Every stake pool publishes its relay set on-chain. That registration is a public
commitment: it is how the rest of the network is supposed to find the pool, and
it is the only part of a pool's infrastructure anyone can verify without trusting
the operator. This module turns it into a queryable dataset and adds one thing
the on-chain record cannot give you — whether those endpoints actually answer a
Cardano handshake.

Graded write-up: [`findings/F21_relay_registration_and_reachability.md`](../../findings/F21_relay_registration_and_reachability.md).
Method and limits: [`docs/27_RELAY_HEALTH_METHOD.md`](../../docs/27_RELAY_HEALTH_METHOD.md).

## Evidence grade (read first)

| Layer | Grade | What it supports |
|---|---|---|
| Registration rows (`relay.pool_current`, `relay.endpoint`) | **FACT** | What each pool published on-chain, and when. Reproducible by anyone with db-sync. |
| Shared endpoints (`relay.endpoint_shared`) | **FACT** of a shared string; **INFERENCE** of shared infrastructure | Several pools advertise one endpoint. A hosting provider, a white-label operator, and one person running twelve pools all look identical here. |
| Reachability (`relay.observation`, `relay.pool_health`) | **OBSERVATION** from one vantage point | This endpoint did / did not complete a handshake with our prober at that moment. |
| Ownership, identity, intent, "the relay is down" | **NOT CLAIMED** | Nothing in this module supports any of these. |

`unreachable` is not `offline`. A firewall that drops our prefix, an inbound
connection limit, a rate limiter, a restart, or a transient route all render as
`unreachable`. We have measured the same endpoint answering from one host and
timing out from another minutes later. Publish the observation, the vantage
point and the timestamp together, or do not publish it.

## Reproduce

```bash
ABCDE_SSH=<warehouse> PROBE_SSH=<probe host> CARDANO_CLI=./cardano-cli \
  scripts/build_relay_health_remote.sh
```

Stages: build registration → export targets → probe → load observations →
roll up → export CSVs. Roughly 9 minutes for ~4,200 endpoints at 40 workers.
The sweep needs `cardano-cli` (a static binary; copy it to the probe host) and
`dig`. Run it from a host with no Cardano production role.

## Four traps this module exists to encode

1. **`pool_stat` is empty** on db-sync 13.6.0.4. Stake and delegator counts come
   from `epoch_stake` at its own max epoch — which is normally one *ahead* of the
   tip block's epoch, because it is keyed by the epoch the stake is active for.
2. **`cardano-cli ping` hangs on an unresponsive peer** rather than failing, and
   returns no useful exit code. Every probe is wrapped in `timeout`; rc=124 is
   how "unreachable" is actually detected.
3. **`cardano-cli ping` does not resolve SRV records** (v11.0.0.0). Handed a
   multi-host relay name it does a plain A lookup on port 3001 and reports a
   bogus failure. `relay_probe.py` resolves `_cardano._tcp.<name>` itself. One
   SRV entry can expand to several hosts on non-standard ports — counting SRV
   pools as "single relay" is simply wrong.
4. **Never assume port 3001.** The registered port is authoritative and operators
   use anything: this dataset contains relays on 19002, 6010, 5001, 1338. A
   probe on the wrong port produces a confident false negative.

## Tables (schema `relay`, warehouse-local)

| table / view | what |
|---|---|
| `pool_current` | one row per pool with a live registration: latest `pool_update`, not retired, with stake / delegators / pledge / ticker |
| `endpoint` | one row per registered relay entry, normalised to a probe target |
| `pool_registration` | per-pool registration shape + `registration_class` |
| `endpoint_shared` | endpoints advertised by more than one current pool |
| `observation` | append-only probe log, one row per (endpoint, resolved target, sweep) |
| `endpoint_status` (view) | latest sweep per endpoint, with `at_tip` |
| `pool_health` | per-pool rollup + `reachability_class` |
| `build_receipt` | tip + stake epoch + row counts for every build |

`reachable_hosts` counts **distinct reachable hosts**, not registration entries.
Two DNS names pointing at one box is one relay, and that is exactly the pattern
this dataset exists to make visible.

## Data receipts

`data/` holds the committed build receipt and checksums. The published tables
are in `data/small/relay_*.csv` and land in the DuckDB as `relay_pool_health`,
`relay_shared_endpoints` and `relay_endpoint_status`. Each is a snapshot at the
recorded tip and sweep time — treat every current-state claim as of that moment.

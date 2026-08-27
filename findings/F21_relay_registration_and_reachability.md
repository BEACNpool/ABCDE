# F21 — Relay registration, shared infrastructure, and observed reachability

**Date:** 2026-08-27 · **Snapshot tip:** block 13,863,342 / epoch 651
(see `sql/56_relay_health/data/relay_build_receipt.csv`) · **Sweep:** 2026-08-27 13:37–14:33 UTC,
single vantage point. **Build:** `sql/56_relay_health/` + `scripts/relay_probe.py`.
**Method and limits, which bind any use of these numbers:**
[`docs/27_RELAY_HEALTH_METHOD.md`](../docs/27_RELAY_HEALTH_METHOD.md).

## Claim

Of 2,898 current Cardano stake pools, 43 have registered no
relay at all and 1,470 registered exactly one endpoint. In a two-pass
handshake sweep of all 5,064 registered endpoints, 1,632
pools had no endpoint that answered and 646 had two or more
distinct reachable hosts. Separately, 605 pools advertise a relay
endpoint that at least one other pool also advertises, and resolution collapses
further fleets that registration strings hide.

## Grade

- **FACT** — every registration figure: which pools are current, what relay
  entries they published, which endpoint strings are shared, and when each
  registration was made. Reproducible by anyone with db-sync.
- **FACT** — that a given endpoint did or did not complete a Cardano handshake
  with our prober at the stated time, and what tip it reported.
- **STRONG_INFERENCE** — that pools sharing an endpoint or a resolved host share
  infrastructure.
- **UNKNOWN / NOT CLAIMED** — whether any relay is "offline"; who operates any
  pool; whether shared infrastructure means shared ownership; whether any
  operator is negligent. Hosting providers, relay-as-a-service and white-label
  operators are indistinguishable here from one person running twelve pools.

## Why the two-pass sweep, and what a single pass would have published

Probe wall time is not handshake time and there is no fast path. Measured on
this build: `backbone.cardano.iog.io` answers in 5.2s while Trust Wallet's
Kiln-hosted relays take 14–30s — both reporting a protocol RTT near 100ms.
`cardano-cli ping -Q` (handshake only, no tip) is no faster on the slow ones.

A first sweep at a 10s timeout therefore marked **TW001 (113.6M ADA delegated)
as having no reachable relay.** It answers fine. That single number, published,
would have been false and would have travelled.

So every non-DNS failure is re-probed in a slower, lower-concurrency second
pass, and only a failure in both passes is recorded. The confirmation pass
recovered **30** endpoints that pass 1 called unreachable — that is
the measured false-negative rate of a single pass, and it is why nothing here
should be read from one sweep.

## Key figures

Registration (2,898 current pools, 21.42B ADA):

| Registration | Pools | ADA |
|---|---|---|
| One endpoint | 1,470 | 8.57B |
| Two or more endpoints | 1,340 | 11.26B |
| SRV (multi-host possible) | 45 | 1.14B |
| No relay registered | 43 | 445.1M |

Observed reachability, 2026-08-27 13:37–14:33 UTC, one vantage point:

| Reachability | Pools | ADA |
|---|---|---|
| Two or more hosts answered | 646 | 11.47B |
| One host answered | 576 | 6.96B |
| Nothing answered | 1,632 | 2.54B |
| No relay registered | 43 | 445.1M |
| Not testable from this probe | 1 | 8.7M |

Unreachability tracks stake almost monotonically — 95.1% of zero-stake
pools had nothing answer, against 11.0% of pools with 10M ADA or more.
A uniformly broken probe would not produce that gradient; abandoned pools that
never filed a retirement certificate do.

644 registered endpoints did not resolve in DNS at all, including
33 pools still advertising `relays-new.cardano-mainnet.iohk.io`,
a hostname that no longer exists.

## Shared infrastructure

Endpoints advertised by more than one current pool, by stake behind them:

| Endpoint | Pools | ADA | Delegators |
|---|---|---|---|
| `dns:cardano-relay-{1,2,3}.upbit.com` | 20 | 643.1M | 27 |
| `dns:cardano-{main,main2,relay,relay1,relay2}.everstake.one` | 15 | 631.2M | 267,342 |
| `ipv4:108.142.42.161 / .221 / 20.61.228.218` | 14 | 503.4M | 50 |
| `dns:relays.wavepool.digital` | 13 | 626.8M | 9,534 |

Delegator counts separate two very different patterns that the pool count alone
does not: an exchange or custodian operating many pools for itself, and a public
operator with hundreds of thousands of delegators.

**Registration strings badly understate sharing, and the gap is measurable.**
605 pools share a registered endpoint *string*. Grouping instead by the host those
names actually resolve to finds 249 shared hosts — and the largest is a set of six
IPs on port 6000 carrying **38 pools that registered 38 different hostnames**,
1.10B ADA and 34,221 delegators between them. Not one of those 38 appears in
`relay_shared_endpoints`, because no two of them wrote the same string.

By parent domain the same shape repeats:

| Domain | Pools | ADA | Delegators |
|---|---|---|---|
| `aeq5f.com` | 41 | 1.10B | 34,227 |
| `staked.cloud` | 34 | 1.11B | 141 |
| `bison.run` | 29 | 1.37B | 269 |
| `ddns.net` | 33 | 80.0M | 10,630 |
| `iohk.io` | 33 | 0.0M | 60 |

`ddns.net` is the counter-example that keeps this honest: it is a free dynamic-DNS
provider, and its 33 pools are 33 unrelated hobbyists, not a fleet. `iohk.io` is 33
pools pointing at a relay hostname that stopped resolving. A shared domain is a
place to look, never a conclusion — which is exactly why the pool count, the stake
and the delegator count are all published next to it.

All three views are floors, never ceilings: an endpoint we could not resolve
contributes nothing to any of them.

For an operator-clustering signal that does not depend on registration strings at
all, use `pool_operator_kes_clusters` — synchronized KES rotation, from block
headers ([`F10`](F10_kes_corotation_pool_operators.md)).

## Queryable

- `relay_pool_health` — one row per current pool: registration shape, class,
  reachable hosts, at-tip hosts, shared-endpoint flag, `last_checked`.
- `relay_shared_endpoints` — endpoint strings advertised by more than one pool.
- `relay_shared_hosts` — pools sharing a **resolved IP**.
- `relay_shared_domains` — pools sharing a parent domain (heuristic).
- `relay_endpoint_status` — the raw per-endpoint sweep, with failure cause.

```sql
SELECT reachability_class, count(*) AS pools, sum(stake_ada) AS ada
FROM relay_pool_health GROUP BY 1 ORDER BY 2 DESC;
```

## Reproduce

```bash
ABCDE_SSH=<warehouse> PROBE_SSH=<probe host> CARDANO_CLI=./cardano-cli \
  scripts/build_relay_health_remote.sh
```

Registration rebuilds in about 2 seconds and is fully reproducible from db-sync.
The sweep is a live measurement and will not reproduce exactly — that is the
nature of the layer, and why the two are kept in separate tables.

## What this finding is for, and what it is not for

Relay registration is the one part of a pool's infrastructure a delegator can
verify without trusting the operator, and checking it a pool at a time through a
public explorer does not scale to a network-wide question. This build makes the
whole surface queryable at once, off one warehouse, without putting load on
anyone's public API.

It is deliberately not a scoreboard. It reports what was registered and what was
observed, with the vantage point and timestamp attached, and it refuses to
convert either into a verdict about an operator. Readers who want to argue about
decentralization now have the numbers to argue with; the argument is theirs.

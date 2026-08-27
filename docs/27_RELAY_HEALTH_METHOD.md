# 27 — Relay registration and reachability: method and limits

This document binds any answer drawn from `relay_pool_health`,
`relay_shared_endpoints` or `relay_endpoint_status`. Read it before you repeat a
number from them, and quote its limits alongside the number.

Build: [`sql/56_relay_health/`](../sql/56_relay_health/) ·
Finding: [`findings/F21_relay_registration_and_reachability.md`](../findings/F21_relay_registration_and_reachability.md)

## Why this dataset exists

A pool's relay set is the one piece of its infrastructure anyone can verify
without trusting the operator: it is registered on-chain, in the same
certificate as the pledge and the margin. Delegators are routinely told to check
it, and the usual route is a block explorer's per-pool page — one pool at a
time, hand-checked, with the explorer's own probe behind it. That does not scale
to a whole-network question, and asking a public API for it 3,000 times is
antisocial.

So this module answers the network-wide version directly off db-sync, and adds
one measurement the chain cannot supply: whether the registered endpoints answer
a Cardano handshake.

## The two layers, and why they are kept apart

**Layer 1 — registration. FACT.** Which pools have a live registration, and what
relay entries that registration carries. Derived from `pool_update` /
`pool_relay` / `pool_retire`, reproducible by anyone with db-sync.

**Layer 2 — reachability. OBSERVATION.** Whether an endpoint completed a
node-to-node handshake with our prober, and what tip it reported.

They are separate tables on purpose. Layer 1 is durable and reproducible; layer
2 is a measurement from one place at one time and expires. Mixing them produces
the thing this dataset must not produce: a verdict about a pool.

## What "current pool" means

A pool's live registration is its **latest** `pool_update`. A `pool_retire`
certificate counts only if it was announced *after* that update — a later
re-registration cancels a pending retirement — and only once its `retiring_epoch`
has arrived. Both halves matter: ignore the first and you drop pools that
cancelled a retirement; ignore the second and you keep pools that are gone.
Pools with a retirement announced but not yet effective are included and flagged
`retire_pending`.

Stake and delegator counts come from `epoch_stake` at its own maximum epoch,
which is normally one epoch *ahead* of the tip block's epoch, because
`epoch_stake` is keyed by the epoch the stake is active **for**. `pool_stat` is
empty on db-sync 13.6.0.4 and is not used.

## What is probed, and how

One `cardano-cli ping` per registered endpoint: a real node-to-node handshake
plus a tip request, not a TCP connect. A successful TCP connection proves a port
is open, not that a Cardano relay is behind it.

- **ipv4 / ipv6 / dns** endpoints go straight to `cardano-cli`, on the
  **registered port**. It fans out over every A record of a DNS name on its own
  and reports one row per resolved IP, which is the behaviour we want.
- **SRV** endpoints are resolved first, by us: Cardano's multi-host relay type
  registers a bare domain whose record is `_cardano._tcp.<domain>`. Each SRV
  target carries its own port, from DNS, not from `pool_relay.port`.

`at_tip` compares a peer's reported slot against the **highest slot any peer
reported during the same sweep**, not against our own db-sync tip — a warehouse
lags the network by design, and grading other people's nodes against a lagging
local clock marks healthy relays as behind. The tolerance is 180 slots (~3
minutes), which absorbs propagation and the sweep's own duration.

`reachable_hosts` counts **distinct reachable hosts** — the resolved IP where we
have one — never registration entries. Two DNS names pointing at one machine is
one relay.

## Limits — all of these are load-bearing

- **`unreachable` is not `offline`.** It means the endpoint did not complete a
  handshake with *our* prober at *that* moment. A firewall that drops our prefix,
  an inbound connection limit, a rate limiter, a node restart, or a transient
  route all look identical. We have measured the same endpoint answering from
  one host and timing out from another minutes later.
- **One vantage point.** Every sweep in this repo is run from a single network
  location. Cross-checks from a second host behind the *same* egress rule out
  host-local faults only — they do not rule out anything that filters by IP or
  by prefix. Genuinely independent confirmation needs a probe on a different
  network, and this dataset does not have one.
- **One sweep is noise.** Reachability needs repeated sampling before any trend
  is readable. A single sweep supports "not reachable at 13:04 UTC" and nothing
  stronger.
- **A shared endpoint is a shared string.** It is strong evidence of shared
  infrastructure and no evidence at all of shared ownership. Hosting providers,
  relay-as-a-service, white-label operators and one person running twelve pools
  are indistinguishable here. For an operator-clustering signal that does not
  depend on registration strings, use `pool_operator_kes_clusters` (docs and
  caveats in `findings/F10_kes_corotation_pool_operators.md`).
- **Registration is not operation.** A pool can run relays it never registered,
  or register endpoints it has since moved. Both are visible only as a mismatch,
  never as an explanation.
- **Small pools are under-measured, not worse.** Nothing here scales with stake;
  a one-relay pool is a single point of failure at any size.

## What this dataset does not support

Any statement of the form "pool X is offline", "pool X is run by Y", "pool X is
negligent", or "these N pools are the same operator". The data supports what was
registered, and what was observed from one place at one time. Everything past
that is the reader's argument, and they should have to make it themselves.

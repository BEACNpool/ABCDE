#!/usr/bin/env python3
"""relay_probe.py — observe whether a pool's REGISTERED relay endpoints answer
the Cardano node-to-node handshake, and whether they are at the chain tip.

What this measures, exactly
---------------------------
For each registered endpoint we open one node-to-node connection and ask for the
peer's tip. A result is an OBSERVATION FROM ONE VANTAGE POINT AT ONE MOMENT.
It is not a property of the pool and it is not "the relay is down": a firewall
that drops our prefix, an inbound connection limit, a rate limiter, or a restart
all produce `unreachable` here while the relay serves its real peers fine.

Measured behaviour of `cardano-cli ping` (v11.0.0.0) that this script works around
-----------------------------------------------------------------------------
1. It HANGS on an unresponsive peer instead of failing. There is no useful exit
   code without a timeout; `timeout` producing rc=124 is the signal.
2. It does NOT resolve SRV records, despite Cardano's multi-host relay type.
   Given an SRV name it does a plain A lookup on port 3001 and reports a bogus
   failure. We resolve `_cardano._tcp.<name>` ourselves and probe each target.
3. It DOES fan out over every address of a DNS name on its own -- every family,
   in order -- reporting one row per resolved IP. That is the behaviour we want,
   so dns and ipv4 targets are handed to it directly. It also means a dual-stack
   peer is NOT mis-scored on a host without IPv6: the v6 attempt fails, the v4
   attempt decides. Only ipv6-ONLY endpoints are untestable, and those are
   reported as `no_ipv6_at_probe` rather than as unreachable.
4. Ports are whatever the operator registered. Assuming 3001 produces false
   `unreachable` results -- one pool in this dataset registers port 19002.
5. Wall time is NOT the handshake time and there is no fast path. Measured on
   this fleet: backbone.cardano.iog.io answers in 5.2s, Trust Wallet's
   Kiln-hosted relays take 14-30s -- while reporting a protocol RTT of 102ms.
   `-Q` (handshake only, no tip) is no faster on the slow ones. So any timeout
   under ~35s produces false negatives on real, healthy, high-stake pools, and
   the reported `rtt_ms` says nothing about how long the probe took. Pass 1 runs
   short on purpose for throughput; pass 2 is what makes the result honest.
6. Consequently a single pass is not publishable. Every failure that is not a
   DNS failure is re-probed in a second, slower, lower-concurrency pass, and
   only a failure in BOTH passes is recorded as unreachable. The script prints
   how many endpoints the confirmation pass recovered -- that number is the
   measured false-negative rate of pass 1 and belongs in the write-up.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

MAINNET_MAGIC = "764824073"
HAVE_IPV6 = False  # set in main(); see _detect_ipv6
SRV_PREFIX = "_cardano._tcp."
DEFAULT_PORT = 3001

# `cardano-cli ping` reports one line per address it tried, in the form
#   (AddrInfo {... addrFamily = AF_INET6, addrAddress = [..]:3001 ...},
#    Network.Socket.connect: <socket: 12>: does not exist (Network unreachable))
# Both getAddrInfo failures and connect failures contain the words "does not
# exist", so matching that phrase alone mislabels every refused connection as a
# DNS failure. Classification must key on WHICH call failed and on the errno
# text in the trailing parenthesis.
_ATTEMPT = re.compile(
    r"addrFamily = (AF_INET6|AF_INET)\b.*?Network\.Socket\.(\w+):[^()]*\(([^)]*)\)",
    re.S)
_GETADDRINFO_FAIL = re.compile(r"getAddrInfo.*?does not exist", re.S)


def _detect_ipv6() -> bool:
    """True only if this host has a global IPv6 default route."""
    try:
        out = subprocess.run(["ip", "-6", "route", "show", "default"],
                             capture_output=True, text=True, timeout=10).stdout
        return bool(out.strip())
    except Exception:
        return False


def _tidy(text: str, limit: int = 160) -> str:
    """One-line, length-capped detail -- raw errors are multi-line and comma-rich,
    which makes the published CSV hostile to naive parsers."""
    return re.sub(r"\s+", " ", (text or "")).strip()[:limit]


def classify(rc: int, err: str) -> tuple[str, str]:
    """Map a failed ping to (cause, detail).

    IPv4 attempts decide the verdict when present. On a probe host without a
    global IPv6 route an AF_INET6 'Network unreachable' is OUR limitation, and
    reporting it as the peer being down would be wrong.
    """
    if rc == 124:
        return "timeout", "no response within the probe timeout"
    if _GETADDRINFO_FAIL.search(err):
        return "dns_fail", "name did not resolve"

    attempts = _ATTEMPT.findall(err)
    v4 = [(call, reason) for fam, call, reason in attempts if fam == "AF_INET"]
    v6 = [(call, reason) for fam, call, reason in attempts if fam == "AF_INET6"]

    for call, reason in v4 or []:
        low = reason.lower()
        if "refused" in low:
            return "refused", reason
        if "unreachable" in low or "no route" in low:
            return "no_route", reason
        if "timed out" in low:
            return "timeout", reason
        return "error", f"{call}: {reason}"

    if v6 and not v4:
        # Only an IPv6 address was available and we cannot route IPv6.
        if any("unreachable" in r.lower() for _, r in v6):
            return "no_ipv6_at_probe", "probe host has no global IPv6 route"
        return "error", v6[0][1]

    return "error", _tidy(err) or "no output"


def resolve_srv(name: str, timeout: int) -> list[tuple[str, int]]:
    """Resolve a Cardano multi-host relay name to (host, port) targets.

    Cardano registers the bare domain; the record to query is
    `_cardano._tcp.<domain>`. Some operators publish the bare name instead, so
    that is tried as a fallback.
    """
    for qname in (SRV_PREFIX + name, name):
        try:
            out = subprocess.run(
                ["dig", "+short", "+time=3", "+tries=1", "SRV", qname],
                capture_output=True, text=True, timeout=timeout,
            ).stdout
        except (subprocess.TimeoutExpired, FileNotFoundError):
            continue
        targets = []
        for line in out.splitlines():
            parts = line.split()
            # priority weight port target -- anything else (e.g. a CNAME answer)
            # is not a usable SRV record and is skipped rather than guessed at.
            if len(parts) == 4 and parts[2].isdigit():
                targets.append((parts[3].rstrip("."), int(parts[2])))
        if targets:
            return targets
    return []


def ping(cli: str, host: str, port: int, timeout: int) -> tuple[list[dict], int, str]:
    """One node-to-node handshake + tip request. Returns (tips, rc, stderr)."""
    cmd = ["timeout", str(timeout), cli, "ping",
           "-h", host, "-p", str(port), "-m", MAINNET_MAGIC,
           "-c", "1", "-q", "-j", "-t"]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 10)
    except subprocess.TimeoutExpired:
        return [], 124, "outer timeout"
    if p.returncode != 0 or not p.stdout.strip():
        # One ~280-char block per address tried; keep enough for every family
        # or a dual-stack peer gets classified from its IPv6 attempt alone.
        return [], p.returncode, (p.stderr or p.stdout).strip()[:4000]
    try:
        return json.loads(p.stdout).get("tip", []), 0, ""
    except json.JSONDecodeError:
        return [], p.returncode, "unparseable json: " + p.stdout.strip()[:200]


def probe_one(cli: str, row: dict, timeout: int) -> list[dict]:
    """Probe one registered endpoint, expanding SRV into its real targets."""
    kind, host = row["endpoint_kind"], row["endpoint_host"]
    base = {
        "endpoint": row["endpoint"],
        "endpoint_kind": kind,
        "endpoint_host": host,
        "registered_port": row["port"] or "",
        "checked_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }

    if kind == "srv":
        targets = resolve_srv(host, timeout)
        if not targets:
            return [{**base, "target_host": host, "target_port": None,
                     "resolved_ip": None, "handshake_ok": False, "block_no": None,
                     "slot_no": None, "rtt_ms": None, "failure": "srv_no_record",
                     "error_detail": "no _cardano._tcp SRV record"}]
    elif kind == "ipv6" and not HAVE_IPV6:
        return [{**base, "target_host": host, "target_port": row["port"] or None,
                 "resolved_ip": None, "handshake_ok": False, "block_no": None,
                 "slot_no": None, "rtt_ms": None, "failure": "no_ipv6_at_probe",
                 "error_detail": "probe host has no global IPv6 route; "
                                 "this endpoint was not tested"}]
    elif kind in ("dns", "ipv4", "ipv6"):
        targets = [(host, int(row["port"]) if row["port"] else DEFAULT_PORT)]
    else:
        return [{**base, "target_host": host, "target_port": None, "resolved_ip": None,
                 "handshake_ok": False, "block_no": None, "slot_no": None,
                 "rtt_ms": None, "failure": "unsupported_endpoint_kind",
                 "error_detail": None}]

    out: list[dict] = []
    for thost, tport in targets:
        tips, rc, err = ping(cli, thost, tport, timeout)
        if not tips:
            cause, detail = classify(rc, err)
            out.append({**base, "target_host": thost, "target_port": tport,
                        "resolved_ip": None, "handshake_ok": False, "block_no": None,
                        "slot_no": None, "rtt_ms": None, "failure": cause,
                        "error_detail": detail})
            continue
        for t in tips:
            out.append({**base, "target_host": thost, "target_port": tport,
                        "resolved_ip": t.get("addr"), "handshake_ok": True,
                        "block_no": t.get("blockNo"), "slot_no": t.get("slotNo"),
                        "rtt_ms": round(float(t.get("rtt", 0)) * 1000, 2),
                        "failure": None, "error_detail": None})
    return out


FIELDS = ["endpoint", "endpoint_kind", "endpoint_host", "registered_port",
          "target_host", "target_port", "resolved_ip", "handshake_ok",
          "block_no", "slot_no", "rtt_ms", "failure", "error_detail",
          "attempts", "checked_at"]

# A DNS failure is a resolver answer, not a race, so it is not worth a slow
# retry. Everything else can be an artefact of our own concurrency.
# no_ipv6_at_probe is a limitation of the prober, not a peer failure -- retrying
# it changes nothing. dns_fail is a resolver answer. Neither is retried.
RETRYABLE = {"timeout", "error", "refused", "no_route"}


def run_pass(cli: str, rows: list[dict], timeout: int, workers: int,
             label: str) -> dict[str, list[dict]]:
    """Probe every row once. Returns {endpoint: [observation, ...]}."""
    out: dict[str, list[dict]] = {}
    started, done = time.time(), 0
    with ThreadPoolExecutor(max_workers=workers) as pool:
        for row, results in zip(rows, pool.map(
                lambda r: probe_one(cli, r, timeout), rows)):
            out[row["endpoint"] + "|" + str(row.get("port", ""))] = results
            done += 1
            if done % 200 == 0:
                rate = done / max(time.time() - started, 1e-9)
                print(f"  [{label}] {done}/{len(rows)} ({rate:.1f}/s)",
                      file=sys.stderr, flush=True)
    print(f"  [{label}] {len(rows)} endpoints in {time.time() - started:.0f}s",
          file=sys.stderr, flush=True)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--targets", required=True,
                    help="CSV with columns endpoint,endpoint_kind,endpoint_host,port")
    ap.add_argument("--out", required=True, help="CSV of observations to write")
    ap.add_argument("--cli", default="cardano-cli", help="path to cardano-cli")
    ap.add_argument("--timeout", type=int, default=20, help="seconds per handshake")
    ap.add_argument("--workers", type=int, default=40,
                    help="parallel probes; keep modest, these are other people's nodes")
    ap.add_argument("--confirm-timeout", type=int, default=40,
                    help="seconds per handshake in the confirmation pass")
    ap.add_argument("--confirm-workers", type=int, default=25,
                    help="parallelism for the confirmation pass; keep it low")
    ap.add_argument("--no-confirm", action="store_true",
                    help="skip the confirmation pass (produces false negatives; "
                         "for debugging only, never for published data)")
    ap.add_argument("--limit", type=int, default=0, help="probe only the first N targets")
    args = ap.parse_args()

    global HAVE_IPV6
    HAVE_IPV6 = _detect_ipv6()
    if not HAVE_IPV6:
        print("note: no global IPv6 route on this host -- ipv6-only endpoints "
              "will be reported as `no_ipv6_at_probe`, not as unreachable",
              file=sys.stderr)

    cli = shutil.which(args.cli) or args.cli
    try:
        subprocess.run([cli, "--version"], capture_output=True, check=True, timeout=30)
    except Exception as exc:
        print(f"cardano-cli not usable at {cli!r}: {exc}", file=sys.stderr)
        return 2

    with open(args.targets, newline="") as fh:
        rows = list(csv.DictReader(fh))
    if args.limit:
        rows = rows[: args.limit]

    print(f"pass 1: {len(rows)} endpoints, {args.timeout}s timeout, "
          f"{args.workers} workers", file=sys.stderr)
    first = run_pass(cli, rows, args.timeout, args.workers, "pass1")

    retry_rows = [r for r in rows
                  if any(o["failure"] in RETRYABLE
                         for o in first[r["endpoint"] + "|" + str(r.get("port", ""))])]
    final = dict(first)
    if retry_rows and not args.no_confirm:
        print(f"pass 2 (confirm): {len(retry_rows)} endpoints, "
              f"{args.confirm_timeout}s timeout, {args.confirm_workers} workers",
              file=sys.stderr)
        second = run_pass(cli, retry_rows, args.confirm_timeout,
                          args.confirm_workers, "pass2")
        recovered = 0
        for key, results in second.items():
            if any(o["handshake_ok"] for o in results) and \
                    not any(o["handshake_ok"] for o in first[key]):
                recovered += 1
            final[key] = results
        print(f"  recovered on retry: {recovered} endpoints that pass 1 called "
              f"unreachable", file=sys.stderr)

    with open(args.out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        for r in rows:
            key = r["endpoint"] + "|" + str(r.get("port", ""))
            attempts = 2 if any(o["failure"] in RETRYABLE for o in first[key]) \
                and not args.no_confirm else 1
            for res in final[key]:
                w.writerow({**res, "attempts": attempts})

    print(f"wrote {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

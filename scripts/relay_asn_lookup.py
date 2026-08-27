#!/usr/bin/env python3
"""relay_asn_lookup.py — map resolved relay IPs to the network that announces them.

Answers the question a pool count cannot: how much of Cardano's stake loses its
relays if ONE hosting provider has a bad day. A pool with three relays is not
redundant if all three sit in the same datacenter.

Source is Team Cymru's IP-to-ASN DNS interface: free, no key, no rate-limit
paperwork, and authoritative for BGP origin. Two record types are used --
`<reversed-ip>.origin.asn.cymru.com` for the announcing ASN, and
`AS<n>.asn.cymru.com` for that ASN's name -- the second cached per ASN, so a
few thousand IPs cost a few hundred name lookups.

An ASN is where a relay is HOSTED. It is not ownership, not an operator, and
not a claim that two pools in one datacenter are related -- Hetzner alone hosts
a large share of the hobbyist internet. Read it as concentration of failure
domain, which is the thing that actually matters here.
"""
from __future__ import annotations

import argparse
import csv
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

_TXT = re.compile(r'"([^"]*)"')


def _dig(name: str, timeout: int = 5) -> str | None:
    try:
        out = subprocess.run(["dig", "+short", "+time=3", "+tries=1", "TXT", name],
                             capture_output=True, text=True, timeout=timeout).stdout
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None
    m = _TXT.search(out)
    return m.group(1) if m else None


def origin_asn(ip: str) -> tuple[str | None, str | None, str | None]:
    """(asn, prefix, country) for an IPv4 address, or (None, None, None)."""
    parts = ip.split(".")
    if len(parts) != 4:
        return None, None, None          # IPv6 uses a different zone; not needed here
    rec = _dig(".".join(reversed(parts)) + ".origin.asn.cymru.com")
    if not rec:
        return None, None, None
    f = [x.strip() for x in rec.split("|")]
    # An IP can be announced by several ASNs; take the first and note it.
    return (f[0].split()[0] if f and f[0] else None,
            f[1] if len(f) > 1 else None,
            f[2] if len(f) > 2 else None)


def asn_name(asn: str) -> str | None:
    rec = _dig(f"AS{asn}.asn.cymru.com")
    if not rec:
        return None
    f = [x.strip() for x in rec.split("|")]
    return f[4] if len(f) > 4 else None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ips", required=True, help="CSV with a resolved_ip column, or '-' for stdin")
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=20)
    args = ap.parse_args()

    src = sys.stdin if args.ips == "-" else open(args.ips, newline="")
    ips = sorted({r["resolved_ip"].strip() for r in csv.DictReader(src)
                  if r.get("resolved_ip", "").strip()})
    print(f"{len(ips)} distinct IPs", file=sys.stderr)

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        origins = list(pool.map(origin_asn, ips))

    asns = sorted({a for a, _, _ in origins if a})
    print(f"{len(asns)} distinct ASNs; resolving names", file=sys.stderr)
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        names = dict(zip(asns, pool.map(asn_name, asns)))

    with open(args.out, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["resolved_ip", "asn", "as_name", "prefix", "country"])
        for ip, (asn, prefix, cc) in zip(ips, origins):
            w.writerow([ip, asn or "", names.get(asn) or "", prefix or "", cc or ""])
    print(f"wrote {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

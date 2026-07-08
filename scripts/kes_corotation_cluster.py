#!/usr/bin/env python3
"""KES co-rotation clustering — the pair-scoring + connected-components step.

Reads the SQL-derived inputs (poolsync.tight, poolsync.pool_info, and the
shared_* corroboration tables, exported to CSV by build_kes_corotation.sql —
see sql/55_pool_operators/README.md) and writes the cluster membership back as
CSV for loading into poolsync.cluster.

Method (stdlib only — no numpy):
  * Candidate pairs: two pools whose tight rotation events (gap <= 48h) fall
    within +/- W of each other at least MIN_CO times.
  * Significance: greedy 1-1 match the two event series within +/- W, then test
    the match count against an EMPIRICAL null — expected matches if the second
    pool's events were drawn from the chain-wide distribution of all rotation
    times (Poisson tail, p <= MAX_P). This absorbs network-upgrade bursts, when
    everyone rotates on the same day and co-rotation is uninformative.
  * A pair also needs the match to cover >= MIN_RATE of the smaller pool's events.
  * Clusters = connected components of surviving pairs (union-find).

EVIDENCE GRADE: a surviving cluster is a FACT of synchronized rotation, i.e.
shared OPERATIONAL control. It is NOT proof of shared ownership. Rarely-minting
pools carry wide timing windows and are missed -> every cluster is a floor.

Usage:
  python scripts/kes_corotation_cluster.py --indir <csv_dir> --out cluster.csv
  # then: \copy poolsync.cluster(cluster_id,pool_hash_id) from 'cluster.csv' csv header
"""
import argparse
import csv
import math
from bisect import bisect_left, bisect_right
from collections import defaultdict
from datetime import datetime, timedelta

W = timedelta(hours=24)      # co-rotation window (+/-)
MIN_CO = 5                   # raw co-rotations required
MAX_P = 1e-9                 # Poisson-null p-value ceiling
MIN_RATE = 0.5               # match must cover >= this share of the smaller pool
MIN_N = 6                    # ignore pools with fewer than this many tight events


def poisson_tail(lam, k):
    """P(X >= k) for X ~ Poisson(lam), log-safe."""
    if lam <= 0:
        return 0.0 if k > 0 else 1.0
    logp = -lam + k * math.log(lam) - math.lgamma(k + 1)
    total, term, i = 0.0, math.exp(min(logp, 700)), k
    while term > 1e-320 and i < k + 2000:
        total += term
        i += 1
        term *= lam / i
    return min(total, 1.0)


def merged_windows(ev):
    ivs = []
    for t in ev:
        lo, hi = t - W, t + W
        if ivs and lo <= ivs[-1][1]:
            ivs[-1] = (ivs[-1][0], max(ivs[-1][1], hi))
        else:
            ivs.append((lo, hi))
    return ivs


def load(indir):
    events = defaultdict(list)
    allev = []
    with open(f"{indir}/tight.csv") as f:
        for row in csv.DictReader(f):
            t = datetime.fromisoformat(row["first_seen"])
            p = int(row["pool_hash_id"])
            events[p].append(t)
            allev.append((t, p))
    for v in events.values():
        v.sort()
    allev.sort()
    return events, allev


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--indir", required=True, help="dir with tight.csv (and optionally pool_info.csv)")
    ap.add_argument("--out", required=True, help="output cluster.csv (cluster_id,pool_hash_id)")
    args = ap.parse_args()

    events, allev = load(args.indir)
    tvec = [t for t, _ in allev]

    def pools_near(t):
        lo, hi = bisect_left(tvec, t - W), bisect_right(tvec, t + W)
        return {p for _, p in allev[lo:hi]}

    # candidate pairs via a single sweep
    cand = defaultdict(int)
    for t, p in allev:
        for q in pools_near(t):
            if q > p:
                cand[(p, q)] += 1
    cand = {k: v for k, v in cand.items() if v >= MIN_CO}

    def greedy_co(ea, eb, pa, pb):
        co, used = 0, set()
        for t in ea:
            lo, hi = bisect_left(eb, t - W), bisect_right(eb, t + W)
            best = None
            for k in range(lo, hi):
                if k in used:
                    continue
                if best is None or abs((eb[k] - t).total_seconds()) < abs((eb[best] - t).total_seconds()):
                    best = k
            if best is not None:
                used.add(best)
                co += 1
        # empirical null: expected matches under the chain-wide rotation-time law
        K = 0
        for lo, hi in merged_windows(ea):
            i, j = bisect_left(tvec, lo), bisect_right(tvec, hi)
            K += sum(1 for _, p in allev[i:j] if p != pa and p != pb)
        N = len(allev) - len(ea) - len(eb)
        lam = len(eb) * K / max(1, N)
        return co, lam

    pairs = []
    for (pa, pb) in cand:
        ea, eb = events[pa], events[pb]
        if min(len(ea), len(eb)) < MIN_N:
            continue
        co, lam = greedy_co(ea, eb, pa, pb)
        rate = co / min(len(ea), len(eb))
        if co >= MIN_CO and rate >= MIN_RATE and poisson_tail(lam, co) <= MAX_P:
            pairs.append((pa, pb))

    # union-find -> connected components
    parent = {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for pa, pb in pairs:
        parent[find(pa)] = find(pb)
    comp = defaultdict(set)
    for pa, pb in pairs:
        comp[find(pa)].update((pa, pb))

    # emit, numbering clusters by descending size (stable enough for receipts)
    clusters = sorted(comp.values(), key=lambda m: -len(m))
    with open(args.out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["cluster_id", "pool_hash_id"])
        for cid, members in enumerate(clusters, 1):
            for p in sorted(members):
                w.writerow([cid, p])
    print(f"{len(cand)} candidate pairs -> {len(pairs)} significant -> "
          f"{len(clusters)} clusters, {sum(len(m) for m in clusters)} pools")


if __name__ == "__main__":
    main()

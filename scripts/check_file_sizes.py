#!/usr/bin/env python3
"""Guard against committing files that strain GitHub or clone-and-ask usability.

Policy (docs: GitHub warns at 50 MiB, blocks at 100 MiB):
  - warn at 10 MiB        (consider a release asset + committed top-cut)
  - fail at 50 MiB        (unless explicitly allowlisted below)
  - fail at 100 MiB       (always; GitHub would block the push)

Checks git-tracked files plus staged/untracked candidates so problems surface
before commit, not after.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

WARN_BYTES = 10 * 1024 * 1024
FAIL_BYTES = 50 * 1024 * 1024
HARD_BYTES = 100 * 1024 * 1024

# Paths allowed between 50 and 100 MiB. Keep this list short and deliberate.
ALLOWLIST: set[str] = set()


def candidate_files() -> list[Path]:
    out = subprocess.check_output(
        ["git", "-C", str(ROOT), "ls-files", "--cached", "--others",
         "--exclude-standard"],
        text=True,
    )
    return [ROOT / line for line in out.splitlines() if line]


def main() -> None:
    warnings, failures = [], []
    for path in candidate_files():
        if not path.is_file():
            continue
        size = path.stat().st_size
        rel = path.relative_to(ROOT).as_posix()
        if size >= HARD_BYTES:
            failures.append(f"{rel}: {size/2**20:.1f} MiB >= 100 MiB (GitHub hard block)")
        elif size >= FAIL_BYTES and rel not in ALLOWLIST:
            failures.append(f"{rel}: {size/2**20:.1f} MiB >= 50 MiB (use a release asset)")
        elif size >= WARN_BYTES:
            warnings.append(f"{rel}: {size/2**20:.1f} MiB >= 10 MiB (consider release asset + top-cut)")
    for w in warnings:
        print(f"WARN  {w}")
    for f in failures:
        print(f"FAIL  {f}", file=sys.stderr)
    if failures:
        raise SystemExit(1)
    print(f"file-size policy OK ({len(warnings)} warning(s))")


if __name__ == "__main__":
    main()

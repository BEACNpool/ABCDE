#!/usr/bin/env python3
"""Rewrite manifested files whose working copy differs from git ONLY by line endings.

Why this exists: `.gitattributes` sets `* text=auto eol=lf`, so git stores LF
blobs, but a working copy can end up CRLF. `git status` treats that as clean
(normalization), so the CRLF never gets fixed — while
scripts/build_public_artifact_manifest.py hashes WORKING COPIES. The manifest
then records CRLF hashes, CI checks out LF blobs, and verify_public_artifacts
fails on files nobody touched.

Why it is written defensively: the obvious version — "rewrite every file from its
blob" — is destructive. Run before `git add`, it silently reverts your actual
work; run after regenerating a derived file, it silently reverts that too. Both
happened here on 2026-08-28, once reverting nine freshly exported CSVs and once
reverting the schema catalogs. So this only ever touches files whose content is
identical once line endings are normalised, and it reports anything else instead
of overwriting it.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIRS = ["claims", "data/small", "docs", "findings", "profiles", "prompts", "reports", "sql"]


def blob(path: str) -> bytes | None:
    r = subprocess.run(["git", "-C", str(ROOT), "show", f":{path}"], capture_output=True)
    return r.stdout if r.returncode == 0 else None


def main() -> int:
    fixed, differ = 0, []
    for d in DIRS:
        out = subprocess.run(["git", "-C", str(ROOT), "ls-files", "-z", d],
                             capture_output=True).stdout
        for raw in out.split(b"\0"):
            if not raw:
                continue
            rel = raw.decode()
            b = blob(rel)
            if b is None:
                continue
            f = ROOT / rel
            try:
                w = f.read_bytes()
            except OSError:
                continue
            if w == b:
                continue
            if w.replace(b"\r\n", b"\n") == b.replace(b"\r\n", b"\n"):
                f.write_bytes(b)          # same content, wrong line endings
                fixed += 1
            else:
                differ.append(rel)        # real change — never touch it

    print(f"normalize_line_endings: {fixed} file(s) had line endings corrected")
    if differ:
        print(f"  {len(differ)} file(s) differ in CONTENT and were left alone "
              f"(stage them before building the manifest):")
        for rel in differ[:20]:
            print(f"    {rel}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Syntax-check the inline JavaScript in the static site pages.

Why this exists: a duplicated `const` shipped to production and blanked the
entire relay page. It was a PARSE error, so nothing ran at all -- no tables, no
fetch, just "Loading...". The deploy had been checked by curling the HTML for
section headings and the JSON for its keys, and both passed, because neither can
see a syntax error.

`node --check` sees it in milliseconds. If node is not installed the check is
skipped rather than failed, so the repo stays clonable without a JS toolchain.
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "web" / "dist"
SCRIPT = re.compile(r"<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>", re.S | re.I)
# Every "source" link on a page points at a real file in this repo. They rot
# silently otherwise -- the README's tour video 404'd for 34 days before anyone
# noticed, and a broken link in the section that says "check my work" is worse
# than no link at all.
REPO_LINK = re.compile(r"https://github\.com/BEACNpool/ABCDE/blob/main/([^\"'\s>)]+)")


def main() -> int:
    node = shutil.which("node")
    if not node:
        print("verify_web_pages: node not found, skipping JS syntax check")
        return 0

    pages = sorted(DIST.glob("*.html")) + sorted(DIST.glob("*.js"))
    if not pages:
        print("verify_web_pages: no pages found")
        return 0

    failures = 0
    for page in pages:
        text = page.read_text(encoding="utf-8", errors="replace")
        blocks = [text] if page.suffix == ".js" else SCRIPT.findall(text)
        for i, js in enumerate(blocks):
            if not js.strip():
                continue
            with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as fh:
                fh.write(js)
                tmp = fh.name
            try:
                r = subprocess.run([node, "--check", tmp], capture_output=True, text=True)
            finally:
                Path(tmp).unlink(missing_ok=True)
            label = f"{page.relative_to(ROOT)}" + (f" [script {i + 1}]" if len(blocks) > 1 else "")
            if r.returncode:
                first = (r.stderr.strip().splitlines() or ["syntax error"])
                detail = next((l for l in first if "Error" in l), first[0])
                print(f"  [FAIL] {label}: {detail.strip()}")
                failures += 1
            else:
                print(f"  [PASS] {label}")

    seen: set[str] = set()
    for page in sorted(DIST.glob("*.html")):
        for rel in REPO_LINK.findall(page.read_text(encoding="utf-8", errors="replace")):
            rel = rel.split("#")[0]
            if rel in seen:
                continue
            seen.add(rel)
            if (ROOT / rel).exists():
                print(f"  [PASS] link -> {rel}")
            else:
                print(f"  [FAIL] link -> {rel} does not exist in the repo")
                failures += 1

    print(f"verify_web_pages: {failures} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

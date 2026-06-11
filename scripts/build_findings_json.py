#!/usr/bin/env python3
"""Generate findings/findings.json — machine-readable claim ⇄ evidence ⇄ hash map.

Parses findings/F*.md (sections: Claim, Grade, Evidence, Reproduce), joins
status labels from findings/INDEX.md and SHA-256 hashes from
data/manifests/public-artifacts-manifest.json, and writes a deterministic JSON
artifact so an agent can answer "what is FACT vs hypothesis, and on what
evidence" without parsing prose.

Usage:
  python scripts/build_findings_json.py          # write findings/findings.json
  python scripts/build_findings_json.py --check  # fail if committed file is stale
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FINDINGS_DIR = ROOT / "findings"
INDEX = FINDINGS_DIR / "INDEX.md"
MANIFEST = ROOT / "data" / "manifests" / "public-artifacts-manifest.json"
OUT = FINDINGS_DIR / "findings.json"

HEADING_RE = re.compile(r"^#\s+(F\d+\w*)\s+—\s+(.+)$")
SECTION_RE = re.compile(r"^##\s+(.+)$")
INDEX_ROW_RE = re.compile(r"\[(F\d+\w*)\s+—[^\]]*\]\(([^)]+)\)\s+—\s+(.+)$")
PATH_RE = re.compile(r"`((?:data|sql|scripts|reports|docs)/[^`]+)`")


def load_manifest_hashes() -> dict[str, str]:
    if not MANIFEST.exists():
        return {}
    payload = json.loads(MANIFEST.read_text())
    return {f["path"]: f["sha256"] for f in payload.get("files", [])}


def load_index_labels() -> dict[str, str]:
    labels: dict[str, str] = {}
    if not INDEX.exists():
        return labels
    for line in INDEX.read_text().splitlines():
        m = INDEX_ROW_RE.search(line)
        if m:
            labels[m.group(1)] = m.group(3).strip().replace("`", "")
    return labels


def parse_finding(path: Path) -> dict | None:
    lines = path.read_text().splitlines()
    if not lines:
        return None
    m = HEADING_RE.match(lines[0])
    if not m:
        return None
    finding_id, title = m.group(1), m.group(2).strip()

    sections: dict[str, list[str]] = {}
    current = None
    for line in lines[1:]:
        sm = SECTION_RE.match(line)
        if sm:
            current = sm.group(1).strip().lower()
            sections[current] = []
        elif current is not None:
            sections[current].append(line)

    def text_of(name: str) -> str:
        return "\n".join(sections.get(name, [])).strip()

    evidence_paths = sorted(set(PATH_RE.findall(text_of("evidence"))))
    return {
        "id": finding_id,
        "file": path.relative_to(ROOT).as_posix(),
        "title": title,
        "claim": text_of("claim"),
        "grade": text_of("grade"),
        "evidence": evidence_paths,
        "has_reproduce_sql": "```sql" in text_of("reproduce"),
    }


def build() -> dict:
    hashes = load_manifest_hashes()
    labels = load_index_labels()
    findings = []
    for path in sorted(FINDINGS_DIR.glob("F*.md")):
        item = parse_finding(path)
        if item is None:
            continue
        item["index_label"] = labels.get(item["id"], "")
        item["evidence"] = [
            {"path": p, "sha256": hashes.get(p)} for p in item["evidence"]
        ]
        findings.append(item)
    return {
        "schema_version": 1,
        "generated_by": "scripts/build_findings_json.py",
        "grading_reference": "docs/02_GRADING.md",
        "finding_count": len(findings),
        "findings": findings,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true",
                        help="verify the committed findings.json is current")
    args = parser.parse_args()
    payload = json.dumps(build(), indent=2, ensure_ascii=False) + "\n"
    if args.check:
        if not OUT.exists() or OUT.read_text() != payload:
            print("findings/findings.json is stale; run scripts/build_findings_json.py",
                  file=sys.stderr)
            raise SystemExit(1)
        print("findings.json OK")
        return
    OUT.write_text(payload)
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

_HEX64 = re.compile(r'^[0-9a-f]{64}$')

@dataclass(frozen=True)
class SeedAnchor:
    seed_id: str
    label: str
    tx_hash: str
    amount_ada: int
    source_type: str
    evidence_grade: str
    notes: str | None = None


def _parse_simple_yaml(path: Path) -> list[SeedAnchor]:
    """Tiny anchors.yaml parser for the constrained manifest shape.

    Avoids requiring PyYAML for the first scaffold; replace with PyYAML once dependencies exist.
    """
    seeds: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    for raw in path.read_text().splitlines():
        line = raw.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith('#') or stripped in {'version: 1', 'seeds:'}:
            continue
        if stripped.startswith('- '):
            if current:
                seeds.append(current)
            current = {}
            stripped = stripped[2:]
        if ':' in stripped and current is not None:
            key, value = stripped.split(':', 1)
            current[key.strip()] = value.strip().strip('"\'')
    if current:
        seeds.append(current)
    anchors: list[SeedAnchor] = []
    for item in seeds:
        tx_hash = item['tx_hash']
        if not _HEX64.match(tx_hash):
            raise ValueError(f"Invalid tx_hash for {item.get('seed_id')}: {tx_hash}")
        anchors.append(SeedAnchor(
            seed_id=item['seed_id'],
            label=item['label'],
            tx_hash=tx_hash,
            amount_ada=int(item['amount_ada']),
            source_type=item['source_type'],
            evidence_grade=item['evidence_grade'],
            notes=item.get('notes'),
        ))
    return anchors


def load_anchors(path: str | Path) -> list[SeedAnchor]:
    return _parse_simple_yaml(Path(path))

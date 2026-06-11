#!/usr/bin/env python3
"""Build SHA-256 manifest for public v2 artifacts committed to git."""
from __future__ import annotations
import csv
import hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/manifests/public-artifacts-manifest.json'
DB_TIP=ROOT/'data/small/db_tip_receipt.csv'
INCLUDE_DIRS=[
    ROOT/'claims',
    ROOT/'data/small',
    ROOT/'docs',
    ROOT/'findings',
    ROOT/'profiles',
    ROOT/'prompts',
    ROOT/'reports',
    ROOT/'sql',
]

def sha256_file(p:Path)->str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024), b''): h.update(chunk)
    return h.hexdigest()

def load_source_block():
    if not DB_TIP.exists():
        return None
    with DB_TIP.open(newline='', encoding='utf-8') as f:
        rows=list(csv.DictReader(f))
    if not rows:
        return None
    row=rows[0]
    return {
        'generated_by':'scripts/build_public_artifact_manifest.py',
        'db_tip_block':row.get('db_tip_block'),
        'db_tip_time':row.get('db_tip_time'),
        'db_tip_epoch':row.get('db_tip_epoch'),
        'source':row.get('source'),
        'staleness_note':row.get('staleness_note'),
    }

def main():
    files=[]
    source=load_source_block()
    for d in INCLUDE_DIRS:
        if not d.exists(): continue
        for p in sorted(d.rglob('*')):
            if p.is_file():
                item={'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':sha256_file(p)}
                if source:
                    item['source']=source
                files.append(item)
    payload={'schema_version':2,'file_count':len(files),'files':files}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2)+'\n')
    print(f'wrote {OUT.relative_to(ROOT)} files={len(files)}')
if __name__=='__main__': main()

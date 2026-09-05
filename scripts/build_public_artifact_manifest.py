#!/usr/bin/env python3
"""Build SHA-256 manifest for public v2 artifacts committed to git."""
from __future__ import annotations
import csv
import hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/manifests/public-artifacts-manifest.json'
DB_TIP=ROOT/'data/small/db_tip_receipt.csv'
FINDINGS_INDEX=ROOT/'findings/findings.json'
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
    receipt_path=ROOT/'data/small/founding_query_receipts.csv'
    founding_sources={}
    if receipt_path.exists():
        with receipt_path.open(newline='', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                founding_sources['data/small/'+row['table_name']+'.csv']={
                    'receipt':receipt_path.relative_to(ROOT).as_posix(),
                    **{key:row[key] for key in ('source_kind','collection_started_utc',
                        'collection_finished_utc','db_tip_block','db_tip_epoch',
                        'db_tip_time','db_tip_hash','query_path') if row.get(key)},
                }
    import sys as _sys
    _sys.path.insert(0, str(ROOT / 'scripts'))
    from build_genesis_db import SKIP_TABLE_STEMS  # don't hash unshipped build inputs
    skip_names={f'{s}.csv' for s in SKIP_TABLE_STEMS}
    for d in INCLUDE_DIRS:
        if not d.exists(): continue
        for p in sorted(d.rglob('*')):
            if p.is_file():
                # findings.json is generated from this manifest. Hashing it here
                # creates an impossible circular dependency after every finding
                # update, so fingerprint its source Markdown instead.
                if p == FINDINGS_INDEX:
                    continue
                if p.name in skip_names and p.parent.name=='small':
                    continue
                item={'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':sha256_file(p)}
                if item['path'] in founding_sources:
                    item['source']=founding_sources[item['path']]
                elif (p.stem.startswith('founding_') or p.parent.name=='35_founding_entities'
                      or p.name=='28_FOUNDER_ACCOUNTABILITY_EVIDENCE.md'
                      or p.name.startswith('F22_')):
                    item['source']={'manifest':'data/manifests/founding-evidence-manifest.json',
                                    'note':'Consult per-table receipts; chain, disclosure and historical-selection boundaries differ.'}
                elif source:
                    item['source']=source
                files.append(item)
    evidence_manifest=ROOT/'data/manifests/founding-evidence-manifest.json'
    if evidence_manifest.exists():
        files.append({'path':evidence_manifest.relative_to(ROOT).as_posix(),
                      'bytes':evidence_manifest.stat().st_size,'sha256':sha256_file(evidence_manifest)})
    payload={'schema_version':2,'file_count':len(files),'files':files}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2)+'\n')
    print(f'wrote {OUT.relative_to(ROOT)} files={len(files)}')
if __name__=='__main__': main()

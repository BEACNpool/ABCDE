#!/usr/bin/env python3
"""Build SHA-256 manifest for public v2 artifacts committed to git."""
from __future__ import annotations
import hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/manifests/public-artifacts-manifest.json'
INCLUDE_DIRS=[ROOT/'data/small', ROOT/'reports', ROOT/'findings', ROOT/'docs', ROOT/'profiles']

def sha256_file(p:Path)->str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024), b''): h.update(chunk)
    return h.hexdigest()

def main():
    files=[]
    for d in INCLUDE_DIRS:
        if not d.exists(): continue
        for p in sorted(d.rglob('*')):
            if p.is_file():
                files.append({'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':sha256_file(p)})
    payload={'schema_version':1,'file_count':len(files),'files':files}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2)+'\n')
    print(f'wrote {OUT.relative_to(ROOT)} files={len(files)}')
if __name__=='__main__': main()

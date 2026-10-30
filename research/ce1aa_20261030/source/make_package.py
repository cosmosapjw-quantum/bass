#!/usr/bin/env python3
"""Fail-closed archives of one physical research unit, 20 per-stage checkpoints."""
from __future__ import annotations
import json,hashlib,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'checkpoints';OUT.mkdir(exist_ok=True)
def sha(b):return hashlib.sha256(b).hexdigest()
def package(path,files):
    payload={str(p.relative_to(ROOT)):p.read_bytes() for p in sorted(set(files)) if p.is_file()}
    man={'schema':'bass.ce1aa.manifest.v1','upper_dag':'9/15','payload':{x:{'size':len(v),'sha256':sha(v)} for x,v in payload.items()}}
    with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=7) as z:
        for k,b in payload.items():z.writestr(k,b)
        z.writestr('MANIFEST_SHA256.json',json.dumps(man,sort_keys=True,indent=2)+'\n')
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        for k,v in man['payload'].items():assert sha(z.read(k))==v['sha256'] and len(z.read(k))==v['size']
    print(path.name,path.stat().st_size,len(payload),sha(path.read_bytes()),flush=True)
    return man

def main():
    for f in sorted((ROOT/'stages').glob('*.json')):
        package(OUT/(f'CE1AA_STAGE_{f.stem}_20261030.zip'),[f])
    initial=[ROOT/n for n in ['THEORY_KO.md','REPRODUCE.md','STAGE_LEDGER.json','DAG_DELTA.json']]
    allfiles=initial[:]
    for folder in ['input','source','tests','data','stages','figures']:
        allfiles += [p for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and not p.name.startswith('GL8_mpfr192_source_1')]
    allfiles+=[ROOT/'REPORT_KO.md',ROOT/'HANDOFF_NEXT_KO.md']
    package(OUT/'CE1AA_S1_MPFR192_PHYSICS_20261030.zip',allfiles)
    allfiles+= [p for p in OUT.glob('CE1AA_STAGE_*.zip')] + [OUT/'S0_THEORY_20261030.zip',OUT/'CE1AA_S1_MPFR192_PHYSICS_20261030.zip']
    package(Path('/mnt/data/BASS_CE1AA_MPFR192_SOURCE_SECOND_MODE_20261030_FULL.zip'),allfiles)
if __name__=='__main__':main()

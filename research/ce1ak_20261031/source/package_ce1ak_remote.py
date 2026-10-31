#!/usr/bin/env python3
"""Deterministic CE1AK GitHub CI science, source-inclusive and stage checkpoint archives."""
from __future__ import annotations
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED, ZipInfo
import hashlib, json

ROOT=Path(__file__).resolve().parents[1]
RESEARCH=ROOT.parent
DIST=ROOT/'dist'
DIST.mkdir(exist_ok=True)
STAMP=(2026,10,31,0,0,0)
COMP=ZIP_DEFLATED

def as_zip(name, files, extra=None):
    target=DIST/name
    manifest={'schema':'bass.ce1ak.archive.v1','source_sha256':'022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035',
      'upper_DAG':'9/15','CE1':'PARTIAL','files':{}}
    with ZipFile(target,'w',COMP,compresslevel=6) as z:
        for file in sorted(set(files), key=lambda p:str(p)):
            rel=file.relative_to(RESEARCH).as_posix()
            data=file.read_bytes()
            info=ZipInfo(rel,STAMP);info.compress_type=COMP
            z.writestr(info,data,compress_type=COMP,compresslevel=6)
            manifest['files'][rel]={'size':len(data),'sha256':hashlib.sha256(data).hexdigest()}
        if extra:
            for rel,data in sorted(extra.items()):
                info=ZipInfo(rel,STAMP);info.compress_type=COMP
                z.writestr(info,data,compress_type=COMP,compresslevel=6)
                manifest['files'][rel]={'size':len(data),'sha256':hashlib.sha256(data).hexdigest()}
        info=ZipInfo('MANIFEST.json',STAMP);info.compress_type=COMP
        z.writestr(info,json.dumps(manifest,indent=2,sort_keys=True)+'\n',compress_type=COMP,compresslevel=6)
    with ZipFile(target) as z:
        if z.testzip() is not None:raise RuntimeError('CRC failure')
        mm=json.loads(z.read('MANIFEST.json'))
        for f,rec in mm['files'].items():
            if hashlib.sha256(z.read(f)).hexdigest()!=rec['sha256']:raise RuntimeError(f)
    return target

def files_at(dir):
    return [f for f in dir.rglob('*') if f.is_file() and
            '__pycache__' not in f.parts and '/dist/' not in f.as_posix() and
            not f.name.endswith(('.pyc','.pyo'))]

def main():
    source=[f for f in files_at(ROOT) if any(part in f.parts for part in
       ('source','checkpoints')) or f.suffix in ('.md','.json') and 'data' not in f.parts]
    physical=files_at(ROOT/'data')+files_at(ROOT/'figures')
    final=[]
    for title,files in [
       ('CE1AK_S0_THEORY_SOURCE_STAGES.zip',source),
       ('CE1AK_S1_REAL_PHYSICAL_HISTORY.zip',physical),
       ('CE1AK_S2_ANCESTOR_SOURCE_INCLUSIVE.zip',source+physical+
        sum((files_at(RESEARCH/f'ce1{name}_20261031') for name in ('aj','ai','ah','ag')),[])+
        files_at(RESEARCH/'ce1af_20261030'))
    ]:
        final.append(as_zip(title,files))
    stages=[]
    for f in sorted((ROOT/'checkpoints').glob('*.json')):
        idx=f.stem
        stages.append(as_zip('CE1AK_STAGE_'+idx+'.zip',[f]))
    with ZipFile(DIST/'CE1AK_STAGE_PACK_20.zip','w',COMP,compresslevel=6) as z:
        for f in stages:
            info=ZipInfo(f.name,STAMP);info.compress_type=COMP
            z.writestr(info,f.read_bytes(),compress_type=COMP,compresslevel=6)
    with ZipFile(DIST/'CE1AK_STAGE_PACK_20.zip') as z:
        if z.testzip() is not None or len(z.namelist())!=20:raise RuntimeError('Stages missing')
    print('CE1AK_SOURCE_ARCHIVES',[(f.name,f.stat().st_size) for f in final])
    print('CE1AK_STAGES',len(stages))
if __name__=='__main__':main()

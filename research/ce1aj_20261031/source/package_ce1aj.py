#!/usr/bin/env python3
"""Package durable original research+code+science payload with SHA256 and ZIP CRC checks."""
from pathlib import Path
import zipfile,json,hashlib
ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[1]
DIST=ROOT/'dist'
DIST.mkdir(exist_ok=True,parents=True)

def sha(raw):return hashlib.sha256(raw).hexdigest()
def grab(prefix,folder):
    out={}
    for p in sorted(folder.rglob('*')):
        if not p.is_file() or any(k in p.parts for k in ('__pycache__','.pytest_cache','dist','.git')):continue
        if p.suffix=='.pyc':continue
        out[prefix+'/'+str(p.relative_to(folder))]=p.read_bytes()
    return out
def make_zip(name,parts):
    parts=dict(sorted(parts.items()))
    manifest={'schema':'bass.ce1aj.sha256_zip_manifest.v1',
              'original_source_sha256':'022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035',
              'parent_head':'06a89b70200c09e44711235ef6d01a0b797b2a03',
              'files':{n:{'sha256':sha(b),'bytes':len(b)} for n,b in parts.items()}}
    dest=DIST/name
    with zipfile.ZipFile(dest,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        z.writestr('MANIFEST.json',json.dumps(manifest,sort_keys=True).encode())
        for n,b in parts.items():z.writestr(n,b)
    with zipfile.ZipFile(dest) as z:
        assert z.testzip() is None
        check=json.loads(z.read('MANIFEST.json'))
        assert len(check['files'])==len(parts)
        for n,item in check['files'].items():
            b=z.read(n)
            assert sha(b)==item['sha256'] and len(b)==item['bytes']
    return {'name':name,'bytes':dest.stat().st_size,'sha256':sha(dest.read_bytes()),'payload_files':len(parts)}
def main():
    new=grab('ce1aj_20261031',ROOT)
    # Exclude untracked parent checkpoint archives from accidental source duplication.
    s0={k:v for k,v in new.items() if '/data/' not in k and '/figures/' not in k}
    workflow=REPO/'.github/workflows/ce1aj-finite-dark-transfer.yml'
    s0['workflow/ce1aj-finite-dark-transfer.yml']=workflow.read_bytes()
    s1={k:v for k,v in new.items() if '/data/' in k or '/figures/' in k}
    # Include proof/theory next to science figures.
    s1['ce1aj_20261031/THEORY_KO.md']=(ROOT/'THEORY_KO.md').read_bytes()
    full={**s0,**s1}
    # Contiguous source-inclusive restore: original immutable ancestor directories.
    for name in ['ce1ai_20261031','ce1ah_20261031','ce1af_20261030','ce1ag_20261031']:
        parent=ROOT.parent/name
        if not parent.exists():raise RuntimeError('Missing exact parent '+name)
        full.update(grab('immutable_ancestors/'+name,parent))
    records=[]
    records.append(make_zip('CE1AJ_S0_SOURCE_STAGES.zip',s0))
    records.append(make_zip('CE1AJ_S1_REAL_SCIENCE.zip',s1))
    records.append(make_zip('CE1AJ_S2_SOURCE_INCLUSIVE_FULL.zip',full))
    sub=DIST/'stage_archives';sub.mkdir(exist_ok=True)
    stages=sorted((ROOT/'checkpoints').glob('*.json'))
    assert len(stages)==20
    for f in stages:
        obj={f.name:f.read_bytes(),'THEORY_KO.md':(ROOT/'THEORY_KO.md').read_bytes()}
        # Each has its own complete checksum-backed ZIP.
        saved=make_zip('stage_archives/'+f.stem+'.zip',obj)
        records.append(saved)
    (DIST/'ZIP_RECEIPTS.json').write_text(json.dumps({'unit':'CE1AJ','results':records,'upper_DAG':'9/15','new_upper_nodes':0},indent=2)+'\n')
    print('CE1AJ_SCIENTIFIC_BACKUP_PACKAGES',len(records),[x['name'] for x in records[:3]])
if __name__=='__main__':main()

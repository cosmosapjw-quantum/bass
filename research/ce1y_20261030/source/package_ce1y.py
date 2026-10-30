"""Integrity checked, nested immutable phase checkpoints of CE1-Y scientific data."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
def package(dest, paths):
    files={str(p.relative_to(ROOT)):p.read_bytes() for p in sorted(set(paths)) if p.exists()}
    m={'schema':'bass.ce1y.zip_manifest.v1','files':{k:{'sha256':sha(v),'bytes':len(v)} for k,v in files.items()}}
    with ZipFile(dest,'w',compression=ZIP_DEFLATED,compresslevel=7) as z:
        for k,v in files.items():z.writestr(k,v)
        z.writestr('MANIFEST_SHA256.json',json.dumps(m,indent=2,sort_keys=True)+'\n')
    with ZipFile(dest) as z:
        assert z.testzip() is None
        chk=json.loads(z.read('MANIFEST_SHA256.json'))
        assert all(sha(z.read(k))==v['sha256'] and len(z.read(k))==v['bytes'] for k,v in chk['files'].items())
    print('PACKAGE_OK',dest.name,dest.stat().st_size,'bytes',len(files),'payloads',sha(dest.read_bytes()))
    return m

def main():
    cp=ROOT/'checkpoints';cp.mkdir(exist_ok=True)
    stagezip=ROOT/'stage_zip';stagezip.mkdir(exist_ok=True)
    for f in sorted((ROOT/'stages').glob('*.json')):
        package(stagezip/f'CE1Y_STAGE_{f.stem}_20261030.zip',[f])
    p0=[ROOT/'THEORY_KO.md',ROOT/'REPRODUCE.md',ROOT/'input/l4_source_and_transfer.json',ROOT/'input/real_time_mpfr.json']
    package(cp/'BASS_CE1Y_S0_THEORY_20261030.zip',p0)
    p1=[ROOT/'THEORY_KO.md',ROOT/'REPORT_KO.md',ROOT/'REPRODUCE.md',ROOT/'HANDOFF_NEXT_KO.md']
    for sub in ['source','data','input','tests','stages','figures']:
        p1.extend([p for p in (ROOT/sub).rglob('*') if p.is_file() and '__pycache__' not in p.parts])
    package(cp/'BASS_CE1Y_S1_REAL_K4_DATA_20261030.zip',p1)
    p2=p1+[p for p in cp.glob('*.zip')]+[p for p in stagezip.glob('*.zip')]
    package(Path('/mnt/data/BASS_CE1Y_10086_K4_PHYSICAL_ATLAS_20261030_FULL.zip'),p2)
if __name__=='__main__':main()

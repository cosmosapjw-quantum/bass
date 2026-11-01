"""Build self-contained scoped phase archives with internal SHA and CRC checks."""
from __future__ import annotations
import hashlib,json,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BACKUP=ROOT/'backups'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def build(phase):
    allowed=(ROOT/'reports/S0_R1_R4_THEORY.md',ROOT/'reports/S0_MANIFEST.json')
    selected=list(allowed)
    if phase>=1:
        selected += list((ROOT/'source').glob('*.py'))
        selected += [ROOT/'reports/S1_R5_R7_SCIENCE.md',ROOT/'reports/HOSTILE_REFEREE_KO.md',ROOT/'reports/R1_R10_STAGE_LEDGER.json',ROOT/'reports/SCIENCE_EXECUTION.log']
        selected += list((ROOT/'data').glob('*'))+list((ROOT/'plots').glob('*'))
    if phase>=2:
        selected += list((ROOT/'reports').glob('*'))
    selected=sorted(set(x for x in selected if x.exists() and x.is_file()))
    manifest={'schema':'bass.vi0.null_liouville.source_integrity.v1','phase':phase,'original_PR311_HEAD':'8d15551c2e0127ede4344f0969f8b7e251a09e3e',
     'files':{x.relative_to(ROOT).as_posix():sha(x) for x in selected}}
    mf=BACKUP/f'S{phase}_SHA_MANIFEST.json';mf.write_text(json.dumps(manifest,sort_keys=True,indent=2)+'\n')
    selected.append(mf)
    out=BACKUP/f'BASS_VI0_NULL_LIOUVILLE_S{phase}_20261101.zip'
    with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as f:
        for p in selected:f.write(p,p.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(out) as f:
        if f.testzip() is not None:raise RuntimeError('ZIP_CRC_FAILURE')
        for p,expected in manifest['files'].items():
            if hashlib.sha256(f.read(p)).hexdigest()!=expected:raise RuntimeError('MEMBER_SHA_FAILURE '+p)
    print('PHASE_BUILT',phase,'bytes',out.stat().st_size,'sha256',sha(out),'member_sha',len(manifest['files']),'zip_count',len(selected))
    return out
if __name__=='__main__':build(int(sys.argv[1]))

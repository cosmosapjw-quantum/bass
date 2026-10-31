"""KM2O full 10-epoch S0/S1/S2, exact original KM2N source and SHA256/ZIP-CRC."""
from __future__ import annotations
import argparse,hashlib,json,os,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
UNIT='research/dual_lane_km2o_dossier_20261031'
SRC=(
 UNIT+'/S0_THEORY_KO.md',UNIT+'/DAG_RECONCILED.json',UNIT+'/DAG_CROSSWALK_AND_VIGILODE_KO.md',
 UNIT+'/replay_second_gain_endpoint.py', UNIT+'/KM2O_10_PHYSICAL_SECOND_GAIN_EPOCHS.csv',
 UNIT+'/replay_second_gain_full.py',UNIT+'/hostile_full_gain_audit.py',
 UNIT+'/make_full_gain_plots.py',UNIT+'/generate_final_report.py',UNIT+'/ARCHIVE_BUILD.py',
 UNIT+'/tests/test_full_second_gain.py','.github/workflows/km2o-second-source-certificate.yml')
S1=(UNIT+'/KM2O_FULL_SCIENCE.json',UNIT+'/KM2O_SECOND_GAIN_GL12_U40.npz',UNIT+'/KM2O_SECOND_GAIN_GL16_U40.npz')
S2=(UNIT+'/KM2O_HOSTILE_FULL_AUDIT.json',UNIT+'/S2_FINAL_REPORT_KO.md',UNIT+'/HANDOFF_NEXT_KO.txt')
def sha(x):return hashlib.sha256(x).hexdigest()
def original_source_entries():
    p=ROOT/'MANIFEST.json'
    if p.is_file():
        info=json.loads(p.read_text());src=info['members']
    else:
        p=ROOT/'SOURCE_MANIFEST.json'
        info=json.loads(p.read_text())
        src={n:v for n,v in info['members'].items()
             if not n.startswith(UNIT+'/') and not n.startswith('KM2O_')
             and n!='.github/workflows/km2o-second-source-certificate.yml'}
    if len(src)!=50:raise ArithmeticError(f'original owner source must contain exactly 50 immutable files, found {len(src)}')
    for rel,descriptor in src.items():
        x=ROOT/rel
        if not x.is_file() or sha(x.read_bytes())!=descriptor['sha256']:
            raise ArithmeticError('ORIGINAL_SCIENCE_SOURCE_SHA_MISMATCH '+rel)
    return src

def build(stage,outfile):
    if stage not in {'S0','S1','S2'}:raise ValueError('wrong backup stage')
    parent=original_source_entries()
    files=set(parent)|set(SRC)
    if stage in ('S1','S2'):
        files.update(S1)
        files.update(str(p.relative_to(ROOT)) for p in (ROOT/UNIT/'figures').glob('*') if p.is_file())
    if stage=='S2':files.update(S2)
    manifest={}
    for path in sorted(files):
        p=ROOT/path
        if not p.is_file():raise FileNotFoundError('SOURCE_OWNED_SCIENCE_OUTPUT_MISSING '+path)
        b=p.read_bytes();manifest[path]={'sha256':sha(b),'bytes':len(b)}
    outfile=Path(outfile);outfile.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(outfile,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for rel in sorted(files):z.write(ROOT/rel,arcname=rel)
        z.writestr('SOURCE_MANIFEST.json',json.dumps({'schema':'bass.km2o.full_source_dossier.v2',
             'stage':stage,'source_git_SHA':os.getenv('GITHUB_SHA','LOCAL_UNATTESTED'),
             'immutable_original_BASS_KM2N':'4137f942d2a95999f4e6627b71042e98f7afc1b7',
             'original_parent_members':50,'upper_BASS_DAG':'9/15','KM2':'PARTIAL',
             'new_upper_completed':0,'production_ready':False,'members':manifest},sort_keys=True,indent=2)+'\n')
    with zipfile.ZipFile(outfile,'r') as z:
        if z.testzip() is not None:raise ArithmeticError('WRITTEN_ZIP_CRC_FAIL')
        meta=json.loads(z.read('SOURCE_MANIFEST.json'))
        for name,x in meta['members'].items():
            if sha(z.read(name))!=x['sha256']:raise ArithmeticError('WRITTEN_ZIP_SHA_FAIL '+name)
    print('KM2O_STAGE_SOURCE_BACKUP',stage,'FILES',len(manifest),'INNER_BYTES',outfile.stat().st_size,
          'SHA256',sha(outfile.read_bytes()),flush=True)
    return manifest

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--stage',required=True,choices=['S0','S1','S2']);ap.add_argument('--output',required=True,type=Path)
    a=ap.parse_args();build(a.stage,a.output)

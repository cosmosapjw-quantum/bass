"""Exact source restore from original KM2N success artifact 13035232055 (PR297).
No owner IVPs regenerated. Only well-defined source result files are extracted.
"""
from __future__ import annotations
import argparse,hashlib,io,json,zipfile
from pathlib import Path
from first_scatter_joint import ORIGINAL_KM2N_HEAD,ORIGINAL_SHA256

OUTER_SHA='45733f4ca2c0250cc94d934e0c58c7dbb0f6220350b2a303e25e55f77c787ffe'
INNER_SHA='8dd9258a3a50b6d0140c9305040c978f5a0790d907a8927769d3d27b5c63ab0d'
NESTED='tmp/km2n_ci/KM2N_S2_COMPLETE_SOURCE_SCIENCE.zip'
ROOT='research/dual_lane_km2n_20261031/results/'

def h(data):return hashlib.sha256(data).hexdigest()

def restore(outer_path:Path,destination:Path):
    raw=outer_path.read_bytes()
    if h(raw)!=OUTER_SHA:raise ArithmeticError('untrusted KM2N outer S2 SHA')
    with zipfile.ZipFile(io.BytesIO(raw)) as outer:
        if outer.testzip() is not None: raise ArithmeticError('KM2N outer CRC failed')
        inner=outer.read(NESTED)
        if h(inner)!=INNER_SHA:raise ArithmeticError('untrusted KM2N inner S2 SHA')
        with zipfile.ZipFile(io.BytesIO(inner)) as source:
            if source.testzip() is not None:raise ArithmeticError('KM2N inner CRC failed')
            mf=json.loads(source.read('MANIFEST.json'))
            if mf.get('git_source_HEAD')!=ORIGINAL_KM2N_HEAD:
                raise ArithmeticError('original owner HEAD mismatch')
            members=mf['members']
            if len(members)!=50:raise ArithmeticError('unexpected original 50 source members')
            for name,entry in members.items():
                b=source.read(name)
                if len(b)!=entry['bytes'] or h(b)!=entry['sha256']:
                    raise ArithmeticError('original 50-member source archive failed '+name)
            destination.mkdir(parents=True,exist_ok=True)
            for filename,sha in ORIGINAL_SHA256.items():
                b=source.read(ROOT+filename)
                if h(b)!=sha:raise ArithmeticError('original locked physics input failed '+filename)
                (destination/filename).write_bytes(b)
            mf_path=destination.parent/'ORIGINAL_KM2N_MANIFEST.json'
            mf_path.write_bytes(source.read('MANIFEST.json'))
    return {'parent_head':ORIGINAL_KM2N_HEAD,'original_members':len(members),
            'exact_selected_input_files':len(ORIGINAL_SHA256),'source_archive_inner_SHA256':INNER_SHA,
            'source_archive_outer_SHA256':OUTER_SHA}

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--artifact',required=True,type=Path)
    p.add_argument('--dest',default=Path(__file__).resolve().parent/'source_inputs',type=Path)
    a=p.parse_args()
    print('KM2_ORIGINAL_RESTORED',json.dumps(restore(a.artifact,a.dest),sort_keys=True))

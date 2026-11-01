#!/usr/bin/env python3
"""Restore only original KM2N/KM2L source NPZ from the pinned CI S2 archive.

No file is trusted based on archive name; cryptographic input source guards apply.
"""
import argparse,hashlib,io,json,zipfile
from pathlib import Path
PARENT='4137f942d2a95999f4e6627b71042e98f7afc1b7'
OUTER_SHA='45733f4ca2c0250cc94d934e0c58c7dbb0f6220350b2a303e25e55f77c787ffe'
INNER_SHA='8dd9258a3a50b6d0140c9305040c978f5a0790d907a8927769d3d27b5c63ab0d'
NESTED='tmp/km2n_ci/KM2N_S2_COMPLETE_SOURCE_SCIENCE.zip'
SOURCE_FILES={
 'KM2N_FIRST_SOURCE_LEDGER_GL12.npz':'ee6d0972a165a515494cfd310e8367cf85886b7ba18da8bb0bb3b34c8f7da8b0',
 'KM2N_FIRST_SOURCE_LEDGER_GL16.npz':'3ebce3e3f1f77d2d75452d87dab664e716eda469664cc14cbb489275b02716d5',
 'KM2L_THOMSON_OPTICAL_GL12_GLT8.npz':'785239a5ed6712144741e5d11e84e5288217026e884f873a1d54623b8a55b4fd',
 'KM2L_THOMSON_OPTICAL_GL16_GLT8.npz':'9d8dd5b8c638a5ff48c9c743af2cfeb483057f745132346ab259605d12312911'}

def digest(b):return hashlib.sha256(b).hexdigest()

def restore(artifact:Path,dest:Path):
    raw=artifact.read_bytes()
    if digest(raw)!=OUTER_SHA:raise ArithmeticError('outer owner artifact SHA incorrect')
    with zipfile.ZipFile(io.BytesIO(raw)) as outer:
        if outer.testzip():raise ArithmeticError('outer artifact CRC failure')
        innerbytes=outer.read(NESTED)
        if digest(innerbytes)!=INNER_SHA:raise ArithmeticError('inner source archive SHA incorrect')
        with zipfile.ZipFile(io.BytesIO(innerbytes)) as z:
            if z.testzip():raise ArithmeticError('inner source CRC failure')
            dest.mkdir(parents=True,exist_ok=True)
            for file,sha in SOURCE_FILES.items():
                b=z.read('research/dual_lane_km2n_20261031/results/'+file)
                if digest(b)!=sha:raise ArithmeticError('original source NPZ mismatched: '+file)
                (dest/'source_inputs').mkdir(exist_ok=True)
                (dest/'source_inputs'/file).write_bytes(b)
    manifest={'source':'BASS KM2N PR297 immutable S2 20261031','parent_pr':297,'parent_head':PARENT,
              'source_archive_outer_sha256':OUTER_SHA,'source_archive_inner_sha256':INNER_SHA,
              'files':SOURCE_FILES,'new_owner_Einstein_IVPs':0}
    (dest/'SOURCE_MANIFEST.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
    return manifest

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--artifact',required=True,type=Path)
    ap.add_argument('--dest',type=Path,default=Path(__file__).resolve().parent)
    x=ap.parse_args();restore(x.artifact,x.dest)
    print('IMMUTABLE_KM2N_RESTORE_PASS_4_OF_4')
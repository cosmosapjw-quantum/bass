"""Extract immutable source-owned 2026-10-31 BASS KM2N physics, fail closed."""
from pathlib import Path
import io,zipfile,hashlib,json,argparse
OUTER_SHA='45733f4ca2c0250cc94d934e0c58c7dbb0f6220350b2a303e25e55f77c787ffe'
INNER_SHA='8dd9258a3a50b6d0140c9305040c978f5a0790d907a8927769d3d27b5c63ab0d'
HEAD='4137f942d2a95999f4e6627b71042e98f7afc1b7'
NESTED='tmp/km2n_ci/KM2N_S2_COMPLETE_SOURCE_SCIENCE.zip'
SOURCE_ROOT='research/dual_lane_km2n_20261031/results/'
ORIGINAL_SHA={
 'KM2K_PACKETS_GL12_GLT8.npz':'dc677740685d760120d56badb5e9073c7b14a6eff2803641fc24259ac9df7e03',
 'KM2K_PACKETS_GL16_GLT8.npz':'caaea73af02ba54313acc14d78e41727409879a0d4286528981704ee857036d6',
 'KM2L_THOMSON_OPTICAL_GL12_GLT8.npz':'785239a5ed6712144741e5d11e84e5288217026e884f873a1d54623b8a55b4fd',
 'KM2L_THOMSON_OPTICAL_GL16_GLT8.npz':'9d8dd5b8c638a5ff48c9c743af2cfeb483057f745132346ab259605d12312911',
 'KM2N_FIRST_SOURCE_LEDGER_GL12.npz':'ee6d0972a165a515494cfd310e8367cf85886b7ba18da8bb0bb3b34c8f7da8b0',
 'KM2N_FIRST_SOURCE_LEDGER_GL16.npz':'3ebce3e3f1f77d2d75452d87dab664e716eda469664cc14cbb489275b02716d5',
 'KM2N_ONCE_POL_SCREEN_GL12_U40.npz':'de93bff3abe775092d87f221ce059834d08fec6307b4ac71484213fbf2cd2df2',
 'KM2N_ONCE_POL_SCREEN_GL16_U40.npz':'89fce4ea3c533212648a88e63e2993ab23df0c31fb55f6a6fe9bc276edc08726',
 'KM2N_ONCE_SCATTER_REAL.json':'dcb98647a7c08c5b503a98900a550198ba1c76f10f94b63a570542c41b504ec4',
}
def hashbytes(x):return hashlib.sha256(x).hexdigest()
def restore(archive, dest):
    archive=Path(archive);dest=Path(dest);raw=archive.read_bytes()
    assert hashbytes(raw)==OUTER_SHA, 'Original S2 outer archive sha failed'
    with zipfile.ZipFile(io.BytesIO(raw)) as outer:
        assert outer.testzip() is None
        inn=outer.read(NESTED)
    assert hashbytes(inn)==INNER_SHA, 'Original S2 nested archive sha failed'
    with zipfile.ZipFile(io.BytesIO(inn)) as data:
        assert data.testzip() is None
        manifest=json.loads(data.read('MANIFEST.json'))
        assert manifest['git_source_HEAD']==HEAD and len(manifest['members'])==50
        for name,info in manifest['members'].items():
            b=data.read(name)
            assert hashbytes(b)==info['sha256'] and len(b)==info['bytes'],name
        dest.mkdir(parents=True,exist_ok=True)
        for name,digest in ORIGINAL_SHA.items():
            b=data.read(SOURCE_ROOT+name)
            assert hashbytes(b)==digest,name
            (dest/name).write_bytes(b)
        (dest.parent/'ORIGINAL_SOURCE_MANIFEST.json').write_bytes(data.read('MANIFEST.json'))
    return dict(source_head=HEAD,original_source_members=50,selected_input_files=len(ORIGINAL_SHA),outer_sha256=OUTER_SHA,inner_sha256=INNER_SHA)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--archive',required=True);p.add_argument('--out',required=True);args=p.parse_args()
 print(json.dumps(restore(args.archive,args.out),sort_keys=True))

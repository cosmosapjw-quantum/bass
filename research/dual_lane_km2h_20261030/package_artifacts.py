"""Source-inclusive KM2H stage S0/S1/S2 with explicit file SHA256 and ZIP CRC.

BASS original fully polarized photon sources and the user-generated native
HYREC-2/CLASS FLRW record remain unmodified, traceable and restorable.
The optional original-native archive is included only when explicitly supplied.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from zipfile import ZIP_DEFLATED,ZipFile

ROOT=Path(__file__).resolve().parents[2]
HERE=ROOT/'research/dual_lane_km2h_20261030'
ORIGINAL=[
 'research/dual_lane_km2c_20261028/code/curved_tilt.py',
 'research/dual_lane_km2c_20261028/vendor/km2b_fixtures.py',
 'research/dual_lane_km2c_20261028/vendor/polarization.py',
 'research/dual_lane_km2c_20261028/vendor/polarized_dictionary.py',
 'research/dual_lane_km2c_20261028/vendor/rest_volterra.py',
 'research/dual_lane_km2c_20261028/vendor/source_memory.py',
 'research/dual_lane_km2c_20261028/vendor/tilted_collision.py',
 'research/dual_lane_km2c_20261028/vendor/tilted_history.py',
 'research/dual_lane_km2d_20261030/accelerating_tilt.py',
 'research/dual_lane_km2e_20261030/coupled_electron_photon.py',
 'research/dual_lane_km2f_20261030/einstein_bianchi.py',
 'research/dual_lane_km2g_20261030/neutral_baryons.py',
]
S0=[
 'research/dual_lane_km2h_20261030/S0_EXTERNAL_OPACITY_THEORY_KO.md',
 'research/dual_lane_km2h_20261030/source_data/flrw_recombination_regression_1to1600.csv',
]
S1=[
 'research/dual_lane_km2h_20261030/external_opacity_bianchi.py',
 'research/dual_lane_km2h_20261030/make_science_plots.py',
 'research/dual_lane_km2h_20261030/tests/test_external_opacity.py',
 'research/dual_lane_km2h_20261030/package_artifacts.py',
]
S2=[
 'research/dual_lane_km2h_20261030/S2_FINAL_REPORT_KO.md',
 'research/dual_lane_km2h_20261030/HANDOFF_NEXT_KO.txt',
 'research/dual_lane_km2h_20261030/DAG_DELTA.json',
 'research/dual_lane_km2h_20261030/DELIVERY_RECEIPTS.json',
 'research/dual_lane_km2h_20261030/HOSTILE_REVIEW_KO.md',
 'research/dual_lane_km2h_20261030/PR285_NUMERICAL_SEMANTIC_AUDIT.json',
 'research/dual_lane_km2h_20261030/hostile_saved_physics_audit.py',
 '.github/workflows/km2h-hyrec-external-bianchi.yml',
]

def sha(x):return hashlib.sha256(x).hexdigest()

def build(stage,output,physics=None,figures=None,original_native=None,hostile=None):
    from research.dual_lane_km2h_20261030.external_opacity_bianchi import exact_source_guards
    source_blobs=exact_source_guards()
    if stage not in ('S0','S1','S2'):raise ValueError('Unknown scientific checkpoint')
    keep=S0+ORIGINAL
    if stage in ('S1','S2'):
        keep+=S1
        if physics is None or not Path(physics).is_file():raise FileNotFoundError('Actual 6-case Einstein/Boltzmann science JSON required')
        a=json.loads(Path(physics).read_text())
        if a['upper_dag']!='9/15' or a['km2']!='PARTIAL' or len(a['cases'])!=6:
            raise ValueError('Actual physics not complete, source family or DAG corrupted')
        if figures is None or not Path(figures).is_dir():raise FileNotFoundError('Real source-derived plots required')
    if stage=='S2':
        keep+=[k for k in S2 if (ROOT/k).is_file()]
    files={n:(ROOT/n).read_bytes() for n in keep}
    if stage in ('S1','S2'):
        files['results/real_conditioned_Einstein_P8_opacity.json']=Path(physics).read_bytes()
        figs=Path(figures)
        for f in sorted(figs.iterdir()):
            if f.suffix in ('.csv','.json','.png'):
                files['results/physical_plots/'+f.name]=f.read_bytes()
    if stage=='S2' and hostile is not None:
        audit=Path(hostile)
        if not audit.is_file():raise FileNotFoundError('Independent hostile saved-data audit missing')
        audited=json.loads(audit.read_text())
        if audited['n_epochs']!=30 or audited['n_GL24_rows']!=144:
            raise ValueError('Hostile source arithmetic audit not complete')
        files['results/hostile_saved_data_audit.json']=audit.read_bytes()
    if stage=='S2' and original_native is not None:
        native=Path(original_native)
        if not native.is_file():raise FileNotFoundError('User original native source zip missing')
        expected='df2840d1c85a2d3ff174113db60928d4b94141347708e810aafd00d862a7fd10'
        if sha(native.read_bytes())!=expected:
            raise ValueError('USER_ORIGINAL_HYREC_CLASS_SOURCE_ARCHIVE_IDENTITY_MISMATCH')
        files['upstream_user_originals/HYREC2_CLASS_native_source_complete_P282.zip']=native.read_bytes()
    manifest={
      'schema':'bass.km2h.source_complete_external_FLRW_Einstein_P8.v1',
      'stage':stage,'flrw_only_parent_pr':282,
      'immutable_parent_head':'0815ff69fb8be7123deb04a09fc54f15fbf6edd1',
      'original_BASS_git_blobs':source_blobs,
      'source_FLRW_SHA256':'7f2c47c70dfab95e9ababed481db2c8d78429c0402ba1a85faeccb73df14d4da',
      'external_original_native_archive_included':bool(stage=='S2' and original_native is not None),
      'upper_DAG':'9/15','KM2':'PARTIAL','new_upper_complete':0,
      'experimental_physics':'conditional FLRW xe volume-redshift proxy in genuine Einstein Bianchi I polarized original P8, NOT solved anisotropic recombination',
      'production_ready':False,'merge_ready':False,'auto_next':False,
      'member_sha256':{}
    }
    path=Path(output);path.parent.mkdir(parents=True,exist_ok=True)
    with ZipFile(path,'w',compression=ZIP_DEFLATED,compresslevel=5) as z:
        for name,raw in sorted(files.items()):
            z.writestr(name,raw)
            manifest['member_sha256'][name]=sha(raw)
        z.writestr('MANIFEST.json',json.dumps(manifest,sort_keys=True,indent=2,ensure_ascii=False)+'\n')
    with ZipFile(path) as z:
        if z.testzip() is not None:raise RuntimeError('KM2H_ZIP_CRC_FAILURE')
        m=json.loads(z.read('MANIFEST.json'))
        for name,digest in m['member_sha256'].items():
            if sha(z.read(name))!=digest:raise RuntimeError('KM2H_ZIP_MEMBER_SHA256_FAILURE '+name)
    print('KM2H_STAGE_ARCHIVE',json.dumps({
      'stage':stage,'bytes':path.stat().st_size,'sha256':sha(path.read_bytes()),
      'payload_members':len(files),'zip_CRC':'PASS','member_SHA256':'PASS',
      'upper_DAG':'9/15','original_native_included':manifest['external_original_native_archive_included'],
    },sort_keys=True),flush=True)
    return manifest

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--stage',required=True,choices=('S0','S1','S2'))
    ap.add_argument('--output',required=True,type=Path)
    ap.add_argument('--physics',type=Path);ap.add_argument('--figures',type=Path)
    ap.add_argument('--original-native',type=Path);ap.add_argument('--hostile',type=Path)
    x=ap.parse_args();build(x.stage,x.output,x.physics,x.figures,x.original_native,x.hostile)

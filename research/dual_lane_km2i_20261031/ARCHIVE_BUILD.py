"""Reproducible source-inclusive S0,S1,S2 checkpoints with verified manifests."""
import argparse,hashlib,json,zipfile,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[2]
HERE=pathlib.Path(__file__).resolve().parent
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
'research/dual_lane_km2h_20261030/external_opacity_bianchi.py',
'research/dual_lane_km2h_20261030/source_data/flrw_recombination_regression_1to1600.csv',
]
S0=['research/dual_lane_km2i_20261031/S0_THEORY_KO.md',
    'research/dual_lane_km2i_20261031/source_data/wrap_recfast.c',
    'research/dual_lane_km2i_20261031/source_data/wrap_recfast.h']
S1=['research/dual_lane_km2i_20261031/lya_peebles.py','research/dual_lane_km2i_20261031/make_plots.py',
    'research/dual_lane_km2i_20261031/tests/test_lya_peebles.py',
    'research/dual_lane_km2i_20261031/results/KM2I_REAL_LYA_PEEBLES_2GRID.json']
S2=['research/dual_lane_km2i_20261031/S2_FINAL_REPORT_KO.md','research/dual_lane_km2i_20261031/HANDOFF_NEXT_KO.txt',
    'research/dual_lane_km2i_20261031/DAG_DELTA.json','research/dual_lane_km2i_20261031/DELIVERY_RECEIPTS.json',
    'research/dual_lane_km2i_20261031/ARCHIVE_BUILD.py','research/dual_lane_km2i_20261031/hostile_saved_rate_audit.py',
    'research/dual_lane_km2i_20261031/results/HOSTILE_INDEPENDENT_CHEM_RATE_AUDIT.json','.github/workflows/km2i-lya-peebles-bianchi.yml']
sha=lambda b:hashlib.sha256(b).hexdigest()
def build(stage,out,native=None):
    if stage not in ('S0','S1','S2'):raise ValueError(stage)
    from research.dual_lane_km2i_20261031.lya_peebles import source_guards
    guards=source_guards()
    files=ORIGINAL+S0
    if stage in ('S1','S2'):files+=S1
    if stage=='S2':files+=S2
    data={p:(ROOT/p).read_bytes() for p in files}
    if stage in ('S1','S2'):
       f=HERE/'figures'
       data.update({str(v.relative_to(ROOT)):v.read_bytes() for v in f.iterdir() if v.is_file() and v.suffix in ('.csv','.json','.png')})
       assert len(json.loads((HERE/'results/KM2I_REAL_LYA_PEEBLES_2GRID.json').read_text())['cases'])==2
    if stage=='S2' and native:
       n=pathlib.Path(native)
       expected='572b35ab08e5959f53d33389c7154c3195b1a6f80221a3face472a8b727574ff'
       raw=n.read_bytes()
       if sha(raw)!=expected:raise ValueError('IMMUTABLE_PARENT_PR285_NATIVE_SOURCE_ARCHIVE_SHA_FAIL')
       data['upstream_original_user_native/BASS_KM2H_PR285_SOURCE_COMPLETE_S2.zip']=raw
    out=pathlib.Path(out);out.parent.mkdir(exist_ok=True,parents=True)
    manifest={'schema':'bass.km2i.directional_lya_recombination_stage.v1','stage':stage,
              'parent_head':'75f9dca9907cbc62af837547c2ba8591ad72bdee',
              'upper_dag':'9/15','km2':'PARTIAL','new_upper_completed':0,
              'source_lock':guards,'original_native_nested':bool(stage=='S2' and native),
              'member_sha256':{k:sha(v) for k,v in data.items()}}
    with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
       for name,bytes_ in sorted(data.items()):z.writestr(name,bytes_)
       z.writestr('MANIFEST.json',json.dumps(manifest,sort_keys=True,indent=2))
    with zipfile.ZipFile(out) as z:
        if z.testzip() is not None:raise AssertionError('CRC FAIL')
        for p,d in manifest['member_sha256'].items():
            if sha(z.read(p))!=d:raise AssertionError('SHA FAIL '+p)
    outinfo={'stage':stage,'members':len(data),'bytes':out.stat().st_size,'sha256':sha(out.read_bytes()),'zip_CRC':'PASS','member_sha256':'PASS','upper_dag':'9/15'}
    print('KM2I_STAGE_ARCHIVE',json.dumps(outinfo,sort_keys=True))
    return outinfo
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--stage',choices=['S0','S1','S2'],required=True)
    p.add_argument('--output',required=True);p.add_argument('--native');a=p.parse_args();build(a.stage,a.output,a.native)

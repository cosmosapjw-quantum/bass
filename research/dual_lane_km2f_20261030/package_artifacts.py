"""Source-complete KM2F physical Einstein S0/S1/S2 ZIP archives with SHA+CRC."""
from __future__ import annotations
import argparse,csv,hashlib,io,json
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED

ROOT=Path(__file__).resolve().parents[2]
HERE=ROOT/'research/dual_lane_km2f_20261030'
KM2C=ROOT/'research/dual_lane_km2c_20261028'
KM2D=ROOT/'research/dual_lane_km2d_20261030'
KM2E=ROOT/'research/dual_lane_km2e_20261030'
ORIG=[
 'code/curved_tilt.py',
 'vendor/polarization.py','vendor/polarized_dictionary.py',
 'vendor/source_memory.py','vendor/tilted_collision.py',
 'vendor/tilted_history.py','vendor/km2b_fixtures.py',
 'vendor/rest_volterra.py',
]


def to_csv(rows):
    f=io.StringIO()
    if not rows:return b''
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    return f.getvalue().encode('utf-8')


def science_csv(data):
    physical=[];sources=[]
    for n,c in sorted(data['cases'].items(),key=lambda kv:int(kv[0])):
        for r in c['physics_epochs']:
            physical.append({
             'ntheta':n,'u':r['u'],'H':r['H'],'sigma2':r['sigma2'],
             'rho_gamma':r['rho_photon'],'rho_electron':r['rho_electron'],'rho_total':r['rho_total'],
             'beta_x':r['beta_electron'][0],'beta_y':r['beta_electron'][1],'beta_z':r['beta_electron'][2],
             'q_total_x':r['q_total'][0],'q_total_y':r['q_total'][1],'q_total_z':r['q_total'][2],
             'Hamiltonian_residual':r['hamiltonian_constraint'],
             'normalized_H_constraint':r['hamiltonian_normalized'],
             'normalized_Q_constraint':r['momentum_constraint_normalized'],
             'Einstein_shear_commutator':r['noncommuting_shear_commutator_norm'],
             'electron_zeta':r['electron_zeta'],'electron_nu':r['nu_rest_tstar'],
            })
        for r in c['integrated_balances']['force_gap_time_rows']:
            sources.append({
             'ntheta':n,'u':r['u'],
             'P8_raw_minus_covariant_force_0':r['gap'][0],
             'force_gap_x':r['gap'][1],'force_gap_y':r['gap'][2],'force_gap_z':r['gap'][3],
            })
    return to_csv(physical),to_csv(sources)


def build(stage,output,result=None):
    from research.dual_lane_km2f_20261030.einstein_bianchi import full_source_guard
    origins=full_source_guard()
    if stage not in ('S0','S1','S2'):raise ValueError('Unknown scientific stage')
    files={
      'research/dual_lane_km2f_20261030/S0_THEORY_KO.md':(HERE/'S0_THEORY_KO.md').read_bytes()
    }
    for name in ORIG:
        files['original_KM2C/'+name]=(KM2C/name).read_bytes()
    files['original_KM2D/accelerating_tilt.py']=(KM2D/'accelerating_tilt.py').read_bytes()
    files['original_KM2E/coupled_electron_photon.py']=(KM2E/'coupled_electron_photon.py').read_bytes()
    if stage in ('S1','S2'):
        if result is None or not result.is_file():raise FileNotFoundError('Actual Einstein photon science JSON required')
        data=json.loads(result.read_text())
        if data['upper_dag']!='9/15' or data['km2']!='PARTIAL':raise ValueError('Upper DAG mismatch')
        ps,force=science_csv(data)
        files.update({
           'research/dual_lane_km2f_20261030/einstein_bianchi.py':(HERE/'einstein_bianchi.py').read_bytes(),
           'research/dual_lane_km2f_20261030/tests/test_einstein_bianchi.py':(HERE/'tests/test_einstein_bianchi.py').read_bytes(),
           'research/dual_lane_km2f_20261030/package_artifacts.py':(HERE/'package_artifacts.py').read_bytes(),
           '.github/workflows/km2f-einstein-constraints.yml':(ROOT/'.github/workflows/km2f-einstein-constraints.yml').read_bytes(),
           'results/real_einstein_photon_electron.json':result.read_bytes(),
           'results/five_epoch_Einstein_photon_electron.csv':ps,
           'results/GL24_original_P8_force_gap.csv':force,
        })
    if stage=='S2':
        for name in ('S2_FINAL_REPORT_KO.md','HANDOFF_NEXT_KO.txt','DAG_DELTA.json','DELIVERY_RECEIPTS.json'):
            p=HERE/name
            if p.is_file():files['research/dual_lane_km2f_20261030/'+name]=p.read_bytes()
    info={
       'schema':'bass.km2f.source_complete_Einstein_Bianchi_I_science_archive.v1',
       'stage':stage,'immutable_parent_pr276_head':'58277dab1af10850ff0a86c74673743b2c0a8a5a',
       'original_BASS_code_git_blobs':origins,'original_photon_source_changed':False,
       'electron_initial_velocity_adjusted_to_Enstein_momentum_constraint':True,
       'Einstein_kappa':.003,'electron_initial_energy_ratio':3.,
       'upper_DAG':'9/15','KM2':'PARTIAL',
       'production_ready':False,'merge_ready':False,'auto_next':False,
       'file_sha256':{},
    }
    output.parent.mkdir(parents=True,exist_ok=True)
    with ZipFile(output,'w',compression=ZIP_DEFLATED,compresslevel=6) as z:
        for name,raw in sorted(files.items()):
            z.writestr(name,raw)
            info['file_sha256'][name]=hashlib.sha256(raw).hexdigest()
        z.writestr('MANIFEST.json',json.dumps(info,sort_keys=True,indent=2)+'\n')
    with ZipFile(output) as z:
        if z.testzip() is not None:raise RuntimeError('S ZIP CRC FAIL')
        meta=json.loads(z.read('MANIFEST.json'))
        for name,digest in meta['file_sha256'].items():
            if hashlib.sha256(z.read(name)).hexdigest()!=digest:
                raise RuntimeError('S ZIP member SHA mismatch '+name)
    print('KM2F_STAGE_ARCHIVE',json.dumps({
       'stage':stage,'zip_crc':'PASS','member_SHA256':'PASS','member_count':len(info['file_sha256']),
       'bytes':output.stat().st_size,'sha256':hashlib.sha256(output.read_bytes()).hexdigest(),
       'upper_DAG':'9/15'},sort_keys=True),flush=True)


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--stage',required=True,choices=('S0','S1','S2'))
    ap.add_argument('--output',type=Path,required=True);ap.add_argument('--results',type=Path)
    a=ap.parse_args();build(a.stage,a.output,a.results)

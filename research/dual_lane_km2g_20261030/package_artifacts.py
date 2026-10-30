"""S0/S1/S2 physical neutral e–p Einstein research archive with original source hashes."""
from __future__ import annotations
import argparse,csv,hashlib,io,json
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED

ROOT=Path(__file__).resolve().parents[2]
HERE=ROOT/'research/dual_lane_km2g_20261030'
KM2C=ROOT/'research/dual_lane_km2c_20261028'
KM2D=ROOT/'research/dual_lane_km2d_20261030'
KM2E=ROOT/'research/dual_lane_km2e_20261030'
KM2F=ROOT/'research/dual_lane_km2f_20261030'
ORIGINAL_FILES=[
 'code/curved_tilt.py','vendor/polarization.py','vendor/polarized_dictionary.py',
 'vendor/source_memory.py','vendor/tilted_collision.py','vendor/tilted_history.py',
 'vendor/km2b_fixtures.py','vendor/rest_volterra.py',
]


def rows_to_csv(rows):
    if not rows:return b''
    f=io.StringIO()
    writer=csv.DictWriter(f,fieldnames=list(rows[0].keys()))
    writer.writeheader();writer.writerows(rows)
    return f.getvalue().encode('utf-8')


def scientific_data_tables(science):
    phys=[];force=[]
    for key,case in sorted(science['cases'].items()):
        for x in case['physics_epochs']:
            phys.append({
                'case':key,'u':x['u'],'Tstar_years':case['Tstar_years'],
                'nu0_dimless':case['nu0_physical_derived'],'H':x['H'],
                'rho_gamma':x['rho_photon'],'rho_electron':x['rho_electron_species'],
                'rho_proton':x['rho_proton_species'],'rho_baryon':x['rho_baryon_total'],
                'rho_total':x['rho_total'],'zeta':x['electron_zeta'],
                'nu_u':x['nu_rest_tstar'],'n_e_per_m3':x['proper_n_electron_m3'],
                'n_p_per_m3':x['proper_n_proton_m3'],
                'beta_x':x['beta_electron'][0],
                'beta_y':x['beta_electron'][1],'beta_z':x['beta_electron'][2],
                'sigma2':x['sigma2'],
                'q_total_x':x['q_total'][0],'q_total_y':x['q_total'][1],
                'q_total_z':x['q_total'][2],
                'H_residual':x['hamiltonian_normalized'],
                'Q_residual':x['momentum_constraint_normalized'],
                'M_zz':x['source_electron_M'][2][2],
                'M_xy':x['source_electron_M'][0][1],
                'charge_density_C_m3':x['charge_density_C_m3']})
            force.append({
                'case':key,'u':x['u'],
                'photon_F0':x['photon_covariant_force'][0],
                'electron_net_F0':x['net_force_on_electron'][0],
                'proton_net_F0':x['net_force_on_proton'][0],
                'Coulomb_e_F0':x['Coulomb_force_on_electron'][0],
                'Coulomb_p_F0':x['Coulomb_force_on_proton'][0],
                'photon_Fx':x['photon_covariant_force'][1],
                'electron_net_Fx':x['net_force_on_electron'][1],
                'proton_net_Fx':x['net_force_on_proton'][1],
                'raw_minus_cov_F0':x['photon_force_discrete_gap'][0]})
    return rows_to_csv(phys),rows_to_csv(force)


def build(stage,output,result=None):
    from research.dual_lane_km2g_20261030.neutral_baryons import verify_unchanged_physics
    if stage not in ('S0','S1','S2'):
        raise ValueError('Scientific phase S0/S1/S2 only')
    origins=verify_unchanged_physics()
    files={'research/dual_lane_km2g_20261030/S0_THEORY_KO.md':(HERE/'S0_THEORY_KO.md').read_bytes()}
    for name in ORIGINAL_FILES:
        files['original_KM2C/'+name]=(KM2C/name).read_bytes()
    for old,label,name in [(KM2D,'KM2D','accelerating_tilt.py'),
                           (KM2E,'KM2E','coupled_electron_photon.py'),
                           (KM2F,'KM2F','einstein_bianchi.py')]:
        files['original_'+label+'/'+name]=(old/name).read_bytes()
    if stage in ('S1','S2'):
        if result is None or not result.is_file():
            raise FileNotFoundError('Actual physical six-case JSON required')
        data=json.loads(result.read_text())
        if data['upper_dag']!='9/15' or data['km2']!='PARTIAL':
            raise ValueError('Current upper BASS DAG provenance changed')
        spectra,forces=scientific_data_tables(data)
        files.update({
            'research/dual_lane_km2g_20261030/neutral_baryons.py':(HERE/'neutral_baryons.py').read_bytes(),
            'research/dual_lane_km2g_20261030/tests/test_neutral_baryons.py':(HERE/'tests/test_neutral_baryons.py').read_bytes(),
            'research/dual_lane_km2g_20261030/package_artifacts.py':(HERE/'package_artifacts.py').read_bytes(),
            'results/neutral_electron_proton_physical.json':result.read_bytes(),
            'results/neutral_electron_proton_5epoch.csv':spectra,
            'results/species_photon_Coulomb_force_5epoch.csv':forces,
        })
    if stage=='S2':
        for name in ('S2_FINAL_REPORT_KO.md','HANDOFF_NEXT_KO.txt','DAG_DELTA.json','DELIVERY_RECEIPTS.json','HOSTILE_REVIEW_KO.md'):
            p=HERE/name
            if p.is_file():files['research/dual_lane_km2g_20261030/'+name]=p.read_bytes()
        flow=ROOT/'.github/workflows/km2g-neutral-baryons.yml'
        if flow.is_file():files['.github/workflows/km2g-neutral-baryons.yml']=flow.read_bytes()
    manifest={
        'schema':'bass.km2g.physical_neutral_electron_proton_source_archive.v1',
        'stage':stage,
        'immutable_parent_PR278':'29ee9114856d493dac2f5e8328c145050169c13e',
        'original_git_sources':origins,
        'physics_scope':'exactly neutral homogeneous e+p ideal Coulomb-lock, source-preserved polarized P8 Einstein Bianchi I, opacity from SI constants',
        'upper_dag':'9/15','km2':'PARTIAL','new_upper_nodes':0,
        'production_ready':False,'merge_ready':False,'auto_next':False,
        'file_sha256':{},
    }
    output.parent.mkdir(parents=True,exist_ok=True)
    with ZipFile(output,'w',compression=ZIP_DEFLATED,compresslevel=6) as z:
        for name,b in sorted(files.items()):
            z.writestr(name,b)
            manifest['file_sha256'][name]=hashlib.sha256(b).hexdigest()
        z.writestr('MANIFEST.json',json.dumps(manifest,indent=2,sort_keys=True)+'\n')
    with ZipFile(output) as z:
        if z.testzip():raise RuntimeError('ZIP CRC failed')
        stored=json.loads(z.read('MANIFEST.json'))
        for name,expected in stored['file_sha256'].items():
            if hashlib.sha256(z.read(name)).hexdigest()!=expected:
                raise RuntimeError('ZIP file member SHA mismatch '+name)
    print('KM2G_STAGE_ZIP',json.dumps({
        'stage':stage,'bytes':output.stat().st_size,
        'sha256':hashlib.sha256(output.read_bytes()).hexdigest(),
        'payload_members':len(manifest['file_sha256']),
        'CRC':'PASS','SHA256_members':'PASS','upper_dag':'9/15'},sort_keys=True),flush=True)
    return manifest

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--stage',required=True,choices=('S0','S1','S2'))
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--results',type=Path)
    args=p.parse_args()
    build(args.stage,args.output,args.results)

"""CE1-Y original BASS-native massless Einstein-Vlasov two-time physical K4.

Reuses immutable PR270 live-CI Rust GL6/GL8 4/8/16 RK4/Hermite sky outputs,
plus the source/MPFR192 conditional mathematically certified kernel budget.
DOP853 comparison is empirical at saved epochs: NOT a validated IVP bound.
The Rust binary64 computed center itself is not an MPFR interval enclosure.
"""
from __future__ import annotations
import csv, hashlib, json, math, argparse
from pathlib import Path
import numpy as np

PARENT_PR270_CI=40991211526
SOURCE_SHA='022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035'
GL_DOP_CSV_SHA={
    6:'6eff8cd9f31d027bbee55720332302b6fbad71b3639b5809aab6b9ce6f53e489',
    8:'1398980ec71662494273e05eb4bd52a78f6e6c7f208702638da6c739698f7502'
}
PARENT_HEAD='614a59acf1bec121cc0f5ef1386488917bba3dc2'
EXPECTED_SOURCE_RUST='a29b12b5e7b0d529bddaf9eac53cfdb984ddaa84'


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def read_csv(path):
    with Path(path).open(newline='') as f: return list(csv.DictReader(f))

def load_parent(inputs):
    l4=json.loads((inputs/'l4_source_and_transfer.json').read_text())
    tm=json.loads((inputs/'real_time_mpfr.json').read_text())
    native=json.loads((inputs/'rust_l4.json').read_text())
    assert l4['source']==SOURCE_SHA and l4['BASS_original_Rust_blob']==EXPECTED_SOURCE_RUST
    assert tm['rust_source_blob']==EXPECTED_SOURCE_RUST and native['BASS_original_Rust_blob']==EXPECTED_SOURCE_RUST
    assert all(tm['cases'][str(n)]['cases'][str(s)]['physical_source_sha256']==SOURCE_SHA for n in (6,8) for s in (4,8,16))
    return l4,tm,native

def l4_from_rust(rows):
    E=np.asarray([float(r['E']) for r in rows]); assert E.shape==(41,) and E.min()>0
    time=np.asarray([float(r['u']) for r in rows]);assert np.max(abs(time-np.linspace(0,.08,41)))<3e-15
    # Real + conjugate parity; use full complex m to avoid conventions from truncation.
    a=np.asarray([[complex(float(r[f'a_4_{m}_re']),float(r[f'a_4_{m}_im']))
                   for m in range(-4,5)] for r in rows])
    adot=np.asarray([[complex(float(r[f'da_4_{m}_re']),float(r[f'da_4_{m}_im']))
                   for m in range(-4,5)] for r in rows])
    # Reflection-even, only m even and real up to binary roundoff.
    assert np.max(abs(a[:,1::2]))<1e-11 # m=-3,-1,1,3
    for m in (1,2,3,4):
        assert np.max(abs(a[:,4-m]-(-1)**m*a[:,4+m].conj()))<1e-11
    z=4*np.pi*a/E[:,None]
    zdot=(4*np.pi/E[:,None])*(adot - np.array([float(r['Eprime']) for r in rows])[:,None]/E[:,None]*a)
    # z source time derivative exact conditional on stored ell,h path derivatives.
    K=(z@z.conj().T)/9
    Ku=(zdot@z.conj().T)/9
    Kv=(z@zdot.conj().T)/9
    assert np.max(abs(K.imag))<1e-12 and np.max(abs(K-K.T.conj()))<1e-12
    K=K.real; Ku=Ku.real; Kv=Kv.real
    C=np.diag(K).copy()
    assert C.min()>0
    rho=K/np.sqrt(C[:,None]*C[None,:])
    D2=C[:,None]+C[None,:]-2*K
    return {'u':time,'E':E,'K':K,'Ku':Ku,'Kv':Kv,'C':C,'rho':rho,'D2':D2,
            'a':a,'adot':adot,'z':z,'zdot':zdot}

def l4_from_dop(rows):
    assert len(rows)==41
    time=np.array([float(r['u']) for r in rows]);assert np.max(abs(time-np.linspace(0,.08,41)))<2e-15
    E=np.array([float(r['E']) for r in rows]);assert E.min()>.6
    a=np.stack([np.array([float(r[k]) for r in rows]) for k in ('a40','a42','a44')],axis=1)
    G=(4*np.pi/E[:,None])*a*np.sqrt(np.array([1.,2.,2.]))[None,:]
    K=G@G.T/9
    return {'K':K,'E':E,'u':time,'C':np.diag(K)}

def generate(inputs,out):
    inputs=Path(inputs);out=Path(out);out.mkdir(parents=True,exist_ok=True)
    l4,tm,native=load_parent(inputs)
    summary={'schema':'bass.ce1y.rk4_sky_vs_dop853_model_data.v1','original_binary64_source_sha256':SOURCE_SHA,
        'parent_pr270_head':PARENT_HEAD, 'parent_ci':PARENT_PR270_CI,
        'certified_kernel_scope':'Exact-real continuum vs exact-real GL source on certified RK4/Hermite geometry path only',
        'input_numeric_rust_centers_are_NOT_rigorous_MPFR_intervals':True,
        'DOP853_bridge_is_empirical_NOT_certified':True,'upper_dag':'9/15','upper_edges':21,
        'ce1':'PARTIAL','production_ready':False,'merge_ready':False,'auto_next':False,
        'channel_results':{},'physical_rows':0,'DOP853_reference':{},'input_file_sha256':{}}
    data={}
    for n in (6,8):
        p=inputs/f'GL{n}_DOP853_coupled_41epochs.csv'
        assert sha(p)==GL_DOP_CSV_SHA[n],(n,sha(p))
        summary['input_file_sha256'][p.name]=sha(p)
        dop=l4_from_dop(read_csv(p))
        summary['DOP853_reference'][str(n)]={'initial_K4':float(dop['K'][0,0]),'endpoint_K4':float(dop['K'][0,-1])}
        for steps in (4,8,16):
            key=f'GL{n}_STEPS{steps}'
            p=inputs/f'{key}_BASS_RUST_SKY.csv';summary['input_file_sha256'][p.name]=sha(p)
            rows=read_csv(p); assert len(rows)==41
            phys=l4_from_rust(rows)
            model_native=native['cases'][key]
            assert model_native['epoch_count']==41
            assert abs(float(model_native['K4_delta_0_008_native'])-phys['K'][0,-1])<1e-13
            cert=l4['cases'][str(n)]['time_path_cases'][str(steps)]
            assert cert['parent_path_coefficients_sha256']==model_native['certified_path_coefficients_sha256']
            # Preserve as proof-defined exact upper decimals. Do not relabel as a full
            # interval about floating output: evaluation roundoff is not certified.
            bsource=float(cert['source_kernel_upper_ceil_27'])
            bgeom=float(cert['geometry_kernel_upper_ceil_27'])
            btotal=float(cert['total_cross_kernel_upper_ceil_27'])
            assert 0<bsource<btotal and 0<bgeom<btotal
            raw_gap=phys['K']-dop['K']; data[key]=(phys,dop)
            if np.min(phys['D2'])<-1e-12 or np.max(np.abs(phys['rho']))>1+1e-12:raise ArithmeticError('Non-physical Gram numerical result')
            summary['channel_results'][key]={
                'source_rays':6*n*n,'panels':steps,'proper_time_samples':41,
                'number_of_two_time_pairs':1681,'source_bound_uniform':cert['source_kernel_upper_ceil_27'],
                'geometry_bound_uniform':cert['geometry_kernel_upper_ceil_27'],
                'total_conditional_exact_real_bound_uniform':cert['total_cross_kernel_upper_ceil_27'],
                'max_empirical_abs_K4delta_minus_DOP853':float(np.max(abs(raw_gap))),
                'endpoint_K4delta_RK4':float(phys['K'][0,-1]),
                'endpoint_K4delta_DOP853':float(dop['K'][0,-1]),
                'endpoint_difference_RK4_minus_DOP853':float(raw_gap[0,-1]),
                'minimum_Gram_eigenvalue_roundoff':float(np.linalg.eigvalsh(phys['K']).min()),
                'max_parity_imaginary_residual':float(np.max(abs(phys['a'].imag))),
                'sample_center_not_a_certified_interval':True}
            with (out/f'{key}_two_time_K4_1681.csv').open('w',newline='') as f:
                writer=csv.writer(f)
                writer.writerow(['u','v','K4_delta_RK4_BASS_Rust','K4_delta_DOP853_reference','empirical_difference',
                                 'r4_RK4','D4_squared_RK4','dK4_du_RK4','dK4_dv_RK4',
                                 'uniform_source_bound_conditional','uniform_geometry_bound_conditional',
                                 'uniform_total_exact_real_functional_bound_conditional'])
                for i in range(41):
                    for j in range(41):
                        writer.writerow([format(float(phys['u'][i]),'.17g'),format(float(phys['u'][j]),'.17g'),
                                         format(float(phys['K'][i,j]),'.17g'),format(float(dop['K'][i,j]),'.17g'),
                                         format(float(raw_gap[i,j]),'.17g'),format(float(phys['rho'][i,j]),'.17g'),
                                         format(float(phys['D2'][i,j]),'.17g'),format(float(phys['Ku'][i,j]),'.17g'),
                                         format(float(phys['Kv'][i,j]),'.17g'),cert['source_kernel_upper_ceil_27'],
                                         cert['geometry_kernel_upper_ceil_27'],cert['total_cross_kernel_upper_ceil_27']])
            np.savez_compressed(out/f'{key}_two_time_arrays.npz',u=phys['u'],K4delta_RK4=phys['K'],
                                K4delta_DOP853=dop['K'],K4delta_error_empirical=raw_gap,
                                r4=phys['rho'],D4_squared=phys['D2'],dK_du=phys['Ku'],dK_dv=phys['Kv'])
            summary['physical_rows']+=1681
    summary['max_over_6_cases_empirical_DOP853_bridge']=max(x['max_empirical_abs_K4delta_minus_DOP853'] for x in summary['channel_results'].values())
    summary['max_uniform_conditional_exact_real_K4_bound']=max(float(x['total_conditional_exact_real_bound_uniform']) for x in summary['channel_results'].values())
    (out/'SCIENCE_RESULTS.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
    print('CE1Y_10086_PHYSICAL_TWO_TIME_K4_ROWS_GENERATED',summary['physical_rows'])
    print('CE1Y_MODEL_COMPARED_TO_DOP853_EMPIRICAL',summary['max_over_6_cases_empirical_DOP853_bridge'])
    for k,v in summary['channel_results'].items():
        print(k,'K4(0,.08)',f"{v['endpoint_K4delta_RK4']:.17g}", 'max DOP gap',f"{v['max_empirical_abs_K4delta_minus_DOP853']:.3e}", 'conditional math bound',v['total_conditional_exact_real_bound_uniform'])
    return summary

def main():
    p=argparse.ArgumentParser();p.add_argument('--inputs',default=str(Path(__file__).resolve().parents[1]/'input'))
    p.add_argument('--output',default=str(Path(__file__).resolve().parents[1]/'data'))
    a=p.parse_args();generate(Path(a.inputs),Path(a.output))
if __name__=='__main__':main()

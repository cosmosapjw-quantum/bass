#!/usr/bin/env python3
"""CE1-V: deterministic unequal-epoch bolometric energy-sky angular cross-power.

No stochastic expectation, cosmic-variance or temperature assumption.
Uses the parent CE1-U original frozen six-cell, self-consistently coupled
Einstein-Vlasov GL6 and GL8 (each 41 proper-time states). The incoming normal
observer tetrad axes at all epochs are identified by Bianchi-I coordinates.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import numpy as np
from numpy.polynomial.legendre import Legendre

PARENT_HEAD = '15bb9fd015570c1562a4a7b9102f25a8481796f5'
ORIGINAL_PHYSICAL_SOURCE_SHA = '022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035'
EXPECTED_INPUT = {
    6: '6eff8cd9f31d027bbee55720332302b6fbad71b3639b5809aab6b9ce6f53e489',
    8: '1398980ec71662494273e05eb4bd52a78f6e6c7f208702638da6c739698f7502',
}


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load_channel(path: Path, n: int) -> dict:
    if sha(path) != EXPECTED_INPUT[n]:
        raise ValueError('Input CE1-U coupled history lost byte identity')
    with path.open(newline='', encoding='utf-8') as f:
        r = list(csv.DictReader(f))
    if len(r) != 41:
        raise ValueError('Expected 41 unique physical proper-time records')
    cols = ('u','E','Eprime','h1','h2','h3','P1','P2','P3','P1prime','P2prime','P3prime',
            'a20','a22','a40','a42','a44','da20','da22','da40','da42','da44',
            'C2','C4','C2prime','C4prime','Hamiltonian_C')
    d = {k:np.array([float(row[k]) for row in r], dtype=float) for k in cols}
    if not all(np.isfinite(v).all() for v in d.values()):
        raise ValueError('Non-finite source physical record')
    if not np.allclose(d['u'], np.linspace(0, .08, 41), atol=2e-16, rtol=0):
        raise ValueError('Improper physical-time grid')
    if not np.all(d['E'] > 0) or not all(np.all(d[k] > 0) for k in ('h1','h2','h3')):
        raise ValueError('Non-expanding or negative-energy source')
    if np.max(np.abs(d['P1'] + d['P2'] + d['P3'] - d['E'])) > 2e-12:
        raise ValueError('Massless trace source failure')
    for ell, keys, dk in [(2, ['a20','a22'], ['da20','da22']),
                          (4, ['a40','a42','a44'], ['da40','da42','da44'])]:
        factors = np.array([1]+[2]*(len(keys)-1), dtype=float)
        a = np.stack([d[k] for k in keys], axis=1)
        ad = np.stack([d[k] for k in dk], axis=1)
        C = np.sum(factors*a*a, axis=1)/(2*ell+1)
        Cp = 2*np.sum(factors*a*ad, axis=1)/(2*ell+1)
        if np.max(np.abs(C-d[f'C{ell}'])) > 2e-14 or np.max(np.abs(Cp-d[f'C{ell}prime'])) > 2e-14:
            raise ValueError('Original complex-harmonic / parity normalization mismatch')
    return d


def product_kernel(d: dict, ell: int) -> dict:
    names = ['a20','a22'] if ell == 2 else ['a40','a42','a44']
    dnames = ['da20','da22'] if ell == 2 else ['da40','da42','da44']
    weights = np.array([1]+[2]*(len(names)-1), dtype=np.float64)
    A = np.stack([d[k] for k in names], axis=1)
    Ad = np.stack([d[k] for k in dnames], axis=1)
    # With reflection parity only m=0, +-2, +-4 survive; conjugate m pairs counted twice.
    G = A*np.sqrt(weights)[None,:]
    Gd = Ad*np.sqrt(weights)[None,:]
    D = 2*ell+1
    K = G@G.T / D
    Ku = Gd@G.T/D
    Kv = G@Gd.T/D
    C = np.diag(K)
    factor = 4*np.pi/d['E']
    KF = K*factor[:,None]*factor[None,:]
    KFu = (Ku-d['Eprime'][:,None]/d['E'][:,None]*K)*factor[:,None]*factor[None,:]
    KFv = (Kv-K*d['Eprime'][None,:]/d['E'][None,:])*factor[:,None]*factor[None,:]
    CF = np.diag(KF)
    rho = K/np.sqrt(C[:,None]*C[None,:])
    dist2 = CF[:,None]+CF[None,:]-2*KF
    # This is a Gram kernel, so negative dist2 is only roundoff and must be tiny.
    return {'K':K,'Ku':Ku,'Kv':Kv,'C':C,'KF':KF,'KFu':KFu,'KFv':KFv,'CF':CF,
            'rho':rho,'dist2':dist2,'G':G,'Gd':Gd,'weights':weights}


def build_channel(d: dict, out: Path, n: int) -> tuple[dict,dict]:
    k2 = product_kernel(d,2)
    k4 = product_kernel(d,4)
    kernels = {2:k2,4:k4}
    gam = np.linspace(0.,np.pi,181)
    cosg = np.cos(gam)
    P2 = Legendre.basis(2)(cosg)
    P4 = Legendre.basis(4)(cosg)
    xi = (5*k2['KF'][:,:,None]*P2[None,None,:]+9*k4['KF'][:,:,None]*P4[None,None,:])/(4*np.pi)
    data = {
        'u':d['u'],'gamma_rad':gam,'K2_bolometric':k2['K'],'K4_bolometric':k4['K'],
        'K2_fractional':k2['KF'],'K4_fractional':k4['KF'],
        'rho2':k2['rho'],'rho4':k4['rho'],'D2_squared':k2['dist2'],'D4_squared':k4['dist2'],
        'xi_even_l2_l4':xi,
    }
    np.savez_compressed(out/f'GL{n}_two_time_rotation_average.npz', **data)
    with (out/f'GL{n}_two_time_1681.csv').open('w', newline='') as f:
        fields = ['u','v','K2_U','K4_U','K2_delta','K4_delta','rho2','rho4','D2_squared','D4_squared',
                  'dK2_du','dK2_dv','dK4_du','dK4_dv','dK2delta_du','dK2delta_dv',
                  'dK4delta_du','dK4delta_dv','xi_gamma0','xi_gamma90','xi_gamma180']
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for i in range(41):
            for j in range(41):
                w.writerow({'u':f'{d["u"][i]:.17g}','v':f'{d["u"][j]:.17g}',
                    'K2_U':f'{k2["K"][i,j]:.17g}','K4_U':f'{k4["K"][i,j]:.17g}',
                    'K2_delta':f'{k2["KF"][i,j]:.17g}','K4_delta':f'{k4["KF"][i,j]:.17g}',
                    'rho2':f'{k2["rho"][i,j]:.17g}','rho4':f'{k4["rho"][i,j]:.17g}',
                    'D2_squared':f'{k2["dist2"][i,j]:.17g}','D4_squared':f'{k4["dist2"][i,j]:.17g}',
                    'dK2_du':f'{k2["Ku"][i,j]:.17g}','dK2_dv':f'{k2["Kv"][i,j]:.17g}',
                    'dK4_du':f'{k4["Ku"][i,j]:.17g}','dK4_dv':f'{k4["Kv"][i,j]:.17g}',
                    'dK2delta_du':f'{k2["KFu"][i,j]:.17g}','dK2delta_dv':f'{k2["KFv"][i,j]:.17g}',
                    'dK4delta_du':f'{k4["KFu"][i,j]:.17g}','dK4delta_dv':f'{k4["KFv"][i,j]:.17g}',
                    'xi_gamma0':f'{xi[i,j,0]:.17g}','xi_gamma90':f'{xi[i,j,90]:.17g}',
                    'xi_gamma180':f'{xi[i,j,-1]:.17g}'})
    results={'states':41,'pairs':41**2,'lmax':4,'rays':6*n*n,
      'endpoints':{},'max_abs_parent_amplitude_error':{},'min_eigenvalue':{},
      'min_rho':{},'max_rho':{},'max_abs_symmetry_gap':{},'max_abs_diag_gap':{},
      'max_abs_diagonal_derivative_gap':{},'max_abs_cauchy_excess':{},
      'shape_change':{},'stored_rank':{},
      'max_negative_distance2':{},'physics_identification':'fixed comoving normal-tetrad coordinate axes; deterministic SO(3)-rotationally averaged fractional energy-sky cross-power; no ensemble, no temperature'}
    for ell,k in kernels.items():
        ev=np.linalg.eigvalsh(k['KF'])
        results['min_eigenvalue'][str(ell)]=float(ev.min())
        results['min_rho'][str(ell)]=float(k['rho'].min())
        results['max_rho'][str(ell)]=float(k['rho'].max())
        results['max_abs_symmetry_gap'][str(ell)]=float(np.max(np.abs(k['KF']-k['KF'].T)))
        results['max_abs_diag_gap'][str(ell)]=float(np.max(np.abs(np.diag(k['K'])-d[f'C{ell}'])))
        results['max_abs_diagonal_derivative_gap'][str(ell)]=float(np.max(np.abs(2*np.diag(k['Ku'])-d[f'C{ell}prime'])))
        results['max_abs_cauchy_excess'][str(ell)]=float(max(0.,np.max(np.abs(k['rho'])-1)))
        results['max_negative_distance2'][str(ell)]=float(max(0.,-k['dist2'].min()))
        results['stored_rank'][str(ell)] = len(k['weights'])
        results['endpoints'][str(ell)] = {'Cdelta_initial':float(k['CF'][0]),'Cdelta_final':float(k['CF'][-1]),
             'Kdelta_0_008':float(k['KF'][0,-1]),'rho_0_008':float(k['rho'][0,-1]),
             'D2_0_008':float(k['dist2'][0,-1]),'Ku_0_008':float(k['Ku'][0,-1]),
             'Kdelta_u008_v004':float(k['KF'][-1,20]),
             'max_abs_Kdelta':float(np.max(abs(k['KF'])))}
        results['shape_change'][str(ell)]={'max_squared_contrast_difference_from_initial':float(k['dist2'][0,:].max()),
                  'integrated_squared_contrast_difference_from_initial':float(np.trapezoid(k['dist2'][0,:],d['u']))}
    return results, kernels


def main(argv=None):
    ap=argparse.ArgumentParser()
    ap.add_argument('--source-dir',default=str(Path(__file__).resolve().parents[1]/'inputs'))
    ap.add_argument('--out-dir',default=str(Path(__file__).resolve().parents[1]/'data'))
    args=ap.parse_args(argv)
    src=Path(args.source_dir); out=Path(args.out_dir);out.mkdir(parents=True,exist_ok=True)
    contract=json.loads((src/'SOURCE_CONTRACT.json').read_text())
    if contract['original_physical_six_cell_sha256'] != ORIGINAL_PHYSICAL_SOURCE_SHA or contract['parent_head']!=PARENT_HEAD:
        raise ValueError('Wrong physical source identity')
    summary={'schema':'bass.ce1v.unequal_time_angular_energy_v1','parent_pr':264,'parent_sha':PARENT_HEAD,
       'original_source_binary64_sha256':ORIGINAL_PHYSICAL_SOURCE_SHA,
       'source_archive_sha256':contract['parent_archive_sha256'],'upper_dag':'9/15','upper_edges':21,
       'ce1':'PARTIAL','production_ready':False,'merge_ready':False,
       'cross_time_interpretation':'fixed tetrad axes deterministic bolometric fractional sky, SO3 rotation average; not stochastic covariance or observation of two lightcones',
       'channels':{},'interchannel':{}}
    outputs={}
    for n in (6,8):
        d=load_channel(src/f'GL{n}_coupled_41epochs.csv',n)
        ch,k=build_channel(d,out,n)
        summary['channels'][f'GL{n}']=ch
        outputs[n]=k
    for ell in (2,4):
        ka=outputs[6][ell]['KF'];kb=outputs[8][ell]['KF']
        summary['interchannel'][f'max_abs_K{ell}delta_GL6_vs_GL8']=float(np.max(np.abs(ka-kb)))
        summary['interchannel'][f'endpoint_abs_K{ell}delta_GL6_vs_GL8']=float(abs(ka[0,-1]-kb[0,-1]))
    (out/'RESULTS.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k!='channels'},indent=2))
    for n in (6,8):
        print(f'GL{n}', json.dumps(summary['channels'][f'GL{n}']['endpoints']))
    return summary

if __name__=='__main__':main()

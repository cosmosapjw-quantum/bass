#!/usr/bin/env python3
"""CE1-OBS: observer-frame bolometric angular-energy sky, frozen BASS CE1-P inputs.

No spectrum, blackbody, polarization, closure, or new dynamical source is introduced.
Stored-ray channels are atomic angular measures; GL channels sample the original
piecewise-constant six-cell continuum distribution with actual solid-angle weights.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import importlib.util
import itertools
import json
import math
from pathlib import Path
import numpy as np
from scipy.special import sph_harm_y

PARENT_ZIP_SHA = '162097533f0bc88ec5ddee8f10edcc08aaf4b81cbf2e4c14c42982dbf73ca6b7'
INPUT_SHA = '022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035'
PARENT_HEAD = '0656e98989750de4ea19c510ff2052654aaa3eda'
PARENT_PR = 258
GL_ORDERS = (24, 40)
REFINEMENTS = (1, 4, 8, 16)
SIGN_OCTANTS = np.array(list(itertools.product((-1., 1.), repeat=3)), dtype=np.float64)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def source_lock(parent, source_archive):
    """Read parent source and verify original binary64 measure, source ZIP and manifest."""
    parent = Path(parent)
    zip_path = Path(source_archive)
    if not zip_path.exists() or sha(zip_path) != PARENT_ZIP_SHA:
        raise ValueError('CE1-P source package is missing or SHA-256 differs')
    manifest = json.loads((parent / 'MANIFEST.json').read_text())
    for path, info in manifest['files'].items():
        file_path = parent / path
        if not file_path.exists() or sha(file_path) != info['sha256']:
            raise ValueError(f'CE1-P manifest mismatch: {path}')
    spec = importlib.util.spec_from_file_location('ce1p_frozen_inputs', parent/'source/generate_physical_history.py')
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    byte_source = b''.join(x.tobytes() for x in (module.MU, module.PHI, module.ENERGY, module.SHEAR))
    if hashlib.sha256(byte_source).hexdigest() != INPUT_SHA:
        raise ValueError('CE1-P six-cell binary64 input identity mismatch')
    if manifest['source_input_binary64_sha256'] != INPUT_SHA:
        raise ValueError('CE1-P manifest physics lock differs')
    if module.END != .08 or module.N_TIMES != 41:
        raise ValueError('CE1-P time sampling changed')
    return module, manifest


def read_history(path):
    with Path(path).open(newline='') as f:
        rows = [{k: (v if k == 'channel' else float(v)) for k,v in row.items() if v not in ('',None)}
                for row in csv.DictReader(f)]
    if len(rows) != 41 or not np.allclose([r['u'] for r in rows], np.linspace(0.,.08,41),rtol=0,atol=1e-15):
        raise ValueError('Frozen physical-history time grid differs')
    return rows


def build_gl(mu,phi,energy,order):
    """Node weights use positive-octant dOmega=(pi/2)dmu dt; 8 reflections."""
    x,w = np.polynomial.legendre.leggauss(order)
    ns=[];weights=[];omega=[];dens=[];cell=[];muval=[];tval=[]
    for i in range(len(mu)-1):
        for j in range(len(phi)-1):
            dm,dt=mu[i+1]-mu[i],phi[j+1]-phi[j]
            mm=mu[i]+dm*(1+x)/2
            tt=phi[j]+dt*(1+x)/2
            m,t=np.meshgrid(mm,tt,indexing='ij')
            pi2t=.5*np.pi*t
            n=np.stack((np.sqrt(1.-m*m)*np.cos(pi2t),
                        np.sqrt(1.-m*m)*np.sin(pi2t),m),axis=-1).reshape(-1,3)
            w2=np.outer(w,w).reshape(-1)
            total_mass=energy[i,j]*w2/4
            d_omega_oct=np.pi/2*dm*dt*w2/4
            I0=np.full(order*order,energy[i,j]/(4*np.pi*dm*dt))
            ns.append(n);weights.append(total_mass);omega.append(d_omega_oct)
            dens.append(I0);cell.extend([f'{i}_{j}']*(order*order))
            muval.append(m.ravel());tval.append(t.ravel())
    n=np.concatenate(ns);mass=np.concatenate(weights)
    Omega=np.concatenate(omega);I0=np.concatenate(dens)
    assert np.max(np.abs(np.sum(n*n,axis=1)-1.))<3e-15
    assert np.max(np.abs(8*I0*Omega-mass))<3e-16
    assert abs(np.sum(mass)-.9)<1e-13
    assert abs(8*np.sum(Omega)-4*np.pi)<1e-12
    return dict(n=n,mass=mass,omega0_oct=Omega,I0=I0,cell=np.array(cell),
                mu=np.concatenate(muval),phi_fraction=np.concatenate(tval),type='gl')


def build_stored(mu,phi,energy,refinement):
    """Reconstruct original MPFR-cell mid-square ray formula (real analytic cell means).

    Input cell masses are original binary64 / f^2, not altered quadrature weights.
    Difference from directed-MPFR midpoint is at roundoff, compared to saved
    physical E,P for all times with a separate identity acceptance test.
    """
    ns=[]; masses=[]
    for i in range(len(mu)-1):
        for j in range(len(phi)-1):
            for k in range(refinement):
                ma=mu[i]+(mu[i+1]-mu[i])*k/refinement
                mb=mu[i]+(mu[i+1]-mu[i])*(k+1)/refinement
                mz=(ma*ma+ma*mb+mb*mb)/3
                for l in range(refinement):
                    ta=phi[j]+(phi[j+1]-phi[j])*l/refinement
                    tb=phi[j]+(phi[j+1]-phi[j])*(l+1)/refinement
                    C=.5+(math.sin(math.pi*tb)-math.sin(math.pi*ta))/(2*math.pi*(tb-ta))
                    n=np.sqrt([max(0,(1-mz)*C),max(0,(1-mz)*(1-C)),mz])
                    ns.append(n);masses.append(float(energy[i,j])/(refinement**2))
    n=np.asarray(ns,float);mass=np.asarray(masses,float)
    if abs(mass.sum()-.9)>1e-13 or np.max(abs(np.sum(n*n,axis=1)-1))>5e-15:
        raise ArithmeticError('Unexpected stored ray normalization')
    return dict(n=n,mass=mass,type='atomic')


def ray_observer(ell,sampler):
    ell=np.asarray(ell,float)
    B=np.exp(-ell)
    v_inv=math.exp(-sum(ell))
    p=sampler['n']*B
    r=np.linalg.norm(p,axis=1)
    e=p/r[:,None]
    jac=v_inv/r**3
    atomic=v_inv*sampler['mass']*r
    return dict(r=r,e=e,jac=jac,atomic=atomic,B=B,V_inv=v_inv)


def harmonics(e,w):
    """Nonzero harmonics for an eight-reflected sky, Condon-Shortley convention.

    Signed octant replicas cancel odd l / odd m / sine sectors. These are
    polynomial evaluations for (l,m)=(0,0),(2,0),(2,2),(4,0),(4,2),(4,4).
    """
    x,y,z=e.T
    x2=x*x;y2=y*y;z2=z*z
    return {
      'a00':float(np.dot(w,np.ones(len(w))/math.sqrt(4*math.pi))),
      'a20':float(np.dot(w,math.sqrt(5/(16*math.pi))*(3*z2-1))),
      'a22':float(np.dot(w,math.sqrt(15/(32*math.pi))*(x2-y2))),
      'a40':float(np.dot(w,3/(16*math.sqrt(math.pi))*(35*z2*z2-30*z2+3))),
      'a42':float(np.dot(w,3/8*math.sqrt(5/(2*math.pi))*(7*z2-1)*(x2-y2))),
      'a44':float(np.dot(w,3/16*math.sqrt(35/(2*math.pi))*(x2*x2-6*x2*y2+y2*y2))),
    }


def direct_spherical_check(e,w,harm):
    """Independent scipy.special spherical harmonics on all eight octants."""
    ep=(e[:,None,:]*SIGN_OCTANTS[None,:,:]).reshape(-1,3)
    ww=np.repeat(w/8,8)
    theta=np.arccos(np.clip(ep[:,2],-1,1))
    phi=np.arctan2(ep[:,1],ep[:,0])
    err=0.; odd=0.; unexpected=0.; conj=0.
    coeff={}
    for L in range(5):
        for m in range(-L,L+1):
            val=complex(np.dot(ww,np.conj(sph_harm_y(L,m,theta,phi))))
            coeff[(L,m)]=val
            if L%2:odd=max(odd,abs(val))
            if m%2:unexpected=max(unexpected,abs(val))
            if L%2==0 and m%2==0 and m>=0:
                key=f'a{L}{m}'
                if key in harm:err=max(err,abs(val-harm[key]))
            if abs(val.imag)>unexpected:unexpected=max(unexpected,abs(val.imag))
    for (L,m),val in coeff.items():
        if m>0:conj=max(conj,abs(coeff[L,-m]-((-1)**m)*val.conjugate()))
    return dict(max_polynomial_vs_scipy=err,odd_l=odd,odd_m_or_imag=unexpected,
                conjugate_symmetry=conj)


def verify_history(rows,sampler,channel,output_sky=False):
    out=[]; samples=None
    errors=dict(kinetic_energy=0.,kinetic_pressure=0.,sky_energy=0.,sky_pressure=0.,
                a00=0.,a20=0.,a22=0.,energy_positive=True)
    for row in rows:
        ell=[row[f'ell{i}'] for i in (1,2,3)]
        obs=ray_observer(ell,sampler)
        e,w=obs['e'],obs['atomic']
        H=harmonics(e,w)
        E=float(np.sum(w))
        P=np.einsum('n,ni->i',w,e*e)
        savedE=row['E'];savedP=np.array([row[f'P{i}'] for i in (1,2,3)])
        errors['kinetic_energy']=max(errors['kinetic_energy'],abs(E-savedE))
        errors['kinetic_pressure']=max(errors['kinetic_pressure'],float(np.max(np.abs(P-savedP))))
        errors['energy_positive'] &= bool(np.all(w>=0))
        errors['a00']=max(errors['a00'],abs(H['a00']-E/math.sqrt(4*math.pi)))
        errors['a20']=max(errors['a20'],abs(H['a20']-math.sqrt(5/(16*math.pi))*(3*P[2]-E)))
        errors['a22']=max(errors['a22'],abs(H['a22']-math.sqrt(15/(32*math.pi))*(P[0]-P[1])))
        # GL values are actual sample values J_obs(e) and quadrature solid angles.
        # For stored finite rays there is only an atomic measure, no sky density.
        if sampler['type']=='gl':
            Iobs=sampler['I0']*obs['r']**4
            dOmega_obs_oct=obs['jac']*sampler['omega0_oct']
            E_sky=8*np.sum(Iobs*dOmega_obs_oct)
            P_sky=8*np.einsum('n,ni->i',Iobs*dOmega_obs_oct,e*e)
            errors['sky_energy']=max(errors['sky_energy'],abs(E_sky-savedE))
            errors['sky_pressure']=max(errors['sky_pressure'],float(np.max(np.abs(P_sky-savedP))))
            if output_sky and abs(row['u']-.08)<1e-14:
                samples=[]
                for k in range(len(w)):
                    samples.append({'cell':sampler['cell'][k],
                       'initial_mu':float(sampler['mu'][k]),
                       'initial_phi_fraction':float(sampler['phi_fraction'][k]),
                       **{f'n0_{axis}':float(sampler['n'][k,i]) for i,axis in enumerate('xyz')},
                       **{f'e_obs_{axis}':float(e[k,i]) for i,axis in enumerate('xyz')},
                       'energy_ratio_r':float(obs['r'][k]),
                       'jac_dOmegaObs_over_dOmega0':float(obs['jac'][k]),
                       'J0_dimless_per_sr':float(sampler['I0'][k]),
                       'J_obs_dimless_per_sr':float(Iobs[k]),
                       'dOmega0_oct_node':float(sampler['omega0_oct'][k]),
                       'dOmegaObs_oct_node':float(dOmega_obs_oct[k]),
                       'energy_total8_node':float(w[k])})
        c2=(H['a20']**2+2*H['a22']**2)/5
        c4=(H['a40']**2+2*H['a42']**2+2*H['a44']**2)/9
        out.append(dict(channel=channel,u=row['u'],E=E,P1=P[0],P2=P[1],P3=P[2],
                        **H,C2_deterministic=c2,C4_deterministic=c4))
    return out,errors,samples


def csvout(path,rows):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    with Path(path).open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)


def run(parent,output,source_archive):
    parent,output=Path(parent),Path(output)
    output.mkdir(parents=True,exist_ok=True)
    M,manifest=source_lock(parent,source_archive)
    samplers={f'stored_ref{k}':build_stored(M.MU,M.PHI,M.ENERGY,k) for k in REFINEMENTS}
    samplers.update({f'gl{k}':build_gl(M.MU,M.PHI,M.ENERGY,k) for k in GL_ORDERS})
    histories={}
    errors={}
    harmonics_all=[]
    for name,sampler in samplers.items():
        csv_name = ('continuum_GL'+str(int(name[2:])) if name.startswith('gl')
                    else name)+'_history.csv'
        rows=read_history(parent/'data'/csv_name)
        multipoles,err,sky=verify_history(rows,sampler,name,output_sky=(name=='gl40'))
        errors[name]=err
        histories[name]=multipoles
        harmonics_all.extend(multipoles)
        if sky is not None:csvout(output/'data/gl40_observer_sky_positive_octant_u008.csv',sky)
    csvout(output/'data/multipoles_all_histories.csv',harmonics_all)
    max_sph={}
    for name in ('gl24','gl40','stored_ref8'):
        sam=samplers[name]
        for u_index in (0,20,40):
            row=read_history(parent/'data'/(('continuum_GL'+name[2:] if name.startswith('gl') else name)+'_history.csv'))[u_index]
            obs=ray_observer([row[f'ell{i}'] for i in (1,2,3)],sam)
            H=harmonics(obs['e'],obs['atomic'])
            ch=direct_spherical_check(obs['e'],obs['atomic'],H)
            max_sph[name+f'_t{u_index}']=ch
    fields=('a00','a20','a22','a40','a42','a44','E','P1','P2','P3')
    ref=histories['gl40']
    convergence={}
    for key,rows in histories.items():
        convergence[key]={f'max_abs_{f}_vs_GL40':max(abs(float(r[f])-float(q[f])) for r,q in zip(rows,ref))
                           for f in fields}
    out={'schema':'BASS.CE1OBS.ANGULAR_SKY.V1','generation':'actual physical-history-derived observer sky',
         'parent_pr':PARENT_PR,'parent_head':PARENT_HEAD,
         'parent_package_sha256':PARENT_ZIP_SHA,'parent_source_git_blobs':manifest['source_git_blobs'],
         'source_input_binary64_sha256':INPUT_SHA,
         'time_samples_per_channel':41,'channels':list(samplers),
         'sky_definition':'J_obs(e)=r(n)^4 J0(n), dOmega_obs=V^-1 r^-3 dOmega0',
         'harmonic_convention':'orthonormal complex Condon-Shortley, a_lm=int J_obs conj(Y_lm) dOmega_obs',
         'spectral_temperature':False,'polarization':False,'observation':False,
         'stored_ray_semantics':'atomic pushforward; NO pointwise sky intensity',
         'gl_semantics':'same original six-cell continuum density evaluated at Gauss-Legendre nodes (not certified)',
         'energy_units':'dimensionless E=8*pi*G*Tstar^2*rho_energy/c^2',
         'errors':errors,'independent_scipy_harmonic_checks':max_sph,
         'convergence':convergence,'gl40_initial_harmonics':ref[0],
         'gl40_final_harmonics':ref[-1],
         'upper_dag':'9/15','upper_edges':21,'ce1_status':'PARTIAL',
         'production_ready':False,'merge_ready':False,'auto_next':False,
         'distinct_author_R6_C9':'NOT_RUN'}
    (output/'data/results.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
    return out


def main():
    arg=argparse.ArgumentParser()
    arg.add_argument('--parent',required=True);arg.add_argument('--output',required=True)
    arg.add_argument('--source-archive',required=True,help='Original CE1-P ZIP with pinned SHA256')
    ns=arg.parse_args()
    result=run(ns.parent,ns.output,ns.source_archive)
    print(json.dumps({'parent_zip_verified':True,'channels':result['channels'],
        'max_history_E_error':max(z['kinetic_energy'] for z in result['errors'].values()),
        'max_history_P_error':max(z['kinetic_pressure'] for z in result['errors'].values()),
        'max_direct_harmonic_error':max(v['max_polynomial_vs_scipy'] for v in result['independent_scipy_harmonic_checks'].values()),
        'a20_final_GL40':result['gl40_final_harmonics']['a20'],
        'a22_final_GL40':result['gl40_final_harmonics']['a22'],
        'a40_final_GL40':result['gl40_final_harmonics']['a40']},indent=2))


if __name__=='__main__':main()

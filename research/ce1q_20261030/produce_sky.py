#!/usr/bin/env python3
"""CE1-Q: use BASS native Rust comoving Frame for actual physical angular-sky multipoles.

Reads *unchanged* frozen CE1-P six-channel numerical histories. Rust imports
BASS _rustcore/src/kinetic/comoving.rs. Source arrays are recreated with
PR253 exact Git-blob MPFR source, not a surrogate. GL24/40 continuum
quadrature and discrete stored rays remain different object types.

Model-generated unpolarized energy-integrated sky, not thermodynamic T/Q/U
or observational data; all multipole amplitudes carry CE1-P E units.
"""
from __future__ import annotations
import argparse,csv,hashlib,importlib.util,io,json,math,os,struct,subprocess,sys
from pathlib import Path
import numpy as np
from scipy.special import sph_harm_y

BASE=Path(__file__).resolve().parents[2]
PARENT=Path(os.environ.get('BASS_CE1Q_PARENT',str(BASE/'research/ce1q_20261030/parent_data')))
RUST=Path(os.environ.get('BASS_CE1Q_RUST',str(BASE/'research/ce1q_20261030/sky_native')))
ORIGINAL='022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035'
EXPECTED_REF8_N='9d46624cdb747a5760eda945d5effeb17f0619ade2b7198ee1700903123455ba'
EXPECTED_REF8_M='c421e8148af743ea44bbb565f32a44090e18299e0e0b15f20eee37fb0a232211'
SOURCE_BLOB='fdeb83a65cd424786ba6bb8ddadbcb2b2e2d45bf'

def sha(b):return hashlib.sha256(b).hexdigest()
def bits(x):return str(struct.unpack('<Q',struct.pack('<d',float(x)))[0])
def save_json(path,obj):Path(path).write_text(json.dumps(obj,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
def source():
    from bianchi.nonperturbative.einstein_tabulated_source import TabulatedRadiation
    from bianchi.nonperturbative.einstein_tabulated_source import __file__ as f
    raw=Path(f).read_bytes()
    blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
    assert blob==SOURCE_BLOB,(blob,SOURCE_BLOB)
    return TabulatedRadiation

def gl_source(n):
    # Reuse actual CE1-P generator, not a silently substituted angular geometry.
    root=Path(os.environ.get('BASS_CE1Q_CE1P_SOURCE',str(PARENT/'source/generate_physical_history.py')))
    spec=importlib.util.spec_from_file_location('ce1p_parent_authority',root)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    mu,ph,en,shear=mod.MU,mod.PHI,mod.ENERGY,mod.SHEAR
    assert sha(mu.tobytes()+ph.tobytes()+en.tobytes()+shear.tobytes())==ORIGINAL
    return mod.GLContinuum(n)

def inputs(rays,weights,history,lmax=4):
    lines=[f'{len(weights)} {len(history)} {lmax}']
    for m,n in zip(weights,rays): lines.append(' '.join([bits(m),*(bits(x) for x in n)]))
    for rec in history:
        lines.append(' '.join(bits(rec[k]) for k in ('u','ell1','ell2','ell3')))
    return '\n'.join(lines)+'\n'

def history_rows(name):
    path=PARENT/'data'/name
    assert path.exists(),f'missing preserved physical history: {path}'
    with path.open(newline='') as f:return [{k:(v if k=='channel' else float(v)) for k,v in r.items() if v!=''} for r in csv.DictReader(f)]

def parse_native(stdout):
    return [{k:float(v) for k,v in x.items()} for x in csv.DictReader(io.StringIO(stdout))]

def write_rows(path,rows):
    with Path(path).open('w',newline='') as f:
        d=csv.DictWriter(f,fieldnames=list(rows[0].keys()));d.writeheader();d.writerows(rows)

def harmonics(row,lmax=4):
    return {(l,m):complex(row[f'a_{l}_{m}_re'],row[f'a_{l}_{m}_im'])
            for l in range(lmax+1) for m in range(-l,l+1)}

def independently_reintegrated(rays,weights,ell,lmax=4):
    """Independent SciPy spherical harmonics in observer sky, not BASS harmonic code."""
    m=np.exp(-np.asarray(ell,dtype=float))
    p=np.asarray(rays,dtype=float)*m
    r=np.linalg.norm(p,axis=1); assert (r>0).all()
    physw=np.asarray(weights,dtype=float)*np.prod(m)*r/8
    directions=[]
    for sx in (-1,1):
        for sy in (-1,1):
            for sz in (-1,1):directions.append(-p/r[:,None]*np.array([sx,sy,sz]))
    n=np.concatenate(directions,axis=0)
    w=np.tile(physw,8)
    theta=np.arccos(np.clip(n[:,2],-1,1));phi=np.mod(np.arctan2(n[:,1],n[:,0]),2*np.pi)
    return {(l,j):complex(np.dot(w,np.conjugate(sph_harm_y(l,j,theta,phi))))
        for l in range(lmax+1) for j in range(-l,l+1)}

def make_maps(ell,source_cell_energy,mu,phi,ntheta=160,nphi=320):
    """Pointwise brightness only for original continuous 6-cell source."""
    theta=(np.arange(ntheta)+.5)*np.pi/ntheta
    az=(np.arange(nphi)+.5)*2*np.pi/nphi
    t,p=np.meshgrid(theta,az,indexing='ij')
    # Sky directions s=-n: physical photon n=-s.
    s=np.stack([np.sin(t)*np.cos(p),np.sin(t)*np.sin(p),np.cos(t)],axis=-1)
    B=s*np.exp(np.asarray(ell))  # initial qhat is -B/|B|; signs irrelevant to even source
    q=B/np.linalg.norm(B,axis=-1)[...,None]
    absq=np.abs(q)
    u=absq[...,2]
    v=(2/np.pi)*np.arctan2(absq[...,1],absq[...,0])
    i=np.clip(np.searchsorted(mu,u,side='right')-1,0,len(mu)-2)
    j=np.clip(np.searchsorted(phi,v,side='right')-1,0,len(phi)-2)
    density=source_cell_energy[i,j]/(4*np.pi*(mu[i+1]-mu[i])*(phi[j+1]-phi[j]))
    redshift=1/np.linalg.norm(B,axis=-1)
    sky=density*redshift**4
    return theta,az,sky

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);ap.add_argument('--quick',action='store_true')
    args=ap.parse_args();out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
    assert RUST.is_file(),f'BASS native Rust binary missing: {RUST}'
    test=subprocess.run([str(RUST),'--selftest'],check=True,capture_output=True,text=True,timeout=20)
    assert 'BASS_CE1Q_NATIVE_RUST_SELFTEST_PASS' in test.stdout
    cls=source()
    cases=(('stored_ref8',),('gl24',)) if args.quick else (('stored_ref1',),('stored_ref4',),('stored_ref8',),('stored_ref16',),('gl24',),('gl40',))
    identity={'schema':'bass.ce1q.model_sky.v1','upper_dag':'9/15','ce1':'PARTIAL',
       'input_binary64_source_sha256':ORIGINAL,'parent_pr':258,'parent_head':'0656e98989750de4ea19c510ff2052654aaa3eda',
       'native_bass_rust':'_rustcore/src/kinetic/comoving.rs Frame.apply/det/phys_dirs/real_ylm_l',
       'source_git_blob':SOURCE_BLOB,'scope':'model-generated collisionless angular energy, NOT observational CMB',
       'conventions':'observer photon propagation n=+M q/|M q|; incoming sky s=-n, Condon-Shortley complex Ylm',
       'channels':{},'physics_gates':{'blackbody_T':'NOT_RUN','polarized_Q_U':'NOT_RUN','likelihood':'NOT_RUN',
           'formal_MPFR_for_new_sky':'NOT_RUN','independent_author_R6_C9':'NOT_RUN'}}
    largest={'moment_gap':0.0,'native_real_basis_gap':0.0,'complex_harmonic_scipy_gap':0.0,
             'trace_gap':0.0,'monopole_gap':0.0,'quadrupole_from_pressure_gap':0.0,
             'parity_odd_gap':0.0,'negative_m_realfield_gap':0.0}
    summaries={}
    for c, in cases:
        if c.startswith('stored'):
            rf=int(c.replace('stored_ref',''))
            rad=cls([0,.5,1],[0,.25,.75,1],[[.1,.25,.05],[.2,.15,.15]],refinement=rf,backend='python_oracle')
            rays,weights=rad.n,rad.mass
            if rf==8:
                assert sha(np.asarray(rays,dtype='<f8').tobytes())==EXPECTED_REF8_N
                assert sha(np.asarray(weights,dtype='<f8').tobytes())==EXPECTED_REF8_M
            source_kind='atomic ray quadrature (NOT pointwise sky brightness)'
            history=history_rows(f'stored_ref{rf}_history.csv')
        else:
            gl=int(c[2:]); rad=gl_source(gl)
            rays,weights=rad.n,rad.mass
            source_kind='Gauss-Legendre quadrature of continuous six-cell density'
            history=history_rows(f'continuum_GL{gl}_history.csv')
        assert len(history)==41
        assert abs(float(sum(weights))-.9)<2e-12
        inp=inputs(rays,weights,history)
        cp=subprocess.run([str(RUST)],input=inp,text=True,capture_output=True,timeout=150)
        if cp.returncode:raise RuntimeError(f'Rust {c} failed: {cp.stderr[:400]}')
        rows=parse_native(cp.stdout);assert len(rows)==len(history)
        write_rows(out/f'{c}_alm.csv',rows)
        testidx=(0,20,40)
        for ix,(r,h) in enumerate(zip(rows,history)):
            e,p=float(r['E']),np.array([r['P1'],r['P2'],r['P3']]);amp=harmonics(r)
            # The stored E/P source in original CE1-P physical history is *not* replaced.
            largest['moment_gap']=max(largest['moment_gap'],abs(e-h['E']),*(abs(p[i]-h['P'+str(i+1)]) for i in range(3)))
            largest['trace_gap']=max(largest['trace_gap'],abs(e-p.sum()))
            largest['monopole_gap']=max(largest['monopole_gap'],abs(amp[(0,0)]*math.sqrt(4*math.pi)-e))
            a20=math.sqrt(5/(16*math.pi))*(3*p[2]-e)
            a22=math.sqrt(15/(32*math.pi))*(p[0]-p[1])
            largest['quadrupole_from_pressure_gap']=max(largest['quadrupole_from_pressure_gap'],abs(amp[(2,0)]-a20),abs(amp[(2,2)]-a22))
            largest['native_real_basis_gap']=max(largest['native_real_basis_gap'],r['native_real_basis_gap'])
            for (l,m),a in amp.items():
                if l%2 or m%2:largest['parity_odd_gap']=max(largest['parity_odd_gap'],abs(a))
                if m>0:largest['negative_m_realfield_gap']=max(largest['negative_m_realfield_gap'],abs(amp[(l,-m)]-(-1)**m*a.conjugate()))
            if ix in testidx and c in ('stored_ref8','gl24','gl40'):
                independent=independently_reintegrated(rays,weights,[h['ell1'],h['ell2'],h['ell3']])
                largest['complex_harmonic_scipy_gap']=max(largest['complex_harmonic_scipy_gap'],
                     max(abs(amp[k]-v) for k,v in independent.items()))
        endpoint=rows[-1]; ap=harmonics(endpoint)
        summaries[c]={'kind':source_kind,'ray_count':len(weights),'times':len(rows),
            'ray_sha256':sha(np.asarray(rays,dtype='<f8').tobytes()),
            'mass_sha256':sha(np.asarray(weights,dtype='<f8').tobytes()),
            'final_E':endpoint['E'],'final_P':[endpoint[f'P{i}'] for i in (1,2,3)],
            'final_a20_real':ap[(2,0)].real,'final_a22_real':ap[(2,2)].real,
            'final_a40_real':ap[(4,0)].real,'final_a42_real':ap[(4,2)].real,'final_a44_real':ap[(4,4)].real,
            'final_C2':sum(abs(ap[(2,m)])**2 for m in range(-2,3))/5,
            'final_C4':sum(abs(ap[(4,m)])**2 for m in range(-4,5))/9,
            'first_a20_real':harmonics(rows[0])[(2,0)].real,
            'first_a22_real':harmonics(rows[0])[(2,2)].real}
        identity['channels'][c]=summaries[c]
    assert largest['moment_gap']<5e-11,largest
    assert largest['monopole_gap']<5e-11,largest
    assert largest['trace_gap']<5e-11,largest
    assert largest['quadrupole_from_pressure_gap']<5e-11,largest
    assert largest['parity_odd_gap']<5e-11,largest
    assert largest['complex_harmonic_scipy_gap']<5e-11,largest
    assert largest['native_real_basis_gap']<5e-11,largest
    if 'gl40' in summaries:
        # Pointwise continuum density can be pushed to an observer sky map.
        final=history_rows('continuum_GL40_history.csv')[-1]
        theta,az,sky=make_maps([final['ell1'],final['ell2'],final['ell3']],
                  np.array([[.1,.25,.05],[.2,.15,.15]]),np.array([0,.5,1]),np.array([0,.25,.75,1]))
        np.savez_compressed(out/'gl40_observer_sky_map.npz',theta=theta,azimuth=az,energy_per_solid_angle=sky)
        identity['continuum_gl24_gl40_max_final_alm_gap']=float(max(abs(harmonics(parse_native((out/'gl24_alm.csv').read_text())[-1])[k]-harmonics(parse_native((out/'gl40_alm.csv').read_text())[-1])[k]) for k in harmonics(parse_native((out/'gl40_alm.csv').read_text())[-1])))
    identity['max_residuals']=largest
    identity['main_model_restrictions']='No spectral distribution, no polarized collision, no local boost, no global tilt, no time LoS visibility, no observational likelihood'
    save_json(out/'results.json',identity)
    print(json.dumps({'status':'CE1Q_MODEL_SKY_GENERATED','channels':list(summaries),'largest_residuals':largest,
                      'gl40':summaries.get('gl40'),'upper_dag':'9/15'},indent=2))

if __name__=='__main__':main()

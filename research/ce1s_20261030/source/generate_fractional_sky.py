"""CE1-S: physical fractional bolometric Bianchi-I sky observables.

Inputs are immutable CE1-R BASS-native Rust CI output, the CE1-P physical
Einstein--Vlasov histories, and CE1-Q source-locked observer sky map. The
model is the SAME original exact-binary64 six-cell source, with no spectral
or fluid closure. The script does not silently recompute or change dynamics.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,math,zipfile
from pathlib import Path
import numpy as np

RUST_ARTIFACT_SHA256='21fe3b9b91b9de4e23f80fb5cba4df4b56b44b3c388bcb6999df9ad838231aa9'
CE1P_ARCHIVE_SHA256='162097533f0bc88ec5ddee8f10edcc08aaf4b81cbf2e4c14c42982dbf73ca6b7'
CE1Q_ARCHIVE_SHA256='cc4d9cba73e4e290d2b44d892b151a429d84d6db157f029dade4c929d9183042'
SOURCE_INPUT_SHA256='022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035'
CHANNELS=('stored_ref8','stored_ref16','gl24','gl40')
MU_EDGES=np.array([0.,.5,1.],dtype=float)
PHI_FRAC_EDGES=np.array([0.,.25,.75,1.],dtype=float)
CELL_ENERGY=np.array([[.1,.25,.05],[.2,.15,.15]],dtype=float)
FOUR_PI=4*math.pi

def read_archive(path, expected):
    path=Path(path)
    digest=hashlib.sha256(path.read_bytes()).hexdigest()
    if digest!=expected:raise ValueError(f'source archive SHA mismatch {path}: {digest}')
    z=zipfile.ZipFile(path)
    if z.testzip() is not None:raise ValueError(f'CRC defect {path}')
    return z

def records(z,name):
    return [{k: (float(v) if k != 'channel' else v) for k,v in r.items()} for r in csv.DictReader(io.StringIO(z.read(name).decode('utf-8')))]

def moments(row,l):
    a=np.array([complex(row[f'a_{l}_{m}_re'],row[f'a_{l}_{m}_im']) for m in range(-l,l+1)])
    ad=np.array([complex(row[f'da_{l}_{m}_re'],row[f'da_{l}_{m}_im']) for m in range(-l,l+1)])
    c=float(np.vdot(a,a).real/(2*l+1))
    cd=float(2*np.vdot(a,ad).real/(2*l+1))
    return c,cd

def fractional_power(row,l):
    E,Ed=row['E'],row['Eprime']
    if E<=0 or not np.isfinite([E,Ed]).all():raise ValueError('invalid kinetic radiation energy')
    c,cd=moments(row,l)
    scale=(FOUR_PI/E)**2
    return {'C':c,'Cprime':cd,'Cdelta':scale*c,'Cdelta_prime':scale*(cd-2*(Ed/E)*c)}

def make_observer_map(theta,phi,ell):
    """Exact pointwise continuum source-map pushforward, pixelized only for display."""
    theta=np.asarray(theta);phi=np.asarray(phi); ell=np.asarray(ell)
    sx=np.sin(theta)[:,None]*np.cos(phi)[None,:]
    sy=np.sin(theta)[:,None]*np.sin(phi)[None,:]
    sz=np.cos(theta)[:,None]*np.ones((1,len(phi)))
    a=np.exp(ell)
    qr=np.sqrt((a[0]*sx)**2+(a[1]*sy)**2+(a[2]*sz)**2)
    qx=np.abs(a[0]*sx/qr);qy=np.abs(a[1]*sy/qr);qz=np.abs(a[2]*sz/qr)
    muf=qz
    phif=np.arctan2(qy,qx)*2/math.pi
    im=np.clip(np.searchsorted(MU_EDGES,muf,side='right')-1,0,1)
    ip=np.clip(np.searchsorted(PHI_FRAC_EDGES,phif,side='right')-1,0,2)
    dmu=np.diff(MU_EDGES)[im]
    dphi=np.diff(PHI_FRAC_EDGES)[ip]
    U0=CELL_ENERGY[im,ip]/(FOUR_PI*dmu*dphi)
    # r=1/|M^{-1}s| and Uobs(s)=r^4 U0(qhat), no blackbody assumption.
    return U0/qr**4

def compute(rust_z,ce1p_z,ce1q_z,outdir):
    out=Path(outdir);out.mkdir(parents=True,exist_ok=True)
    data=[];results={'schema':'bass.ce1s.fractional_bolometric_angular_atlas.v1',
        'model':'original exact-binary64 six-cell positive massless collisionless diagonal Bianchi I',
        'source_sha256':SOURCE_INPUT_SHA256,
        'sources':{'ce1r_pr261_ci_sha256':RUST_ARTIFACT_SHA256,
                   'ce1p_pr258_archive_sha256':CE1P_ARCHIVE_SHA256,
                   'ce1q_pr259_archive_sha256':CE1Q_ARCHIVE_SHA256},
        'time_definition':'u=t/Tstar', 'normal_observer':True, 'ell_max':4,
        'channels':{},'pass_criteria':{'fivepoint_Cdelta_prime_abs':2e-8,
                                       'simpson_Cdelta_closure_abs':5e-10,
                                       'rust_Eprime_continuity_abs':5e-12,
                                       'gl24_gl40_fractional_angular_power_abs':2e-10},
        'upper_dag':'9/15','production_ready':False,'merge_ready':False,
        'blackbody_assumed':False,'polarization_assumed':False}
    for ch in CHANNELS:
        rs=records(rust_z,ch+'.csv')
        if len(rs)!=41:raise AssertionError(f'expected 41 physical epochs {ch}')
        t=np.array([r['u'] for r in rs]);dt=t[1]-t[0]
        if abs(t[0])>1e-14 or abs(t[-1]-.08)>1e-14 or np.max(np.abs(np.diff(t)-dt))>1e-13:raise AssertionError('frozen proper-time grid mismatch')
        local=[]
        for i,r in enumerate(rs):
            d={'channel':ch,'u':r['u'],'E':r['E'],'Eprime':r['Eprime'],'P1':r['P1'],'P2':r['P2'],'P3':r['P3'],
               'continuity_gap':r['continuity_gap']}
            if r['continuity_gap']>5e-12:raise AssertionError('kinetic continuity failed')
            for l in (2,4):
                v=fractional_power(r,l)
                for k,val in v.items():d[f'{k}{l}']=val
            local.append(d);data.append(d)
        vals={}; numerrors={}
        for l in (2,4):
            cs=np.array([x[f'Cdelta{l}'] for x in local]); cps=np.array([x[f'Cdelta_prime{l}'] for x in local])
            fd=(-cs[4:]+8*cs[3:-1]-8*cs[1:-3]+cs[:-4])/(12*dt)
            gap=float(np.max(np.abs(fd-cps[2:-2])))
            integ=dt/3*(cps[0]+cps[-1]+4*cps[1:-1:2].sum()+2*cps[2:-1:2].sum())
            simgap=float(abs(integ-(cs[-1]-cs[0])))
            if gap>2e-8 or simgap>5e-10:raise AssertionError(f'Liouville physical shape closure failed {ch} l={l}: {gap=} {simgap=}')
            vals[str(l)]={'first':float(cs[0]),'final':float(cs[-1]),'delta':float(cs[-1]-cs[0]),
                          'relative_change':float(cs[-1]/cs[0]-1),'final_derivative':float(cps[-1])}
            numerrors[str(l)]={'fivepoint_time_derivative_max_abs':gap,'simpson_integral_closure_abs':simgap}
        results['channels'][ch]={'rays':json.loads(rust_z.read(ch+'.json'))['rays'],
                                 'rows':len(rs),'fractional_power':vals,'checks':numerrors,
                                 'max_rust_continuity_gap':max(x['continuity_gap'] for x in local)}
    bychan={ch:[x for x in data if x['channel']==ch] for ch in CHANNELS}
    gl24,gl40=bychan['gl24'],bychan['gl40']
    continuum_diff={str(l):max(abs(a[f'Cdelta{l}']-b[f'Cdelta{l}']) for a,b in zip(gl24,gl40)) for l in (2,4)}
    if any(x>2e-10 for x in continuum_diff.values()):raise AssertionError('GL24/GL40 discrepancy too high')
    results['gl24_gl40_max_Cdelta_difference']=continuum_diff
    # Physical continuum sky snapshots on unchanged CE1-Q display grid.
    parent_hist=records(ce1p_z,'data/continuum_GL40_history.csv')
    if len(parent_hist)!=41:raise AssertionError('parent continuum history count mismatch')
    parent_npz=np.load(io.BytesIO(ce1q_z.read('ce1q/data/gl40_observer_sky_map.npz')))
    theta=parent_npz['theta'];phi=parent_npz['azimuth']
    if theta.shape!=(160,) or phi.shape!=(320,):raise AssertionError('frozen sky pixel grid mismatch')
    snapshots={}
    for k in (0,20,40):
        rr=parent_hist[k];ell=[rr['ell1'],rr['ell2'],rr['ell3']]
        U=make_observer_map(theta,phi,ell)
        E=gl40[k]['E']
        delta=FOUR_PI*U/E-1
        snapshots[f'u_{k:02d}_U']=U
        snapshots[f'u_{k:02d}_delta']=delta
    snapshot_error=float(np.max(np.abs(snapshots['u_40_U']-parent_npz['energy_per_solid_angle'])))
    # This is a pointwise map identity; the pixelized sky itself is NOT an integration certificate.
    if snapshot_error>2e-12:raise AssertionError(f'archived CE1-Q map not reproduced: {snapshot_error}')
    results['sky_snapshot']={'times':[0.,.04,.08],'grid':[160,320],
        'ce1q_archived_endpoint_map_max_abs_gap':snapshot_error,
        'use':'pointwise display; NOT a continuum quadrature oracle'}
    (out/'fractional_angular_power_164rows.csv').write_text('')
    with (out/'fractional_angular_power_164rows.csv').open('w',newline='') as fh:
        writer=csv.DictWriter(fh,fieldnames=list(data[0].keys()));writer.writeheader();writer.writerows(data)
    np.savez_compressed(out/'fractional_sky_maps_3epochs.npz',theta=theta,azimuth=phi,**snapshots)
    (out/'RESULTS.json').write_text(json.dumps(results,indent=2,sort_keys=True)+'\n')
    return results

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--rust-ci',required=True);p.add_argument('--ce1p-zip',required=True);p.add_argument('--ce1q-zip',required=True);p.add_argument('--out',required=True)
    args=p.parse_args()
    with read_archive(args.rust_ci,RUST_ARTIFACT_SHA256) as rz, read_archive(args.ce1p_zip,CE1P_ARCHIVE_SHA256) as pz, read_archive(args.ce1q_zip,CE1Q_ARCHIVE_SHA256) as qz:
        r=compute(rz,pz,qz,args.out)
    print('CE1S_FROZEN_RUST_SOURCE_FRACTIONAL_SKY_PASS')
    print(json.dumps({'gl40':r['channels']['gl40'],'gl24_gl40_max_Cdelta_difference':r['gl24_gl40_max_Cdelta_difference'],'snapshot':r['sky_snapshot']},indent=2))
if __name__=='__main__':main()

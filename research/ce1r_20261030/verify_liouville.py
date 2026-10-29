"""CE1-R Rust vs independent SciPy Y_lm and analytic collisionless moment ODE.

--synthetic: source matches original six *cell weights*, geometry and
collisionless identities, but local rays are a synthetic midpoint quadrature,
NOT the frozen binary64 source identity. --frozen: load PR259's actual source.
"""
from __future__ import annotations
import argparse,csv,io,math,os,struct,subprocess,json
from pathlib import Path
import numpy as np
from scipy.special import sph_harm_y
ROOT=Path(__file__).resolve().parents[2]
RUST=Path(os.environ.get('BASS_CE1R_RUST',ROOT/'research/ce1r_20261030/sky_time_derivative'))

def bits(v):return str(struct.unpack('<Q',struct.pack('<d',float(v)))[0])
def msg(rays,weights,records,lmax=4):
    lines=[f'{len(weights)} {len(records)} {lmax}']
    for w,n in zip(weights,rays): lines.append(' '.join([bits(w),*(bits(x) for x in n)]))
    for rec in records:
        lines.append(' '.join(bits(rec[k]) for k in ('u','ell1','ell2','ell3','h1','h2','h3')))
    return '\n'.join(lines)+'\n'

def run_rust(rays,weights,records,lmax=4):
    r=subprocess.run([str(RUST)],input=msg(rays,weights,records,lmax),text=True,capture_output=True,timeout=120)
    if r.returncode:raise RuntimeError(f'Rust exit={r.returncode}: {r.stderr[:250]}')
    return [{k:float(v) for k,v in row.items()} for row in csv.DictReader(io.StringIO(r.stdout))]

def alm(r,l,m,der=False):
    prefix='da' if der else 'a'
    return complex(r[f'{prefix}_{l}_{m}_re'],r[f'{prefix}_{l}_{m}_im'])

def independent_scipy(rays,weights,ell,lmax=4):
    m=np.exp(-np.array(ell,dtype=np.float64));q=np.asarray(rays)*m
    rr=np.linalg.norm(q,axis=1);s=-q/rr[:,None]
    w=np.asarray(weights)*np.prod(m)*rr/8.
    vv=[]
    for sx in (-1.,1.):
        for sy in (-1.,1.):
            for sz in (-1.,1.):vv.append(s*np.array([sx,sy,sz]))
    s=np.concatenate(vv,axis=0)
    w=np.tile(w,8)
    theta=np.arccos(np.clip(s[:,2],-1,1))
    phi=np.mod(np.arctan2(s[:,1],s[:,0]),2*np.pi)
    out={(l,mm):complex(np.dot(w,np.conjugate(sph_harm_y(l,mm,theta,phi))))
         for l in range(lmax+1) for mm in range(-l,l+1)}
    energy=float(w.sum())
    p=np.einsum('n,ni->i',w,s*s)
    return out,energy,p

def synthetic():
    mu=[0.,.5,1.];frac=[0.,.25,.75,1.];en=[[.1,.25,.05],[.2,.15,.15]]
    nn=[];ww=[];ref=8
    for i in range(2):
        for j in range(3):
            for ii in range(ref):
                for jj in range(ref):
                    u=mu[i]+(ii+.5)*(mu[i+1]-mu[i])/ref
                    phi=(frac[j]+(jj+.5)*(frac[j+1]-frac[j])/ref)*np.pi/2
                    nn.append([np.sqrt(1-u*u)*np.cos(phi),np.sqrt(1-u*u)*np.sin(phi),u]);ww.append(en[i][j]/(ref*ref))
    return np.array(nn),np.array(ww)

def test_cases(rays,weights,records,reference_rows=None):
    rust=run_rust(rays,weights,records)
    assert len(rust)==len(records)
    errors={'amp_scipy':0.,'derivative_scipy_central':0.,'time_series_5pt':0.,
            'Eprime_continuity':0.,'Pprime_moment':0.,'quadrupole_dot':0.,
            'massless_trace':0.,'parity':0.,'historical_amplitude':0.,
            'max_derivative_abs':0.,'max_C2prime_abs':0.,'max_C4prime_abs':0.,'C2prime_fivepoint_gap':0.,'C4prime_fivepoint_gap':0.}
    for k,(r,rec) in enumerate(zip(rust,records)):
        ell=np.array([rec['ell1'],rec['ell2'],rec['ell3']]);h=np.array([rec['h1'],rec['h2'],rec['h3']]);theta=h.sum()
        if k in {0,len(records)//2,len(records)-1}:
            av,e,p=independent_scipy(rays,weights,ell)
            errors['amp_scipy']=max(errors['amp_scipy'],max(abs(alm(r,l,m)-z) for (l,m),z in av.items()))
            assert abs(r['E']-e)<1e-12 and max(abs(np.array([r['P1'],r['P2'],r['P3']])-p))<1e-12
        er=r['E'];ed=r['Eprime'];pr=np.array([r[f'P{i}'] for i in range(1,4)]);pd=np.array([r[f'P{i}prime'] for i in range(1,4)])
        eerr=abs(ed+theta*er+np.dot(h,pr))
        errors['Eprime_continuity']=max(errors['Eprime_continuity'],eerr)
        assert eerr<3e-12
        errors['massless_trace']=max(errors['massless_trace'],abs(er-pr.sum()))
        assert abs(er-pr.sum())<3e-12
        ref_quad20=np.sqrt(5/(16*np.pi))*(3*pd[2]-ed)
        ref_quad22=np.sqrt(15/(32*np.pi))*(pd[0]-pd[1])
        diff=max(abs(alm(r,2,0,True)-ref_quad20),abs(alm(r,2,2,True)-ref_quad22))
        errors['quadrupole_dot']=max(errors['quadrupole_dot'],diff)
        assert diff<3e-12
        # Independent 4th moment of current source: dP_i = -(theta+2h_i) P_i + sum_j h_j R_ij.
        mm=np.exp(-ell);xyz=np.asarray(rays)*mm;norm=np.linalg.norm(xyz,axis=1)
        diag=(xyz/norm[:,None])**2
        w=weights*np.prod(mm)*norm
        R=np.einsum('n,ni,nj->ij',w,diag,diag)
        prdot=-(theta+2*h)*pr+R@h
        err=float(np.max(np.abs(prdot-pd)))
        errors['Pprime_moment']=max(errors['Pprime_moment'],err)
        assert err<3e-12
        errors['max_derivative_abs']=max(errors['max_derivative_abs'],max(abs(alm(r,l,m,True)) for l in range(5) for m in range(-l,l+1)))
        for l in (2,4):
            Cp=sum(abs(alm(r,l,m))**2 for m in range(-l,l+1))/(2*l+1)
            Cpd=2*sum((alm(r,l,m).conjugate()*alm(r,l,m,True)).real for m in range(-l,l+1))/(2*l+1)
            errors[f'max_C{l}prime_abs']=max(errors[f'max_C{l}prime_abs'],abs(Cpd))
        errors['parity']=max(errors['parity'],max(abs(alm(r,l,m))+abs(alm(r,l,m,True)) for l in range(5) for m in range(-l,l+1) if l%2 or m%2))
        if reference_rows:
            rr=reference_rows[k]
            errors['historical_amplitude']=max(errors['historical_amplitude'],max(abs(alm(r,l,m)-alm(rr,l,m)) for l in range(5) for m in range(-l,l+1)))
    if reference_rows:
        dt=float(records[1]['u']-records[0]['u'])
        assert max(abs((records[i+1]['u']-records[i]['u'])-dt) for i in range(len(records)-1))<1e-12
        for k in range(2,len(records)-2):
            for l in (2,4):
                def spec(row):
                    return sum(abs(alm(row,l,m))**2 for m in range(-l,l+1))/(2*l+1)
                fdC=(-spec(reference_rows[k+2])+8*spec(reference_rows[k+1])-8*spec(reference_rows[k-1])+spec(reference_rows[k-2]))/(12*dt)
                dC=2*sum((alm(rust[k],l,m).conjugate()*alm(rust[k],l,m,True)).real for m in range(-l,l+1))/(2*l+1)
                errors[f'C{l}prime_fivepoint_gap']=max(errors[f'C{l}prime_fivepoint_gap'],abs(fdC-dC))
            for l in range(5):
                for m in range(-l,l+1):
                    deriv=(-alm(reference_rows[k+2],l,m)+8*alm(reference_rows[k+1],l,m)-8*alm(reference_rows[k-1],l,m)+alm(reference_rows[k-2],l,m))/(12*dt)
                    errors['time_series_5pt']=max(errors['time_series_5pt'],abs(deriv-alm(rust[k],l,m,True)))
    # Separate numerical directional derivative of SciPy spherical harmonics, no Rust differentiation.
    for k in {0,len(records)//2,len(records)-1}:
        rec=records[k];ell=np.array([rec['ell1'],rec['ell2'],rec['ell3']]);h=np.array([rec['h1'],rec['h2'],rec['h3']]);delta=3e-5
        plus,_,_=independent_scipy(rays,weights,ell+delta*h)
        minus,_,_=independent_scipy(rays,weights,ell-delta*h)
        fd={p:(plus[p]-minus[p])/(2*delta) for p in plus}
        errs=max(abs(alm(rust[k],l,m,True)-v) for (l,m),v in fd.items())
        errors['derivative_scipy_central']=max(errors['derivative_scipy_central'],errs)
        assert errs<2e-8,(k,errs)
    assert errors['amp_scipy']<2e-12
    assert errors['Pprime_moment']<3e-12
    assert errors['quadrupole_dot']<3e-12
    if reference_rows:
        assert errors['historical_amplitude']<2e-12
        assert errors['time_series_5pt']<5e-7,errors
        assert errors['C2prime_fivepoint_gap']<5e-7 and errors['C4prime_fivepoint_gap']<5e-7
    assert errors['parity']<2e-12,errors
    return errors,rust

def main():
    p=argparse.ArgumentParser();p.add_argument('--synthetic',action='store_true');p.add_argument('--channel',choices=('stored_ref8','gl24','gl40','stored_ref16'),default='stored_ref8');p.add_argument('--out',default='');p.add_argument('--csv-out',default='');args=p.parse_args()
    if args.synthetic:
        rays,weights=synthetic();data=[{'u':0.02,'ell1':.012,'ell2':.011,'ell3':.008,'h1':.74,'h2':.43,'h3':.50}]
        reference=None
    else:
        import research.ce1q_20261030.produce_sky as parent
        channel=args.channel
        if channel.startswith('stored_ref'):
            cls=parent.source()
            ref=int(channel.split('ref')[1])
            rad=cls([0,.5,1],[0,.25,.75,1],[[.1,.25,.05],[.2,.15,.15]],refinement=ref,backend='python_oracle')
            rays,weights=rad.n,rad.mass
            if ref==8:
                assert parent.sha(np.asarray(rays,dtype='<f8').tobytes())==parent.EXPECTED_REF8_N
                assert parent.sha(np.asarray(weights,dtype='<f8').tobytes())==parent.EXPECTED_REF8_M
            fname=channel+'_history.csv'
        else:
            order=int(channel.replace('gl',''))
            rad=parent.gl_source(order)
            rays,weights=rad.n,rad.mass
            fname=f'continuum_GL{order}_history.csv'
        data=parent.history_rows(fname)
        with (ROOT/f'research/ce1q_20261030/data/{channel}_alm.csv').open() as f:
            reference=[{k:float(v) for k,v in row.items()} for row in csv.DictReader(f)]
    errs,rows=test_cases(rays,weights,data,reference)
    final_Cdot={f'C{l}prime':2*sum((alm(rows[-1],l,m).conjugate()*alm(rows[-1],l,m,True)).real for m in range(-l,l+1))/(2*l+1) for l in (2,4)}
    result={'schema':'bass.ce1r.liouville_derivative.v1','mode':'synthetic_noncanonical' if args.synthetic else args.channel,
            'states':len(data),'rays':len(weights),'errors':errs,'last_Cprime':final_Cdot,
            'last':{k:rows[-1][k] for k in ('u','E','Eprime','P1prime','P2prime','P3prime','da_2_0_re','da_2_2_re','da_4_0_re','da_4_2_re','da_4_4_re')},
            'upper_dag':'9/15','production_ready':False,'rigorous_interval_sky':False}
    print(json.dumps(result,indent=2))
    print('BASS_CE1R_RUST_LIOUVILLE_SCIENTIFIC_CHECK_PASS')
    if args.out: Path(args.out).write_text(json.dumps(result,indent=2)+'\n')
    if args.csv_out:
        with Path(args.csv_out).open('w',newline='') as handle:
            w=csv.DictWriter(handle,fieldnames=list(rows[0].keys()));w.writeheader();w.writerows(rows)
    return result
if __name__=='__main__':main()

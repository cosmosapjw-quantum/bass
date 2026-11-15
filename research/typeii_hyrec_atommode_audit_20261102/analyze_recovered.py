#!/usr/bin/env python3
"""Native-mode and timestep comparison plus fixed-source photon observables.
FULL is a reference within the inherited isotropic closure, not exact Bianchi physics.
"""
import ast,csv,json,math,hashlib,subprocess
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
from scipy.interpolate import PchipInterpolator,CubicHermiteSpline
from numpy.polynomial.legendre import leggauss
from native_modes import HERE,ROOT,P0,P1,check,sha,tag

def main():
    raw=json.loads((HERE/'NATIVE_RUNS.json').read_text());runs=raw['runs']
    check(len(runs)==18,'campaign not yet finished')
    good=[r for r in runs if r['exit']==0];hist={}
    for r in good:
        path=HERE/r['data'];check(sha(path)==r['sha256'],'native output identity')
        hist[tag(r['mode'],r['refinement'])+'_'+r['background']]=np.loadtxt(path)
    z=next(iter(hist.values()))[:,0];win=(z>=300)&(z<=1700)
    def stats(a,b):
        x=hist[a][:,1];y=hist[b][:,1];delta=x-y;rel=abs(delta/y)
        idx=np.where(win)[0];i=idx[np.argmax(abs(delta[win]))];j=idx[np.argmax(rel[win])]
        return {'a':a,'reference':b,'max_abs_xe':float(max(abs(delta[win]))),'z_abs':float(z[i]),'max_rel_xe':float(max(rel[win])),'z_rel':float(z[j]),'xe1100_a':float(x[6900]),'xe1100_reference':float(y[6900])}
    pairs=[]
    for bg in ('FLRW','TypeII'):
        for a,b in [('SWIFT_r1','FULL_r1'),('SWIFT_matched','FULL_r1'),('SWIFT_r1','FULL_r4'),('SWIFT_matched','FULL_r4'),('EMLA2s2p_r1','FULL_r4'),('SWIFT_r1','SWIFT_r2'),('SWIFT_r2','SWIFT_matched'),('FULL_r1','FULL_r2'),('FULL_r2','FULL_r4'),('EMLA2s2p_r1','EMLA2s2p_r2')]:
            ak,bk=a+'_'+bg,b+'_'+bg
            if ak in hist and bk in hist:pairs.append(stats(ak,bk))
    pairs.append(stats('FULL_r4_TypeII','FULL_r4_FLRW'))
    rf=P0/'EXTENDED_TYPEII_HYREC2_RAY_26.csv'
    path=str(rf.relative_to(ROOT));blob=subprocess.check_output(['git','rev-parse','9f10e1145c8582f71f7d81dcebfd3c125c70c04c:'+path],cwd=ROOT,text=True).strip()
    check(subprocess.check_output(['git','hash-object',str(rf)],text=True).strip()==blob,'immutable parent rays changed')
    rays=np.genfromtxt(rf,delimiter=',',names=True).reshape(26,1167)
    t=rays['tau_H'][0];zz=rays['z_mean_not_observed'][0]
    check(np.all(np.diff(t)>0) and max(abs(zz-(1701*np.exp(-t)-1)))<4e-11,'ray/time contract')
    check(np.max(abs(rays['tau_H']-t[None,:]))<1e-14,'ray ordering')
    src=ROOT/'compiler/validation/generate_typeii_fixture.py'
    fn=[n for n in ast.parse(src.read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='typeii_rhs']
    check(len(fn)==1,'source rhs identity');env={'math':math};exec(compile(ast.Module(body=fn,type_ignores=[]),str(src),'exec'),env);rhs=env['typeii_rhs']
    fx=json.loads((ROOT/'compiler/validation/typeii_fixture_canonical.json').read_text())['trajectory']['samples'];x0=np.array(fx[0]['state'])
    bg=solve_ivp(lambda s,x:rhs(list(x),1.3),(0.,float(t[-1])),x0,method='DOP853',rtol=2e-12,atol=1e-13,max_step=.004,dense_output=True)
    check(bg.success,'source background integration');state=bg.sol(t).T;sp,sm,s13,N1,v=state.T
    Omega=1-sp**2-sm**2-s13**2-N1**2/12
    C=-np.sqrt(3)*N1*s13-3*1.3*Omega*v/(1+.3*v*v)
    check(max(abs(C))<5e-12 and min(Omega)>0 and max(abs(v))<1,'TypeII physical chart')
    nx,ny,nz=rays['n_x'],rays['n_y'],rays['n_z']
    snn=-2*sp*nx*nx+(sp+np.sqrt(3)*sm)*ny*ny+(sp-np.sqrt(3)*sm)*nz*nz+2*np.sqrt(3)*s13*nx*nz
    dny=(snn-(sp+np.sqrt(3)*sm))*ny-N1*nx*nz
    NY=CubicHermiteSpline(t,ny,dny,axis=1)
    h_anchor=json.loads((P1/'R3_TYPEII_HUBBLE_GRID.json').read_text())['H_anchor_source_FLRW_s_inverse']
    Hray=rays['H_s_inv'][0];Hlog=PchipInterpolator(t,np.log(Hray*h_anchor/Hray[0]))
    G0=1/np.sqrt(1-x0[4]**2);nh0=11.223846333047e-6*.0224*(1-.245)
    N0=nh0*1701**3*G0
    ip=int(np.argmin(np.max(abs(np.column_stack((nx[:,0],ny[:,0],nz[:,0]))-[0,1,0]),axis=1)))
    im=int(np.argmin(np.max(abs(np.column_stack((nx[:,0],ny[:,0],nz[:,0]))-[0,-1,0]),axis=1)))
    def quadrature(order):
        a,w=leggauss(order);dt=np.diff(t);qt=(t[:-1,None]+.5*dt[:,None]*(a+1)).ravel();qw=(.5*dt[:,None]*w).ravel()
        zq=1701*np.exp(-qt)-1;vq=bg.sol(qt)[4];gq=1/np.sqrt(1-vq*vq)
        W=6.6524587e-25*29979245800.*N0*np.exp(-3*qt)/np.exp(Hlog(qt))
        Q=1-vq[None,:]*NY(qt)
        return qt,qw,zq,vq,gq,W,Q
    depths={};qgap={};oddgap={}
    q8=quadrature(8);q16=quadrature(16)
    for name,a in hist.items():
        if not name.endswith('TypeII'):continue
        xe=PchipInterpolator(np.log1p(a[::-1,0]),a[::-1,1],extrapolate=False)
        values=[]
        for qt,qw,zq,vq,gq,W,Q in (q8,q16):
            x=xe(np.log1p(zq));check(np.isfinite(x).all() and min(x)>0,'xe interpolation domain')
            values.append(np.sum(Q*(qw*W*x)[None,:],axis=1))
        d=values[1];qgap[name]=float(max(abs(values[0]-d)))
        qt,qw,zq,vq,gq,W,Q=q16;x=xe(np.log1p(zq));even=float(np.sum(qw*W*x));odd=float(np.sum(qw*W*x*vq))
        oddgap[name]=float(max(abs(d[ip]-(even-odd)),abs(d[im]-(even+odd))))
        depths[name]={'plus':float(d[ip]),'minus':float(d[im]),'asymmetry':float((d[im]-d[ip])/(d[im]+d[ip])),'all_rays':d.tolist()}
    old=json.loads((P1/'R5_SOURCE_ATOMIC_TYPEII_PHOTON_RESULTS.json').read_text())['four_actual_native_atomic_history_lanes']['TypeII_H_and_proper_nH']
    parity=max(abs(depths['SWIFT_r1_TypeII']['plus']-old['plus']),abs(depths['SWIFT_r1_TypeII']['minus']-old['minus']))
    check(parity<2e-8,'parent opacity parity')
    check(max(qgap.values())<5e-8 and max(oddgap.values())<1e-10,'opacity quadrature or symmetry')
    # Independent finite Simpson quadrature from source nodes for the preferred reference.
    from scipy.integrate import simpson
    pref='FULL_r4_TypeII';a=hist[pref];curve=PchipInterpolator(np.log1p(a[::-1,0]),a[::-1,1])
    Wnode=6.6524587e-25*29979245800.*N0*np.exp(-3*t)/np.exp(Hlog(t));qnode=1-v[None,:]*ny
    sim=simpson(qnode*(Wnode*curve(np.log1p(zz)))[None,:],x=t,axis=1)
    simgap=float(max(abs(sim-np.array(depths[pref]['all_rays']))));check(simgap<3e-7,'independent Simpson mismatch')
    # Deliberately wrong source transformations must give finite discrepancies.
    qt,qw,zq,vq,gq,W,Q=q16;x=curve(np.log1p(zq));weight=qw*W*x
    base=np.sum(Q*weight[None,:],axis=1)
    wrong_q=np.sum(Q*Q*weight[None,:],axis=1)-base
    wrong_gamma=np.sum(Q*(weight/gq)[None,:],axis=1)-base
    wrong_current=np.sum(Q*(weight*gq/G0)[None,:],axis=1)-base
    check(wrong_q[ip]<-.5 and wrong_q[im]>.5 and max(abs(wrong_gamma))>.02,'hostile counterexample not detected')
    # Covariant check: Gamma H x' = proper-time reaction source, for homogeneous x.
    G=1/np.sqrt(1-v*v);vprime=np.array([rhs(list(s),1.3)[4] for s in state]);logGprime=v*vprime/(1-v*v)
    clock={'max_Gamma_minus_one':float(max(G-1)),'min_Gamma':float(min(G)),'max_Gamma':float(max(G)),
           'range_dlogGamma_dtau':[float(min(logGprime)),float(max(logGprime))],
           'proper_reaction_conversion':'dx/dtau_H = R_proper/(Gamma H_normal)',
           'proper_fluid_expansion':'Theta_e = Gamma H_normal (3+dlogGamma/dtau_H)',
           'status':'DERIVED_NOT_IMPLEMENTED_IN_INHERITED_ATOMIC_CLOSURE',
           'impact':'The same-input mode experiment is valid; it does not establish a covariant tilted electron atom/thermal closure.'}
    out={'runs_attempted':sum(r['exit'] is not None for r in runs),'successful_runs':len(good),'failed_or_unrun':[r for r in runs if r['exit']!=0],
         'comparisons':pairs,'optical_depths':depths,'max_gauss8_16_gap':max(qgap.values()),'max_axial_identity_gap':max(oddgap.values()),
         'independent_Simpson_gap':simgap,'parent_optical_depth_gap':parity,'max_Codazzi':float(max(abs(C))),
         'clock_and_thermal_closure':clock,'hostile_wrong_flux_plus':float(wrong_q[ip]),'hostile_wrong_flux_minus':float(wrong_q[im]),
         'hostile_missing_Gamma_max':float(max(abs(wrong_gamma))),'hostile_wrong_current_max':float(max(abs(wrong_current))),
         'ray_source_Git_blob':blob,'source_byte_exact':raw['original_sources_byte_exact'],
         'claim_scope':'same-input source-conditioned HYREC mode comparison; not precision-cosmology certification'}
    (HERE/'MODE_COMPARISON_RESULTS.json').write_text(json.dumps(out,indent=2)+'\n')
    with (HERE/'MODE_OPACITY.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['mode','ray','tau_to_mean_z300'])
        for name,ds in depths.items():
            for j,tau in enumerate(ds['all_rays']):w.writerow([name,j,format(tau,'.17g')])
    for x in pairs:print('PAIR',json.dumps(x),flush=True)
    print('OPACITY',json.dumps({n:{k:v for k,v in x.items() if k!='all_rays'} for n,x in depths.items()}),flush=True)
    print('CHECKS',json.dumps({k:out[k] for k in ('successful_runs','runs_attempted','max_gauss8_16_gap','independent_Simpson_gap','parent_optical_depth_gap','max_Codazzi','clock_and_thermal_closure')}),flush=True)
if __name__=='__main__':main()

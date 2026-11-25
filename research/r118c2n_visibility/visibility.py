"""Conditional z20->4 visibility and prescribed homogeneous shear response.
Physical input histories are full-resolution, not plotting thins."""
import json,hashlib
from pathlib import Path
import numpy as np
from scipy.integrate import cumulative_trapezoid,solve_ivp
from numpy.polynomial.legendre import leggauss
D=Path(__file__).resolve().parent
I=Path('/home/cosmosapjw/worktrees/rei-htt-thomson-20261124'); H=Path('/home/cosmosapjw/Downloads')
K=I/'research/r118c2k_segment'; M=I/'research/r118c2m_energy_budget'; L=I/'research/r118c2l_tight_continuation'
fhe=.2454/(4*(1-.2454)); c=299792458.;st=6.6524587051e-29; a0=1/21
H20=67.4e3/3.0856775814913673e22*np.sqrt(.315*21**3+9.2e-5*21**4+1-.315-9.2e-5)
C=np.array([[-.9,-.4],[-.15,-.4]])
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def j(p):return json.loads(p.read_text())
sources={}
def read(p,hash_,bass=False):
    assert sha(p)==hash_;sources[str(p)]=hash_
    keys=['eta','time_s','nH_m3','x_HII','x_HeII','x_HeIII','xe'] if bass else ['a','time_s','nH_proper_cm3','x_HII','x_HeII','x_HeIII','ne_proper_cm3']
    x=np.genfromtxt(p,names=True,delimiter='\t' if bass else ',',usecols=keys)
    v=np.stack([x[k] for k in keys],axis=1)
    if bass:
        v[:,0]=np.exp(v[:,0])*a0;v[:,6]*=v[:,2]
    else:v[:,2]*=1e6;v[:,6]*=1e6
    assert np.all(np.isfinite(v)) and np.all(v[:,2]>0) and np.all(v[:,6]>=0)
    assert np.max(abs(v[:,6]/v[:,2]-v[:,3]-fhe*(v[:,4]+2*v[:,5])))<2e-14
    return v
runs={r['case']:r for r in j(K/'RUNS.json')}
old={r['case']:r for r in j(I/'research/r118c2j_error_control/RUNS.json') if r['variant']=='reduced'}
def row(r):return read(Path(r['raw_path'])/'history.csv',r['hashes']['history.csv'])
def chain(*arr):
    a=arr[0]
    for b in arr[1:]:
        assert np.allclose(a[-1],b[0],rtol=3e-14,atol=1e-30)
        a=np.concatenate((a,b[1:]))
    return a
hist={'q16':chain(row(old['long16']),row(runs['resume16']),row(runs['extend16'])),
      'q32':chain(row(old['long32']),row(runs['resume32'])),
      'q64':row(runs['fresh64']),
      'tight32':chain(row(runs['fresh32tight']),row(j(L/'ACCEPTANCE.json')),row(j(M/'CONTINUATION.json')),row(j(M/'EXTENSION.json')),row(j(M/'FINAL_HISTORY.json')))}
hist['q128']=row(j(I/'research/r118c2n_spectral/Q128.json'))
q256=j(I/'research/r118c2n_spectral/Q256.json');assert q256['status']=='PASS_SCOPED_COMPLETE'
hist['q256']=chain(*(row(r) for r in q256['segments']))
bass=j(D.parent/'r118c2m_energy_budget/RESULTS.json')
for r in bass['results']:
    if r['name'] in ('base','time2','cross','time2_strict'):
        hist['bass_'+r['name']]=read(Path(bass['raw'])/r['name']/'history.tsv',r['hashes']['history.tsv'],True)
# independent quadrature of Thomson scattering kernel, not merely eigenvalues
mu,w=leggauss(16);P=(3*mu**2-1)/2
for A,B in [(0.02,0.),(0.,0.03),(-.04,.02)]:
    m=np.dot(w,(A*P+B*(1-mu**2))*(1-mu**2))/4
    assert abs(m-(-A+4*B)/15)<1e-16
    gain=np.array([-1.5*m,2.25*m])
    assert np.max(abs(gain-np.array([A,B])-C@np.array([A,B])))<1e-16
def response(t,a,k,scale=1.):
    future=cumulative_trapezoid((k*scale)[::-1],-t[::-1],initial=0)[::-1]
    ex=np.exp(-future);sl=np.exp(-.3*future)
    s=H20*(a0/a)**3
    v=-4*np.array([np.trapezoid(s*(6*ex+sl)/7,t),np.trapezoid(s*(3/14)*(ex-sl),t)])
    return v,future
def integrate(a,grid=None,eqtau=None):
    scale_a,t,nh,x,y,z,ne=a.T;t=t-t[0]
    assert np.all(np.diff(t)>0) and np.all(np.diff(scale_a)>0) and abs(scale_a[0]-a0)<2e-15 and abs(scale_a[-1]-.2)<2e-15
    k=st*c*ne; tau=np.trapezoid(k,t); factor=1 if eqtau is None else eqtau/tau
    v,fut=response(t,scale_a,k,factor);tot=float(fut[0]);mass=-np.expm1(-tot)
    # exact interval mass from the represented integrated opacity; stable for small segments
    dm=np.exp(-fut[1:])*(-np.expm1(-(fut[:-1]-fut[1:])))
    assert abs(dm.sum()-mass)<5e-13*mass
    zbar=1/scale_a-1
    zm=.5*(zbar[1:]+zbar[:-1]);tm=.5*(t[1:]+t[:-1]);p=dm/mass
    mean=float(p@zm);std=float(np.sqrt(p@((zm-mean)**2)))
    cdf=np.r_[0.,np.cumsum(p)];quant=np.interp([.1,.5,.9],cdf,zbar)
    tau_comp=[float(np.trapezoid(c*st*nh*u,t)) for u in (x,fhe*(y+z),fhe*z)]
    assert abs(sum(tau_comp)-tau)<2e-14
    return dict(tau=float(tau),visibility_mass=float(mass),mean_z=mean,std_z=std,z_quantiles_time_order=quant.tolist(),mean_t_Myr=float(p@tm/31557600e6),tau_components=tau_comp,heiii_fraction=tau_comp[2]/tau,unscattered_A_per_s20=float(-4*np.trapezoid(H20*(a0/scale_a)**3,t)),A_per_s20=float(v[0]),B_per_s20=float(v[1])),zbar,cdf
def ode_compare(a):
    aa,t,nh,x,y,z,ne=a.T;t=t-t[0];T=t[-1];u=t/T;k=c*st*ne
    # use common uniform loga grid and independently solve in t/T
    zz=np.linspace(0,1,12001);ki=np.interp(zz,u,k);ai=np.interp(zz,u,aa)
    tt=zz*T
    v,_=response(tt,ai,ki)
    def rhs(x,y):
        ka=np.interp(x,zz,ki);av=np.interp(x,zz,ai)
        return T*(ka*(C@y)+np.array([-4*H20*(a0/av)**3,0.]))
    sol=solve_ivp(rhs,(0,1),[0.,0.],rtol=3e-10,atol=1e-12,max_step=.001,method='DOP853')
    assert sol.success
    gap=np.max(abs(sol.y[:,-1]-v))
    assert gap<2e-5,(gap,v,sol.y[:,-1])
    return dict(quadrature=v.tolist(),ode=sol.y[:,-1].tolist(),max_abs=float(gap))
out={};cdfs={};eq={};qref=integrate(hist['q32'])[0]['tau'];zz=np.linspace(4,20,16001)
for name,a in hist.items():
    r,z,g=integrate(a); out[name]=r;cdfs[name]=np.interp(zz,z[::-1],g[::-1]);eq[name]=integrate(a,eqtau=qref)[0]
    # CDF W1 in redshift and equal-tau shape comparison
    print(name,{k:r[k] for k in ('tau','mean_z','std_z','heiii_fraction','A_per_s20','B_per_s20')},flush=True)
ref=cdfs['q32'];comparison={name:dict(W1_z=float(np.trapezoid(abs(g-ref),zz)),CDF_sup=float(np.max(abs(g-ref))),
     B_relative_to_q32=float(out[name]['B_per_s20']/out['q32']['B_per_s20']-1),
     equal_tau_B_relative_to_q32=float(eq[name]['B_per_s20']/eq['q32']['B_per_s20']-1)) for name,g in cdfs.items()}
checks={name:ode_compare(hist[name]) for name in ('q64','bass_cross')}
# A zero-opacity limit must not create polarization; analytic constant test.
t=np.linspace(0,1e14,1001);aa=np.full_like(t,a0);v,_=response(t,aa,np.zeros_like(t));assert v[1]==0 and abs(v[0]+4*H20*t[-1])<1e-15
np.savez_compressed(D/'VISIBILITY_CURVES.npz',z=zz,**cdfs)
result=dict(status='PASS_SCOPED_HOMOGENEOUS_LINEAR_RESPONSE',scope='z20->4 conditional screen, prescribed FLRW volume + weak LRS I test shear, no feedback/no primordial modes; not observed C_ell',sources=sources,H20_s=H20,results=out,equal_tau_results=eq,comparison=comparison,independent_ode_checks=checks)
(D/'RESULTS.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
print('comparisons',json.dumps(comparison),flush=True);print('checks',checks,flush=True)

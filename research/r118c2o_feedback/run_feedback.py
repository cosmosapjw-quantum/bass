"""Conditional z20->4 visibility and prescribed homogeneous shear response.
Physical input histories are full-resolution, not plotting thins."""
import json,hashlib
from pathlib import Path
import numpy as np
from scipy.integrate import cumulative_trapezoid,solve_ivp
from numpy.polynomial.legendre import leggauss
D=Path(__file__).resolve().parent.parent/'r118c2n_visibility'
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

from feedback import coefficients,mat,lyapunov,loss,integrate as solve,midpoint,OG0,ON0,OM,OR,OL,A0,C,SIG
OUT=Path(__file__).resolve().parent
prior=j(D/'RESULTS.json')
results={};series={}
for name,arr in hist.items():
    a=arr[:,0];u=np.log(a/A0);u[0]=0.;u[-1]=np.log(21/5)
    Hval=coefficients(a)[0];k=C*SIG*arr[:,6]/Hval
    # Use original accepted knots (not thin) for interpolant. Solve in eta.
    modes={}
    for mode in ('tracer','photon','all'):
        r=solve(u,k,mode);series[name+'_'+mode]=r.pop('series');modes[mode]=r
    tracer=modes['tracer']['end'];p=prior['results'][name]
    assert abs(tracer[1]-p['A_per_s20'])<3e-6 and abs(tracer[2]-p['B_per_s20'])<5e-8,(name,tracer,p)
    v=np.asarray(modes['all']['end']);c0=np.asarray(tracer)
    results[name]=dict(modes=modes,feedback_rel=(v[:3]/c0[:3]-1).tolist())
    print(name,'tracer',tracer[:3],'all',v.tolist(),'relative',results[name]['feedback_rel'],'Lbalance',modes['all']['lyapunov_relative_balance'],flush=True)
checks={}
for name in ('q256','bass_cross'):
    arr=hist[name];a=arr[:,0];u=np.log(a/A0);u[0]=0.;u[-1]=np.log(21/5);k=C*SIG*arr[:,6]/coefficients(a)[0]
    ref=np.array(results[name]['modes']['all']['end'])
    errors=[];vs=[]
    for n in (512,1024,2048,4096):
        v=midpoint(u,k,'all',n);vs.append(v.tolist());errors.append(float(np.max(abs(v-ref))))
    orders=np.log2(np.array(errors[:-1])/np.array(errors[1:]))
    # fine scale can be interpolation limited; require actual reduction and fine absolute control
    assert errors[-1]<2e-6 and errors[-1]<errors[0]
    checks[name]=dict(steps=[512,1024,2048,4096],errors=errors,orders=orders.tolist(),values=vs)
    print('independent midpoint',name,checks[name],flush=True)
# freeze opacity to zero but retain physical radiation densities; verify no Q source.
u=np.linspace(0,np.log(21/5),4097);r=solve(u,np.zeros_like(u),'all');assert r['end'][2]==0.
np.savez_compressed(OUT/'SERIES.npz',**series)
out=dict(status='PASS_SCOPED_LINEAR_FEEDBACK',scope='z20->4; prescribed FLRW monopole; linear homogeneous shear, radiation feedback; massless neutrino diagnostic',Omega_gamma0=OG0,Omega_nu0=ON0,source_hashes=sources,results=results,midpoint=checks,zero_opacity_end=r['end'])
(OUT/'RESULTS.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')

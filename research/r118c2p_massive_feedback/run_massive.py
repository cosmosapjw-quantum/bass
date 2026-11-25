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


from massive import Background,Species,solve,exact_stress,OG0,ON0,TNU_EV
OUT=Path(__file__).resolve().parent
prior=j(D.parent/'r118c2o_feedback/RESULTS.json')
masses=[0.,.001,.01,.05,.1,.3]
results={};series={};checks={}
for name in ('q256','bass_cross'):
    arr=hist[name];a=arr[:,0];u=np.log(a/(1/21));u[0]=0.;u[-1]=np.log(21/5);ne=arr[:,6]
    out=[]
    for m in masses:
        bg=Background(m,128);r={}
        for mode in ('tracer','photon','all'):
            v=solve(bg,u,ne,mode);series[f'{name}_{m}_{mode}']=v.pop('series');r[mode]=v
        if m==0:
            q=prior['results'][name]['modes']['all']['end']
            assert np.max(abs(np.array(r['all']['end'][:3])-q[:3]))<2e-8
            assert abs(-4*r['all']['end'][3]-q[3])<2e-8
        arr0=np.array(r['photon']['end'][:3]);arr1=np.array(r['all']['end'][:3])
        chi_ratio=[bg.s.moments(aa)[2]/(8*ON0/15) for aa in (1/21,.2)]
        row=dict(m_ev=m,cold_omega0=bg.om,chi_rel_massless=chi_ratio,modes=r,neutrino_feedback_relative=(arr1/arr0-1).tolist())
        out.append(row);print(name,m,'end',r['all']['end'],'nu effect',row['neutrino_feedback_relative'],'chi',chi_ratio,'balance',r['all']['balance'],flush=True)
    results[name]=out
    for m in (0.,.05,.3):
        bg=Background(m,256);v=solve(bg,u,ne,'all',rtol=3e-11,method='Radau');v.pop('series')
        ref=np.array(next(x for x in out if x['m_ev']==m)['modes']['all']['end'])
        gap=float(np.max(abs(np.array(v['end'])-ref)));assert gap<2e-8
        checks[f'{name}_{m}']=dict(max_abs=gap,reference=v)
# Direct nonlinear orthonormal momentum integral vs linear kernel
angular=[]
for m in masses:
    bg=Background(m,256)
    for a in (1/21,.1,.2):
        chi=bg.s.moments(a)[2]
        for h in (1e-3,1e-4,1e-5):
            d=(exact_stress(bg.s,a,h)-exact_stress(bg.s,a,-h))/(2*h)
            err=float(abs(d/(-chi)-1));assert err<3*h*h+3e-10
            angular.append(dict(m=m,a=a,h=h,relative=err))
np.savez_compressed(OUT/'SERIES.npz',**series)
out=dict(status='PASS_SCOPED_MASSIVE_FEEDBACK',scope='linear homogeneous LRS I, isotropic decoupled species at z20, fixed actual ne(a), self-consistent isotropic background rebalanced cold matter, not new ionization history',Omega_gamma0=OG0,Omega_nu_rel0=ON0,Tnu0_eV=TNU_EV,source_hashes=sources,results=results,independent=checks,angular_checks=angular)
(OUT/'RESULTS.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')

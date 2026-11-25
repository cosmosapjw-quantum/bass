"""Budgeted BASS/REI matched campaign; retains failures and tests actual per-step ledger."""
from pathlib import Path
import json,math,hashlib,subprocess,time
from concurrent.futures import ThreadPoolExecutor
import numpy as np
P=Path(__file__).parent; root=Path((P/'TRIAL_PATH.txt').read_text().strip());exe=root/'rei_live_budget'
def sha(f):
    with open(f,'rb') as g:return hashlib.file_digest(g,'sha256').hexdigest()
assert sha(exe)==(P/'BINARY.sha256').read_text().split()[0]
old=json.loads((P.parent/'r118c2l_factor_control/TIGHT_RESULTS.json').read_text())
orig=json.loads((P.parent/'r118c2k_rate_control/ACCEPTANCE.json').read_text())
base=orig['finest'];original=Path(base['command'][0]);assert sha(original)==orig['binary_sha256']
pars=[(13.60,.4298,5.475e4,32.88,2.963,0.,0.,0.),(24.59,13.61,949.2,1.469,3.188,2.039,.4434,2.136),(54.42,1.720,1.369e4,32.88,2.963,0.,0.,0.)]
bind=np.array([13.598434599702,24.587389011,54.41776])
def kv(p):return dict(l.split('=',1) for l in p.read_text().splitlines())
def run(case):
    name,z,n,q,sub,tol,B=case;out=root/name
    args=[str(exe),str(out),str(z),str(n),str(q),str(sub),'8','0.00021014665671400957','9.304371943681256','0.04',str(tol),str(B)]
    # First campaign produced final run.txt for completed simulations, but
    # a Python postprocessing typo aborted collection; reuse exact outputs.
    if out.exists():
        assert (out/'run.txt').is_file(),f'incomplete prior output {out}'
        row=dict(name=name,z=z,n=n,q=q,sub=sub,tol=tol,budget_ev=B,returncode=None,stderr=None,command=args,execution_evidence='recovered complete raw output; initial subprocess exit not persisted')
    else:
        t=time.monotonic();p=subprocess.run(args,capture_output=True,text=True,timeout=150)
        row=dict(name=name,z=z,n=n,q=q,sub=sub,tol=tol,budget_ev=B,returncode=p.returncode,stderr=p.stderr,wall_s=time.monotonic()-t,command=args,execution_evidence='fresh subprocess')
        if p.returncode:row['status']='REJECTED';print(name,'REJECT',p.stderr,flush=True);return row
    h=np.genfromtxt(out/'history.tsv',names=True,delimiter='\t')
    u=np.genfromtxt(out/'uv_exchange.tsv',names=True,delimiter='\t')
    cb=np.genfromtxt(out/'chemistry_budget.tsv',names=True,delimiter='\t')
    pk=np.genfromtxt(out/'packets.tsv',names=True,delimiter='\t')
    assert len(h)==len(u)==len(cb)==n+1 and np.all(np.isfinite(h.view(float))) and np.all(np.isfinite(cb.view(float)))
    assert np.all(np.diff(h['time_s'])>0) and np.all(h['Tm_K']>0)
    assert np.all((h['x_HII']>=0)&(h['x_HII']<=1)&(h['x_HeII']>=0)&(h['x_HeIII']>=0)&(h['x_HeII']+h['x_HeIII']<=1))
    E,N=pk['energy_eV'],pk['N_per_H'];assert min(E)>=13.6 and min(N)>=0 and abs(h['eta'][-1]-math.log(21/(1+z)))<2e-15
    assert abs(N.sum()-h['N'][-1])<2e-12*max(N.sum(),1e-30) and abs(N@E-h['U_eV'][-1])<2e-12*max(N@E,1e-30)
    ng=float(np.max(abs(h['number_defect'])/np.maximum(h['emitted_N'],1.)))
    eg=float(np.max(abs(h['energy_defect'])/np.maximum(h['emitted_U'],1.)))
    ue=float(np.max(abs(u['current_U']+u['absorbed_U']+u['boundary_U']+u['geometry_U']-u['emitted_U'])/np.maximum(u['emitted_U'],1e-30)))
    up=float(np.max(abs(u['current_pz']+u['absorbed_pz']+u['boundary_pz']+u['geometry_pz']-u['emitted_pz'])/np.maximum(u['emitted_U'],1e-30)))
    assert max(ng,eg)<1e-8 and max(ue,up)<1e-9
    assert np.array_equal(cb['eta'],h['eta']) and np.all(cb['local_limit_ev'][1:]>0)
    assert np.max(abs(cb['local_defect_ev'][1:])/cb['local_limit_ev'][1:])<=1.
    want=B*np.diff(cb['eta'])/(cb['eta'][-1]-cb['eta'][0])
    assert np.allclose(want,cb['local_limit_ev'][1:],rtol=4e-15,atol=0.)
    for k,v in [('signed_ev',cb['local_defect_ev']),('absolute_ev',abs(cb['local_defect_ev'])),('budget_used_ev',cb['local_limit_ev'])]:
        assert np.allclose(np.cumsum(v,dtype=np.longdouble),cb[k],rtol=1e-10,atol=1e-21)
    assert abs(cb['budget_used_ev'][-1]/B-1)<1e-10 and cb['absolute_ev'][-1]<=B*(1+1e-10)
    rate=kv(out/'rate_control.txt');assert float(rate['max_group_relative'])<=tol/2 and float(rate['max_final_relative'])<=tol
    tau=float(np.trapezoid(299792458.*6.6524587051e-29*h['nH_m3']*h['xe']/h['H_s'],h['eta']));assert abs(tau/h['tau'][-1]-1)<2e-8
    sig=[]
    for eth,e0,s0,ya,p_,yw,y0,y1 in pars:
        x=E/e0-y0;y=np.sqrt(x*x+y1*y1);sig.append(np.where(E>=eth,s0*((x-1)**2+yw*yw)*y**(p_/2-5.5)*(1+np.sqrt(y/ya))**(-p_)*1e-18,0.))
    s=np.asarray(sig);fac=2.99792458e10*h['nH_m3'][-1]*1e-6;g=fac*(s@N);heat=fac*((s*(E[None,:]-bind[:,None]))@N)
    runinfo=kv(out/'run.txt');assert int(runinfo['steps'])==n;row['solver_wall_s']=float(runinfo['wall_s']);row['status']='PASS_SCOPED'
    row.update(tau=tau,terminal={k:float(h[k][-1]) for k in ('x_HII','x_HeII','x_HeIII','Tm_K','N','U_eV','xe')},gamma=g.tolist(),heat=heat.tolist(),
        ng=ng,eg=eg,uv_gap=ue,uv_momentum_gap=up,root_max=float(np.max(h['root_residual'])),rhs=int(runinfo['rhs']),
        max_local_ratio=float(np.max(cb['max_ratio'])),sum_abs_ev=float(cb['absolute_ev'][-1]),sum_signed_ev=float(cb['signed_ev'][-1]),used_ev=float(cb['budget_used_ev'][-1]),max_global_minus_chem=float(np.max(abs(h['energy_defect']-cb['signed_ev']))),hashes={f.name:sha(f) for f in out.iterdir() if f.is_file()})
    assert row['root_max']<=1e-11
    ref={'base':'base_tight','time2':'time2_tight','cross':'cross_tight'}.get(name)
    if ref:
        t=next(x for x in old['rows'] if x['name']==ref)
        refpath=Path(old['raw'])/ref
        assert sha(refpath/'run.txt')==t['hashes']['run.txt']
        row['tight_rhs']=int(kv(refpath/'run.txt')['rhs'])
        row['delta_tight']={k:row['terminal'][k]-t['terminal'][k] for k in row['terminal']}
        row['gamma_relative_tight']=(np.array(row['gamma'])/t['gamma']-1).tolist()
    print(name,{k:v for k,v in row.items() if k not in ('hashes','command','stderr')},flush=True);return row
cases=[('base',4.,32768,0.,16,1e-4,5e-9),('time2',4.,65536,0.,16,1e-4,5e-9),('cross',4.,65536,0.,32,1e-5,5e-9),('lrs_plus',19.98,256,.01,8,1e-4,5e-9),('lrs_minus',19.98,256,-.01,8,1e-4,5e-9),('time2_strict',4.,65536,0.,16,1e-4,1e-9)]
with ThreadPoolExecutor(max_workers=3) as pool:rows=list(pool.map(run,cases))
(P/'RESULTS.json').write_text(json.dumps(dict(scope='opt-in actual energy defect budget; original BASS physical gates retained',binary_sha256=sha(exe),raw=str(root),results=rows),indent=2,allow_nan=False)+'\n')

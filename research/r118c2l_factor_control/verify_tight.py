import hashlib,json,math
from pathlib import Path
import numpy as np
D=Path(__file__).parent; raw=Path((D/'DIAG_PATH.txt').read_text().strip()); old=json.loads((D/'RESULTS.json').read_text())
def sha(p):
    with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
assert sha(raw/'rei_live_tight')==(D/'tight_binary.sha256').read_text().split()[0]
assert sha(Path(json.loads(Path('research/r118c2k_rate_control/ACCEPTANCE.json').read_text())['finest']['command'][0]))==old['binary_sha256']
pars=[(13.60,.4298,5.475e4,32.88,2.963,0.,0.,0.),(24.59,13.61,949.2,1.469,3.188,2.039,.4434,2.136),(54.42,1.720,1.369e4,32.88,2.963,0.,0.,0.)];bind=np.array([13.598434599702,24.587389011,54.41776]); rows=[];hist={}
for name,n,sub,tol in [('base_tight',32768,16,1e-4),('time2_tight',65536,16,1e-4),('cross_tight',65536,32,1e-5)]:
    assert int((D/(name+'.exit')).read_text())==0
    p=raw/name;h=np.genfromtxt(p/'history.tsv',names=True,delimiter='\t');pk=np.genfromtxt(p/'packets.tsv',names=True,delimiter='\t');uv=np.genfromtxt(p/'uv_exchange.tsv',names=True,delimiter='\t');rate=dict(l.split('=',1) for l in (p/'rate_control.txt').read_text().splitlines())
    assert len(h)==len(uv)==n+1 and np.all(np.isfinite(h.view(float))) and np.all(np.diff(h['time_s'])>0) and np.all(h['Tm_K']>0)
    assert np.all((h['x_HII']>=0)&(h['x_HII']<=1)&(h['x_HeII']>=0)&(h['x_HeIII']>=0)&(h['x_HeII']+h['x_HeIII']<=1))
    E,N=pk['energy_eV'],pk['N_per_H'];assert E.min()>=13.6 and N.min()>=0 and abs(h['eta'][-1]-math.log(21/5))<2e-15
    assert abs(N.sum()-h['N'][-1])<2e-12*max(N.sum(),1e-30) and abs(N@E-h['U_eV'][-1])<2e-12*max(N@E,1e-30)
    ng=float(np.max(abs(h['number_defect'])/np.maximum(h['emitted_N'],1.)));eg=float(np.max(abs(h['energy_defect'])/np.maximum(h['emitted_U'],1.)));ue=float(np.max(abs(uv['current_U']+uv['absorbed_U']+uv['boundary_U']+uv['geometry_U']-uv['emitted_U'])/np.maximum(uv['emitted_U'],1e-30)))
    assert max(ng,eg)<1e-8 and ue<1e-9 and float(rate['max_group_relative'])<=tol/2 and float(rate['max_final_relative'])<=tol
    tau=float(np.trapezoid(299792458.*6.6524587051e-29*h['nH_m3']*h['xe']/h['H_s'],h['eta']));assert abs(tau/h['tau'][-1]-1)<2e-8
    sig=[]
    for eth,e0,s0,ya,p_,yw,y0,y1 in pars:
        x=E/e0-y0;y=np.sqrt(x*x+y1*y1);sig.append(np.where(E>=eth,s0*((x-1)**2+yw*yw)*y**(p_/2-5.5)*(1+np.sqrt(y/ya))**(-p_)*1e-18,0.))
    s=np.array(sig);fac=2.99792458e10*h['nH_m3'][-1]*1e-6;g=fac*(s@N);q=fac*((s*(E[None,:]-bind[:,None]))@N)
    assert np.all(g>0) and np.all(q>0)
    row=dict(name=name,n=n,sub=sub,tol=tol,tau=tau,terminal={k:float(h[k][-1]) for k in ('x_HII','x_HeII','x_HeIII','Tm_K','N','U_eV','xe')},gamma=g.tolist(),heat=q.tolist(),ng=ng,eg=eg,uv_gap=ue,root_max=float(np.max(h['root_residual'])),guard=rate,peak_packets=int(np.max(h['packets'])),hashes={f.name:sha(f) for f in p.iterdir() if f.is_file()});assert row['root_max']<=1e-13;rows.append(row);hist[name]=h
base=rows[0];bh=hist['base_tight'];zz=np.linspace(0,bh['eta'][-1],20001)
for row in rows:
    h=hist[row['name']];row['delta_vs_tight_base']={k:row['terminal'][k]-base['terminal'][k] for k in base['terminal']};row['gamma_relative_vs_tight_base']=(np.array(row['gamma'])/base['gamma']-1).tolist();row['history_max_abs_vs_tight_base']={k:float(np.max(abs(np.interp(zz,h['eta'],h[k])-np.interp(zz,bh['eta'],bh[k])))) for k in ('x_HII','x_HeII','x_HeIII','Tm_K')}
    row['delta_vs_original_base']={k:row['terminal'][k]-old['baseline']['terminal'][k] for k in base['terminal']}
result=dict(status='PASS_SCOPED_ISOLATED_TOLERANCE_TRIAL',original_binary_sha256=old['binary_sha256'],trial_binary_sha256=sha(raw/'rei_live_tight'),source_change='only packet-stage norm threshold 1e-11 -> 1e-13; diagnostic BASS patch; original source and gates untouched',original_baseline_energy_gate=old['baseline']['eg'],rows=rows,production_admission='HOLD',global_convergence='UNRESOLVED',raw=str(raw));(D/'TIGHT_RESULTS.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({**result,'rows':[{k:v for k,v in x.items() if k not in ('hashes','guard')} for x in rows]},indent=2))

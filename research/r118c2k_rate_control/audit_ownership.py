"""Actual UV ledger increments; no fictitious evolved owner stocks."""
import argparse,json,hashlib
from pathlib import Path
import numpy as np
p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
R=a.root;rows=[]
def sha(p):
 with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
for c in json.loads((R/'RESULTS.json').read_text())['cases']:
 q=R/c['case'];u=np.genfromtxt(q/'uv_exchange.tsv',names=True,delimiter='\t');h=np.genfromtxt(q/'history.tsv',names=True,delimiter='\t')
 assert len(u)==len(h)==c['steps']+1
 E={k:np.diff(u[k+'_U']) for k in ('emitted','absorbed','boundary','geometry','current','binding','heat')}
 P={k:np.diff(u[k+'_pz']) for k in ('emitted','absorbed','boundary','geometry','current')}
 roundoff=64*np.finfo(float).eps*np.maximum(u['emitted_U'][1:],1e-30)
 future={}
 for edge in ('emitted','absorbed','boundary'):
  assert np.all(E[edge]>=-roundoff)
  excess=np.maximum(abs(P[edge])-E[edge],0)
  assert np.all(excess<=roundoff)
  future[edge]=float(np.max(excess/np.maximum(u['emitted_U'][1:],1e-30)))
 de=E['current']+E['absorbed']+E['boundary']+E['geometry']-E['emitted']
 dp=P['current']+P['absorbed']+P['boundary']+P['geometry']-P['emitted']
 scale=np.maximum(abs(E['current'])+E['absorbed']+E['boundary']+abs(E['geometry'])+E['emitted'],1e-30)
 assert np.all(abs(de)<1e-8*scale+roundoff)
 assert np.all(abs(dp)<1e-8*scale+roundoff)
 assert np.all(abs(E['binding']+E['heat']-E['absorbed'])<1e-8*scale+roundoff)
 dt=np.diff(h['time_s']);assert np.min(dt)>0
 mid=(h['eta'][1:]+h['eta'][:-1])/2
 nh=h['nH_m3'][0]*np.exp(-3*mid)
 # only midpoint-frozen source/absorption stage mean rates.
 fac=nh*1.602176634e-19/dt
 rows.append(dict(case=c['case'],energy_step_relative=float(np.max(abs(de)/scale)),axial_step_relative=float(np.max(abs(dp)/scale)),future_causal_excess=future,source_power_max_W_m3=float(np.max(fac*E['emitted'])),gas_absorption_power_max_W_m3=float(np.max(fac*E['absorbed'])),emitter_debit_eV_per_H=float(-u['emitted_U'][-1]),gas_credit_eV_per_H=float(u['absorbed_U'][-1]),nonionizing_credit_eV_per_H=float(u['boundary_U'][-1]),geometry_loss_eV_per_H=float(u['geometry_U'][-1]),uv_final_eV_per_H=float(u['current_U'][-1]),input_hash=sha(q/'uv_exchange.tsv')))
a.out.write_text(json.dumps(dict(scope='integrated per-H edge ownership diagnostics; local midpoint emitter/absorption rates; no evolved counterpart reservoirs',cases=rows),indent=2)+'\n')
print('owner diagnostic cases',len(rows),'max step energy residual',max(x['energy_step_relative'] for x in rows))

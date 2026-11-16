#!/usr/bin/env python3
"""Independent unsplit source operator, tighter matched comparisons and boundary tests."""
import json
import numpy as np
from scipy.sparse import diags,block_diag,kron,bmat,csc_matrix
from scipy.integrate import solve_ivp
from redistribution import *
from packet_campaign import evolve

def reference():
 # A smaller but actual source discretization; independent unsplit sparse BDF.
 t0=np.log(1701/1101);duration=1e-4;ge=Geometry(t0,t0+duration,2,4);s=ge.at(t0);g=fixed_grid(s['Tm'],20,40);M=40;K=ge.nang
 u0,d0=frequency_rates(g,s['Tm'],s['nl'],s['pion'],True);rs,kr=medium_rates(g['nu'],s['Tm'],s['nl'],s['pion']);factor=s['D'][:,None]/s['H']
 up=factor*u0;down=factor*d0+s['kappa'][:,None]*g['nu_edges'][:-1]/g['width'];kill=factor*kr
 Q,pi=angular_generator(s['na'],s['we'],s['D'])
 blocks=[diags((up[a,:-1],-(up[a]+down[a]+kill[a]),down[a,1:]),(-1,0,1),shape=(M,M),format='csc') for a in range(K)]
 A=block_diag(blocks,format='csc')+kron(csc_matrix(Q),diags(rs/s['H']),format='csc')
 losses=np.zeros((3,K*M));losses[0,np.arange(K)*M]=down[:,0];losses[1,np.arange(K)*M+M-1]=up[:,-1];losses[2]=kill.ravel()
 B=bmat([[A,csc_matrix((K*M,3))],[csc_matrix(losses),csc_matrix((3,3))]],format='csc')
 N=s['capacity_angle'][:,None]*g['cap'][None,:]*np.exp(-.5*((g['x']-3)/3)**2);N/=N.sum();y0=np.r_[N.ravel(),0.,0.,0.]
 sol=solve_ivp(lambda t,y:B@y,(0,duration),y0,method='BDF',jac=B,rtol=3e-9,atol=1e-12)
 check(sol.success,'independent unsplit BDF failed')
 truth=np.r_[sol.y[:-3,-1].sum(),sol.y[-3:,-1]];mass=float(max(abs(np.sum(sol.y,axis=0)-1)))
 check(mass<5e-7,'independent BDF probability ledger')
 trials=[]
 for steps in (96,192,384):
  r=evolve(cells=40,steps=steps,nmu=2,nphi=4,duration=duration,frozen=True)
  value=np.array([r['survival'],r['red_band_exit'],r['blue_band_exit'],r['tagged_ionized']]);gap=float(max(abs(value-truth)))
  trials.append({'steps':steps,'probabilities':value.tolist(),'max_abs_gap_vs_unsplit_BDF':gap})
 check(trials[-1]['max_abs_gap_vs_unsplit_BDF']<2e-4 and trials[-1]['max_abs_gap_vs_unsplit_BDF']<trials[0]['max_abs_gap_vs_unsplit_BDF'],'split source time refinement fails independent ODE')
 return {'source_discretization':{'angular_nodes':K,'frequency_cells':M,'duration_tauH':duration},'BDF_probabilities':truth.tolist(),'BDF_number_max_defect':mass,'BDF_nfev':sol.nfev,'time_refinements':trials,'scope':'independent unsplit finite-dimensional source model, not exact R_II physics'}

def main():
 ref=reference();print('UNSPLIT_REFERENCE',json.dumps(ref),flush=True)
 extra=[]
 for name,kw in [('fine_evolving',dict(cells=640,steps=768)),('fine_frozen',dict(cells=640,steps=768,frozen=True)),('band80',dict(X=80,cells=1280,steps=768)),('earlier_source',dict(z0=1400,cells=320,steps=384)),('later_source',dict(z0=800,cells=320,steps=384))]:
  r=evolve(**kw,save='PACKET_'+name);r['case']=name;extra.append(r)
  (HERE/'EXTRA_SOURCE_PACKET_RESULTS.json').write_text(json.dumps({'cases':extra,'independent_reference':ref},indent=2)+'\n')
  print('EXTRA',name,json.dumps({k:r[k] for k in ('red_band_exit','blue_band_exit','tagged_ionized','max_count_ledger_defect')}),flush=True)
 base={r['case']:r for r in json.loads((HERE/'SOURCE_PACKET_RESULTS.json').read_text())['cases']};ex={r['case']:r for r in extra}
 fields=['red_band_exit','blue_band_exit','tagged_ionized']
 coarse=np.array([base['frequency_double'][f]-base['frozen'][f] for f in fields]);fine=np.array([ex['fine_evolving'][f]-ex['fine_frozen'][f] for f in fields])
 result={'independent_reference':ref,'matched_time_dependence_coarse':dict(zip(fields,coarse.tolist())),'matched_time_dependence_fine':dict(zip(fields,fine.tolist())),
 'max_change_of_time_dependence_effect_under_joint_refinement':float(max(abs(coarse-fine))),
 'max_absolute_probability_change_under_joint_refinement':max(abs(ex['fine_evolving'][f]-base['frequency_double'][f]) for f in fields),
 'extra_cases':extra,'conclusion':'time-dependent finite-band source model computed; no global escape or exact angular-frequency redistribution claim'}
 (HERE/'TIME_DEPENDENCE_AND_CONVERGENCE.json').write_text(json.dumps(result,indent=2)+'\n');print('TIME_DEPENDENCE',json.dumps({k:v for k,v in result.items() if k not in ('extra_cases','independent_reference')}),flush=True)
if __name__=='__main__':main()

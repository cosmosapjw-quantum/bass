"""Postprocess immutable CE1-U primary result CSV into physical diagnostics."""
import json,csv,argparse
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def records(p):
 with Path(p).open() as f:return [{k:float(v) for k,v in row.items()} for row in csv.DictReader(f)]

def main(root):
 root=Path(root);D=root/'data';I=root.parent/'ce1t_20261030'/'local_GL40_history_authority.csv'
 if not I.exists(): I=root.parent/'ce1q_20261030'/'parent_verified'/'data'/'continuum_GL40_history.csv'
 gl40=records(I)
 result={'schema':'bass.ce1u.physical_science_results.v1','source_kind':'six original binary64 cells, new GL6/GL8 positive rays','original_source_sha256':'022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035','upper_dag':'9/15','results':{},'numerical_reference':'previous GL40 41-epoch Einstein history, not certified continuum'}
 for n in (6,8):
  r=records(D/f'GL{n}_coupled_41epochs.csv')
  b=json.loads((D/f'GL{n}_source_exact_bound.json').read_text())
  s=json.loads((D/f'GL{n}_coupled_summary.json').read_text())
  assert len(r)==len(gl40)==41
  hgap=max(abs(x[f'h{i}']-y[f'h{i}']) for x,y in zip(r,gl40) for i in (1,2,3))
  ellgap=max(abs(x[f'ell{i}']-y[f'ell{i}']) for x,y in zip(r,gl40) for i in (1,2,3))
  dt=.002
  time_err={name:max(abs((-r[j+2][name]+8*r[j+1][name]-8*r[j-1][name]+r[j-2][name])/(12*dt)-r[j][name+'prime']) for j in range(2,39)) for name in ('C2','C4')}
  result['results'][f'GL{n}']={'rays':6*n*n,'states':41,'source_pressure_bound':b['maximum_epsilon_source'],'exact_ode_h_bound':b['final_h_ell_bound'],'meets_h_target':b['meets_target'],'source_ray_sha256':b['stored_gl_hashes']['ray_sha256'],'source_mass_sha256':b['stored_gl_hashes']['mass_sha256'],'max_h_gap_vs_GL40_numerical':hgap,'max_ell_gap_vs_GL40_numerical':ellgap,'max_fd_5pt_gap':time_err,'max_constraint_C':s['maximum_Hamiltonian_C'],'max_four_panel_RK4_h_gap_against_DOP853':s['rk4_endpoint_h_gaps']['4'],'last_u':r[-1]['u'],'E_at_end':r[-1]['E'],'h_at_end':[r[-1][f'h{i}'] for i in (1,2,3)],'pi_at_end':[r[-1][f'P{i}']-r[-1]['E']/3 for i in (1,2,3)],'C2prime_at_end':r[-1]['C2prime'],'C4prime_at_end':r[-1]['C4prime'],'C4_at_end':r[-1]['C4']}
  for obs in ('C4prime','C4','E'):
   if obs=='C4prime':continue
  print(n,'eps=',b['maximum_epsilon_source'],'hbound',b['final_h_ell_bound'],'hGap_GL40',hgap,'C4p',r[-1]['C4prime'])
  t=np.array([x['u'] for x in r]); v=np.array([x['C4prime'] for x in r]); plt.plot(t,v,label=f'GL{n} coupled, {6*n*n} rays')
 plt.xlabel('u=t/T* (dimensionless proper time)');plt.ylabel("dC4^U/du (bolometric energy-sky units²)")
 plt.title('CE1-U: Self-consistent Einstein-Vlasov GL source C4 derivative')
 plt.legend();plt.grid(alpha=.2);plt.tight_layout();plt.savefig(root/'figures'/'CE1U_COUPLED_C4PRIME.png',dpi=170);plt.close()
 (D/'SCIENCE_RESULTS.json').write_text(json.dumps(result,indent=2)+'\n')
 return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',required=True);a=p.parse_args();main(a.root)

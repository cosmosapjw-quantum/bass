"""Compare independently computed reachable late STF with signed native quadrupoles."""
import numpy as np,json
from pathlib import Path
D=Path(__file__).resolve().parent
def harm(v):
 k=np.sqrt(4*np.pi/15);a=k*(v[0]-1j*v[2]);b=k*(-v[3]+1j*v[4])
 return np.array([a.conjugate(),-b.conjugate(),np.sqrt(2)*k*v[1],b,a])/np.sqrt(4*np.pi)
def run():
 T=np.array(json.loads((D/'R7.json').read_text())[-1]['transfer']);rows={}
 for n in [4096,8192]:
  for label in ['late','whole','generic']:
   C=np.loadtxt(D/f'{label}_1.ctrl')[3:].reshape(4,5).T;pred=C@T.T
   a,b=[np.genfromtxt(D/f'{label}_{n}_{s}.csv',names=True,delimiter=',') for s in [1,-1]]
   m=(a['epoch']==0)&(a['ell']==2)
   di=((a['Ire']-b['Ire'])+1j*(a['Iim']-b['Iim']))[m]/2
   dp=((a['Ere']-b['Ere'])+1j*(a['Eim']-b['Eim']))[m]/2
   # E=-sqrt(8/3) times P in C3K convention.
   wi=harm(pred[:,4]);wp=-np.sqrt(8/3)*harm(pred[:,5])
   g=[]
   for s in [1,-1]:
    l=(D/f'{label}_{n}_{s}.geom').read_text().splitlines()
    q=np.genfromtxt(l[:-1],names=True,delimiter=',');g.append(np.array([q[f'S{i}'][1] for i in range(5)]))
   ds=(g[0]-g[1])/2;want=pred[:,0]
   rows[f'{label}_{n}']=dict(I_error=float(np.linalg.norm(di-wi)/np.linalg.norm(wi)),P_error=float(np.linalg.norm(dp-wp)/np.linalg.norm(wp)),S_error=float(np.linalg.norm(ds-want)/np.linalg.norm(want)),I_norm=float(np.linalg.norm(di)),E_norm=float(np.linalg.norm(dp)))
 o=dict(rows=rows,scope='linear vs native signed finite amplitude, early shear and normalized harmonic quadrupoles; no primordial cosmology claim')
 (D/'AUDIT.json').write_text(json.dumps(o,indent=2)+'\n');print(o)
if __name__=='__main__':run()

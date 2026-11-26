"""Independent cubic order audit including rotated complex coefficients and extrapolation."""
import json,numpy as np
from pathlib import Path
D=Path(__file__).resolve().parent
def run():
 rows={};v={}
 for f in sorted(D.glob('ORDERS_*.json')):
  for r in json.loads(f.read_text()):
   key=f"{r['key']}_{r['n']}_{r['eps']:g}";z=np.array(r['cubic_vector']);v[key]=z[:,0]+1j*z[:,1];rows[key]={k:r[k] for k in ['quadratic','cubic_linear','cubic_geometry','cubic_total','native_odd','native_diff']}
 z=v['whole_4096_0.01'];q=v['rot_4096_0.01']
 rot=float(np.linalg.norm(q-z*np.exp(-1j*np.arange(-3,4)*np.pi/3))/np.linalg.norm(z))
 r={}
 for n in [4096,8192]:
  a=v[f'whole_{n}_0.01'];b=v[f'whole_{n}_0.005'];rr=(4*b-a)/3
  r[str(n)]=dict(coefficient_norm=float(np.linalg.norm(rr)),amplitude_change=float(np.linalg.norm(a-b)/np.linalg.norm(rr)),vector=np.c_[rr.real,rr.imag].tolist())
 a=np.array(r['4096']['vector']);b=np.array(r['8192']['vector'])
 rel=float(np.linalg.norm(a-b)/np.linalg.norm(b));o=dict(rows=rows,rotation_relative=rot,richardson=r,mesh_relative=rel,scope='conditional order reconstruction with finite-amplitude native shear coefficients; not full analytic geometry perturbation theorem')
 assert rot<1e-5 and rel<1e-3
 (D/'AUDIT.json').write_text(json.dumps(o,indent=2)+'\n');print({k:v for k,v in o.items() if k!='rows'})
if __name__=='__main__':run()

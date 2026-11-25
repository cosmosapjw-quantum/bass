"""Independent reverse-order evaluation using REC's unmodified public integrators."""
import pathlib,sys,json,numpy as np,time
rec=pathlib.Path(sys.argv[1]);out=pathlib.Path(sys.argv[2]);sys.path.insert(0,str(rec/'src'))
from full_bianchi_hyrec.recoil import pair_cell_conductance as P,exterior_interface as E
z=np.load(rec/'data/full_scalar_com_khw_v050.npz',allow_pickle=False)
fac=8*np.pi*P.dnu/P.c**3;interval=z['state_intervals'];ref=z['pair_moments_m3_sInv'];rows=[]
for i,j in ((7,10),(0,16),(8,29),(8,34)):
 t=time.monotonic()
 if j<17:
  a=fac*P.integrate_unordered_pair(i,j,ell_max=24,amplitude_lane='full')
  b=fac*P.integrate_unordered_pair(j,i,ell_max=24,amplitude_lane='full')
 else:
  a=E.exterior_pair_conductance(tuple(interval[j]),tuple(interval[i]),ell_max=24,amplitude_lane='full')
  b=E.exterior_pair_conductance(tuple(interval[i]),tuple(interval[j]),ell_max=24,amplitude_lane='full')
 scale=ref[0,i,j]
 r=dict(pair=[i,j],forward_moment_gap=float(np.max(abs(a-ref[:,i,j]))/scale),reverse_moment_gap=float(np.max(abs(b-a))/scale),elapsed_s=time.monotonic()-t)
 rows.append(r);print(r,flush=True)
 assert r['forward_moment_gap']<2e-11 and r['reverse_moment_gap']<2e-5
out.write_text(json.dumps(rows,indent=2,allow_nan=False)+'\n')

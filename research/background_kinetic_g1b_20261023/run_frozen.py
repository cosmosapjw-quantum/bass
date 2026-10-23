"""New G1B fixed-state study. All coarse results are retained, no overwrite."""
from pathlib import Path
import json,time,hashlib,sys,csv
import numpy as np
import mpmath as mp
import smooth as sm
from vendor import kinetic as kn
ROOT=Path(__file__).resolve().parent
CASES=[
 {'name':'FD3_initial','kind':'FD','mass':3.,'alpha':0.,'beta':[0.,0.,0.],'boost':[0.,0.,0.]},
 {'name':'FD3_triaxial','kind':'FD','mass':3.,'alpha':.4,'beta':[.9,-.3,-.6],'boost':[0.,0.,0.]},
 {'name':'FD3_boost','kind':'FD','mass':3.,'alpha':.1,'beta':[-1.,.4,.6],'boost':[.3,-.1,.1]},
 {'name':'FD30_triaxial','kind':'FD','mass':30.,'alpha':.6,'beta':[.7,-.2,-.5],'boost':[0.,0.,0.]},
 {'name':'Planck_triaxial','kind':'Planck','mass':0.,'alpha':.4,'beta':[1.,-.3,-.7],'boost':[0.,0.,0.]},
 {'name':'Planck_boost','kind':'Planck','mass':0.,'alpha':.25,'beta':[-1.2,.5,.7],'boost':[.15,.2,-.1]}]


def main():
 out=ROOT/'evidence/frozen_001';out.mkdir(exist_ok=False)
 start=time.perf_counter();rows=[];cache={}
 def calc(c,r,a):
  key=(c['name'],r,a)
  if key not in cache:
   data=sm.packets(c['kind'],c['mass'],r,a,A=sm.default_anisotropy() if c['kind']=='FD' else None)
   data=sm.deformed(data,c['alpha'],c['beta'],c['boost'])
   T,N=sm.observables(data)
   cache[key]=(T,N,len(data[1]))
  return cache[key]
 for c in CASES:
  T0,N0,_=calc(c,16,56)
  choices=[('radial',r,56) for r in (4,8,12,16)]+[('angular',16,a) for a in (6,10,14,20,28,40,56)]
  for axis,r,a in choices:
   T,N,count=calc(c,r,a)
   rhoerr=abs(T[0,0]-T0[0,0])/T0[0,0]
   ferr=np.linalg.norm(T[0,1:]-T0[0,1:])/T0[0,0]
   perr=np.linalg.norm(T[1:,1:]-T0[1:,1:])/T0[0,0]
   nerr=np.max(np.abs(N-N0))/N0[0]
   rows.append(dict(case=c['name'],axis=axis,radial_order=r,radial_nodes=4*r,nmu=a,nphi=2*a,packets=count,rho_error=rhoerr,flux_error=ferr,pressure_F_error=perr,number_current_error=nerr,max_error=max(rhoerr,ferr,perr,nerr),rho=float(T[0,0]),number=float(N[0])))
 # Independent 1D, high-precision LRS Planck angular oracle, not the production rule.
 mp.mp.dps=55;alpha=mp.mpf('.4');b=mp.mpf('.45')
 f=lambda u:mp.sqrt(mp.exp(-2*b)*(1-u*u)+mp.exp(4*b)*u*u)
 rref=mp.exp(-4*alpha)*mp.quad(f,[-1,0,1])/2
 pzref=mp.exp(-4*alpha+4*b)*mp.quad(lambda u:u*u/f(u),[-1,0,1])/2
 data=sm.deformed(sm.photon_packets('Planck',56),float(alpha),(float(b),float(b),float(-2*b)))
 T,_=sm.observables(data);want=np.diag([float(rref),float((rref-pzref)/2),float((rref-pzref)/2),float(pzref)])
 oracle=float(np.max(np.abs(T-want))/float(rref))
 selected=[x for x in rows if (x['axis']=='radial' and x['radial_order']==12) or (x['axis']=='angular' and x['nmu']==40)]
 maximum=max(x['max_error'] for x in selected)
 tails=[]
 for kind,mass in [('FD',3.),('FD',30.),('Planck',0.)]:
  for Q in (4.,8.,12.,16.,24.,32.,40.,48.):
   tails.append({'kind':kind,'mass':mass,'Q':Q,'initial_energy_bound':sm.energy_tail_bound(kind,mass,Q),'field_envelope_bound':sm.energy_tail_bound(kind,mass,Q,np.exp(2.4),np.exp(5.6))})
 # Preserve actual arrays supporting every table, not just maxima.
 arrays={f'{key[0]}_r{key[1]}_a{key[2]}_T':v[0] for key,v in cache.items()}
 arrays.update({f'{key[0]}_r{key[1]}_a{key[2]}_N':v[1] for key,v in cache.items()})
 np.savez_compressed(out/'moments.npz',**arrays)
 for name,data in [('refinement.csv',rows),('tails.csv',tails)]:
  with (out/name).open('w',newline='') as f:
   wr=csv.DictWriter(f,fieldnames=list(data[0]));wr.writeheader();wr.writerows(data)
 result={'status':'PASS_SCOPED' if maximum<2e-8 and oracle<5e-12 else 'FAIL','cases':CASES,'unique_moment_evaluations':len(cache),'table_rows':len(rows),'selected_radial_order':12,'selected_angular_order':40,'reference':{'radial_order':16,'nmu':56},'selected_max_error':maximum,'independent_LRS_Planck_MP55_error':oracle,'lrs_oracle':{'rho':str(rref),'p_z':str(pzref)},'tail_envelope_max_Q48':max(x['field_envelope_bound'] for x in tails if x['Q']==48),'elapsed_s':time.perf_counter()-start,'old_campaign_replays':0,'error_norm':'max(abs(density),2-norm flux,Frobenius pressure)/reference rho, plus max(number current components)/reference number','claim':'finite quadrature refinement; not global or interval-certified convergence'}
 (out/'RESULTS.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result,indent=2))
 return int(result['status']=='FAIL')
if __name__=='__main__':sys.exit(main())

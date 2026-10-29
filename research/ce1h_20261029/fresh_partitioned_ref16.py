"""Fresh ref16 CE1-H source/time run with per-panel process isolation.

MPFR192 residuals are calculated independently in four OS worker processes;
byte identity of source and recorded RK4 path is checked against parent.
This avoids a current-session long-lived MPFR worker stall, not an alteration
of the scientific algorithm or its tolerance.
"""
import json,sys,subprocess,hashlib,time,os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from bianchi.nonperturbative.einstein_tabulated_source import TabulatedRadiation,certified_tabulated_geometry,certified_tabulated_pressure
from bianchi.nonperturbative.einstein_error_budget import rk4_path
from bianchi.nonperturbative.einstein_interval import Interval,_bernstein_box_binary,propagate_interval
from bianchi.nonperturbative.einstein_tabulated_time import _panel_endpoint_jump
from bianchi.nonperturbative.einstein_tabulated_sharp import initial_continuum_pressure_cap,_initial_constraint_mismatch
ROOT=Path(__file__).resolve().parent
start=time.perf_counter()
s=TabulatedRadiation([0,.5,1],[0,.25,.75,1],[[.1,.25,.05],[.2,.15,.15]],refinement=16,backend='python_oracle')
p=rk4_path(s,s.initial_state(),.08,4,backend='python_oracle')
sha=lambda a:hashlib.sha256(a.tobytes()).hexdigest()
path_id=sha(p.states)+':'+sha(p.coefficients)+':'+sha(p.times)
source_id=sha(s.n)+':'+sha(s.mass)
initial=certified_tabulated_geometry(s,end=.08,shear=(.2,-.13,-.07))
box=list(initial['geometry_box_upper'])
for i in range(4):
 lo,hi=_bernstein_box_binary(p,i)
 assert min(lo)>=0
 for k in range(3):box[k]=max(box[k],hi[k])
eta=certified_tabulated_pressure(s,box)['bound_max']
pmax=initial_continuum_pressure_cap(s)['pressure_max_upper']
Emax=initial['energy_max_upper']
assert pmax<=Emax
print('PRECHECK',time.perf_counter()-start,'pmax',pmax,'Emax',Emax,'eta',eta,flush=True)

def work(i):
 env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',PYTHONPATH=os.environ.get('PYTHONPATH',str(ROOT.parent.parent)))
 r=subprocess.run([sys.executable,str(ROOT/'panel_worker.py'),str(i)],capture_output=True,text=True,env=env,timeout=90,check=True)
 return json.loads(r.stdout)
with ThreadPoolExecutor(max_workers=4) as pool:
 panels=list(pool.map(work,range(4)))
assert [x['panel'] for x in panels]==[0,1,2,3]
assert all(x['path_sha256']==path_id and x['source_sha256']==source_id for x in panels)
print('WORKERS',time.perf_counter()-start,[round(x['elapsed_sec'],2) for x in panels],flush=True)

def prop(E):
 init=[Interval(0),Interval(_initial_constraint_mismatch(s,p,(.2,-.13,-.07)))]
 src=[Interval(0),Interval(0)];tim=[Interval(0),Interval(0)]
 for i,w in enumerate(panels):
  dt=Interval(float(p.times[i+1]))-Interval(float(p.times[i]))
  d=w['defect'];je,jh=_panel_endpoint_jump(p,i)
  init=propagate_interval(init,dt,Interval(E),Interval(0),Interval(0))
  src=propagate_interval(src,dt,Interval(E),Interval(0),Interval(eta))
  tim=propagate_interval(tim,dt,Interval(E),Interval(d['ell_defect']),Interval(d['h_defect']))
  tim=[tim[0]+Interval(je),tim[1]+Interval(jh)]
 return {'initial_h':init[1].upper,'source_h':src[1].upper,'time_jump_h':tim[1].upper,
         'total_h':sum((x[1] for x in [init,src,tim]),Interval(0)).upper}
base=prop(Emax);sharp=prop(pmax)
result={'method':'fresh four isolated OS MPFR panel workers, exact byte identities checked',
 'source_sha256':source_id,'path_sha256':path_id,'elapsed_sec':time.perf_counter()-start,
 'panel_times':[x['elapsed_sec'] for x in panels], 'baseline':base,'sharp':sharp,
 'pmax':pmax,'Emax':Emax,'eta':eta,'target_met':sharp['total_h']<1e-5,
 'formal_machine_verified':False,'native_subagents':'NOT_RUN'}
(ROOT/'FRESH_PARTITIONED_REF16.json').write_text(json.dumps(result,indent=2)+'\n')
print('RESULT',json.dumps(result),flush=True)

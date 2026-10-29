"""CE1-I ref16 same-physics current-session replay, no native/production claim."""
import hashlib, json, time
import numpy as np
from bianchi.nonperturbative.einstein_tabulated_source import TabulatedRadiation
from bianchi.nonperturbative.einstein_error_budget import rk4_path
from bianchi.nonperturbative.einstein_tabulated_local import certify_local_tabulated_path

def hashary(a):return hashlib.sha256(np.asarray(a,dtype='<f8').tobytes()).hexdigest()
t0=time.monotonic()
s=TabulatedRadiation([0,.5,1],[0,.25,.75,1],[[.1,.25,.05],[.2,.15,.15]],refinement=16,backend='python_oracle')
p=rk4_path(s,s.initial_state((.2,-.13,-.07)),.08,4,backend='python_oracle')
t1=time.monotonic()
print('PATH_GENERATED',len(s.n),t1-t0,flush=True)
o=certify_local_tabulated_path(s,p,end=.08,subcells=1)
t2=time.monotonic()
assert abs(o['ce1h_total_ell_h_upper'][1]-3.675931156248731e-6)<5e-14
assert o['local_total_ell_h_upper'][1]<o['ce1h_total_ell_h_upper'][1]<o['ce1g_total_ell_h_upper'][1]
assert o['target_met']
d={'schema':'bass.ce1i.ref16.current_run.v1','status':'NUMERICALLY_CHECKED','source_ray_sha256':hashary(s.n),'source_mass_sha256':hashary(s.mass),'rk4_state_sha256':hashary(p.states),'hermite_coeff_sha256':hashary(p.coefficients),'rays':o['rays'],'steps':o['steps'],'u_end':o['u_end'],'L_panel':o['time_local_lipschitz_upper'],'m_panel':o['time_local_min_logscale_lower'],'ce1g_total_h':o['ce1g_total_ell_h_upper'][1],'ce1h_total_h':o['ce1h_total_ell_h_upper'][1],'ce1i_total_h':o['local_total_ell_h_upper'][1],'initial_h':o['initial_ell_h_upper'][1],'source_h':o['source_ell_h_upper'][1],'time_and_jumps_h':o['time_and_jump_ell_h_upper'][1],'gain_fraction':1-o['local_total_ell_h_upper'][1]/o['ce1h_total_ell_h_upper'][1],'target_met':o['target_met'],'source_generation_s':t1-t0,'certificate_s':t2-t1,'elapsed_s':t2-t0,'upper_dag':'9/15','production_ready':False,'formal_mpfr_python_verified':False,'rows':o['rows']}
with open('/mnt/data/bass_ce1i_work/S2_REF16.json','w') as f:json.dump(d,f,indent=2)
print('PASS',json.dumps({k:d[k] for k in ['rays','ce1g_total_h','ce1h_total_h','ce1i_total_h','gain_fraction','elapsed_s','target_met']}),flush=True)

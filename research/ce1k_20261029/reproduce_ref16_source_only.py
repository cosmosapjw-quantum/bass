"""CE1-K fresh MPFR192 ref16 source forcing; SHA-verified inherited residual.

Not a fresh full independent time-residual recomputation. Uses immutable
PR246 fresh OS-partitioned panel proof after checking binary source/path SHAs.
"""
import json, time, hashlib, zipfile, math
from pathlib import Path
from bianchi.nonperturbative.einstein_interval import Interval, _bernstein_box_binary, propagate_interval
from bianchi.nonperturbative.einstein_tabulated_source import TabulatedRadiation,certified_tabulated_pressure,certified_tabulated_energy
from bianchi.nonperturbative.einstein_tabulated_sharp import initial_continuum_pressure_cap
from bianchi.nonperturbative.einstein_tabulated_local import _exact_expansion_initial, _local_pressure_caps
from bianchi.nonperturbative.einstein_tabulated_source_canonical import canonical_shifted_box
from bianchi.nonperturbative.einstein_error_budget import rk4_path

project=Path(__file__).parent
s2=zipfile.ZipFile('/mnt/data/BASS_CE1J_S2_FINAL_20261029_c25092d1.zip')
saved=json.loads(s2.read('research/ce1j_20261029/evidence/S2_REF16_PARTITIONED.json'))
t0=time.perf_counter()
source=TabulatedRadiation([0,.5,1],[0,.25,.75,1],[[.1,.25,.05],[.2,.15,.15]],refinement=16,backend='python_oracle')
path=rk4_path(source,source.initial_state(),.08,4,backend='python_oracle')
sha=lambda a:hashlib.sha256(a.tobytes()).hexdigest()
source_id=sha(source.n)+':'+sha(source.mass)
path_id=sha(path.states)+':'+sha(path.coefficients)+':'+sha(path.times)
assert source_id==saved['source_id'], 'source rays and masses differ from PR246'
assert path_id==saved['path_id'], 'binary RK4/Hermite state/time differs from PR246'
assert path.coefficients.shape==(4,4,6)
from numpy import array_equal
assert array_equal(path.coefficients[:,0,:],path.states[:-1])
print('SHA_MATCH',source_id,path_id,flush=True)
energy=certified_tabulated_energy(source)
assert energy['energy_max_upper']==0.9
Emax=Interval(float(energy['energy_max_upper']))
h0,theta=_exact_expansion_initial(source,(.2,-.13,-.07))
initialh=source.initial_state()[3:]
T=Interval(.08)
box=[(Interval(max(h0[i].upper, float(initialh[i])))*T+Emax*T*T/2).upper for i in range(3)]
for i in range(4):
    lo,hi=_bernstein_box_binary(path,i)
    assert min(lo)>=0
    box=[max(box[k],hi[k]) for k in range(3)]
expected_box=[0.06344366232705748,0.037043662327057476,0.041843662327057475]
assert box==expected_box, (box,expected_box)
pmax=initial_continuum_pressure_cap(source)['pressure_max_upper']
caps=_local_pressure_caps(source,path,(.2,-.13,-.07),pmax)
assert [r['shared_logscale_lower'] for r in caps]==saved['m_panel']
assert all(abs(4*r['pressure_cap_upper']-L)<=2e-15 for r,L in zip(caps,saved['L_panel']))
print('PROVEN_GEOMETRY',box,'LOWERS',[r['shared_logscale_lower'] for r in caps],flush=True)

src=[Interval(0),Interval(0)]
uniform_cert=None
panel_rows=[]
for j,row in enumerate(caps):
    shift=row['shared_logscale_lower']
    bounds=canonical_shifted_box(box,shift)
    cert=certified_tabulated_pressure(source,bounds)
    unscaled=cert['bound_max']
    local=(Interval(float(unscaled))*(-4*Interval(shift)).exp()).upper
    if j==0:
        uniform_cert=unscaled
        assert abs(uniform_cert-3.569278983301304e-05)<1e-17
    eta=min(uniform_cert,local)
    dt=Interval(float(path.times[j+1]))-Interval(float(path.times[j]))
    src=propagate_interval(src,dt,Interval(float(row['pressure_cap_upper'])),Interval(0),Interval(float(eta)))
    panel_rows.append({'j':j,'u_left':float(path.times[j]),'m':shift,'pmax':row['pressure_cap_upper'],'raw_bound':unscaled,'scaled_bound':local,'adopted_eta':eta,'source_h_cumulative':src[1].upper})
    print('PANEL',j,unscaled,local,eta,src[1].upper,flush=True)
initial=saved['local']['initial_h']
time_bound=saved['local']['time_jump_h']
source_bound=src[1].upper
h_total=sum((Interval(float(v)) for v in [initial,time_bound,source_bound]),Interval(0)).upper
out={'schema':'bass.ce1k.current_run.ref16_source_only.v1','scope':'EXACT_STORED_BINARY_SOURCE_CURRENT; INHERITED_SHA_VERIFIED_FULL_PANEL_RESIDUAL','parent_pr':246,'donor_pr':247,'source_id':source_id,'path_id':path_id,'pr246_prior_local_total':saved['local']['total_h'],'pr247_prior_local_total':3.0184081966517434e-6,'ce1k_total_h_upper':h_total,'fresh_source_h_upper':source_bound,'inherited_initial_h_upper':initial,'inherited_time_jump_h_upper':time_bound,'panels':panel_rows,'target':1e-5,'target_met':h_total<1e-5,'elapsed_s':time.perf_counter()-t0,'upper_dag':'9/15','formal_mpfr_python_proof':False,'distinct_author_review':'NOT_RUN','production_ready':False}
(project/'REF16_SOURCE_ONLY.json').write_text(json.dumps(out,indent=2))
print('RESULT',json.dumps({k:out[k] for k in ['ce1k_total_h_upper','fresh_source_h_upper','inherited_time_jump_h_upper','target_met','elapsed_s']}),flush=True)
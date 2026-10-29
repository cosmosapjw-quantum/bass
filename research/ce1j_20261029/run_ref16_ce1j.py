"""Reuse SHA-bound fresh CE1-I MPFR panel defects, recompute CE1-J source caps.
No previous result is silently called a fresh time defect.
"""
import os,json,hashlib,time
from pathlib import Path
from fractions import Fraction
from bianchi.nonperturbative.einstein_tabulated_source import (
 TabulatedRadiation,certified_tabulated_geometry,certified_tabulated_pressure)
from bianchi.nonperturbative.einstein_error_budget import rk4_path
from bianchi.nonperturbative.einstein_interval import Interval,_iv_fraction,propagate_interval,_bernstein_box_binary
from bianchi.nonperturbative.einstein_tabulated_source_local import certify_common_linear_growth
ROOT=Path(__file__).resolve().parent
start=time.perf_counter()
prev=json.loads((ROOT/'FRESH_CE1I_REF16.json').read_text())
s=TabulatedRadiation([0,.5,1],[0,.25,.75,1],[[.1,.25,.05],[.2,.15,.15]],refinement=16,backend='python_oracle')
p=rk4_path(s,s.initial_state(),.08,4,backend='python_oracle')
sha=lambda a:hashlib.sha256(a.tobytes()).hexdigest()
source=':'.join(map(sha,(s.n,s.mass)));path=':'.join(map(sha,(p.states,p.coefficients,p.times)))
assert source==prev['source_sha256'] and path==prev['path_sha256']
assert all((p.coefficients[:,0,:]==p.states[:-1]).flat)
g=certify_common_linear_growth(s,p)
init=certified_tabulated_geometry(s,end=.08,shear=(.2,-.13,-.07));box=list(init['geometry_box_upper'])
for i in range(4):
 lo,hi=_bernstein_box_binary(p,i); assert min(lo)>=0
 for k in range(3):box[k]=max(box[k],hi[k])
eta=certified_tabulated_pressure(s,box)['bound_max']
assert abs(eta-prev['source_upper']) < 1e-18
panels=[]; src=[Interval(0),Interval(0)]
for j in range(4):
 tleft=_iv_fraction(Fraction(float(p.times[j])));shift=(_iv_fraction(Fraction(3,8))*tleft).lower
 shifted=[max(0.,(Interval(float(v))-Interval(shift)).upper) for v in box]
 cap0=certified_tabulated_pressure(s,shifted)['bound_max']
 capscaled=(Interval(float(cap0))*(-4*Interval(shift)).exp()).upper
 cap=min(eta,capscaled)
 L=prev['per_panel_caps'][j]
 dt=Interval(float(p.times[j+1]))-Interval(float(p.times[j]))
 src=propagate_interval(src,dt,Interval(float(L)),Interval(0),Interval(float(cap)))
 panels.append({'j':j,'tleft':float(p.times[j]),'shift_lower':shift,
  'box_upper':shifted,'unscaled_source_cap':cap0,'scaled_source_cap':capscaled,
  'adopted_source_cap':cap,'jacobian_cap':L,'source_error_h_upper':src[1].upper})
 print('PANEL',j,'eta',cap,'elapsed',round(time.perf_counter()-start,3),flush=True)
res={'initial':prev['ce1i']['initial'],'source':[a.upper for a in src], 'time_and_jump':prev['ce1i']['time_and_jump']}
res['total']=[sum((Interval(res[k][i]) for k in ('initial','source','time_and_jump')),Interval(0)).upper for i in range(2)]
assert res['total'][1]<prev['ce1i']['total'][1]<prev['ce1h']['total'][1]
result={'status':'CE1J_PANELWISE_SOURCE_EXACT_REAL_SCOPED_REF16',
 'source_sha256':source,'path_sha256':path,
 'time_residual_origin':'REUSE_SHA_VERIFIED_FROM_PREVIOUS_FRESH_CE1I_REF16',
 'source_certificate':'CURRENT_RUN_FRESH_MPFR192',
 'original_global_source_upper':eta, 'original_geometry_Emax_upper':init['energy_max_upper'],
 'pressure_jacobian_caps':prev['per_panel_caps'],'growth_certificate':g,
 'panels':panels,'ce1g':prev['ce1g']['total'][1],
 'ce1h':prev['ce1h']['total'][1], 'ce1i':prev['ce1i']['total'][1],
 'ce1j_components':res,'gain_over_ce1i_pct':100*(1-res['total'][1]/prev['ce1i']['total'][1]),
 'target_unchanged':1e-5,'target_met':res['total'][1]<1e-5,
 'elapsed_sec':time.perf_counter()-start,
 'formal_program_proof':False,'distinct_author_review':'NOT_RUN'}
fn=ROOT/'CE1J_REF16_REUSE_SHA.json';fn.write_text(json.dumps(result,indent=2)+'\n')
print('RESULT',res['total'][1],'improvement',result['gain_over_ce1i_pct'],'elapsed',result['elapsed_sec'],flush=True)

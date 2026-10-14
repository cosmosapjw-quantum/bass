"""R8 source-bound decision: no radiative-transfer or chemistry solve.

Run: python code/decide.py [--out FILE]
Reads selected immutable R7 summaries, recomputes exact rational decisions,
then independently integrates only the frozen one-dimensional Bianchi-I clock.
"""
from __future__ import annotations
import argparse, csv, hashlib, io, json, math
from fractions import Fraction as Q
from pathlib import Path
from mpmath import mp

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / 'reference'
EXPECTED = {
 'A_CERTIFICATE.json':'cac2515682821deebe7eb30770a27b30dc7576522c3a1f6101ef0e70e2486adc',
 'B_CERTIFICATE.json':'46d588c48b0518648914e7dcc98c04fe3ddca1c861d1bdcb5bfca92a5cc7d874',
 'PEER_COMPATIBILITY.json':'22af9f2b4ec95a4c885fca413c1a3a7a07e5c3db3ed99ef89f70a9c1002bcd2b',
 'ZERO_native_rows.csv':'677795c3dc7af63f8d56008ef0a094d68b14bedb3ff5fd24b905aead5cb760fb',
}
EXPECTED_ARCHIVES = {
 'PR147':'551ca3cd2f8679fcf5bbe4b0885176147c77e232def6c5606622a6364ea987f6',
 'PR146':'5fbdc60f4d614e7c71378b043081469aced34d713cd33108f34b96f26ed99fc1',
 'PR145_parent':'c040514105fa856b05a8792a628e441a2ad73c991cc253b94b7646425d8bb0e8',
}
R6_COEFF = Q(926402349807, 1953125000000000) # multiplies |epsilon|**3

def sha(path:Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()
def rat(pair):return Q(int(pair[0]),int(pair[1]))
def stokes_norm(st):
    i,q,u,v = (float(rat(x)) for x in st)
    return max(abs(i),math.hypot(q,u,v))

def decision():
    for name,digest in EXPECTED.items():
        assert sha(REF/name)==digest, 'immutable record mismatch: '+name
    a=json.loads((REF/'A_CERTIFICATE.json').read_text())
    b=json.loads((REF/'B_CERTIFICATE.json').read_text())
    x=json.loads((REF/'PEER_COMPATIBILITY.json').read_text())
    assert x['pass'] and x['common_parent_sha256']==EXPECTED_ARCHIVES['PR145_parent']
    assert a['state_order']==b['state_order']==['S0','S1','S2','V0','V1','W0']
    assert a['rays']==36 and b['parameters']['quadrature'].startswith('exact GL3')
    assert all(s['all_four_component_intervals_mapped'] and s['entire_peer_component_box_inside_main_trace_ball'] for s in x['state_checks'])
    assert x['component_interval_mappings']==24 and x['block_containments']==6
    d0=rat(x['state_checks'][0]['main_reference_error_from_peer_box'])
    d1=rat(x['state_checks'][3]['main_reference_error_from_peer_box'])
    d2=rat(x['state_checks'][5]['main_reference_error_from_peer_box'])
    emax=Q(1,10)
    d_numeric=d0+emax*d1+emax**2*d2/2
    assert d_numeric==rat(x['main_numeric_polynomial_error_from_peer_box'])
    d_analytic=R6_COEFF*emax**3
    d_total=d_analytic+d_numeric
    assert d_total==rat(x['main_polynomial_total_with_inherited_R6_remainder'])
    assert d_numeric < Q(7361,10**15) and d_total < Q(475,10**9)
    assert a['angular_continuum_error'] is None and b['angular_continuum_error'] is None
    assert a['observer_derivative_numerical_error'] is None
    assert a['empirical_provider_error'] is None and b['empirical_provider_error'] is None
    assert len(a['reference_stokes'])==6
    s0,v0,w0=[a['reference_stokes'][j] for j in (0,3,5)]
    I0,Q0,U0,V0=[rat(x) for x in s0]
    assert I0>Q(4958,10000)
    assert 0<Q0<Q(2287,10000) and 0<U0<Q(658,10000) and -Q(486,10000)<V0<0
    assert Q(2287,10000)**2+Q(658,10000)**2+Q(486,10000)**2 < Q(243,1000)**2
    assert stokes_norm(v0)<0.0091 and stokes_norm(w0)<0.000364
    # Exact rational conservative Weyl lower bound (norm estimates conservative).
    positive_margin=(Q(4958,10000)-Q(243,1000))/2-emax*Q(91,10000)-emax**2*Q(364,10**6)/2-Q(475,10**9)
    assert positive_margin>Q(12548,100000)
    first_slope=rat(v0[0]);assert first_slope<-Q(9,1000)
    # The source-specific xenon/helium count is H+He and charge, NOT Ye==xe.
    he_mass=Q(2454,10000)
    f=he_mass/(4*(1-he_mass))
    xe_floor=Q(1,10**7)*(1+3*f)
    ye_floor=xe_floor/(1+4*f)
    synthetic_ion=[Q(9,10)*Q(1,10**7),Q(4,5)*Q(1,10**7),Q(2,5)*Q(1,10**7)]
    synthetic_xe=synthetic_ion[0]+f*(synthetic_ion[1]+2*synthetic_ion[2])
    assert all(c<Q(1,10**7) for c in synthetic_ion)
    assert Q(1,10**7)<synthetic_xe<xe_floor  # discriminates current xe=1e-7 floor
    with (REF/'ZERO_native_rows.csv').open() as stream:
        rows=list(csv.DictReader(stream))
    assert len(rows)==10 and rows[0]['case_id']=='ZERO' and rows[-1]['zbar']=='4'
    diag=[]
    for milestone,i in [('0.1',2),('0.5',4),('0.9',6)]:
        r,s=rows[i:i+2]
        lo,hi=(float(t['x_HII']) for t in (r,s));t0,t1=(float(t['time_s']) for t in (r,s))
        assert lo<float(milestone)<=hi and t1>t0
        dt=t1-t0;dX=hi-lo
        diag.append({'threshold':milestone,'xHII_bracket':[lo,hi], 'elapsed_time_s_bracket':[t0,t1],
                     'native_chord_slope_per_Myr':dX/dt*31557600*1e6,
                     'nominal_1e-7_fraction_to_years':Q(1,10**7)/Q.from_float(dX/dt)/31557600,
                     'slope_type':'saved_native_chord_only_NOT_CONTINUOUS_DERIVATIVE_BOUND'})
    # Source-frozen geometry only: H0 in SI from Mpc_cm; two independent integral representations.
    mp.dps=55
    a_ref=mp.mpf(1)/21
    h0=mp.mpf('67.4')*mp.mpf(10)**5/mp.mpf('3.085677581491367e24')
    om=mp.mpf('.315');orr=mp.mpf('.000092');ol=1-om-orr
    def hf(aa):return h0*mp.sqrt(orr/aa**4+om/aa**3+ol)
    hs=hf(a_ref)
    def tau(q,aa):
        q=mp.mpf(q)
        return mp.quad(lambda L:1/mp.sqrt(hf(mp.exp(L))**2+(q*hs*(a_ref/mp.exp(L))**3)**2),[mp.log(a_ref),mp.log(aa)])
    geos=[]
    points=[('original_pair',mp.mpf('0.08873654701704167'))]+[(str(d['threshold']),mp.mpf(1)/(1+mp.mpf(str(z)))) for d,z in zip(diag,[10.248068402397193,6.816991167760682,5.8045371895307705])]+[('endpoint_z4',mp.mpf('0.2'))]
    for name,aa in points:
        zero=tau(0,aa)
        de5=tau('0.005',aa)-zero
        de10=tau('0.01',aa)-zero
        assert de10<de5<0 and tau('-0.01',aa)==tau('0.01',aa)
        geos.append({'label':name,'a':mp.nstr(aa,22),'zbar':mp.nstr(1/aa-1,22),'zero_elapsed_Myr':mp.nstr(zero/31557600/1e6,20),
                     'delta_005_years':mp.nstr(de5/31557600,19),'delta_010_years':mp.nstr(de10/31557600,19),
                     'time_coordinate':'gas proper elapsed since zbar20; exact signed-even prescribed model'})
    diff_observed=Q(8701318923319379-8701490096946133)  # exact saved binary64 clock representations; seconds
    diff_pred=float(tau('.01',points[0][1])-tau(0,points[0][1]))
    assert abs(float(diff_observed)-diff_pred)<20
    return {'schema':'bass.fa03.r8.decision.v1','stage':'FA03-R8','decision':'PROMOTE_FOR_FIXED_36RAY_MODEL_ONLY','parent_pr147':'e67d6fc6c1ad8b3a219abf72104877da1f267e6d',
      'parent_pr146':'3e612547a5e54f48aa930a16778b6b656f4671ad','source_identity':EXPECTED,'archive_sha256s':EXPECTED_ARCHIVES,
      'coefficient_error':str(d_numeric),'coefficient_error_display':float(d_numeric), 'analytic_remainder_at_point1':str(d_analytic),
      'total_error':str(d_total),'total_error_display':float(d_total),'outward_total_bound':'4.75e-7',
      'finite_detector':{'chi':'1/125','psi':'1/100','delta':'1/50','rays':36,'band':'[0.98,1.02] exact rational moments','epsilon':'real [-0.1,0.1]'},
      'conservative_stokes_min_eigen_lower':str(positive_margin),'conservative_stokes_min_eigen_lower_display':float(positive_margin),
      'R8_positivity_threshold':'strictly >0.12548 for exact finite-model coherency','intensity_opacity_slope_at_zero':float(first_slope),
      'held_claims':['continuous_angle_cap_quadrature','numeric_observer_derivative','actual_atom_opacity_calibration','finite_epsilon_exact_six_moment_closure','whole_nonzero_shear_REI','AX11_convergence'],
      'xe_over_H_floor':str(xe_floor),'xe_over_H_floor_display':float(xe_floor),'electron_per_baryon_floor':str(ye_floor),'electron_per_baryon_floor_display':float(ye_floor),
      'historical_bad_xe_floor_discriminator':float(synthetic_xe),'owner_reducer_floor_current':{'observed_utc':'2026-10-14T12:48:22.912882+00:00','head':'6fe1e8d03fadbc46bdc6dd0072a55b83cbd03d0d','source_sha256':'35e1499ef9a69180e5df442c198d3b4c28ea1090c9f6829aad1a68eba8c69cc9','formula':'1e-7*(h+3*he)/h','decision':'PREVIOUS_XE_FLOOR_MISMATCH_ALREADY_RESOLVED_BY_OWNER; NO_SUPPLIER_PATCH'},'milestone_chord_diagnostics':[{**{k:v for k,v in d.items() if k!='nominal_1e-7_fraction_to_years'},'nominal_1e-7_fraction_to_years':float(d['nominal_1e-7_fraction_to_years'])} for d in diag],
      'geometry_clock':geos,'frozen_original_pair_seconds':int(diff_observed),'geometry_difference_seconds':diff_pred,
      'background_sha256':'46f818c2f9de890c72f71fa3cc70366b28c42ca0d65190bd905b6310023e7af0',
      'model_scope':'prescribed Bianchi-I clock; no chemistry/atomic re-run, no physical signal accuracy asserted'}

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--out');arg=ap.parse_args()
 obj=decision()
 out=json.dumps(obj,indent=2,ensure_ascii=False)+'\n'
 if arg.out:
  p=Path(arg.out)
  if p.exists():raise RuntimeError('Refuse overwrite: '+str(p))
  p.parent.mkdir(parents=True,exist_ok=True);p.write_text(out)
 else:print(out)

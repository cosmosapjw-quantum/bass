"""Read-only exact comparison of two stored R7 certificates; no ODE/CAS run."""
from pathlib import Path
from fractions import Fraction as F
from math import isqrt
import json, hashlib, sys

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / 'BASS_FA03_R7_REI_MILESTONE_20261014'
PEER = ROOT / 'BASS_FA03_R7_VALIDATED_20261014'

def decode(v):
    return F(int(v[0]), int(v[1]))

def encode(v):
    return [str(v.numerator), str(v.denominator)]

def root_upper(v):
    if v < 0:
        raise ValueError('negative squared norm')
    scale = 10**35
    numer = v.numerator * scale**2
    denom = v.denominator
    k = isqrt(numer // denom)
    if k*k*denom < numer:
        k += 1
    result = F(k, scale)
    assert result**2 >= v
    return result

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    a = json.loads((MAIN / 'evidence/CERTIFICATE.json').read_text())
    b = json.loads((PEER / 'evidence/CERTIFICATE.json').read_text())
    assert a['state_order'] == b['state_order'] == ['S0','S1','S2','V0','V1','W0']
    for key in ['chi', 'psi', 'delta']:
        assert F(a['base_parameters'][key]) == F(b['parameters'][key])
    assert sha(MAIN/'reference/PARENT_R6.zip') == sha(PEER/'reference/PARENT_R6.zip') == 'c040514105fa856b05a8792a628e441a2ad73c991cc253b94b7646425d8bb0e8'
    # The manuscripts additionally bind the same exact GL nodes/weights,
    # source, initial slice, passive opacity, analyzer and Stokes convention.
    records=[]
    radii=[]
    for index,state in enumerate(a['state_order']):
        centre = [decode(x) for x in a['reference_stokes'][index]]
        endpoint_boxes = b['endpoints'][4*index:4*(index+1)]
        entry = [(decode(v['lo']), decode(v['hi'])) for v in endpoint_boxes]
        assert all(lo <= hi for lo,hi in entry)
        p,q,u,v = entry
        # F11,F22,ReF12,ImF12 -> I,Q,U,V, V = -2 Im F12.
        intervals=[(p[0]+q[0],p[1]+q[1]),(p[0]-q[1],p[1]-q[0]),(2*u[0],2*u[1]),(-2*v[1],-2*v[0])]
        for j,(lo,hi) in enumerate(intervals):
            expected=b['stokes'][state][j]
            assert lo == decode(expected['lo']) and hi == decode(expected['hi'])
        components=[max(abs(lo-c),abs(hi-c)) for c,(lo,hi) in zip(centre,intervals)]
        polar_sq=sum(d*d for d in components[1:])
        old=decode(a['six_state_forward_radii'][index])
        contained=components[0] <= old and polar_sq <= old*old
        assert contained
        new=max(components[0],root_upper(polar_sq))
        assert new <= old
        radii.append(new)
        records.append({'state':state,'all_four_component_intervals_mapped':True,'entire_peer_component_box_inside_main_trace_ball':contained,'main_original_radius':encode(old),'main_reference_error_from_peer_box':encode(new),'display':float(new)})
    exact_remainder=F(926402349807,1953125000000000000)
    numeric=radii[0]+radii[3]/10+radii[5]/200
    total=numeric+exact_remainder
    assert total < F(475,10**9)
    out={'kind':'Exact stored-certificate interoperability and conditional inherited bound; no new trajectory or external independent review',
         'common_parent_sha256':sha(MAIN/'reference/PARENT_R6.zip'),
         'main_certificate_sha256':sha(MAIN/'evidence/CERTIFICATE.json'),
         'peer_certificate_sha256':sha(PEER/'evidence/CERTIFICATE.json'),
         'main_reference_npz_sha256':a['reference_sha256'],
         'state_checks':records,'component_interval_mappings':24,'block_containments':6,
         'main_numeric_polynomial_error_from_peer_box':encode(numeric),'main_numeric_polynomial_error_display':float(numeric),
         'main_polynomial_total_with_inherited_R6_remainder':encode(total),'total_display':float(total),
         'short_outward_total_bound':'<4.75e-7 for |epsilon|<=0.1',
         'source_of_stronger_bound':'PR146 interval certificate, plus current exact-rational comparison. Not an independent regeneration of PR146.',
         'angular_continuum_error':None,'empirical_provider_error':None,'observer_derivative_numerical_error':None,
         'main_original_archive_changed':False,'peer_original_archive_changed':False,'R8_executed':False,'pass':True}
    print(json.dumps(out,indent=2))

if __name__ == '__main__':
    main()

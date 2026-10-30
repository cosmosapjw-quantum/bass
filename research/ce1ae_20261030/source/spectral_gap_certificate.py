#!/usr/bin/env python3
"""CE1-AE rational algebra witness: sampled Gram => genuine continuum-time gap.

Uses exact inequalities and stated physical ODE positivity; does not purport to
independently re-prove inherited PR281 41-sample certified lambda3.
"""
from __future__ import annotations
import json
from fractions import Fraction as F
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
SRC='022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035'
PARENT=F(3,10**12)
A=F(1,4000000)
HMAX=F(9,10)
L=F(150)
T=F(2,25)

def main():
    x=json.loads((BASE/'input'/'CE1AD_SAMPLED_SPECTRAL_GATE.json').read_text())
    assert x['schema']=='bass.ce1ad.science.v1'
    for n in ('6','8'):
        d=x['results'][n]
        assert d['original_source_sha256']==SRC
        assert d['rank3_41samples_certified_conditional']
        assert F(d['original_continuum_lambda3_lower'])>PARENT
        assert F(d['chosen_simple_lambda3_lower_decimal'])==PARENT
    assert 41*A*A<PARENT
    # For positive x_i on simplex: |partial_ell_j x_i|<=1/2.
    # T40 degree2: |T|<=8 and |dT|<=20.
    # T42: |T|<=6 and |dT|<=19/2.
    # T44=(x-y)^2-4xy: |T|<=1, |dT|<=6.
    # Score covariance of normalized sqrt(Q) angular probability <= |T|.
    # 4pi times conventional real-harmonic factors bounded by (2,5,6).
    jac_sq=(F(56,3)**2+F(155,4)**2+F(21)**2)
    assert jac_sq<F(50)**2
    assert 3*HMAX*50<L
    # Positivity Einstein ODE: h_i'= -(sum h)h_i+P_i, P_i>=0.
    # Initial: E0<1, shear s=(1/5,-13/100,-7/100),
    # 0.5 sum(s_i^2)< 1/25 and h_i(0)< sqrt((1+1/25)/3)+1/5<.8.
    # Along expanding time P_i<=E<=E0<1, hence h_i(u)<.8+.08=.88<.9.
    assert (F(1)+F(1,25))/3 < F(3,5)**2
    assert F(3,5)+F(1,5)+T < HMAX
    # E0>.5 implies H0>sqrt(1/6)>.13, so all three initial h_i positive.
    assert F(1,6)>F(13,100)**2
    rad=A/(2*L)
    assert rad<T/2
    certified=A**3/(8*L)
    assert certified>F(1,10**23)
    result={'schema':'bass.ce1ae.conditional_true_continuous_time_integral_kernel_min_eigenvalue.v1',
      'parent_pr':281,'parent_head':'f80f03d33a8b98cd49dfb9cda85ae316d868cdf6',
      'original_source_sha256':SRC,
      'strict_sampled_Gram_lambda3_inherited_rational':str(PARENT),
      'per_sample_abs_projection_lower_rational':str(A),
      'physical_hubble_upper_rational':str(HMAX),'Lipschitz_norm_bound_rational':str(L),
      'local_one_sided_duration_rational':str(rad),
      'strict_uniform_du_integral_Gram_lambda3_lower_rational':str(certified),
      'strict_integral_Gram_simple_lower_rational':str(F(1,10**23)),
      'conditional_on':['valid original 6-cell continuum Einstein-Vlasov source, positive massless angular density',
                        'correct original CE1-AD strict sampled Gram lambda3 >3e-12',
                        'input source, EOS and proper-time conventions unchanged'],
      'derivation':[
        'For any unit v, sum_j (v dot X(u_j))^2 > 3e-12; 41*a^2<3e-12 implies some |v dot X(u_j)|>a=1/4e6.',
        'Positive original angular mass yields |partial_ell_j X|_2<50 by normalized polynomial covariance bounds.',
        'Einstein-Vlasov positive pressure, E<1 and h_i(0)<.8 imply |h_i(u)|<.9 on [0,.08]. Hence ||X_prime(u)||_2 < 135 < L=150.',
        'Within one-sided radius a/(2L) from that u_j, |v dot X(u)|>a/2.',
        'Integral du (v dot X(u))^2 > (a/(2L))*(a/2)^2=a^3/(8L)>1e-23.',
        'The three nonzero eigenvalues of integral kernel operator K4(u,v)=X(u).X(v) on L2([0,.08],du) are equal to eigenvalues of G=integral X X^T du.'
      ],
      'status':'EXACT_RATIONAL_ALGEBRA_DERIVED_CONDITIONAL_ON_PARENT_41_SAMPLED_CERT',
      'numerical_spectrum_not_used_in_inequality':True,
      'UPPER_DAG':'9/15','CE1':'PARTIAL','production_ready':False,'merge_ready':False,'auto_next':False}
    (BASE/'data'/'CONTINUOUS_TIME_STRICT_GAP_WITNESS.json').write_text(json.dumps(result,indent=2)+'\n')
    print('INTEGRAL GRAM certified >',certified,' = ',float(certified),' > 1e-23 (conditional on PR281)')
    return result
if __name__=='__main__':main()

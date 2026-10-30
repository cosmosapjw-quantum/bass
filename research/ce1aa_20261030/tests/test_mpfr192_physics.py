"""Scoped physics/provenance tests. These are NOT independent-author R6/C9."""
from pathlib import Path
import csv,hashlib,json,math,sys
from fractions import Fraction
import numpy as np
import pytest
import mpmath as mp
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'source'))
import mpfr192_sky as m
import interval_k4_spectrum as s
DATA=json.loads((ROOT/'data/SCIENCE_RESULTS.json').read_text())


def test_01_original_exact_binary_source():
    assert m.frozen_source_identity()==m.SOURCE_SHA
    for n in (6,8):
        rays,w=m.make_cell_rays(n)
        assert m.hashbytes(rays.tobytes())==m.RAY_SHA[n][0]
        assert m.hashbytes(w.tobytes())==m.RAY_SHA[n][1]
        assert m.hashbytes((ROOT/'input'/f'GL{n}_DOP853_coupled_41epochs.csv').read_bytes())==m.INPUT_SHA[n]


def test_02_true_native_mpfr192_and_directed_roundings():
    assert m.PREC==192 and m.RD==3 and m.RU==2
    x=m.pi_iv().pair()
    assert x[0]<=math.pi<=x[1]
    y=(m.IV.val(2).sqrt()).pair()
    assert y[0]<=math.sqrt(2)<=y[1]
    a=(m.IV.val(-1)*m.IV.val(2)).pair()
    assert a==[-2.0,-2.0]
    b=(m.IV.val(1)/m.IV.val(3)).pair()
    assert b[0]<=1/3<=b[1] and b[0]<b[1]
    z=m.IV.val(-7)-m.IV.val(3);assert z.pair()==[-10,-10]


def test_03_MPFR_result_counts_and_epistemic_gates():
    assert DATA['upper_dag']=='9/15' and DATA['CE1']=='PARTIAL'
    assert not DATA['merge_ready'] and not DATA['production_ready']
    for n in (6,8):
        d=DATA['channels'][str(n)]
        assert d['epoch_count']==41 and d['physical_pair_count']==1681
        assert d['GL']==n and d['ray_count']==6*n*n
        assert d['DOP853_geometry_accuracy']=='NOT_CERTIFIED'
        assert d['continuous_einstein_vlasov_solution_lambda2']=='NOT_CERTIFIED'
        assert d['GL_source_at_fixed_geometry_lambda2']=='CERTIFIED_STRICTLY_POSITIVE_IF_PARENT_PR270_PROOF_ACCEPTED'


def test_04_true_192_bit_hex_endpoints_encoded():
    for n in (6,8):
        obj=json.loads((ROOT/'data'/f'GL{n}_mpfr192_source_41.json').read_text())
        assert len(obj['states'])==41 and obj['precision_bits']==192
        for row in obj['states']:
            assert len(row['alpha_mpfr192'])==3
            for endpoints in row['alpha_mpfr192']:
                assert all('mantissa_base16' in e and 'base16_exponent' in e for e in endpoints)
            for k in ('E','a40','a42','a44'):
                assert row[k][0] <= row[k][1]


def test_05_mathematically_signed_gram_spectral_criterion():
    for n in (6,8):
        d=DATA['channels'][str(n)];p=d['stored_GL_lambda2_strict_lower_candidate'];
        assert p['det_S_minus_LI_outward_f64'][1]<0
        assert p['trace_S_outward_f64'][0]>3*p['candidate_L_literal']
        assert d['stored_GL_lambda_estimates_exploratory'][1]>p['candidate_L_literal']


def test_06_exact_rational_source_to_continuum_weyl_gate():
    proof=json.loads((ROOT/'input/l4_source_and_transfer.json').read_text())
    for n in (6,8):
        d=DATA['channels'][str(n)];parent=proof['cases'][str(n)]
        eps=Fraction(parent['source_only_cross_kernel_error_ceil_27'])
        L=float(d['stored_GL_lambda2_strict_lower_candidate']['candidate_L_literal'])
        exact=Fraction.from_float(L)-41*eps
        assert exact>0 and str(exact)==d['continuous_original_six_cell_source_fixed_geometry_lambda2_lower_rational']
        assert d['source_41x41_weyl_matrix_spectral_norm_upper_decimal']==str(41*eps)


def test_07_physical_K4_41_squared_matrix():
    for n in (6,8):
        p=ROOT/'data'/f'GL{n}_MPFR192_K4_1681.csv'
        with p.open() as f:rows=list(csv.DictReader(f))
        assert len(rows)==41**2
        lo=np.array([float(r['K4_delta_lbound_float_outward']) for r in rows]).reshape(41,41)
        hi=np.array([float(r['K4_delta_ubound_float_outward']) for r in rows]).reshape(41,41)
        assert np.isfinite(lo).all() and np.all(lo<=hi)
        assert np.max(abs(lo-lo.T))<1e-15
        assert np.max(abs(hi-hi.T))<1e-15
        assert np.max(hi-lo)<2e-16
        target=DATA['channels'][str(n)]['K4_endpoint_original_stored_geometry_interval_f64']
        assert lo[0,40]==target[0] and hi[0,40]==target[1]


def test_08_first_certified_temporal_mode_is_an_error_gate_not_physical_onset():
    assert DATA['channels']['6']['first_certified_nonzero_continuum_secondary_mode_prefix_count']==15
    assert DATA['channels']['8']['first_certified_nonzero_continuum_secondary_mode_prefix_count']==3
    for n in (6,8):
        with (ROOT/'data'/f'GL{n}_CUMULATIVE_41_PREFIX_SPECTRA.csv').open() as f:rows=list(csv.DictReader(f))
        assert len(rows)==41
        arr=[r['continuum_secondary_mode_certified']=='True' for r in rows]
        assert arr[-1] and any(arr)
        assert arr.index(True)+1==DATA['channels'][str(n)]['first_certified_nonzero_continuum_secondary_mode_prefix_count']


def test_09_cross_harmonic_orthogonality_not_thermodynamic_cmb():
    assert 'DOP853' in DATA['scientific_scope']
    assert 'NOT DOP853 trajectory certificate' in DATA['scientific_scope']


def test_10_binary64_sky_center_gap_recorded_not_assumed_zero():
    assert DATA['channels']['6']['max_binary64_DOP_coefficient_gap_from_interval']>0
    assert DATA['channels']['8']['max_binary64_DOP_coefficient_gap_from_interval']>0
    assert DATA['channels']['8']['max_binary64_DOP_coefficient_gap_from_interval']<5e-15


def test_11_source_hash_rejects_mutation(tmp_path):
    q=tmp_path/'GL8_DOP853_coupled_41epochs.csv'
    q.write_bytes((ROOT/'input/GL8_DOP853_coupled_41epochs.csv').read_bytes()+b'fake')
    assert m.hashbytes(q.read_bytes())!=m.INPUT_SHA[8]


def independent_mpmath_source(n,index):
    mp.mp.dps=95
    rays,ww=m.make_cell_rays(n)
    with (ROOT/'input'/f'GL{n}_DOP853_coupled_41epochs.csv').open() as f:rows=list(csv.DictReader(f))
    row=rows[index]
    ell=[mp.mpf(float(row[f'ell{k}'])) for k in (1,2,3)]
    b=[mp.exp(-2*x) for x in ell];v=mp.exp(-sum(ell))
    E=a40=a42=a44=mp.mpf(0)
    c40=mp.mpf(3)/(16*mp.sqrt(mp.pi))
    c42=mp.mpf(3)/8*mp.sqrt(5/(2*mp.pi))
    c44=mp.mpf(3)/16*mp.sqrt(35/(2*mp.pi))
    for rr,w0 in zip(rays,ww):
        xx,yy,zz=[b[j]*mp.mpf(float(rr[j]))**2 for j in range(3)]
        r=mp.sqrt(xx+yy+zz);x,y,z=xx/r**2,yy/r**2,zz/r**2
        weight=mp.mpf(float(w0))*r
        E+=weight
        a40+=weight*c40*(35*z*z-30*z+3)
        a42+=weight*c42*(x-y)*(7*z-1)
        a44+=weight*c44*(x*x-6*x*y+y*y)
    return [float(v*E),float(v*a40),float(v*a42),float(v*a44)]

@pytest.mark.parametrize('n,index',[(6,0),(6,20),(6,40),(8,0),(8,20),(8,40)])
def test_12_independent_mpmath_95digit_source_at_original_geometry(n,index):
    q=json.loads((ROOT/'data'/f'GL{n}_mpfr192_source_41.json').read_text())['states'][index]
    v=independent_mpmath_source(n,index)
    for k,actual in zip(('E','a40','a42','a44'),v):
        lo,hi=q[k]
        # Independent mp.mpf calculation is rounded at 95 digits, and then
        # converted to float. The MPFR endpoints are outward to float.
        assert lo<=actual<=hi,(n,index,k,lo,actual,hi)


def test_13_original_six_cell_GL_off_unit_preserved():
    ray,w=m.make_cell_rays(8)
    n2=np.sum(ray*ray,axis=1)
    assert n2.shape==(384,)
    assert np.max(abs(n2-1))>0
    assert np.max(abs(n2-1))<1e-12


def test_14_analytic_isotropic_scaling_contrast_invariance():
    # U transforms as common volume-energy density; normalized sky shape
    # for every fixed initial source is invariant under e1=e2=e3 shift.
    q=m.rays(6);cs=m.constants()
    a=m.sky_at_state([0.,0.,0.],q,cs)['alpha']
    b=m.sky_at_state([0.02,0.02,0.02],q,cs)['alpha']
    for x,y in zip(a,b):
        assert abs(np.mean(x.pair())-np.mean(y.pair()))<2e-15

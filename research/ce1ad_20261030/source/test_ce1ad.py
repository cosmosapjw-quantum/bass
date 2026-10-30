"""CE1-AD scientific regression, trust-boundary and same-context adversarial checks."""
from pathlib import Path
import csv,hashlib,json,sys
from fractions import Fraction as F
import numpy as np
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'source'))
import certify_sampled_lambda3 as cert
import physical_third_mode_atlas as atlas

@pytest.mark.parametrize('n',[6,8])
def test_proof_input_identity(n):
    d=json.loads((ROOT/'data'/f'GL{n}_EXACT_41SAMPLE_LAMBDA3_CERTIFICATE.json').read_text())
    assert d['original_source_sha256']==cert.SOURCE_SHA
    assert d['source_41epoch_history_sha256']==cert.GL_HISTORY_SHA[n]
    for name, input in [('MPFR192_interval_center_source_sha256',f'GL{n}_SOURCE_MPFR192.json'),('inherited_geometric_transport_sha256',f'GL{n}_GEOMETRY_BOUND.json'),('inherited_exact_angular_source_sha256','EXACT_SIX_CELL_L4_SOURCE.json')]:
        assert d[name]==hashlib.sha256((ROOT/'input'/input).read_bytes()).hexdigest()

@pytest.mark.parametrize('n',[6,8])
def test_stored_lambda3_positive_sylvester(n):
    d=json.loads((ROOT/'data'/f'GL{n}_EXACT_41SAMPLE_LAMBDA3_CERTIFICATE.json').read_text())
    assert F(d['rigorous_Sylvester_first_principal_minor_lower'])>0
    assert F(d['rigorous_Sylvester_second_principal_minor_lower'])>0
    assert F(d['rigorous_Sylvester_third_principal_minor_lower'])>0
    assert F(d['rigorous_sigma3_stored_GL_lower_rational'])==cert.R_LOW

@pytest.mark.parametrize('n',[6,8])
def test_true_continuum_source_ode_transport(n):
    d=json.loads((ROOT/'data'/f'GL{n}_EXACT_41SAMPLE_LAMBDA3_CERTIFICATE.json').read_text())
    assert F(d['original_continuum_sigma3_lower'])>0
    assert F(d['original_continuum_lambda3_lower'])>cert.PROOF_LAM3
    assert d['rank3_41samples_certified_conditional']
    assert d['UPPER_DAG']=='9/15' and d['CE1']=='PARTIAL'
    assert not d['production_ready'] and not d['merge_ready'] and not d['auto_next']
    assert not any('integral operator' in x and 'eigenvalue' not in x for x in d['not_claimed'])

@pytest.mark.parametrize('n',[6,8])
def test_mpfr192_hex_endpoint_exact_contains_double(n):
    data=json.loads((ROOT/'input'/f'GL{n}_SOURCE_MPFR192.json').read_text())
    for row in data['states']:
        for original,prec in zip(row['alpha'],row['alpha_mpfr192']):
            lo=cert.hex_mpfr192_rational(prec[0]);hi=cert.hex_mpfr192_rational(prec[1])
            assert F.from_float(original[0])<=lo<=hi<=F.from_float(original[1])

@pytest.mark.parametrize('n',[6,8])
def test_independent_mpmath_smallest_eigenvalue(n):
    import mpmath as mp
    mp.mp.dps=90
    data=json.loads((ROOT/'input'/f'GL{n}_SOURCE_MPFR192.json').read_text())
    rt2=mp.sqrt(2)
    s=[mp.mpf(1)/3,rt2/3,rt2/3]
    mat=[]
    for row in data['states']:
        vals=[]
        for k,ep in enumerate(row['alpha_mpfr192']):
            q=[cert.hex_mpfr192_rational(z) for z in ep]
            midpoint=(q[0]+q[1])/2
            vals.append(mp.mpf(midpoint.numerator)/mp.mpf(midpoint.denominator)*s[k])
        mat.append(vals)
    gram=mp.matrix([[sum(mat[t][i]*mat[t][j] for t in range(41)) for j in range(3)] for i in range(3)])
    eig,_=mp.eigsy(gram)
    # independent high-precision numerical check only; not the proof basis.
    assert eig[0]>mp.mpf(7549)**2/mp.mpf(10)**18
    assert eig[0] < mp.mpf('5.72e-11')

@pytest.mark.parametrize('n',[6,8])
def test_mode3_physical_atlas_consistency(n):
    d=json.loads((ROOT/'data'/'THIRD_MODE_ATLAS.json').read_text())[str(n)]
    v=np.array(d['physical_41sample_mode3_direction_X40_X42_X44'])
    assert abs(v@v-1)<1e-13 and v[-1]>0
    assert abs(d['sum_mode3_amplitude_sq']-d['numerical_lambda3'])<3e-15
    assert len(d['max_three_epoch_det_indices_and_signed_value'])==4

@pytest.mark.parametrize('n',[6,8])
def test_old_gram_weyl_does_not_prove_third_mode(n):
    d=json.loads((ROOT/'input'/f'GL{n}_GEOMETRY_BOUND.json').read_text())
    a=json.loads((ROOT/'data'/'THIRD_MODE_ATLAS.json').read_text())[str(n)]
    assert d['Gram_weyl_delta_upper']>a['numerical_lambda3']
    assert cert.R_LOW-2*F.from_float(d['frob_deltaX_upper'])<0


def test_rational_scale_and_source_error_attack():
    from fractions import Fraction as F
    rt=cert.sqrt_rational_enclosure(F(2),75)
    assert rt.lo**2<=2<=rt.hi**2
    # Unit MPFR base16 mantissa "1", exponent=1 encodes exactly 1.
    unit={'mantissa_base16':'1','base16_exponent':1}
    row=cert.scale_columns([[unit,unit]]*3)
    assert row[0].lo==row[0].hi==F(1,3)
    assert row[1].lo<=rt.hi/3<=row[1].hi
    assert row[2].lo<=rt.lo/3<=row[2].hi
    # Replacing the physics-derived Bgeo by twice its value is NOT certified.
    for n in (6,8):
        d=json.loads((ROOT/'input'/f'GL{n}_GEOMETRY_BOUND.json').read_text())
        assert cert.R_LOW - 2*F.from_float(d['frob_deltaX_upper'])<0


def test_all_82_physical_records_present():
    with (ROOT/'data'/'CE1AD_82_PHYSICAL_THIRD_MODE_TIMELINE.csv').open() as f:rows=list(csv.DictReader(f))
    assert len(rows)==82
    assert set(r['GL'] for r in rows)=={'6','8'}
    for n in (6,8):
        rr=[r for r in rows if r['GL']==str(n)]
        assert len(rr)==41 and abs(float(rr[0]['u']))<1e-15 and abs(float(rr[-1]['u'])-.08)<1e-15

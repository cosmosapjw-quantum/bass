#!/usr/bin/env python3
"""CE1-AD conditional, exact-rational sampled l=4 Gram third eigenvalue proof.

No numerical eigensolver is a proof ingredient. PR275 directed 192-bit sky intervals
are regarded as certified outward endpoint doubles; PR270 exact source and PR277
geometry transport are inherited with their declared hypotheses. A new exact
Fraction interval Sylvester witness and singular-value (not Gram-Weyl) transport
certifies the original six-cell continuum 41-epoch lambda3 lower bound.
"""
from __future__ import annotations
from fractions import Fraction as F
from dataclasses import dataclass
from pathlib import Path
import hashlib, json, math

BASE = Path(__file__).resolve().parents[1]
SOURCE_SHA = '022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035'
GL_HISTORY_SHA = {
    6: '6eff8cd9f31d027bbee55720332302b6fbad71b3639b5809aab6b9ce6f53e489',
    8: '1398980ec71662494273e05eb4bd52a78f6e6c7f208702638da6c739698f7502',
}
PARENT_HEAD='15dd3ad604f0219132984b7b23538ef91aeff87e'
EXPECTED_INPUT_SHA256={
 'EXACT_SIX_CELL_L4_SOURCE.json':'f1579a9b3ebed7bea3588d9ae759ab12b59c2714729f2b9e22a2cdf1a1b153f2',
 'GL6_SOURCE_MPFR192.json':'edd08d0276daa955f1388fbb4ac2ad73424d6b3b51f7fcdacbbb164a19f546ec',
 'GL8_SOURCE_MPFR192.json':'e02bdc353652e26a689ecc353124f9fd6efadb1d27c8f895a9db993c5c620fb3',
 'GL6_GEOMETRY_BOUND.json':'17bdb90ed8612c8123a4e407b34225fcb4b09bed3cd644e3751b248dab28e226',
 'GL8_GEOMETRY_BOUND.json':'0745717abcdc737df09c0c20fbe7bfe8b8d0a5b16cba1a52b76cea60b47452cf',
}
PROOF_LAM3=F(3,10**12)
# Lower numerical singular-value witness (rational). The proof checks
# S-(r_lower)^2 I >0 via all exact interval leading principal minors.
R_LOW=F(7549,10**9)

@dataclass(frozen=True)
class Iv:
    lo:F
    hi:F
    def __post_init__(self):
        if self.lo>self.hi:raise ValueError('interval reversed')
    @staticmethod
    def val(q):
        if isinstance(q,Iv):return q
        q=F(q);return Iv(q,q)
    def __add__(self,other):
        o=Iv.val(other);return Iv(self.lo+o.lo,self.hi+o.hi)
    __radd__=__add__
    def __neg__(self):return Iv(-self.hi,-self.lo)
    def __sub__(self,other):return self+-Iv.val(other)
    def __rsub__(self,other):return Iv.val(other)+-self
    def __mul__(self,other):
        o=Iv.val(other)
        q=[self.lo*o.lo,self.lo*o.hi,self.hi*o.lo,self.hi*o.hi]
        return Iv(min(q),max(q))
    __rmul__=__mul__
    def __truediv__(self,other):
        o=Iv.val(other)
        if o.lo<=0<=o.hi:raise ZeroDivisionError('interval divisor contains zero')
        return self*Iv(F(1,o.hi),F(1,o.lo))

def sqrt_rational_enclosure(q:F, digits=75):
    if q<0:raise ValueError('negative')
    scale=10**digits
    n=math.isqrt((q.numerator*scale*scale)//q.denominator)
    return Iv(F(n,scale),F(n+1,scale))

def det3(A):
    a,b,c=A[0];d,e,f=A[1];g,h,i=A[2]
    return a*(e*i-f*h)-b*(d*i-f*g)+c*(d*h-e*g)

def mat_mid(A):
    return [[float((c.lo+c.hi)/2) for c in row] for row in A]

def hex_mpfr192_rational(payload):
    """MPFR mpfr_get_str(base16) mantissa/exponent exact bit-pattern."""
    m=payload["mantissa_base16"]; e=int(payload["base16_exponent"])
    d=len(m.lstrip("+-"))
    return F(int(m,16))*16**(e-d) if e>=d else F(int(m,16),16**(d-e))

def scale_columns(alpha):
    # K4=(alpha40^2+2 alpha42^2+2 alpha44^2)/9.
    # sqrt(2) enclosure is obtained from exact rational integer isqrt.
    rt2=sqrt_rational_enclosure(F(2),75)
    scales=[Iv.val(F(1,3)),rt2/3,rt2/3]
    return [Iv(hex_mpfr192_rational(v[0]),hex_mpfr192_rational(v[1]))*s for v,s in zip(alpha,scales)]

def fmt_lower(q:F,places=28):
    a=(q.numerator*10**places)//q.denominator
    return f'{a//10**places}.{a%10**places:0{places}d}'

def fmt_upper(q:F,places=28):
    n=(q.numerator*10**places+q.denominator-1)//q.denominator
    return f'{n//10**places}.{n%10**places:0{places}d}'

def find_input(name, relative):
    # Source-inclusive ZIP owns input snapshots; GitHub branch reuses original
    # immutable parent files without copying or rewriting the authority.
    local=BASE/'input'/name
    if local.is_file():return local
    remote=BASE.parent/relative
    if not remote.is_file():raise FileNotFoundError(f'No original dependency: {local} or {remote}')
    return remote

def run_one(n):
    source=find_input(f'GL{n}_SOURCE_MPFR192.json',f'ce1aa_20261030/data/GL{n}_mpfr192_source_41.json')
    geo=find_input(f'GL{n}_GEOMETRY_BOUND.json',f'ce1ab_20261030/results/GL{n}_CE1AB_RANK2_N32.json')
    pr=find_input('EXACT_SIX_CELL_L4_SOURCE.json','ce1aa_20261030/input/l4_source_and_transfer.json')
    for path in (source,geo,pr):
        key={'GL'+str(n)+'_SOURCE_MPFR192.json':f'GL{n}_SOURCE_MPFR192.json',
             f'GL{n}_GEOMETRY_BOUND.json':f'GL{n}_GEOMETRY_BOUND.json',
             'EXACT_SIX_CELL_L4_SOURCE.json':'EXACT_SIX_CELL_L4_SOURCE.json'}.get(path.name)
        if key is not None:
            assert hashlib.sha256(path.read_bytes()).hexdigest()==EXPECTED_INPUT_SHA256[key],key
    a=json.loads(source.read_text());g=json.loads(geo.read_text());p=json.loads(pr.read_text())
    assert a['source_sha256']==g['original_source_sha256']==SOURCE_SHA
    assert a['history_sha256']==g['original_history_sha256']==GL_HISTORY_SHA[n]
    assert a['order']==g['GL']==n and a['precision_bits']==g['MPFR_precision_bits']==192
    assert len(a['states'])==41 and g['rank_at_least_two'] and g['integrator_GL_enclosed']
    pc=p['cases'][str(n)]
    assert pc['original_physical_source_sha256']==SOURCE_SHA
    # Verify that MPFR192 rational endpoint conversion lies inside its original
    # outward binary64 published carrier. This catches an exponent convention bug.
    for state in a['states']:
        for j, pair in enumerate(state['alpha_mpfr192']):
            lo=hex_mpfr192_rational(pair[0]);hi=hex_mpfr192_rational(pair[1])
            pub=state['alpha'][j]
            assert F.from_float(float(pub[0]))<=lo<=hi<=F.from_float(float(pub[1]))
    X=[scale_columns(st['alpha_mpfr192']) for st in a['states']]
    S=[[sum((X[k][i]*X[k][j] for k in range(41)),Iv.val(0)) for j in range(3)] for i in range(3)]
    shifted=[[S[i][j]-(R_LOW**2 if i==j else 0) for j in range(3)] for i in range(3)]
    D1=shifted[0][0]
    D2=shifted[0][0]*shifted[1][1]-shifted[0][1]*shifted[1][0]
    D3=det3(shifted)
    assert D1.lo>0 and D2.lo>0 and D3.lo>0, 'Sylvester did not prove sigma_3 > 7549e-9'
    # Fresh source-only error in alpha_m at any of 41 fixed geometries.
    eps=[F(pc['fractional_harmonic_source_errors'][k]['exact']) for k in ('a40','a42','a44')]
    epsX=[eps[0]/3,eps[1]*sqrt_rational_enclosure(F(2),75).hi/3,eps[2]*sqrt_rational_enclosure(F(2),75).hi/3]
    b_src_sq=41*sum((v*v for v in epsX),F(0))
    b_src_up=sqrt_rational_enclosure(b_src_sq,60).hi
    b_geom=F.from_float(float(g['frob_deltaX_upper']))  # outward MPFR upper in parent
    b_total=b_geom+b_src_up
    sigma_lower=R_LOW-b_total
    assert sigma_lower>0,'Cumulative source+geometry error swallows original 3rd mode'
    lambda_lower=sigma_lower*sigma_lower
    assert lambda_lower>PROOF_LAM3, 'Selected 3e-12 lower target not proved'
    output={
        'schema':'bass.ce1ad.original_sixcell_41sample_lambda3.v1',
        'claim':'conditional certified lower on 41x3 sampled exact original continuous Einstein-Vlasov l4 Gram',
        'parent_pr':280,'parent_head_sha':PARENT_HEAD,
        'original_source_sha256':SOURCE_SHA,
        'gl_order':n,'time_samples':41,'MPFR192_interval_center_source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'inherited_geometric_transport_sha256':hashlib.sha256(geo.read_bytes()).hexdigest(),
        'inherited_exact_angular_source_sha256':hashlib.sha256(pr.read_bytes()).hexdigest(),
        'source_41epoch_history_sha256':GL_HISTORY_SHA[n],
        'stored_exact_dyadic_gl_angular_interval':True,
        'sigma_ref_interval_method':'MPFR192 raw hex exact Fractions + rational sqrt2 enclosure + Sylvester SPD sign',
        'rigorous_Sylvester_first_principal_minor_lower':fmt_lower(D1.lo,40),
        'rigorous_Sylvester_second_principal_minor_lower':fmt_lower(D2.lo,40),
        'rigorous_Sylvester_third_principal_minor_lower':fmt_lower(D3.lo,50),
        'rigorous_sigma3_stored_GL_lower_rational':str(R_LOW),
        'rigorous_sigma3_stored_GL_lower_decimal':fmt_lower(R_LOW,14),
        'inherited_geometry_and_ODE_Frobenius_X_error_upper':g['frob_deltaX_upper'],
        'PR270_rational_uniform_fractional_harmonic_alpha_component_error_ceil_27':[pc['fractional_harmonic_source_errors'][k]['ceil_27'] for k in ('a40','a42','a44')],
        'new_source_only_Frobenius_X_error_upper':fmt_upper(b_src_up,26),
        'total_Frobenius_X_error_upper':fmt_upper(b_total,26),
        'original_continuum_sigma3_lower':fmt_lower(sigma_lower,26),
        'original_continuum_lambda3_lower':fmt_lower(lambda_lower,28),
        'chosen_simple_lambda3_lower_exact_rational':str(PROOF_LAM3),
        'chosen_simple_lambda3_lower_decimal':fmt_lower(PROOF_LAM3,16),
        'rank3_41samples_certified_conditional':True,
        'source_uniform_ell_box':'[0,0.08]^3 (inherited PR270)',
        'source_ODE_trajectory_status':'CONDITIONAL_ON_PR264_PR277_DOP853_IVP_PROOF',
        'assumptions':['Correct PR270 680-moment exact rational positive six-cell source theorem',
                       'Correct PR277 MPFR192 path/derivative/tube enclosure and 41 source evaluation',
                       'Correct MPFR192 ctypes directed roundoff and source input identity'],
        'not_claimed':['rigorous smallest nonzero eigenvalue for continuous time integral operator',
                       'CMB temperature/polarization likelihood','third independent manuscript reviewer',
                       'production solver or global BASS DAG completion'],
        'UPPER_DAG':'9/15','CE1':'PARTIAL','production_ready':False,'merge_ready':False,'auto_next':False,
    }
    path=BASE/'data'/f'GL{n}_EXACT_41SAMPLE_LAMBDA3_CERTIFICATE.json'
    path.write_text(json.dumps(output,indent=2,ensure_ascii=False)+'\n')
    print('GL',n,'Sylvester3lower',output['rigorous_Sylvester_third_principal_minor_lower'],
          'Bgeo',b_geom,'Bsrc',float(b_src_up),'sigma margin',float(sigma_lower),
          'lam3 bound',float(lambda_lower),flush=True)
    return output

def main():
    out={str(n):run_one(n) for n in (6,8)}
    path=BASE/'data'/'SCIENCE_RESULTS.json'
    path.write_text(json.dumps({'schema':'bass.ce1ad.science.v1','results':out},indent=2,ensure_ascii=False)+'\n')
    return out

if __name__=='__main__':main()

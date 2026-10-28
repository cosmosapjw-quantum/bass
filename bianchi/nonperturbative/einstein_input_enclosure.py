"""CE1-D: nonperturbative sensitivity to specified physical-input intervals.

These functions use directed GNU MPFR intervals from CE1-C. Unlike a linearized
Einstein-Vlasov solution, comparison inequalities apply to finite parameter
changes, given positivity and expanding-octant assumptions. The *nominal path*
error is a separate already-verified CE1-C bound, combined by triangle inequality.

All inputs defining physical uncertainty are exact rational-decimal strings.
The reference initial data are the exact binary64 coefficients stored by CE1-C.
No claim of formally verified Python bindings, arbitrary radiation or source
acquisition uncertainty outside these declared boxes is made.
"""
from __future__ import annotations
from fractions import Fraction
import math
from bianchi.nonperturbative.einstein_interval import Interval, _iv_fraction, propagate_interval


def _need_oracle(backend):
    if backend != 'python_oracle':
        raise ValueError("Explicit backend='python_oracle' required")


def _as_fraction(s):
    if not isinstance(s, str):
        raise ValueError('Physical input center/radius must be an exact decimal string')
    try:
        return Fraction(s)
    except (ValueError, ZeroDivisionError) as exc:
        raise ValueError('Invalid exact decimal input') from exc


def _box(pair):
    if not isinstance(pair, (tuple,list)) or len(pair)!=2:
        raise ValueError('Expected (decimal center, decimal radius)')
    center,radius=map(_as_fraction,pair)
    if radius<0:raise ValueError('Nonnegative radius required')
    return center-radius,center+radius


def _max_delta(lo,hi,reference):
    return max(abs(lo-reference),abs(hi-reference))


def _iv_box(lo,hi):
    x=_iv_fraction(lo);y=_iv_fraction(hi)
    return Interval.between(x.lower,y.upper)


def _sq_nonnegative(a):
    if a.lower<=0<=a.upper:
        return Interval.between(0,max((Interval(a.lower)**2).upper,
                                      (Interval(a.upper)**2).upper))
    return a*a


def _maxabs_interval(z):
    return max(abs(z.lower),abs(z.upper))


def _polynomial_exact_min(c2,ct,c4):
    """Exact minimum over q on S² of 1+c2 P2+ct(qx²-qy²)+c4 P4."""
    a=Fraction(35,8)*c4
    b=Fraction(3,2)*c2-Fraction(30,8)*c4+abs(ct)
    d=1-c2/2+Fraction(3,8)*c4-abs(ct)
    vals=[d,a+b+d]
    if a>0:
        r=-b/(2*a)
        if 0<r<1:vals.append(a*r*r+b*r+d)
    return min(vals)


def angular_absolute_basis_bounds():
    """Proved upper means: <|P2|><=2/5, <|(qx²-qy²)|><=4/9, <|P4|><=1/3.

    First: exact 2/(3 sqrt 3)<2/5; second exact 4/(3pi)<4/9
    since pi>3; third Cauchy-Schwarz and <P4²>=1/9.
    """
    return {'P2': Fraction(2,5),'T':Fraction(4,9),'P4':Fraction(1,3)}


def enclose_physical_inputs(source, *, energy, coefficients, shear,
                            u_end='1', reference_shear_xy=(.2,-.13),backend=None):
    """Bound *continuum ODE* input-to-geometry effect on 0 <= u <= u_end.

    For ell_i >=0, 0<=r(q;ell)<=1 and b_i q_i²/r<=r;
    thus |delta P_i|<= integral |delta F0| <= eta_data.  Constant
    source forcing eta_data and initial H perturbation are passed through
    CE1-A's finite-difference comparison via outward MPFR arithmetic.
    """
    _need_oracle(backend)
    from bianchi.nonperturbative.einstein_error_budget import PolynomialRadiation
    if not isinstance(source,PolynomialRadiation):
        raise TypeError('PolynomialRadiation reference required')
    if len(coefficients)!=3 or len(shear)!=2:
        raise ValueError('Three angular coefficient and two shear boxes required')
    E_lo,E_hi=_box(energy)
    C=[_box(c) for c in coefficients]
    S=[_box(s) for s in shear]
    U=_as_fraction(u_end)
    if E_lo<=0:raise ValueError('Positive energy throughout physical input box required')
    if U<0:raise ValueError('Nonnegative time endpoint required')
    E_ref=Fraction.from_float(float(source.energy0))
    C_ref=[Fraction.from_float(float(x)) for x in source.coefficients]
    S_ref=[Fraction.from_float(float(v)) for v in reference_shear_xy]
    if len(S_ref)!=2:raise ValueError('Two nominal shear components required')
    dE=_max_delta(E_lo,E_hi,E_ref)
    dC=[_max_delta(*C[i],C_ref[i]) for i in range(3)]
    dS=[_max_delta(*S[i],S_ref[i]) for i in range(2)]
    margin=_polynomial_exact_min(*C_ref)-sum(dC)
    if margin<=0:raise ValueError('Cannot guarantee angular positivity throughout input box')
    Emax=max(E_ref,E_hi)
    caps=angular_absolute_basis_bounds()
    eta=dE+Emax*(caps['P2']*dC[0]+caps['T']*dC[1]+caps['P4']*dC[2])
    si=[_iv_box(*s) for s in S]
    si.append(-(si[0]+si[1]))
    hbar=((_iv_box(E_lo,E_hi)+sum((_sq_nonnegative(x) for x in si),Interval(0))/2)/3).sqrt()
    h0=[hbar+x for x in si]
    if any(h.lower<0 for h in h0):
        raise ValueError('Cannot guarantee all-direction initial expansion in input box')
    sref=[_iv_fraction(v) for v in S_ref];sref.append(-(sref[0]+sref[1]))
    root_ref=((_iv_fraction(E_ref)+sum((_sq_nonnegative(x) for x in sref),Interval(0))/2)/3).sqrt()
    hr=[root_ref+x for x in sref]
    initial_diff=max(_maxabs_interval(h0[i]-hr[i]) for i in range(3))
    d0=_iv_fraction(Fraction.from_float(initial_diff))
    a=propagate_interval([Interval(0),d0],_iv_fraction(U),_iv_fraction(Emax),Interval(0),Interval(0))
    b=propagate_interval([Interval(0),Interval(0)],_iv_fraction(U),_iv_fraction(Emax),Interval(0),_iv_fraction(eta))
    total=[a[i]+b[i] for i in range(2)]
    return {'status':'ADMITTED_POSITIVE_EXPANDING_INPUT_BOX',
            'input_semantics':'exact rational decimal input boxes vs stored binary64 reference',
            'u_end':str(u_end), 'eta_source_upper':_iv_fraction(eta).upper,
            'initial_h_upper':d0.upper,'positivity_margin_lower':_iv_fraction(margin).lower,
            'min_expansion_lower':min(x.lower for x in h0),
            'initial_h_propagated_upper':a[1].upper,
            'source_h_upper':b[1].upper,
            'input_h_upper':total[1].upper,
            'input_ell_upper':total[0].upper,
            'reference_energy_binary':float(source.energy0),
            'Emax_upper':_iv_fraction(Emax).upper,
            'bounds_are_outward_MPFR':True,
            'scope':'positive degree-four angular polynomial; expanding diagonal Bianchi I',
            'production_ready':False}


def combine_nominal_path_budget(nominal_h_upper,physical_envelope,*,target_h,backend=None):
    """Triangle inequality for a trusted CE1-C upper and a CE1-D physical box.

    The nominal upper must be an already outward-rounded *binary64* ceiling,
    such as the CE1-C published total_h_upper, not an estimated measured error.
    """
    _need_oracle(backend)
    if physical_envelope.get('status')!='ADMITTED_POSITIVE_EXPANDING_INPUT_BOX':
        raise ValueError('Admitted physical input envelope required')
    if isinstance(nominal_h_upper, (str, bool)):
        raise ValueError('Stored outward-rounded float64 nominal upper required')
    n=float(nominal_h_upper)
    if not math.isfinite(n) or n<0:raise ValueError('Finite nonnegative nominal upper required')
    t=_as_fraction(target_h)
    if t<=0:raise ValueError('Positive target_h required')
    z=Interval(n)+Interval(float(physical_envelope['input_h_upper']))
    meets=z.upper<=_iv_fraction(t).lower
    return {'status':'SCOPED_TARGET_MET' if meets else 'SCOPED_TARGET_NOT_MET',
            'target_h':target_h,'combined_h_upper':z.upper,
            'nominal_h_upper':n,'data_h_upper':physical_envelope['input_h_upper'],
            'assurance':'MPFR outward, under source positivity and all-expanding input box; nominal upper must be independently established',
            'production_ready':False}

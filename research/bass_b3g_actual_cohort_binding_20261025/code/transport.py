"""Conditional finite map bounds; physical and numerical inputs stay distinct."""
import math
import numpy as np
from binding import real


def scalar(x, name, nonnegative=False):
    x = float(real(x, (), name))
    if nonnegative and x < 0: raise ValueError(name+' must be nonnegative')
    return x


def checked(x):
    if not np.all(np.isfinite(x)): raise ValueError('nonfinite/overflow finite bound')
    return x


def product(*values):
    """Refuse a nonzero analytic product rounded to zero or infinity."""
    if any(value==0 for value in values): return 0.
    out=1.
    for value in values:
        prior=out; out=checked(out*value)
        if prior!=0 and value!=0 and out==0:
            raise ValueError('underflow in positive finite bound/product')
    return out


def diagonal_bound(a_hat, e_i):
    a = real(a_hat, (3,), 'a_hat')
    with np.errstate(over='raise', invalid='raise', under='ignore'):
        try: R = checked(np.exp(-a))
        except FloatingPointError as exc: raise ValueError('map overflow') from exc
    if np.any(R==0): raise ValueError('underflow in strictly positive nominal diagonal map')
    if e_i is None: return dict(status='INPUT_DEPENDENT',Rhat_diagonal=R,e_i=None,eR=None)
    e = real(e_i, (3,), 'e_i')
    if np.any(e < 0): raise ValueError('negative diagonal radius')
    with np.errstate(over='raise',invalid='raise',under='ignore'):
        try: terms = checked(R*np.expm1(e))
        except FloatingPointError as exc: raise ValueError('bound overflow') from exc
    if np.any((e>0)&(terms==0)):
        raise ValueError('underflow in positive diagonal error bound/product')
    return dict(status='CONDITIONAL_ON_SUPPLIED_RADII',Rhat_diagonal=R,e_i=e,eR=float(np.max(terms)),component_bounds=terms)


def diagonal_records(a_hat, physical=None, numerical=None, *, provenance=None):
    out = dict(physical=diagonal_bound(a_hat,physical),numerical=diagonal_bound(a_hat,numerical),provenance=provenance)
    out['composed'] = diagonal_bound(a_hat, None if physical is None or numerical is None else checked(np.asarray(physical)+np.asarray(numerical)))
    out['composition_provenance'] = 'TRIANGLE_INEQUALITY_OF_SEPARATELY_SUPPLIED_RADII'
    return out


def determinant_bound(delta_alpha_hat, e_alpha, *, beta_exactly_stf):
    a = scalar(delta_alpha_hat,'delta_alpha_hat')
    if not beta_exactly_stf: raise ValueError('STF beta hypothesis is required')
    try: D = checked(math.exp(checked(-3*a)))
    except OverflowError as exc: raise ValueError('determinant overflow') from exc
    if D==0: raise ValueError('underflow in strictly positive nominal determinant')
    if e_alpha is None: return dict(Dhat=D,bound=None,status='INPUT_DEPENDENT')
    e = scalar(e_alpha,'e_alpha',True)
    try: bound = product(D,checked(math.expm1(checked(3*e))))
    except OverflowError as exc: raise ValueError('determinant bound overflow') from exc
    return dict(Dhat=D,bound=bound,status='CONDITIONAL_ON_SUPPLIED_ALPHA_RADIUS')


def duhamel(T, mhat, eta, M, defect, e0_phys=0., e0_num=0., *, envelope_provenance):
    """All bounds must hold interval-wide, not merely at saved sample points."""
    T=scalar(T,'T',True); mhat=scalar(mhat,'mhat')
    eta=scalar(eta,'eta',True); M=scalar(M,'M',True); defect=scalar(defect,'defect',True)
    e0_phys=scalar(e0_phys,'e0_phys',True); e0_num=scalar(e0_num,'e0_num',True)
    if not envelope_provenance: raise ValueError('supplied interval-wide envelope provenance required')
    m=checked(mhat+eta); z=product(m,T)
    try:
        growth=math.exp(z)
        if growth==0: raise ValueError('underflow in strictly positive Duhamel growth factor')
        numerator=product(T,math.expm1(z)) if z!=0 else None
        integral=T if z==0 else checked(numerator/z)
        if T>0 and integral==0: raise ValueError('underflow in positive Duhamel integral factor')
        phys=checked(product(growth,e0_phys)+product(eta,M,integral))
        num=checked(product(growth,e0_num)+product(defect,integral))
        total=checked(phys+num)
    except OverflowError as exc: raise ValueError('Duhamel bound overflow') from exc
    return dict(status='CONDITIONAL_ON_INTERVAL_WIDE_ENVELOPES',physical_bound=phys,numerical_bound=num,
        total_bound=total,growth=growth,integral_factor=integral,m=m,envelope_provenance=envelope_provenance)

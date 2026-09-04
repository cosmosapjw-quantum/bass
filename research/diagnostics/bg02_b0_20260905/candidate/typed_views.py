"""BG02-B0R1 reference candidate. NOT an admitted production/native interface.

Conventions: metric (-,+,+,+), tau=c*t, positive K=h h nabla n,
q_a=-h_a^b T_bc n^c, kappa_G=8*pi*G/c**4. Geometrical derivatives
are per unit length. Momentum residual has dimension length**(-2).

Inputs to physical_ricci must be components of an algebraic Riemann tensor
in the declared view. This adapter checks the layout, NOT all symmetries,
the Einstein equations, or the metric's signature. Such validation belongs
to the caller's geometry certificate. No silent default view is accepted.
"""
from __future__ import annotations
from enum import Enum
import sympy as s

class CurvatureView(Enum):
    BASS_DERIVATIVE_FIRST = 'BASS_DERIVATIVE_FIRST'
    XACT_RAW = 'XACT_RAW'


def _view(value: CurvatureView) -> None:
    if not isinstance(value, CurvatureView):
        raise ValueError('A typed CurvatureView is required')


def _tensor(value) -> s.ImmutableDenseNDimArray:
    tensor = s.ImmutableDenseNDimArray(value)
    if len(tensor.shape) != 4 or len(set(tensor.shape)) != 1 or tensor.shape[0] < 2:
        raise ValueError('Expected an n by n by n by n all-lower curvature array')
    return tensor


def convert_riemann(value, *, source: CurvatureView, target: CurvatureView):
    """Convert all-lower components, not Ricci or the Einstein tensor."""
    _view(source); _view(target)
    tensor = _tensor(value)
    return tensor if source is target else -tensor


def physical_ricci(value, inverse_metric, *, view: CurvatureView) -> s.ImmutableMatrix:
    """BASS: Ric_ab=g^cd B_cbad. Raw xAct: Ric_ab=g^cd X_acbd."""
    _view(view)
    tensor = _tensor(value)
    inv = s.ImmutableMatrix(inverse_metric)
    n = tensor.shape[0]
    if inv.shape != (n, n):
        raise ValueError('Metric and curvature dimensions differ')
    if inv != inv.T:
        raise ValueError('Inverse metric must be symmetric')
    def component(a, b):
        if view is CurvatureView.BASS_DERIVATIVE_FIRST:
            return s.simplify(sum(inv[c,d]*tensor[c,b,a,d] for c in range(n) for d in range(n)))
        return s.simplify(sum(inv[c,d]*tensor[a,c,b,d] for c in range(n) for d in range(n)))
    return s.ImmutableMatrix(n, n, component)


def _scalar(value) -> s.Expr:
    result = s.sympify(value)
    if not isinstance(result, s.Expr) or result.is_commutative is not True:
        raise ValueError('Expected a commutative scalar component')
    if result.has(s.nan, s.zoo, s.oo, -s.oo):
        raise ValueError('Nonfinite scalar input')
    return result


def momentum_from_positive_k(*, divergence_k, gradient_k, kappa_g, flux) -> s.Expr:
    """Reference component of -h E n; all four inputs are mandatory."""
    div, grad, kg, q = map(_scalar, (divergence_k, gradient_k, kappa_g, flux))
    return s.expand(-div + grad - kg*q)


def class_b_momentum3(*, a_b1, n_b22, n_b23, sigma12, sigma13, kappa_g, flux3) -> s.Expr:
    """Dimensional class-B chart a_B=(a_b1,0,0), n_B a_B=0, D_i K=0.

    This is not by itself certification of the exceptional VI_-1/9 branch.
    Hubble-normalised data require an explicit dimensional adapter first.
    """
    A, n22, n23, s12, s13 = map(_scalar, (a_b1,n_b22,n_b23,sigma12,sigma13))
    carrier = n22*s12 + (n23-3*A)*s13
    return momentum_from_positive_k(divergence_k=carrier,gradient_k=0,kappa_g=kappa_g,flux=flux3)

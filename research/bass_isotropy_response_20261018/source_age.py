"""S6d: source-age cohort composition with frozen birth weights, prescribed geometry.

Dimensionless, non-tilted LRS Bianchi I, x=ln a. A cohort born at u with birth
energy-density increment w (in units of U at birth) and frozen positive rule alpha
contributes U=w e^{-4(x-u)}F_alpha(d), DeltaP=w e^{-4(x-u)}G_alpha(d), d=b(x)-b(u).
This prescribes b(x); it is NOT an Einstein-coupled history. The observed
geometry never re-weights an existing cohort.
"""
from __future__ import annotations
import math
import numpy as np
from scipy.integrate import quad
from angular_balance import lrs_rule, project as project2
from angular_p24 import project as project24

X_BIRTH = (0.0, 0.8)


def b_of_x(x):
    return 0.15*np.sin(2*x)+0.1*x


def db_dx(x):
    return 0.3*np.cos(2*x)+0.1


def j_of_u(u):
    return np.exp(-((u-0.4)/0.2)**2)


def _kernels(d, mu):
    z = mu*mu
    perp, para = np.exp(2*d)*(1-z), np.exp(-4*d)*z
    r = np.sqrt(perp+para)
    return r, (para-perp/2)/r


def rule(b, n, mode):
    mu, q = lrs_rule(float(b), n)
    if mode == 'prior':
        return mu, q
    if mode == 'P2':
        return mu, project2(mu, q).weights
    if mode == 'P24':
        return mu, project24(mu, q).weights
    raise ValueError('S6D_MODE')


def iso_FG(d):
    if d == 0:
        return 1.0, 0.0
    a, c = math.exp(2*d), math.exp(-4*d)
    rr = lambda m: math.sqrt(a*(1-m*m)+c*m*m)
    dd = lambda m: (c*m*m-a*(1-m*m)/2)/rr(m)
    return (quad(rr, 0, 1, epsabs=1e-14, epsrel=1e-12, limit=200)[0],
            quad(dd, 0, 1, epsabs=1e-14, epsrel=1e-12, limit=200)[0])


def cohorts(K):
    du = (X_BIRTH[1]-X_BIRTH[0])/K
    u = X_BIRTH[0]+(np.arange(K)+0.5)*du
    return u, du*j_of_u(u)


def compose(x, u, w, rules):
    """U and DeltaP at x from cohorts born at u<=x with frozen rules [(mu,alpha)]."""
    U = P = 0.0
    for uk, wk, (mu, al) in zip(u, w, rules):
        if uk > x:
            continue
        R, D = _kernels(b_of_x(x)-b_of_x(uk), mu)
        f = math.exp(-4*(x-uk))*wk
        U += f*math.fsum(al*R); P += f*math.fsum(al*D)
    return U, P


def compose_iso(x, u, w):
    U = P = 0.0
    for uk, wk in zip(u, w):
        if uk > x:
            continue
        F, G = iso_FG(float(b_of_x(x)-b_of_x(uk)))
        f = math.exp(-4*(x-uk))*wk
        U += f*F; P += f*G
    return U, P


def identity_residual(x, u, w, rules, h=1e-20):
    """Complex-step dU/dx+4U+2b'(x)DeltaP for the cohort sum at x between births."""
    xc = x+1j*h
    Uc = 0j
    for uk, wk, (mu, al) in zip(u, w, rules):
        if uk > x:
            continue
        z = mu*mu
        d = b_of_x(xc)-b_of_x(uk)
        R = np.sqrt(np.exp(2*d)*(1-z)+np.exp(-4*d)*z)
        Uc += np.exp(-4*(xc-uk))*wk*np.sum(al*R)
    dU = Uc.imag/h
    U, P = compose(x, u, w, rules)
    return dU+4*U+2*db_dx(x)*P, U


def leading_p4(x, u, w, rules):
    """(36/35) sum w e^{-4(x-u)} M4 d: S3 first-order source-age bias for M2=0 rules."""
    s = 0.0
    for uk, wk, (mu, al) in zip(u, w, rules):
        if uk > x:
            continue
        m4 = math.fsum(al*(35*mu**4-30*mu**2+3)/8)
        s += wk*math.exp(-4*(x-uk))*m4*(b_of_x(x)-b_of_x(uk))
    return 36/35*s

"""
PR-25 · 물리량 재구성 (Hubble 정규화 해 -> 관측 가능량).

    H'/H = -(1+q)              -> H(tau)
    dt/dtau = 1/H              -> t(tau)   (quadrature)
    l'/l = 1                   -> l = l_0 e^tau
    sigma_ab = H Sigma_ab , n_ab = H N_ab , a_a = H A_a
    Gamma = (1-V^2)^{-1/2}     <- 여기서**만** 계산 (진화식에는 절대 안 넣는다)

★ shear 스칼라 기호 충돌 (conventions.ShearScalar):
    Sigma_WE    = sqrt((1/6) Sigma_ab Sigma^ab)
    Sigma_theta = sigma/theta = Sigma_WE / sqrt3
  관측 문헌은 후자를 쓴다. 반드시 타입으로 구분한다.
"""
from __future__ import annotations

import jax.numpy as jnp
import numpy as np

from bianchi.conventions import ShearScalar, SQRT3


def integrate_H(tau, q, H0=1.0):
    """H(tau) = H0 exp(-int (1+q) dtau).  사다리꼴 적분."""
    tau = np.asarray(tau); q = np.asarray(q)
    integrand = 1.0 + q
    cum = np.concatenate([[0.0], np.cumsum(0.5*(integrand[1:]+integrand[:-1])
                                           * np.diff(tau))])
    return H0 * np.exp(-cum)


def cosmic_time(tau, H, t0=0.0):
    """t(tau) = t0 + int dtau / H."""
    tau = np.asarray(tau); H = np.asarray(H)
    inv = 1.0 / H
    return t0 + np.concatenate([[0.0], np.cumsum(0.5*(inv[1:]+inv[:-1])
                                                 * np.diff(tau))])


def mean_scale_factor(tau, l0=1.0):
    """l = l0 e^tau  (평균 스케일; ell'/ell = 1)."""
    return l0 * np.exp(np.asarray(tau))


def directional_scale_factors(tau, Sigma_diag, l0=1.0):
    """a_i(t): d ln a_i/dtau = 1 + Sigma_i  (대각 프레임)."""
    tau = np.asarray(tau); S = np.asarray(Sigma_diag)   # (T, 3)
    out = []
    for i in range(3):
        integ = 1.0 + S[:, i]
        cum = np.concatenate([[0.0], np.cumsum(0.5*(integ[1:]+integ[:-1])
                                               * np.diff(tau))])
        out.append(l0 * np.exp(cum))
    return np.stack(out, axis=-1)


def shear_scalar(Sigma_ab_or_Sigma2, kind="WE"):
    """Sigma 스칼라를 타입 붙여 반환."""
    x = np.asarray(Sigma_ab_or_Sigma2)
    Sigma2 = float(np.trace(x @ x) / 6.0) if x.ndim == 2 else float(x)
    return ShearScalar(float(np.sqrt(max(Sigma2, 0.0))), "WE").to(kind)


def dimensionful(H, Sigma, N, A):
    """정규화 -> 차원량."""
    return dict(sigma=H*np.asarray(Sigma), n=H*np.asarray(N), a=H*np.asarray(A))


def lorentz_factor(V2):
    """Gamma = (1-V^2)^{-1/2}. V->1 에서 발산하므로 log 로도 제공."""
    V2 = np.asarray(V2)
    one_minus = np.maximum(1.0 - V2, np.finfo(float).tiny)
    return dict(Gamma=one_minus**-0.5, log_Gamma=-0.5*np.log(one_minus))


def bbn_expansion_anisotropy(Sigma2_at_bbn):
    """BBN 시점 이방성 -> 유효 팽창률 증가 -> Delta N_eff 등가.

    H^2 = H_iso^2 (1 + Sigma^2/(1-Sigma^2)) 근사에서
      Delta N_eff ~ (43/7) * Sigma^2 / (1 - Sigma^2)  (복사지배 근사)
    """
    S2 = float(Sigma2_at_bbn)
    return (43.0/7.0) * S2 / max(1e-12, 1.0 - S2)


def observables(tau, states, aux_fn, args, H0=1.0):
    """표준 출력 묶음."""
    q = np.array([float(aux_fn(s, args)["q"]) for s in states])
    S2 = np.array([float(aux_fn(s, args)["Sigma2"]) for s in states])
    Om = np.array([float(aux_fn(s, args)["Omega"]) for s in states])
    H = integrate_H(tau, q, H0)
    t = cosmic_time(tau, H)
    return dict(tau=np.asarray(tau), q=q, Sigma2=S2, Omega=Om, H=H, t=t,
                ell=mean_scale_factor(tau),
                Sigma_WE=np.sqrt(np.maximum(S2, 0)),
                Sigma_theta=np.sqrt(np.maximum(S2, 0))/SQRT3)

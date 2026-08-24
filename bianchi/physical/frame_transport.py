"""
PR-29 · 삼각대(triad) 전송과 방향 스케일인자.

불변기저 공간 여벡터 E^α_i (좌표기저 <-> 직교틀 사상) 는 (audit/d_transport.py 검증):

    dE/dτ = (I + Σ + Ω) E ,     Ω_ab = eps_abc R^c   (ENGINE/generator R)
                                             = -W_ab, W = conventions.rotation_matrix
    tr(I + Σ + Ω) = 3        ->   det E = e^{3τ}     (부피 = ℓ^3 = e^{3τ})

부호 판정 (d_transport): +Ω 는 잔차 1.1e-9, -Ω 는 17.0 으로 실패.
좌표계량 h_ij = (E^T E)_ij 재구성과 방향 스케일인자 a_i 는 여기서 나온다.

★ 회전 규약: 여기의 Ω 는 프레임 접속에서 직접 뽑은 generator 형(= eps R).
  conventions.rotation_matrix 는 commutator 형 W = -eps R 을 준다.  둘의 관계는
  Ω = -W 이며, 이 모듈은 전송식 dE/dτ = (I + Σ - W)E 로 W 를 써서 구현한다
  (부호 혼용 사고 방지 — v1.1/v1.3 교훈).
"""
from __future__ import annotations

import jax
import jax.numpy as jnp

from bianchi.conventions import rotation_matrix, EPS3_J


def transport_generator(Sigma, R):
    """전송 생성자 M = I + Σ + Ω,  Ω = -W = +eps R.

    Σ: (3,3) trace-free 대칭 (Hubble 정규화),  R: (3,) 각속도.
    """
    Sigma = jnp.asarray(Sigma)
    W = rotation_matrix(R)                       # commutator: W = -eps R
    Omega = -W                                   # generator:  Ω = +eps R
    return jnp.eye(3) + Sigma + Omega


def dtriad_dtau(E, Sigma, R):
    """dE/dτ = (I + Σ + Ω) E."""
    return transport_generator(Sigma, R) @ jnp.asarray(E)


def integrate_triad(taus, Sigma_of, R_of, E0=None):
    """τ 격자에서 삼각대 E(τ) 를 RK4 로 적분.

    Sigma_of(i), R_of(i): 격자점 i 의 (Σ, R) 반환 콜백.
    반환: E 스택 (len(taus), 3, 3),  det E (부피).
    """
    import numpy as np
    taus = np.asarray(taus, float)
    E = np.eye(3) if E0 is None else np.asarray(E0, float)
    out = [E.copy()]
    for i in range(len(taus) - 1):
        h = taus[i + 1] - taus[i]

        def f(Emat, j):
            return np.asarray(transport_generator(Sigma_of(j), R_of(j))) @ Emat
        k1 = f(E, i)
        k2 = f(E + 0.5 * h * k1, i)
        k3 = f(E + 0.5 * h * k2, i)
        k4 = f(E + h * k3, i + 1)
        E = E + h / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)
        out.append(E.copy())
    E_stack = np.stack(out)
    return E_stack, np.linalg.det(E_stack)


def spatial_metric(E):
    """좌표기저 3-계량 h_ij = (E^T E)_ij  (직교틀 E 로부터)."""
    E = jnp.asarray(E)
    return E.T @ E


def directional_scale_factors_diag(taus, Sigma_diag, l0=1.0):
    """대각 게이지(Σ = diag(Σ1,Σ2,Σ3), R=0) 의 방향 스케일인자.

    d ln a_i / dτ = 1 + Σ_i   ->   a_i = ℓ0 exp(∫ (1+Σ_i) dτ).
    기존 physical._legacy.directional_scale_factors 와 동일 (교차검증용).
    """
    import numpy as np
    taus = np.asarray(taus, float); S = np.asarray(Sigma_diag, float)
    out = []
    for i in range(3):
        integ = 1.0 + S[:, i]
        cum = np.concatenate([[0.0], np.cumsum(0.5 * (integ[1:] + integ[:-1])
                                              * np.diff(taus))])
        out.append(l0 * np.exp(cum))
    return np.stack(out, axis=-1)


def trace_identity_residual(Sigma, R):
    """tr(I + Σ + Ω) - 3  (=0 항등적: Σ trace-free, Ω 반대칭)."""
    return float(jnp.trace(transport_generator(Sigma, R)) - 3.0)

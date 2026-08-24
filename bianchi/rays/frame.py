"""
PR-43/45 지원 · 프레임 접속과 3차원 접속의 이중축약 P^a.

프레임 접속 블록 (audit/d_transport.py 로 검증, 잔차 ≤ 6.7e-16):
    Gamma^0_00 = 0
    Gamma^0_ab = Gamma^a_0b = H δ_ab + σ_ab           (외재곡률 K)
    Gamma^a_b0 = -Ω_ab ,   Ω_ab = eps_abc R^c          (generator R)
    Gamma^a_bc = 3차원 Levi-Civita 접속 (구조상수에서)
    나머지 (0 이 둘 이상, Gamma^0_0a 등) = 0  (측지 법선 + 비회전)

여기서 σ, N, A 는 **차원량** (Hubble 정규화가 아님).  광선 적분은 우주시간 t 로
하므로 차원량을 쓴다; 정규화 해로부터의 복원은 physical.chart 참조.
"""
from __future__ import annotations

import jax.numpy as jnp

from bianchi.conventions import EPS3_J
from bianchi.charts.general import _connection as _connection3


def P_double(N, A, x):
    """이중축약 P^a = ^3Gamma^a_{bc} x^b x^c = A^a|x|² - (A·x)x^a + eps^a_bc x^b (Nx)^c.

    (v1.1 검증; d_transport/r5d 에서 광자·질량입자 전송에 공통으로 등장.)
    """
    N = jnp.asarray(N); A = jnp.asarray(A); x = jnp.asarray(x)
    x2 = x @ x
    return A * x2 - (A @ x) * x + jnp.einsum("abc,b,c->a", EPS3_J, x, N @ x)


def frame_connection(H, sigma, N, A, R):
    """전체 4차원 프레임 접속 Gamma^a_{bc} (c = 미분 슬롯 마지막) 를 조립.

    반환 shape (4,4,4):  G[a,b,c] = Gamma^a_{bc}.
    """
    H = jnp.asarray(H); sigma = jnp.asarray(sigma)
    N = jnp.asarray(N); A = jnp.asarray(A); R = jnp.asarray(R)
    K = H * jnp.eye(3) + sigma                       # 외재곡률
    Omega = jnp.einsum("abc,c->ab", EPS3_J, R)       # generator Ω = eps R
    C3 = _connection3(N, A)                          # _connection: 미분슬롯=**가운데** 지표

    G = jnp.zeros((4, 4, 4))
    # Gamma^0_ab = K
    G = G.at[0, 1:, 1:].set(K)
    # Gamma^a_0b = K
    G = G.at[1:, 0, 1:].set(K)
    # Gamma^a_b0 = -Omega
    G = G.at[1:, 1:, 0].set(-Omega)
    # spatial block:  _connection 은 [a,c,b]=³Γ^a_{bc} (미분슬롯 가운데) 를 주므로
    # 마지막 두 지표를 바꿔 G[a,b,c]=³Γ^a_{bc} (미분슬롯=마지막) 규약으로 맞춘다.
    # (P_double 의 대칭축약 x^b x^c 는 이 순서에 무관 — v2.0 에서야 비대칭 소비자
    #  physical.congruence 가 등장해 드러난 규약 불일치. audit/d_vorticity a∥v 로 확정.)
    G = G.at[1:, 1:, 1:].set(jnp.swapaxes(C3, 1, 2))
    return G

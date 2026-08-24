"""
PR-43 · 널 측지선 전송과 방향 의존 적색이동.

법선 프레임에서 광자 4-운동량을 (E, n̂) 로 분해:  p = E(e_0 + n̂^a e_a),  |n̂| = 1.
검증된 전송식 (audit/d_transport.py, D13; v1.3 회전부호 정정 +(R×P)):

    dE/dt   = -E ( H + σ_ab n̂^a n̂^b )
    dP^a/dt = -(H δ + σ)^a_b P^b + (R × P)^a - E · 𝒫^a(n̂)
    d n̂^a/dt = -(σ n̂ - (n̂·σ·n̂) n̂)^a + (R × n̂)^a - [𝒫(n̂) - (n̂·𝒫(n̂)) n̂]^a
    𝒫^a(x) = A^a|x|² - (A·x)x^a + eps^a_bc x^b (Nx)^c

적색이동:  1 + z = E_emit / E_obs.  관측점(t0)에서 E=E_obs=1 로 두고 과거로
  역적분(t_end < t0)하면 E 가 증가하며, 그 지점의 z = E - 1 이다 (z ≥ 0 단조).

★ 여기의 σ, N, A, R, H 는 **차원량** (우주시간 t).  Hubble 정규화 해로부터의
  복원은 physical.chart / frame_transport 참조.
★ 자유흐름 종족(PR-38)의 질량입자 특성곡선과 **같은 전송 코드**를 쓴다 (설계 D4).
"""
from __future__ import annotations

import numpy as np
import jax.numpy as jnp

from bianchi.conventions import EPS3
from bianchi.rays.frame import P_double


def photon_rhs(E, nhat, H, sigma, N, A, R):
    """(dE/dt, dn̂/dt).  nhat 는 단위벡터 (|n̂|=1 보존)."""
    sigma = np.asarray(sigma); N = np.asarray(N); A = np.asarray(A); R = np.asarray(R)
    nhat = np.asarray(nhat, float)
    Sn = sigma @ nhat
    nSn = nhat @ Sn
    P = np.asarray(P_double(N, A, nhat))
    dE = -E * (H + nSn)
    RxN = np.cross(R, nhat)
    dn = -(Sn - nSn * nhat) + RxN - (P - (nhat @ P) * nhat)
    return dE, dn


def momentum_rhs(E, P, H, sigma, N, A, R, mass=0.0):
    """일반 4-운동량 전송 dP^a/dt (질량 입자 포함; 광자는 mass=0, E=|P|).

    dP^a/dt = -(H δ + σ)^a_b P^b + (R × P)^a - 𝒫^a(P)/E
    dE/dt   = -(H|P|² + σ_ab P^a P^b)/E
    """
    P = np.asarray(P, float); sigma = np.asarray(sigma)
    N = np.asarray(N); A = np.asarray(A); R = np.asarray(R)
    K = H * np.eye(3) + sigma
    Pd = np.asarray(P_double(N, A, P))
    dP = -(K @ P) + np.cross(R, P) - Pd / E
    dE = -(H * (P @ P) + P @ (sigma @ P)) / E
    return dE, dP


def trace_ray_diag_bianchi(model, t0, t_end, nsteps=4000, backward=None):
    """대각 Bianchi 배경에서 광선을 적분해 z, n̂(t), a_i(t) 를 반환.

    방향은 t0 -> t_end 로 자연스럽게 결정된다 (과거 광선이면 t_end < t0 로 호출).
    model: dict(H0, Sigma0=(3,), Omega0, gamma, nhat).  진공+대각 shear+유체 배경을
    우주시간으로 함께 적분(RK4)한다.  일반 유형·비대각으로의 확장은 PR-44/솔버에서
    physical.chart 로 복원한 배경을 콜백으로 넘기면 된다.

    반환: 히스토리 리스트 (z, nhat, lna(3,), t, H).
    """
    g = model["gamma"]
    nh = np.asarray(model["nhat"], float); nh = nh / np.linalg.norm(nh)
    st = dict(H=model["H0"], sig=np.asarray(model["Sigma0"], float) * model["H0"],
              rho=3 * model["H0"] ** 2 * model["Omega0"], lna=np.zeros(3),
              E=1.0, nh=nh, t=t0)
    dt = (t_end - t0) / nsteps           # 부호는 t0->t_end 방향이 결정
    hist = []
    Z3 = np.zeros((3, 3)); z3 = np.zeros(3)

    def deriv(s):
        H, sig, rho = s["H"], s["sig"], s["rho"]
        S = np.diag(sig)
        dE, dn = photon_rhs(s["E"], s["nh"], H, S, Z3, z3, z3)
        Hd = -H ** 2 - (sig @ sig) / 3.0 - (rho + 3 * (g - 1) * rho) / 6.0
        return dict(E=dE, nh=dn, H=Hd, sig=-3 * H * sig, rho=-3 * H * g * rho,
                    lna=H + sig, t=1.0)

    for i in range(nsteps):
        d = deriv(st)
        for k in ("E", "H", "rho", "t"):
            st[k] = st[k] + dt * d[k]
        st["nh"] = st["nh"] + dt * d["nh"]; st["nh"] /= np.linalg.norm(st["nh"])
        st["sig"] = st["sig"] + dt * d["sig"]
        st["lna"] = st["lna"] + dt * d["lna"]
        if st["H"] <= 0 or not np.isfinite(st["H"]):
            break
        if i % max(1, nsteps // 400) == 0:
            hist.append(dict(z=st["E"] - 1.0, nhat=st["nh"].copy(),
                             lna=st["lna"].copy(), t=st["t"], H=st["H"]))
    return hist

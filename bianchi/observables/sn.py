"""
PR-48 · Ia 초신성 Hubble diagram 의 방향 의존 (이방 우주).

거리계수  μ(z, n̂) = 5 log₁₀(d_L[Mpc]) + 25,   d_L(z,n̂) = (1+z) ∫₀^z c/H_∥(n̂,z') dz'.

이방 배경의 두 각인:
  • **사중극(ℓ=2)** — shear.  시선 팽창률 H_∥(n̂)=H(1+Σ_ab n̂n̂) 가 방향마다 달라
    Hubble diagram 잔차에 Σ 비례 사중극을 남긴다 (Σ→0 이면 소멸).
  • **쌍극(ℓ=1)** — 관측자 고유속도(bulk flow).  δz = -(v·n̂)/c 로 저-z 에서
    δμ ≈ -(5/ln10)(v·n̂/c)/z (∝1/z, 저-z 지배).  PR-42 CMB 쌍극과 같은 v.

Pantheon+ 형식(zHD, μ, μ_err, RA, Dec)으로 방향 표본을 내보낸다.

FLRW 극한(Σ=0, v=0): 등방 μ(z), 모든 다극 진폭 0.
"""
from __future__ import annotations

import numpy as np

from bianchi.physical import units as U
from bianchi.observables import distances as D
from bianchi.optional_dependencies import require_optional

quad = require_optional("scipy.integrate", feature=__name__, dependency="scipy").quad

_5_OVER_LN10 = 5.0 / np.log(10.0)


# ---------------------------------------------------------------- 기본 거리계수
def distance_modulus(dL_mpc):
    """μ = 5 log₁₀(d_L/Mpc) + 25."""
    return 5.0 * np.log10(np.asarray(dL_mpc, float)) + 25.0


def luminosity_distance_iso(z, H0=67.4, Om=0.315, Or=9.24e-5):
    """등방 d_L(z) = (1+z) D_C(z)  [Mpc]."""
    DC = D.comoving_distance(z, H0=H0, Om=Om, Or=Or)
    return (1.0 + z) * DC


def luminosity_distance_directional(z, nhat, Sigma, H0=67.4, Om=0.315, Or=9.24e-5):
    """방향 d_L(z,n̂) = (1+z) ∫₀^z c/H_∥ dz',  H_∥=H(z)(1+Σ_ab n̂n̂)  (Σ 상수 근사).

    Σ 는 오늘의 정규화 전단(선두 이방성).  z-의존 Σ(z) 가 필요하면 Sigma_of(z) 콜백.
    """
    nhat = np.asarray(nhat, float); nhat = nhat / np.linalg.norm(nhat)
    Sig = np.asarray(Sigma, float)
    proj = nhat @ Sig @ nhat

    def integrand(zz):
        Hz = D.flrw_hubble(zz, H0, Om, Or) * (1.0 + proj)
        return U.C_LIGHT_KM_S / Hz
    DC, _ = quad(integrand, 0.0, float(z), limit=200)
    return (1.0 + z) * DC


def mu_directional(z, nhat, Sigma, **kw):
    """μ(z,n̂)  (shear 사중극 포함)."""
    return distance_modulus(luminosity_distance_directional(z, nhat, Sigma, **kw))


# ---------------------------------------------------------------- 쌍극 (고유속도)
def peculiar_velocity_residual(z, v, nhat):
    """관측자 고유속도 v 로 인한 저-z 쌍극 잔차 δμ ≈ -(5/ln10)(v·n̂/c)/z.

    v 는 광속 단위가 아닌 실제 속도라면 v/c 로; 여기 v 는 **광속 단위(β)** 로 받는다.
    (v·n̂>0: 관측자가 해당 방향으로 이동→청색편이→가까워 보임→μ 감소.)
    """
    nhat = np.asarray(nhat, float); nhat = nhat / np.linalg.norm(nhat)
    beta_par = np.asarray(v, float) @ nhat            # β·n̂  (무차원)
    return -_5_OVER_LN10 * beta_par / z


# ---------------------------------------------------------------- Hubble map 분해
def hubble_map(zs, nhats, Sigma, v=None, H0=67.4, Om=0.315, Or=9.24e-5):
    """방향·적색이동 표본의 μ 잔차 (등방 대비).  잔차 = μ(z,n̂) - μ_iso(z) + δμ_pec.

    zs: (M,) 또는 스칼라, nhats: (K,3).  반환 (M,K) 잔차 (스칼라 z 면 (K,)).
    """
    zs = np.atleast_1d(np.asarray(zs, float)); nhats = np.atleast_2d(np.asarray(nhats, float))
    out = np.zeros((zs.size, nhats.shape[0]))
    for i, z in enumerate(zs):
        mu_iso = distance_modulus(luminosity_distance_iso(z, H0, Om, Or))
        for j, n in enumerate(nhats):
            r = mu_directional(z, n, Sigma, H0=H0, Om=Om, Or=Or) - mu_iso
            if v is not None:
                r += peculiar_velocity_residual(z, v, n)
            out[i, j] = r
    return out[0] if out.shape[0] == 1 else out


def decompose_dipole_quadrupole(z, Sigma, v=None, H0=67.4, Om=0.315, Or=9.24e-5,
                                n_theta=16, n_phi=32):
    """단일 z 껍질에서 μ 잔차를 구면 분해해 C₁(쌍극)·C₂(사중극) 파워 반환.

    Σ→0, v=0 → 모두 0.  v≠0 → C₁>0,  Σ≠0 → C₂>0.
    """
    th = np.linspace(0, np.pi, n_theta); ph = np.linspace(0, 2 * np.pi, n_phi, endpoint=False)
    T, P = np.meshgrid(th, ph, indexing="ij")
    nx = np.sin(T) * np.cos(P); ny = np.sin(T) * np.sin(P); nz = np.cos(T)
    nhats = np.stack([nx.ravel(), ny.ravel(), nz.ravel()], axis=-1)
    resid = hubble_map(z, nhats, Sigma, v, H0, Om, Or).reshape(T.shape)
    special = require_optional(
        "scipy.special",
        feature=f"{__name__}.decompose_dipole_quadrupole",
        dependency="scipy",
    )
    if hasattr(special, "sph_harm_y"):
        Y = lambda l, m: special.sph_harm_y(l, m, T, P)
    else:
        Y = lambda l, m: special.sph_harm(m, l, P, T)
    dOm = np.sin(T) * (th[1] - th[0]) * (ph[1] - ph[0])
    mono = np.sum(resid * dOm) / np.sum(dOm)
    r0 = resid - mono
    Cl = {}
    for l in (1, 2):
        Cl[l] = float(sum(abs(np.sum(r0 * np.conj(Y(l, m)) * dOm)) ** 2
                          for m in range(-l, l + 1)) / (2 * l + 1))
    return dict(C1=Cl[1], C2=Cl[2], monopole=float(mono))


# ---------------------------------------------------------------- Pantheon+ 내보내기
def to_pantheon_format(zs, ras, decs, Sigma, v=None, sigma_mu=0.1,
                       H0=67.4, Om=0.315, Or=9.24e-5):
    """방향 표본을 Pantheon+ 유사 레코드로.

    입력 (zHD, RA[deg], Dec[deg]) 표본과 배경 (Σ, v) 로 μ 와 오차를 채운다.
    반환: numpy structured array (zHD, MU, MU_ERR, RA, DEC).
    """
    zs = np.atleast_1d(np.asarray(zs, float))
    ras = np.atleast_1d(np.asarray(ras, float)); decs = np.atleast_1d(np.asarray(decs, float))
    ra = np.deg2rad(ras); dec = np.deg2rad(decs)
    nx = np.cos(dec) * np.cos(ra); ny = np.cos(dec) * np.sin(ra); nz = np.sin(dec)
    rec = np.zeros(zs.size, dtype=[("zHD", "f8"), ("MU", "f8"), ("MU_ERR", "f8"),
                                   ("RA", "f8"), ("DEC", "f8")])
    for i, z in enumerate(zs):
        n = np.array([nx[i], ny[i], nz[i]])
        mu = mu_directional(z, n, Sigma, H0=H0, Om=Om, Or=Or)
        if v is not None:
            mu += peculiar_velocity_residual(z, v, n)
        rec[i] = (z, mu, sigma_mu, ras[i], decs[i])
    return rec


def sky_to_unit(ra_deg, dec_deg):
    """적경/적위(deg) → 단위벡터 n̂ (검증·표본 생성용)."""
    ra = np.deg2rad(ra_deg); dec = np.deg2rad(dec_deg)
    return np.array([np.cos(dec) * np.cos(ra), np.cos(dec) * np.sin(ra), np.sin(dec)])

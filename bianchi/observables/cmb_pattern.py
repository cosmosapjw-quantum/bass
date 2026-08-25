"""
PR-46 · CMB 이방 온도 패턴 ΔT/T(n̂).

★ 이것은 **섭동이 아니라 배경 이방 팽창의 적색이동 패턴**이다 (설계 §0.1-2).
  최종산란면까지의 광선 적분(PR-43)에서 방향마다 다른 적색이동이 나오고,
  그 방향 의존이 CMB 온도의 이방 패턴을 만든다.  Planck 의 Bianchi VII_h 탐색이
  쓰는 것이 바로 이 배경 템플릿이다.

관측 온도:  T_obs(n̂) = T_emit / (1 + z(n̂)).  등방 성분을 빼면
  ΔT/T(n̂) = [⟨1+z⟩ - (1+z(n̂))] / (1+z(n̂)) ≈ -δz(n̂)/(1+z̄).

healpy 없이 직접 구면조화 분해 (ℓ ≤ 소수).  Bianchi I -> 순수 사중극(ℓ=2),
VII_h -> 나선 패턴 (N_× 회전이 ℓ=1 쌍극에 나선을 얹음).

함정 (설계 §6-4): VII_h 의 "오늘의 Σ" 와 "CMB 패턴 진폭" 은 교환 불가 — 나선은
N_× 회전이 만들며 Σ_0 가 극소여도 큰 패턴을 남긴다.
"""
from __future__ import annotations

import numpy as np

from bianchi import backend
from bianchi.backend_policy import BackendPolicy, select_backend
from bianchi.optional_dependencies import require_optional


def _direction_grid(n_theta=24, n_phi=48):
    """구면 방향 격자 (θ,φ) 와 단위벡터 n̂, 사다리꼴 가중치."""
    th = np.linspace(0, np.pi, n_theta)
    ph = np.linspace(0, 2 * np.pi, n_phi, endpoint=False)
    T, P = np.meshgrid(th, ph, indexing="ij")
    nx = np.sin(T) * np.cos(P); ny = np.sin(T) * np.sin(P); nz = np.cos(T)
    nhat = np.stack([nx, ny, nz], axis=-1)        # (nth, nph, 3)
    w = np.sin(T)                                 # 구면 요소 ∝ sinθ
    return th, ph, nhat, w


def temperature_pattern_diag_bianchi(model, t0, t_lss, n_theta=24, n_phi=48,
                                     nsteps=2000, force_python=False, *, policy=None):
    """대각 Bianchi 배경에서 ΔT/T(n̂) 패턴을 계산.

    각 방향으로 관측 -> 최종산란(t_lss) 광선을 적분해 z(n̂) 를 얻고,
    등방 평균을 빼서 ΔT/T = (⟨1+z⟩ - (1+z))/(1+z) 를 만든다.
    반환: dict(nhat, dT_over_T, z, quadrupole_amplitude).
    """
    selected = select_backend(
        "observable.cmb_pattern_diag",
        policy=policy,
        force_python=force_python,
    )
    child_policy = (BackendPolicy.RUST_REQUIRED if selected.uses_rust
                    else BackendPolicy.PYTHON_ORACLE)
    th, ph, nhat, w = _direction_grid(n_theta, n_phi)
    shape = nhat.shape[:2]
    # ★ R3 (성능): 방향마다 Python 루프로 광선을 적분했다 (10×16 방향 × 400 스텝이
    #   회귀시험 하나에 65 초).  같은 계산을 이미 있는 **배치 백엔드**로 넘긴다
    #   (Rust 가 있으면 Rust, 없으면 같은 Python 루프로 폴백 — 값은 동일).
    z = np.asarray(backend.ray_final_z_batch(
        model, nhat.reshape(-1, 3), t0, t_lss, nsteps=nsteps,
        policy=child_policy)).reshape(shape)
    one_pz = 1.0 + z
    # 구면 가중 평균 (등방 성분).  w 는 이미 (nth, nph) 2D (sinθ 격자).
    W = np.broadcast_to(w, shape)
    mean_one_pz = np.nansum(one_pz * W) / np.nansum(W)
    dT = (mean_one_pz - one_pz) / one_pz          # ΔT/T
    return dict(nhat=nhat, dT_over_T=dT, z=z, theta=th, phi=ph, weight=w,
                mean_one_plus_z=mean_one_pz)


def multipole_amplitudes(pattern, lmax=4):
    """ΔT/T 패턴을 실수 구면조화로 분해해 각 ℓ 의 파워 C_ℓ (진폭²) 를 반환.

    직접 적분 (healpy 불요):  a_lm = ∫ ΔT/T Y_lm* dΩ,  C_ℓ = (1/(2ℓ+1)) Σ_m |a_lm|².
    """
    special = require_optional(
        "scipy.special", feature=f"{__name__}.multipole_amplitudes", dependency="scipy"
    )
    if hasattr(special, "sph_harm_y"):
        def _Y(l, m, T, P):
            return special.sph_harm_y(l, m, T, P)  # (n, m, theta, phi)
    else:                                          # 구버전 scipy 폴백
        def _Y(l, m, T, P):
            return special.sph_harm(m, l, P, T)    # (m, n, phi, theta)
    dT = pattern["dT_over_T"]; th = pattern["theta"]; ph = pattern["phi"]
    T, P = np.meshgrid(th, ph, indexing="ij")
    w = np.sin(T)
    dphi = (ph[1] - ph[0]) if len(ph) > 1 else 2 * np.pi
    dth = (th[1] - th[0]) if len(th) > 1 else np.pi
    dOmega = w * dth * dphi
    Cl = {}
    for l in range(lmax + 1):
        power = 0.0
        for m in range(-l, l + 1):
            Ylm = _Y(l, m, T, P)
            a_lm = np.sum(dT * np.conj(Ylm) * dOmega)
            power += abs(a_lm) ** 2
        Cl[l] = power / (2 * l + 1)
    return Cl


def quadrupole_dominance(pattern):
    """Bianchi I 는 순수 사중극: C_2 >> C_1, C_3.  지표 반환."""
    Cl = multipole_amplitudes(pattern, lmax=4)
    total = sum(Cl[l] for l in range(1, 5)) + 1e-300
    return dict(C=Cl, quadrupole_fraction=Cl[2] / total)


def shear_from_planck_limit(sigma_over_H_limit=7.6e-10):
    """Planck VII_h 제한 (ω/H)_0 < 7.6e-10 (95% CL) 을 shear 상한 안내로.

    참고: Planck 2015 XVIII.  vorticity 와 shear 는 유형별로 다르게 묶이므로
    직접 번역하지 말고 (설계 §6-4) 안내값으로만 사용.
    """
    return dict(vorticity_over_H=sigma_over_H_limit,
                note="Planck 2015 XVIII Bianchi VII_h; shear 는 유형별 별도")

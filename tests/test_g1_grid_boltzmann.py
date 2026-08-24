"""
G1 · **운동량격자 볼츠만 (비-PSTF 절편 1)** (71차) — 계획 삼중 게이트.

  (i) 충돌 off + 이방 a: J-모멘트 ≡ J_moment 오라클 — **동일 측도·격자**라
      기계 0 (자유흐름 팔 = 항등의 강한 형태).
  (ii) PSTF 계층 절단 대조: 격자 (정확) vs 계층 (l_max 절단) — 절단오차 이내.
  (iii) Thomson 감쇠율 ≡ ν(1−k_l), k_l = rustcore 핵 고유값 (l=1: 1, l=2: 0.9)
      — 비-PSTF 직접구적의 심판.  + 수 보존 기계 · 양수성 보존.
LIMITATIONS 게이트: 이방배경 충돌 재맵·Strang 오차 = G2 (여기선 분할오차 0).
"""
import numpy as np
import pytest

pytest.importorskip("bianchi_rustcore")

from bianchi.matter import grid_boltzmann as GB
from bianchi.matter.hierarchy import J_moment


def test_gate_i_freestream_moments_machine_exact():
    """★★ (i): 충돌 off — 격자 모멘트 ≡ 오라클 (이방 a, 여러 (l,i))."""
    F = GB.initial_grid()
    for a in (np.array([1.3, 0.8, 1.1]), np.array([2.0, 0.5, 1.4])):
        for l, i in ((0, 0), (1, 0), (2, 0), (2, 1), (3, 1), (4, 0)):
            g = GB.moments_from_grid(F, a, l, i)
            o = J_moment(a, 0.0, l, i, backend="python")
            assert np.max(np.abs(np.asarray(g) - np.asarray(o))) <= 1e-14


def test_gate_ii_hierarchy_truncation_crosscheck():
    """★ (ii): 격자 (정확) vs 계층 (절단 l_max=5) — Kasner σ 배경, l=2 대조."""
    from bianchi.matter import pstf_coeff as PC
    from bianchi.matter.hierarchy_coeff import hierarchy_rhs_coeff
    Sp, Sm = 0.2, -0.12
    sig = np.array([-2*Sp, Sp + np.sqrt(3)*Sm, Sp - np.sqrt(3)*Sm])
    s5 = PC.to_ccoef(np.diag(sig), 2)
    lmax, tau, ns = 5, 0.5, 800
    F = GB.initial_grid()
    a0 = np.ones(3)
    Jc = {(l, 0): (np.atleast_1d(PC.to_ccoef(
        GB.moments_from_grid(F, a0, l, 0), l)) if l else
        np.array([GB.moments_from_grid(F, a0, 0, 0)]))
        for l in range(lmax + 1)}

    class A(dict):
        def get(s, k, d=None):
            l, i = k
            return Jc[(l, 0)] if l <= lmax else np.zeros(2*l + 1)
        __getitem__ = get

    h = tau / ns
    for _ in range(ns):
        d = {l: hierarchy_rhs_coeff(A(), 1.0, s5, l, 0)
             for l in range(lmax + 1)}
        for l in range(lmax + 1):                      # RK1 충분 (대조 성격)
            Jc[(l, 0)] = Jc[(l, 0)] + h * d[l]
    aT = np.exp((1.0 + sig) * tau)
    gJ2 = PC.to_ccoef(GB.moments_from_grid(F, aT, 2, 0), 2)
    hJ2 = Jc[(2, 0)]
    rel = np.abs(gJ2 - hJ2).max() / max(np.abs(gJ2).max(), 1e-300)
    assert rel <= 5e-3, rel                            # RK1+절단 수준 (실측 기록)


def test_gate_iii_thomson_rates_conservation_positivity():
    """★★ (iii): 격자 감쇠율 ≡ ν(1−k_l) + 수 보존 기계 + 양수성."""
    import bianchi_rustcore as R
    aniso = lambda n: 1.0 + 0.3*n[:, 2] + 0.2*(n[:, 0]**2 - n[:, 1]**2)
    F = GB.initial_grid(aniso=aniso)
    nu_dt = 0.05
    a0 = GB.multipole_amplitudes(F)
    F1 = GB.thomson_step(F, nu_dt)
    a1 = GB.multipole_amplitudes(F1)
    for l in (1, 2):
        rate = -np.log(a1[l]/a0[l]) / nu_dt
        want = 1.0 - R.kin_thomson_eigenvalue(l)
        assert abs(rate - want) <= 1e-10, (l, rate, want)
    n0 = (F * GB.WANG).sum()
    n1 = (F1 * GB.WANG).sum()
    assert abs(n1 - n0) / abs(n0) <= 1e-13             # 이산 보존형
    assert F1.min() > 0.0                              # 마르코프 양수성
    assert abs(a1[0] - a0[0]) / abs(a0[0]) <= 1e-13    # 에너지 (탄성)


def test_isotropization_endpoint():
    """★ ν dt ≫ 1: 다중극 전멸, 등방 성분 보존 — 끝점 물리."""
    aniso = lambda n: 1.0 + 0.4*n[:, 0] + 0.3*n[:, 1]*n[:, 2]
    F = GB.initial_grid(aniso=aniso)
    F_inf = GB.thomson_step(F, 50.0)
    a = GB.multipole_amplitudes(F_inf)
    assert a[1] <= 1e-12 * a[0] and a[2] <= 1e-12 * a[0]
    assert abs(a[0] - GB.multipole_amplitudes(F)[0]) <= 1e-10 * a[0]


def test_i2_finding_regularized_teaser():
    """★ I2 절단-민감 발견의 정칙화 방향 실증 (개념 게이트): 충돌은 다중극을
    감쇠시키므로 (감쇠율 ≥ 0.9ν), ν 가 충분하면 |J₂|/J₀ 성장이 꺾인다 —
    격자 수준 단일스텝 부등식으로 박제 (동역학 결합은 G2)."""
    aniso = lambda n: 1.0 + 0.5*(n[:, 2]**2 - 1.0/3.0)
    F = GB.initial_grid(aniso=aniso)
    r0 = GB.multipole_amplitudes(F)[2] / GB.multipole_amplitudes(F)[0]
    F1 = GB.thomson_step(F, 1.0)
    r1 = GB.multipole_amplitudes(F1)[2] / GB.multipole_amplitudes(F1)[0]
    assert r1 < 0.5 * r0

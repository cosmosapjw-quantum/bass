"""
G2 · **충돌 사다리 + 이방배경 재맵 + Strang 실측** (72차).

  · 물리 프레임: Σw_phys = 4π (등방 **정확 0**), ∫dΩ ê_iê_j = 4π/3 δ (독립 항등).
  · 등방 배경 환원 ≡ G1 (기계).
  · 사다리 감쇠율: BGK-등방 = ν (전 l≥1) · BGK-보존 = 0 (l≤1) / ν (l≥2) ·
    Thomson = ν(1−k_l),  k=(1,0,1/10,0) — rustcore 고유값과 대조.
  · 보존: 에너지 기계 (3종 전부); **운동량은 BGK-보존만 기계**, Thomson/BGK-등방
    은 쌍극이 1−e^{−νdt} 만큼 전자욕으로 전달 (해석식 게이트 — 물리이지 결함
    아님; B2b 가 복원).
  · ★ 에너지-교환 정리: 가중 n=0,1,2 의 감쇠율 일치 (핵 λ-무관의 실측).
  · ★★ Strang 2차 / Lie 1차 (실측 차수 2.00 / 1.00) — 두 팔이 각각 **정확**
    하므로 남는 오차가 순수 분할오차.
  · ★ 이방 재맵 열화 곡선 (발견 박제): 왜곡이 커지면 각구적 정확도가
    3e−12 → 1e−8 → 3e−5 로 급락 — 자유흐름 팔은 정확한데 **충돌 팔의 구적**이
    이방성의 대가를 치른다 (G1b/K'2 격자 재설계의 입력).
"""
import numpy as np
import pytest

pytest.importorskip("bianchi_rustcore")

import bianchi_rustcore as R  # noqa: E402

from bianchi.matter import collision_ladder as CL  # noqa: E402
from bianchi.matter import grid_boltzmann as GB  # noqa: E402

ANISO = (lambda n: 1.0 + 0.3*n[:, 2] + 0.2*(n[:, 0]**2 - n[:, 1]**2)
         + 0.1*n[:, 0]*n[:, 1])


def _G(a, n=0):
    return CL.angular_density(GB.initial_grid(aniso=ANISO), a, n=n)


def test_physical_frame_measure_and_identity():
    """★ 야코비안 무게: Σw=4π (등방 정확 0) + ∫dΩ êê = (4π/3)δ 독립 항등."""
    e, mu, w = CL.physical_frame(np.ones(3))
    assert abs(w.sum() - 4.0*np.pi) == 0.0
    # 실측: 왜곡이 커질수록 구적이 열화 (아래 곡선 시험과 동일 현상) —
    # 항등 ∫êê 는 Σw 보다 한 자릿수 더 민감 (1e−8 → 1e−7, 3e−5 → 1.8e−4).
    for a, tol in ((np.array([1.2, 0.86, 1.04]), 1e-6),
                   (np.array([1.4, 0.72, 1.08]), 1e-3)):
        e, mu, w = CL.physical_frame(a)
        assert abs(w.sum() - 4.0*np.pi) <= tol
        M = np.einsum("a,ai,aj->ij", w, e, e)
        assert np.abs(M - (4.0*np.pi/3.0)*np.eye(3)).max() <= tol


def test_isotropic_background_reduces_to_g1():
    """★ 등방 배경: Thomson 감쇠율 = ν(1−k_l) 기계 (G1 재현)."""
    a = np.ones(3)
    G = _G(a)
    G1 = CL.collide(G, a, 0.05, "thomson")
    for l in (1, 2):
        r = -np.log(CL.phys_multipole(G1, a, l)
                    / CL.phys_multipole(G, a, l)) / 0.05
        assert abs(r - (1.0 - R.kin_thomson_eigenvalue(l))) <= 1e-11


@pytest.mark.parametrize("kind,want", [
    ("bgk_iso", {1: 1.0, 2: 1.0, 3: 1.0}),
    ("bgk_cons", {1: 0.0, 2: 1.0, 3: 1.0}),
    ("thomson", {1: 1.0, 2: 0.9, 3: 1.0})])
def test_ladder_damping_rates(kind, want):
    """★★ 사다리 3단: 각 연산자의 다중극 감쇠율 (해석 대조군 포함)."""
    a = np.array([1.2, 0.86, 1.04])
    G = _G(a)
    nu_dt = 0.05
    G1 = CL.collide(G, a, nu_dt, kind)
    for l, wl in want.items():
        A0, A1 = CL.phys_multipole(G, a, l), CL.phys_multipole(G1, a, l)
        if wl == 0.0:
            assert abs(A1 - A0) / A0 <= 1e-9          # 보존 (l≤1)
        else:
            r = -np.log(A1 / A0) / nu_dt
            assert abs(r - wl) <= 1e-6, (kind, l, r)
    if kind == "thomson":                              # rustcore 고유값 대조
        for l in (1, 2, 3):
            assert abs(want[l] - (1.0 - R.kin_thomson_eigenvalue(l))) <= 1e-15


def test_conservation_and_honest_momentum_transfer():
    """★ 에너지 기계보존 (3종) + 운동량: BGK-보존만 기계, 나머지는
    1−e^{−νdt} 전달 (해석식 — 물리이지 결함 아님)."""
    a = np.array([1.2, 0.86, 1.04])
    G = _G(a)
    nu_dt = 0.05
    n0, p0 = CL.invariants(G, a)
    for kind in ("bgk_iso", "bgk_cons", "thomson"):
        G1 = CL.collide(G, a, nu_dt, kind)
        n1, p1 = CL.invariants(G1, a)
        assert abs(n1 - n0) / abs(n0) <= 1e-14, kind   # 에너지 (탄성)
        if kind == "bgk_cons":
            assert np.abs(p1 - p0).max() / np.abs(p0).max() <= 1e-12
        else:
            frac = np.abs(p1).max() / np.abs(p0).max()
            assert abs(frac - np.exp(-nu_dt)) <= 1e-6, (kind, frac)


def test_energy_commuting_theorem():
    """★ 핵 λ-무관 ⇒ 가중 n=0,1,2 의 감쇠율 일치 (구적 수준 1e−5)."""
    a = np.array([1.3, 0.8, 1.05])
    rates = []
    for n in (0, 1, 2):
        G = _G(a, n=n)
        G1 = CL.collide(G, a, 0.05, "thomson")
        rates.append(-np.log(CL.phys_multipole(G1, a, 2)
                             / CL.phys_multipole(G, a, 2)) / 0.05)
    assert max(rates) - min(rates) <= 1e-5, rates
    assert abs(np.mean(rates) - 0.9) <= 1e-5


def test_strang_second_order_lie_first():
    """★★ 두 팔이 각각 정확 ⇒ 남는 오차 = 분할오차: Strang 2차 / Lie 1차."""
    a_of = lambda t: np.array([np.exp(0.3*t), np.exp(-0.2*t), np.exp(-0.1*t)])
    G0 = CL.angular_density(GB.initial_grid(aniso=ANISO), a_of(0.0))
    ref = CL.strang_evolve(G0, a_of, 0.0, 1.0, 1600, nu=2.0)
    scale = np.abs(ref).max()

    def err(fn, ns):
        return float(np.abs(fn(G0, a_of, 0.0, 1.0, ns, nu=2.0)
                            - ref).max() / scale)

    es = [err(CL.strang_evolve, ns) for ns in (25, 50, 100)]
    orders = [np.log2(es[k]/es[k+1]) for k in range(2)]
    assert all(1.9 <= o <= 2.1 for o in orders), (es, orders)
    el = [err(CL.lie_evolve, ns) for ns in (25, 50, 100)]
    ol = [np.log2(el[k]/el[k+1]) for k in range(2)]
    assert all(0.9 <= o <= 1.1 for o in ol), (el, ol)
    assert es[0] < el[0] / 50.0                        # 정량 우위


def test_anisotropy_degradation_curve_pinned():
    """★ 발견 박제: 이방 왜곡이 커지면 **충돌 팔 구적**이 급락 (자유흐름 팔은
    정확).  s=0.1 → 1e−9급, s=0.4 → 1e−4급 — 격자 재설계의 정량 입력."""
    errs = {}
    for s in (0.1, 0.4):
        a = np.array([1 + s, 1 - 0.7*s, 1 + 0.2*s])
        _, _, w = CL.physical_frame(a)
        errs[s] = abs(w.sum() - 4.0*np.pi)
    assert errs[0.1] <= 1e-9
    assert errs[0.4] >= 100.0 * errs[0.1]              # 급락 실재
    assert errs[0.4] <= 1e-3                           # 그래도 유계

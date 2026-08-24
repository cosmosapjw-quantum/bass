"""
K2b · tilt 허용조건 — **Bianchi I 은 tilt 를 담을 수 없다** (no-go).

운동량 구속(Codazzi):
    C^a = 3 A_b Σ^{ab} + ε^{abc} N_{bd} Σ_c{}^d − q^a = 0

★ 왜 이게 중요한가: K2 에서 에너지틀 v(t) 를 물질에서 풀어냈지만, 그것을 기하와
  결합하려면 구속을 만족해야 한다.  Bianchi I 은 N = A = 0 이라 **용량이 0** 이고
  구속이 q = 0 을 강제한다.  ⇒ K2 의 tilt 는 **운동학적으로 옳은 test-field 구성**
  이지만 **type I 의 Einstein 해가 아니다**.  이걸 모르고 K1+K2 를 통합하면
  존재하지 않는 대상 위에 짓게 된다.

★ 더 뾰족한 사실 (측정): **대각 N · 대각 Σ 이면 class A 전체가 못 담는다** —
  I, II, VII₀, IX 모두 용량이 정확히 0.  ε^{abc}N_{bd}Σ_c{}^d 가 둘 다 대각일 때
  항등적으로 사라지기 때문이다.  담으려면 **A ≠ 0 (class B)** 이거나 **비대각 N/Σ**.
"""
import numpy as np
import pytest

from bianchi.matter import tilt_admissibility as TA

SIG = np.diag([0.06, -0.02, -0.04])


# ═══════════════════════════════ no-go: Bianchi I
def test_bianchi_I_capacity_is_identically_zero():
    """★★ Bianchi I (N=A=0) 은 **어떤 Σ 에서도** 운동량밀도를 담지 못한다."""
    rng = np.random.default_rng(0)
    for _ in range(20):
        s = rng.normal(size=(3, 3))
        s = 0.5 * (s + s.T)
        s = s - np.trace(s) * np.eye(3) / 3.0        # 무대각합 대칭
        assert np.abs(TA.bianchi_I_capacity(s)).max() < 1e-15


def test_bianchi_I_forbids_tilt():
    """구속이 q = 0 을 강제 — `tilt_is_admissible` 가 False."""
    assert not TA.tilt_is_admissible(SIG)


def test_diagonal_class_A_types_all_have_zero_capacity():
    """★ I, II, VII₀, IX — **대각 N·대각 Σ 이면 전부 용량 0**.

    ε^{abc}N_{bd}Σ_c{}^d 가 둘 다 대각일 때 항등적으로 사라진다.
    "type II 로 올리면 tilt 가 된다" 는 순진한 기대는 **틀렸다**.
    """
    for N in (np.diag([1.0, 0, 0]), np.diag([1.0, 1.0, 0]), np.eye(3)):
        assert np.abs(TA.constraint_capacity(SIG, N, None)).max() < 1e-15, N


def test_offdiagonal_N_or_nonzero_A_restores_capacity():
    """A ≠ 0 (class B) 또는 **비대각 N** 이면 담을 수 있다."""
    assert TA.tilt_is_admissible(SIG, None, np.array([0.0, 0.0, 0.7]))
    Noff = np.array([[0.0, 1.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 0.0]])
    assert TA.tilt_is_admissible(SIG, Noff, None)


def test_G_0i_vanishes_for_diagonal_bianchi_I():
    """★ 같은 사실의 계량 쪽 표현: 대각 Bianchi I 은 G_{0i} ≡ 0.

    기하에 운동량밀도를 받을 자리가 아예 없다.
    """
    import sympy as sp
    AUD = pytest.importorskip("audit.k1_shear_source_normalization")
    for i in range(3):
        assert sp.simplify(AUD.EIN[0, i + 1]) == 0


# ═══════════════════════════════ K2 구성이 실제로 위반한다
def test_dipole_configuration_violates_type_I_constraint():
    """★★ K2 의 쌍극 tilt 를 type I 에 넣으면 위반량이 정확히 |q| 다.

    (용량이 0 이므로 C^a = −q^a.)  측정: |q|/ρ = 8.5e−2 → |C| = 8.5e−2.
    """
    from bianchi.matter import tilted_frame as TF
    from bianchi.matter import tilted_moments as TM
    a = np.array([1.0, 0.9, 1.2])
    f0 = TF.dipole_f0()
    rho = TM.J_moment_tilted(a, np.zeros(3), 0.0, 0, 0, f0)
    q = np.asarray(TM.J_moment_tilted(a, np.zeros(3), 0.0, 1, 0, f0), float)
    Hb = np.sqrt((rho + 0.5 * float(np.diag(SIG) @ np.diag(SIG))) / 3.0)
    qn = q / (3 * Hb ** 2)
    viol = TA.violation_for_flux(qn, SIG)
    assert viol > 1e-3, viol
    assert abs(viol - np.abs(qn).max()) < 1e-12      # 정확히 |q|


def test_isotropic_distribution_is_admissible_in_type_I():
    """등방 f₀ 는 q = 0 이라 type I 에서 **문제없다** — K1 결합이 정당한 이유."""
    from bianchi.matter import freestream as fs
    from bianchi.matter import tilted_moments as TM
    a = np.array([1.0, 0.9, 1.2])
    q = np.asarray(TM.J_moment_tilted(a, np.zeros(3), 0.0, 1, 0,
                                      fs.f_fermi_dirac), float)
    rho = TM.J_moment_tilted(a, np.zeros(3), 0.0, 0, 0, fs.f_fermi_dirac)
    assert np.abs(q).max() / rho < 1e-14
    assert TA.violation_for_flux(q / rho, SIG) < 1e-14


# ═══════════════════════════════ 구성적: 담을 수 있는 배경이 존재한다
def test_type_V_can_hold_a_given_flux_exactly():
    """★★ **no-go 로 끝내지 않는다**: type V 에서 주어진 q 를 담는 A 가 정확히 존재.

    3Σ^{ab}A_b = q^a 를 A 에 대해 풀면 Codazzi 잔차 1.4e−17.
    ⇒ tilt 를 담는 일관된 구성이 **있다** — 다만 type I 이 아닐 뿐이다.
    """
    q = np.array([0.0, 0.0, 0.084556])
    r = TA.type_V_consistent_configuration(q, SIG)
    assert r["exact"], r
    assert r["codazzi"] < 1e-12, r
    assert np.abs(r["A"]).max() > 1e-3


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_type_V_solve_is_exact_for_random_flux(seed):
    """무작위 q 에 대해서도 type V 해가 정확 (Σ 가 정칙인 한)."""
    rng = np.random.default_rng(seed)
    q = rng.normal(size=3) * 0.05
    r = TA.type_V_consistent_configuration(q, SIG)
    assert r["rank"] == 3
    assert r["codazzi"] < 1e-12, r


def test_singular_shear_reports_inexact_solution():
    """Σ 가 특이하면 (예: 축대칭으로 q 방향이 상공간 밖) 정확해가 없음을 **보고**한다."""
    S = np.diag([0.05, 0.05, -0.10])
    q = np.array([0.0, 0.0, 0.0])
    r = TA.solve_type_V_A(q, S)
    assert r["exact"]                                  # q=0 은 항상 가능
    # q 를 Σ 의 상공간 밖으로: 특이 Σ 를 만든다
    S2 = np.diag([0.0, 0.0, 0.0])
    r2 = TA.solve_type_V_A(np.array([0.0, 0.0, 0.1]), S2)
    assert not r2["exact"]
    assert r2["rank"] == 0

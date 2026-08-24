"""PR-41 no-hair + PR-42 유체 합동 (vorticity·가속도·CMB 쌍극) 테스트.

PR-42 는 audit/d_vorticity.json 오라클을 프레임 접속 위에서 재현하는지 검증한다.
"""
import numpy as np
import pytest

from bianchi.analysis import no_hair as nh
from bianchi.physical import congruence as cg


# ═══════════════════════════════════════════ PR-41 Wald no-hair
def test_desitter_hubble():
    assert abs(nh.desitter_hubble(3.0) - 1.0) < 1e-12        # √(3/3)=1
    assert abs(nh.desitter_expansion(3.0) - 3.0) < 1e-12     # √(3·3)=3


def test_wald_shear_decays_as_minus3():
    """Bianchi I + Λ: d ln Σ/dτ → -3 (Wald 지수)."""
    r = nh.verify_no_hair(Lambda=1.0, Sigma0=0.8, tau_max=10.0)
    assert abs(r["decay_exponent"] - (-3.0)) < 0.05
    assert r["Sigma_final"] < 1e-8                            # Σ → 0
    assert r["constraint_max"] < 1e-6                         # 구속 보존


def test_wald_desitter_attractor():
    """H → √(Λ/3), θ 단조감소하여 √(3Λ) 로."""
    r = nh.verify_no_hair(Lambda=2.0, Sigma0=0.6, tau_max=10.0)
    assert abs(r["H_final"] - r["H_dS"]) < 1e-4
    assert r["theta_monotone_decreasing"]
    assert r["theta_final"] > r["theta_dS"] - 1e-4           # 위에서 하한으로 접근
    assert abs(r["theta_final"] - r["theta_dS"]) < 1e-3


def test_wald_constraint_positivity_guard():
    with pytest.raises(ValueError):
        nh.integrate_bianchi_I_lambda(Sigma0=2.0)            # Σ0 ≥ √3 금지


def test_no_hair_counterexample():
    """이방 인플레이션(게이지장): d ln Σ/dτ → 0, Σ → Σ* ≠ 0 (no-hair 위반)."""
    c = nh.anisotropic_inflation_counterexample(epsilon=0.03, c=2.0)
    assert abs(c["decay_exponent"]) < 0.05                   # 감쇠 없음
    assert c["Sigma_final"] > 1e-4                           # 잔류 이방성
    assert abs(c["Sigma_final"] - c["Sigma_star"]) < 1e-4
    assert c["violates_no_hair"]


def test_no_hair_counterexample_epsilon_zero():
    """ε→0: Σ*=0 → 잔류 이방성 소멸, 위반 아님 (Wald 회복)."""
    c = nh.anisotropic_inflation_counterexample(epsilon=0.0, c=2.0)
    assert c["Sigma_star"] == 0.0
    assert not c["violates_no_hair"]


# ═══════════════════════════════════════════ PR-42 유체 합동 (D22)
def _sym(M):
    return 0.5 * (M + M.T)


def _stf(M):
    S = _sym(M)
    return S - np.trace(S) * np.eye(3) / 3.0


def _draw(rng):
    """audit/d_vorticity.py 의 draw 재현: Jacobi(N·A=0) 만족 상태."""
    N = _sym(rng.normal(size=(3, 3)))
    w, V = np.linalg.eigh(N)
    k = int(np.argmin(abs(w))); w[k] = 0.0
    N = V @ np.diag(w) @ V.T
    A = float(rng.normal()) * V[:, k]                        # N·A = 0
    v = rng.normal(size=3); v *= rng.uniform(0.05, 0.5) / np.linalg.norm(v)
    S = _stf(rng.normal(size=(3, 3)))
    R = rng.normal(size=3)
    H = float(rng.uniform(0.6, 1.6))
    return H, S, N, A, R, v


def test_normal_congruence_irrotational():
    """법선 합동 v=0 ⇒ ω_ab = 0 (구성상)."""
    rng = np.random.default_rng(1)
    for _ in range(20):
        H, S, N, A, R, v = _draw(rng)
        assert cg.normal_congruence_is_irrotational(H, S, N, A, R) < 1e-13


def test_onshell_vorticity_clean_observable():
    """on-shell ω: u-직교·반대칭·v=0 소멸 (D22 오라클)."""
    rng = np.random.default_rng(2)
    e_ortho = e_asym = e_v0 = 0.0
    for _ in range(60):
        H, S, N, A, R, v = _draw(rng)
        gamma = float(rng.uniform(1.05, 1.6)); rho = float(rng.uniform(0.2, 1.0))
        k = cg.onshell_kinematics(H, S, N, A, R, v, gamma, rho)
        e_ortho = max(e_ortho, float(np.abs(k["omega4"] @ k["u_up"]).max()))
        e_asym = max(e_asym, float(np.abs(k["omega4"] + k["omega4"].T).max()))
        k0 = cg.congruence_kinematics(H, S, N, A, R, np.zeros(3), np.zeros(3))
        e_v0 = max(e_v0, float(np.abs(k0["omega3"]).max()))
    assert e_ortho < 1e-12
    assert e_asym < 1e-12
    assert e_v0 < 1e-13


def test_onshell_acceleration_parallel_to_v():
    """운동량 보존 ⇒ 공간 가속도가 v 에 평행 (D22: 잔차 ~1e-9)."""
    rng = np.random.default_rng(3)
    worst = 0.0
    for _ in range(60):
        H, S, N, A, R, v = _draw(rng)
        gamma = float(rng.uniform(1.05, 1.6)); rho = float(rng.uniform(0.2, 1.0))
        k = cg.onshell_kinematics(H, S, N, A, R, v, gamma, rho)
        a_sp = k["accel"][1:]
        perp = a_sp - (a_sp @ v) / (v @ v) * v
        worst = max(worst, float(np.linalg.norm(perp)))
    assert worst < 1e-7


def test_onshell_spatial_vorticity_EOS_independent():
    """on-shell 공간 vorticity 는 EOS(γ,ρ) 무관 (D22 핵심)."""
    rng = np.random.default_rng(4)
    spread = 0.0
    for _ in range(40):
        H, S, N, A, R, v = _draw(rng)
        oms = []
        for gamma, rho in [(1.1, 0.3), (4/3, 0.5), (1.5, 0.9), (1.05, 0.2)]:
            k = cg.onshell_kinematics(H, S, N, A, R, v, gamma, rho)
            oms.append(k["omega3"])
        spread = max(spread, max(float(np.abs(o - oms[0]).max()) for o in oms))
    assert spread < 1e-8


def test_offshell_vdot_dependence_is_real():
    """off-shell 에서 임의 v̇ 는 ω 를 바꾼다 — 물리 (D22: v1.2 오개념 반박)."""
    rng = np.random.default_rng(5)
    biggest = 0.0
    for _ in range(40):
        H, S, N, A, R, v = _draw(rng)
        o1 = cg.congruence_kinematics(H, S, N, A, R, v, np.zeros(3))["omega3"]
        o2 = cg.congruence_kinematics(H, S, N, A, R, v, rng.normal(size=3))["omega3"]
        biggest = max(biggest, float(np.abs(o1 - o2).max()))
    assert biggest > 0.1                                     # 진짜 의존 (O(1))


def test_vorticity_over_H_planck():
    """(ω/H) 계산과 Planck 상한 상수 노출."""
    rng = np.random.default_rng(6)
    H, S, N, A, R, v = _draw(rng)
    k = cg.onshell_kinematics(H, S, N, A, R, v, 4/3, 0.5)
    r = cg.vorticity_over_H(k["omega3"], H)
    assert r >= 0.0
    assert cg.PLANCK_VORTICITY_BOUND == pytest.approx(7.6e-10)


def test_cmb_dipole_from_tilt():
    """CMB 쌍극 β = |v|; 도플러 패턴 blueshift/redshift 방향."""
    v = np.array([0.001, 0.0, 0.0])
    assert abs(cg.cmb_dipole_amplitude(v) - 0.001) < 1e-15
    # 운동 방향 (+x) 관측 → 청색편이 (T>T0), 반대 → 적색편이
    T_fwd = cg.cmb_temperature_pattern(v, np.array([1.0, 0, 0]), T0=1.0)
    T_bwd = cg.cmb_temperature_pattern(v, np.array([-1.0, 0, 0]), T0=1.0)
    assert T_fwd > 1.0 > T_bwd
    m = cg.cmb_multipoles_from_tilt(v)
    assert abs(m["dipole"] - 0.001) < 1e-12
    assert m["quadrupole"] == pytest.approx(0.001 ** 2 / 3.0)


def test_cmb_pattern_relativistic_normalization():
    """√(1-v²) 인자로 v→0 에서 등방 T₀ 회복."""
    v = np.zeros(3)
    for nh_ in [np.array([1.0, 0, 0]), np.array([0, 1.0, 0]), np.array([0, 0, 1.0])]:
        assert abs(cg.cmb_temperature_pattern(v, nh_, T0=2.725) - 2.725) < 1e-12

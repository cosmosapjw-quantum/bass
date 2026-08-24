"""
K1 · 운동론 계층 ↔ Einstein 결합 검증.

지금까지 계층은 **고정 배경 위의 test-field** 였다.  여기서 π_ab 가 기하를 움직인다.

★ 이 파일이 고정하는 것:
  1. 차트의 Π 규격화가 **측정으로 확정**됐다 (Π = π/H², 잔차 6.7e−16).
     문헌마다 π/H², π/(3H²), ½π/H² 로 갈리는 지점이라 인용 대신 계량에서 쟀다.
  2. **K3 게이트** — Ḣ 를 (구속 미분 + 에너지보존) 과 (Raychaudhuri) 두 경로로 계산해
     비교.  일치는 곧 ∇_μT^{μν}=0 이다.
     ★ 그러나 K3 는 **Π 규격화에 눈이 멀었다** (σ·π 가 상쇄).  처음에 잡는다고 적었다가
       측정으로 반증됐다.  규격화는 `einstein_residual` 이 검사하며 0.01% 도 잡는다.
  3. 결합이 **실제로 궤적을 바꾼다** (안 바뀌면 결합했다는 주장이 공허하다).
  4. 결합 궤적이 **정확 구적 기준**과 일치한다.
"""
import numpy as np
import pytest

from bianchi.matter import kinetic_einstein as KE

A0 = (1.0, 0.85, 1.2)
S0 = (0.05, -0.02, -0.03)

AUD = pytest.importorskip("audit.k1_shear_source_normalization")


# ═══════════════════════════════ 1. 규격화 (Einstein 에서 직접 측정)
def test_friedmann_control_group():
    """★ 통제군: G_00 = 3H² − σ² 재생산.  실패하면 Einstein 텐서 구성을 못 믿는다."""
    assert AUD.friedmann_residual() < 1e-12


def test_shear_source_coefficient_is_exactly_one():
    """σ̇^i + θσ^i = 1 × (무대각합 공간 Einstein) — 측정 1.000000000000."""
    c, res = AUD.shear_source_coefficient()
    assert abs(c - 1.0) < 1e-10, c
    assert res < 1e-12, res


def test_chart_normalization_is_pi_over_H_squared():
    """★★ Σ' = −(2−q)Σ + Π 에서 **Π = π/H²** (손대수가 아니라 수치 검증, 6.7e−16).

    경로 A: 계량에서 직접 얻은 σ̇ 를 τ=ln ℓ, Σ=σ/H 로 변환
    경로 B: 차트 공식에 Π = π/H² 대입
    """
    assert AUD.verify_chart_normalization() < 1e-12


def test_raychaudhuri_fit_is_rank_deficient_and_equivalent():
    """★ 함정: Friedmann 3H²=ρ+σ² 이 {H²,σ²,ρ} 를 종속시켜 계수가 **유일하지 않다**.

    설계행렬 rank 가 3/4 이므로 최소제곱 계수를 그대로 읽으면 오독한다.
    올바른 판정은 "교과서형과의 차가 영공간 (3,−1,−1,0) 에 평행한가" 다.
    """
    c, res, rank, _ = AUD.raychaudhuri_coefficients()
    assert rank == 3, rank
    assert res < 1e-12
    eq = AUD.raychaudhuri_equivalent_to_standard()
    assert eq["equivalent"], eq
    assert eq["perpendicular"] < 1e-9
    assert abs(eq["parallel_component"]) > 0.1      # 실제로 어긋나 보인다 (영공간 방향)


# ═══════════════════════════════ 2. ★★ K3 · Bianchi 항등식 게이트
@pytest.mark.parametrize("mass", [0.0, 0.7, 3.0])
@pytest.mark.parametrize("sig", [S0, (0.2, -0.15, -0.05), (0.0, 0.0, 0.0)])
def test_K3_bianchi_identity_holds_to_machine_precision(mass, sig):
    """★★ Ḣ(구속미분+에너지보존) = Ḣ(Raychaudhuri) — 곧 ∇_μT^{μν}=0.

    Friedmann 은 H 를 구속에서 풀기 때문에 **설계상 항상 만족**되어 아무것도 못 잡는다.
    자유롭지 않은 검사는 이 정합성이다.
    """
    r = KE.K3_residual(A0, sig, mass)
    assert r["rel"] < 1e-13, r


def test_K3_is_blind_to_the_Pi_normalization():
    """★★ **정직한 한계**: K3 는 Π 규격화를 검사하지 **못한다**.

    π 를 3배·0배·−5배로 틀리게 넣어도 잔차가 1.5e−16 로 같다.  이유:
        6HḢ = ρ̇ + σ·σ̇ = [−3H(ρ+p) − σ·π] + [−3Hσ·σ + σ·π]    ← π 가 소거된다
    처음에 이 게이트가 규격화도 잡는다고 적었는데 **틀렸다**.  측정이 바로잡았다.
    ⇒ 규격화는 `einstein_residual` 이 검사한다 (아래).
    """
    import bianchi.matter.kinetic_einstein as M
    orig = M.matter_from_quadrature
    vals = []
    try:
        for c in (1.0, 3.0, 0.0, -5.0):
            M.matter_from_quadrature = (
                lambda a, m, f0=None, _o=orig, _c=c:
                (lambda t: (t[0], t[1], _c * t[2]))(_o(a, m)))
            vals.append(KE.K3_residual(A0, S0, 0.0)["rel"])
    finally:
        M.matter_from_quadrature = orig
    assert all(v < 1e-13 for v in vals), vals          # 전부 통과해버린다
    assert max(vals) - min(vals) < 1e-15, vals         # 구별조차 못 한다


@pytest.mark.parametrize("scale,expect_big", [(1.0, False), (1.0001, True),
                                              (1.1, True), (3.0, True), (0.0, True)])
def test_einstein_residual_has_teeth_on_normalization(scale, expect_big):
    """★★ Einstein 잔차는 규격화를 **본다** — 0.01% 오차도 9.2e−6 로 드러난다.

    (a, ȧ, ä) 를 결합식에서 만들어 G_μν 에 넣고 물질 응력과 비교하므로, Π 배율이
    틀리면 ä 가 틀어져 G_tf 가 π 에서 벗어난다.
    측정: ×1.0 → 8.8e−17,  ×1.0001 → 9.2e−6,  ×1.1 → 9.2e−3,  ×3 → 1.8e−1.
    """
    r = KE.einstein_residual(A0, S0, 0.0, pi_scale=scale)
    assert r["G00_rel"] < 1e-13                        # Friedmann 은 늘 만족
    if expect_big:
        assert r["Gtf_rel"] > 1e-6, r
    else:
        assert r["Gtf_rel"] < 1e-13, r


@pytest.mark.parametrize("mass", [0.0, 0.7, 3.0])
def test_einstein_equations_hold_on_the_coupled_flow(mass):
    """★★ 결합 흐름 위에서 **G_μν = T_μν** 가 기계정밀도로 성립 (규격화 포함)."""
    r = KE.einstein_residual(A0, S0, mass)
    assert r["G00_rel"] < 1e-13, r
    assert r["Gtf_rel"] < 1e-13, r


def test_K3_uses_measured_sigma_squared_convention():
    """★ σ² ≡ ½σ_abσ^ab 규약.  d(σ²)/dt 를 2배로 쓰면 게이트가 1e−5 로 터진다.

    실제로 그 실수를 했고 게이트가 즉시 잡았다 — 차이가 정확히
    −σ² + σ·π/(6H) 로 떨어져 원인이 특정됐다.  회귀로 고정한다.
    """
    s = np.asarray(S0, float)
    assert abs(KE.sigma_sq(s) - 0.5 * float(s @ s)) < 1e-15
    r = KE.K3_residual(A0, S0, 0.0)
    assert r["rel"] < 1e-13


# ═══════════════════════════════ 3. 결합이 실제로 작동하는가
def test_coupling_actually_changes_the_trajectory():
    """★★ π 를 끄면 궤적이 달라진다 — 결합했다는 주장의 최소 조건.

    측정: a 가 4.8% , σ 가 100% 달라진다 (무질량, t=0.3).
    """
    c = KE.coupling_matters()
    assert c["rel_a"] > 1e-3, c
    assert c["rel_sigma"] > 1e-2, c


def test_isotropic_start_shear_is_damped_by_pi():
    """★ **등방 a_vec** 에서 시작하면 π 는 순전히 σ 가 만들고, σ 를 감쇠시킨다.

    H4 에서 유도한 η > 0 (Misner 점성) 의 기하학적 귀결.
    측정: |σ| 가 6.42e−3 (π 없음) → 3.56e−3 (π 있음).
    """
    d = KE.shear_damping_with_isotropic_start()
    assert d["damped"], d
    assert np.abs(d["with_pi"]).max() < 0.7 * np.abs(d["without_pi"]).max()


def test_anisotropic_start_can_grow_the_shear():
    """★ 순진한 기대 반증: "이방응력은 늘 전단을 감쇠시킨다" 는 **틀렸다**.

    비등방 a_vec 으로 시작하면 π 가 σ 와 무관하게 이미 존재해 σ 를 **키운다**
    (측정: 0.0065 → 0.147).  처음에 감쇠를 기대하는 시험을 썼다가 이 사실에 부딪혔다.
    """
    c = KE.coupling_matters()
    assert np.abs(c["sigma_with"]).max() > np.abs(c["sigma_without"]).max()


@pytest.mark.parametrize("mass", [0.0, 1.0])
def test_coupled_trajectory_matches_exact_quadrature(mass):
    """★★ 계층이 기하를 **옳게** 움직인다 — 정확 구적 기준과 대조.

    측정 (nsteps=100): m=0 → a 1.2e−7, σ 8.3e−6;  m=1 → a 1.9e−4, σ 1.7e−3.
    """
    e = KE.coupled_trajectory_error(mass=mass, nsteps=100)
    assert e["a"] < 1e-2, e
    assert e["sigma"] < 5e-2, e


def test_massless_coupled_trajectory_is_accurate():
    """무질량은 계층이 정확해 결합 궤적도 1e−7 수준."""
    e = KE.coupled_trajectory_error(mass=0.0, nsteps=100)
    assert e["a"] < 1e-5, e


# ═══════════════════════════════ 4. 구조·극한
def test_isotropic_limit_keeps_shear_zero():
    """등방 초기조건(σ=0, a 등방)이면 π=0 이라 σ 가 계속 0."""
    h = KE.integrate_reference((1.0, 1.0, 1.0), (0.0, 0.0, 0.0), 0.0, 0.2, 50)
    assert np.abs(h["sigma"][-1]).max() < 1e-12


def test_hubble_comes_from_the_constraint():
    """H 는 진화가 아니라 구속에서 나온다 — 3H² = ρ + σ² 가 항등적으로 성립."""
    rho, p, pi = KE.matter_from_quadrature(A0, 0.7)
    s = np.asarray(S0, float)
    Hb = KE.hubble_from_constraint(rho, s)
    assert abs(3 * Hb ** 2 - (rho + KE.sigma_sq(s))) < 1e-12 * rho


def test_negative_hubble_squared_raises():
    """ρ+σ² ≤ 0 이면 조용히 nan 을 내지 않고 예외."""
    with pytest.raises(ValueError):
        KE.hubble_from_constraint(-1.0, (0.0, 0.0, 0.0))


def test_shear_stays_trace_free():
    """σ 의 무대각합성이 적분 내내 유지 (사영으로 표류 방지)."""
    h = KE.integrate_reference(A0, S0, 0.0, 0.3, 100)
    for s in h["sigma"]:
        assert abs(float(np.sum(s))) < 1e-12

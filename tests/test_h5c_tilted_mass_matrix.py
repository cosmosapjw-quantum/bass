"""
H5-c · tilted 질량행렬 시험 — M(v)·J̇ = F 조립의 검증.

★ 이 파일의 핵심 두 가지:
  1. **독립 교차검증**: `matter/tilted.py` 가 조립한 계층 좌변이 `audit/
     h5_tilted_conservation.py` 가 직접 계산한 ∇_μT^{μν} 사영과 **항등적으로** 같다.
     두 모듈은 서로를 임포트하지 않는다 (한쪽은 계층 항을 조립, 다른 쪽은 T^{μν} 발산).
  2. **닫힌형 발견의 잠금**:  M = γ (I + e₀ vᵀ)  — 즉 l≤1 블록의 질량행렬은
     상삼각이고 역행렬이 해석적이다.  선형해 없이 풀 수 있다.

★ 항등식임에 주의: 계층 좌변이 0 이라는 게 아니라 ∇_μT^{μν} 사영과 **같다**는 것이다
  (off-shell 항등식).  그래서 무작위 도함수 표본으로 시험할 수 있다.
"""
import numpy as np
import pytest

from bianchi.matter import tilted as T

O = pytest.importorskip("audit.h5_tilted_conservation")


def _rand_kw(rng):
    return dict(a_vec=rng.uniform(0.7, 1.4, 3), da_vec=rng.uniform(-0.5, 0.5, 3),
                v=rng.uniform(-0.25, 0.25, 3), dv=rng.uniform(-0.3, 0.3, 3),
                rho=rng.uniform(0.5, 2.0), drho=rng.uniform(-0.5, 0.5),
                p=rng.uniform(0.05, 0.6), dp=rng.uniform(-0.5, 0.5),
                q=rng.uniform(-0.3, 0.3, 3), dq=rng.uniform(-0.5, 0.5, 3),
                pi5=rng.uniform(-0.3, 0.3, 5), dpi5=rng.uniform(-0.5, 0.5, 5))


def _audit_vals(kw):
    """같은 상태를 audit 모듈의 인자 벡터로 옮긴다."""
    val = dict(zip(("a1", "a2", "a3"), kw["a_vec"]))
    val.update(zip(("v1", "v2", "v3"), kw["v"]))
    val["rho"], val["p"] = kw["rho"], kw["p"]
    val.update(zip(("q1", "q2", "q3"), kw["q"]))
    val.update({f"pi{k}": kw["pi5"][k] for k in range(5)})
    dot = dict(zip(("a1", "a2", "a3"), kw["da_vec"]))
    dot.update(zip(("v1", "v2", "v3"), kw["dv"]))
    dot["rho"], dot["p"] = kw["drho"], kw["dp"]
    dot.update(zip(("q1", "q2", "q3"), kw["dq"]))
    dot.update({f"pi{k}": kw["dpi5"][k] for k in range(5)})
    return [val[n] for n in O._BASE] + [dot[n] for n in O._BASE]


# ═══════════════════════════════ 기하 자기검증
def test_tetrad_orthonormal():
    assert T.state()["ortho"] < 1e-13


def test_vanishing_tilt_gate():
    """★ v=0 → ω = u̇ = D = 0 이고 M = I (법선합동 = H1 형태로 정확 환원)."""
    g = T.vanishing_tilt_recovers_normal()
    assert g["omega"] == 0.0
    assert g["udot"] == 0.0
    assert g["div"] == 0.0
    assert g["M_minus_I"] < 1e-14


# ═══════════════════════════════ ★ 독립 교차검증 (계층 조립 vs ∇T)
@pytest.mark.parametrize("seed", [0, 1, 2, 3])
def test_hierarchy_lhs_equals_divT_identically(seed):
    """★★ tilted.py 의 계층 좌변 ≡ audit 의 ∇_μT^{μν} 사영 (off-shell 항등식).

    두 모듈은 독립이다: 한쪽은 (Ω),(D),(E),(div) 항을 조립하고, 다른 쪽은 T^{μν} 의
    발산을 직접 계산한다.  일치는 부호·계수·항 구조가 전부 맞다는 뜻이다.
    """
    rng = np.random.default_rng(seed)
    kw = _rand_kw(rng)
    eq = np.asarray(T.residual(**kw), float)
    r = O.evaluate(_audit_vals(kw))
    want = np.array([r["energy"], *r["mom"]], float)
    scale = max(np.abs(want).max(), 1e-12)
    assert np.abs(eq - want).max() / scale < 1e-11, (eq, want)


def test_solve_jdot_reproduces_onshell_derivatives():
    """★ M·J̇ = F 를 풀면 ∇_μT^{μν}=0 을 만족하는 (ρ̇, q̇) 가 나온다.

    검증: 풀어 얻은 도함수를 되넣으면 좌변(=∇T 사영)이 0 이 된다.
    """
    rng = np.random.default_rng(11)
    kw = _rand_kw(rng)
    sol = T.solve_jdot(**kw)
    kw2 = dict(kw)
    kw2["drho"] = sol["rho_dot"]
    kw2["dq"] = sol["q_dot"]
    eq = np.abs(np.asarray(T.residual(**kw2), float)).max()
    assert eq < 1e-12, eq
    # 같은 상태를 audit 쪽에서 봐도 ∇T 사영이 0
    r = O.evaluate(_audit_vals(kw2))
    assert abs(r["energy"]) < 1e-12
    assert np.abs(r["mom"]).max() < 1e-12


def test_equation_is_affine_in_time_derivatives():
    """★ M, F 추출의 **전제를 시험으로 못 박는다**: 좌변이 (ρ̇, q̇) 에 대해 정확히 아핀.

    아핀이 아니면 `M[:,c] = EQ(e_c) − EQ(0)` 이 틀린다 (유한차분 근사가 되어버린다).
    확인: EQ(2x) − EQ(0) = 2[EQ(x) − EQ(0)] 이 기계정밀도로 성립.
    """
    rng = np.random.default_rng(21)
    kw = _rand_kw(rng)
    base = dict(kw); base["drho"] = 0.0; base["dq"] = np.zeros(3)
    e0 = np.asarray(T.residual(**base), float)
    x_rho, x_q = 0.37, np.array([0.11, -0.23, 0.05])
    k1 = dict(kw); k1["drho"] = x_rho; k1["dq"] = x_q
    k2 = dict(kw); k2["drho"] = 2 * x_rho; k2["dq"] = 2 * x_q
    d1 = np.asarray(T.residual(**k1), float) - e0
    d2 = np.asarray(T.residual(**k2), float) - e0
    assert np.abs(d2 - 2.0 * d1).max() < 1e-13 * max(np.abs(d1).max(), 1.0)


def test_mass_matrix_columns_are_exact_not_finite_difference():
    """M 열이 아핀성으로 정확히 뽑혔는지 — 스텝 크기를 바꿔도 같은 값."""
    rng = np.random.default_rng(22)
    kw = _rand_kw(rng)
    M = T.mass_matrix(**kw)
    base = dict(kw); base["drho"] = 0.0; base["dq"] = np.zeros(3)
    e0 = np.asarray(T.residual(**base), float)
    for h in (1.0, 1e-3, 1e3):                      # 임의 스텝에서 같은 열
        k = dict(base); k["drho"] = h
        col = (np.asarray(T.residual(**k), float) - e0) / h
        assert np.abs(col - M[:, 0]).max() < 1e-11 * max(np.abs(M[:, 0]).max(), 1.0)


# ═══════════════════════════════ ★ 질량행렬 닫힌형
@pytest.mark.parametrize("seed", [0, 5, 9])
def test_mass_matrix_closed_form_is_gamma_times_unit_upper(seed):
    """★★ 발견:  M = γ (I + e₀ vᵀ).

    l=0 행:  γ(ρ̇ + v·q̇)  ← ⊥ρ̇ = γρ̇ 와 D^aq_a 의 γv_B q̇_B 가 합쳐진 것
    l=1 행:  γ q̇_A 만    ← D^bπ_ba 는 π̇ (이 블록 밖) 로 가므로 q̇ 결합이 없다
    ⇒ 상삼각.  역행렬이 해석적이라 **선형해 없이** 풀 수 있다.
    """
    rng = np.random.default_rng(seed)
    kw = _rand_kw(rng)
    M = T.mass_matrix(**kw)
    v = np.asarray(kw["v"], float)
    gam = 1.0 / np.sqrt(1.0 - v @ v)
    want = gam * (np.eye(4) + np.outer(np.eye(4)[0], np.r_[0.0, v]))
    assert np.abs(M - want).max() < 1e-13, (M, want)
    # 모듈이 노출한 닫힌형과도 일치 (독립 표현)
    assert np.abs(M - T.mass_matrix_closed_form(v)).max() < 1e-13


def test_mass_matrix_is_upper_triangular():
    """하삼각부가 정확히 0 — l=1 행이 ρ̇ 에 의존하지 않는다."""
    rng = np.random.default_rng(4)
    M = T.mass_matrix(**_rand_kw(rng))
    assert np.abs(np.tril(M, -1)).max() < 1e-15


def test_analytic_inverse_matches():
    """M⁻¹ = γ⁻¹(I − e₀ vᵀ) — 닫힌형 역행렬이 수치해와 일치."""
    rng = np.random.default_rng(6)
    kw = _rand_kw(rng)
    M = T.mass_matrix(**kw)
    v = np.asarray(kw["v"], float)
    gam = 1.0 / np.sqrt(1.0 - v @ v)
    inv = (np.eye(4) - np.outer(np.eye(4)[0], np.r_[0.0, v])) / gam
    assert np.abs(inv @ M - np.eye(4)).max() < 1e-13


# ═══════════════════════════════ 조건수 (유효 tilt 범위를 명시)
def test_conditioning_is_benign_up_to_extreme_tilt():
    """★ |v| → 0.9 까지 cond(M) ≤ 2.4 — 질량행렬은 극단 tilt 에서도 온순하다.

    (조용히 쓰지 않고 측정해 보고한다: 0.1→1.11, 0.5→1.64, 0.9→2.39)
    """
    scan = T.tilt_scan(vmax=0.9, n=10)
    conds = [c for _, c, _ in scan]
    assert conds[0] == pytest.approx(1.0, abs=1e-12)
    assert max(conds) < 3.0, conds
    assert all(b >= a - 1e-12 for a, b in zip(conds, conds[1:])), conds


def test_vorticity_grows_with_tilt():
    """다축 tilt 크기와 함께 |ω| 가 단조증가 (0 에서 8.4e−2 까지)."""
    scan = T.tilt_scan(vmax=0.9, n=10)
    ws = [w for _, _, w in scan]
    assert ws[0] == 0.0
    assert all(b >= a - 1e-15 for a, b in zip(ws, ws[1:])), ws
    assert ws[-1] > 1e-2


def test_signs_match_h5b_and_h1():
    """부호 표가 H5-b 확정값 및 H1 의 σ 부호와 일관."""
    from bianchi.matter import hierarchy as H
    assert T.SIGNS["A"] == H.SIGMA_SIGNS["A"]
    assert T.SIGNS["B"] == H.SIGMA_SIGNS["B"]
    assert T.SIGNS["C"] == H.SIGMA_SIGNS["C"]
    assert (T.SIGNS["D"], T.SIGNS["E"], T.SIGNS["Omega"]) == (+1.0, -1.0, +1.0)
    assert (T.SIGNS["divcon"], T.SIGNS["divfree"]) == (+1.0, -1.0)

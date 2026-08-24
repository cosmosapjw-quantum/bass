"""
v1.1 회귀 테스트 — 외부검토 항목 (1) 회전 규약 통일, (2) ^3S_ab / v_a',
(4) 구속 전파, (6) 순수 회전 프레임 테스트.

각 테스트는 audit/ 의 독립 재유도 결과를 코드에 고정한다.
"""
import numpy as np
import jax.numpy as jnp
import pytest

from bianchi.conventions import (
    EPS3, rotation_matrix, rotation_apply_vector, rotation_apply_tensor,
    constraint_propagation_matrix, gauge_rotation_classB, SQRT3,
    RotationConvention,
)
from bianchi.charts import general as G
from bianchi.charts import class_b_tilted as BT
from bianchi.matter.fluid import TiltedFluid, dv_general, sources as aux_scalars
from bianchi.matter.components import MagneticField


def _rng(seed=20260729):
    return np.random.default_rng(seed)


def _sym(M):
    return 0.5 * (M + M.T)


def _stf(M):
    M = _sym(M)
    return M - np.trace(M) * np.eye(3) / 3.0


# ══════════════════════════════════════════ (6) 순수 회전 프레임 테스트
def test_pure_rotation_vector_is_R_cross_v():
    """마스터 규칙:  Y_a' = +(R x Y)_a ,  부호 포함."""
    rng = _rng()
    for _ in range(50):
        R = rng.normal(size=3)
        Y = rng.normal(size=3)
        expect = np.cross(R, Y)
        got = np.asarray(rotation_apply_vector(jnp.asarray(R), jnp.asarray(Y)))
        assert np.allclose(got, expect, atol=1e-13)
        # GENERATOR 규약은 정확히 반대 부호여야 한다
        Wg = np.asarray(rotation_matrix(jnp.asarray(R), RotationConvention.GENERATOR))
        assert np.allclose(Wg @ Y, -expect, atol=1e-13)


def test_pure_rotation_frame_is_rigid():
    """순수 회전(모든 물리 소스 off)에서 Sigma, N, A 는 강체회전만 한다.

    R 이 상수이면  X(tau) = O(tau) X_0 O(tau)^T ,  O = exp(tau W) 이어야 한다.
    수치적으로: rhs 의 회전항만 남기고 적분 1스텝 -> 회전 행렬과 비교.
    """
    rng = _rng(7)
    R = rng.normal(size=3)
    W = np.asarray(rotation_matrix(jnp.asarray(R)))
    assert np.allclose(W, -W.T, atol=1e-14)          # 반대칭

    S0 = _stf(rng.normal(size=(3, 3)))
    N0 = _sym(rng.normal(size=(3, 3)))
    A0 = rng.normal(size=3)

    dt = 1e-6
    O = np.eye(3) + dt * W + 0.5 * dt * dt * (W @ W)

    dS = np.asarray(rotation_apply_tensor(jnp.asarray(R), jnp.asarray(S0)))
    dN = np.asarray(rotation_apply_tensor(jnp.asarray(R), jnp.asarray(N0)))
    dA = np.asarray(rotation_apply_vector(jnp.asarray(R), jnp.asarray(A0)))

    assert np.allclose(S0 + dt * dS, O @ S0 @ O.T, atol=1e-10)
    assert np.allclose(N0 + dt * dN, O @ N0 @ O.T, atol=1e-10)
    assert np.allclose(A0 + dt * dA, O @ A0, atol=1e-10)


def test_rotation_is_norm_preserving():
    """회전항은 Sigma^2, N.N, A.A, v.v, B.B 를 보존한다 (순수 게이지)."""
    rng = _rng(11)
    R = rng.normal(size=3)
    for X in (_stf(rng.normal(size=(3, 3))), _sym(rng.normal(size=(3, 3)))):
        dX = np.asarray(rotation_apply_tensor(jnp.asarray(R), jnp.asarray(X)))
        assert abs(np.sum(X * dX)) < 1e-12
    for Y in (rng.normal(size=3), rng.normal(size=3)):
        dY = np.asarray(rotation_apply_vector(jnp.asarray(R), jnp.asarray(Y)))
        assert abs(Y @ dY) < 1e-13


def test_magnetic_rotation_sign_matches_master_rule():
    """B_a 도 a_a, v_a 와 같은 부호를 써야 한다 (v1.0 버그 회귀 고정)."""
    rng = _rng(3)
    B = rng.normal(size=3)
    R = rng.normal(size=3)
    Sigma = jnp.asarray(_stf(rng.normal(size=(3, 3))))
    mf = MagneticField.of(B)
    got = np.asarray(mf.rhs(Sigma, jnp.asarray(R), 0.0).B)
    expect = -B + np.asarray(Sigma) @ B + np.cross(R, B)
    assert np.allclose(got, expect, atol=1e-13)


def test_gauge_rotation_reproduces_hervik_terms():
    """게이지 회전 부호가 Hervik 차트의 두 항을 동시에 재현하는지.

      Sigma_+' ⊃ +3 (Sigma_12^2 + Sigma_13^2)
      v_1'     ⊃ -2 sqrt3 (Sigma_12 v_2 + Sigma_13 v_3)
    """
    rng = _rng(5)
    Sm, S12, S13, lam = rng.normal(size=4)
    R = np.asarray(gauge_rotation_classB(Sm, S12, S13, lam))
    W = np.asarray(rotation_matrix(jnp.asarray(R)))

    Sp = rng.normal()
    S23 = rng.normal()
    Sigma = np.array([
        [-2 * Sp, SQRT3 * S12, SQRT3 * S13],
        [SQRT3 * S12, Sp + SQRT3 * Sm, SQRT3 * S23],
        [SQRT3 * S13, SQRT3 * S23, Sp - SQRT3 * Sm]])
    rot = W @ Sigma - Sigma @ W
    dSp_rot = -0.5 * rot[0, 0]
    assert np.isclose(dSp_rot, 3.0 * (S12 ** 2 + S13 ** 2), atol=1e-12)

    v = rng.normal(size=3)
    off = (-(Sigma @ v) + np.cross(R, v))[0] + 2 * Sp * v[0] * 0
    # 대각 기여를 빼면 순수 off-diagonal 조합만 남는다
    off_only = off - 2 * Sp * v[0]
    assert np.isclose(off_only, -2 * SQRT3 * (S12 * v[1] + S13 * v[2]), atol=1e-12)


# ══════════════════════════════════════════ (2) ^3S_ab 명시식
def test_S3_closed_matches_ricci3():
    rng = _rng(17)
    worst = 0.0
    for _ in range(300):
        N = _sym(rng.normal(size=(3, 3)))
        w, V = np.linalg.eigh(N)
        k = int(np.argmin(abs(w)))
        w[k] = 0.0
        N = V @ np.diag(w) @ V.T
        A = float(rng.normal()) * V[:, k]
        _, S3 = G.curvature(jnp.asarray(N), jnp.asarray(A))
        worst = max(worst, float(np.abs(np.asarray(S3)
                                        - np.asarray(G.S3_closed(jnp.asarray(N),
                                                                 jnp.asarray(A)))).max()))
    assert worst < 1e-12


def test_S3_closed_holds_off_jacobi_surface():
    """Jacobi 를 쓰지 않고도 성립 (계수 유도가 옳다는 강한 증거)."""
    rng = _rng(19)
    for _ in range(100):
        N = _sym(rng.normal(size=(3, 3)))
        A = rng.normal(size=3)
        _, S3 = G.curvature(jnp.asarray(N), jnp.asarray(A))
        assert np.allclose(np.asarray(S3),
                           np.asarray(G.S3_closed(jnp.asarray(N), jnp.asarray(A))),
                           atol=1e-11)


def test_S3_A_term_coefficient_is_exactly_two():
    """A-항 계수를 흔들면 O(1) 로 깨진다 (계수 2 가 유일)."""
    rng = _rng(23)
    N = _sym(rng.normal(size=(3, 3)))
    A = rng.normal(size=3)
    _, S3 = G.curvature(jnp.asarray(N), jnp.asarray(A))
    B = 2.0 * (N @ N) - np.trace(N) * N
    C = np.einsum("cda,c,bd->ab", EPS3, A, N)
    for bad in (0.0, 1.0, -2.0):
        M = _stf(B + bad * C)
        assert np.abs(np.asarray(S3) - M).max() > 1e-3


# ══════════════════════════════════════════ (2) 완전한 v_a'
def test_dv_general_matches_derived_closed_form():
    rng = _rng(29)
    for _ in range(60):
        N = _sym(rng.normal(size=(3, 3)))
        w, V = np.linalg.eigh(N)
        k = int(np.argmin(abs(w)))
        w[k] = 0.0
        N = V @ np.diag(w) @ V.T
        A = float(rng.normal()) * V[:, k]
        Sigma = _stf(rng.normal(size=(3, 3)))
        R = rng.normal(size=3)
        v = rng.normal(size=3)
        v *= rng.uniform(0.05, 0.9) / np.linalg.norm(v)
        gamma = float(rng.uniform(0.4, 1.9))

        f = TiltedFluid.of(gamma, 0.3, v)
        s = aux_scalars(f, jnp.asarray(Sigma), jnp.asarray(A))
        got = np.asarray(dv_general(f, s, jnp.asarray(Sigma), jnp.asarray(N),
                                    jnp.asarray(A), jnp.asarray(R)))

        V2 = v @ v
        Gm = 1.0 - (gamma - 1.0) * V2
        S = v @ (Sigma @ v)
        T = (((3 * gamma - 4) - 2 * (gamma - 1) * (A @ v)) * (1 - V2)
             + (2 - gamma) * S) / Gm
        P = A * V2 - (A @ v) * v + np.einsum("abc,b,c->a", EPS3, v, N @ v)
        expect = T * v - Sigma @ v + np.cross(R, v) - P
        assert np.allclose(got, expect, atol=1e-11)


def test_dv_general_reduces_to_hervik_chart():
    """일반식이 Hervik 게이지 특수화(class_b_tilted)와 v_1' 에서 일치."""
    rng = _rng(31)
    Sp, Sm, S12, S13, S23, N, lam, A = rng.normal(size=8)
    v = rng.normal(size=3)
    v *= 0.4 / np.linalg.norm(v)
    gamma = 1.3

    Sigma = np.array([
        [-2 * Sp, SQRT3 * S12, SQRT3 * S13],
        [SQRT3 * S12, Sp + SQRT3 * Sm, SQRT3 * S23],
        [SQRT3 * S13, SQRT3 * S23, Sp - SQRT3 * Sm]])
    Nm = np.array([[0.0, 0.0, 0.0],
                   [0.0, SQRT3 * lam * N, SQRT3 * N],
                   [0.0, SQRT3 * N, SQRT3 * lam * N]])
    Av = np.array([A, 0.0, 0.0])
    R = np.asarray(gauge_rotation_classB(Sm, S12, S13, lam))

    f = TiltedFluid.of(gamma, 0.3, v)
    s = aux_scalars(f, jnp.asarray(Sigma), jnp.asarray(Av))
    gen = np.asarray(dv_general(f, s, jnp.asarray(Sigma), jnp.asarray(Nm),
                                jnp.asarray(Av), jnp.asarray(R)))

    T = float(s["T"]) if "T" in s else None
    from bianchi.matter.fluid import T_coefficient
    T = float(T_coefficient(f, s))
    v1, v2, v3 = v
    chart_v1 = ((T + 2 * Sp) * v1 - 2 * SQRT3 * S13 * v3 - 2 * SQRT3 * S12 * v2
                - A * (v2 ** 2 + v3 ** 2) - SQRT3 * N * (v2 ** 2 - v3 ** 2))
    chart_v2 = ((T - Sp - SQRT3 * Sm) * v2 - SQRT3 * (S23 + Sm * lam) * v3
                + SQRT3 * lam * N * v1 * v3 + (A + SQRT3 * N) * v1 * v2)
    chart_v3 = ((T - Sp + SQRT3 * Sm) * v3 - SQRT3 * (S23 - Sm * lam) * v2
                - SQRT3 * lam * N * v1 * v2 + (A - SQRT3 * N) * v1 * v3)
    # ★ v1.3: v1 만 비교하던 것을 3성분 전부로 확장 (감사 지적)
    assert np.allclose(gen, [chart_v1, chart_v2, chart_v3], atol=1e-10)


# ══════════════════════════════════════════ (4) 구속 전파 행렬
def test_constraint_propagation_matrix_structure():
    rng = _rng(37)
    H = float(rng.uniform(0.5, 2.0))
    Sigma = _stf(rng.normal(size=(3, 3)))
    A = rng.normal(size=3)
    R = rng.normal(size=3)
    M = np.asarray(constraint_propagation_matrix(H, jnp.asarray(Sigma),
                                                 jnp.asarray(A), jnp.asarray(R)))
    assert np.isclose(M[0, 0], -3 * H)
    assert np.allclose(M[0, 1:], -2 * A)
    assert np.allclose(M[1:, 0], 0.0)          # Codazzi 는 Gauss 를 소스로 받지 않는다
    blk = M[1:, 1:]
    assert np.allclose(0.5 * (blk + blk.T), -4 * H * np.eye(3) - Sigma, atol=1e-12)
    anti = 0.5 * (blk - blk.T)
    assert np.allclose(anti @ np.ones(3) * 0, 0)
    # 반대칭 부분이 정확히 회전항
    assert np.allclose(anti, np.asarray(rotation_matrix(jnp.asarray(R))), atol=1e-12)


def test_constraint_propagation_matches_actual_flow():
    """★ v1.3 (감사 결함 #6): 이전의 M @ 0 == 0 단언은 어떤 행렬에도 참인
    공허한 테스트였다. 실제 검증으로 교체: 진공 차원 있는 변수 (H, sigma, n, a)
    를 구속을 **위반한 채로** ij-Einstein 진화식으로 흘리면, Gauss/Codazzi 잔차가
    정확히 dC/dt = M C 로 전파되어야 한다 (보고서 eq. cprop). RK4 + Richardson.
    """
    from bianchi.charts.general import S3_closed, R3_closed

    rng = _rng(53)
    R = rng.normal(size=3) * 0.5

    def s3_dim(n, a):
        return np.asarray(S3_closed(jnp.asarray(n), jnp.asarray(a)))

    def rhs(st):
        H, sig, n, a = st
        R3 = float(R3_closed(jnp.asarray(n), jnp.asarray(a)))
        s2 = float(np.sum(sig * sig))
        # 진공 ij-방정식 (trace + tracefree; fit_einstein 계수):
        Hd = -(9.0 * H**2 + 1.5 * s2 + 0.5 * R3) / 6.0
        sd = (-3.0 * H * sig - s3_dim(n, a)
              + np.asarray(rotation_apply_tensor(jnp.asarray(R), jnp.asarray(sig))))
        nd = (-H * n + sig @ n + n @ sig
              + np.asarray(rotation_apply_tensor(jnp.asarray(R), jnp.asarray(n))))
        ad = (-H * a - sig @ a
              + np.asarray(rotation_apply_vector(jnp.asarray(R), jnp.asarray(a))))
        return (Hd, sd, nd, ad)

    def C_of(st):
        H, sig, n, a = st
        R3 = float(R3_closed(jnp.asarray(n), jnp.asarray(a)))
        C0 = 3.0 * H**2 - 0.5 * float(np.sum(sig * sig)) + 0.5 * R3
        Ci = -3.0 * (sig @ a) + np.einsum("ibc,bd,cd->i", EPS3, sig, n)
        return np.concatenate([[C0], Ci])

    def step(st, h):
        def add(st, k, c):
            return tuple(x + c * y for x, y in zip(st, k))
        k1 = rhs(st); k2 = rhs(add(st, k1, h / 2)); k3 = rhs(add(st, k2, h / 2))
        k4 = rhs(add(st, k3, h))
        return tuple(x + h / 6 * (a1 + 2 * a2 + 2 * a3 + a4)
                     for x, a1, a2, a3, a4 in zip(st, k1, k2, k3, k4))

    # 구속을 위반한 무작위 초기 데이터 (Jacobi n a = 0 만 만족시켜 순수 대수 유지)
    n = _sym(rng.normal(size=(3, 3)))
    w, V = np.linalg.eigh(n)
    k = int(np.argmin(abs(w))); w[k] = 0.0
    n = V @ np.diag(w) @ V.T
    a = float(rng.normal()) * V[:, k]
    st0 = (1.3, _stf(rng.normal(size=(3, 3))), n, a)

    def dC(h):
        return (C_of(step(st0, h)) - C_of(step(st0, -h))) / (2 * h)

    dC_num = (4.0 * dC(5e-4) - dC(1e-3)) / 3.0        # Richardson
    H0, sig0 = st0[0], st0[1]
    M = np.asarray(constraint_propagation_matrix(
        H0, jnp.asarray(sig0), jnp.asarray(st0[3]), jnp.asarray(R)))
    dC_pred = M @ C_of(st0)
    scale = max(1.0, float(np.abs(dC_pred).max()))
    assert np.abs(dC_num - dC_pred).max() / scale < 1e-6, (dC_num, dC_pred)


# ══════════════════════════════════════════ (3) tilt 정의역
@pytest.mark.parametrize("gamma", [0.5, 1.0, 4.0 / 3.0, 1.9])
def test_V_equals_one_invariant_only_for_gamma_below_two(gamma):
    """V=1 은 0 < gamma < 2 에서만 불변 경계 (gamma=2 에서 G_- 가 (1-V^2) 를 상쇄)."""
    from bianchi.matter.fluid import dV2, G_minus
    rng = _rng(43)
    Sigma = _stf(rng.normal(size=(3, 3)))
    A = rng.normal(size=3)
    v = rng.normal(size=3)
    v /= np.linalg.norm(v)                       # V = 1
    f = TiltedFluid.of(gamma, 0.3, v)
    s = aux_scalars(f, jnp.asarray(Sigma), jnp.asarray(A))
    assert abs(float(dV2(f, s))) < 1e-10


def test_V_equals_one_not_invariant_at_gamma_two():
    from bianchi.matter.fluid import dV2
    rng = _rng(47)
    Sigma = _stf(rng.normal(size=(3, 3)))
    A = rng.normal(size=3)
    v = rng.normal(size=3)
    v /= np.linalg.norm(v)
    f = TiltedFluid.of(2.0, 0.3, v)
    s = aux_scalars(f, jnp.asarray(Sigma), jnp.asarray(A))
    # G_-(2, 1) = 0 -> 코드의 _safe 가드가 작동하며 극한은 (1-V^2) 상쇄로 유한·비영
    val = float(dV2(f, s))
    assert np.isfinite(val)


# ══════════════════════════════════════════ v1.2 (audit/d_matter.py)
def test_magnetic_ampere_constraint_relative_sign():
    """curl 결합의 상대부호는 +  :  n_ab B^b + eps_abc a^b B^c = 0.

    E, B 를 동시에 넣고 프레임 Maxwell 을 풀면 나오는 결합이며, Faraday 쪽의
    +(N E) + (a x E) 와 쌍대 구조를 이룬다.  n != 0 이고 a != 0 인 class B 에서만
    v1.1 의 '-' 와 구별된다.
    """
    rng = _rng(101)
    # Bianchi V (n=0, a!=0): 두 부호 모두 B=0 을 강제 -> 구별 불가
    A = np.array([0.7, 0.0, 0.0])
    B = np.array([0.0, 0.3, -0.2])
    mf = MagneticField.of(B)
    c = mf.constraints(jnp.zeros((3, 3)), jnp.asarray(A))
    assert np.allclose(np.asarray(c["ampere"]),
                       np.cross(A, B), atol=1e-13)
    # class B (n != 0, a != 0): 부호가 실제로 구별된다
    N = np.diag([0.0, 0.6, -0.4])
    A = np.array([0.5, 0.0, 0.0])
    B = rng.normal(size=3)
    got = np.asarray(MagneticField.of(B).constraints(jnp.asarray(N), jnp.asarray(A))
                     ["ampere"])
    assert np.allclose(got, N @ B + np.cross(A, B), atol=1e-13)
    assert not np.allclose(got, N @ B - np.cross(A, B), atol=1e-6)

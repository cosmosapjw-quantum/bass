"""M0 완료 기준 — PR-02/03/04/05.

PR-02: 유도 엔진 L0~L4 사다리
PR-03: 규약 왕복, 함정 가드
PR-04: 11 유형 + 예외형 분류, 두 kappa 경로 일치
PR-05: 오라클 A~F 전부 PASS + **커널 오염이 A 를 통과하고 B·D 에 걸리는 것**
"""
import numpy as np
import pytest
import sympy as sp

import bianchi
from bianchi import algebra as alg
from bianchi import conventions as cv
from bianchi.symbolic import frame, oracles

I3 = range(3)
R3 = sp.sqrt(3)


# ================================================================ PR-02
def test_L0_unit_three_sphere():
    """Koszul/Riemann 기계 앵커: n=diag(2,2,2) 는 단위 둥근 S^3."""
    n = [[2 if i == j else 0 for j in I3] for i in I3]
    Ric = frame.ricci3(n, [0, 0, 0])
    assert sp.simplify(Ric - 2 * sp.eye(3)).norm() == 0
    assert sp.simplify(sp.trace(Ric) - 6) == 0


def test_L1_R3_closed_form():
    n = sp.Matrix(3, 3, lambda i, j: sp.Symbol(f"n{min(i,j)}{max(i,j)}"))
    a = sp.Matrix([sp.Symbol(f"a{i}") for i in I3])
    R3sym, _, _ = frame.curvature_pieces(
        [[n[i, j] for j in I3] for i in I3], [a[i] for i in I3]
    )
    assert sp.simplify(R3sym - frame.R3_closed_form(n, a)) == 0


def test_L2_WE_curvature_and_wainwright_hsu():
    """K = 1/12[...], ^3S_alpha WE 형태, WH 계 완전 재현."""
    N1, N2, N3 = sp.symbols("N_1 N_2 N_3")
    N = sp.diag(N1, N2, N3)
    _, S3, K = frame.curvature_pieces([[N[i, j] for j in I3] for i in I3], [0, 0, 0])
    assert sp.simplify(
        K - sp.Rational(1, 12) * (N1**2 + N2**2 + N3**2
                                  - 2 * (N1*N2 + N2*N3 + N3*N1))
    ) == 0
    Nl = [N1, N2, N3]
    for al, (be, ga) in zip(I3, [(1, 2), (2, 0), (0, 1)]):
        we = sp.Rational(1, 3) * (
            Nl[al] * (2*Nl[al] - Nl[be] - Nl[ga]) - (Nl[be] - Nl[ga])**2
        )
        assert sp.simplify(S3[al, al] - we) == 0

    (Sp, Sm, n1, n2, n3, g), (dSp, dSm, dN1, dN2, dN3), aux = frame.wainwright_hsu()
    q = aux["q"]
    assert sp.simplify(dSp - (-(2 - q)*Sp - sp.Rational(1, 6) *
                              ((n2 - n3)**2 - n1*(2*n1 - n2 - n3)))) == 0
    assert sp.simplify(dSm - (-(2 - q)*Sm - (n3 - n2)*(n1 - n2 - n3)/(2*R3))) == 0
    assert sp.simplify(dN1 - (q - 4*Sp)*n1) == 0
    assert sp.simplify(dN2 - (q + 2*Sp + 2*R3*Sm)*n2) == 0
    assert sp.simplify(dN3 - (q + 2*Sp - 2*R3*Sm)*n3) == 0


def test_L3_omega_identity_from_derived_system():
    (Sp, Sm, N1, N2, N3, g), rhs, aux = frame.wainwright_hsu()
    flow = dict(zip((Sp, Sm, N1, N2, N3), (rhs[0], rhs[1], rhs[2], rhs[3], rhs[4])))
    d = oracles.lie_derivative(aux["Omega"], flow)
    assert sp.simplify(d - (2*aux["q"] - (3*g - 2)) * aux["Omega"]) == 0


def test_L4_codazzi_plus_eps_unique():
    """접속에서 직접 유도한 운동량 구속은 +eps 에만 비례상수가 존재."""
    H = sp.Symbol("H")
    n = sp.Matrix(3, 3, lambda i, j: sp.Symbol(f"n{min(i,j)}{max(i,j)}"))
    sgk = {x: sp.Symbol("sg" + x) for x in ["00", "11", "01", "02", "12"]}
    sg = sp.Matrix([[sgk["00"], sgk["01"], sgk["02"]],
                    [sgk["01"], sgk["11"], sgk["12"]],
                    [sgk["02"], sgk["12"], -sgk["00"] - sgk["11"]]])
    a = sp.Matrix([sp.Symbol(f"a{i}") for i in I3])
    mom = frame.codazzi_from_connection(
        [[n[i, j] for j in I3] for i in I3], [a[i] for i in I3], sg, H
    )
    lam = sp.Symbol("lam")
    free = sorted(
        set().union(*[m.free_symbols for m in mom]) - {lam}, key=str
    )
    got = {}
    for s in (+1, -1):
        cand = frame.codazzi_standard(n, [a[i] for i in I3], sg, eps_sign=s)
        # lam 은 '상수' 여야 한다 -> 3성분 전체의 다항식 계수계를 동시에 푼다
        eqs = []
        for al in I3:
            poly = sp.Poly(sp.expand(mom[al] - lam * cand[al]), *free)
            eqs.extend(poly.coeffs())
        got[s] = sp.solve(eqs, lam, dict=True)
    assert got[+1] == [{lam: 1}], f"+eps 해 = {got[+1]}"
    assert got[-1] == [], f"-eps 에 상수해가 존재해서는 안 됨: {got[-1]}"
    assert cv.CODAZZI_EPS_SIGN == +1


# ================================================================ PR-03
def test_normalization_roundtrip():
    N = np.array([1.3, -0.7, 0.4])
    back = cv.N_ringstrom_to_we(cv.N_we_to_ringstrom(N))
    assert np.allclose(np.asarray(back), N, atol=1e-15)


def test_factor_nine_trap_is_real():
    """WE 의 S_pm 과 Ringstrom 의 K 를 섞으면 Omega' 항등식이 깨진다."""
    good = oracles.class_a_system()
    bad = oracles.class_a_system(ringstrom_K=True)
    ok_g, _ = oracles.random_zero_check(oracles.oracle_A_omega(good), good["syms"])
    ok_b, _ = oracles.random_zero_check(oracles.oracle_A_omega(bad), bad["syms"], n=6)
    assert ok_g and not ok_b


def test_shear_scalar_type_separation():
    s = cv.ShearScalar(1.0, "WE")
    assert np.isclose(s.to("theta").value, 1.0 / cv.SQRT3)
    assert np.isclose(s.to("theta").to("WE").value, 1.0)
    with pytest.raises(TypeError):
        _ = s + cv.ShearScalar(1.0, "theta")


def test_tracefree_helper():
    M = np.asarray(cv.tracefree_from_5(0.3, -0.2, 0.1, -0.05, 0.07))
    assert abs(np.trace(M)) < 1e-15
    assert np.allclose(M, M.T)
    five = np.asarray(cv.five_from_tracefree(M))
    assert np.allclose(np.asarray(cv.tracefree_from_5(*five)), M)


def test_gauge_rotation_returns_all_three():
    """함정 2: 게이지가 회전 3개를 전부 소모한다."""
    Sm_, S12, S13, lam = 0.11, 0.23, -0.17, 0.4
    R = np.asarray(cv.gauge_rotation_classB(Sm_, S12, S13, lam))
    assert R.shape == (3,)
    assert np.abs(R).min() > 0, "세 성분 모두 비자명이어야 한다"
    # ★ v1.1 부호 정정 (외부검토 R1): COMMUTATOR 규약에서 A_a' ⊃ +(R x A)_a 이므로
    #   A_2' = 0 -> R_3 = +sqrt3 Sigma_12 ,  A_3' = 0 -> R_2 = -sqrt3 Sigma_13.
    #   v1.0 은 GENERATOR 부호를 반환하면서 소비 측은 COMMUTATOR 였다.
    assert np.isclose(R[0], cv.SQRT3 * Sm_ * lam)      # N_-' = 0
    assert np.isclose(R[1], -cv.SQRT3 * S13)           # A_3' = 0
    assert np.isclose(R[2], cv.SQRT3 * S12)            # A_2' = 0


def test_A_exceptional_no_rescale():
    assert cv.A_EXCEPTIONAL_RESCALE == 1.0


# ================================================================ PR-04
@pytest.mark.parametrize("name", list(alg.CANONICAL))
def test_classify_all_types(name):
    n, a = alg.CANONICAL[name]
    t = alg.classify(n, a)
    assert np.abs(alg.jacobi_residual(n, a)).max() < 1e-12
    if name in ("VI_h", "VII_h"):
        assert t.name == name
    elif name == "VI*_-1/9":
        assert t.exceptional and t.name == "VI*_-1/9"
        assert np.isclose(t.kappa, -9.0)
    else:
        assert t.name == name


def test_kappa_two_paths_agree():
    for name in ("V", "IV", "III", "VI_h", "VII_h", "VI*_-1/9"):
        n, a = alg.CANONICAL[name]
        k_diag = alg.kappa_from_diagonal(n[1], n[2], a[0])
        k_basis = alg.kappa_basis_independent(np.diag(n), a)
        assert np.isclose(k_diag, k_basis), f"{name}: {k_diag} vs {k_basis}"


def test_kappa_basis_independent_under_rotation():
    """비대각 프레임에서도 같은 kappa (Layer 0 진단의 근거)."""
    n, a = alg.CANONICAL["VI_h"]
    rng = np.random.default_rng(3)
    for _ in range(5):
        v = rng.normal(size=3); v /= np.linalg.norm(v)
        th = rng.uniform(0, 2*np.pi)
        Kx = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
        Rm = np.eye(3) + np.sin(th)*Kx + (1-np.cos(th))*(Kx@Kx)
        n_r = Rm @ np.diag(n) @ Rm.T
        a_r = Rm @ a
        assert np.isclose(
            alg.kappa_basis_independent(n_r, a_r),
            alg.kappa_basis_independent(np.diag(n), a),
        )


def test_exceptional_via_detL_not_hardcoded():
    """예외형 판정이 det L = 3(9A^2 + n2n3) 에서 나온다."""
    assert np.isclose(alg.det_L(3.0, -3.0, 1.0), 0.0)
    assert not np.isclose(alg.det_L(1.0, -1.0, 1.0), 0.0)


def test_structure_constants_roundtrip():
    for name, (n, a) in alg.CANONICAL.items():
        C = alg.structure_constants(n, a)
        n2, a2 = alg.decompose(C)
        assert np.allclose(n2, np.diag(n), atol=1e-12), name
        assert np.allclose(a2, a, atol=1e-12), name


# ================================================================ PR-05
def test_oracles_all_pass_on_correct_system():
    s = oracles.class_a_system()
    syms = s["syms"]
    ok, bad = oracles.random_zero_check(oracles.oracle_A_omega(s), syms)
    assert ok, bad
    for e in oracles.oracle_B_lrs(s):
        assert sp.simplify(e) == 0
    for e in oracles.oracle_C_invariant_submanifolds(s):
        assert sp.simplify(e) == 0
    for e in oracles.oracle_D_cyclic(s):
        assert sp.simplify(e) == 0
    assert sp.simplify(oracles.oracle_E_kasner(s)) == 0


def test_obvious_transcription_errors_are_caught_by_A():
    for kw in ({"flip_Sm": True}, {"flip_N2": True}):
        s = oracles.class_a_system(**kw)
        ok, _ = oracles.random_zero_check(oracles.oracle_A_omega(s), s["syms"], n=6)
        assert not ok, f"오라클 A 가 {kw} 를 검출하지 못했다"


def test_kernel_passes_A_but_caught_by_B_and_D():
    """★ 오라클 A 의 사각지대를 테스트로 박제한다."""
    s = oracles.inject_kernel()
    syms = s["syms"]
    ok_A, _ = oracles.random_zero_check(oracles.oracle_A_omega(s), syms)
    assert ok_A, "커널 오염이 A 를 통과해야 한다 (이것이 사각지대의 정의)"
    B = oracles.oracle_B_lrs(s)
    assert any(sp.simplify(e) != 0 for e in B), "오라클 B 가 커널을 검출해야 한다"
    D = oracles.oracle_D_cyclic(s)
    assert any(sp.simplify(e) != 0 for e in D), "오라클 D 가 커널을 검출해야 한다"


def test_blind_spots_documented():
    assert "A_omega" in oracles.ORACLE_BLIND_SPOTS
    assert "class_b_coefficients" in oracles.ORACLE_BLIND_SPOTS

"""
J1 · **계수공간 PSTF** — 3^l 폐기 1절편의 게이트 (57차).

측정:
  · 규약 잠금: ∫Z₁Z₂Z₃ ≡ sympy real_gaunt (정확구적, ≤5e−15 표본).
  · 사전 D_l=(2l+1)!!/(4π l!) 로 정준기저 직교정규 (l≤6); SVD 기저와는
    직교행렬로 연결 (좌표변환 가역).
  · 두 경로: dense 사영(A) ≡ 닫힌형(B) — 3연산 × 검증가능 전 l, ≤1.3e−15.
    outer 는 자유상수 없는 곱-사영 사전 (첫 시도 합치); c2 는 수반항등
    R_c2(l)=R_out(l+2) (1차 위상조립 반증 후 유도 정정); c1 은 널벡터
    고유값 −1/√6 + 닫힌형 R_c1(l)=2(2l+3)/l·√(π/30) (측정→인식→이중검증).
  · 반증 기록: c1 1차 조립의 잉여인자 √D₂/(4π)=0.061477 (관측비율과 정확
    일치), c2 1차의 l-의존 비율 — 비율의 (m',m,k)-불변성이 Wigner-Eckart
    인수분해를 기계정밀로 증명했었다 (반증이 구조를 확인한 사례).
  · l>6 (dense 불가): e_{m=+l} 널 고유게이트 (l=10, 비순환), rg 대칭성
    (독립 계산된 (8,10)↔(10,8) 표 전치일치), 선택규칙 지름길 무손실.
"""
import numpy as np
import pytest
import sympy as sp

from bianchi.matter import pstf_coeff as PC
from bianchi.matter.hierarchy import (_contract_one, _contract_two,
                                      _outer_sigma, is_pstf)


# ---------------------------------------------------------------- 기저·사전
@pytest.mark.parametrize("l", [1, 2, 3, 4, 5, 6])
def test_canonical_basis_is_orthonormal_pstf_and_dictionary_holds(l):
    """★★ U_lm 직교정규 + PSTF + D_l 닫힌형 = 측정 노름."""
    B = PC.U_basis(l)                               # 조립 자체가 직교정규 검증
    assert B.shape == (3**l, 2*l + 1)
    for m in (-l, 0, l):
        T = PC.canonical_tensor(l, m)
        assert is_pstf(T, tol=1e-11)
        assert abs((T.ravel() @ T.ravel()) - PC.D_norm(l)) <= 1e-12 * PC.D_norm(l)


def test_convention_locked_to_real_gaunt():
    """★ 정준 Z 구성 ≡ sympy real_gaunt (정확구적 표본 3건)."""
    from sympy.physics.wigner import real_gaunt
    ng = 16
    tg, tw = np.polynomial.legendre.leggauss(ng)
    ph = 2*np.pi*np.arange(2*ng)/(2*ng)
    CT, PH = np.meshgrid(tg, ph, indexing="ij")
    ST = np.sqrt(1 - CT**2)
    X, Y, Z = ST*np.cos(PH), ST*np.sin(PH), CT
    W = np.repeat(tw[:, None], 2*ng, 1) * (2*np.pi/(2*ng))

    def fn(l, m):
        return sp.lambdify((PC._x, PC._y, PC._z), PC.solid_expr(l, m), "numpy")

    for (l1, l2, l3, m1, m2, m3) in [(2, 2, 2, 0, 0, 0), (4, 2, 2, 3, 1, 2),
                                     (4, 2, 2, -3, 2, -1)]:
        num = float((fn(l1, m1)(X, Y, Z) * fn(l2, m2)(X, Y, Z)
                     * fn(l3, m3)(X, Y, Z) * W).sum())
        assert abs(num - float(real_gaunt(l1, l2, l3, m1, m2, m3))) <= 5e-15


def test_roundtrip_and_svd_change_of_basis_is_orthogonal(l=4):
    """★ 왕복 + 기존 SVD 기저와의 좌표변환이 직교행렬 (두 표현 등가)."""
    rng = np.random.default_rng(3)
    c = rng.standard_normal(2*l + 1)
    assert np.abs(PC.to_ccoef(PC.from_ccoef(c, l), l) - c).max() <= 1e-13
    from bianchi.matter.tilted_mass import pstf_basis
    O = pstf_basis(l).T @ PC.U_basis(l)
    assert np.abs(O.T @ O - np.eye(2*l + 1)).max() <= 1e-11


# ---------------------------------------------------------------- 두 경로
def test_dense_vs_closed_all_ops_all_l():
    """★★ J1 의 심판: 경로 A ≡ 경로 B, 3연산 × 검증가능 전 l ≤ 5e−15."""
    from audit.j1_coeff_derivation import dense_vs_closed_sweep
    sweep = dense_vs_closed_sweep()
    assert max(sweep.values()) <= 5e-15, sweep


def test_r_c1_closed_form_matches_independent_gaunt_route():
    """★ R_c1(l)=2(2l+3)/l·√(π/30) — 측정 인식 닫힌형 = Gaunt 산술, l≤12."""
    from audit.j1_coeff_derivation import closed_form_matches_gaunt_route
    res = closed_form_matches_gaunt_route()
    assert max(res.values()) <= 1e-14, res


def test_falsified_first_attempt_factor_is_pinned():
    """★ 반증 박제: c1 1차 잉여인자 √D₂/(4π) = 관측비율 0.0614766…."""
    assert abs(np.sqrt(PC.D_norm(2)) / (4*np.pi) - 0.06147744864087) <= 1e-12


def test_adjoint_identity_is_exact_dense(l=4):
    """★★ c2 유도의 초석: <pstf(J⊗σ),K>_l = <J, c2(K,σ)>_{l−2} (상수 1 정확)."""
    rng = np.random.default_rng(11)
    J = PC.from_ccoef(rng.standard_normal(2*(l-2) + 1), l - 2)
    K = PC.from_ccoef(rng.standard_normal(2*l + 1), l)
    sig = PC.from_ccoef(rng.standard_normal(5), 2)
    lhs = float(np.tensordot(_outer_sigma(J, sig), K, axes=l))
    rhs = float(np.tensordot(J, _contract_two(K, sig), axes=l - 2))
    assert abs(lhs - rhs) <= 1e-13 * max(1.0, abs(lhs))


def test_end_to_end_pipeline_matches_dense(l=4):
    """★ 무작위 상태·σ 로 계수 파이프라인 == dense 파이프라인 (3연산)."""
    rng = np.random.default_rng(5)
    sig = PC.from_ccoef(rng.standard_normal(5), 2)
    s5 = PC.sigma_to_c5(sig)
    for op, l_in, blk, fn in (("outer", l - 2, PC.outer_block, _outer_sigma),
                              ("c1", l, PC.c1_block, _contract_one),
                              ("c2", l + 2, PC.c2_block, _contract_two)):
        c_in = rng.standard_normal(2*l_in + 1)
        J = PC.from_ccoef(c_in, l_in)
        want = PC.to_ccoef(fn(np.asarray(J, float), sig), l)
        got = PC.apply_block(blk(l), c_in, s5)
        assert np.abs(want - got).max() <= 5e-14, op


# ---------------------------------------------------------------- l > 6
def test_dense_wall_is_explicit_and_coeff_path_crosses_it():
    """★★ 구조 전환의 요점: dense 는 l=7 에서 명시 거부, 계수 경로는 l=10 가동."""
    with pytest.raises(ValueError, match="경로 B"):
        PC.canonical_tensor(7, 0)
    G = PC.c1_block(10)                             # 3^10=59049 은 어디에도 없다
    assert G.shape == (21, 21, 5)
    assert np.isfinite(G).all() and np.abs(G).max() > 0.0


def test_null_eigen_gate_at_l10():
    """★★ 비순환 l=10 게이트: e_{m=+10} 은 c1(U₂₀) 고유벡터, 고유값 −1/√6."""
    from audit.j1_coeff_derivation import null_eigen_gate
    assert null_eigen_gate(10) <= 1e-14


def test_rg_symmetry_between_independent_tables():
    """★ rg 완전대칭: 독립 계산된 (8,10)·(10,8) 표가 전치로 일치 —
    수반항등 R_c2(8)=R_out(10) 과 함께 c2/outer 의 l>6 정합을 닫는다."""
    A = PC.c2_block(8)                              # rg(8,10,2) 사용
    B = PC.outer_block(10)                          # rg(10,8,2) 사용
    assert np.abs(A - B.transpose(1, 0, 2)).max() <= 1e-14


def test_m_selection_shortcut_loses_nothing(l=3):
    """★ _rg_table 의 m-지름길 무손실: 지름길 없는 전수 계산과 일치."""
    from sympy.physics.wigner import real_gaunt
    G = PC._rg_table(l, l)
    for i, mp in enumerate(range(-l, l + 1)):
        for j, m in enumerate(range(-l, l + 1)):
            for k, mk in enumerate(range(-2, 3)):
                full = float(real_gaunt(l, l, 2, mp, m, mk))
                assert abs(G[i, j, k] - full) <= 1e-15, (mp, m, mk)


def test_sigma_roundtrip_and_shapes():
    rng = np.random.default_rng(9)
    sig = PC.from_ccoef(rng.standard_normal(5), 2)
    assert np.abs(PC.from_ccoef(PC.sigma_to_c5(sig), 2) - sig).max() <= 1e-14
    assert PC.outer_block(5).shape == (11, 7, 5)
    assert PC.c2_block(3).shape == (7, 11, 5)


def test_r_c1_theorem_holds_symbolically():
    """★ 리뷰 승격: R_c1 닫힌형은 인식이 아니라 **정리** (기호 잔차 0)."""
    from audit.j1_coeff_derivation import r_c1_theorem_symbolic
    assert r_c1_theorem_symbolic() == 0


def test_m_selection_shortcut_lossless_on_mixed_tables():
    """★ 리뷰 MINOR 2: 혼합쌍 (4,2)·(2,4) 전수 무손실 (전치시험의 맹점 보완)."""
    from sympy.physics.wigner import real_gaunt
    for lo, li in ((4, 2), (2, 4)):
        G = PC._rg_table(lo, li)
        for i, mp in enumerate(range(-lo, lo + 1)):
            for j, m in enumerate(range(-li, li + 1)):
                for k, mk in enumerate(range(-2, 3)):
                    assert abs(G[i, j, k]
                               - float(real_gaunt(lo, li, 2, mp, m, mk))) \
                        <= 1e-15, (lo, li, mp, m, mk)


def test_convention_pinned_externally_to_scipy():
    """★ 리뷰 MINOR 3: 부호지표 게이지까지 외부 핀 — scipy 실 SH 와 전 (l,m)
    부호반전 0 (내부 게이트는 Z→±Z 게이지에 불변이라 이 핀이 필요하다)."""
    from scipy.special import sph_harm_y
    rng = np.random.default_rng(2)
    th, ph = rng.uniform(0.2, 2.9, 8), rng.uniform(0.0, 6.2, 8)
    xyz = np.stack([np.sin(th)*np.cos(ph), np.sin(th)*np.sin(ph), np.cos(th)])
    for l in range(1, 7):
        for m in range(-l, l + 1):
            mine = sp.lambdify((PC._x, PC._y, PC._z), PC.solid_expr(l, m),
                               "numpy")(*xyz)
            Y = sph_harm_y(l, abs(m), th, ph)
            if m > 0:
                ref = np.sqrt(2.0) * (-1)**m * Y.real
            elif m < 0:
                ref = np.sqrt(2.0) * (-1)**m * Y.imag
            else:
                ref = Y.real
            assert np.abs(mine - ref).max() <= 2e-14, (l, m)


def test_real_gaunt_validated_by_quadrature_at_l10():
    """★ 리뷰 MINOR 4: l>6 의 real_gaunt 자체를 정확구적으로 독립 검증
    ((10,8,2)·(10,10,2) 혼합부호 표본 — sympy 신뢰의 in-repo 근거)."""
    from sympy.physics.wigner import real_gaunt
    ng = 40
    tg, tw = np.polynomial.legendre.leggauss(ng)
    ph = 2*np.pi*np.arange(128)/128
    CT, PH = np.meshgrid(tg, ph, indexing="ij")
    ST = np.sqrt(1 - CT**2)
    X, Y, Z = ST*np.cos(PH), ST*np.sin(PH), CT
    W = np.repeat(tw[:, None], 128, 1) * (2*np.pi/128)

    def fn(l, m):
        return sp.lambdify((PC._x, PC._y, PC._z), PC.solid_expr(l, m), "numpy")

    cases = [(10, 8, 2, 9, 7, 2), (10, 8, 2, -9, -7, 2), (10, 8, 2, 5, 7, -2),
             (10, 10, 2, 10, 10, 0), (10, 10, 2, -3, -5, 2)]
    for (l1, l2, l3, m1, m2, m3) in cases:
        num = float((fn(l1, m1)(X, Y, Z) * fn(l2, m2)(X, Y, Z)
                     * fn(l3, m3)(X, Y, Z) * W).sum())
        assert abs(num - float(real_gaunt(l1, l2, l3, m1, m2, m3))) <= 1e-13

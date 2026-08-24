"""I1b · 계층 N-항의 계수공간 닫힘 (66–67차) — PLAN §1 게이트.

★★ 반증 박제 (67차): 1판 α 배정 (α_up≡1, α_dn=l/(2l+1)) 은 계수↔함수 규약
오독 (φ=Z/√D vs to_ccoef 의 ψ=√D·Z) — 오라클·수송 시험이 같은 오규약으로
**순환 자기일치**해 통과했었다.  결합 freestream (dense-텐서 to_ccoef 앵커)
이 D₃/D₂=7/3 인자로 적발.  정정: α_up=(l+1)/(2l+3), α_dn≡1 (표준 재귀 가중).
비순환 앵커 시험 (test_convention_anchor) 이 재발을 막는다."""
import numpy as np
import pytest

from bianchi.matter import hierarchy_nterm as HN
from bianchi.matter import pstf_coeff as PC


def test_composition_identity_and_selection_rules():
    X = HN.dense_nterm_matrix(2, 1, 2)
    M, G = HN.mult_matrix(2, 1, 2), HN.rot_gen(1, 2)
    assert np.abs(X - (-(M @ G))).max() <= 1e-14
    assert np.abs(HN.dense_nterm_matrix(2, 2, 0)).max() <= 1e-14
    assert np.abs(HN.dense_nterm_matrix(3, 1, 1)).max() <= 1e-14
    iso = sum(HN.dense_nterm_matrix(3, 2, d) for d in range(3))
    assert np.abs(iso).max() <= 1e-13


def test_mult_constants_closed_form():
    a_up, a_dn = HN.measure_mult_constants()
    for l, v in a_up.items():
        assert abs(v - HN.alpha_up(l)) <= 1e-12
    for l, v in a_dn.items():
        assert abs(v - HN.alpha_dn(l)) <= 1e-12


def test_closed_equals_oracle_full_sweep():
    worst = 0.0
    for l_in in range(1, 6):
        for l_out in (l_in - 1, l_in + 1):
            if not (1 <= l_out <= 6):
                continue
            for d in range(3):
                worst = max(worst, float(np.abs(
                    HN.dense_nterm_matrix(l_out, l_in, d)
                    - HN.closed_nterm_matrix(l_out, l_in, d)).max()))
    assert worst <= 1e-13, worst


def test_l2_pin_matches_dual_engine_value():
    """★ (T4) 핀: u=ê₃, N=ê₂−ê₁ ⇒ N₂−N₁=2 ⇒ (12)-율 = 8π/5.
    (반증 박제: 첫 판 4π/5 — 인자 2 누락 즉시 적발.)"""
    pts, wts = HN._grid(10)
    e = pts
    f = 1.0 + 3.0 * e[:, 2]
    w = np.zeros_like(e)
    w[:, 1] = e[:, 1]
    ed2 = np.cross(w, e)
    w = np.zeros_like(e)
    w[:, 0] = e[:, 0]
    ed1 = np.cross(w, e)
    ed = ed2 - ed1
    m12 = float(np.sum((ed[:, 0]*e[:, 1] + e[:, 0]*ed[:, 1]) * f * wts))
    assert abs(m12 - 8.0*np.pi/5.0) <= 1e-12
    c_dip = PC.vec_to_c3(np.array([0.0, 0.0, 1.0]))
    out = (HN.dense_nterm_matrix(2, 1, 1) - HN.dense_nterm_matrix(2, 1, 0)) @ c_dip
    T = PC.from_ccoef(out, 2)
    assert np.abs(T[0, 1]) > 1e-3


def test_nterm_coeff_grid_and_guards():
    rng = np.random.default_rng(17)
    Jc = {(l, i): rng.standard_normal(2*l + 1)
          for l in range(7) for i in range(3)}
    N3 = np.array([0.4, -0.7, 0.2])
    for l in (1, 2, 3, 4):
        got = HN.nterm_coeff(Jc, N3, l, 1)
        want = np.zeros(2*l + 1)
        for d in range(3):
            if l - 1 >= 1:
                want += N3[d] * (HN.dense_nterm_matrix(l, l - 1, d)
                                 @ Jc[(l - 1, 1)])
            if l + 1 <= 6:
                want += N3[d] * (HN.dense_nterm_matrix(l, l + 1, d)
                                 @ Jc[(l + 1, 1)])
        assert np.abs(got - want).max() <= 1e-13, l
    with pytest.raises(NotImplementedError, match="질량"):
        HN.nterm_coeff(Jc, N3, 2, 0, mass=0.5)
    with pytest.raises(ValueError, match="대각"):
        HN.nterm_coeff(Jc, np.eye(3), 2, 0)


def test_arbitrary_l_extends_beyond_oracle():
    X = HN.closed_nterm_matrix(9, 8, 1)
    assert X.shape == (19, 17) and np.isfinite(X).all()
    assert np.abs(X).max() > 1e-6
    rng = np.random.default_rng(23)
    Jc = {(l, i): rng.standard_normal(2*l + 1) for l in range(11) for i in range(2)}
    a = HN.nterm_coeff(Jc, np.array([0.7, 0.7, 0.7]), 9, 0)
    assert np.abs(a).max() <= 1e-12


def test_convention_anchor_dense_tensor_route():
    """★★ 비순환 앵커 (67차 교훈): dense 텐서 규약원으로 X 재구성 —
    c_in → F = D_l·(T:e^l) → −ė·∇F (접선 방향미분) → ∫e^{⊗l_out}(·) →
    to_ccoef ≡ X @ c_in.  구면·계수 기저 공유 없는 경로 (순환 차단)."""
    rng = np.random.default_rng(5)
    pts, wts = HN._grid(12)

    def contract(T, li, E):
        letters = "abcdef"[:li]
        sub = "".join(letters) + "," + ",".join(f"k{c}" for c in letters) + "->k"
        return np.einsum(sub, T, *([E] * li))

    for (lo, li, d) in ((3, 2, 0), (1, 2, 1), (2, 1, 2)):
        c_in = rng.standard_normal(2*li + 1)
        T_in = PC.from_ccoef(c_in, li)
        ee = pts
        F = PC.D_norm(li) * contract(T_in, li, ee)
        w = np.zeros_like(ee)
        w[:, d] = ee[:, d]
        edot = np.cross(w, ee)
        eps = 1e-6
        Fp = PC.D_norm(li) * contract(T_in, li, ee + eps * edot)
        adv = -(Fp - F) / eps
        T_out = np.zeros((3,) * lo)
        for k in range(len(pts)):
            t = np.array(wts[k] * adv[k])
            for _ in range(lo):
                t = np.multiply.outer(t, pts[k])
            T_out = T_out + t
        want = PC.to_ccoef(T_out, lo)
        got = HN.dense_nterm_matrix(lo, li, d) @ c_in
        assert np.abs(got - want).max() <= 5e-6, (lo, li, d)

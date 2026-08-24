"""
J2 · **계층 RHS 계수공간 스왑 + 신규 블록 (vec·rot) + rg 영속화** (58차).

측정:
  · vec 블록 (u̇): ov(l−1→l)=√(D_l/(D_{l−1}D₁)) (곱-사영 정리 벡터판),
    cv(l+1→l)=R_ov(l+1) (수반항등 — c2 증명과 동형).  dense 대조 ≤7.8e−16.
  · rot 블록 (ω): Gaunt 형 아님 (패리티 소멸) — 각운동량 생성자 경로.
    **R_rot(l) = 1/l (슬롯평균 정리)** + 변환식 2단 정정 기록: 1차 조립
    V·(−iL)·V† 는 켤레 누락+전역부호 두 오류가 상쇄되며 "y만 반전"으로
    위장했다 — 옳은 변환은 conj(V)·(+iL)·Vᵀ (리뷰 진단; dense 가 심판).
    교환관계 [B_a,B_b] = −ε_{abc}B_c 균일.  dense 대조 ≤5.6e−16.
  · 계층 RHS: dense hierarchy_rhs ≡ hierarchy_rhs_coeff, (l≤4)×(i≤2) 전 격자
    무작위 상태 ≤1e−13; **l=10 가동** (3^10 무생성 — dense 원리 불가 영역).
  · rg 영속화: l≤12 사전계산 npz (36KB, 생성 40.7s 1회) + 규약 스탬프 가드.
"""
import os

import numpy as np

from bianchi.matter import hierarchy_coeff as HC
from bianchi.matter import pstf_coeff as PC
from bianchi.matter.hierarchy import hierarchy_rhs
from bianchi.matter.tilted_equation import (_contract_vec_first,
                                            _outer_vec_last)

_EPS = np.zeros((3, 3, 3))
for _a, _b, _c in [(0, 1, 2), (1, 2, 0), (2, 0, 1)]:
    _EPS[_a, _b, _c] = 1.0
    _EPS[_c, _b, _a] = -1.0


# ---------------------------------------------------------------- vec 블록
def test_vec_blocks_match_dense_all_l():
    """★★ ov/cv 두 경로: dense 사영 ≡ 닫힌형, l≤6 전 슬롯 ≤5e−15."""
    rng = np.random.default_rng(1)
    w = rng.standard_normal(3)
    w3 = PC.vec_to_c3(w)
    worst = 0.0
    for l in (1, 2, 3, 4, 5, 6):
        for op, blk, l_in, l_out, fn in (
                ("ov", PC.outer_vec_block(l), l - 1, l,
                 lambda J: _outer_vec_last(J, w, l)),
                ("cv", PC.contract_vec_block(l - 1), l, l - 1,
                 lambda J: _contract_vec_first(J, w))):
            for j in range(2*l_in + 1):
                e = np.zeros(2*l_in + 1)
                e[j] = 1.0
                J = PC.from_ccoef(e, l_in)
                want = PC.to_ccoef(fn(np.asarray(J, float)), l_out)
                got = PC.apply_block(blk, e, w3)
                worst = max(worst, float(np.abs(want - got).max()))
    assert worst <= 5e-15, worst


def test_vec_adjoint_identity_dense(l=4):
    """★ cv 유도의 초석: <pstf(J⊗w),K>_l = <J, cv(K,w)>_{l−1} (상수 1 정확)."""
    rng = np.random.default_rng(7)
    J = PC.from_ccoef(rng.standard_normal(2*l - 1), l - 1)
    K = PC.from_ccoef(rng.standard_normal(2*l + 1), l)
    w = rng.standard_normal(3)
    lhs = float(np.tensordot(_outer_vec_last(J, w, l), K, axes=l))
    rhs = float(np.tensordot(J, _contract_vec_first(K, w), axes=l - 1))
    assert abs(lhs - rhs) <= 1e-13 * max(1.0, abs(lhs))


def test_vec_null_annihilation_at_l10():
    """★★ 비순환 l=10 게이트: ẑ·M = 0 ⇒ cv(M^{⊗11}, ẑ) = 0 —
    e_{m=+11} 방향(Re M^{⊗11})이 ẑ-축약에 소멸해야 한다."""
    e = np.zeros(23)
    e[-1] = 1.0                                    # m = +11
    z3 = PC.vec_to_c3(np.array([0.0, 0.0, 1.0]))
    out = PC.apply_block(PC.contract_vec_block(10), e, z3)
    assert np.abs(out).max() <= 1e-14


# ---------------------------------------------------------------- rot 블록
def test_rot_block_matches_dense_all_l():
    """★★ ω-회전: pstf∘c1(·, ε·ω̂) ≡ (1/l)·B_a, l≤6 전 축·슬롯 ≤5e−15."""
    from bianchi.matter.hierarchy import _contract_one
    worst = 0.0
    for l in (1, 2, 3, 4, 5, 6):
        G = PC.rot_block(l)
        for axis in range(3):
            w = np.zeros(3)
            w[axis] = 1.0
            W = np.einsum("bac,c->ba", _EPS, w)
            for j in range(2*l + 1):
                e = np.zeros(2*l + 1)
                e[j] = 1.0
                want = PC.to_ccoef(_contract_one(PC.from_ccoef(e, l), W), l)
                worst = max(worst, float(np.abs(want - G[:, j, axis]).max()))
    assert worst <= 5e-15, worst


def test_rot_commutators_at_l10():
    """★★ 임의-l 내부게이트: [B_a,B_b] = −ε_{abc}B_c (l=10, dense 무사용)."""
    Bx, By, Bz = PC.rotation_generators(10)
    for (A, B, C) in ((Bx, By, Bz), (By, Bz, Bx), (Bz, Bx, By)):
        assert np.abs(A @ B - B @ A + C).max() <= 1e-12


def test_rot_reduced_element_is_one_over_l():
    """★ R_rot(l)=1/l 박제 — rot_block 이 정확히 생성자/l (l=5)."""
    l = 5
    G = PC.rot_block(l)
    B = PC.rotation_generators(l)
    for axis in range(3):
        assert np.abs(G[:, :, axis] - B[axis]/l).max() <= 1e-15


# ---------------------------------------------------------------- 계층 스왑
def _random_state(l_max, i_max, seed=0):
    rng = np.random.default_rng(seed)
    Jd, Jc = {}, {}
    for l in range(l_max + 1):
        for i in range(i_max + 1):
            c = rng.standard_normal(2*l + 1)
            Jc[(l, i)] = c
            if l == 0:
                Jd[(l, i)] = float(c[0])
            elif l <= 6:                           # dense 는 벽 안에서만 (l>6 은 계수 전용)
                Jd[(l, i)] = PC.from_ccoef(c, l)
    return Jd, Jc


def test_hierarchy_rhs_coeff_matches_dense_full_grid():
    """★★ J2 의 심판: dense hierarchy_rhs ≡ 계수판, (l≤4)×(i≤2) 전 격자."""
    Jd, Jc = _random_state(6, 5, seed=42)
    rng = np.random.default_rng(3)
    sig = PC.from_ccoef(rng.standard_normal(5), 2)
    s5 = PC.sigma_to_c5(sig)
    H = 0.7
    worst = 0.0
    for l in range(0, 5):
        for i in range(0, 3):
            dense = hierarchy_rhs(Jd, H, sig, l, i)
            want = PC.to_ccoef(np.asarray(dense, float), l)
            got = HC.hierarchy_rhs_coeff(Jc, H, s5, l, i)
            worst = max(worst, float(np.abs(want - got).max()))
    assert worst <= 1e-13, worst


def test_hierarchy_runs_at_l10_without_dense_objects():
    """★★ 구조 전환의 목적: l=10 계층 RHS 가동 (3^10=59049 무생성)."""
    _, Jc = _random_state(12, 4, seed=9)
    s5 = np.array([0.1, -0.2, 0.05, 0.3, -0.1])
    out = HC.hierarchy_rhs_coeff(Jc, 0.7, s5, 10, 1)
    assert out.shape == (21,)
    assert np.isfinite(out).all() and np.abs(out).max() > 0.0


def test_hierarchy_h_only_limit_is_exact():
    """★ σ=0 극한: RHS = −H[(3+n)J^(i) + (1−n)J^(i+1)] 정확 (블록 소거 확인)."""
    _, Jc = _random_state(8, 3, seed=5)
    l, i = 6, 1
    n = l + 2*i
    out = HC.hierarchy_rhs_coeff(Jc, 1.3, np.zeros(5), l, i)
    want = -1.3 * ((3.0 + n)*Jc[(l, i)] + (1.0 - n)*Jc[(l, i + 1)])
    assert np.abs(out - want).max() <= 1e-14


# ---------------------------------------------------------------- 영속화
def test_gaunt_tables_are_persisted_and_stamped():
    """★ rg 표 npz: 존재·로드·내용 일치·규약 스탬프 가드."""
    from sympy.physics.wigner import real_gaunt
    path = PC._default_tables_path()
    assert os.path.exists(path), "gaunt_tables.npz 미생성 — export_tables 필요"
    n = PC.load_tables(path)
    assert n == 59                                 # 조합수 정확 (35 l3=2 + 24 l3=1)
    disk = PC._DISK[(4, 2, 2)]
    fresh = np.asarray([[[float(real_gaunt(4, 2, 2, mp, m, mk))
                          for mk in range(-2, 3)]
                         for m in range(-2, 3)]
                        for mp in range(-4, 5)])
    assert np.abs(disk - fresh).max() <= 1e-15
    data = np.load(path)
    assert str(data["convention"]) == "sympy_real_gaunt_CS_v1"



def test_joint_covariance_rot_with_vec_and_sigma():
    """★★ 리뷰 MINOR 4: 블록 간 규약 정합 (J2b 의 전제) — dense 무관, l>6 확장.
    [G_l(w), CV(v)] = CV(W v),  [G_l(w), C1(σ)] = C1(G₂(w)σ),  G_l(w)=l·Σw_a rot."""
    rng = np.random.default_rng(13)
    for l in (3, 8):
        w, v = rng.standard_normal(3), rng.standard_normal(3)
        W = np.einsum("bac,c->ba", _EPS, w)
        Gl = l * np.einsum("pqa,a->pq", PC.rot_block(l), w)
        Gl1 = (l + 1) * np.einsum("pqa,a->pq", PC.rot_block(l + 1), w)
        CVv = np.einsum("pqa,a->pq", PC.contract_vec_block(l), PC.vec_to_c3(v))
        CVWv = np.einsum("pqa,a->pq", PC.contract_vec_block(l),
                         PC.vec_to_c3(W @ v))
        assert np.abs(Gl @ CVv - CVv @ Gl1 - CVWv).max() <= 5e-14, l
        s5 = rng.standard_normal(5)
        G2w = 2.0 * np.einsum("pqa,a->pq", PC.rot_block(2), w)
        C1s = np.einsum("pqk,k->pq", PC.c1_block(l), s5)
        C1Gs = np.einsum("pqk,k->pq", PC.c1_block(l), G2w @ s5)
        assert np.abs(Gl @ C1s - C1s @ Gl - C1Gs).max() <= 5e-14, l


def test_vec_transpose_between_independent_tables_l_gt_6():
    """★ l3=1 전치게이트 (J1 의 (8,10)↔(10,8) 벡터판): R_cv(l)=R_ov(l+1) 를
    dense 벽 위에서 닫는다 — 독립 계산된 (10,11,1)·(11,10,1) 표."""
    A = PC.contract_vec_block(10)                  # rg(10,11,1)
    B = PC.outer_vec_block(11)                     # rg(11,10,1)
    assert np.abs(A - B.transpose(1, 0, 2)).max() <= 1e-14


def test_l3_1_table_spot_checked_against_fresh_sympy():
    """★ 리뷰 MINOR 7: l3=1 표 내용 표본 (디스크 ↔ 신선 sympy)."""
    from sympy.physics.wigner import real_gaunt
    G = PC._rg_table(3, 2, 1)
    for (mp, m, mk) in [(1, 0, 1), (-2, -1, -1), (3, 2, 1), (0, 0, 0)]:
        assert abs(G[mp + 3, m + 2, mk + 1]
                   - float(real_gaunt(3, 2, 1, mp, m, mk))) <= 1e-15

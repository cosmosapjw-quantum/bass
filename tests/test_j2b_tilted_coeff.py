"""
J2b · **tilted 좌변 계수공간 조립 + 질량행렬 두 경로** (59차).

측정:
  · 좌변 전항 패리티: equation_lhs_coeff ≡ dense equation_lhs, (l≤4)×(i=1,2)
    전 격자 무작위 (J, J̇, geo) ≤1.8e−15.
  · ★ ω 규약 반증·잠금: 1차 추출부호가 비율 정확 −1 로 반증됨 — 정정된
    _omega_vec 는 W = **+ε·w** 를 만족 (rot_block 게이트 규약과 동일; 핀
    |ε·w − W| ≤ 1e−18).
  · 질량행렬 두 경로: 닫힌형 블록 (γI, s·γ·CV_v, −l/(2l+1)γ·OV_v) ≡
    dense LHS 의 J̇-선형부 추출 (닫힌형 전혀 안 씀) ≤1e−13.
  · 기하 3항 추출행렬: 선형성 (op(0,0)=0) + l>6 명시 거부 (J2c 이월 박제).
  · 표현가능성 프로브: perp_dot 의 X-부가 블록족 스팬 {I, c1(σ̃), rot(w)}
    에 분해되는 잔차 실측 (J2c 닫힌형 유도의 사전 정찰).
"""
import numpy as np
import pytest

from bianchi.matter import pstf_coeff as PC
from bianchi.matter import tilted_coeff as TC
from bianchi.matter import tilted_terms as TT
from bianchi.matter.tilted_equation import equation_lhs


@pytest.fixture(scope="module")
def geo():
    return TT.geometry(np.array([1.0, 1.1, 0.9]), np.array([0.3, 0.2, 0.4]),
                       np.array([0.12, -0.05, 0.08]),
                       np.array([0.02, 0.01, -0.03]))


def _states(seed=4, l_max=6, i_max=5):
    rng = np.random.default_rng(seed)
    Jd, dJd, Jc, dJc = {}, {}, {}, {}
    for l in range(l_max + 1):
        for i in range(i_max + 1):
            c, d = rng.standard_normal(2*l + 1), rng.standard_normal(2*l + 1)
            Jc[(l, i)], dJc[(l, i)] = c, d
            Jd[(l, i)] = PC.from_ccoef(c, l) if l else float(c[0])
            dJd[(l, i)] = PC.from_ccoef(d, l) if l else float(d[0])
    return Jd, dJd, Jc, dJc


def test_lhs_full_parity(geo):
    """★★ J2b 의 심판: 좌변 9항 전부, 전 격자 dense ≡ 계수공간."""
    Jd, dJd, Jc, dJc = _states()
    gm = TC.GeoMats(geo)
    worst = 0.0
    for l in range(5):
        for i in (0, 1, 2):                        # i=0: (l−n)=0 가드-스킵 가지
            dense = equation_lhs(Jd, dJd, geo, l, i)
            want = PC.to_ccoef(np.asarray(dense, float), l)
            got = TC.equation_lhs_coeff(Jc, dJc, geo, l, i, gm=gm)
            worst = max(worst, float(np.abs(want - got).max()))
    assert worst <= 5e-14, worst


def test_omega_convention_is_pinned(geo):
    """★ 반증 박제: 1차 추출부호는 ε·w_old = −W (비율 −1 로 적발).  정정된
    _omega_vec 는 W = **+ε·w** 를 만족한다 — rot_block 게이트 규약과 일치."""
    W = geo["omega"]
    w = TC._omega_vec(W)                           # 정정된 부호
    eps = np.zeros((3, 3, 3))
    for a, b, c in [(0, 1, 2), (1, 2, 0), (2, 0, 1)]:
        eps[a, b, c] = 1.0
        eps[c, b, a] = -1.0
    assert np.abs(np.einsum("bac,c->ba", eps, w) - W).max() <= 1e-18


def test_mass_blocks_two_routes(geo):
    """★★ 질량행렬: 닫힌형 블록 ≡ dense LHS 의 J̇-선형부 (닫힌형 무사용 추출)."""
    Jd, dJd, Jc, dJc = _states(seed=11)
    zero_d = {k: (np.zeros_like(v) if np.ndim(v) else 0.0)
              for k, v in Jd.items()}
    worst = 0.0
    for l in (0, 1, 2, 3, 4):                      # l=0: down=None 가지 포함
        for i in (1, 2):
            dense = equation_lhs(zero_d, dJd, geo, l, i)   # J=0 ⇒ M·J̇ 만
            want = PC.to_ccoef(np.asarray(dense, float), l)
            dg_, up, down = TC.mass_blocks_for(geo, l)     # v 는 geo 가 나른다
            got = dg_ @ dJc[(l, i)] + up @ dJc[(l + 1, i)]
            if down is not None:
                got = got + down @ dJc[(l - 1, i + 1)]
            worst = max(worst, float(np.abs(want - got).max()))
    assert worst <= 1e-13, worst


def test_geo_extraction_is_linear_and_walled(geo):
    """★ 추출행렬 전제: op(0,0)=0 (순수 선형) + l>6 명시 거부 (J2c 이월)."""
    gm = TC.GeoMats(geo)
    P, Q = gm.perp_dot(3)
    assert np.isfinite(P).all() and np.isfinite(Q).all()
    z = np.zeros((3,) * 3)
    out = TT.perp_dot(z, z, geo, backend="python")
    assert np.abs(out).max() == 0.0
    with pytest.raises(ValueError, match="J2c"):
        gm.perp_dot(7)
    # div 계열 선형성 전제 (리뷰: perp 만 검사하던 공백)
    z4 = np.zeros((3,) * 4)
    assert np.abs(TT.div_contracted(z4, z4, geo, backend="python")).max() == 0.0
    z2 = np.zeros((3,) * 2)
    assert np.abs(TT.div_free_index(z2, z2, geo, 3, backend="python")).max() == 0.0
    # ★ 스테일 가드 (리뷰 MAJOR — R5a 패턴): geo 배열 교체 시 명시 예외
    geo2 = dict(geo)
    geo2["deup"] = np.array(geo["deup"])
    gm2 = TC.GeoMats(geo2)
    gm2.perp_dot(2)
    geo2["deup"] = np.array(geo2["deup"])          # 제자리 교체 재현 (id 변경)
    with pytest.raises(RuntimeError, match="R5a"):
        gm2.perp_dot(3)


def test_perp_dot_representability_probe(geo):
    """★ J2c 정찰: perp_dot 의 X-부 (P) 가 스팬 {I, c1(sym5), rot(w)} 에
    최소자승 분해될 때의 잔차 실측 — 닫힌형 유도 가능성의 수치 증거."""
    rng = np.random.default_rng(21)
    geos = [geo, TT.geometry(1.0 + 0.3*rng.standard_normal(3),
                             0.3*rng.standard_normal(3),
                             0.1*rng.standard_normal(3),
                             0.03*rng.standard_normal(3))]
    for gg in geos:                                # 리뷰: 다중 geo × 다중 l
        gm = TC.GeoMats(gg)
        for l in (2, 3):
            P, _ = gm.perp_dot(l)
            cols = [np.eye(2*l + 1).ravel()]
            for k in range(5):
                e5 = np.zeros(5)
                e5[k] = 1.0
                cols.append(np.einsum("pqk,k->pq", PC.c1_block(l), e5).ravel())
            for a in range(3):
                cols.append(PC.rot_block(l)[:, :, a].ravel())
            A = np.stack(cols, axis=1)
            coef, *_ = np.linalg.lstsq(A, P.ravel(), rcond=None)
            resid = float(np.abs(A @ coef - P.ravel()).max())
            assert resid <= 1e-12, (l, resid)      # 스팬 안 ⇒ 닫힌형 유도 가능

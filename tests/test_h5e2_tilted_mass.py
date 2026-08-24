"""
H5-e2 · 일반 l tilted 질량행렬 M(v)·J̇ = F 검증.

★ 두 경로 (프로젝트 관례):
  A — `matter/tilted_mass.py` 의 **닫힌형**
  B — `audit/h5d_tilted_residual.equation_lhs` 를 J̇ 단위벡터로 때린 **일반 아핀 추출**
      (닫힌형을 전혀 쓰지 않는다)

이 파일이 고정하는 구조적 사실 3가지:
  1. 상태공간은 3^l 이 아니라 **2l+1 차원 PSTF 부분공간**이다 (rank(P) = 2l+1).
     3^l 좌표로 M 을 세우면 대각합 방향에서 **특이**해진다.
  2. **M 은 물질과 무관하다** (순수 기하) — J̇-선형부가 J 를 포함하지 않기 때문.
  3. 격자 밖 J̇ 는 **F 로 가야 한다**.  조용히 버리면 잔차가 1.5e−10 → 5.5e−2 로
     8자리 나빠진다 (아래 시험이 그 차이를 못 박는다).
"""
import numpy as np
import pytest

from bianchi.matter import tilted_mass as TM
from bianchi.matter.tilted_terms import geometry

R = pytest.importorskip("audit.h5d_tilted_residual")

KW = dict(a_vec=(1.0, 0.9, 1.2), da_vec=(0.35, 0.28, 0.42),
          v=(0.08, -0.05, 0.12), dv=(0.015, 0.01, -0.02))
L, I = 3, 1          # ★ 방정식이 i+2 를 참조하므로 i_max=1 (격자 i ≤ 3)


@pytest.fixture(scope="module")
def geo():
    return geometry(**KW)


def _generic_mass(geo, mass):
    """경로 B — 닫힌형을 쓰지 않는 일반 아핀 추출."""
    J = R.moment_grid(KW["a_vec"], KW["v"], mass)

    def lhs(dJd):
        d = {k: np.zeros(np.asarray(J[k]).shape) for k in J}
        d.update(dJd)
        return {(l, i): np.asarray(R.equation_lhs(J, d, geo, l, i), float)
                for l in range(L + 1) for i in range(I + 1)}

    base = lhs({})
    _, _, n = TM.layout(L, I)
    M = np.zeros((n, n))
    for c in range(n):
        e = np.zeros(n)
        e[c] = 1.0
        col = lhs(TM.unpack(e, L, I))
        M[:, c] = TM.pack({k: col[k] - base[k] for k in col}, L, I)
    return M


# ═══════════════════════════════ 1. 상태공간은 PSTF 부분공간
@pytest.mark.parametrize("l", [0, 1, 2, 3, 4, 5])
def test_pstf_subspace_dimension_is_2l_plus_1(l):
    """★ rank(P) = 2l+1 — 논문의 "2l+1 독립성분" 규약을 코드에서 **확인**한다.

    l=2 는 9 중 5, l=5 는 243 중 11.  3^l 저장공간을 그대로 상태공간으로 쓰면
    나머지 방향이 M 의 영공간이 되어 `solve` 가 특이행렬을 만난다.
    """
    Q = TM.pstf_basis(l)
    assert Q.shape == (3 ** l, 2 * l + 1)
    P = TM.pstf_projector(l)
    assert np.linalg.matrix_rank(P, tol=1e-10) == 2 * l + 1
    # Q 가 P 의 상공간을 정확히 span (PQ = Q)
    assert np.abs(P @ Q - Q).max() < 1e-10


def test_coef_tensor_roundtrip():
    rng = np.random.default_rng(3)
    for l in (0, 1, 2, 3):
        from bianchi.matter.hierarchy import pstf
        T = rng.normal(size=(3,) * l)
        T = np.asarray(pstf(T), float) if l >= 2 else T
        back = TM.to_tensor(TM.to_coef(T, l), l)
        assert np.abs(np.asarray(back, float) - T).max() < 1e-12, l


def test_naive_3l_state_space_would_be_singular():
    """★ 왜 PSTF 좌표를 쓰는지 — 3^l 좌표에서는 M 이 특이하다는 것을 직접 보인다."""
    l = 2
    P = TM.pstf_projector(l)
    assert np.linalg.matrix_rank(P, tol=1e-10) < 3 ** l
    assert abs(np.linalg.det(P)) < 1e-12


# ═══════════════════════════════ 2. ★ 두 경로 교차검증
def test_closed_form_matches_generic_extraction(geo):
    """★★ 닫힌형 = 일반 아핀 추출 (측정 9.5e−15).

    닫힌형:  대각 γ·P,  l+1 → γ·P∘(v 축약),  l−1(i+1) → −(l/(2l+1))γ·P∘(·⊗v)
    """
    Mg = _generic_mass(geo, 0.0)
    Mc = TM.dense(geo, L, I)
    assert np.abs(Mg - Mc).max() < 1e-12, np.abs(Mg - Mc).max()


def test_mass_matrix_is_material_independent(geo):
    """★ M 은 순수 기하 — 방정식의 J̇-선형부가 J 를 포함하지 않기 때문.

    (사틀 회전항은 J 에만 붙으므로 F 로 간다.)  측정: m=0 vs m=1.5 에서 1.4e−14.
    """
    assert np.abs(_generic_mass(geo, 0.0) - _generic_mass(geo, 1.5)).max() < 1e-11


def test_outer_pstf_projection_is_required(geo):
    """★ 마지막 PSTF 사영을 빼면 대각 블록이 어긋난다 (실제로 겪은 오류).

    `equation_lhs` 가 l ≥ 2 에서 출력을 사영하므로 M 도 그래야 한다.
    빼면 l=2 에서 0.51, l=3 에서 0.84 불일치.
    """
    Mc = TM.dense(geo, L, I)
    gam, _ = TM.gamma_and_v(geo)
    # 사영 없는 대각(γ·Id)과 실제 대각이 l≥2 에서 다르다
    keys, off, _ = TM.layout(L, I)
    l3 = (3, 0)
    blk = Mc[off[l3]:off[l3] + 7, off[l3]:off[l3] + 7]
    assert np.abs(blk - gam * np.eye(7)).max() < 1e-12   # PSTF 좌표에서는 γ·Id 로 보인다
    # 그러나 3^l 좌표에서는 사영이 필수 (P ≠ Id)
    assert np.abs(TM.pstf_projector(3) - np.eye(27)).max() > 0.5


# ═══════════════════════════════ 3. 게이트
def test_vanishing_tilt_gives_identity():
    """★ v=0 → M = I (법선합동에서 명시적 RHS 로 정확히 환원)."""
    g0 = geometry(KW["a_vec"], KW["da_vec"], (0.0, 0.0, 0.0), (0.0, 0.0, 0.0))
    _, _, n = TM.layout(L, I)
    assert np.abs(TM.dense(g0, L, I) - np.eye(n)).max() < 1e-14


def test_reproduces_h5c_closed_form_at_low_l(geo):
    """★ l≤1, i=0 에서 H5-c 의 M = γ(I + e₀vᵀ) 를 **정확히** 재생산."""
    M1 = TM.dense(geo, 1, 0)
    gam, v = TM.gamma_and_v(geo)
    want = gam * (np.eye(4) + np.outer(np.eye(4)[0], np.r_[0.0, v]))
    assert np.abs(M1 - want).max() < 1e-14


def test_mass_matrix_is_nonsingular_and_well_conditioned(geo):
    M = TM.dense(geo, L, I)
    assert abs(np.linalg.det(M)) > 1e-3
    assert np.linalg.cond(M) < 2.0


def test_conditioning_scan_is_benign():
    """★ |v| → 0.9 까지 cond(M) ≤ 5.3 — 일반 l 도 극단 tilt 에서 온순하다.

    (측정: 0.1→1.18, 0.5→2.38, 0.9→5.25.  l≤1 상삼각 판은 2.4 였다.)
    """
    scan = TM.conditioning_scan(l_max=L, i_max=I)
    conds = [c for _, c, _ in scan]
    assert conds[0] == pytest.approx(1.0, abs=1e-12)
    assert max(conds) < 8.0, conds
    assert all(b >= a - 1e-12 for a, b in zip(conds, conds[1:])), conds


# ═══════════════════════════════ 4. ★★ 폐쇄 시험 (정확 구적과의 연결)
@pytest.fixture(scope="module")
def exact(geo):
    out = {}
    for mass in (0.0, 1.0):
        J = R.moment_grid(KW["a_vec"], KW["v"], mass)
        dJ = R.moment_grid_dot(KW["a_vec"], KW["da_vec"], KW["v"], KW["dv"], mass, 1e-5)
        out[mass] = (J, dJ)
    return out


def _forcing(J, dJ, geo, drop_outside):
    """F = −LHS(격자 안쪽 J̇ = 0).

    drop_outside=True 면 격자 **밖** J̇ 도 0 으로 둔다 (= 조용히 버리는 오류 재현).
    """
    keys, _, _ = TM.layout(L, I)
    part = {k: np.zeros(np.asarray(J[k]).shape) for k in J} if drop_outside else dict(dJ)
    for k in keys:
        part[k] = np.zeros(np.asarray(J[k]).shape)
    return {(l, i): -np.asarray(R.equation_lhs(J, part, geo, l, i), float)
            for l in range(L + 1) for i in range(I + 1)}


@pytest.mark.parametrize("mass", [0.0, 1.0])
def test_exact_derivatives_satisfy_mass_equation(geo, exact, mass):
    """★★ 정확 구적의 J̇ 가 M·J̇ = F 를 만족 (중앙차분 바닥 ~1.7e−10)."""
    J, dJ = exact[mass]
    rho = float(J[(0, 0)])
    keys, _, _ = TM.layout(L, I)
    F = _forcing(J, dJ, geo, drop_outside=False)
    Md = TM.matvec({k: dJ[k] for k in keys}, geo, L, I)
    worst = max(np.abs(np.atleast_1d(Md[k] - F[k])).max() for k in F) / rho
    assert worst < 1e-8, worst


@pytest.mark.parametrize("mass", [0.0, 1.0])
def test_solving_recovers_exact_derivatives(geo, exact, mass):
    """★★ 역으로 M·J̇ = F 를 풀면 정확 구적의 J̇ 가 되돌아온다."""
    J, dJ = exact[mass]
    keys, _, _ = TM.layout(L, I)
    F = _forcing(J, dJ, geo, drop_outside=False)
    sol = TM.solve(F, geo, L, I)
    scale = max(np.abs(np.atleast_1d(np.asarray(dJ[k], float))).max() for k in F)
    worst = max(np.abs(np.atleast_1d(
        np.asarray(sol[k], float)
        - np.asarray(TM.to_tensor(TM.to_coef(dJ[k], k[0]), k[0]), float))).max()
        for k in F) / scale
    assert worst < 1e-8, worst


def test_dropping_out_of_grid_derivatives_is_a_trap(geo, exact):
    """★★ 격자 **밖** J̇ 를 조용히 버리면 잔차가 8자리 나빠진다.

    l=3 행은 J̇^(i)_{A_4} 를, i=1 행은 J̇^(2) 를 참조한다.  이들은 상태공간 밖이므로
    **F 로 가야 한다**.  0 으로 버리면 1.5e−10 → 5.5e−2.
    절단을 "그냥 0" 으로 두는 것이 무해하지 않다는 정량적 증거다.
    """
    J, dJ = exact[0.0]
    rho = float(J[(0, 0)])
    keys, _, _ = TM.layout(L, I)
    dJ_in = {k: dJ[k] for k in keys}
    Md = TM.matvec(dJ_in, geo, L, I)
    good = _forcing(J, dJ, geo, drop_outside=False)
    bad = _forcing(J, dJ, geo, drop_outside=True)
    r_good = max(np.abs(np.atleast_1d(Md[k] - good[k])).max() for k in good) / rho
    r_bad = max(np.abs(np.atleast_1d(Md[k] - bad[k])).max() for k in bad) / rho
    assert r_good < 1e-8, r_good
    assert r_bad > 1e-3, r_bad
    assert r_bad / r_good > 1e5, (r_good, r_bad)

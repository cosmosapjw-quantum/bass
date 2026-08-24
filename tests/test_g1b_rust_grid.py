"""
G1b · **격자 충돌 Rust 커널 + 이방-강건 각격자** (73차).

  · Rust 핵 (Sinkhorn 보존형) ≡ Python (1.6e−17) · expm 테일러 ≡ eigh (5.6e−14)
    — ★ eigh 를 **안 쓴다**: exp(νdt(K−I))g = e^{−νdt}Σ(νdt)^m/m! K^m g,
      O(m·N²) vs O(N³).  Strang 루프째 (R5b) 패리티 1.6e−13, 속도 ×4.
  · ★★ G2 열화 곡선의 **해결**: 각격자 정밀화 24²→48²→96² 에서 s=0.4 왜곡의
    Σw 오차 3.0e−5 → 3.5e−11 → **8.9e−15 (기계)** — 이방-강건 격자 확보.
    (G2 발견이 요구사양이었고, 여기서 사양을 만족하는 해상도를 확정.)
  · 정밀 격자에서 Thomson 감쇠율이 강한 이방에서도 기계급 회복.
"""
import numpy as np
import pytest

pytest.importorskip("bianchi_rustcore")

import bianchi_rustcore as R  # noqa: E402

from bianchi.matter import collision_ladder as CL  # noqa: E402
from bianchi.matter import grid_boltzmann as GB  # noqa: E402

ANISO = (lambda n: 1.0 + 0.3*n[:, 2] + 0.2*(n[:, 0]**2 - n[:, 1]**2)
         + 0.1*n[:, 0]*n[:, 1])
A_MID = np.array([1.2, 0.86, 1.04])
A_HARD = np.array([1.4, 0.72, 1.08])


def test_kernel_parity_and_conservation():
    """★ Rust Sinkhorn 핵 ≡ Python + 행합/w-열합 = 1 (보존형)."""
    Kp = CL.thomson_operator(A_MID)[0]
    Kr = CL.thomson_matrix_rust(A_MID)
    assert np.abs(Kp - Kr).max() <= 1e-15
    _, _, w = CL.physical_frame(A_MID)
    assert np.abs(Kr.sum(axis=1) - 1.0).max() <= 1e-13
    assert np.abs((w[:, None] * Kr).sum(axis=0) / w - 1.0).max() <= 1e-13


def test_expm_taylor_parity_and_invariants():
    """★ 테일러 expm ≡ eigh 경로 + 상수벡터 불변 + 에너지 기계보존."""
    F = GB.initial_grid(aniso=ANISO)
    G = CL.angular_density(F, A_MID)
    K = CL.thomson_matrix_rust(A_MID)
    for nu_dt in (0.05, 0.4, 1.5):
        a_ = CL.collide(G, A_MID, nu_dt, "thomson")
        b_ = CL.collide_rust(G, K, nu_dt)
        assert np.abs(a_ - b_).max() / np.abs(a_).max() <= 1e-12, nu_dt
    ones = np.ones_like(G)
    assert np.abs(CL.collide_rust(ones, K, 0.7) - 1.0).max() <= 1e-13
    n0, _ = CL.invariants(G, A_MID)
    n1, _ = CL.invariants(CL.collide_rust(G, K, 0.3), A_MID)
    assert abs(n1 - n0) / abs(n0) <= 1e-13


def test_strang_loop_whole_parity_and_speed():
    """★★ 루프째 (R5b): Rust Strang ≡ Python ≤1e−12, 속도 ≥3×."""
    import time
    F = GB.initial_grid(aniso=ANISO)
    a_of = lambda t: np.array([np.exp(0.3*t), np.exp(-0.2*t), np.exp(-0.1*t)])
    G0 = CL.angular_density(F, a_of(0.0))
    t0 = time.perf_counter()
    gp = CL.strang_evolve(G0, a_of, 0.0, 1.0, 60, nu=2.0)
    tp = time.perf_counter() - t0
    t0 = time.perf_counter()
    gr = CL.strang_evolve_rust(G0, a_of, 0.0, 1.0, 60, nu=2.0)
    tr = time.perf_counter() - t0
    assert np.abs(gp - gr).max() / np.abs(gp).max() <= 1e-12
    assert tp / tr >= 3.0, (tp, tr)


def test_angular_refinement_solves_degradation():
    """★★ G2 발견의 해결: s=0.4 왜곡에서 Σw·êê 오차가 해상도로 기계 수렴."""
    seq = [(24, 24), (48, 48), (96, 96)]
    errs = [CL.measure_grid_quality(A_HARD, nt, npv) for nt, npv in seq]
    assert errs[0][0] >= 1e-6                          # 기준 격자의 열화 (G2)
    assert errs[1][0] <= 1e-9                          # 4배 노드로 급개선
    assert errs[2][0] <= 1e-13 and errs[2][1] <= 1e-12  # 기계 회복
    assert errs[0][0] > errs[1][0] > errs[2][0]        # 단조


def test_refined_grid_restores_thomson_rates():
    """★ 정밀 격자 (96²) 에서 강한 이방의 Thomson 율이 기계급 회복."""
    nhat, wang = CL.angular_grid(96, 96)
    e, mu, w = CL.physical_frame_on(nhat, wang, A_HARD)
    K = np.asarray(R.gc_thomson(np.ascontiguousarray(e),
                                np.ascontiguousarray(w)))
    rng = np.random.default_rng(4)
    G = 1.0 + 0.3*e[:, 2] + 0.2*(e[:, 0]**2 - e[:, 1]**2)
    nu_dt = 0.05
    G1 = CL.collide_rust(G, K, nu_dt)

    def amp(g, l):
        from bianchi.matter import pstf_coeff as PC
        letters = "ijklmn"[:l]
        subs = ",".join(f"a{c}" for c in letters)
        T = np.einsum(f"a,{subs}->{letters}", w * g, *([e] * l))
        return float(np.linalg.norm(PC.to_ccoef(T, l)))

    for l in (1, 2):
        r = -np.log(amp(G1, l) / amp(G, l)) / nu_dt
        assert abs(r - (1.0 - R.kin_thomson_eigenvalue(l))) <= 1e-9, (l, r)

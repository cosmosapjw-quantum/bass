"""
R3 · **뜨거운 경로 정리** — 값은 그대로, 시간만 줄인다.

R1/R2 가 type V 노드 커널을 Rust 로 옮긴 뒤, 남은 회귀시험 시간은 세 군데에 몰려
있었다.  셋 다 **이식이 아니라 낭비**였다:

```
tilted 적분 (L1/L2/L3)     34.3 s → 2.3 s   (15배)   PSTF 사영 + 질량행렬 조립
Lyapunov / 극한주기 (M4)   75.2 s → 1.1 s   (68배)   JAX 즉시실행 루프 → lax.scan
CMB 패턴 (M11)             59.2 s → 0.01 s  (5900배) 이미 있던 배치 백엔드 미사용
scipy 대조 (M1)            46   s → 6.6 s   (7배)    RHS 를 jit 없이 수천 번 호출
```

★ 이 파일이 고정하는 것: **바꾼 연산이 옛 값을 재현하는가.**
  · `pstf` 를 고정 행렬 Q_l = (I − A A⁺)·S_l 로 굳혔다 — 옛 판(순열 평균 + lstsq)과
    1.9e−14 로 일치하고, l=6 에서 28배 빠르다.
  · 질량행렬 `dense` 를 희소 조립으로 바꿨다 — M 이 **비트-정확** 동일.
  · CMB 패턴이 Rust/Python 백엔드에서 z 8.4e−16 로 같다.

★ **정직한 대가 하나** (`test_l3_massive_closure` 에 기록): PSTF 를 행렬로 굳히면서
  "1차원 환원 = J̇ 닫힘" 의 **비트-일치가 깨졌다** (1.8e−18 절대차로 남는다).
  비트-일치는 수학적 항등식이 아니라 연산 순서가 같아서 생긴 것이었다 — 이분법으로
  원인을 확정하고 게이트를 절대 척도로 바꿨다.
"""
import numpy as np
import pytest

from bianchi.matter import hierarchy as H


def _old_pstf(T):
    """옛 판 그대로 — l! 개 전치 평균 + lstsq 직교사영."""
    T = H._symmetrize(np.asarray(T, float))
    l = T.ndim
    if l < 2:
        return T
    A = H._trace_subspace(l)
    v = T.ravel()
    coef, *_ = np.linalg.lstsq(A, v, rcond=None)
    return (v - A @ coef).reshape(T.shape)


# ═══════════════════════════════ 1. PSTF 를 행렬로 굳힌 것
@pytest.mark.parametrize("l", [2, 3, 4, 5, 6])
def test_frozen_pstf_operator_reproduces_the_old_projection(l):
    """★★ 값 대조 — 무작위 텐서 5개에서 옛 판과 1.9e−14 이내."""
    rng = np.random.default_rng(l)
    worst = 0.0
    for _ in range(5):
        T = rng.normal(size=(3,) * l)
        a, b = _old_pstf(T), H.pstf(T)
        worst = max(worst, float(np.abs(a - b).max() / max(np.abs(a).max(), 1e-300)))
    assert worst < 1e-12, worst


def test_the_operator_is_a_projector_and_kills_traces():
    """★ Q_l 이 실제로 사영자다 (Q² = Q) — 그리고 대각합을 정확히 죽인다."""
    for l in (2, 3, 4):
        Q = H.pstf_operator(l)
        assert np.abs(Q @ Q - Q).max() < 1e-10, l
        rng = np.random.default_rng(7 + l)
        out = H.pstf(rng.normal(size=(3,) * l))
        assert np.abs(np.trace(out, axis1=-2, axis2=-1)).max() < 1e-12, l


def test_pstf_still_refuses_unsupported_rank():
    """★ 안전장치는 그대로 — l > L_MAX_SUPPORTED 는 예외."""
    with pytest.raises(ValueError):
        H.pstf(np.zeros((3,) * (H.L_MAX_SUPPORTED + 1)))


# ═══════════════════════════════ 2. 질량행렬 희소 조립
def test_sparse_mass_matrix_assembly_is_bit_identical():
    """★★ 단위벡터 전체 대신 **한 블록만** 넘겨도 M 이 비트-정확 같다.

    옛 판은 빈 블록마다 0 배열을 만들고 사영까지 했다 (프로파일: pstf 87093회).
    """
    from bianchi.matter import tilted_integrate as TI
    from bianchi.matter import tilted_mass as TM
    geo = TI.Background().geometry(0.1)

    def dense_full(l_max, i_max):
        keys, off, n = TM.layout(l_max, i_max, None)
        M = np.zeros((n, n))
        for c in range(n):
            e = np.zeros(n)
            e[c] = 1.0
            M[:, c] = TM.pack(TM.matvec(TM.unpack(e, l_max, i_max, None), geo,
                                        l_max, i_max, None, None), l_max, i_max, None)
        return M

    for (lm, im) in ((2, 1), (3, 1), (3, 3)):
        assert np.abs(TM.dense(geo, lm, im) - dense_full(lm, im)).max() == 0.0, (lm, im)


def test_tilted_trajectory_error_is_unchanged():
    """★ L3 이 고정한 값이 그대로다 (m=1, l_max=3, i_max=3)."""
    from bianchi.matter import tilted_integrate as TI
    e = TI.trajectory_error(TI.Background(), 1.0, 0.2, 20, 3, 3)
    assert e["rho"] < 1e-5 and e["q"] < 1e-5 and e["pi"] < 1e-4, e
    assert abs(e["q"] / 2.355498e-06 - 1) < 1e-3, e


# ═══════════════════════════════ 3. CMB 패턴 — 두 백엔드
def test_cmb_pattern_agrees_between_backends():
    """★★ 배치 백엔드(Rust)와 옛 Python 방향 루프가 z 8.4e−16 으로 같다."""
    from bianchi import backend
    from bianchi.observables import cmb_pattern as cmb
    if not backend.available():
        pytest.skip("bianchi_rustcore 없음")
    model = dict(H0=1.0, Sigma0=[0.2, -0.1, -0.1], Omega0=0.9, gamma=1.0,
                 nhat=[0, 0, 1])
    t0 = 2 / 3
    kw = dict(n_theta=5, n_phi=8, nsteps=200)
    a = cmb.temperature_pattern_diag_bianchi(model, t0, 0.6 * t0,
                                             force_python=True, **kw)
    b = cmb.temperature_pattern_diag_bianchi(model, t0, 0.6 * t0, **kw)
    assert np.abs(a["z"] - b["z"]).max() / np.abs(a["z"]).max() < 1e-13
    assert np.abs(a["dT_over_T"] - b["dT_over_T"]).max() < 1e-13


# ═══════════════════════════════ 4. Lyapunov — scan 판이 옛 값을 낸다
def test_lyapunov_matches_the_documented_value():
    """★ λ = −0.7265523307057 (옛 즉시실행 루프와 1 ulp)."""
    import jax.numpy as jnp
    import tests.test_m4_m7 as M
    from bianchi.analysis import dynamics as dyn
    Sp = (3 * 1.0 - 2) / 8
    N1 = np.sqrt(3 * (2 - 4 * Sp) * Sp)
    v = jnp.asarray([Sp, 0.0, N1, 0.0, 0.0])
    lam = dyn.largest_lyapunov(M._rhs_arr, v, M._args(1.0), T=20.0, dt=0.01)
    assert abs(lam - (-0.7265523307057665)) < 1e-12, lam

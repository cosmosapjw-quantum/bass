"""v1.4 부채 해소 회귀 테스트 — A(vorticity), B(CS II 완전성), C(connection 핀)."""
import numpy as np
import jax
import jax.numpy as jnp
import pytest


# ══════════════════════════ 부채 B: CS(II) tilt 축소의 완전성
def test_cs_II_v1_forbidden_but_v23_sets_threshold():
    """v1 비구속 고윳값은 6/5 에서 교차하지만 운동량 구속이 v1 을 금지하므로,
    물리적 tilt 임계값은 {v2,v3} 의 10/7 이다 (audit/d_tilted_II.py 요약)."""
    from bianchi import thresholds as th
    from bianchi.matter.fluid import TiltedFluid, dv_general, sources
    from bianchi.conventions import codazzi_residual

    # 해석식: v1 은 6/5, v23 는 10/7 에서 교차
    assert abs(th.cs_II_v1_unconstrained_eigenvalue(6 / 5)) < 1e-12
    assert abs(th.cs_II_tilt_eigenvalue_analytic(10 / 7)) < 1e-12
    # 6/5 < 10/7 이므로 v1 을 순진하게 읽으면 더 이른 (틀린) 임계값이 나온다
    assert 6 / 5 < 10 / 7

    # v1 이 구속으로 금지됨을 실제로 확인: 유형 II 기하 운동량 = 0, 따라서
    # Codazzi C1 = q1 = 3 g Omega v1 (v/G+) 의 v1-기울기 != 0.
    for g in (1.1, 1.25, 1.4):
        Sp = (3 * g - 2) / 8.0
        Om = 9.0 / 8.0 - 3.0 * g / 16.0
        N1 = np.sqrt(max(9.0 * (2 - g) * (3 * g - 2) / 16.0, 0.0))
        Sigma = jnp.diag(jnp.array([-2 * Sp, Sp, Sp]))
        N = jnp.diag(jnp.array([N1, 0.0, 0.0]))
        A = jnp.zeros(3)
        # 기하 운동량 (v=0) 은 정확히 0
        Gmom = np.asarray(codazzi_residual(Sigma, N, A, None))
        assert np.abs(Gmom).max() < 1e-12

        def C(v):
            fl = TiltedFluid.of(g, Om, v)
            src = sources(fl, Sigma, A)
            return codazzi_residual(Sigma, N, A, src["q_flux"])

        Jc = np.asarray(jax.jacfwd(C)(jnp.zeros(3)))
        assert abs(Jc[0, 0]) > 1e-6                # v1 은 구속면에 접하지 않음
        assert np.isclose(abs(Jc[0, 0]), 3 * g * Om, rtol=1e-6)


def test_stability_of_CS_II_uses_v23_doublet():
    """stability_of_CS_II 는 {v2,v3} 이중항을 쓰며 10/7 에서 부호전환."""
    from bianchi import thresholds as th
    assert th.stability_of_CS_II(1.3) < 0 < th.stability_of_CS_II(1.5)
    assert abs(th.stability_of_CS_II(10 / 7)) < 1e-12
    # v1 비구속 값(6/5 교차)과 혼동하지 않는지: 1.25 (=6/5<g<10/7) 에서는
    # 물리 임계값이 아직 음수여야 한다 (v1 을 썼다면 양수가 됐을 것)
    assert th.stability_of_CS_II(1.25) < 0


# ══════════════════════════ 부채 A: vorticity 는 on-shell 관측량 (v̇ 의존은 실물리)
def test_tilted_vorticity_is_wellposed_onshell():
    """유체 vorticity 는 off-shell 에서 v̇ 에 의존(실물리)하지만, on-shell
    (운동량 보존 -> a || v) 에서 u-직교·반대칭·v=0 소멸의 깨끗한 관측량이다.
    여기서는 저장소 규약과 무관한 자립 계산으로 그 성질만 고정한다."""
    from bianchi.charts.general import _connection   # 3d frame connection (JAX)

    rng = np.random.default_rng(3)

    def kin(N, A, S, vv, vdot, G4):
        Gam2 = 1.0 / np.sqrt(1 - vv @ vv)
        Gd = Gam2 ** 3 * (vv @ vdot)
        ul = np.array([-Gam2, *(Gam2 * vv)])
        uu = np.array([Gam2, *(Gam2 * vv)])
        dul = np.array([-Gd, *(Gd * vv + Gam2 * vdot)])
        Du = np.zeros((4, 4))
        for b in range(4):
            for c in range(4):
                e_c = dul[b] if c == 0 else 0.0
                Du[b][c] = e_c - sum(G4[d][b][c] * ul[d] for d in range(4))
        P = np.eye(4) + np.outer(ul, uu)
        K = np.einsum('ma,nb,ab->mn', P, P, Du)
        om = 0.5 * (K - K.T)
        return om, uu

    # build the 4d frame connection blocks:  Gamma^0_ab = H d + sigma, Gamma^a_b0 = -Omega,
    # spatial block = 3d connection.  (all dimensionful; R=0 for simplicity)
    def frame_G(H, S, N, A):
        G = np.zeros((4, 4, 4))
        K = H * np.eye(3) + S
        for a in range(3):
            for b in range(3):
                G[0][a + 1][b + 1] = K[a, b]        # Gamma^0_ab
                G[a + 1][0][b + 1] = K[a, b]        # Gamma^a_0b
        C3 = np.asarray(_connection(jnp.asarray(N), jnp.asarray(A)))  # [k,i,j]
        for a in range(3):
            for b in range(3):
                for c in range(3):
                    G[a + 1][b + 1][c + 1] = C3[a, b, c]
        return G

    from bianchi.charts.general import _connection
    worst_uortho = worst_asym = worst_v0 = 0.0
    offshell_dep = 0.0
    for _ in range(30):
        N = rng.normal(size=(3, 3)); N = 0.5 * (N + N.T)
        w, V = np.linalg.eigh(N); k = int(np.argmin(abs(w))); w[k] = 0
        N = V @ np.diag(w) @ V.T; A = float(rng.normal()) * V[:, k]
        S = rng.normal(size=(3, 3)); S = 0.5 * (S + S.T); S -= np.trace(S) * np.eye(3) / 3
        H = float(rng.uniform(0.6, 1.5))
        vv = rng.normal(size=3); vv *= 0.4 / np.linalg.norm(vv)
        G4 = frame_G(H, S, N, A)
        o1, uu = kin(N, A, S, vv, np.zeros(3), G4)
        o2, _ = kin(N, A, S, vv, rng.normal(size=3), G4)
        offshell_dep = max(offshell_dep, np.abs(o1 - o2).max())   # real physics: > 0
        worst_uortho = max(worst_uortho, np.abs(o1 @ uu).max())
        worst_asym = max(worst_asym, np.abs(o1 + o1.T).max())
        o0, _ = kin(N, A, S, np.zeros(3), np.zeros(3), G4)
        worst_v0 = max(worst_v0, np.abs(o0).max())
    assert offshell_dep > 1e-2       # v̇ 의존은 실물리 (v1.2 '버그' 라벨은 오개념)
    assert worst_uortho < 1e-10      # ω ⊥ u
    assert worst_asym < 1e-12        # 반대칭
    assert worst_v0 < 1e-12          # v=0 에서 소멸


# ══════════════════════════ 부채 C: connection3 규약 핀
def test_connection3_pin_and_convention():
    """core.connection3 지표순서가 S^3 앵커로 고정되어 있는지 (import 시 자동 검사).
    저장소 audit 코어를 직접 로드해 재확인."""
    import importlib.util
    import os
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(root, "audit", "core.py")
    spec = importlib.util.spec_from_file_location("audit_core", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)      # _pin_connection3() runs at import; raises if drifted
    # S^3 anchor explicit
    Ric = mod.ricci3(2.0 * np.eye(3), np.zeros(3))
    assert np.allclose(Ric, 2.0 * np.eye(3), atol=1e-12)
    assert abs(np.trace(Ric) - 6.0) < 1e-12
    # P_a double contraction is symmetric -> order-independent (the safe use)
    rng = np.random.default_rng(1)
    N = rng.normal(size=(3, 3)); N = 0.5 * (N + N.T); A = rng.normal(size=3)
    v = rng.normal(size=3)
    G = mod.connection3(N, A)
    Pa1 = np.einsum('abc,b,c->a', G, v, v)
    Pa2 = np.einsum('acb,b,c->a', G, v, v)   # transposed last two slots
    assert np.allclose(Pa1, Pa2, atol=1e-12)  # symmetric contraction: order-safe

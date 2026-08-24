"""v1.3 적대적 감사 대응 회귀 테스트 — 결함 #3(투영기), #5(general q), #12(스칼라 계수)."""
import numpy as np
import jax.numpy as jnp
import pytest

from bianchi.conventions import SQRT3


# ══════════════════════════════ 결함 #12: 스칼라장 lambda 결합 sqrt(3/2) 고정
def test_scalar_field_scaling_fixed_point_pins_coupling():
    """지수 퍼텐셜 스칼라 지배 고정점 x*=lam/sqrt6, y*=sqrt(1-lam^2/6) 는
    결합계수가 정확히 sqrt(3/2) 일 때만 정지한다. 기존 conservation_residual
    테스트는 계수와 무관하게 0 이라 판별력이 없었다 (감사 지적)."""
    from bianchi.matter.components import ScalarField
    for lam in (0.5, 1.0, 1.8):
        x = lam / np.sqrt(6.0)
        y = np.sqrt(1.0 - lam**2 / 6.0)
        f = ScalarField.of(x, y, lam)
        q = 2.0 * x**2 - y**2                     # 스칼라 지배: Sigma = 0
        d = f.rhs(q)
        assert abs(float(d.x)) < 1e-14 and abs(float(d.y)) < 1e-14, (lam, d.x, d.y)
        # 판별력 증명: 계수가 1% 만 틀려도 고정점이 정지하지 않는다
        s32_bad = np.sqrt(1.5) * 1.01
        dx_bad = (q - 2.0) * x + s32_bad * lam * y**2
        assert abs(dx_bad) > 1e-3


# ══════════════════════════════ 결함 #5: general 차트 ↔ tilted 차트 완전 폐포
def _bt_state_and_maps():
    from bianchi.charts import class_b_tilted as cbt
    y = cbt.StateBT.of(0.08, 0.05, 0.11, -0.07, 0.04, 0.35, 0.25, 0.28,
                       0.12, 0.06, -0.09)
    args = {"gamma": 1.25}
    a = cbt.aux(y, args)
    Sigma = np.asarray(cbt.shear_matrix(y))
    lam, N, A = float(y.lam), float(y.N), float(y.A)
    Nmat = np.array([[0.0, 0.0, 0.0],
                     [0.0, SQRT3 * lam * N, SQRT3 * N],
                     [0.0, SQRT3 * N, SQRT3 * lam * N]])
    Avec = np.array([A, 0.0, 0.0])
    R = np.asarray(cbt.gauge_rotations(y))
    return cbt, y, args, a, Sigma, Nmat, Avec, R


def test_general_chart_closes_on_tilted_chart_with_correct_q():
    """tilted 물질을 주입한 general.rhs 가 class_b_tilted.rhs 의 기하 부분과
    전 성분 일치해야 한다 — 단, args["q"] 로 tilted q 를 넘겼을 때만.
    (감사 결함 #5: q 훅 없이는 (2-g)V^2/G_+ 보정이 빠져 조용히 틀렸다.)"""
    from bianchi.charts import general as G
    from bianchi.matter.fluid import TiltedFluid, sources

    cbt, y, args, a, Sigma, Nmat, Avec, R = _bt_state_and_maps()
    g = args["gamma"]
    f = TiltedFluid.of(g, float(a["Omega"]), np.array([float(y.v1), float(y.v2),
                                                       float(y.v3)]))
    src = sources(f, jnp.asarray(Sigma), jnp.asarray(Avec))
    gargs = {"gamma": g, "Omega": float(a["Omega"]), "q": float(a["q"]),
             "Pi": src["Pi"], "R": jnp.asarray(R)}
    dG = G.rhs(0.0, G.StateG.of(Sigma, Nmat, Avec), gargs)

    d = cbt.rhs(0.0, y, args)
    dSigma_ref = np.asarray(cbt.shear_matrix(d))          # shear_matrix 는 선형
    dN_ref = np.zeros((3, 3))
    lamv, Nv = float(y.lam), float(y.N)
    dN_ref[1, 1] = dN_ref[2, 2] = SQRT3 * (float(d.lam) * Nv + lamv * float(d.N))
    dN_ref[1, 2] = dN_ref[2, 1] = SQRT3 * float(d.N)
    dA_ref = np.array([float(d.A), 0.0, 0.0])

    assert np.abs(np.asarray(dG.Sigma) - dSigma_ref).max() < 1e-12
    assert np.abs(np.asarray(dG.N) - dN_ref).max() < 1e-12
    assert np.abs(np.asarray(dG.A) - dA_ref).max() < 1e-12


def test_general_chart_without_q_hook_is_wrong_for_tilted_matter():
    """q 훅을 생략하면 불일치가 실제로 발생함을 고정 (회귀 방지용 음성 통제)."""
    from bianchi.charts import general as G
    from bianchi.matter.fluid import TiltedFluid, sources

    cbt, y, args, a, Sigma, Nmat, Avec, R = _bt_state_and_maps()
    g = args["gamma"]
    f = TiltedFluid.of(g, float(a["Omega"]), np.array([float(y.v1), float(y.v2),
                                                       float(y.v3)]))
    src = sources(f, jnp.asarray(Sigma), jnp.asarray(Avec))
    gargs = {"gamma": g, "Omega": float(a["Omega"]),      # q 생략!
             "Pi": src["Pi"], "R": jnp.asarray(R)}
    dG = G.rhs(0.0, G.StateG.of(Sigma, Nmat, Avec), gargs)
    d = cbt.rhs(0.0, y, args)
    dSigma_ref = np.asarray(cbt.shear_matrix(d))
    assert np.abs(np.asarray(dG.Sigma) - dSigma_ref).max() > 1e-6


# ══════════════════════════════ 결함 #3: 투영기 무등록 차트 침묵 금지
def test_projector_registry_no_silent_identity():
    from bianchi import constraints as con
    from bianchi.charts import class_b_tilted as cbt
    from bianchi.charts import type_ix_d as ixd

    # tilted class B: C2 위반 상태가 실제로 투영으로 줄어야 한다
    y = cbt.StateBT.of(0.3, 0.2, 0.15, -0.1, 0.05, 0.4, 0.3, 0.35, .1, .05, -.05)
    args = {"gamma": 4.0 / 3.0}
    proj = con.make_projector(cbt)
    before = max(abs(float(v)) for k, v in cbt.constraints(y, args).items()
                 if k in ("C2", "C3", "C4"))
    y2 = proj(y, args)
    after = max(abs(float(v)) for k, v in cbt.constraints(y2, args).items()
                if k in ("C2", "C3", "C4"))
    assert after < before * 1e-3, (before, after)

    # IX-D: definition 위반이 줄어야 한다
    yd = ixd.StateD.of(0.9, [0.2, -0.1, -0.1], [1.2, 1.0, 0.8])
    argsd = {"gamma": 1.0}
    projd = con.make_projector(ixd)
    b = abs(float(ixd.constraints(yd, argsd)["definition"]))
    yd2 = projd(yd, argsd)
    aft = abs(float(ixd.constraints(yd2, argsd)["definition"]))
    assert aft < b * 1e-3, (b, aft)

    # 미등록 차트는 조용히 통과하지 않고 명시적으로 실패해야 한다
    class Fake:
        name = "unknown_chart"
    with pytest.raises(ValueError):
        con.make_projector(Fake())

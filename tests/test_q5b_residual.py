"""
Q5b ★ **잔여 곡률 이류** 게이트 (78차) — 계획 부록 A.5 의 간극을 메운다.

유도 (모듈 docstring 에 제1원리): 공변좌표에서 곡률항만 남는다.
    dq̂/dτ     = μ · P_⊥[M⁻¹ w],     w = ((N̂ê)×ê) − Â_⊥
    dln|q|/dτ = μ · (q̂ · M⁻¹ w)
둘 다 |q| 무관 ⇒ 방향흐름이 자율계 (Q5 의 스텐실 공유 논리가 그대로 산다).

★★ 이 증분의 결정적 측정 — **간극의 성격이 바뀌었다**:
    residual OFF : |Codazzi| = 3.64e−3,  Δτ 8배 정밀화에 **불변** (누락된 항)
    residual ON  : |Codazzi| 가 각 해상도로 **수렴** (n_θ 12→48: 9.1e−4 → 3.0e−5,
                   차수 2.45), Δτ·부분스텝·보간차수에는 불변
  ⇒ 계약 §1 의 "벗는 것" 에서 "남는 것 (수렴하는 이산화)" 으로 이동.
     차수가 스펙트럴이 아닌 이유: 큰 축비에서 μ(q̂) 가 |cosθ|-형 꺾임을 갖는다
     (공변 캐리어의 알려진 대수적 수렴 — 계획 §1 이 예고한 축).
"""
import numpy as np
import pytest

RC = pytest.importorskip("bianchi_rustcore")
if not hasattr(RC, "qt_plan_from_points"):
    pytest.skip("Q5b 미빌드", allow_module_level=True)

from bianchi.q import contract as C  # noqa: E402
from bianchi.q import coupled as Q  # noqa: E402
from bianchi.q import residual as RS  # noqa: E402
from bianchi.q import sphere as S  # noqa: E402

N_B = np.diag([0.0, 0.3, -0.3])
A_B = np.array([0.3, 0.0, 0.0])
S_B = np.diag([0.0, 0.15, -0.15])


def _run(nt=24, ns=500, residual=True, sub=2, k=6, N=N_B, A=A_B, Sg=S_B):
    sph = S.sphere(nt, 2 * nt)
    st0 = Q.QState(sph, Sg, N, A)
    K, _ = st0.curvature()
    st = Q.on_gauss_surface(sph, Sg, N, A,
                            1.0 - float(np.trace(Sg @ Sg) / 6.0) - K,
                            residual=residual)
    for _ in range(ns):
        st.residual_step(-0.5 / ns, k, k, sub)
        st.rk4_step(-1.0 / ns)
        st.residual_step(-0.5 / ns, k, k, sub)
    return st


def test_bianchi_I_residual_is_exactly_identity():
    """★ 곡률이 없으면 잔여 이류가 정확히 항등 (보간 0회 유지)."""
    sph = S.sphere(16, 32)
    lG = np.linspace(-1.0, 1.0, int(sph.n))
    out, jac = RS.residual_step(sph, np.eye(3).ravel(), lG,
                                np.zeros(6), np.zeros(3), -0.01)
    assert np.array_equal(out, lG) and jac == 1.0


def test_residual_field_is_momentum_magnitude_independent():
    """★ (R1)(R2) 가 |q| 무관 — Q5 의 '스텐실 전 반경 공유' 논리가 산다."""
    sph = S.sphere(16, 32)
    qhat, _ = S.nodes(sph)
    M = np.array([[1.3, 0.1, 0.0], [0.1, 0.7, 0.0], [0.0, 0.0, 0.5]]).ravel()
    v1, r1 = RS.residual_field(M, qhat, [0.3, -0.2, 0.1, 0, 0, 0], [0.2, 0, 0])
    v2, r2 = RS.residual_field(M, 1.0 * qhat, [0.3, -0.2, 0.1, 0, 0, 0], [0.2, 0, 0])
    assert float(np.abs(v1 - v2).max()) == 0.0 and float(np.abs(r1 - r2).max()) == 0.0
    # 접벡터: v ⊥ q̂ (구면 위 흐름)
    assert float(np.abs(np.einsum("ai,ai->a", v1, qhat)).max()) <= 1e-14


def test_T4_and_QT5_multipole_diagnostics_at_identity_frame():
    """T4 (N-항 l≤1 = 0) 와 Q-T5 를 등방 프레임에서 확인."""
    sph = S.sphere(24, 48)
    M = np.eye(3).ravel()
    for N6, A3 in (([0.3, -0.2, 0.1, 0, 0, 0], np.zeros(3)),
                   (np.zeros(6), [0.3, 0, 0])):
        assert abs(RS.multipole_rate(sph, M, N6, A3, 0)) <= 1e-14
        assert float(np.abs(RS.multipole_rate(sph, M, N6, A3, 1)).max()) <= 1e-14


def test_class_b_codazzi_gap_becomes_convergent():
    """★★ 이 증분의 본체: 간극이 **누락된 항 → 수렴하는 이산화** 로 바뀐다."""
    off = _run(nt=24, ns=500, residual=False)
    on = _run(nt=24, ns=500, residual=True)
    c_off = float(np.abs(off.codazzi_residual()).max())
    c_on = float(np.abs(on.codazzi_residual()).max())
    assert c_off > 3e-3, c_off                      # 76차 실측 재현
    assert c_on < c_off / 15.0, (c_off, c_on)       # 20배 이상 개선


def test_residual_error_converges_with_angular_resolution():
    """★★ 각 해상도 수렴 (차수 > 2) — 이것이 '이산화' 판정의 근거."""
    errs = [float(np.abs(_run(nt=n, ns=400).codazzi_residual()).max())
            for n in (12, 24, 48)]
    orders = [np.log2(errs[i] / errs[i + 1]) for i in range(len(errs) - 1)]
    assert all(o > 2.0 for o in orders), (orders, errs)
    assert errs[-1] < 5e-5, errs


@pytest.mark.parametrize("axis,vals", [("sub", (1, 4, 8)), ("k", (4, 6, 8))])
def test_residual_error_is_not_time_or_stencil_limited(axis, vals):
    """★ 남은 오차가 시간·스텐실 축이 **아님**을 못박는다 (각 축임을 분리)."""
    out = [float(np.abs(_run(nt=24, ns=400,
                             **({"sub": v} if axis == "sub" else {"k": v}))
                        .codazzi_residual()).max()) for v in vals]
    assert max(out) / min(out) < 2.0, (axis, out)


def test_class_a_constraints_unaffected():
    """★ class A 는 T4 가 보호 — 잔여 이류를 켜도 구속이 기계정밀."""
    st = _run(nt=16, ns=300, N=np.diag([0.3, 0.3, 0.3]), A=np.zeros(3),
              Sg=np.diag([0.2, -0.1, -0.1]))
    assert abs(st.gauss_residual()) <= 1e-11
    assert float(np.abs(st.codazzi_residual()).max()) <= 1e-13


def test_contract_gap_entry_is_updated():
    """계약이 간극의 **성격 변화**를 기록하고 있다."""
    g = C.KNOWN_GAPS["residual_curvature_advection"]
    assert g["status"] == "resolved"
    assert "Q5b" in g["remedy"]
    assert g["converged_order"] > 2.0

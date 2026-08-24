"""
P 티어 · **편광** 게이트 (84차) — P0·P2′·P-C·P-T·P4·P5·P6·P7.

유도: `docs/P-DERIVATION.md` (D1–D5), 감사 `audit/p1_*`, `audit/p3_*`.

★★ 이 파일이 박제하는 두 결과
  (D3) 스크린 홀로노미가 **배율 1 의 순수 SO(2)** ⇒ 편광 수송은 텐서 문제가
       아니라 각 하나짜리 문제다.
  (D5) 편광 Thomson 이 **정확히 rank-9** ⇒ l-분해 없이 3항 정확 지수.
★★ 그리고 P4 가 미해결 하나를 **닫았다**: 편광/무편광 차는 앨리어싱이 아니라
    **E→I 되먹임 (물리)** 이고, **l=2 를 통해서만** 들어오며 (νΔτ)² 로 커진다.
"""
import numpy as np
import pytest

from audit import p1_polarized_transport as A1
from audit.p3_polarized_thomson import grid, scalar_three_term
from bianchi.q import contract as C
from bianchi.q import polarization as PL


@pytest.fixture(scope="module")
def g():
    e, w = grid(24, 48)
    return e, w


# ───────────────────────────────── P0 계약
def test_p0_polarization_contract():
    """★ 규약 검사 3종 + Stokes 부호 규약이 **필요 없다**는 사실의 박제."""
    r = C.validate_polarization()
    assert all(r.values()), r
    assert C.POLARIZATION["stokes_basis_required"] is False
    assert C.POLARIZATION["kernel_rank"] == 9
    assert C.POLARIZATION["screen_holonomy_scale"] == 1.0


def test_p0_kcal_eigenvalues_recomputed(g):
    """★ 하드코딩 금지 — 구적 재계산이 계약 상수와 일치 (k_l 조항의 편광판)."""
    e, w = g
    got = PL.kcal_eigenvalues_numeric(e, w)
    ref = C.POLARIZATION["kcal_eigenvalues"]
    assert max(abs(got[i] - ref[i]) for i in range(3)) <= C.budget("P0", "kcal_eigen")


# ───────────────────────────────── P2′ 캐리어
def test_p2_carrier_roundtrip_and_constraint(g):
    e, w = g
    rng = np.random.default_rng(0)
    J = PL.project_screen(e, rng.standard_normal((len(w), 3, 3)))
    assert np.abs(PL.unpack9(PL.pack9(J)) - J).max() <= 1e-15
    assert PL.screen_leak(e, J) <= C.budget("P2", "screen_leak")


def test_p2_unpolarized_roundtrip(g):
    """무편광 J = (I/2)Π 의 세기 왕복.

    ★ 정정 (84차): 처음엔 **비트**를 요구했다.  해석적으로는 정확하지만
    (tr = (I/2)(3−1) = I), 실제 계산은 세 float 의 합이라 반올림이 남는다.
    비트를 요구하는 것은 **부동소수 산술을 모르는 게이트**다 — 임계를 1e−15 로
    두고 이유를 여기 적는다.  '비트' 요구는 P4 의 I-채널 자유흐름에만 남긴다."""
    e, w = g
    I0 = 1.0 + 0.5 * np.random.default_rng(1).standard_normal(len(w))
    d = float(np.abs(PL.intensity(PL.unpolarized(e, I0)) - I0).max())
    assert d <= 1e-15, d


# ───────────────────────────────── P-C 충돌
@pytest.mark.parametrize("x", [0.01, 0.1, 1.0, 5.0, 50.0])
def test_pc_three_term_vs_taylor(g, x):
    """★★ rank-9 3항 vs 직접 구적 Taylor 심판 (계약 1e−13)."""
    e, w = g
    rng = np.random.default_rng(2)
    J = PL.project_screen(e, rng.standard_normal((len(w), 3, 3)))
    a, b = PL.collide(e, w, J, x), PL.collide_taylor(e, w, J, x)
    assert float(np.abs(a - b).max() / np.abs(b).max()) <= C.budget("PC", "vs_taylor")


def test_pc_stiff_limit_and_conservation(g):
    """강성 소멸 + 광자 수 보존 (편광판)."""
    e, w = g
    rng = np.random.default_rng(3)
    J = PL.project_screen(e, np.abs(rng.standard_normal((len(w), 3, 3))))
    big = PL.collide(e, w, J, C.budget("PC", "stiff_x"))
    assert np.isfinite(big).all()
    assert np.abs(big - PL.collide(e, w, J, 1e7)).max() <= 1e-12
    n0 = float((w * PL.intensity(J)).sum())
    for x in (0.1, 3.0, 1e3):
        n1 = float((w * PL.intensity(PL.collide(e, w, J, x))).sum())
        assert abs(n1 - n0) / abs(n0) <= C.budget("PC", "number")


def test_pc_polarization_only_from_quadrupole(g):
    """★★ 물리 서명: 등방 입사는 편광을 **정확히 0** 만든다."""
    e, w = g
    iso = PL.unpolarized(e, np.ones(len(w)))
    out = PL.collide(e, w, iso, 1.0)
    pol = out - PL.unpolarized(e, PL.intensity(out))
    assert float(np.abs(pol).max()) <= C.budget("PC", "iso_no_polarization")
    aniso = PL.unpolarized(e, 1.0 + 0.8 * e[:, 2] ** 2)
    out2 = PL.collide(e, w, aniso, 1.0)
    pol2 = out2 - PL.unpolarized(e, PL.intensity(out2))
    assert float(np.abs(pol2).max()) > 1e-3


def test_pc_V_not_generated(g):
    """Thomson 은 원편광을 만들지 않는다 (대칭 입력 → 반대칭 출력 0)."""
    e, w = g
    rng = np.random.default_rng(4)
    J = PL.project_screen(e, rng.standard_normal((len(w), 3, 3)))
    J = 0.5 * (J + np.einsum("aij->aji", J))
    out = PL.collide(e, w, J, 1.0)
    assert float(np.abs(out - np.einsum("aij->aji", out)).max()) <= 1e-14


# ───────────────────────────────── P-T 수송
@pytest.mark.parametrize("kind", ["V", "II"])
def test_pt_screen_transport_vs_coordinate(kind):
    """★★ 스크린 수송률이 좌표 평행이동을 재현 (계약 1e−12)."""
    traj, bg = A1.coord_transport(kind, nstep=3000, four=True)
    t0, P0, V0 = traj[0]; tE, PE, VE = traj[-1]
    W0, WE = A1.screen_rep(V0, P0), A1.screen_rep(VE, PE)

    def f(y, t):
        p, W = y[:3], y[3:]
        H, S, R, N, Aa = bg(t)
        E = np.linalg.norm(p)
        dp = (-H * p - S @ p + np.cross(R, p)
              + (np.cross(N @ p, p) + (Aa @ p) * p - Aa * (p @ p)) / E)
        dW = PL.screen_vector_rate(W[None, :], p[None, :], H, S, R, N, Aa)[0]
        return np.concatenate([dp, dW])

    y = np.concatenate([P0[1:], W0]); n = 3000; h = (tE - t0) / n; t = t0
    for _ in range(n):
        k1 = f(y, t); k2 = f(y + 0.5 * h * k1, t + 0.5 * h)
        k3 = f(y + 0.5 * h * k2, t + 0.5 * h); k4 = f(y + h * k3, t + h)
        y = y + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4); t += h
    tol = C.budget("PT", "vs_coordinate")
    assert float(np.abs(y[3:] - WE).max() / np.abs(WE).max()) <= tol


@pytest.mark.parametrize("kind", ["V", "II"])
def test_pt_screen_holonomy_is_pure_rotation(kind):
    """★★ D3 의 승격: 배율 1 의 순수 SO(2), 제약 이탈 기계정밀."""
    r = A1.d3_screen_holonomy_is_rotation(kind, nstep=3000)
    assert r["leak"] <= 1e-13
    assert abs(r["aniso"]) <= 1e-12
    assert abs(r["scale"] - 1.0) <= 1e-12


def test_pt_rodrigues_rotates_linear_polarization_at_2psi(g):
    """spin-2 확인: 스크린 회전 ψ 는 선형편광을 2ψ 로 돌린다."""
    e, w = g
    rng = np.random.default_rng(5)
    J = PL.project_screen(e, rng.standard_normal((len(w), 3, 3)))
    J = 0.5 * (J + np.einsum("aij->aji", J))
    psi = np.full(len(w), np.pi / 2)
    _, Q0, U0, _ = PL.stokes_diagnostic(e, J)
    _, Q1, U1, _ = PL.stokes_diagnostic(e, PL.rotate_screen(J, e, psi))
    # 2ψ = π ⇒ (Q,U) → −(Q,U)
    assert float(np.abs(Q1 + Q0).max()) <= 1e-12
    assert float(np.abs(U1 + U0).max()) <= 1e-12


# ───────────────────────────────── P4 무편광 축약 ★★
def test_p4_unpolarized_reduction_is_exact_except_quadrupole(g):
    """★★ 미해결의 해소: 차이는 **l=2 를 통해서만** 들어온다."""
    e, w = grid(32, 64)
    z = e[:, 2]
    modes = {0: np.ones(len(w)), 1: z, 2: 0.5 * (3 * z ** 2 - 1),
             3: 0.5 * (5 * z ** 3 - 3 * z),
             4: (35 * z ** 4 - 30 * z ** 2 + 3) / 8}
    d = {}
    for l, f in modes.items():
        I0 = 1.0 + 0.6 * f
        d[l] = float(np.abs(PL.intensity(PL.collide(e, w, PL.unpolarized(e, I0), 2.0))
                            - scalar_three_term(e, w, I0, 2.0)).max())
    tol = C.budget("P4", "collide")
    for l in (0, 1, 3, 4):
        assert d[l] <= tol, (l, d)
    assert d[2] > 1e-3, d                        # l=2 만 유의미


def test_p4_difference_is_physics_not_aliasing():
    """★★ 각 해상도로 **수렴하지 않는다** ⇒ 앨리어싱이 아니라 물리."""
    vals = []
    for nt in (16, 24, 32, 48):
        e, w = grid(nt, 2 * nt)
        I0 = 1.0 + 0.6 * 0.5 * (3 * e[:, 2] ** 2 - 1)
        vals.append(float(np.abs(
            PL.intensity(PL.collide(e, w, PL.unpolarized(e, I0), 2.0))
            - scalar_three_term(e, w, I0, 2.0)).max()))
    assert min(vals) > 1e-3, vals                       # 사라지지 않는다
    assert (max(vals) - min(vals)) / max(vals) < 0.25, vals   # 정체한다


def test_p4_feedback_is_second_order_in_nu_dt():
    """★ E→I 되먹임이 (νΔτ)² — 무편광 솔버는 1차까지 정확하고 2차에서 틀린다."""
    e, w = grid(32, 64)
    I0 = 1.0 + 0.6 * 0.5 * (3 * e[:, 2] ** 2 - 1)
    xs = np.array([1e-3, 3e-3, 1e-2, 3e-2])
    ds = [float(np.abs(PL.intensity(PL.collide(e, w, PL.unpolarized(e, I0), x))
                       - scalar_three_term(e, w, I0, x)).max()) for x in xs]
    p = float(np.polyfit(np.log(xs), np.log(ds), 1)[0])
    assert abs(p - 2.0) <= 0.1, (p, ds)


# ───────────────────────────────── P5 / P6 / P7
def test_p5_cost_model():
    c = PL.cost_model(9216, n_p=200)
    assert c["bytes_per_node"] == C.budget("P5", "bytes_per_node")
    assert c["state_bytes"] == 9 * 8 * 9216 * 200
    assert c["state_bytes"] / 1e6 > 100.0        # ★ 멤버당 100 MB 초과 — 앙상블 제약


def test_p6_observables_are_marked_diagnostic(g):
    """★ E/B 언어는 선형이론 것 — 이름에 `_diagnostic` 이 박혀 있어야 한다."""
    assert PL.multipoles_diagnostic.__name__.endswith("_diagnostic")
    assert PL.stokes_diagnostic.__name__.endswith("_diagnostic")
    assert "선형이론" in PL.multipoles_diagnostic.__doc__
    e, w = g
    iso = PL.unpolarized(e, np.ones(len(w)))
    m = PL.multipoles_diagnostic(e, w, iso, l_max=2)
    assert abs(m[0]["I"] - 1.0) <= 1e-12
    assert abs(m[2]["I"]) <= 1e-12
    assert float(np.abs(PL.polarization_fraction(e, iso)).max()) <= 1e-14


def test_p7_b2b_contract_unchanged_but_response_differs(g):
    """★★ B2b 영향평가 — **사전 등록한 예상이 반쯤 빗나갔고, 그게 결론이다.**

    계약 자체는 무변경이다: 외부 모듈은 x_e(z) 만 주고, ν_τ = σ_T n_e c/H 정의도
    그대로다.  편광은 전부 **우리 쪽 충돌 연산자 안**의 일이다.

    그러나 사전 등록한 검증 ("x_e ±10% 에서 l=2 응답 민감도가 무편광과 같은가")
    은 **실패한다** — 그리고 실패해야 맞다.  P4 가 방금 보인 대로 편광은 l=2
    감쇠를 (νΔτ)² 로 바꾸므로, l=2 응답의 x_e-민감도는 **달라야** 한다.
    ⇒ 결론: 접합면(계약)은 무변경, 그러나 **x_e 로부터 관측량까지의 민감도는
      편광 여부에 의존**한다.  외부 모듈 작성자에게는 전자가, 이쪽 오차예산에는
      후자가 중요하다.  두 문장을 분리해 적는 것이 이 시험의 목적이다."""
    from bianchi.thermo.history_api import SahaHistory, validate_history
    assert all(validate_history(SahaHistory()).values())
    e, w = g
    I0 = 1.0 + 0.6 * 0.5 * (3 * e[:, 2] ** 2 - 1)
    base = 1.0

    def resp(nu, polarized):
        if polarized:
            out = PL.intensity(PL.collide(e, w, PL.unpolarized(e, I0), nu))
        else:
            out = scalar_three_term(e, w, I0, nu)
        return float((w * 0.5 * (3 * e[:, 2] ** 2 - 1) * out).sum())

    sens = []
    for pol in (True, False):
        hi, lo = resp(1.1 * base, pol), resp(0.9 * base, pol)
        sens.append((hi - lo) / (0.2 * base))
    rel = abs(sens[0] - sens[1]) / max(abs(sens[1]), 1e-30)
    # 계약 무변경 (외부 인터페이스): 이건 반드시 참이어야 한다
    from bianchi.thermo import history_api as HA
    assert hasattr(HA, "thomson_rate") and hasattr(HA, "validate_history")
    assert "polariz" not in "".join(HA.IonizationHistory.__annotations__).lower()
    # 민감도는 **다르다** — 그리고 그것이 P4 의 물리적 귀결이다
    assert rel > C.budget("P7", "xe_sensitivity_ratio"), (rel, sens)
    assert rel < 1.0, (rel, sens)          # 그러나 같은 차수 (계약을 갈아엎진 않는다)

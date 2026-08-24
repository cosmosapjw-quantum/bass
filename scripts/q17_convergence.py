"""
Q17 · **수렴 · 오차예산** — 계약 §1 "남는 것" 을 전부 숫자로 (76차).

이 스크립트가 `docs/Q-ERROR-BUDGET.md` 를 **자동 생성**한다 (수기 표 금지).
사용:  PYTHONPATH=. python scripts/q17_convergence.py
"""
from __future__ import annotations

import numpy as np

from bianchi.q import collide as X
from bianchi.q import coupled as QC
from bianchi.q import sphere as S
from bianchi.q import transport as T


FLOOR = 1e-15


def _order(errs):
    """차수 추정.  기계정밀 바닥에 닿은 구간은 제외한다 (log2(0) 방지)."""
    out = []
    for i in range(len(errs) - 1):
        if errs[i] <= FLOOR or errs[i + 1] <= FLOOR:
            continue
        out.append(float(np.log2(errs[i] / errs[i + 1])))
    return out


def axis_time():
    """시간 (RK4) — 4차."""
    sph = S.sphere(16, 32)

    def run(ns):
        Sg = np.diag([0.2, -0.1, -0.1]); N = np.diag([0.3, 0.3, 0.3])
        st0 = QC.QState(sph, Sg, N, np.zeros(3)); K, _ = st0.curvature()
        st = QC.on_gauss_surface(sph, Sg, N, np.zeros(3),
                                 1 - float(np.trace(Sg @ Sg) / 6) - K)
        QC.evolve(st, -1.0 / ns, ns)
        return st.ln_omega()
    ref = run(3200)
    e = [abs(run(n) - ref) for n in (50, 100, 200)]
    return "time (RK4)", 4.0, _order(e), e


def axis_splitting():
    """분할 (Strang) — 2차."""
    sph = S.sphere(16, 32)

    def run(ns):
        Sg = np.diag([0.1, -0.05, -0.05])
        st0 = QC.QState(sph, Sg, np.zeros((3, 3)), np.zeros(3)); K, _ = st0.curvature()
        st = QC.on_gauss_surface(sph, Sg, np.zeros((3, 3)), np.zeros(3),
                                 1 - float(np.trace(Sg @ Sg) / 6) - K,
                                 aniso=lambda x: 1 + 0.4 * x[2] ** 2)
        QC.evolve(st, -0.5 / ns, ns, nu=3.0)
        return st.ln_omega()
    ref = run(1600)
    e = [abs(run(n) - ref) for n in (25, 50, 100)]
    return "splitting (Strang)", 2.0, _order(e), e


def axis_radial():
    """반경 시프트 — 8점 Lagrange, 실효 ≥6."""
    errs = []
    dln = 0.23
    for n in (48, 96, 192, 384):
        r = T.radial(-5.0, 5.0, n)
        lnf = T.planck_lnf(r)
        got = np.asarray(r.apply_shift_log(lnf, dln, 8, "wien"))
        p = np.asarray(r.p())
        ref = np.log(1.0 / np.expm1(p * np.exp(-dln)))
        # 경계 제외 폭은 스텐실 + **시프트 셀 수** 만큼 (외삽은 별도 축)
        k = 8 + int(np.ceil(abs(dln) / float(r.dlnp)))
        errs.append(float(np.abs(got[k:-k] - ref[k:-k]).max()))
    return "radial (shift)", 6.0, _order(errs), errs


def axis_angular():
    """각 격자 — 스펙트럴 (지수 감쇠)."""
    errs = []
    for nt in (8, 12, 16, 24):
        sph = S.sphere(nt, 2 * nt)
        e, w = S.nodes(sph)
        f = np.exp(2.0 * e[:, 2])                     # 대역 무한, 매끄러움
        got = float((w * f).sum())
        ref = 4.0 * np.pi * np.sinh(2.0) / 2.0
        errs.append(abs(got - ref) / ref)
    return "angular (GL×uniform)", float("inf"), _order(errs), errs


def axis_collision():
    """충돌 — **정확** (이산화 축이 아니다).  dense expm 대비 잔차."""
    sph = S.sphere(16, 32)
    e, w = S.nodes(sph)
    rng = np.random.default_rng(0)
    f = 1.0 + 0.7 * rng.standard_normal(len(w))
    M = X.dense_operator(sph)
    errs = [float(np.abs(X.collide(sph, f, x) - X.dense_expm_apply(M, f, x)).max()
                  / np.abs(f).max()) for x in (0.1, 1.0, 10.0)]
    return "collision (exact 3-term)", 0.0, [0.0] * (len(errs) - 1), errs


def _exp_rate(errs, ns):
    """지수 수렴의 감쇠율:  ln(err) ~ -rate * n  의 기울기 (대수 차수가 아니다)."""
    import numpy as np
    return -float(np.polyfit(np.asarray(ns, float), np.log(np.asarray(errs)), 1)[0])


def _modeb_err(nt, n_p=200, lo=-8.0, hi=5.0):
    """Mode A ≡ Mode B (충돌 포함) 불일치 — 81차 정정 이후의 일관성 오차."""
    import numpy as np
    from bianchi.q import coupled as QC
    from bianchi.q import modeb as MB
    M = np.array([[1.6, 0, 0], [0, 0.7, 0], [0, 0, 0.5]]).ravel()
    sph = S.sphere(nt, 2 * nt)
    b = MB.planck_state(sph, n_p=n_p, lnq_min=lo, lnq_max=hi)
    b.M = M.copy()
    a = QC.QState(sph, np.zeros((3, 3)), np.zeros((3, 3)), np.zeros(3),
                  lG=b.ln_ghat(), M=M.copy())
    a.collide(1.0)
    MB.evolve(b, -1e-12, 1, nu=1e12)
    return float(np.abs(a.lG - b.ln_ghat()).max())


def axis_modeb_angular():
    """★ Mode B 일관성 — **각 해상도** 축.  대수가 아니라 **지수** 수렴이다.

    (Q5b 의 공변 꺾임 축과 대조: 거기는 mu 의 |cos| 꺾임 때문에 대수 2.45.
     여기는 피적분함수가 매끄러워 지수.)"""
    ns = [8, 12, 16, 24, 32]
    errs = [_modeb_err(n) for n in ns]
    return ("modeB angular (A≡B, 지수)", float("inf"),
            [_exp_rate(errs, ns)], errs)


def axis_modeb_range():
    """★ Mode B 일관성 — **반경 정의역** 축 (해상도 아님).  꼬리가 지수적이라
    격자가 열 피크를 덮는 순간 오차가 지수로 사라진다."""
    spans = [(-4.0, 2.0, 120), (-6.0, 3.0, 150), (-8.0, 5.0, 200)]
    errs = [_modeb_err(16, npp, lo, hi) for lo, hi, npp in spans]
    widths = [hi - lo for lo, hi, _ in spans]
    return ("modeB radial range (지수)", float("inf"),
            [_exp_rate(errs, widths)], errs)


def axis_angular_kinked():
    """★ 각 격자 — **공변 캐리어의 꺾임** (Q5b): class B Codazzi 잔차로 잰다.
    매끄러운 피적분함수의 스펙트럴 수렴과 달리 대수적 (μ 의 |cosθ| 꺾임)."""
    import numpy as np
    from bianchi.q import coupled as QC
    N = np.diag([0.0, 0.3, -0.3]); A = np.array([0.3, 0.0, 0.0])
    Sg = np.diag([0.0, 0.15, -0.15])
    errs = []
    for nt in (12, 24, 48):
        sph = S.sphere(nt, 2 * nt)
        st0 = QC.QState(sph, Sg, N, A); K, _ = st0.curvature()
        st = QC.on_gauss_surface(sph, Sg, N, A,
                                 1 - float(np.trace(Sg @ Sg) / 6) - K)
        QC.evolve(st, -1.0 / 400, 400)
        errs.append(float(np.abs(st.codazzi_residual()).max()))
    return "angular (comoving kink, Q5b)", 2.45, _order(errs), errs


AXES = [axis_time, axis_splitting, axis_radial, axis_angular,
        axis_angular_kinked, axis_modeb_angular, axis_modeb_range,
        axis_collision]


def main(path="docs/Q-ERROR-BUDGET.md"):
    rows = []
    for f in AXES:
        rows.append(f())
    lines = ["# Q-ERROR-BUDGET (자동 생성 — 수기 편집 금지)", "",
             "계약 §1 '남는 것' 의 실측.  생성: `scripts/q17_convergence.py`", "",
             "| 축 | 기대 차수 | 실측 차수 | 오차열 |", "|---|---|---|---|"]
    for name, want, ords, errs in rows:
        w = "스펙트럴" if want == float("inf") else ("정확" if want == 0 else f"{want:g}")
        if want == float("inf") and ords:
            o = f"감쇠율 {ords[0]:.2f}/노드"      # 지수 축은 차수가 아니라 율
        else:
            o = ", ".join(f"{x:.2f}" for x in ords) if ords else "—"
        e = ", ".join(f"{x:.2e}" for x in errs)
        lines.append(f"| {name} | {w} | {o} | {e} |")
    lines += ["", "★ '스펙트럴' 축은 대수 차수가 없다 — ln(오차) 의 **감쇠율**로 적는다.",
              "  Q5b 의 공변 꺾임 축만 대수 (2.45) 다: mu(q̂) 의 |cosθ| 꺾임 때문.",
              "", "결합 예산 (제곱합):",
              f"  총 = {np.sqrt(sum(r[3][-1] ** 2 for r in rows)):.3e}", "",
              "★ 충돌 축은 수렴하는 오차가 아니라 **정확**이다 (3항 공식) — "
              "이것이 강성·근사 절환을 없앤 근거."]
    open(path, "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))
    return rows


if __name__ == "__main__":
    main()

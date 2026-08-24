"""
D2 · **구속 사영과 감시** — 위반은 어떻게 자라고, 투영은 무엇을 고치는가.

K5b §7 은 "Codazzi 를 깨면 Friedmann 이 따라 자란다" 를 **관찰만** 했다.
`bianchi/constraints.py` 는 class B 증폭률 `4(q + Σ₊ − 1)` 을 **인용**해 두었을 뿐
어디에서도 재지 않았고, 일반 차트에서는 `amplification_rate` 가 그냥 0.0 을 돌려준다.
여기서 셋 다 메운다.

★ 이 파일이 하는 것:
  1. **(F, C) 가 닫힌 선형계인가** — 가정하지 않고 측정한다.  독립 섭동 둘로 기본해
     행렬 Φ(t) 를 만들고, **셋째 섭동을 예측**해 맞는지 본다 (반증 가능한 검사).
  2. **물리 단위 투영기** — δh 최소노름 Gauss-Newton.  J 는 해석적이다:
         ∂F/∂h_i = 2H − σ_i ,        ∂C/∂h_i = 3(A/a₁)(δ_{i1} − ⅓)
     (ρ 와 q₁ 은 h 에 안 들어간다 — 물질은 노드가 나르므로 순간적으로 h 와 무관.)
  3. **투영이 무엇을 고치고 무엇을 못 고치는지** 정직하게 잰다.  구속은 되찾지만
     **해가 달라진다** — 그 거리를 숫자로 낸다.

단위: 8πG = 1, 물리 단위 (확장정규화 아님).
"""
from __future__ import annotations

import numpy as np

from bianchi.matter import type_v_coupled as TC


# ═══════════════════════════════════════ 1. 구속 잔차와 그 야코비안
def residual(a_vec, da_vec, A, rho, q1):
    """(F, C) — K5b 의 `constraints` 와 같은 정의, 벡터로."""
    c = TC.constraints(a_vec, da_vec, A, rho, (q1, 0.0, 0.0))
    return np.array([c["friedmann"], c["codazzi"]])


def jacobian_h(a_vec, da_vec, A):
    """★ ∂(F, C)/∂h_i — **해석적**.  물질(ρ, q₁)은 h 에 의존하지 않는다.

        F = 3H² − ρ − σ² − 3A²/a₁²,   σ² = ½Σσ_i²,   H = ⅓Σh_i
        ∂F/∂h_i = 2H − σ_i
        C = 3σ₁A/a₁ + q₁            ⇒  ∂C/∂h_i = 3(A/a₁)(δ_{i1} − ⅓)
    """
    a = np.asarray(a_vec, float)
    h = np.asarray(da_vec, float) / a
    H = float(h.mean())
    sig = h - H
    dF = 2.0 * H - sig
    dC = 3.0 * float(A) / a[0] * (np.array([1.0, 0.0, 0.0]) - 1.0 / 3.0)
    return np.vstack([dF, dC])


def jacobian_check(a_vec=(1.0, 0.95, 1.05), da_vec=(5.0, 4.7, 5.2), A=0.7,
                   rho=73.0, q1=0.004, eps=1e-6):
    """★ 대조군 — 해석 야코비안을 **중심차분**과 대조한다 (손대수 금지)."""
    a = np.asarray(a_vec, float)
    J = jacobian_h(a, da_vec, A)
    fd = np.zeros_like(J)
    for i in range(3):
        d = np.zeros(3)
        d[i] = eps
        fd[:, i] = (residual(a, np.asarray(da_vec, float) + d * a, A, rho, q1)
                    - residual(a, np.asarray(da_vec, float) - d * a, A, rho, q1)
                    ) / (2 * eps)
    return float(np.abs(J - fd).max() / np.abs(J).max())


# ═══════════════════════════════════════ 2. ★★ (F, C) 는 닫힌 선형계인가
def _pair_trajectory(dh, nsteps, t_end, **kw):
    """δh 를 초기 ȧ 에 실어 굴리고 (F(t), C(t)) 를 돌려준다."""
    a0 = np.asarray(kw.pop("a0", (1.0, 0.95, 1.05)), float)
    A = kw.pop("A", 0.7)
    mass = kw.pop("mass", 0.6)
    shear = kw.pop("shear", 0.03)
    P, W = TC.initial_nodes(mass)
    rho0 = float(TC.moments_from_nodes(P, W, a0, mass, 0, 0)[(0, 0)])
    da0 = TC.initial_expansion(a0, A, rho0, shear)[0] + np.asarray(dh, float) * a0
    r = TC.evolve_coupled(a0=a0, A=A, mass=mass, t_end=t_end, nsteps=nsteps,
                          shear=shear, da0=da0, **kw)
    return r, np.vstack([r["friedmann"], r["codazzi"]])


def fundamental_matrix(eps=2e-3, nsteps=120, t_end=0.3, **kw):
    """★★ 독립 섭동 둘로 기본해 행렬 Φ(t) 를 **측정**한다.

    δ¹ = ε(1,1,1)/3  (등방 — H 를 흔들어 F 를 깬다)
    δ² = ε(2,−1,−1)/3 (전단 — σ₁ 을 흔들어 C 를 깬다)
    비섭동 궤적을 빼서 **선형 응답만** 남긴다 (절단오차 제거).
    """
    base, X0 = _pair_trajectory(np.zeros(3), nsteps, t_end, **kw)
    d1 = eps * np.array([1.0, 1.0, 1.0]) / 3.0
    d2 = eps * np.array([2.0, -1.0, -1.0]) / 3.0
    _, X1 = _pair_trajectory(d1, nsteps, t_end, **kw)
    _, X2 = _pair_trajectory(d2, nsteps, t_end, **kw)
    D = np.stack([X1 - X0, X2 - X0], axis=-1)          # (성분 i, 시각 n, 섭동 s)
    D0 = D[:, 0, :]                                     # (2,2) 초기 응답
    Phi = np.einsum("ins,sk->ink", D, np.linalg.inv(D0))   # Φ(t) = D(t)·D(0)⁻¹
    return dict(t=base["t"], Phi=Phi, D0=D0, base=X0)


def closure_prediction(eps=2e-3, nsteps=120, t_end=0.3, **kw):
    """★★ **반증 가능한 검사**: 셋째 섭동을 Φ 로 예측해 맞는가.

    (F, C) 가 자기들끼리 닫힌 선형계라면 Φ 가 **모든** 섭동을 옮겨야 한다.
    닫혀 있지 않다면 (예: 다른 자유도가 끼어들면) 예측이 어긋난다.
    """
    f = fundamental_matrix(eps, nsteps, t_end, **kw)
    base, X0 = _pair_trajectory(np.zeros(3), nsteps, t_end, **kw)
    d3 = eps * np.array([0.4, 1.3, -0.9])
    _, X3 = _pair_trajectory(d3, nsteps, t_end, **kw)
    dX3 = X3 - X0
    pred = np.einsum("ink,k->in", f["Phi"], dX3[:, 0])
    sc = np.abs(dX3).max(axis=1)
    return dict(t=base["t"], actual=dX3, pred=pred,
                rel=float(np.max(np.abs(pred - dX3) / sc[:, None])))


def linearity_check(eps=2e-3, ratio=2.0, nsteps=120, t_end=0.3, **kw):
    """★ 섭동 크기를 배로 키우면 응답도 배가 되는가 (선형 영역 확인)."""
    _, X0 = _pair_trajectory(np.zeros(3), nsteps, t_end, **kw)
    d = np.array([0.4, 1.3, -0.9])
    _, Xa = _pair_trajectory(eps * d, nsteps, t_end, **kw)
    _, Xb = _pair_trajectory(ratio * eps * d, nsteps, t_end, **kw)
    r = (Xb - X0) / np.where(np.abs(Xa - X0) > 0, Xa - X0, np.inf)
    return float(np.abs(r[:, 1:] - ratio).max())


def growth_rates(**kw):
    """★★ Φ 의 고윳값 → **증폭 지수**.  type V 의 구속 증폭률을 숫자로 얻는다."""
    f = fundamental_matrix(**kw)
    t, Phi = f["t"], f["Phi"]
    ev = np.array([np.sort(np.abs(np.linalg.eigvals(Phi[:, k, :])))
                   for k in range(len(t))])
    with np.errstate(divide="ignore", invalid="ignore"):
        rate = np.where(t[:, None] > 0, np.log(np.maximum(ev, 1e-300))
                        / np.where(t[:, None] > 0, t[:, None], 1.0), np.nan)
    return dict(t=t, eig=ev, rate=rate, final=ev[-1],
                mean_rate=np.nanmean(rate[len(t) // 2:], axis=0))


# ═══════════════════════════════════════ 2b. ★★ 유도한 전파 법칙과 대조
def predicted_fundamental_matrix(traj, A):
    """★★ `audit.d2_constraint_propagation` 이 유도한 법칙의 **닫힌형** Φ.

        Ḟ = −3H·F − 2(A/a₁)·C,     Ċ = −(4H + σ₁)·C = −(3H + h₁)C

    ⇒  (V·a₁·C)˙ = 0,   (V·F)˙ = −2(A/a₁)·V·C          (V = a₁a₂a₃)

        Φ_CC = V₀a₁₀/(V a₁),   Φ_FF = V₀/V,   Φ_CF = 0
        Φ_FC = **+**2A·V₀a₁₀/V · ∫₀ᵗ dt′/a₁²

    ★ 궤적의 a_i(t) 만 쓴다 — 섭동 실험을 전혀 쓰지 않는다 (독립 경로).

    ★ **부호는 논쟁이 아니라 지표 올리기로 정해진다** (실제로 여기서 틀렸었다):
      유도는 E^{μν} = G^{μν} − T^{μν} 의 **반변** 성분으로 했는데, K5b 의 감시자
      `C = 3σ₁A/a₁ + q₁` 는 **공변** 성분 기준이다.  η^{0̂0̂}η^{1̂1̂} = −1 이라
      E^{0̂1̂} = −C 이고, 그래서 F←C 결합의 부호가 뒤집힌다.  첫 판은 이걸 놓쳐
      대각 성분은 1e−4 로 맞는데 Φ_FC 만 부호가 반대로 나왔다 (상대차 6.8e−02).
    """
    from audit.d2_constraint_propagation import mixed_index_sign
    csign = mixed_index_sign()
    a = np.asarray(traj["a"], float)
    tt = np.asarray(traj["t"], float)
    V = a.prod(axis=1)
    a1 = a[:, 0]
    V0, a10 = float(V[0]), float(a1[0])
    y = 1.0 / a1 ** 2
    I = np.concatenate([[0.0], np.cumsum(0.5 * (y[1:] + y[:-1]) * np.diff(tt))])
    Phi = np.zeros((2, len(tt), 2))
    Phi[0, :, 0] = V0 / V                                  # F ← F
    Phi[1, :, 1] = V0 * a10 / (V * a1)                     # C ← C
    Phi[0, :, 1] = csign * (-2.0) * float(A) * V0 * a10 / V * I    # F ← C
    return Phi


def propagation_law_residual(eps=2e-3, nsteps=120, t_end=0.3, **kw):
    """★★ **두 경로 대조** — 섭동으로 잰 Φ vs 계량에서 유도한 닫힌형 Φ.

    측정 쪽은 결합계를 세 번 굴려 얻고, 예측 쪽은 궤적의 a_i(t) 와 유도식만 쓴다.
    """
    f = fundamental_matrix(eps, nsteps, t_end, **kw)
    base, _ = _pair_trajectory(np.zeros(3), nsteps, t_end, **kw)
    Ph = predicted_fundamental_matrix(base, kw.get("A", 0.7))
    sc = np.abs(f["Phi"]).max()
    return dict(t=f["t"], measured=f["Phi"], predicted=Ph,
                rel=float(np.abs(f["Phi"] - Ph).max() / sc),
                no_feedback=float(np.abs(f["Phi"][1, :, 0]).max() / sc))


# ═══════════════════════════════════════ 3. ★★ 물리 단위 투영기
def project(a_vec, da_vec, A, rho, q1, iters=3):
    """★★ 최소노름 Gauss-Newton 투영 — h 만 움직여 (F, C) = 0 으로 되돌린다.

        δh = −Jᵀ(JJᵀ)⁻¹ (F, C)

    ★ a_i 는 건드리지 않는다 (위치는 물질 노드와 함께 정의된 값이다).
    ★ 물질(ρ, q₁)도 건드리지 않는다 — 노드가 나르는 값이라 h 와 독립이다.
    """
    a = np.asarray(a_vec, float)
    da = np.asarray(da_vec, float).copy()
    for _ in range(int(iters)):
        c = residual(a, da, A, rho, q1)
        J = jacobian_h(a, da, A)
        dh = -J.T @ np.linalg.solve(J @ J.T, c)
        da = da + dh * a
    return da


def projection_is_minimal_norm(a_vec=(1.0, 0.95, 1.05), A=0.7, rho=73.0,
                               q1=0.004, dh=(3e-3, -1e-3, 2e-3)):
    """★ 보정이 J 의 **행공간** 안에 있는가 (영공간 성분이 0 이어야 최소노름)."""
    a = np.asarray(a_vec, float)
    da0 = np.array([5.0, 4.7, 5.2]) + np.asarray(dh, float) * a
    da1 = project(a, da0, A, rho, q1)
    corr = (da1 - da0) / a
    J = jacobian_h(a, da0, A)
    null = corr - J.T @ np.linalg.solve(J @ J.T, J @ corr)
    return float(np.linalg.norm(null) / np.linalg.norm(corr))


def projection_report(a_vec=(1.0, 0.95, 1.05), A=0.7, rho=73.0, q1=0.004):
    """★ 정합 자료에서는 무동작, 깨진 자료에서는 복원 — 둘 다 잰다."""
    a = np.asarray(a_vec, float)
    good = project(a, np.array([5.0, 4.7, 5.2]), A, rho, q1, iters=6)
    g0 = residual(a, good, A, rho, q1)
    again = project(a, good, A, rho, q1)
    bad = np.array([5.0, 4.7, 5.2]) + np.array([0.05, -0.02, 0.01]) * a
    fixed = project(a, bad, A, rho, q1, iters=4)
    return dict(restored=float(np.abs(g0).max() / rho),
                noop=float(np.abs(again - good).max() / np.abs(good).max()),
                broken_before=float(np.abs(residual(a, bad, A, rho, q1)).max() / rho),
                broken_after=float(np.abs(residual(a, fixed, A, rho, q1)).max() / rho))


# ═══════════════════════════════════════ 4. ★★ 언제 자라고, 투영이 무엇을 하는가
def violation_growth(hsign=1.0, sigma1=0.02, nsteps=60, t_end=0.15, **kw):
    """★★ 유도한 법칙의 예측 — **팽창이면 감쇠, 수축이면 증폭**.

        C ∝ 1/(V a₁),   F 의 제차해 ∝ 1/V         (V = a₁a₂a₃)

    팽창(V↑)에서는 둘 다 줄어든다.  `hsign=-1` 로 수축시키면 V 가 줄어 **자란다**.
    `constraints.py` 의 "구속은 지수 증폭한다" 는 서술은 **어느 방향인지에 달렸다**.
    """
    r = TC.evolve_coupled(hsign=hsign, sigma1=sigma1, nsteps=nsteps,
                          t_end=t_end, **kw)
    V = np.asarray(r["a"], float).prod(axis=1)
    a1 = np.asarray(r["a"], float)[:, 0]
    Cn = np.abs(r["codazzi"])
    pred = Cn[0] * (V[0] * a1[0]) / (V * a1)
    return dict(t=r["t"], C=Cn, C_pred=pred, F=np.abs(r["friedmann"]),
                V_ratio=float(V[-1] / V[0]),
                C_ratio=float(Cn[-1] / Cn[0]),
                law_residual=float(np.abs(Cn / pred - 1.0).max()))


def projection_controls_growth(nsteps=60, t_end=0.15, sigma1=0.02, hsign=-1.0,
                               **kw):
    """★★ 투영이 **실제로** 증폭을 잡는가 — 수축 구간에서 켜고/끄고 비교."""
    off = TC.evolve_coupled(hsign=hsign, sigma1=sigma1, nsteps=nsteps,
                            t_end=t_end, project=False, **kw)
    on = TC.evolve_coupled(hsign=hsign, sigma1=sigma1, nsteps=nsteps,
                           t_end=t_end, project=True, **kw)
    # ★ k=0 은 **투영 전** 초기자료다 (기록이 스텝 앞에서 일어난다).  그걸 넣으면
    #   투영판의 최대값이 초기 위반으로 덮여 "안 고쳤다" 로 보인다 — 실제로 겪었다.
    return dict(initial_C=float(abs(off["codazzi"][0] / off["rho"][0])),
                off_C=float(np.abs(off["codazzi"][1:] / off["rho"][1:]).max()),
                on_C=float(np.abs(on["codazzi"][1:] / on["rho"][1:]).max()),
                off_F=float(np.abs(off["friedmann"][1:] / off["rho"][1:]).max()),
                on_F=float(np.abs(on["friedmann"][1:] / on["rho"][1:]).max()))


def projection_moves_the_solution(nsteps=60, t_end=0.15, sigma1=0.02, **kw):
    """★★ **정직한 몫**: 투영은 구속을 되찾지만 **다른 해**로 옮긴다.

    깨진 자료를 투영하며 굴린 궤적과, 애초에 정합했던 자료의 궤적을 비교한다.
    구속 잔차는 1e−16 이 되지만 a_i 는 눈에 띄게 다르다 — 투영은 **오차를 지우는
    도구지 잘못된 초기자료를 고쳐 주는 도구가 아니다**.
    """
    good = TC.evolve_coupled(nsteps=nsteps, t_end=t_end, **kw)
    fixed = TC.evolve_coupled(nsteps=nsteps, t_end=t_end, sigma1=sigma1,
                              project=True, **kw)
    ga, fa = np.asarray(good["a"], float), np.asarray(fixed["a"], float)
    return dict(constraint=float(np.abs(fixed["codazzi"][1:]
                                        / fixed["rho"][1:]).max()),
                a_distance=float(np.abs(fa - ga).max() / np.abs(ga).max()),
                sigma1_gap=float(np.abs(fixed["sigma1"][1:]
                                        - good["sigma1"][1:]).max()))


def projection_is_harmless_on_good_data(nsteps=60, t_end=0.15, **kw):
    """★ 대조군 — 이미 정합한 자료에 매 스텝 투영해도 궤적이 안 바뀌어야 한다."""
    off = TC.evolve_coupled(nsteps=nsteps, t_end=t_end, project=False, **kw)
    on = TC.evolve_coupled(nsteps=nsteps, t_end=t_end, project=True, **kw)
    ga = np.asarray(off["a"], float)
    return dict(a=float(np.abs(np.asarray(on["a"], float) - ga).max()
                        / np.abs(ga).max()),
                rho=float(np.abs(on["rho"] / off["rho"] - 1.0).max()))


# ═══════════════════════════════════════ 5. ★★ 닫힘이 요구하는 물질 법칙
def momentum_law_residual(A=0.7, mass=0.6, t_end=0.3, nsteps=120, **kw):
    """★★ **아무도 안 가르쳐 준 법칙**: 운동론 해가 type V 운동량 보존을 만족한다.

        q̇₁ = −(4H + σ₁)q₁ − 3(A/a₁)π₁₁          (= −4Hq₁ − σ₁q₁ + 3a^bπ_ab)

    `evolve_coupled` 이 매 스텝 기록한 (노드에서 정확히 잰 q̇₁, 줄인 법칙) 을 대조한다.
    D2b 가 보인 대로 **차트의 구속계가 닫히려면 바로 이 법칙이 필요하다** — 여기서
    그게 실제로 성립함을 확인한다 (Liouville 수송에 넣은 적이 없다).

    ★ 대조군 `naive` 는 a·π 항을 뺀 판이다 (교과서의 등방 배경 형태).
    """
    r = TC.evolve_coupled(A=A, mass=mass, t_end=t_end, nsteps=nsteps, **kw)
    node = np.asarray(r["qdot_node"], float)
    law = np.asarray(r["qdot_law"], float)
    naive = np.asarray(r["qdot_naive"], float)
    sc = np.maximum(np.abs(node), 1e-300)
    return dict(t=r["t"], node=node, law=law, naive=naive,
                reduced=float(np.abs(law - node).max() / np.abs(node).max()),
                naive_err=float(np.abs(naive - node).max() / np.abs(node).max()),
                pointwise=float(np.max(np.abs(law - node) / sc)))


def iteration_convergence(a_vec=(1.0, 0.95, 1.05), A=0.7, rho=73.0, q1=0.004,
                          kick=(0.05, -0.02, 0.01)):
    """★ Gauss-Newton 이 **2차 수렴**하는가 (F 의 H² 항이 비선형이라 1회로는 안 된다)."""
    a = np.asarray(a_vec, float)
    da = np.array([5.0, 4.7, 5.2]) + np.asarray(kick, float) * a
    out = []
    for k in range(5):
        out.append(float(np.abs(residual(a, da, A, rho, q1)).max() / rho))
        da = project(a, da, A, rho, q1, iters=1)
    return out

"""
D3 · **혼합정밀 (특이점 근방)** — 어디서 배정밀도가 죽고, 무엇으로 고치는가.

D1b 의 반증 기록이 한계를 확정했다: "혼돈 증폭이 아니라 **벽의 언더플로**".  특이점
쪽으로 벽 N_i 는 에라마다 기하급수로 죽어 f64 의 표현바닥(ln 1e−308 ≈ −709)을
만나고, 그 아래서는 선형 표현의 튐 수열이 물리가 아니다 (D1c 의 접두부 절단이 자르던
병리 행이 그 잔재다).

★★ 고침은 정밀도 상향이 아니라 **표현 혼합**이다:
    Σ±  : f64 그대로 (O(1) 양 — 조건수 측정이 아래에 있다)
    벽   : w = ln|N| (f64) — 표현범위 ±1.8e308, 사실상 무한 깊이
곱셈 구조 dN/dτ = rate·N 이 덧셈 dw/dτ = rate 가 되므로 **물리를 근사 없이** 옮긴다.
측정 (u₀ = 2+1/√2, 은비 주기궤도, 8000 τ̃):
    선형: 표현한계 w ≥ −709,  그 근방부터 u 표류
    로그: w = **−2197** 까지 추적, u 는 주기점 √2+1 에 5e−3 이내로 고정

★★ 그리고 로그 표현이 **다음 한계를 드러냈다** — 이번엔 물리다:
    벽 골 깊이가 에라마다 |w| → ×~3.2 (기하급수) → 회복 τ ∝ |w| → 튐당 τ 비용이
    기하급수로 증가 → **튐 수 ~ O(ln τ_budget)**.  어떤 표현도 이걸 못 고친다
    (τ 를 지수적으로 재매개화하는 것 = 새 시간변수 — 그건 별개 증분).

★ f32 는 어디에 쓸 수 있는가 (E1 GPU 결정표) — 아래 측정 함수들이 표를 채운다:
    · 혼돈 그림자 지평: n* ≈ ln(1/ε)/λ 에라 — f32 ≈ 7, f64 ≈ 15.5 (Gauss 사상 실측)
    · u 판독 조건수: |du/dΣ| ~ O(u²) — f32 잡음 6e−8 → u=50 에서 δu ~ 수 e−4 (허용)
    · 구속 감시 Ω = 1−Σ²−K: 상쇄로 f32 바닥 ~1e−7 — 프로젝트 게이트(1e−9 이하) 불가
    ⇒ f32 는 "짧은 구간·u 급 판독" 전용, 구속·장기 수열은 f64 + 로그벽.
"""
from __future__ import annotations

import numpy as np

from bianchi.analysis import gauss_map as G
from bianchi.analysis import mixmaster as MX

#: 선형 f64 가 벽을 표현할 수 있는 절대 바닥 ln(최소 정규수)
LINEAR_FLOOR = float(np.log(np.finfo(np.float64).tiny))          # ≈ −708.4


# ═══════════════════════════════════════ 1. 로그-벽 대 선형-벽 (깊이)
def depth_comparison(u0=2.0 + 2.0 ** -0.5, seed=1e-3, n_bounce=12, tau_max=8000.0):
    """★★ 같은 초기자료·예산에서 두 표현의 도달 깊이와 u 품질.

    반환 dict(u_lin, u_log, w_trough_log, deepest, overlap_du,
              linear_can_represent) — deepest 는 로그판의 최저 w.
    """
    y0, args = MX.mixmaster_ic(u0, seed, "IX")
    lin = MX.bounce_sequence(y0, args, n_bounce=n_bounce, tau_max=tau_max)
    log = MX.bounce_sequence(y0, args, n_bounce=n_bounce, tau_max=tau_max,
                             walls="log")
    u_lin = [r[2] for r in lin]
    u_log = [r[2] for r in log]
    w_tr = [r[4] for r in log]                     # max_n 열 = max w (로그값)
    k = min(len(u_lin), len(u_log))
    overlap = max((abs(a - b) for a, b in zip(u_lin[:k], u_log[:k])), default=0.0)
    deepest = min(w_tr) if w_tr else 0.0
    return dict(u_lin=u_lin, u_log=u_log, w_trough_log=w_tr, deepest=deepest,
                overlap_du=overlap, linear_can_represent=bool(deepest > LINEAR_FLOOR))


def trough_growth(u0=2.0 + 2.0 ** -0.5, seed=1e-3, n_bounce=12, tau_max=8000.0):
    """★★ 벽 골의 기하급수 성장 — **남는 한계가 물리임**을 정량화.

    |w_trough| 의 인접비와 튐 간 τ 의 인접비를 함께 잰다: 둘 다 같은 비로 자라면
    "회복 τ ∝ |골 깊이|" 가 맞고, 튐 수 ~ ln(τ_budget)/ln(비) 가 따라 나온다.
    """
    y0, args = MX.mixmaster_ic(u0, seed, "IX")
    rows = MX.bounce_sequence(y0, args, n_bounce=n_bounce, tau_max=tau_max,
                              walls="log")
    w = np.array([r[4] for r in rows])
    tau = np.array([r[0] for r in rows])
    dw = np.abs(w[np.abs(w) > 20.0])               # 도입 에폭 제외 (얕은 골)
    ratios_w = list(dw[1:] / dw[:-1]) if len(dw) > 1 else []
    dtau = np.diff(tau)
    big = dtau[dtau > 50.0]
    ratios_tau = list(big[1:] / big[:-1]) if len(big) > 1 else []
    return dict(w_trough=list(w), ratios_w=ratios_w, ratios_tau=ratios_tau,
                n_bounce=len(rows), tau_last=float(tau[-1]) if len(tau) else 0.0)


# ═══════════════════════════════════════ 2. 로그-RHS 항등 (표현 무의존성)
def log_rhs_identity(n=200, seed=3, gamma=2.0):
    """★ dw/dτ = (dN/dτ)/N 항등 — 로그 RHS 가 선형 RHS 의 **정확한** 재표현인지.

    무작위 상태에서 두 RHS 를 대조한다 (Σ̇ 은 그대로, 벽은 로그미분).  이게 기계
    정밀도로 맞으면 로그 커널의 물리는 선형 커널과 같고, 다른 것은 표현뿐이다.
    """
    import jax.numpy as jnp

    from bianchi.charts import class_a as ca
    rng = np.random.default_rng(seed)
    worst = 0.0
    for _ in range(int(n)):
        sp, sm = rng.normal(size=2) * 0.5
        w = -rng.random(3) * 30.0 - 1.0
        sg = rng.choice([-1.0, 1.0], size=3)
        y = np.concatenate([[sp, sm], w])
        d_log = MX.rhs_past_log_np(y, sg, gamma)
        st = ca.StateA.of(sp, sm, *(sg * np.exp(w)))
        d_lin = MX.rhs_past(0.0, st, {"gamma": gamma})
        # Σ̇ 은 그대로 비교
        worst = max(worst, abs(float(d_lin.Sigma_p) - d_log[0]),
                    abs(float(d_lin.Sigma_m) - d_log[1]))
        # 벽: dN/dτ̃ / N = dw/dτ̃
        for i, (dn, nn) in enumerate(((d_lin.N1, st.N1), (d_lin.N2, st.N2),
                                      (d_lin.N3, st.N3))):
            worst = max(worst, abs(float(dn) / float(nn) - d_log[2 + i]))
    return worst


# ═══════════════════════════════════════ 3. f32 혼돈 그림자 지평 (E1 결정표)
def shadow_horizon(eps, n_orbit=300, n_era=40, seed=17, thresh=0.1):
    """★★ 정밀도 ε 의 궤도가 참궤도를 놓치는 에라 수 — 예측 n* ≈ ln(1/ε)/λ.

    Gauss 사상에서 잰다 (에라 사상이 곧 u 동역학의 골격이므로).  참조는 mpmath
    50자리, 시험궤도는 스텝마다 ε 정밀도로 반올림.  D1c 황금비 대조군에서 실측한
    이탈(f64, 37 **스텝** — λ_궤도 = 2lnφ)과 같은 기전의 앙상블판이다.
    """
    from mpmath import mp, mpf
    mp.dps = 50
    rng = np.random.default_rng(seed)
    lam = G.LYAPUNOV
    pred = float(np.log(1.0 / eps) / lam)
    outs = []
    for _ in range(int(n_orbit)):
        x0 = float(G.sample_gauss(rng, 1)[0])
        ref = mpf(x0)
        if eps >= 2.0 ** -30:
            test = float(np.float32(x0))
        else:
            test = x0
        div = n_era
        for k in range(int(n_era)):
            ref = 1.0 / ref
            ref = ref - int(ref)
            y = 1.0 / test
            test = y - np.floor(y)
            if eps >= 2.0 ** -30:
                test = float(np.float32(test))
            if abs(float(ref) - test) > thresh:
                div = k + 1
                break
        outs.append(div)
    outs = np.asarray(outs, float)
    return dict(mean=float(outs.mean()), median=float(np.median(outs)),
                predicted=pred, eps=float(eps),
                censored=float((outs >= n_era).mean()))


# ═══════════════════════════════════════ 4. 조건수 (무엇이 f32 를 견디는가)
def u_conditioning(us=(2.0, 5.0, 20.0, 50.0), h=1e-7):
    """★ u 판독의 조건수 |du/dΣ| — Σ 를 f32 로 낮췄을 때의 u 잡음 추정.

    반환 [(u, |du/dΣ|, f32 잡음 추정 = 6e−8·|du/dΣ|)].
    """
    from bianchi.analysis import kasner as K
    out = []
    for u in us:
        p = K.u_to_exponents(u)
        sp, sm = K.sigma_from_exponents(p)
        g = 0.0
        for dsp, dsm in ((h, 0.0), (0.0, h)):
            g = max(g, abs(K.kasner_u(sp + dsp, sm + dsm) - K.kasner_u(sp, sm)) / h)
        out.append((float(u), float(g), float(6e-8 * g)))
    return out


def omega_cancellation_floor(n=200, seed=5):
    """★★ 구속 감시량 Ω = 1 − Σ² − K 의 f32 상쇄 바닥 — **f32 로 불가능한 것**.

    Kasner 원 근방(참 Ω ~ 1e−12)에서 f32 로 계산한 Ω 의 잡음을 잰다.
    프로젝트의 구속 게이트(1e−9 급)와 비교하면 f32 배제가 산술로 확정된다.
    """
    rng = np.random.default_rng(seed)
    worst = 0.0
    for _ in range(int(n)):
        th = rng.random() * 2.0 * np.pi
        n3 = rng.random(3) * 1e-6
        k = float(1.0 / 12.0 * (n3 @ n3 - 2.0 * (n3[0] * n3[1] + n3[1] * n3[2]
                                                 + n3[2] * n3[0])))
        r = np.sqrt(1.0 - k)
        sp, sm = r * np.cos(th), r * np.sin(th)          # 참 Ω = 0 (구성상)
        om64 = 1.0 - (sp * sp + sm * sm) - k
        f = np.float32
        om32 = float(f(1.0) - (f(sp) * f(sp) + f(sm) * f(sm)) - f(k))
        worst = max(worst, abs(om32 - om64))
    return worst

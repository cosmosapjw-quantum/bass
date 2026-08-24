"""
I2b · IX 다중튐 × 물질: **절단 계층 vs 정확 격자의 결정실험** (74차).

측정 사슬 (전부 시험 게이트):
  · 진공 극한: 결합기계의 u-수열 ≡ BKL 사상 (오차 1.1e−4) — D1/R4 회귀.
  · 수동 추적자: dlnΩ/dτ 가 Ω₀ 에 무관 (1e−10..1e−6 에서 −0.2616/−0.2604).
  · ★★ 결정실험 (74차의 핵심):
        정확 격자 (G1, 시험장·양수성 구조보장)   dlnΩ/dτ = **+0.234**
        절단 계층 (l_max=3)                      dlnΩ/dτ = **−0.258**  ← 부호 반대
        완전유체 (γ=4/3) 예측                     dlnΩ/dτ = +1.906
    ⇒ (i) **BKL 무시는 성립**한다 — 무충돌 물질도 특이점 방향으로 Ω 감쇠.
       (ii) 그러나 감쇠율이 완전유체보다 **8배 느리다** (0.234 vs 1.906) —
            'ρ∝V^{−4/3}' 논증은 무충돌 종에 그대로 쓰면 안 된다.
       (iii) **PSTF 절단 계층은 이 영역에서 정성적으로 틀린다** (부호 반전;
            l_max=4 에서는 Ω<0 로 양수성 붕괴) — I2 의 절단-민감 발견이
            여기서 실제 오답으로 현실화.  G-티어 격자가 필수임의 증명.
  · 반증 기록: 절단 계층에 BGK-감쇠 (l≥2) 를 넣어 유체극한을 흉내내려는
    시도는 Ω<0 로 **발산** — 정칙화는 격자(양수성 보존)에서 해야 한다.

사용:  python -m audit.i2b_mixmaster_statistics
"""
from __future__ import annotations

import numpy as np

from bianchi.analysis import kasner as K
from bianchi.matter import coupled_tilted as CT
from bianchi.matter import grid_boltzmann as GB


def mixmaster_ic(u0=3.7, Om0=1e-12, seed=1e-3, l_max=3):
    """Kasner 원 위 (u0) + 씨앗 N + Gauss 로 Ω₀ 수용."""
    p = K.u_to_exponents(u0)
    Sp, Sm = K.sigma_from_exponents(p)
    n = np.array([seed] * 3)
    Kc = (n @ n - 2*(n[0]*n[1] + n[1]*n[2] + n[2]*n[0])) / 12.0
    r = np.sqrt(max(1.0 - Kc - Om0, 0.0) / (Sp*Sp + Sm*Sm))
    Jc = {(l, 0): np.zeros(2*l + 1) for l in range(l_max + 1)}
    Jc[(0, 0)] = np.array([3.0 * Om0])
    return CT.pack(np.array([Sp*r, Sm*r, 0, 0, 0]), n, 0.0,
                   np.zeros(0), np.zeros((0, 3)), Jc, l_max)


def collapse(u0=3.7, Om0=1e-12, l_max=3, tau=-25.0, ns=25000, nu_bgk=0.0):
    y = mixmaster_ic(u0, Om0, l_max=l_max)
    return CT.rk4_evolve_rust(y, np.zeros(0), l_max, tau, ns, keep=True,
                              nu_bgk=nu_bgk)[1]


def epoch_indices(traj, win=60, merge=80):
    """Kasner 에폭 = max|N_i| 의 국소최소 (튐 사이의 가장 Kasner 다운 순간)."""
    mx = np.abs(traj[:, 5:8]).max(axis=1)
    hits = [i for i in range(win, len(mx) - win)
            if mx[i] <= mx[i-win:i+win+1].min()]
    grp = []
    for i in hits:
        if grp and i - grp[-1][-1] <= merge:
            grp[-1].append(i)
        else:
            grp.append([i])
    return [g[len(g)//2] for g in grp]


def u_sequence_coupled(traj):
    return [K.kasner_u(traj[i, 0], traj[i, 1]) for i in epoch_indices(traj)]


def omega_exponent(traj, tau=-25.0, t_cut=-5.0):
    """dlnΩ/dτ 적합 (벽 초기 과도 제외)."""
    t = np.linspace(0.0, tau, traj.shape[0])
    Om = traj[:, 9] / (3.0 * np.exp(2.0 * traj[:, 8]))
    m = t < t_cut
    return float(np.polyfit(t[m], np.log(np.abs(Om[m])), 1)[0]), Om


def grid_exponent(traj, tau=-25.0, stride=250, t_cut=-5.0):
    """★ 정확 격자 (시험장): Σ(τ) → ln a_i(τ) → ρ_grid(τ) → Ω_grid 지수.
    자유흐름이 **정확**하고 f ≥ 0 이 구조보장 (G1) — 절단·양수성 오류 없음."""
    ns = traj.shape[0] - 1
    t = np.linspace(0.0, tau, ns + 1)
    h = t[1] - t[0]
    S5 = traj[:, :5]
    sig = np.stack([-2*S5[:, 0], S5[:, 0] + np.sqrt(3)*S5[:, 1],
                    S5[:, 0] - np.sqrt(3)*S5[:, 1]], axis=1)
    lna = np.cumsum((1.0 + sig) * h, axis=0) - (1.0 + sig[0]) * h
    F = GB.initial_grid()
    sub = np.arange(0, ns + 1, stride)
    rho = np.array([GB.moments_from_grid(F, np.exp(lna[i]), 0, 0) for i in sub])
    Om = rho / (3.0 * np.exp(2.0 * traj[sub, 8]))
    m = t[sub] < t_cut
    return float(np.polyfit(t[sub][m], np.log(Om[m]), 1)[0]), Om, t[sub]


def perfect_fluid_exponent(traj, tau=-25.0, stride=250, t_cut=-5.0):
    """대조: 완전유체 γ=4/3 이면 dlnΩ/dτ = 2q−2 (q=2Σ² 진공극한)."""
    ns = traj.shape[0] - 1
    t = np.linspace(0.0, tau, ns + 1)[::stride]
    q = 2.0 * (traj[::stride, :5] ** 2).sum(axis=1)
    return float(np.mean((2.0 * q - 2.0)[t < t_cut]))


if __name__ == "__main__":
    tr = collapse()
    print("u-수열:", np.round(u_sequence_coupled(tr), 4))
    sg, _, _ = grid_exponent(tr)
    sh, _ = omega_exponent(tr)
    print(f"격자 {sg:+.4f} / 계층 {sh:+.4f} / 유체 {perfect_fluid_exponent(tr):+.4f}")

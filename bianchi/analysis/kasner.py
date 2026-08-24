"""
D1 · **Kasner 튐(bounce) 사건 검출** — BKL 사상을 인용하지 않고 **측정**한다.

Mixmaster (Bianchi VIII/IX) 궤적은 Kasner 원 (Ω = 0, N = 0, Σ₊²+Σ₋² = 1) 근처에
오래 머물다가 곡률 벽 하나가 자라며 **튄다**.  튐마다 Kasner 지수가 갈아치워지고,
그 이산 사상이 BKL 사상이다.  여기서 하는 것:

  1. 튐을 **정확한 근**으로 잡는다 (`diffrax` 이벤트 + Newton).  출력 격자를 훑어
     극대점을 고르는 방식은 스텝 크기에 오염된다.
  2. Kasner 매개변수 u 를 상태에서 뽑는다 (p_i = (1+Σ_i)/3, u = p_max/p_mid).
  3. ★★ **Bianchi II 를 오라클로** 쓴다: 벽이 하나뿐이라 튐도 정확히 한 번이고,
     들어온 u 와 나간 u 의 관계가 BKL 사상의 **기본 벽돌**이다.  그 관계를
     여러 u 에서 재서 `u ↦ u−1 (u≥2) / 1/(u−1) (1≤u<2)` 와 대조한다.
  4. Bianchi IX 에서 튐을 **연속으로** 잡아 u 수열이 그 사상을 따르는지 본다.

★ 규약 (프로젝트 chart `class_a`, Wainwright-Hsu):
      Σ = diag(−2Σ₊, Σ₊+√3Σ₋, Σ₊−√3Σ₋),   p_i = (1 + Σ_i)/3
      Kasner 원에서 q = 2 이고  d ln N₁/dτ = q − 4Σ₊ = 2 − 4Σ₊
  ⇒ N₁ 벽은 **Σ₊ < 1/2 에서 자란다**.  이것이 튐 사건의 정의다.
"""
from __future__ import annotations

import jax
import jax.numpy as jnp
import numpy as np

from bianchi import integrate as itg
from bianchi.charts import class_a as ca
from bianchi.conventions import SQRT3


# ═══════════════════════════════════════ 1. Kasner 좌표
def sigma_diag(Sp, Sm):
    """Σ_i = (−2Σ₊, Σ₊+√3Σ₋, Σ₊−√3Σ₋)  (chart 규약 `charts.general.from_class_a`)."""
    Sp, Sm = float(Sp), float(Sm)
    return np.array([-2.0 * Sp, Sp + SQRT3 * Sm, Sp - SQRT3 * Sm])


def kasner_exponents(Sp, Sm):
    """p_i = (1 + Σ_i)/3.  Kasner 원 위에서 Σp = Σp² = 1 이 **자동**이다."""
    return (1.0 + sigma_diag(Sp, Sm)) / 3.0


def kasner_u(Sp, Sm):
    """★ Kasner 매개변수 u = p_max / p_mid  (표준 매개화의 역).

        p = (−u, 1+u, u(1+u)) / (1+u+u²)   ⇒   p₃/p₂ = u
    """
    p = np.sort(kasner_exponents(Sp, Sm))
    return float(p[2] / p[1]) if abs(p[1]) > 1e-300 else np.inf


def u_to_exponents(u):
    """u → 정렬된 (p₁ ≤ p₂ ≤ p₃)."""
    u = float(u)
    s = 1.0 + u + u * u
    return np.array([-u / s, (1.0 + u) / s, u * (1.0 + u) / s])


def sigma_from_exponents(p):
    """p_i → (Σ₊, Σ₋)  (Σ_i = 3p_i − 1 의 역)."""
    S = 3.0 * np.asarray(p, float) - 1.0
    return -S[0] / 2.0, (S[1] - S[2]) / (2.0 * SQRT3)


def kasner_residual(Sp, Sm):
    """★ 자기검증 — Kasner 원 위인가 (Σ₊²+Σ₋² = 1, Σp = Σp² = 1)."""
    p = kasner_exponents(Sp, Sm)
    return dict(circle=abs(Sp ** 2 + Sm ** 2 - 1.0),
                sum_p=abs(float(p.sum()) - 1.0),
                sum_p2=abs(float((p ** 2).sum()) - 1.0))


def bkl_map(u):
    """★ BKL(Gauss) 사상 — **인용식**.  측정과 대조하기 위해서만 쓴다.

        u ↦ u − 1        (u ≥ 2)
        u ↦ 1/(u − 1)    (1 ≤ u < 2)
    """
    u = float(u)
    return u - 1.0 if u >= 2.0 else 1.0 / (u - 1.0)


# ═══════════════════════════════════════ 2. 벽과 튐 사건
def wall_rates(y, gamma=0.0):
    """d ln N_i/dτ = (q − 4Σ₊, q + 2Σ₊ ± 2√3Σ₋)  — 벽이 자라는지 재는 양."""
    a = ca.aux(y, gamma)
    q, Sp, Sm = float(a["q"]), float(y.Sigma_p), float(y.Sigma_m)
    return np.array([q - 4.0 * Sp,
                     q + 2.0 * Sp + 2.0 * SQRT3 * Sm,
                     q + 2.0 * Sp - 2.0 * SQRT3 * Sm])


def bounce_event(wall=0, gamma=0.0):
    """★★ 튐 = **벽의 성장률이 0 을 아래로 지나는 순간** (N_i 가 극대).

    `d ln N_i/dτ = 0` 을 Newton 으로 정확히 푼다 — 출력 격자를 훑지 않는다.
    `direction=False` 는 양 → 음 교차만 잡는다 (자라던 벽이 꺾이는 지점).
    """
    def cond(t, y, args, **kw):
        a = ca.aux(y, args["gamma"])
        q, Sp, Sm = a["q"], y.Sigma_p, y.Sigma_m
        rates = (q - 4.0 * Sp,
                 q + 2.0 * Sp + 2.0 * SQRT3 * Sm,
                 q + 2.0 * Sp - 2.0 * SQRT3 * Sm)
        return rates[wall]
    return itg.float_event(cond, direction=False)


def _project_to_vacuum(Sp, Sm, N1, N2=0.0, N3=0.0):
    """★ Ω = 1 − Σ² − K = 0 이 되도록 (Σ₊,Σ₋) 를 방사 방향으로 재척도한다.

    벽을 켜면 곡률 K 가 생기므로 Kasner 원(Σ²=1)은 더 이상 진공이 아니다.
    """
    K = float(ca.curvature_K(jnp.asarray(N1), jnp.asarray(N2), jnp.asarray(N3)))
    r2 = Sp ** 2 + Sm ** 2
    if r2 <= 0.0:
        return Sp, Sm
    f = float(np.sqrt(max(1.0 - K, 0.0) / r2))
    return Sp * f, Sm * f


def _state(v):
    return ca.StateA.from_array(jnp.asarray(np.asarray(v, float)))


def _last(sol):
    return jax.tree.map(lambda x: x[-1] if jnp.ndim(x) else x, sol.ys)


# ═══════════════════════════════════════ 3. ★★ Bianchi II — 하나의 튐이 오라클
#
# ★ γ = 2 를 **기본값**으로 쓴다.  진공(Ω = 0)에서 물리는 γ 와 무관하지만, 차트가
#   Ω 를 Gauss 로 소거해 두었으므로 Ω = 0 **면의 수치 안정성**은 γ 에 달렸다:
#         Ω′ = [2q − (3γ − 2)]Ω,   Kasner 원에서 q = 2
#   γ=0 이면 지수 +6 으로 자라 τ≈6 에서 Ω 오차가 1e−17 → 1e−1 이 되고 궤적이 터진다
#   (실제로 겪었다).  γ=2 면 2q−4 = 0 으로 **중립**이다.  D2 가 잰 구속 증폭이
#   여기서 그대로 나타난다.
def _integrate_until_wall_decays(y0, args, wall_tol=1e-9, chunk=8.0, max_tau=64.0,
                                 rtol=1e-12, atol=1e-14):
    """벽이 `wall_tol` 아래로 죽을 때까지 이어 적분한다 (나간 Kasner 점을 읽으려고).

    ★ 고정 τ 로 끊으면 벽이 덜 죽은 채 읽혀 u_out 이 1e−3 수준으로 틀린다
      (측정: N₁_end = 2.7e−02 일 때 u_out 4.70107 vs 참값 4.7).
    """
    cfg = itg.SolverConfig(rtol=rtol, atol=atol, max_steps=200000)
    y, t = y0, 0.0
    while t < max_tau:
        sol = itg.solve_jit(ca.rhs, y, t, t + chunk, args, cfg=cfg)
        y, t = _last(sol), t + chunk
        if float(jnp.max(jnp.abs(jnp.stack([y.N1, y.N2, y.N3])))) < wall_tol:
            break
    return y, t


def bianchi_II_transition(u_in, perm=(2, 0, 1), seed=1e-6, gamma=2.0,
                          rtol=1e-12, atol=1e-14, tau_max=40.0):
    """★★ Kasner 원에서 출발해 N₁ 벽 하나를 통과시키고 **나간 u** 를 잰다.

    벽이 하나뿐(Bianchi II)이라 튐이 정확히 한 번이고, 그 사상이 Kasner 사상의
    기본 벽돌이다.  `perm` 은 정렬된 (p₁≤p₂≤p₃) 를 축에 배정하는 순열 — **어느 축이
    벽을 갖느냐가 사상의 가지를 정한다** (아래 `branch_table` 참조).

    ★ τ 를 **키우며** 적분하므로 이것은 특이점에서 **멀어지는** 방향이다.
      그래서 측정되는 것은 BKL 사상 자체가 아니라 그 **역**이다:  bkl(u_out) = u_in.
    """
    p = u_to_exponents(u_in)
    Sp, Sm = sigma_from_exponents(p[list(perm)])
    if not Sp < 0.5 - 1e-12:
        return None                          # N₁ 벽이 자라지 않는 배정
    Sp, Sm = _project_to_vacuum(Sp, Sm, seed)
    y0 = ca.StateA.of(Sp, Sm, seed, 0.0, 0.0)
    args = {"gamma": float(gamma)}
    cfg = itg.SolverConfig(rtol=rtol, atol=atol, max_steps=200000)
    sol = itg.solve_jit(ca.rhs, y0, 0.0, tau_max, args,
                        event=bounce_event(0), cfg=cfg)
    fired = itg.status(sol)["event_fired"]
    yb, tau_b = _last(sol), float(sol.ts[-1])
    yf, _ = _integrate_until_wall_decays(yb, args, rtol=rtol, atol=atol)
    Spf, Smf = float(yf.Sigma_p), float(yf.Sigma_m)
    return dict(u_in=float(u_in), u_out=kasner_u(Spf, Smf),
                inverse=bkl_map(kasner_u(Spf, Smf)),
                tau_bounce=tau_b, N1_peak=float(yb.N1), N1_end=float(yf.N1),
                circle_out=abs(Spf ** 2 + Smf ** 2 - 1.0),
                omega_out=float(ca.aux(yf, float(gamma))["Omega"]),
                perm=tuple(perm), bounced=bool(fired))


def transition_vs_bkl(us=(1.3, 1.7, 2.4, 3.1, 4.6, 7.2), perm=(2, 0, 1), **kw):
    """★★ **측정 vs 인용** — bkl(u_out) 이 u_in 을 되돌려 주는가.

    반환 [(u_in, u_out, bkl(u_out), |bkl(u_out) − u_in|, 원 잔차)].
    """
    rows = []
    for u in us:
        r = bianchi_II_transition(u, perm=perm, **kw)
        rows.append((float(u), r["u_out"], r["inverse"],
                     abs(r["inverse"] - float(u)), r["circle_out"]))
    return rows


def branch_table(u_in=3.7, **kw):
    """★★ 두 가지 축 배정이 BKL 사상의 **두 가지**를 각각 되돌린다.

    측정 (u_in = 3.7):
        배정 (1,0,2) → u_out = u_in + 1        (bkl 의 u ≥ 2 가지의 역)
        배정 (2,0,1) → u_out = 1 + 1/u_in      (bkl 의 1<u<2 가지의 역)
    두 경우 모두 `bkl(u_out) = u_in`.
    """
    from itertools import permutations
    out = []
    for perm in permutations(range(3)):
        r = bianchi_II_transition(u_in, perm=perm, **kw)
        if r is None:
            continue
        out.append((perm, r["u_out"], r["inverse"], abs(r["inverse"] - u_in)))
    return out


def vacuum_surface_amplification(u_in=3.7, gammas=(0.0, 4.0 / 3.0, 2.0),
                                 tau=12.0, seed=1e-6):
    """★★ **D1 ↔ D2 연결** — Ω = 0 면의 수치 안정성이 γ 에 달렸다.

        Ω′ = [2q − (3γ − 2)]Ω,   Kasner 원에서 q = 2  ⇒  지수 = 6 − 3γ

    γ=0 이면 +6 (터진다), γ=4/3 이면 +2, γ=2 면 **0** (중립).  측정으로 확인한다.
    반환 [(γ, 예측 지수, |Ω(τ)|, 터졌는가)].
    """
    p = u_to_exponents(u_in)
    Sp, Sm = sigma_from_exponents(p[[2, 0, 1]])
    Sp, Sm = _project_to_vacuum(Sp, Sm, seed)
    y0 = ca.StateA.of(Sp, Sm, seed, 0.0, 0.0)
    cfg = itg.SolverConfig(rtol=1e-12, atol=1e-14, max_steps=200000)
    rows = []
    for g in gammas:
        sol = itg.solve_jit(ca.rhs, y0, 0.0, tau, {"gamma": float(g)}, cfg=cfg)
        yf = _last(sol)
        om = float(ca.aux(yf, float(g))["Omega"])
        rows.append((float(g), 6.0 - 3.0 * float(g), abs(om),
                     not np.isfinite(om) or abs(om) > 1e-3))
    return rows


# ═══════════════════════════════════════ 4. 이벤트 vs 격자 훑기
def event_beats_grid_scan(u_in=3.7, perm=(2, 0, 1), seed=1e-6, gamma=2.0,
                          ns=(40, 80, 160, 320)):
    """★★ **이벤트가 격자 훑기보다 낫다** — 같은 튐 시각을 두 방법으로 잰다.

    격자에서 argmax N₁ 을 고르면 오차가 Δτ 에 걸려 **1차로만** 준다.
    """
    r = bianchi_II_transition(u_in, perm=perm, seed=seed, gamma=gamma)
    exact = r["tau_bounce"]
    p = u_to_exponents(u_in)
    Sp, Sm = sigma_from_exponents(p[list(perm)])
    Sp, Sm = _project_to_vacuum(Sp, Sm, seed)
    y0 = ca.StateA.of(Sp, Sm, seed, 0.0, 0.0)
    cfg = itg.SolverConfig(rtol=1e-12, atol=1e-14, max_steps=200000)
    rows = []
    for n in ns:
        ts = jnp.linspace(0.0, 2.0 * exact, int(n))
        sol = itg.solve_jit(ca.rhs, y0, 0.0, float(ts[-1]), {"gamma": gamma},
                            ts=ts, cfg=cfg)
        j = int(np.argmax(np.asarray(sol.ys.N1)))
        rows.append((int(n), float(ts[1] - ts[0]), abs(float(ts[j]) - exact)))
    return dict(exact=exact, rows=rows)


# ═══════════════════════════════════════ 5. 대조군
def bianchi_I_has_no_bounce(u0=3.1, tau_max=40.0, gamma=2.0):
    """★ 대조군 — 벽이 없으면(N = 0) 튐도 없다 (이벤트가 안 터져야 한다)."""
    Sp, Sm = sigma_from_exponents(u_to_exponents(u0))
    y0 = ca.StateA.of(Sp, Sm, 0.0, 0.0, 0.0)
    cfg = itg.SolverConfig(rtol=1e-12, atol=1e-14)
    sol = itg.solve_jit(ca.rhs, y0, 0.0, tau_max, {"gamma": gamma},
                        event=bounce_event(0), cfg=cfg)
    return itg.status(sol)["event_fired"]


def non_growing_wall_never_bounces(u0=3.7, seed=1e-6, gamma=2.0, tau_max=40.0):
    """★ 대조군 — Σ₊ > 1/2 로 출발하면 N₁ 은 처음부터 죽으므로 튐이 없다."""
    p = u_to_exponents(u0)
    Sp, Sm = sigma_from_exponents(p)            # 항등 배정 → Σ₊ > 1/2
    assert Sp > 0.5
    Sp, Sm = _project_to_vacuum(Sp, Sm, seed)
    y0 = ca.StateA.of(Sp, Sm, seed, 0.0, 0.0)
    cfg = itg.SolverConfig(rtol=1e-12, atol=1e-14)
    sol = itg.solve_jit(ca.rhs, y0, 0.0, tau_max, {"gamma": gamma},
                        event=bounce_event(0), cfg=cfg)
    return itg.status(sol)["event_fired"]


def report():
    print("=" * 74)
    print("D1 · Kasner 튐 사건 검출 — Kasner 사상을 측정한다")
    print("=" * 74)
    print("\n[1] ★★ Bianchi II 사상 (τ 증가 = 특이점에서 멀어지는 방향)")
    print("      u_in     u_out(측정)   bkl(u_out)   |차|      원 잔차")
    for u, uo, inv, d, c in transition_vs_bkl():
        print(f"    {u:7.3f}   {uo:11.7f}  {inv:11.7f}  {d:.2e}  {c:.1e}")
    print("\n[2] ★★ 축 배정이 사상의 가지를 정한다 (u_in = 3.7)")
    for perm, uo, inv, d in branch_table():
        print(f"    배정 {perm}  u_out={uo:.8f}   bkl(u_out)={inv:.8f}  |차| {d:.1e}")
    print("\n[3] ★★ 진공면 Ω = 0 의 수치 안정성 (D2 의 구속 증폭)")
    for g, e, om, blew in vacuum_surface_amplification():
        print(f"    γ={g:.3f}  예측 지수 {e:+.1f}   |Ω(τ=12)| = {om:.2e}"
              f"   {'터짐' if blew else '안정'}")
    print("\n[4] ★★ 이벤트 vs 격자 훑기 (튐 시각 오차)")
    e = event_beats_grid_scan()
    print(f"    이벤트(Newton) τ_bounce = {e['exact']:.10f}")
    for n, dt, err in e["rows"]:
        print(f"    격자 {n:4d}점 (Δτ={dt:.4f})  오차 {err:.3e}")
    print(f"\n[5] 대조군")
    print(f"    Bianchi I (벽 없음) 튐 발생: {bianchi_I_has_no_bounce()}")
    print(f"    Σ₊ > 1/2 (벽이 죽는 쪽) 튐 발생: {non_growing_wall_never_bounces()}")


if __name__ == "__main__":
    report()

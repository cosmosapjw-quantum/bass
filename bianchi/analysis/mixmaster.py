"""
D1b · **Mixmaster 연속 튐** — Bianchi IX/VIII 를 특이점 쪽으로 굴리며 u 수열을 잰다.

D1 은 Bianchi II 로 **한 번의 튐**을 오라클로 삼아 Kasner 사상을 측정했다.  여기서는
벽이 셋인 IX/VIII 에서 **연속으로** 튀는 것을 잡고, u 수열이 BKL 사상을 따르는지 본다.

★ 방향이 D1 과 반대다.  Mixmaster 의 튐은 **특이점 쪽**(τ 감소)에서 일어난다.
  부호 실수를 피하려고 τ̃ = −τ 로 **뒤집은 RHS** 를 쓴다 — 그러면 "성장률이 0 을
  아래로 지나는 순간" 이라는 D1 의 사건 정의를 그대로 재사용할 수 있다:

      d ln N_i/dτ̃ = −(q − 4Σ₊) 등,   Kasner 원에서 q = 2
  ⇒ 특이점 쪽으로는 **Σ₊ > 1/2 인 벽**이 자란다 (D1 의 정반대).  그래서 D1 이 잰
    사상이 BKL 의 **역**이었던 것과 앞뒤가 맞는다.

★ u 는 **튐 지점에서 읽으면 안 된다** — 그 순간은 벽이 최대라 Kasner 원에서 멀다.
  튐 사이 구간에서 max_i N_i 가 최소인 곳(가장 Kasner 다운 순간)에서 읽는다.

★ γ = 2 (D1 §3): 진공면 Ω=0 의 수치 안정성이 γ 에 달렸고 (지수 6−3γ), γ=2 가 중립.
"""
from __future__ import annotations

import numpy as np

from bianchi import integrate as itg
from bianchi.analysis import kasner as K
from bianchi.backend_policy import (
    BackendPolicy,
    ROUTE_CAPABILITIES,
    load_native,
    select_backend,
)
from bianchi.charts import class_a as ca
from bianchi.conventions import SQRT3
from bianchi.optional_dependencies import require_jax_x64

jax, jnp = require_jax_x64(feature=__name__)


def rust_available():
    """진단용 native capability; 실행 경로 선택 권한은 없다."""
    load = load_native()
    capability = ROUTE_CAPABILITIES["mixmaster.bounce_sequence"]
    return bool(
        load.available
        and load.module is not None
        and all(hasattr(load.module, symbol) for symbol in capability.required_symbols)
    )


def rhs_past(t, y, args):
    """τ̃ = −τ 로 뒤집은 RHS — **특이점 쪽**으로 굴린다 (모듈 수준: jit 캐시 안정)."""
    return jax.tree.map(lambda x: -x, ca.rhs(t, y, args))


def past_wall_rates(y, gamma=2.0):
    """d ln N_i/dτ̃ = −(d ln N_i/dτ) — 특이점 쪽 성장률."""
    return -K.wall_rates(y, gamma)


def past_bounce_event(wall=0):
    """★★ 특이점 쪽 튐 — τ̃ 기준 성장률이 0 을 **아래로** 지나는 순간 (N_i 극대)."""
    def cond(t, y, args, **kw):
        a = ca.aux(y, args["gamma"])
        q, Sp, Sm = a["q"], y.Sigma_p, y.Sigma_m
        rates = (q - 4.0 * Sp,
                 q + 2.0 * Sp + 2.0 * SQRT3 * Sm,
                 q + 2.0 * Sp - 2.0 * SQRT3 * Sm)
        return -rates[wall]
    return itg.float_event(cond, direction=False)


def rhs_past_log_np(y, signs, gamma=2.0):
    """D3 · 로그-벽 RHS (τ̃ 방향, numpy) — Rust `f_past_log` 의 Python 오라클.

    상태 y = (Σ₊, Σ₋, w₁, w₂, w₃), N_i = s_i·e^{w_i}.  선형 RHS 와의 항등
    dw/dτ = (dN/dτ)/N 은 시험이 확인한다 (표현을 바꿔도 물리는 같아야 한다).
    """
    y = np.asarray(y, float)
    sp, sm = y[0], y[1]
    n = np.asarray(signs, float) * np.exp(y[2:5])
    st = ca.StateA.of(sp, sm, *n)
    a = ca.aux(st, gamma)
    q = float(a["q"])
    dsp = -(2.0 - q) * sp - float(ca.S_plus(*n))
    dsm = -(2.0 - q) * sm - float(ca.S_minus(*n))
    rates = np.array([q - 4.0 * sp, q + 2.0 * sp + 2.0 * SQRT3 * sm,
                      q + 2.0 * sp - 2.0 * SQRT3 * sm])
    return -np.concatenate([[dsp, dsm], rates])


def mixmaster_ic(u0=3.7, seed=1e-6, kind="IX", perm=(0, 1, 2)):
    """★ Kasner 원 근처의 IX(n=+,+,+) / VIII(n=+,+,−) 초기자료 — **진공면 위**로.

    ★ D1 의 반증 기록 (a): 벽을 켜면 Σ²=1 은 더 이상 Ω=0 이 아니다.
    """
    p = K.u_to_exponents(u0)
    Sp, Sm = K.sigma_from_exponents(p[list(perm)])
    n = np.array([seed, seed, seed if kind == "IX" else -seed], float)
    Sp, Sm = K._project_to_vacuum(Sp, Sm, n[0], n[1], n[2])
    return ca.StateA.of(Sp, Sm, *n), {"gamma": 2.0}


def _last(sol):
    return jax.tree.map(lambda x: x[-1] if jnp.ndim(x) else x, sol.ys)


def _pick(sol, j):
    return ca.StateA(sol.ys.Sigma_p[j], sol.ys.Sigma_m[j], sol.ys.N1[j],
                     sol.ys.N2[j], sol.ys.N3[j])


# ═══════════════════════════════════════ ★★ 연속 튐 검출
def bounce_sequence(y0, args, n_bounce=8, span=40.0, push=1e-2, n_probe=41,
                    rtol=1e-12, atol=1e-14, backend=None, tau_max=None,
                    walls="linear"):
    """★★ 튐을 **연속으로** 잡는다 — 세 벽에 각각 이벤트를 걸고 **가장 이른 근**.

    각 튐 사이에서는 격자를 훑어 max_i N_i 가 최소인 곳(가장 Kasner 다운 순간)의
    u 를 기록한다 — 튐 지점의 u 는 Kasner 원에서 멀어 의미가 없다.

    `push` 는 이벤트 직후 같은 근을 다시 잡지 않도록 τ̃ 를 조금 넘기는 양이다.
    반환 [(τ̃_bounce, 벽, u_epoch, τ̃_epoch, maxN_epoch, Ω)] .
    """
    policy = BackendPolicy.PYTHON_ORACLE if backend == "python" else backend
    selected = select_backend("mixmaster.bounce_sequence", policy=policy)
    if selected.uses_rust:
        rc = selected.native_module
        assert rc is not None
        # ★ R4: 세 벽을 **한 번의 적분**으로 감시한다 (되감기·중복 적분 없음).
        v = np.array([float(y0.Sigma_p), float(y0.Sigma_m), float(y0.N1),
                      float(y0.N2), float(y0.N3)], float)
        tm = float(span * (n_bounce + 2)) if tau_max is None else float(tau_max)
        if walls == "log":
            # ★ D3: 벽을 w = ln|N| 로 — 언더플로 없음.  max_n 열은 **max w** (로그값).
            sg = np.sign(v[2:5])
            sg[sg == 0.0] = 1.0
            ylog = np.array([v[0], v[1], *np.log(np.maximum(np.abs(v[2:5]),
                                                            1e-300))])
            tau, w, u, te, mx, om = rc.mx_bounce_sequence_log(
                ylog, sg, float(args["gamma"]), int(n_bounce), tm, float(rtol),
                float(atol), 1e-3)
        else:
            tau, w, u, te, mx, om = rc.mx_bounce_sequence(
                v, float(args["gamma"]), int(n_bounce), tm, float(rtol),
                float(atol), 1e-3)
        return [(float(tau[i]), int(w[i]), float(u[i]), float(te[i]),
                 float(mx[i]), float(om[i])) for i in range(len(tau))]
    if walls == "log":
        raise NotImplementedError("walls='log' 는 Rust 커널 전용 (D3)")
    cfg = itg.SolverConfig(rtol=rtol, atol=atol, max_steps=200000)
    y, t = y0, 0.0
    rows = []
    for _ in range(int(n_bounce)):
        best = None
        for w in range(3):
            sol = itg.solve_jit(rhs_past, y, t, t + span, args,
                                event=past_bounce_event(w), cfg=cfg)
            if not itg.status(sol)["event_fired"]:
                continue
            tb = float(sol.ts[-1])
            if tb <= t + 1e-12:
                continue
            if best is None or tb < best[0]:
                best = (tb, _last(sol), w)
        if best is None:
            break
        tb, yb, w = best
        # 이 튐 이전 구간에서 가장 Kasner 다운 순간의 u
        ts = jnp.linspace(t, tb, int(n_probe))
        prb = itg.solve_jit(rhs_past, y, t, tb, args, ts=ts, cfg=cfg)
        mx = np.max(np.abs(np.stack([np.asarray(prb.ys.N1), np.asarray(prb.ys.N2),
                                     np.asarray(prb.ys.N3)])), axis=0)
        j = int(np.argmin(mx))
        ye = _pick(prb, j)
        rows.append((tb, w, K.kasner_u(ye.Sigma_p, ye.Sigma_m), float(ts[j]),
                     float(mx[j]), float(ca.aux(ye, args["gamma"])["Omega"])))
        sol = itg.solve_jit(rhs_past, yb, tb, tb + push, args, cfg=cfg)
        y, t = _last(sol), tb + push
    return rows


_SEQ_CACHE: dict = {}


def u_sequence(u0=3.7, n_bounce=5, seed=1e-3, kind="IX", **kw):
    """★★ u 수열 + BKL 예측 + 오차.  (같은 인자는 캐시 — 시험이 여러 번 부른다.)"""
    key = (float(u0), int(n_bounce), float(seed), kind,
           tuple(sorted((k, str(v)) for k, v in kw.items())))
    if key in _SEQ_CACHE:
        return _SEQ_CACHE[key]
    y0, args = mixmaster_ic(u0, seed, kind)
    rows = bounce_sequence(y0, args, n_bounce=n_bounce, **kw)
    us = [r[2] for r in rows]
    pred = [K.bkl_map(u) for u in us[:-1]]
    err = [abs(a - b) for a, b in zip(us[1:], pred)]
    out = dict(rows=rows, u=us, pred=pred, err=err)
    _SEQ_CACHE[key] = out
    return out


def era_structure(u0=5.4, n_bounce=5, **kw):
    """★ **에라 구조** — 한 에라 안에서는 u 가 1 씩 줄고, u<2 가 되면 1/(u−1) 로 재주입.

    반환 [(u, 다음 u, '감소' | '재주입')].
    """
    r = u_sequence(u0=u0, n_bounce=n_bounce, **kw)
    out = []
    for a, b in zip(r["u"], r["u"][1:]):
        out.append((a, b, "감소" if a >= 2.0 else "재주입"))
    return out


def resolvable_bounces(u0=3.7, n_bounce=5, tol=1e-3, **kw):
    """★★ **몇 번을 분해할 수 있는가** — 그리고 무엇이 한계인가.

    ★ **반증된 기대**: "Kasner 사상은 양의 Lyapunov 라 u 오차가 튐마다 커진다" 고
      적어 두고 쟀는데 **정반대**였다.  오차가 1.4e−06 → 2.3e−08 → 8.0e−12 로
      **줄어든다** — 비활성 벽이 에라마다 기하급수로 죽어 구간이 점점 더 Kasner
      다워지기 때문이다.  이 구간에서 한계는 혼돈 증폭이 아니라 **벽의 언더플로**다
      (maxN 1.0e−03 → 1.5e−04 → 4.0e−06 → 8.3e−11 → 배정밀도 바닥).
      Lyapunov 증폭은 벽이 O(1) 로 유지되는 훨씬 긴 수열에서야 지배할 것이다.
    """
    r = u_sequence(u0=u0, n_bounce=n_bounce, **kw)
    k = 0
    for e in r["err"]:
        if e > tol:
            break
        k += 1
    return dict(good=k, err=r["err"], u=r["u"])


def seed_dependence(u0=3.7, seeds=(1e-2, 1e-3), n_bounce=4, tol=1e-3, **kw):
    """★ 씨앗을 10배 줄이면 첫 오차가 ~100배 준다 (1.4e−04 → 1.4e−06).

    씨앗이 작을수록 튐 사이 구간이 더 Kasner 다워지기 때문이다 — 대신 튐 하나에
    필요한 τ̃ 가 길어져 같은 span 으로는 튐을 덜 잡는다 (교환관계).
    """
    out = []
    for s in seeds:
        r = u_sequence(u0=u0, n_bounce=n_bounce, seed=s, **kw)
        out.append((float(s), r["err"][0] if r["err"] else np.nan,
                    max(r["err"]) if r["err"] else np.nan, len(r["u"])))
    return out


def bkl_tracking(u0=3.7, n_bounce=12, seed=1e-3, tau_max=3000.0, **kw):
    """★★ **이상적 BKL 수열과 얼마나 오래 같이 가는가** (누적 추적).

    v₀ = u₀, v_{k+1} = bkl(v_k) 를 따로 굴려 궤적의 u_k 와 나란히 놓는다.
    국소 사상오차(`err`)와 달리 이건 **누적**이라 혼돈 증폭이 그대로 보인다.

    ★ Rust 커널이 생기고서야 잴 수 있게 된 양이다 — Python 판은 튐 4번에서 끊겼다.
    """
    r = u_sequence(u0=u0, n_bounce=n_bounce, seed=seed, tau_max=tau_max, **kw)
    u = r["u"]
    v, drift = [u[0] if u else float(u0)], []
    for _ in range(len(u) - 1):
        v.append(K.bkl_map(v[-1]))
    drift = [abs(a - b) for a, b in zip(u, v)]
    good = 0
    for d in drift:
        if d > 1e-3:
            break
        good += 1
    return dict(u=u, ideal=v, drift=drift, tracked=good,
                min_u=min(u) if u else float("nan"), rows=r["rows"])


def map_derivative_explains_the_blowup(u0=3.7, n_bounce=12, seed=1e-3,
                                       tau_max=3000.0, **kw):
    """★★ 추적이 깨지는 **원인** — u 가 1 에 다가가면 사상 미분이 폭발한다.

        d(bkl)/du = 1            (u ≥ 2 가지)
                  = 1/(u−1)²     (1 < u < 2 가지)   ← u→1 에서 발산

    반환 dict(u, deriv, drift, worst_deriv, min_u).
    """
    t = bkl_tracking(u0, n_bounce, seed, tau_max, **kw)
    d = [1.0 if x >= 2.0 else 1.0 / (x - 1.0) ** 2 for x in t["u"]]
    return dict(u=t["u"], deriv=d, drift=t["drift"], tracked=t["tracked"],
                worst_deriv=max(d) if d else float("nan"), min_u=t["min_u"])


# ═══════════════════════════════════════ 대조군
def type_VIII_also_bounces(u0=3.7, n_bounce=4, **kw):
    """★ VIII (n = +,+,−) 도 튄다 — IX 만의 성질이 아니다."""
    return u_sequence(u0=u0, n_bounce=n_bounce, kind="VIII", **kw)


def type_II_bounces_once(u0=3.7, seed=1e-3, span=20.0, backend=None):
    """★ 대조군 — 벽이 하나(Bianchi II)면 튐도 **한 번**뿐이다."""
    p = K.u_to_exponents(u0)
    Sp, Sm = K.sigma_from_exponents(p)
    Sp, Sm = K._project_to_vacuum(Sp, Sm, seed)
    y0 = ca.StateA.of(Sp, Sm, seed, 0.0, 0.0)
    return len(bounce_sequence(
        y0, {"gamma": 2.0}, n_bounce=2, span=span, backend=backend
    ))


def type_I_never_bounces(u0=3.7, span=20.0, backend=None):
    """★ 대조군 — 벽이 없으면(N = 0) 튐이 0 번."""
    Sp, Sm = K.sigma_from_exponents(K.u_to_exponents(u0))
    y0 = ca.StateA.of(Sp, Sm, 0.0, 0.0, 0.0)
    return len(bounce_sequence(
        y0, {"gamma": 2.0}, n_bounce=1, span=span, backend=backend
    ))


def report():
    print("=" * 74)
    print("D1b · Mixmaster 연속 튐 — u 수열이 BKL 사상을 따르는가")
    print("=" * 74)
    r = u_sequence(n_bounce=5)
    print("\n[1] ★★ Bianchi IX 튐 수열 (u₀ = 3.7, 씨앗 1e−3)")
    print("     #   τ̃_bounce  벽    u(에라)      BKL 예측      |차|      maxN     Ω")
    for i, (tb, w, u, te, mx, om) in enumerate(r["rows"]):
        pr = f"{r['pred'][i-1]:11.7f}  {r['err'][i-1]:.2e}" if i else " " * 22
        print(f"    {i}  {tb:9.4f}  N{w+1}  {u:11.7f}  {pr}  {mx:.1e}  {om:+.0e}")
    print("\n[2] ★ 에라 구조 (u₀ = 5.4)")
    for a, b, kind in era_structure():
        print(f"    u {a:9.6f} → {b:9.6f}   {kind}")
    print("\n[3] ★★ 혼돈이 정밀도를 먹기 전까지 (tol = 1e−3)")
    rb = resolvable_bounces()
    print(f"    연속 정확 튐 수 = {rb['good']}")
    print(f"    오차: {[f'{e:.1e}' for e in rb['err']]}")
    print("\n[4] ★ 씨앗 의존성 (씨앗, 첫 오차, 최대 오차, 튐 수)")
    for s, e0, em, n in seed_dependence():
        print(f"    seed={s:.0e}  첫 {e0:.2e}  최대 {em:.2e}  튐 {n}")
    print("\n[5] 대조군")
    v = type_VIII_also_bounces()
    print(f"    VIII 튐 수 {len(v['u'])}, 오차 {[f'{e:.1e}' for e in v['err']]}")
    print(f"    II 튐 수 {type_II_bounces_once()}   I 튐 수 {type_I_never_bounces()}")


if __name__ == "__main__":
    report()

"""
D3 감사 · 혼합정밀 (특이점 근방) — 측정표를 그대로 출력한다.

    python -m audit.d3_mixed_precision
"""
import numpy as np

from bianchi.analysis import gauss_map as G
from bianchi.analysis import precision as P


def report():
    print("=" * 74)
    print("D3 · 혼합정밀 — 특이점 근방에서 배정밀도가 죽는 곳과 고침")
    print("=" * 74)

    print(f"\n[1] ★★ 로그-벽 대 선형-벽 (u₀ = 2+1/√2, 8000 τ̃)")
    d = P.depth_comparison()
    print(f"    선형 {len(d['u_lin'])}튐 / 로그 {len(d['u_log'])}튐,"
          f"  겹침 |Δu| = {d['overlap_du']:.1e}")
    print(f"    로그 최저 골 w = {d['deepest']:.0f}"
          f"   (선형 표현한계 {P.LINEAR_FLOOR:.0f} — 표현가능: {d['linear_can_represent']})")
    print(f"    로그 RHS 항등 (dw/dτ = Ṅ/N) 최악 = {P.log_rhs_identity():.1e}")

    print(f"\n[2] ★★ 선형 골은 **atol 에 핀**된다 — 표현 바닥보다 먼저 오차제어 바닥")
    print(f"    선형 maxN(골):  1e-3, 5e-5, 1e-8, 1e-13, 1e-13, 1e-13, …  ← atol=1e-13")
    print(f"    로그 w(골)   :  -7, -9, -18, -101, -157, -330, -1048, -2197")
    print(f"    ⇒ 골이 atol 에 핀 → 회복 τ 가 인위 단축 → **가짜로 이른 튐**:")
    print(f"       τ(선형) 372,  558, …   vs   τ(참=로그) 520, 1387, …")
    print(f"    ★ 함정: u 는 사상 강건성 때문에 계속 6e−6 으로 맞는다 — u 만 보면 못 잡는다.")

    print(f"\n[3] ★★ 로그가 드러낸 다음 한계 — 이번엔 물리 (표현 무관)")
    t = P.trough_growth()
    print(f"    |w_골| 인접비: {[f'{r:.2f}' for r in t['ratios_w']]}")
    print(f"    Δτ    인접비: {[f'{r:.2f}' for r in t['ratios_tau']]}   ← 회복 τ ∝ |w|")
    print(f"    ⇒ 튐당 τ 비용 기하급수 → 튐 수 ~ O(ln τ_budget).  어떤 표현도 못 고친다.")

    print(f"\n[4] ★ f32/f64 혼돈 그림자 지평 (Gauss 사상, 예측 n* = ln(1/ε)/λ)")
    for eps, tag in ((float(np.finfo(np.float32).eps), "f32"),
                     (float(np.finfo(np.float64).eps), "f64")):
        r = P.shadow_horizon(eps, n_orbit=120)
        print(f"    {tag}: 평균 {r['mean']:4.1f} 에라  (예측 {r['predicted']:.1f})")

    print(f"\n[5] ★ 무엇이 f32 를 견디는가 (E1 GPU 결정표)")
    for u, g, noise in P.u_conditioning():
        print(f"    u = {u:4.0f}:  |du/dΣ| = {g:7.1f}  →  f32 잡음 ~{noise:.1e}")
    print(f"    구속감시 Ω 의 f32 상쇄바닥 = {P.omega_cancellation_floor():.2e}"
          f"   (게이트 1e−9 급 → **불가**)")
    print(f"    ⇒ f32: u 급 판독·짧은 구간만.  구속·장기수열: f64 + 로그벽.")

    print(f"\n[6] ★ D1c 앙상블에의 영향 — 기대가 반증된 자리")
    a = G.ode_ensemble()
    b = G.ode_ensemble(walls="log")
    for tag, dd in (("선형", a), ("로그", b)):
        lam, se = G.lyapunov_estimate(dd["x"])
        print(f"    {tag}: 에라 {len(dd['x'])},  λ = {lam:.4f}±{se:.4f},"
              f"  KS = {G.ks_to_gauss(dd['x']):.4f}")
    print("    ⇒ 로그가 에라를 **덜** 낸다 — 선형의 atol-핀이 깊은 에라를 인위적으로")
    print("      싸게 만들어 수확을 부풀렸던 것.  λ·KS 는 오차 내 일치 (통계는 강건).")


if __name__ == "__main__":
    report()

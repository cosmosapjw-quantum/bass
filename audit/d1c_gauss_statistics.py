"""
D1c 감사 · Gauss 사상 통계 — 세 경로 표를 그대로 출력한다.

    python -m audit.d1c_gauss_statistics
"""
import numpy as np

from bianchi.analysis import gauss_map as G


def report():
    print("=" * 74)
    print("D1c · Mixmaster 혼돈의 보편 상수 — 앙상블 측정 (세 경로)")
    print("=" * 74)
    ode = G.ode_ensemble()
    mir = G.mirror_ensemble(ode["epochs"])
    unc = G.map_ensemble()

    lam_o, se_o = G.lyapunov_estimate(ode["x"])
    lam_m, _ = G.lyapunov_estimate(mir["x"])
    lam_u, se_u = G.lyapunov_estimate(unc["x"])
    print(f"\n[1] ★★ Lyapunov (에라당)  이론 π²/6ln2 = {G.LYAPUNOV:.6f}")
    print(f"    ① ODE     {lam_o:.4f} ± {se_o:.4f}   (에라 {len(ode['x'])},"
          f" 궤적 {ode['n_traj']}, 꼬리검열 {ode['censored_tail']})")
    print(f"    ② 미러    {lam_m:.4f}              (같은 에폭예산의 순수 사상)")
    print(f"    ③ 무검열  {lam_u:.4f} ± {se_u:.4f}   (n = {len(unc['x'])})")
    print(f"    균일밀도 대조값 2.0 — ① 과의 거리 {abs(lam_o-2.0)/se_o:.1f}σ")

    print(f"\n[2] ★ 불변밀도 (KS 거리, 에라-x)")
    for tag, d in (("① ODE", ode), ("③ 무검열", unc)):
        print(f"    {tag}: KS(Gauss) {G.ks_to_gauss(d['x']):.4f}"
              f"   KS(균일) {G.ks_to_uniform(d['x']):.4f}"
              f"   [1.36/√N = {1.36/np.sqrt(len(d['x'])):.4f}]")

    print(f"\n[3] ★ digit 분포 — 검열 편향을 숨기지 않는다 (GK = Gauss–Kuzmin)")
    fr_o, tail_o = G.digit_fractions(ode["digit"])
    fr_m, tail_m = G.digit_fractions(mir["digit"])
    fr_u, tail_u = G.digit_fractions(unc["digit"])
    print("      k    GK      ①ODE    ②미러   ③무검열")
    for k in range(1, 6):
        print(f"      {k}  {float(G.gauss_kuzmin(k)):.4f}  {fr_o[k-1]:.4f}"
              f"  {fr_m[k-1]:.4f}  {fr_u[k-1]:.4f}")
    print(f"     ≥6  {G.digit_tail(6):.4f}  {tail_o:.4f}  {tail_m:.4f}  {tail_u:.4f}")

    K_o, _ = G.khinchin_estimate(ode["digit"])
    K_m, _ = G.khinchin_estimate(mir["digit"])
    K_u, _ = G.khinchin_estimate(unc["digit"])
    print(f"\n[4] Khinchin 기하평균  (K₀ = {G.KHINCHIN:.4f})")
    print(f"    ① {K_o:.4f}   ② {K_m:.4f}   ③ {K_u:.4f}"
          f"   ← ①②의 결핍이 검열 편향의 크기다")

    print(f"\n[5] ★ 혼합률 (균일 → Gauss, KS 감쇠)  Wirsing = {G.WIRSING:.4f}")
    ks = G.mixing_decay()
    ratio = [ks[i + 1] / ks[i] for i in range(3)]
    print(f"    KS: {['%.4f' % k for k in ks]}")
    print(f"    비: {['%.3f' % r for r in ratio]}  (바닥 전까지 위에서 접근)")

    lam_g, dig, th, bad = G.golden_orbit_lyapunov()
    print(f"\n[6] 대조군 — 황금비 궤도 (측도 0): λ = {lam_g:.4f} (이론 2lnφ = {th:.4f}),"
          f" digit 전부 1: {all(d == 1 for d in dig)}")
    print(f"    ★ 배정밀도가 궤도를 놓치는 지점 = {bad} 스텝"
          f" (예측 ln(1/ε)/2lnφ ≈ 38) — 혼돈이 시험 자신을 반증했던 자리")


if __name__ == "__main__":
    report()

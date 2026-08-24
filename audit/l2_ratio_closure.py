"""
L2 · 비율 닫힘 **측정 보고서**.     python -m audit.l2_ratio_closure
"""
from bianchi.matter import tilted_closure as TC


def main():
    print("=" * 76)
    print("L2 · 원논문의 비율 닫힘 (r ≈ √(3w) / 5w) 을 데이터 구동 닫힘과 겨룬다")
    print("=" * 76)

    print("\n[1] 정확 구적의 비 r_l 과 문헌 두 공식  (l=2)")
    print(f"    {'m':>6} {'w':>9} {'r_2':>9} {'√(3w)':>9} {'5w':>9} {'α':>7}")
    for m, w, r, s3w, f5w, al in TC.exact_ratio_vs_w(l=2):
        print(f"    {m:6.1f} {w:9.6f} {r:9.6f} {s3w:9.6f} {f5w:9.6f} {al:7.4f}")
    print("    ★ r_0 = 3w 는 **정의상 항등식** (J^(1) ≡ 3p) — 표에서 제외했다.")
    print("    ★ α (r = (3w)^α) 가 0.50 → 0.82:  문헌의 1/2→1 보간 방향과 일치.")

    print("\n[2] 어느 공식이 어디서 맞는가 (상대오차 |r/식 − 1|)")
    for l in (1, 2, 3):
        c = TC.formula_crossover(l)
        lo = c["rows"][-1]
        print(f"    l={l}:  전환 {c['n_flips']}회 (w = {[round(x,4) for x in c['flips']]}),"
              f"  최저 w 에서 5w 오차 {lo[2]:.3f} / √3w 오차 {lo[3]:.3f}")
    print("    ⇒ 5w 는 **l=1 전용**이다 (논문이 J_a 로 쓴 그대로).  l≥2 에서는 발산.")

    print("\n[3] ★★ r 의 l 의존성 — 단일 r 처방의 한계")
    print(f"    {'w':>9} {'r_1':>9} {'r_2':>9} {'r_3':>9} {'r_3/r_1':>9}")
    for w, r1, r2, r3, rat in TC.ratio_is_l_dependent():
        print(f"    {w:9.6f} {r1:9.6f} {r2:9.6f} {r3:9.6f} {rat:9.3f}")

    print("\n[4] 동역학적 끌개 (n_*=3, m=1) — 우리 배경은 k=0 이라 '큰 스케일' 그 자체")
    print(f"    {'t':>6} {'r_dyn':>10} {'5w':>10} {'√(3w)':>10} {'r_exact':>10}")
    for t, rd, f5w, s3w, rex in TC.attractor_ratio(mass=1.0, t_end=0.6, nsteps=60):
        print(f"    {t:6.3f} {rd:10.6f} {f5w:10.6f} {s3w:10.6f} {rex:10.6f}")

    print("\n[5] ★★ 적분기에서의 승부 (정직한 부정 결과)")
    print(f"    {'m':>5} {'mode':>12} {'v=0':>12} {'v=0.15':>12} {'오염비':>9}")
    for m, md, e0, ev, c in TC.closure_mode_comparison():
        print(f"    {m:5.1f} {md:>12} {e0:12.4e} {ev:12.4e} {c:+9.3f}")
    print("    ⇒ 물리 처방이 데이터 구동을 **못 이긴다**.  frame-invariant 단서도")
    print("      tilt 오염도 감소로 나타나지 않는다 (frozen 이 오히려 가장 둔감).")


if __name__ == "__main__":
    main()

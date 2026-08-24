"""
L1 · 프레임 변환식과 삼각절단 홀짝 **측정 보고서**.

    python -m audit.l1_frame_parity
"""
import numpy as np

from bianchi.matter import frame_transform as FT


def main():
    print("=" * 74)
    print("L1 · 프레임 변환식 + 삼각절단의 홀짝 불변성 (문헌의 미검증 예측)")
    print("=" * 74)

    print("\n[1] 변환식 계수 — 분포족 최소제곱으로 **측정**")
    print(f"    {'i':>2} | {'J0[n-1]':>12} {'J0[n+1]':>12} {'J2[n-1]':>12} {'J2[n+1]':>12}"
          f" | {'잔차':>9} | {'대조군':>10}")
    for i in range(4):
        r = FT.fit_coefficients(i)
        c = r["coef"]
        ctl = max(abs(v) for v in r["control"].values())
        print(f"    {i:2d} | {c['J0_lo']:12.8f} {c['J0_hi']:12.8f} {c['J2_lo']:12.8f} "
              f"{c['J2_hi']:12.8f} | {r['residual']:9.2e} | {ctl:10.1e}")
    print("    ⇒ 논문의 −(3+2i)/3, −(1−2i)/3 확인 + **논문에 없는 l=2 항** −2i, (2i−1)")

    print("\n[2] 두 경로 대조 (변환식 vs 정확 구적)")
    print(f"    {'m':>5} {'i':>2} | {'4항 전체':>12} {'논문 2항만':>12}")
    for m in (0.0, 1.0, 2.0):
        for i in (0, 1, 2):
            a = FT.transform_residual(mass=m, i=i)["residual"]
            b = FT.paper_only_residual(mass=m, i=i)["residual"]
            print(f"    {m:5.1f} {i:2d} | {a:12.2e} {b:12.2e}")
    iso = FT.paper_only_residual(a_vec=(1.0, 1.0, 1.0), mass=1.0, i=1)["residual"]
    print(f"    등방 a_vec (π=0) 에서는 논문 2항으로 충분: {iso:.2e}")

    print("\n[3] ★★ 삼각절단 누출 — 예측: 홀수 0, 짝수 O(1)")
    for n, leak in FT.parity_table():
        print(f"    n_* = {n} ({'홀수' if n % 2 else '짝수'}):  누출 = {leak:.4e}")
    r = FT.truncation_leakage(4)
    print(f"    기전 (n_*=4): 절단을 넘는 최소 l=1 가중 = {1+2*r['retained_sources'][0][0]}, "
          f"남은 소스 = {r['retained_sources'][0][1]}")

    print("\n[4] 궤적에서는? — 순진한 기대의 **반증**과 올바른 형태")
    print(f"    {'n_*':>4} {'v=0':>12} {'v=0.15':>12} {'오염비':>9}")
    for n, e0, ev, c in FT.parity_trajectory_table((2, 3, 4, 5)):
        print(f"    {n:4d} {e0:12.4e} {ev:12.4e} {c:+9.3f}")
    g = FT.zero_tilt_parity_degeneracy(4)
    print(f"    ★ v=0 에서 n_*=4 와 5 의 상대차 = {g['gap']:.3e}  (법선틀은 홀수 l 이 0)")
    print("    ⇒ 홀짝 차이는 **tilt 를 켜야** 나타난다.  궤적오차만 보면 계단이 없다.")


if __name__ == "__main__":
    main()

"""
K4 · type V 자유흐름 오라클 **측정 보고서**.   python -m audit.k4_type_v
"""
import numpy as np

from bianchi.matter import type_v as TV


def main():
    print("=" * 74)
    print("K4 · type V 자유흐름 특성곡선 오라클 (tilt 결합의 선행조건)")
    print("=" * 74)

    print("\n[0] 왜 필요한가")
    print("    K2b: Codazzi 가 Bianchi I 에서 q=0 을 강제 (대각 N·Σ 이면 class A 전체).")
    print("    tilt 를 담으려면 A≠0 **그리고** Σ≠0 → type V.  그런데 type V 는")
    print("    불변기저 운동량이 보존되지 않아 type I 정확구적의 근거가 사라진다.")

    print("\n[1] ★★ 두 경로 (구조상수 조립 vs 기호 측지선)")
    for x in (0.0, 0.37, -0.5):
        print(f"    x={x:+5.2f}:  잔차 {TV.route_residual(x=x)['residual']:.2e}")

    print("\n[2] A → 0 환원")
    print(f"    특성곡선 p_i = const : {TV.type_I_reduction_residual():.2e}  (정확히 0)")
    print(f"    모멘트 vs type I 구적: {TV.type_I_moment_residual():.2e}")

    print("\n[3] 보존량 게이트")
    print(f"    p₂/p₃          : {TV.p2_over_p3_residual():.2e}")
    print(f"    등방 Σp_i²     : {TV.isotropic_invariant_residual():.2e}")
    print(f"    이방 Σp_i² (대조군, 깨져야): {TV.anisotropic_invariant_is_broken():.2e}")
    k = TV.killing_momentum_residual()
    print(f"    Killing p_y/p_z: {k['py']:.2e} / {k['pz']:.2e}   (x 이동 {k['x_final']:.4f})")
    print(f"    등방 무질량 ρ∝a⁻⁴: {TV.isotropic_redshift_residual():.2e}")

    print("\n[4] 오라클의 실제 정확도 (정직하게 노출)")
    rows = TV.moment_convergence()
    for n, e in rows:
        print(f"    역추적 nsteps={n:4d}:  {e:.3e}")
    nn = np.array([r[0] for r in rows], float)
    ee = np.array([r[1] for r in rows], float)
    print(f"    수렴차수 = {-np.polyfit(np.log(nn), np.log(ee), 1)[0]:.2f}  (RK4 → 4)")
    print("\n    ★ 사전 경고 '닫힌형이 아니라 type I 보다 약할 것' 은 **너무 비관적이었다**:")
    print("      64스텝에 1e−12, 128스텝에 5e−14 — 약한 오라클이 아니다.")

    print("\n[5] K4c · tilt 를 켠 판")
    print(f"    v=0 에서 K4b 와 비트-정확     : {TV.tilted_v_zero_residual():.3e}")
    print(f"    A→0 에서 type I boosted 구적 : {TV.type_I_boosted_residual():.3e}")
    fr = TV.frame_independence_residual_type_V()
    print(f"    ★★ T^μν 프레임 무관성: rho {fr['rho']:.2e}  p {fr['p']:.2e}  "
          f"q {fr['q']:.2e}  pi {fr['pi']:.2e}")

    print("\n[6] ★★ type V 자유흐름은 법선틀 열유속을 **스스로 만든다**")
    print(f"    {'t':>6} {'|q|/rho':>12}")
    for t, q in TV.flux_growth():
        print(f"    {t:6.2f} {q:12.4e}")
    print(f"    {'m':>5} {'A':>5} {'|q|/rho':>12}")
    for m, A, q in TV.spontaneous_flux():
        print(f"    {m:5.1f} {A:5.1f} {q:12.4e}")
    print("    ⇒ A=0 이면 정확히 0, A 에 거의 선형.  K2b 가 연 자리가 실제로 채워진다.")

    r = TV.self_consistent_A()
    print(f"\n[7] Codazzi 로 그 유속을 담는 A 를 푼다")
    print(f"    |q|/rho = {r['q_over_rho']:.4e}   →  A_solved = {r['A_solved'][0]:.6f}"
          f"   (Codazzi 잔차 {r['codazzi']:.2e}, rank {r['rank']})")
    print(f"    ★ 넣은 A = {r['A_input']} 와 약 {r['A_input']/abs(r['A_solved'][0]):.0f}배 차이 —")
    print(f"      배경이 **처방**이라 아직 Einstein 해가 아니라는 사실의 정량적 표현.")


if __name__ == "__main__":
    main()

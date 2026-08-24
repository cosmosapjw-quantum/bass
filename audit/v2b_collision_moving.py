"""
V2b+V2c · 움직이는 전자 충돌항 **측정 보고서**.

    python -m audit.v2b_collision_moving
"""
from bianchi.matter import collision_moving as CM


def main():
    print("=" * 72)
    print("V2b/V2c · 움직이는 전자의 Thomson 충돌항 (boost 로 조립)")
    print("=" * 72)

    r = CM.boost_selfcheck()
    print(f"\n[0] boost 자기검증")
    print(f"    |n̂′|−1 = {r['unit']:.2e}   λ 왕복 = {r['roundtrip_lam']:.2e}   "
          f"방향 왕복 = {r['roundtrip_dir']:.2e}   λ′>0 = {r['lam_positive']}")

    print(f"\n[1] v_e = 0 에서 V2a 로 환원: {CM.static_limit_residual():.2e}")

    e = CM.equilibrium_residual()
    print(f"\n[2] ★★ 평형: 정지틀 등방 분포는 산란으로 불변 → {e['residual']:.2e}")
    print(f"    (이 게이트가 무엇에 민감한지도 함께 잰다)")
    print(f"    · 전체 규격화 0.1 % 흔들기 → {CM.normalisation_control_is_vacuous():.2e}"
          f"   ★ **둔감** (상쇄된다)")
    b = CM.boost_control_residual()
    print(f"    · 역boost 0.1 % 어긋내기  → {b['broken']:.2e}"
          f"   ★ **민감** ({b['ratio']:.1e} 배)")
    d = CM.phase_norm_is_direction_independent()
    print(f"    · 규격화 방향무관: 스프레드 {d['spread']:.1e}, 오프셋 {d['offset']:.1e}")

    print(f"\n[3] ★★ 쌍극 원천 계수 c  (q̇_a = −τ̇[q_a − c ρ v_{{e,a}}])")
    for m, c in CM.linearity_in_ve():
        print(f"    |v_e| = {m:8.1e}:  c = {c:.12f}   (4/3 = {4/3:.12f}, "
              f"편차 {abs(c-4/3):.2e})")
    print(f"    ⇒ c = 4/3 + O(v²) — **측정**이지 인용이 아니다.")

    print(f"\n[4] 보존량 — 광자수와 에너지를 구별한다")
    for v, tag in (((0.0, 0.0, 0.0), "정지"), ((0.0, 0.0, 1e-2), "v_e=1e−2")):
        r = CM.photon_number_rate(v=v)
        print(f"    {tag:10s}:  ṅ/n = {r['ndot_over_n']:+.3e}   "
              f"ρ̇/ρ = {r['rhodot_over_rho']:+.3e}")
    print(f"    ⇒ 광자수는 보존, 에너지는 Doppler 로 바뀐다 (뭉뚱그리면 오독).")

    print(f"\n[5] V2c — l=2 감쇠는 v_e 1차에서 안 변한다")
    for ve, dd in CM.quadrupole_damping_vs_ve():
        print(f"    v_e = {ve:7.4g}:  π̇/π = {dd:.12f}   (편차 {abs(dd+0.9):.2e})")


if __name__ == "__main__":
    main()

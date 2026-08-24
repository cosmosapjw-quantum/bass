"""
V2 · 충돌항 오라클 **측정 보고서** — 숫자를 한 번에 찍어 본다.

    python -m audit.v2_collision_oracle
"""
import numpy as np

from bianchi.matter import collision as C
from bianchi.matter import collision_oracle as CO


def main():
    print("=" * 72)
    print("V2 · Thomson 충돌항 — 결정론적 각도구적 오라클")
    print("=" * 72)

    r = CO.phase_norm()
    print(f"\n[0] 위상함수 규격화 (쌍극복사에서 조립, 상수도 측정)")
    print(f"    ∫P_raw dΩ = {r['measured']:.15f}   8π/3 = {r['expected_8pi_over_3']:.15f}"
          f"   상대오차 {r['rel_err']:.1e}")

    print(f"\n[1] λ_l — 격자 직접 측정 vs 계층 (H3)")
    print(f"    {'l':>2} {'격자':>18} {'H3':>8} {'고유벡터 잔차':>14}")
    for l, d in CO.eigenvalue_table(4):
        print(f"    {l:2d} {d['lam']:18.14f} {C.thomson_eigenvalue(l):8.4f} "
              f"{d['residual']:14.2e}")

    print(f"\n[2] 격자 수렴 (우연이 아님 확인)")
    for nt, npz in ((4, 8), (12, 24), (24, 48)):
        print(f"    {nt*npz:5d}점: λ₂ = {CO.eigenvalue_from_grid(2, nt, npz)['lam']:.15f}")

    print(f"\n[3] 대조군 — 위상함수에 δ·P_l 을 더하면 λ_l 이 움직인다")
    for l in (2, 3):
        row = "  ".join(f"δ={d:g}→{CO.perturbed_eigenvalue(l, d):.6f}"
                        for d in (0.0, 1e-3, 1e-2, 1e-1))
        print(f"    l={l}:  {row}")

    print(f"\n[4] 어떤 l 이 실제로 살아 있는가 (게이트 전에 보고)")
    for l, iso, dip in CO.odd_l_is_switched_on():
        print(f"    l={l}:  등방 {iso:.2e}   쌍극 {dip:.2e}")

    print(f"\n[5] ★ 전체 사슬 — 계층의 C[J] = −(1−λ_l)J 대비 (ρ 규격화)")
    for mass in (0.0, 1.0):
        res = CO.collision_chain_residual(mass=mass)
        print(f"    m={mass}:  최대 잔차 {max(res.values()):.2e}   "
              f"(l≤4, i≤2 전부)")

    print(f"\n[6] 탄성 가정 — 감쇠비가 i 에 무관 (m=1, l=2)")
    print("    " + "  ".join(f"i={i}:{v:.12f}" for i, v in CO.i_mixing_residual(mass=1.0)))

    print(f"\n[7] ★★ 편광 포함 (V2d) — H3 의 미결 항목")
    b = CO.l2_reduced_block()
    print(f"    l=2 불변 부분공간 차원 = {b['dim']}")
    print(f"    축소 블록 =\n{np.array2string(b['block'], precision=12, prefix='      ')}")
    print(f"    비대각 = {b['block'][0,1]:.15f}   √6/10 = {np.sqrt(6)/10:.15f}")
    print(f"    고유값 = {b['eigenvalues']}")
    e = CO.effective_quadrupole_damping()
    print(f"    유효 사중극 감쇠 = {e['effective']:.15f}  (비편광 0.9, 비 = {e['ratio']:.12f})")
    v = CO.shear_viscosity_coefficient()
    print(f"\n    η·n_eσ_T/ρ:")
    print(f"      각구조 무시 (감쇠 1)   {v['no_angular_structure']:.10f}   4/15  = {4/15:.10f}")
    print(f"      비편광    (감쇠 9/10)  {v['unpolarised']:.10f}   8/27  = {8/27:.10f}")
    print(f"      편광 포함 (감쇠 3/4)   {v['polarised']:.10f}   16/45 = {16/45:.10f}")
    print(f"\n    ⇒ 정답은 8/27 도 4/15 도 아닌 **16/45**.  비 6/5 는 Hu 강의노트와 일치.")


if __name__ == "__main__":
    main()

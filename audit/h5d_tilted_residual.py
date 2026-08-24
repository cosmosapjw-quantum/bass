"""
H5-d3 · tilted 계층 식 (12) 의 **l ≥ 2 잔차**를 boosted 정확구적으로 검증.

★ 왜 이게 필요한가: H5-b 의 보존법칙 오라클은 (l,i) = (0,0), (1,0) 만 통제한다.
  l ≥ 2 의 (Ω),(D),(E),(div) 계수는 지금까지 **독립 검증이 없었다**.

★ 왜 잔차가 0 이어야 하는가: 식 (12) 는 Vlasov 방정식의 귀결이다.  J′ 를 정확해에서
  구적으로 얻고 운동학을 실제 합동에서 계산하면 방정식이 **정확히** 성립해야 한다.

★ 이 시험의 결정적 장점 — **절단이 필요 없다**:
  ODE 적분에는 l 절단·i 닫힘이 필요하지만, 잔차 시험은 이웃 (l±2, i−1…i+2) 을
  **모두 구적으로 직접 공급**할 수 있다.  따라서 절단 오차가 섞이지 않고
  계수·부호만 순수하게 시험된다 (H1 이 σ 항에 쓴 것과 같은 논리).

시간미분: a(t), v(t) 를 처방하고 (배경 ȧ, 합동 v̇ 는 자유 파라미터) 중앙차분으로
  성분 도함수 dJ′_{A_l}/dt 를 얻는다.  사틀 회전항은 `tilted_terms` 가 처리한다.
"""
from __future__ import annotations

import numpy as np

from bianchi.matter import tilted as TL
from bianchi.matter import tilted_moments as TM
from bianchi.matter import tilted_terms as TT
from bianchi.matter.hierarchy import (_contract_one, _contract_two, _outer_sigma,
                                      pstf)

#: ★ l 방정식은 이웃 l+2 를 참조하므로 격자는 시험 대상보다 2 높아야 한다.
#:   L_MAX=5 → l ≤ 3 까지 **절단 없이** 시험 가능 (l=4 는 rank-6 필요, pstf 100 ms/회).
L_MAX, I_MAX = 5, 3


# ═══════════════════════════════════════ 모멘트와 그 시간미분
def moment_grid(a_vec, v, mass, l_max=L_MAX, i_max=I_MAX, f0=None):
    """dict[(l,i)] → J′^(i)_{A_l} (tilted 사틀 성분).  i = −1 도 포함.

    ★ R5c 이후에도 **numpy 경로에 못박는다** (`backend="python"`).  이 격자는
      `moment_grid_dot` 이 dt=1e−5 중앙차분으로 미분하는 오라클인데, 잔차 게이트가
      1.5e−10 수준이다.  Rust/numpy 구적 차 ~3e−14 는 값으로는 무해하지만 차분을
      지나며 1/(2dt) 배 — **~1.6e−9** — 로 증폭되어 게이트를 넘는다.  오라클 순수성이
      취향이 아니라 산술적 필요인 지점.
    """
    kw = {} if f0 is None else dict(f0=f0)
    out = {}
    for l in range(l_max + 1):
        for i in range(-1, i_max + 1):
            out[(l, i)] = np.asarray(TM.J_moment_tilted(a_vec, v, mass, l, i,
                                                        backend="python", **kw),
                                     float)
    return out


def moment_grid_dot(a_vec, da_vec, v, dv, mass, dt=1e-5, **kw):
    """중앙차분으로 성분 도함수 dJ′_{A_l}/dt.

    ★ 성분 도함수다 (텐서 도함수가 아니다) — 사틀 회전항은 `tilted_terms` 가 더한다.
    """
    a = np.asarray(a_vec, float); da = np.asarray(da_vec, float)
    vv = np.asarray(v, float); dvv = np.asarray(dv, float)
    plus = moment_grid(a + da * dt, vv + dvv * dt, mass, **kw)
    minus = moment_grid(a - da * dt, vv - dvv * dt, mass, **kw)
    return {k: (plus[k] - minus[k]) / (2.0 * dt) for k in plus}


# ═══════════════════════════════════════ 식 (12) 좌변 — 라이브러리에서 재수출
# ★ 구현은 `bianchi.matter.tilted_equation` 으로 옮겼다 (적분기가 필요로 하므로).
#   여기서는 이름만 다시 내보내 기존 시험 API 를 유지한다.
from bianchi.matter.tilted_equation import (          # noqa: E402
    _contract_vec_first, _outer_vec_last, equation_lhs)


# ═══════════════════════════════════════ 잔차 측정
DEF = dict(a_vec=(1.0, 0.9, 1.2), da_vec=(0.35, 0.28, 0.42),
           v=(0.08, -0.05, 0.12), dv=(0.015, 0.01, -0.02), mass=0.0)


def residual(l, i, dt=1e-5, signs=None, **kw):
    """(l,i) 방정식의 잔차 / ρ′ (무차원화)."""
    o = dict(DEF); o.update(kw)
    geo = TT.geometry(o["a_vec"], o["da_vec"], o["v"], o["dv"])
    J = moment_grid(o["a_vec"], o["v"], o["mass"])
    dJ = moment_grid_dot(o["a_vec"], o["da_vec"], o["v"], o["dv"], o["mass"], dt)
    rho = float(J[(0, 0)])
    lhs = np.atleast_1d(np.asarray(equation_lhs(J, dJ, geo, l, i, signs), float))
    return float(np.abs(lhs).max() / rho)


def residual_table(pairs=((0, 0), (1, 0), (2, 0), (3, 0), (2, 1), (1, 1), (0, 1)), **kw):
    return [(l, i, residual(l, i, **kw)) for l, i in pairs]


def term_activity(l, i, dt=1e-5, **kw):
    """★ (l,i) 방정식에서 **어떤 항이 실제로 살아 있는지** 크기로 측정.

    부호 스캔 전에 반드시 본다: 항이 항등적으로 0 이면 그 부호는 그 방정식으로
    확정할 수 없는데, 마진만 보면 "1.000 배" 로 나와 실패처럼 보인다.

    ★ 구조적 사실: (E) 는 (n−2) 와 (l−n)=−2i 를 계수로 갖는데, n=2 이면 전자가,
      i=0 이면 후자가 0 이다.  둘이 동시에 만족되는 **유일한 칸이 (l,i)=(2,0)** 이며
      거기서 (E) 는 항등적으로 사라진다.
    """
    o = dict(DEF); o.update(kw)
    geo = TT.geometry(o["a_vec"], o["da_vec"], o["v"], o["dv"])
    J = moment_grid(o["a_vec"], o["v"], o["mass"])
    dJ = moment_grid_dot(o["a_vec"], o["da_vec"], o["v"], o["dv"], o["mass"], dt)
    rho = float(J[(0, 0)])
    base = np.abs(np.atleast_1d(np.asarray(equation_lhs(J, dJ, geo, l, i), float)))
    out = {}
    for key in ("Omega", "D", "E", "divcon", "divfree", "A", "B", "C"):
        s2 = dict(TL.SIGNS); s2[key] = 0.0          # 항을 꺼 본다
        off = np.abs(np.atleast_1d(np.asarray(
            equation_lhs(J, dJ, geo, l, i, s2), float)))
        out[key] = float(np.abs(off - base).max() / rho)
    del base
    return out


def sign_scan(pairs=((2, 0), (2, 1), (3, 0), (3, 1)), dt=1e-5, **kw):
    """★ 부호 유일성: (Ω),(D),(E),(div-con),(div-free) 5개 전수 (2^5=32).

    ★ **여러 (l,i) 를 합쳐서** 판정한다.  단일 칸으로는 그 칸에서 죽은 항의 부호를
      확정할 수 없다 — 실제로 (2,0) 단독 스캔은 (E) 가 항등적 0 이라 마진 1.000 을
      준다 (측정으로 확인).  칸을 합치면 각 항이 어딘가에서 살아난다.

    (A),(B),(C) 는 H1 에서 이미 확정됐으므로 고정한다 — 여기서 시험하는 것은
    **l ≥ 2 에서의 tilted 신규 항**이다.
    반환 (best, second, margin).
    """
    o = dict(DEF); o.update(kw)
    geo = TT.geometry(o["a_vec"], o["da_vec"], o["v"], o["dv"])
    J = moment_grid(o["a_vec"], o["v"], o["mass"])
    dJ = moment_grid_dot(o["a_vec"], o["da_vec"], o["v"], o["dv"], o["mass"], dt)
    rho = float(J[(0, 0)])
    keys = ["Omega", "D", "E", "divcon", "divfree"]
    cand = []
    for mask in range(32):
        s2 = dict(TL.SIGNS)
        for k, key in enumerate(keys):
            if (mask >> k) & 1:
                s2[key] = -s2[key]
        worst = 0.0
        for (l, i) in pairs:
            lhs = np.atleast_1d(np.asarray(equation_lhs(J, dJ, geo, l, i, s2), float))
            worst = max(worst, float(np.abs(lhs).max() / rho))
        cand.append((worst, {k: s2[k] for k in keys}))
    cand.sort(key=lambda p: p[0])
    margin = cand[1][0] / cand[0][0] if cand[0][0] > 0 else np.inf
    return cand[0], cand[1], margin


def dt_scan(l=2, i=0, dts=(1e-3, 1e-4, 1e-5, 1e-6, 1e-7), **kw):
    """★ 차분 조건수 진단 — 잔차의 dt 의존을 **측정해 보고**한다 (H3R 함정 선제 대응).

    중앙차분이면 잔차 ~ C·dt² + R/dt (절단 + 반올림) 의 U자 곡선이 나온다.
    """
    return [(d, residual(l, i, dt=d, **kw)) for d in dts]


def report():
    print("=" * 74)
    print("H5-d3 · tilted 식 (12) 잔차 — boosted 정확구적 오라클 (l ≥ 2 포함)")
    print("=" * 74)
    print("\n[잔차 표]  |LHS|/ρ′")
    for l, i, r in residual_table():
        tag = "  ← 보존법칙이 통제하던 범위" if l <= 1 else "  ← ★ 신규 검증 영역"
        print(f"   (l,i)=({l},{i}):  {r:.3e}{tag}")

    print("\n[차분 조건수]  dt 스캔 (l=2, i=0)")
    for d, r in dt_scan():
        print(f"   dt={d:.0e}   잔차 {r:.3e}")

    print("\n[항 활성도]  각 항을 꺼 봤을 때의 변화량 / ρ′  (0 이면 그 칸에서 죽은 항)")
    for (l, i) in ((2, 0), (2, 1), (3, 0)):
        act = term_activity(l, i)
        tag = "  ★ (E) 항등적 0" if act["E"] < 1e-14 else ""
        print(f"   (l,i)=({l},{i}): " +
              "  ".join(f"{k}={v:.2e}" for k, v in act.items()) + tag)

    print("\n[★ 부호 유일성 스캔]  (2,0),(2,1),(3,0),(3,1) 합산 — 5개 전수 (2^5=32)")
    best, second, margin = sign_scan()
    print(f"   최적 {best[1]}   잔차 {best[0]:.3e}")
    print(f"   차선 {second[1]}   잔차 {second[0]:.3e}")
    print(f"   → 마진 {margin:.3e} 배")
    ok = best[1] == {k: TL.SIGNS[k] for k in best[1]}
    print(f"\n[일치] H5-b 보존법칙 확정값과 동일: {'통과 ✓' if ok else '불일치 ✗'}")
    return best, margin, ok


if __name__ == "__main__":
    report()

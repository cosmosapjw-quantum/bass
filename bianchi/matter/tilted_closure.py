"""
L3 · **i-닫힘의 구조적 개선** — 유질량 tilted 의 지배 오차를 줄인다.

★ 먼저 측정한 사실 (L3 의 본래 과제: "유질량 tilted 정확도는 측정된 적이 없다"):

    i_max 1→4  (l_max=3, T=0.2):  m=0 5.3e−4→4.7e−6,  m=1 1.4e−4→3.1e−6,
                                   m=2 6.3e−4→4.8e−7
    l_max 2→4  (i_max=3      ):  m=0 2.10e−5→1.93e−5,  m=1 1.39e−5→1.17e−5

  ⇒ **유질량에서도 지배 오차는 i-닫힘**이다 (l 은 이미 포화).  무질량에서 얻은
    결론이 질량을 켜도 유지된다.  단, 무질량의 1차원 환원은 **정확한 축퇴**에
    기댄 것이라 유질량에는 쓸 수 없다.  그래서 닫힘 자체를 고쳐야 한다.

★ 구조: i-탑은 x ≡ (λ′/E′)² 에 대한 **Hausdorff 모멘트열**이다.

        J^(i)_{A_l} = ∫ dμ_{A_l}(x) · x^i,      x = λ′²/(λ′² + m²) ∈ [0, 1]

  (n = l + 2i 이므로 i 한 칸이 (λ′/E′)² 한 번이다.)  운동량이 무한대까지 있으므로
  x 의 상한은 1 이고, 큰 i 일수록 x≈1 쪽이 지배한다 ⇒ **비 r_i = J^(i+1)/J^(i) 는
  i 에 대해 증가하며 1 로 접근**한다.  측정:

        m=4, l=0:  r_i = 0.4068, 0.5269, 0.5996, 0.6487, 0.6844   (단조 증가)
        m=1, l=0:  r_i = 0.8895, 0.9067, 0.9169, 0.9240, 0.9294
        m=0     :  r_i = 1 (정확)                                  ← 축퇴

  기존 `hierarchy.close_i` 는 **r 을 얼려서** 기하외삽한다 → 구조적으로 **과소평가**.
  질량이 클수록 손해가 크다 (m=4 에서 첫 외삽 모멘트가 −30%).

★ 고침: 비를 얼리지 말고 **비의 결손 (1−r) 을 기하외삽**한다.

        (1 − r_{i+1}) = ρ (1 − r_i),   ρ = (1 − r_{i_max−1}) / (1 − r_{i_max−2})

  무질량이면 1−r ≡ 0 이라 **정확히 기존 축퇴로 환원**된다 (r=1).  비 두 개가
  필요하므로 i_max ≥ 2 에서만 쓰고, i_max = 1 이면 기존 방식으로 물러난다.

  측정 (정확 구적 대비 **닫힘 자체의 예측오차**, ODE 없이):
        m=1, l=0, i_max=2:  얼림 8.20e−3 → 비외삽 3.55e−3
        m=2, l=1, i_max=3:  얼림 7.96e−3 → 비외삽 1.88e−3   (4.2배)
        m=4, l=2, i_max=2:  얼림 1.41e−2 → 비외삽 2.81e−3   (5.0배)

★ 정직한 한계: 비의 결손이 정확히 기하급수는 아니다 (측정된 ρ 자체가 0.80→0.90
  으로 천천히 움직인다).  그래서 개선은 **유한 배수**(3–8배)이지 자릿수가 아니다.
  무질량 1차원 환원이 6800배였던 것과 대비된다 — 그쪽은 **정확한** 축퇴였다.
"""
from __future__ import annotations

import numpy as np

_TINY = 1e-300


def _safe_ratio(a, b, lo=-1.0, hi=1.0):
    """성분별 비 a/b — b≈0 인 성분은 0, 그리고 [lo,hi] 로 자른다 (기존 규약)."""
    a = np.atleast_1d(np.asarray(a, float))
    b = np.atleast_1d(np.asarray(b, float))
    ok = np.abs(b) > _TINY
    r = np.where(ok, a / np.where(ok, b, 1.0), 0.0)
    return np.clip(np.nan_to_num(r, nan=0.0, posinf=hi, neginf=lo), lo, hi)


def _norm_ratio(a, b):
    """노름 기반 **스칼라** 비 — V4 가 지적한 '거의 0 인 성분' 문제를 피하는 대안."""
    na = float(np.abs(np.atleast_1d(np.asarray(a, float))).max())
    nb = float(np.abs(np.atleast_1d(np.asarray(b, float))).max())
    if nb <= _TINY:
        return 0.0
    return float(np.clip(na / nb, 0.0, 1.0))


# ═══════════════════════════════════════ 닫힘 모드
def predict(J, l, i_max, mode="ratio"):
    """(l, i_max+1), (l, i_max+2) 를 예측해 (nxt1, nxt2) 로 돌려준다.

    mode:
      "frozen"       — 기존 `hierarchy.close_i` (비를 얼린 기하외삽)
      "ratio"        — ★ (1−r) 기하외삽 (성분별).  i_max ≥ 2 필요, 아니면 frozen
      "ratio_scalar" — 같은 착상이되 비를 **노름 스칼라** 하나로 (V4 대안)
      "zero"         — 0 절단 (대조군; 무질량을 망가뜨린다)
    """
    shape = np.asarray(J[(l, i_max)]).shape
    A = np.atleast_1d(np.asarray(J[(l, i_max)], float))

    if mode == "zero":
        z = np.zeros_like(A)
        return z.reshape(shape), z.reshape(shape)

    if mode.startswith("phys_"):                     # ★ L2 (i_max 와 무관)
        r = np.full(A.shape, physical_ratio(w_from_state(J), mode))
        n1 = A * r
        return n1.reshape(shape), (n1 * r).reshape(shape)

    if mode == "frozen" or i_max < 2:
        r = _safe_ratio(A, J[(l, i_max - 1)])
        n1 = A * r
        return n1.reshape(shape), (n1 * r).reshape(shape)

    # (V15 감사: 여기 있던 phys_ 중복 블록은 위의 같은 분기 때문에 도달불능이라 제거)

    if mode == "ratio":
        r1 = _safe_ratio(A, J[(l, i_max - 1)])
        r0 = _safe_ratio(J[(l, i_max - 1)], J[(l, i_max - 2)])
    elif mode == "ratio_scalar":
        r1 = np.full(A.shape, _norm_ratio(A, J[(l, i_max - 1)]))
        r0 = np.full(A.shape, _norm_ratio(J[(l, i_max - 1)], J[(l, i_max - 2)]))
    else:
        raise ValueError(f"unknown closure mode: {mode!r}")

    d1, d0 = 1.0 - r1, 1.0 - r0
    ok = np.abs(d0) > 1e-14
    rho = np.where(ok, d1 / np.where(ok, d0, 1.0), 1.0)
    rho = np.clip(np.nan_to_num(rho, nan=1.0), 0.0, 1.0)
    rA = np.clip(1.0 - rho * d1, -1.0, 1.0)
    rB = np.clip(1.0 - rho * rho * d1, -1.0, 1.0)
    n1 = A * rA
    return n1.reshape(shape), (n1 * rB).reshape(shape)


def close_i(J, l, i_max, mode="ratio"):
    """격자 J 에 (l, i_max+1), (l, i_max+2) 를 채워 넣는다 (제자리)."""
    n1, n2 = predict(J, l, i_max, mode)
    shape = np.asarray(J[(l, i_max)]).shape
    J[(l, i_max + 1)] = float(n1) if shape == () else n1
    J[(l, i_max + 2)] = float(n2) if shape == () else n2
    return J


MODES = ("frozen", "ratio", "ratio_scalar", "zero",
         "phys_sqrt", "phys_5w", "phys_interp")


# ═══════════════════════════════════════ L2 · 물리적 비 (문헌 처방)
#
# 원논문은 비를 데이터에서 추정하지 말고 **상태방정식 w 에서** 주라고 한다:
#     초기  r ≈ (3w)^{1/2}     후기  r ≈ 5w
#     보간  r = (5/3)^{S/(S+200)} (3w)^{(S+2)/(S+4)}     (S = 스케일인자)
# 그리고 이 조건이 "frame-invariant to the order of our velocity-weight truncation"
# 이라고 단서를 단다 — L1 에서 프레임 효과가 **tilt 오염도**로 드러남을 확인했으므로,
# 그 단서가 실제 이득인지 여기서 잰다.
#
# ★ 측정으로 확인한 사실 (정확 구적, `physical_ratio_table`):
#   · l=0 의 비는 **정의상 정확히 3w** 다 (J^(1) ≡ 3p) — 잴 것이 없다.
#   · l=2 의 비는 상대론 영역에서 **√(3w) 와 4자리 일치** (w=0.32 에서 α=0.5003).
#   · w 가 작아지면 지수 α 가 0.50 → 0.82 로 올라간다 (문헌의 1/2→1 방향과 일치,
#     다만 우리 범위에서는 1 에 닿지 않는다).
#   · l=1 은 α ≈ 0.89~1.08 로 처음부터 1 근처다 — **l 마다 다르다**.
#     단일 r 처방은 그 자체로 근사다 (r_l = ⟨v^{l+2}⟩/⟨v^l⟩ 이므로 l 의존).
#
# ★ 우리 배경에는 k-모드가 없다는 점도 정직하게 적어 둔다: 논문의 5w 는 큰 스케일에서
#   **절단된 계층의 해**라는 동역학적 진술이지 배경 분포의 모멘트비가 아니다.
#   그래서 `attractor_ratio()` 로 동역학적 형태를 따로 잰다.
def w_from_state(J):
    """상태에서 w = p/ρ = J^(1)_{l=0} / (3 J^(0)_{l=0}) — 솔버가 이미 아는 값."""
    rho = float(np.atleast_1d(np.asarray(J[(0, 0)], float)).ravel()[0])
    j1 = float(np.atleast_1d(np.asarray(J[(0, 1)], float)).ravel()[0])
    return j1 / (3.0 * rho) if abs(rho) > _TINY else 0.0


def physical_ratio(w, mode="phys_sqrt"):
    """★ w 에서 비를 **계산**한다 (데이터 추정이 아니다).

    phys_sqrt   : r = (3w)^{1/2}   — 초기(상대론) 처방.  무질량 w=1/3 에서 **정확히 1**
                  이라 우리가 아는 축퇴와 맞는다.
    phys_5w     : r = 5w           — 후기 처방.  무질량에서 5/3 이라 축퇴와 **어긋난다**.
    phys_interp : r = (5/3)^{1−3w} (3w)^{(2−3w)/2}
                  3w→1 에서 1, 3w→0 에서 5w 로 가는 무매개변수 보간.
                  ★ 논문은 스케일인자 S 로 보간하는데 우리 배경에는 대응물이 없어
                    **3w 자체로 보간**했다 — 우리 선택임을 명시한다.
    """
    t = max(3.0 * float(w), 0.0)
    if mode == "phys_sqrt":
        return float(np.sqrt(t))
    if mode == "phys_5w":
        return float(5.0 * w)
    if mode == "phys_interp":
        if t <= 0.0:
            return 0.0
        return float((5.0 / 3.0) ** (1.0 - t) * t ** ((2.0 - t) / 2.0))
    raise ValueError(f"unknown physical mode: {mode!r}")


# ═══════════════════════════════════════ ★ J̇ 닫힘 (L3 의 본 수확)
#
# 측정으로 드러난 사실: **J 닫힘을 정확하게 만들어도 궤적은 좋아지지 않는다.**
#   m=1, i_max=2 에서 i_max+1,+2 를 **정확 구적**으로 채워 넣어도
#   ρ 4.6e−5 → 5.5e−5 (오히려 나쁨), q 6.2e−5 → 4.8e−5, π 2.0e−4 → 1.3e−4.
# 반면 i_max 를 1→4 로 올리면 100배 좋아진다.  ⇒ 한계는 **J 값**이 아니라
# 상태를 하나 더 두는 것, 즉 그 상태의 **J̇** 다.
#
# 실제 결함: (div-free) 가 (l,i) ← (l−1,i+1) 로 결합하므로 i=i_max 에서 격자 밖
# J̇ 이 필요한데 **그것만 0 으로 버려왔다**.  J 는 닫힘으로 채우면서 J̇ 은 버리니
# **닫힘이 J 와 J̇ 사이에서 불일치**한다.  같은 비 r 을 J̇ 에도 적용하면 일관된다:
#
#       J^(i_max+1) = r · J^(i_max)   ⇒   J̇^(i_max+1) ≈ r · J̇^(i_max)
#
# 무질량이면 r ≡ 1 이라 정확한 축퇴를 재현한다 (1차원 환원과 같은 내용).
def jdot_ratio(J, l_max, i_max, mode="frozen"):
    """J̇ 닫힘에 쓸 비 r_l — J 닫힘과 **같은 비**를 돌려준다 (성분별 배열).

    반환 dict{l: array(shape (3,)*l)}.  `tilted_mass.matvec(i_ratio=...)` 에 넣는다.
    """
    out = {}
    for l in range(l_max + 1):
        shape = np.asarray(J[(l, i_max)]).shape
        A = np.atleast_1d(np.asarray(J[(l, i_max)], float))
        if mode == "zero":
            out[l] = np.zeros(A.shape).reshape(shape)
            continue
        if mode.startswith("phys_"):
            r = np.full(A.shape, physical_ratio(w_from_state(J), mode))
        elif mode == "frozen" or i_max < 2:
            r = _safe_ratio(A, J[(l, i_max - 1)])
        elif mode == "ratio":
            r1 = _safe_ratio(A, J[(l, i_max - 1)])
            r0 = _safe_ratio(J[(l, i_max - 1)], J[(l, i_max - 2)])
            d1, d0 = 1.0 - r1, 1.0 - r0
            ok = np.abs(d0) > 1e-14
            rho = np.clip(np.nan_to_num(
                np.where(ok, d1 / np.where(ok, d0, 1.0), 1.0), nan=1.0), 0.0, 1.0)
            r = np.clip(1.0 - rho * d1, -1.0, 1.0)
        elif mode == "ratio_scalar":
            r = np.full(A.shape, _norm_ratio(A, J[(l, i_max - 1)]))
        else:
            raise ValueError(f"unknown closure mode: {mode!r}")
        out[l] = np.asarray(r, float).reshape(shape)
    return out


# ═══════════════════════════════════════ 진단: 구조를 가정하지 않고 측정
def exact_ratio_sequence(mass, l=0, i_max=5, a_vec=(1.0, 0.9, 1.2),
                         v=(0.08, -0.05, 0.12)):
    """★ r_i = |J^(i+1)|/|J^(i)| 를 **정확 구적**에서 뽑는다.

    무질량이면 전부 1, 유질량이면 **단조 증가**해야 한다 (Hausdorff 구조).
    """
    from bianchi.matter import tilted_moments as TM
    js = [np.abs(np.atleast_1d(np.asarray(
        TM.J_moment_tilted(a_vec, v, mass, l, i), float))).max()
        for i in range(i_max + 2)]
    return [js[i + 1] / max(js[i], _TINY) for i in range(i_max + 1)]


def closure_prediction_error(mass, l=0, i_max=2, mode="ratio",
                             a_vec=(1.0, 0.9, 1.2), v=(0.08, -0.05, 0.12)):
    """★ **ODE 없이** 닫힘 자체의 정확도: 정확한 i≤i_max 를 주고 i_max+1, +2 를 예측.

    반환 dict(e1, e2) — ρ 로 정규화된 최대 성분오차.
    ★ 적분 오차와 분리해서 재기 때문에 닫힘 개선을 **단독으로** 판정할 수 있다.
    """
    from bianchi.matter import tilted_moments as TM

    def J(i):
        return np.atleast_1d(np.asarray(
            TM.J_moment_tilted(a_vec, v, mass, l, i), float))

    grid = {(l, i): J(i).reshape((3,) * l) for i in range(i_max + 1)}
    n1, n2 = predict(grid, l, i_max, mode)
    sc = max(float(np.abs(J(0)).max()), _TINY)
    return dict(
        e1=float(np.abs(np.atleast_1d(n1).ravel() - J(i_max + 1).ravel()).max() / sc),
        e2=float(np.abs(np.atleast_1d(n2).ravel() - J(i_max + 2).ravel()).max() / sc))


def closure_comparison(masses=(0.0, 0.5, 1.0, 2.0, 4.0), ls=(0, 1, 2), i_max=2,
                       modes=("frozen", "ratio")):
    """모드별 예측오차 표 — 개선을 **주장하지 않고 표로 보인다**."""
    rows = []
    for m in masses:
        for l in ls:
            r = {md: closure_prediction_error(m, l, i_max, md) for md in modes}
            rows.append((m, l, r))
    return rows


# ═══════════════════════════════════════ L2 진단
def exact_ratio_vs_w(masses=(0.0, 0.5, 1.0, 2.0, 3.0, 5.0, 8.0, 15.0, 30.0, 60.0),
                     l=2, a_vec=(1.0, 0.85, 1.18)):
    """★ 정확 구적의 비 r_l 과 w 를 함께 재서 문헌 두 공식과 대조한다.

    반환 [(m, w, r_l, √(3w), 5w, α)] — α 는 r_l = (3w)^α 의 유효 지수.
    ★ l=0 은 넣지 말 것: J^(1) ≡ 3p 이므로 r₀ = 3w 가 **정의상 항등식**이다.
    """
    from bianchi.matter import hierarchy as HH
    out = []
    for m in masses:
        rho = HH.J_moment(a_vec, m, 0, 0)
        w = HH.J_moment(a_vec, m, 0, 1) / (3.0 * rho)
        kw = dict(f0=HH.f_dipole(0.3, 2)) if l % 2 else {}
        j0 = np.abs(np.atleast_1d(np.asarray(HH.J_moment(a_vec, m, l, 0, **kw), float))).max()
        j1 = np.abs(np.atleast_1d(np.asarray(HH.J_moment(a_vec, m, l, 1, **kw), float))).max()
        r = j1 / max(j0, _TINY)
        t = 3.0 * w
        al = float(np.log(r) / np.log(t)) if 0 < t < 1 and r > 0 else float("nan")
        out.append((float(m), float(w), float(r), float(np.sqrt(t)), float(5 * w), al))
    return out


def formula_crossover(l=1, a_vec=(1.0, 0.85, 1.18),
                      masses=(0.5, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 12.0, 15.0,
                              30.0, 60.0)):
    """★ √(3w) 와 5w 중 어느 쪽이 맞는지 뒤바뀌는 지점을 **스캔으로** 찾는다.

    ★ 처음에 **절대오차 + 이분법**으로 짰다가 틀렸다: l=2 에서 술어가 단조가 아니라
      (w≈0.10 에서 5w 로 갔다가 w≈0.08 에서 다시 √3w 로 돌아온다) 이분법이 첫 교차만
      잡고 나머지를 놓쳤다.  **상대오차 |r/식 − 1|** 로 바꾸고 스캔으로 전수 확인한다.

    반환 dict(rows, flips) — rows = [(w, r, 5w 상대오차, √3w 상대오차, 승자)].
    """
    from bianchi.matter import hierarchy as HH
    rows, flips, prev = [], [], None
    for m in masses:
        rho = HH.J_moment(a_vec, m, 0, 0)
        w = HH.J_moment(a_vec, m, 0, 1) / (3.0 * rho)
        kw = dict(f0=HH.f_dipole(0.3, 2)) if l % 2 else {}
        j0 = np.abs(np.atleast_1d(np.asarray(HH.J_moment(a_vec, m, l, 0, **kw), float))).max()
        j1 = np.abs(np.atleast_1d(np.asarray(HH.J_moment(a_vec, m, l, 1, **kw), float))).max()
        r = j1 / max(j0, _TINY)
        e5, es = abs(r / (5 * w) - 1), abs(r / np.sqrt(3 * w) - 1)
        win = "5w" if e5 < es else "sqrt3w"
        if prev is not None and win != prev:
            flips.append(float(w))
        prev = win
        rows.append((float(w), float(r), float(e5), float(es), win))
    return dict(rows=rows, flips=flips, n_flips=len(flips))


def ratio_is_l_dependent(masses=(1.0, 3.0, 8.0, 30.0), a_vec=(1.0, 0.85, 1.18)):
    """★★ **단일 r 처방의 한계를 정량화**: r_l = ⟨v^{l+2}⟩/⟨v^l⟩ 이라 l 마다 다르다.

    반환 [(w, r1, r2, r3, r3/r1)] — 마지막 열이 1 에서 멀수록 단일 r 이 부적절하다.
    """
    from bianchi.matter import hierarchy as HH
    out = []
    for m in masses:
        rho = HH.J_moment(a_vec, m, 0, 0)
        w = HH.J_moment(a_vec, m, 0, 1) / (3.0 * rho)
        rs = []
        for l in (1, 2, 3):
            kw = dict(f0=HH.f_dipole(0.3, 2)) if l % 2 else {}
            j0 = np.abs(np.atleast_1d(np.asarray(HH.J_moment(a_vec, m, l, 0, **kw), float))).max()
            j1 = np.abs(np.atleast_1d(np.asarray(HH.J_moment(a_vec, m, l, 1, **kw), float))).max()
            rs.append(j1 / max(j0, _TINY))
        out.append((float(w), rs[0], rs[1], rs[2], rs[2] / rs[0]))
    return out


def attractor_ratio(mass=1.0, n_star=3, t_end=0.6, nsteps=60, v0=(0.06, -0.04, 0.09)):
    """★★ 논문의 **동역학적** 주장: n_*=3 절단에서 J^(1)_a ≈ r J^(0)_a 가 해다.

    ★ 우리 배경에는 k-모드가 없다 — 즉 **큰 스케일 극한 그 자체**라 논문의 조건이
      자동 충족된다.  그래서 이 주장은 여기서 곧바로 시험할 수 있다.
    반환 [(t, r_dyn, 5w, √(3w), r_exact)].
    """
    from bianchi.matter import tilted_integrate as TI
    from bianchi.matter import tilted_moments as TM
    bg = TI.Background(v0=v0)
    h = TI.integrate(bg, mass, t_end, nsteps, l_max=3, i_max=1, n_star=n_star)
    out = []
    for k in range(0, nsteps + 1, max(1, nsteps // 4)):
        t, J = h["t"][k], h["J"][k]
        rho = float(J[(0, 0)])
        w = float(J[(0, 1)]) / (3.0 * rho)
        j0 = np.asarray(J[(1, 0)], float)
        j1 = np.asarray(J.get((1, 1), np.zeros(3)), float)
        msk = np.abs(j0) > 1e-10 * np.abs(j0).max()
        rd = float(np.median(j1[msk] / j0[msk])) if msk.any() else float("nan")
        a, v = bg.a(t), bg.v(t)
        e0 = np.abs(np.asarray(TM.J_moment_tilted(a, v, mass, 1, 0), float)).max()
        e1 = np.abs(np.asarray(TM.J_moment_tilted(a, v, mass, 1, 1), float)).max()
        out.append((float(t), rd, float(5 * w), float(np.sqrt(3 * w)), float(e1 / e0)))
    return out


def closure_mode_comparison(masses=(0.5, 1.0, 3.0), v_mag=0.15, t_end=0.2, nsteps=20,
                            l_max=3, i_max=3,
                            modes=("frozen", "ratio", "phys_sqrt", "phys_interp",
                                   "phys_5w")):
    """★ 모드별 (v=0 오차, tilt 오차, 오염비) — 물리 처방이 실제로 이득인지 **측정**."""
    from bianchi.matter import tilted_integrate as TI
    rows = []
    for m in masses:
        for md in modes:
            e0 = max(TI.trajectory_error(TI.Background(v0=(0.0, 0.0, 0.0)), m, t_end,
                                         nsteps, l_max, i_max, mode=md).values())
            s = float(v_mag)
            ev = max(TI.trajectory_error(TI.Background(v0=(s, -0.6 * s, 1.5 * s)), m,
                                         t_end, nsteps, l_max, i_max, mode=md).values())
            rows.append((float(m), md, e0, ev, (ev - e0) / e0))
    return rows

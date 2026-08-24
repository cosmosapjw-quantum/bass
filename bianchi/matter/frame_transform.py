"""
L1 · **프레임 변환식과 삼각절단의 홀짝 불변성** — 문헌의 미검증 예측을 시험한다.

원논문 (Lewis & Challinor, astro-ph/0203507) 은 fiducial velocity 를 바꿀 때

    J^(i)_{A_l} → J^(i)_{A_l} − ⅓ δ_{l1} v_{a₁}[(3+2i)J^(i) + (1−2i)J^(i+1)]      (trans)

라 적고, 이로부터 **"절단조건 J=0 for l+2i > n_* 는 n_* 가 홀수일 때만 (선형차수에서)
프레임 불변"** 이라는 결론을 낸다.  우리 프로젝트에는 boosted 정확 구적이 있으므로
이 식과 결론을 **검증할 수 있다** — 지금까지 아무도 확인하지 않은 항목이다.

★★ 측정 결과 1 — **논문 식은 우리 배경에서 불완전하다** (그리고 그 이유가 분명하다).
  분포족 10종에 걸쳐 dJ̃/dv 를 정확 구적에서 재고 소스 기저에 최소제곱을 걸면,
  논문의 두 항만으로는 i ≥ 1 에서 잔차가 2e−2 로 남는다.  **l=2 항 두 개**를 넣으면
  잔차가 3e−12 로 떨어지고 계수가 전부 깔끔한 유리수로 나온다:

      J̃^(i)_a = J^(i)_a − ⅓v_a[(3+2i)J^(i) + (1−2i)J^(i+1)]
                        − 2i · J^(i−1)_{ab}v^b + (2i−1) · J^(i)_{ab}v^b

  ★ 논문 식이 틀린 게 아니다 — **선형섭동론**에서는 π_ab 가 1차라 π·v 가 2차로
    떨어진다.  Bianchi 배경에서는 π_ab 가 **0차**이므로 같은 차수로 살아난다.
    (i=0 에서는 −J^(0)_{ab}v^b, 즉 잘 알려진 q̃ = q − (ρ+p)v − π·v.)

★★ 측정 결과 2 — **홀짝 결론은 살아남는다** (다만 근거가 넓어진다).
  네 소스의 가중이 전부 n∓1 (n = 1+2i) 이므로, l=1 가중이 홀수라는 사실과 합쳐
  절단 경계에서 이렇게 된다:

      n_* 홀수 → 절단을 넘는 최소 l=1 가중은 n_*+2 ⇒ 소스 가중 n_*+1 도 잘려 있다 ⇒ 불변
      n_* 짝수 → 절단을 넘는 최소 l=1 가중은 n_*+1 ⇒ 소스 가중 n_* 가 **남아 있다** ⇒ 깨짐

  `truncation_leakage()` 가 이것을 수치로 확인한다.
"""
from __future__ import annotations

import numpy as np

from bianchi.matter import hierarchy as H


# ═══════════════════════════════════════ 1. 측정된 변환 계수
def transform_coefficients(i):
    """★ dJ̃^(i)_a/dv 의 소스 계수 — **분포족 최소제곱으로 측정한 값** (인용 아님).

    반환 dict:
        J0_lo  = −(3+2i)/3    (l=0, 가중 n−1)   ← 논문
        J0_hi  = −(1−2i)/3    (l=0, 가중 n+1)   ← 논문
        J2_lo  = −2i          (l=2, 가중 n−1)   ← ★ 논문에 없음
        J2_hi  = +(2i−1)      (l=2, 가중 n+1)   ← ★ 논문에 없음
    측정값 (i=0..3): (−1,−1/3,0,−1), (−5/3,+1/3,−2,+1), (−7/3,+1,−4,+3), (−3,+5/3,−6,+5)
    """
    i = int(i)
    return dict(J0_lo=-(3 + 2 * i) / 3.0, J0_hi=-(1 - 2 * i) / 3.0,
                J2_lo=-2.0 * i, J2_hi=(2.0 * i - 1.0))


def source_weights(i):
    """소스의 속도가중 — 전부 n∓1 (n = 1+2i).  홀짝 논증의 근거."""
    n = 1 + 2 * i
    return dict(J0_lo=n - 1, J0_hi=n + 1, J2_lo=n - 1, J2_hi=n + 1)


def dq_dv(J, i, v_hat, axis=None):
    """측정된 변환식으로 dJ̃^(i)_a/dv 를 계산한다 (J 는 법선틀 모멘트 dict).

    J[(0, i)] = 스칼라, J[(2, i)] = (3,3) 배열.  없는 키는 0 으로 본다.
    """
    c = transform_coefficients(i)
    v = np.asarray(v_hat, float)

    def g0(k):
        return float(J.get((0, k), 0.0))

    def g2(k):
        return np.asarray(J.get((2, k), np.zeros((3, 3))), float)

    out = (c["J0_lo"] * g0(i) + c["J0_hi"] * g0(i + 1)) * v
    out = out + (c["J2_lo"] * g2(i - 1) + c["J2_hi"] * g2(i)) @ v
    return out if axis is None else float(out[axis])


# ═══════════════════════════════════════ 2. ★ 정확 구적과의 교차검증
def exact_dq_dv(a_vec, mass, i, axis=2, f0=None, h=1e-5):
    """boosted 정확 구적을 v 로 유한차분한 dJ̃^(i)_a/dv (독립 경로)."""
    from bianchi.matter import freestream as fs
    from bianchi.matter import tilted_moments as TM
    f0 = fs.f_fermi_dirac if f0 is None else f0

    def q(v):
        vv = np.zeros(3)
        vv[axis] = v
        return np.asarray(TM.J_moment_tilted(a_vec, vv, mass, 1, i, f0), float)[axis]

    return (q(h) - q(-h)) / (2 * h)


def transform_residual(a_vec=(1.0, 0.85, 1.18), mass=1.0, i=1, axis=2, f0=None):
    """★★ 두 경로 대조: 측정된 변환식 vs 정확 구적 유한차분.  ρ 로 규격화."""
    from bianchi.matter import freestream as fs
    f0 = fs.f_fermi_dirac if f0 is None else f0
    J = {(0, k): H.J_moment(a_vec, mass, 0, k, f0) for k in range(-1, i + 3)}
    J.update({(2, k): H.J_moment(a_vec, mass, 2, k, f0) for k in range(-1, i + 3)})
    v = np.zeros(3)
    v[axis] = 1.0
    pred = dq_dv(J, i, v, axis)
    ex = exact_dq_dv(a_vec, mass, i, axis, f0)
    rho = H.J_moment(a_vec, mass, 0, 0, f0)
    return dict(predicted=pred, exact=ex, residual=abs(pred - ex) / rho)


def paper_only_residual(a_vec=(1.0, 0.85, 1.18), mass=1.0, i=1, axis=2, f0=None):
    """★ **논문의 두 항만** 쓰면 얼마나 어긋나는가 (l=2 항의 필요성을 정량화)."""
    from bianchi.matter import freestream as fs
    f0 = fs.f_fermi_dirac if f0 is None else f0
    c = transform_coefficients(i)
    J0 = H.J_moment(a_vec, mass, 0, i, f0)
    J1 = H.J_moment(a_vec, mass, 0, i + 1, f0)
    pred = c["J0_lo"] * J0 + c["J0_hi"] * J1
    ex = exact_dq_dv(a_vec, mass, i, axis, f0)
    rho = H.J_moment(a_vec, mass, 0, 0, f0)
    return dict(paper_only=pred, exact=ex, residual=abs(pred - ex) / rho)


def fit_coefficients(i, family=None, axis=2, h=1e-5):
    """★ 계수를 **다시 맞춰 본다** (하드코딩이 측정과 일치하는지 회귀로 확인).

    소스 기저에 가중 n±3 항을 **대조군**으로 넣어 0 이 나오는지도 본다.
    반환 dict(coef, control, residual).
    """
    from bianchi.matter import freestream as fs
    fam = family or [((1.0, 0.85, 1.18), 0.0, fs.f_fermi_dirac),
                     ((1.0, 0.85, 1.18), 1.0, fs.f_fermi_dirac),
                     ((1.0, 0.60, 1.40), 0.0, fs.f_fermi_dirac),
                     ((1.0, 0.60, 1.40), 2.0, fs.f_fermi_dirac),
                     ((1.0, 1.30, 0.80), 0.5, fs.f_bose_einstein),
                     ((1.2, 0.90, 1.05), 3.0, fs.f_bose_einstein),
                     ((1.0, 1.00, 1.00), 1.5, fs.f_fermi_dirac),
                     ((0.9, 1.10, 1.25), 0.8, fs.f_fermi_dirac)]
    M, d, sc = [], [], []
    for a, m, f0 in fam:
        M.append([H.J_moment(a, m, 0, i, f0), H.J_moment(a, m, 0, i + 1, f0),
                  np.asarray(H.J_moment(a, m, 2, i - 1, f0), float)[axis, axis],
                  np.asarray(H.J_moment(a, m, 2, i, f0), float)[axis, axis],
                  H.J_moment(a, m, 0, i - 1, f0) if i >= 1 else 0.0,
                  np.asarray(H.J_moment(a, m, 2, i + 1, f0), float)[axis, axis]])
        d.append(exact_dq_dv(a, m, i, axis, f0, h))
        sc.append(H.J_moment(a, m, 0, 0, f0))
    M, d = np.array(M), np.array(d)
    c, *_ = np.linalg.lstsq(M, d, rcond=None)
    return dict(coef=dict(J0_lo=c[0], J0_hi=c[1], J2_lo=c[2], J2_hi=c[3]),
                control=dict(J0_n_minus_3=c[4], J2_n_plus_3=c[5]),
                residual=float(np.abs(M @ c - d).max() / max(sc)))


# ═══════════════════════════════════════ 3. ★★ 삼각절단의 홀짝 불변성
def triangular_keys(n_star, l_max=None):
    """삼각 절단의 상태집합 {(l, i) : l + 2i ≤ n_*, i ≥ 0}."""
    lm = n_star if l_max is None else min(int(l_max), int(n_star))
    return [(l, i) for l in range(lm + 1) for i in range(0, (n_star - l) // 2 + 1)]


def truncation_leakage(n_star, a_vec=(1.0, 0.85, 1.18), mass=1.0, axis=2, f0=None):
    """★★ **핵심 측정**: 절단된 상태를 무한소 boost 하면 금지영역으로 얼마나 새는가.

    절단조건은 "l+2i > n_* 인 모멘트는 0" 이다.  boost 는 l=1 행에 소스를 주는데,
    그 소스들의 가중이 n∓1 이므로 **남아 있는 소스가 있으면** 금지영역의 l=1 모멘트가
    0 이 아니게 된다 (= 프레임 불변성 깨짐).

    반환 dict(leak, worst_key, retained_sources) — leak 은 ρ 로 규격화.
    예측: n_* 홀수 → 0,  n_* 짝수 → O(1).
    """
    from bianchi.matter import freestream as fs
    f0 = fs.f_fermi_dirac if f0 is None else f0
    keep = set(triangular_keys(n_star))
    rho = H.J_moment(a_vec, mass, 0, 0, f0)
    # 절단된 상태: 남아 있는 것만 실제 값, 나머지는 0
    J = {}
    for l in (0, 2):
        for k in range(-1, n_star + 4):
            J[(l, k)] = (H.J_moment(a_vec, mass, l, k, f0) if (l, k) in keep
                         else (0.0 if l == 0 else np.zeros((3, 3))))
    v = np.zeros(3)
    v[axis] = 1.0
    leak, worst, srcs = 0.0, None, []
    for i in range(0, n_star + 3):
        n = 1 + 2 * i
        if n <= n_star:
            continue                                   # 금지영역만 본다
        d = np.asarray(dq_dv(J, i, v), float)
        m = float(np.abs(d).max() / rho)
        if m > leak:
            leak, worst = m, (1, i)
        if m > 1e-14:
            srcs.append((i, [k for k, w in source_weights(i).items() if w <= n_star]))
    return dict(leak=leak, worst_key=worst, retained_sources=srcs,
                n_star=int(n_star), parity="odd" if n_star % 2 else "even")


def parity_table(n_stars=(2, 3, 4, 5, 6, 7), **kw):
    """★ n_* 홀짝 표 — 예측(홀수 0 / 짝수 O(1))이 실제로 나오는지."""
    return [(int(n), truncation_leakage(n, **kw)["leak"]) for n in n_stars]


# ═══════════════════════════════════════ 4. 동역학적 시험 (궤적)
#
# ★ 주의 — §3 의 누출은 **틀을 바꿀 때** 절단이 보존되는가의 문제다.  고정된 틀에서
#   정확 구적과 대조하는 궤적오차는 그것과 **다른 양**이다.  실제로 궤적오차만 보면
#   홀짝 계단이 보이지 않고 n_* 수렴만 보인다 (m=1, T=0.2):
#       n_* = 2,3,4,5,6,7 → 1.4e−2, 1.5e−2, 3.0e−3, 2.5e−3, 6.9e−4, 5.4e−4
#   ⇒ "홀짝 계단이 궤적오차에 보인다" 는 순진한 기대는 **반증**된다.
#
# ★★ 올바른 동역학적 시험은 **tilt 를 켰을 때의 오염**이다.  측정 (m=1, T=0.2):
#       n_*   v=0        v=0.15      오염비
#        2   1.5435e−2  1.4886e−2   −0.14      (짝)
#        3   1.5435e−2  1.3117e−2   −0.04      (홀)
#        4   2.8881e−3  3.8741e−3   **+0.34**  (짝)
#        5   2.8881e−3  2.6079e−3   −0.10      (홀)
#        6   7.8863e−4  1.6971e−3   **+1.15**  (짝)
#        7   7.8863e−4  1.2065e−3   +0.53      (홀)
#   ⇒ **v=0 에서는 짝·홀이 정확히 같고** (법선틀에서 홀수 l 이 0 이라 추가 상태가
#     아무것도 안 한다), **tilt 를 켜야 비로소 홀수가 낫다** (1.1–1.5배).
#     문헌 예측이 확인되지만 크기는 "계단" 이 아니라 **유한 배수**다 — 정직하게 적는다.
def parity_trajectory_table(n_stars=(2, 3, 4, 5), mass=1.0, v_mag=0.15, t_end=0.2,
                            nsteps=20):
    """★ n_* 별로 (v=0 오차, tilt 오차, 오염비) — 홀짝 효과를 **틀 의존성으로** 본다."""
    from bianchi.matter import tilted_integrate as TI
    out = []
    for ns in n_stars:
        lm, im = min(int(ns), 4), int(ns) // 2
        s = float(v_mag)
        e0 = max(TI.trajectory_error(TI.Background(v0=(0.0, 0.0, 0.0)), mass, t_end,
                                     nsteps, lm, im, n_star=ns).values())
        ev = max(TI.trajectory_error(TI.Background(v0=(s, -0.6 * s, 1.5 * s)), mass,
                                     t_end, nsteps, lm, im, n_star=ns).values())
        out.append((int(ns), e0, ev, (ev - e0) / e0))
    return out


def zero_tilt_parity_degeneracy(n_even=4, mass=1.0, t_end=0.2, nsteps=20):
    """★★ v = 0 에서 n_* 와 n_*+1 (짝→홀) 이 **정확히 같은 답**을 준다.

    법선틀에서는 홀수 l 이 항등적으로 0 이므로 가중 n_*+1 상태를 더해도 아무것도
    바뀌지 않는다.  ⇒ 홀짝 차이는 **오직 tilt 를 켤 때만** 나타난다.
    """
    from bianchi.matter import tilted_integrate as TI
    bg = TI.Background(v0=(0.0, 0.0, 0.0))
    a = TI.trajectory_error(bg, mass, t_end, nsteps, min(n_even, 4), n_even // 2,
                            n_star=n_even)
    b = TI.trajectory_error(bg, mass, t_end, nsteps, min(n_even + 1, 4),
                            (n_even + 1) // 2, n_star=n_even + 1)
    gap = max(abs(a[k] - b[k]) / max(a[k], 1e-300) for k in a)
    return dict(even=a, odd=b, gap=float(gap))

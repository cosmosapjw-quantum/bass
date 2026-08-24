"""
D1c · **Gauss 사상 통계** — Mixmaster 혼돈의 보편 상수를 앙상블로 잰다.

D1b/R4 는 궤적 **하나**의 u 수열이 BKL 사상을 따름을 보였다 (튐당 0.3 ms).  여기서는
초기조건 **앙상블**로 사상의 통계적 보편량을 측정한다:

    에라 사상  x ↦ frac(1/x)  (Gauss 사상)          x = 에라의 소수부분
    불변밀도   ρ_G(x) = 1/((1+x) ln 2)
    Lyapunov  λ = ⟨2 ln(1/x)⟩_G = π²/(6 ln 2) = 2.3731382…
    digit 분포 (Gauss–Kuzmin)  P(a=k) = log₂(1 + 1/(k(k+2)))
    Khinchin  기하평균 a → K₀ = 2.6854520…

★ 에라 분해에 floor() 가 없다: 에라의 끝 에폭은 u ∈ (1,2) 이므로 **x = u_끝 − 1** 로
  읽고, digit 은 에폭 개수를 **센다**.  (u_시작 = a+x 에서 x = frac(u) 로 읽으면 u 가
  정수 근처일 때 ODE 오차 1e−4 로 digit 이 뒤집히는 함정이 있다 — 피했다.)

★ 에라-시작 u 의 정상밀도는 ρ_G 에서 **유도**했고 자기검증했다:
      P(a=k, x∈dx) = μ_G{x′: floor(1/x′)=k, frac(1/x′)∈dx} = dx/(ln2·(k+x)(k+x+1))
  ⇒ 에라-시작 u 밀도 = 1/(ln2·u(u+1)),  ∫₁^∞ = 1 ✓,  구간 [k,k+1) 질량 = Gauss–Kuzmin ✓.
  같은 계산이 **에폭 풀링의 함정**도 준다: 에라 (a,x) 의 에폭 u = j+x (j=1..a) 를 전부
  풀면 x-주변밀도 ∝ Σ_j 1/(j+x) 가 **발산** — 에폭당 풀링은 정상분포가 없고 유한
  표본에서는 검열에 지배된다.  그래서 통계는 전부 **에라당 1 표본**이다.

★★ 세 경로 구조 (검열을 분리하기 위해):
    ① ODE (Rust R4 커널)      — 물리.  τ·에폭 예산과 벽 바닥 때문에 **검열**된다.
    ② 미러 (사상 + 같은 예산)  — ①과 같은 프로토콜로 순수 산술 사상을 검열.
    ③ 무검열 사상             — 닫힌형에 수렴하는 기준.
  ③↔닫힌형 이 이론을, ①↔② 가 "ODE 가 사상이다" 를, ②↔③ 차가 **검열 편향 자체**를
  각각 잰다.  측정 (500 궤적, 씨앗 7):
      λ:      ① 2.4358±0.066   ② 2.4035   ③ 2.3716   (이론 2.3731)
      digit1: ① 0.5230          ② 0.5549   ③ 0.4157   (GK 0.4150)
      K:      ① 1.7153          ② 1.6074   ③ 2.6831   (K₀ 2.6854)
  ⇒ 검열은 digit-1 을 **과잉**, 꼬리와 K 를 **결핍**시킨다 (예산 안에 끝나는 에라가
    짧은 에라 쪽으로 길이-편향).  ①의 λ/밀도는 편향이 잡음 아래라 닫힌형에 직접
    게이트하고, digit/K 는 ②로 게이트하며 편향은 숨기지 않고 **측정으로 보고**한다.

★ 초기조건: 에라-시작 정상법칙으로 뽑는다 — x′ ~ μ_G (역CDF: x′ = 2^ξ − 1),
  u₀ = 1/x′.  u₀ > u_cap 은 재추출하고 (검열의 일부로 계수) **첫 에라는 통계에서
  버린다** (u₀ 절단의 잔류 편향은 한 사상걸음의 Wirsing 혼합 ~0.30 배로 준다).
"""
from __future__ import annotations

import numpy as np

from bianchi.analysis import mixmaster as MX

LN2 = float(np.log(2.0))
#: Gauss 사상의 Lyapunov 지수 (에라당) — π²/(6 ln 2)
LYAPUNOV = float(np.pi ** 2 / (6.0 * LN2))
#: Khinchin 상수 (digit 기하평균의 a.e. 극한)
KHINCHIN = 2.685452001065306
#: Wirsing 상수 — Gauss–Kuzmin–Wirsing 전달연산자의 둘째 고유값 (혼합률)
WIRSING = 0.3036630029


# ═══════════════════════════════════════ 닫힌형
def gauss_density(x):
    """불변밀도 ρ_G(x) = 1/((1+x) ln2)."""
    return 1.0 / ((1.0 + np.asarray(x, float)) * LN2)


def gauss_cdf(x):
    """F_G(x) = log₂(1+x)."""
    return np.log2(1.0 + np.asarray(x, float))


def sample_gauss(rng, n):
    """정상측도에서 정확 표본 — 역CDF: x = 2^ξ − 1."""
    return 2.0 ** rng.random(n) - 1.0


def gauss_kuzmin(k):
    """P(digit = k) = log₂(1 + 1/(k(k+2)))."""
    k = np.asarray(k, float)
    return np.log2(1.0 + 1.0 / (k * (k + 2.0)))


def digit_tail(kmin):
    """P(digit ≥ k) = log₂(1 + 1/k)  (망원합)."""
    return np.log2(1.0 + 1.0 / float(kmin))


def era_start_u_density(u):
    """에라-시작 u 의 정상밀도 1/(ln2·u(u+1)) — ρ_G 에서 유도 (모듈 서두)."""
    u = np.asarray(u, float)
    return 1.0 / (LN2 * u * (u + 1.0))


def gauss_map(x):
    """x ↦ frac(1/x)  (성분별)."""
    y = 1.0 / np.asarray(x, float)
    return y - np.floor(y)


# ═══════════════════════════════════════ 에라 분해 (u 수열 → 에라)
def consistent_prefix(us, tol=0.02):
    """★ BKL 사상을 한 걸음씩 만족하는 접두부 길이 — 그 뒤는 **아무것도 믿지 않는다**.

    D1b 가 보인 대로 벽이 에라마다 기하급수로 죽어 바닥(1e−13)에 닿으면 튐 검출이
    병리적 행(예: u 52 대신 24)을 낼 수 있다.  국소 사상잔차가 tol 을 넘는 첫 지점에서
    자른다.  (잔차 중앙값 실측 8e−9 — tol=0.02 는 여유 6자릿수.)
    """
    k = 1
    while k < len(us):
        u, un = us[k - 1], us[k]
        if u >= 2.0:
            exp = u - 1.0
        elif u > 1.0 + 1e-12:
            exp = 1.0 / (u - 1.0)
        else:
            break
        if abs(un - exp) / max(1.0, abs(exp)) > tol:
            break
        k += 1
    return k


def eras_from_u(us, tol=0.02, drop_first=True):
    """u 수열 → [(u_시작, digit, x)], 미완 꼬리 여부.

    끝 에폭 u<2 에서 **x = u−1** (floor 없음), digit = 에폭 개수 (센다).
    `drop_first` 면 첫 에라(초기조건이 만든 것)를 버린다.
    """
    us = list(us)[:consistent_prefix(us, tol)]
    eras, run = [], []
    for u in us:
        run.append(u)
        if u < 2.0:
            eras.append((run[0], len(run), u - 1.0))
            run = []
    if drop_first and eras:
        eras = eras[1:]
    return eras, bool(run)


# ═══════════════════════════════════════ ① ODE 앙상블 (Rust R4)
def sample_start_u(rng, cap=12.0):
    """에라-시작 정상법칙 u₀ = 1/x′, x′~μ_G — cap 초과는 재추출 (횟수 반환)."""
    rej = 0
    while True:
        u0 = 1.0 / (2.0 ** rng.random() - 1.0)
        if u0 <= cap:
            return float(u0), rej
        rej += 1


def ode_ensemble(n_traj=500, seed=7, wall=1e-2, n_bounce=48, tau_max=1500.0,
                 cap=12.0, kind="IX", tol=0.02, walls="linear"):
    """★★ Rust 커널로 n_traj 궤적을 굴려 에라 통계를 모은다.

    씨앗 wall=1e−2 선택 근거 (실측): 1e−2 가 완결에라/궤적 3.5 로 최다
    (3e−3: 2.8, 1e−3: 2.5) — 통계에는 사상잔차 1e−4 도 충분해서 (추적시험의
    1e−3 게이트와 달리) 벽이 오래 사는 쪽이 이득이다.

    반환 dict(x, digit, u_start[에라], epochs[궤적], censored_tail, rejected_u0).
    """
    rng = np.random.default_rng(seed)
    X, D, U, M = [], [], [], []
    tail = rej_tot = 0
    for _ in range(int(n_traj)):
        u0, rej = sample_start_u(rng, cap)
        rej_tot += rej
        y0, args = MX.mixmaster_ic(u0, wall, kind)
        rows = MX.bounce_sequence(y0, args, n_bounce=n_bounce, tau_max=tau_max,
                                  walls=walls)
        us = [r[2] for r in rows]
        M.append(consistent_prefix(us, tol))
        eras, has_tail = eras_from_u(us, tol)
        tail += has_tail
        for (ust, d, x) in eras:
            U.append(ust)
            D.append(d)
            X.append(x)
    return dict(x=np.asarray(X), digit=np.asarray(D, int), u_start=np.asarray(U),
                epochs=np.asarray(M, int), censored_tail=int(tail),
                rejected_u0=int(rej_tot), n_traj=int(n_traj))


# ═══════════════════════════════════════ ② 미러 (사상 + 같은 검열 프로토콜)
def mirror_ensemble(epoch_budgets, n_traj=4000, seed=11, cap=12.0):
    """★ ①과 같은 프로토콜의 **순수 산술** 사상 앙상블.

    예산은 ODE 가 실제로 준 에폭 수 분포(`epochs`)에서 궤적마다 추출한다.
    ★ 정직한 한계: ODE 의 예산은 **내생적**이다 (큰 digit 이 τ 를 태워 스스로
      끊는다).  주변분포로 뽑으면 그 상관을 놓쳐 ②↔① 이 2~3σ 급으로 남는다
      (실측 digit1 0.555 vs 0.523).  ②는 편향의 **방향과 크기급**을 재현하는
      대조군이지 ①의 정밀 복제가 아니다 — 게이트도 그렇게만 건다.
    """
    rng = np.random.default_rng(seed)
    budgets = np.asarray(epoch_budgets, int)
    X, D = [], []
    tail = 0
    for _ in range(int(n_traj)):
        b = int(budgets[rng.integers(len(budgets))])
        u0, _ = sample_start_u(rng, cap)
        a, xx = int(np.floor(u0)), u0 - np.floor(u0)
        used, first = 0, True
        while used + a <= b:
            used += a
            if not first:
                X.append(xx)
                D.append(a)
            first = False
            y = 1.0 / xx
            a, xx = int(np.floor(y)), float(y - np.floor(y))
        tail += 1 if used < b or first else 0
    return dict(x=np.asarray(X), digit=np.asarray(D, int), censored_tail=int(tail))


# ═══════════════════════════════════════ ③ 무검열 사상
def map_ensemble(n_orbit=200, n_era=1000, seed=13, init="gauss"):
    """정상측도(기본) 또는 균일 초기에서 사상 궤도를 풀링 — 닫힌형의 기준 경로."""
    rng = np.random.default_rng(seed)
    x = sample_gauss(rng, n_orbit) if init == "gauss" else rng.random(n_orbit)
    X, D = [], []
    for _ in range(int(n_era)):
        y = 1.0 / x
        a = np.floor(y)
        x = y - a
        D.append(a.copy())
        X.append(x.copy())
    return dict(x=np.concatenate(X), digit=np.concatenate(D).astype(int))


# ═══════════════════════════════════════ 통계
def ks_to_gauss(xs):
    """경험CDF 대 F_G 의 KS 거리."""
    xs = np.sort(np.asarray(xs, float))
    emp = np.arange(1, len(xs) + 1) / len(xs)
    return float(np.abs(emp - gauss_cdf(xs)).max())


def ks_to_uniform(xs):
    xs = np.sort(np.asarray(xs, float))
    emp = np.arange(1, len(xs) + 1) / len(xs)
    return float(np.abs(emp - xs).max())


def lyapunov_estimate(xs):
    """λ = ⟨2 ln(1/x)⟩ 와 표준오차."""
    w = 2.0 * np.log(1.0 / np.asarray(xs, float))
    return float(w.mean()), float(w.std(ddof=1) / np.sqrt(len(w)))


def khinchin_estimate(digits):
    """digit 기하평균 exp⟨ln a⟩ 와 (로그의) 표준오차."""
    ln = np.log(np.asarray(digits, float))
    return float(np.exp(ln.mean())), float(ln.std(ddof=1) / np.sqrt(len(ln)))


def digit_fractions(digits, kmax=5):
    """관측 digit 분율 [1..kmax] + 꼬리(≥kmax+1)."""
    d = np.asarray(digits, int)
    fr = [float((d == k).mean()) for k in range(1, kmax + 1)]
    return fr, float((d > kmax).mean())


def mixing_decay(n=300000, n_step=5, seed=5):
    """★ 균일 초기 앙상블의 KS(→Gauss) 감쇠 — Wirsing 혼합률의 측정.

    실측 (n=3e5): 0.0866 → 0.0308 → 0.0099 → 0.0042 → 1/√n 바닥.
    첫 비 0.356, 둘째 0.322 — Wirsing 0.3037 로 위에서 접근 (KS 는 여러 고유모드의
    혼합이라 유한 k 에서 조금 크다).  바닥에 닿기 전 비만 의미가 있다.
    """
    rng = np.random.default_rng(seed)
    x = rng.random(int(n))
    ks = [ks_to_gauss(x)]
    for _ in range(int(n_step)):
        x = gauss_map(x)
        ks.append(ks_to_gauss(x))
    return ks


def golden_orbit_lyapunov(n=25):
    """★ 대조군 — 황금비 x = (√5−1)/2 궤도는 digit 이 전부 1, λ_궤도 = 2 ln φ.

    보편값 π²/6ln2 는 **거의 모든** 초기조건의 값이고, 측도 0 궤도는 다르다 —
    추정기가 궤도를 재는 것이지 상수를 내장한 게 아님을 보이는 시험.

    ★★ **반증 기록**: 처음 n=60 으로 돌렸더니 λ = 1.2786, digit 도 1 이 아니었다.
      원인은 시험 대상인 혼돈 그 자체다 — 배정밀도 오차가 스텝마다 |T′| = φ² ≈ 2.618
      배로 커져, n* ≈ ln(1/ε)/(2 ln φ) ≈ 38 스텝에서 궤도가 측도-0 점을 떠나 **전형
      궤도로 돌아간다**.  그래서 (a) λ 추정은 이탈 전(n=25)만 쓰고, (b) 이탈 지점
      자체를 반환해 예측 [30, 45] 와 맞는지 **정량 시험**으로 돌렸다.

    반환 (λ_추정, digit 목록(n개), 이론 2lnφ, 첫 digit≠1 지점 또는 −1).
    """
    phi = (np.sqrt(5.0) - 1.0) / 2.0
    x, w, d = phi, [], []
    first_bad = -1
    for k in range(120):
        y = 1.0 / x
        a = int(np.floor(y))
        if a != 1 and first_bad < 0:
            first_bad = k
        if k < int(n):
            d.append(a)
            w.append(2.0 * np.log(1.0 / x))
        x = float(y - np.floor(y))
    return (float(np.mean(w)), d,
            2.0 * float(np.log((np.sqrt(5.0) + 1.0) / 2.0)), first_bad)

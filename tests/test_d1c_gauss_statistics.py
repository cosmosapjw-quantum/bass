"""
D1c · **Gauss 사상 통계** — Mixmaster 혼돈의 보편 상수를 앙상블로.

세 경로 (검열을 분리한다):
    ① ODE (Rust R4)      ② 미러 (사상 + 같은 에폭예산)      ③ 무검열 사상
측정 (500 궤적 → 통계에라 1130, 꼬리검열 173):
```
λ (이론 2.373138):        ① 2.4358±0.0663   ② 2.4193   ③ 2.3760±0.0049
KS(era-x → Gauss):        ① 0.0256 [임계 0.0405]         ③ 0.0032
digit1 (GK 0.4150):       ① 0.5230           ② 0.5575   ③ 0.4141
Khinchin (K₀ 2.6855):     ① 1.7153           ② 1.5950   ③ 2.6915
```
★ ①/② 의 digit·K 편향은 **검열**(예산 안에 끝나는 에라의 길이-편향)이고, 숨기지
  않고 게이트로 고정한다.  λ·밀도는 편향이 잡음 아래라 닫힌형에 직접 게이트한다.

★★ 반증 기록 (황금비 대조군): n=60 으로 돌렸더니 λ=1.2786, digit≠1 — **시험 대상인
  혼돈이 시험을 먹었다**.  배정밀도 오차가 스텝당 φ²≈2.618 배로 자라 n*≈38 에서
  측도-0 궤도를 떠난다.  실측 이탈 = 37.  λ 는 이탈 전(n=25)만 쓰고, 이탈 지점
  자체를 예측 [30,45] 와 대조하는 시험으로 바꿨다.

★ 에폭 풀링의 함정 (유도 §서두): 에라 (a,x) 의 에폭 a 개가 같은 x 를 공유하므로
  에폭당 풀링의 x-주변밀도는 ∝ Σ_j 1/(j+x) 로 **발산** — 정상분포가 없다.
  실측: KS(풀링→Gauss) 0.110 ≫ KS(에라→Gauss) 0.005, 풀링은 오히려 균일에 가깝다
  (0.080) — "큰 a 조건부 x 는 균일에 가깝다" 는 유도와 방향이 맞는다.
"""
from functools import lru_cache

import numpy as np
import pytest
import scipy.integrate as si

from bianchi.analysis import gauss_map as G
from bianchi.analysis import mixmaster as MX

pytestmark = pytest.mark.skipif(not MX.rust_available(),
                                reason="bianchi_rustcore 없음 (R4 커널 필요)")


@lru_cache(maxsize=1)
def _ode():
    return G.ode_ensemble()          # 기본 인자: 500 궤적, 씨앗 7 — 결정적


@lru_cache(maxsize=1)
def _mirror():
    return G.mirror_ensemble(tuple(_ode()["epochs"]))


@lru_cache(maxsize=1)
def _map():
    return G.map_ensemble()


# ═══════════════════════════════════════ 닫힌형 자기검증
def test_gauss_density_normalizes_and_matches_cdf():
    v, _ = si.quad(G.gauss_density, 0.0, 1.0)
    assert abs(v - 1.0) < 1e-12
    assert abs(G.gauss_cdf(1.0) - 1.0) < 1e-15
    x = 0.37
    h = 1e-6
    assert abs((G.gauss_cdf(x + h) - G.gauss_cdf(x - h)) / (2 * h)
               - G.gauss_density(x)) < 1e-8


def test_inverse_cdf_sampling_is_exact():
    """★ x = 2^ξ − 1 이 μ_G 의 정확 표본 — 초기조건 정상성의 근거."""
    xs = G.sample_gauss(np.random.default_rng(0), 200000)
    assert G.ks_to_gauss(xs) < 1.36 / np.sqrt(len(xs)) * 1.5


def test_era_start_u_density_is_derived_consistently():
    """★★ 유도 자기검증 — 1/(ln2·u(u+1)) 이 정규화되고 [k,k+1) 질량이 GK 와 같다.

    이 밀도는 ρ_G 에서 유도한 것이다 (기억 인용이 아니다) — 유도가 맞으면 구간
    질량이 Gauss–Kuzmin 과 **항등**이어야 한다.
    """
    v, _ = si.quad(G.era_start_u_density, 1.0, np.inf)
    assert abs(v - 1.0) < 1e-10
    for k in (1, 2, 3, 7):
        m, _ = si.quad(G.era_start_u_density, float(k), float(k + 1))
        assert abs(m - float(G.gauss_kuzmin(k))) < 1e-12


def test_gauss_measure_is_invariant_and_uniform_is_not():
    """★ 전달연산자 검증 — μ_G 표본을 사상에 밀어도 μ_G, 균일은 아니다."""
    rng = np.random.default_rng(2)
    x = G.sample_gauss(rng, 200000)
    crit = 1.36 / np.sqrt(len(x))
    assert G.ks_to_gauss(G.gauss_map(x)) < 1.5 * crit
    # 대조군: 균일은 한 걸음으로는 부족 — 한 걸음 뒤 KS ≈ 0.0866·Wirsing ≈ 0.030
    # (측정 0.0296; 통계 임계 0.0030 의 10배 언저리라 절대값으로 게이트)
    u = rng.random(200000)
    assert G.ks_to_gauss(G.gauss_map(u)) > 0.02


# ═══════════════════════════════════════ ③ 무검열 사상 → 닫힌형
def test_map_lyapunov_matches_the_closed_form():
    """★★ λ = π²/(6 ln2) — 무검열 경로 (측정 2.3760±0.0049)."""
    lam, se = G.lyapunov_estimate(_map()["x"])
    assert abs(lam - G.LYAPUNOV) < max(3.5 * se, 0.02)


def test_map_digits_match_gauss_kuzmin():
    fr, tail = G.digit_fractions(_map()["digit"])
    for k in range(1, 6):
        assert abs(fr[k - 1] - float(G.gauss_kuzmin(k))) < 0.01, k
    assert abs(tail - G.digit_tail(6)) < 0.01


def test_map_khinchin_constant():
    """★ 기하평균 → K₀ = 2.6855 (측정 2.6915; ln-SE 로 게이트)."""
    K, se_ln = G.khinchin_estimate(_map()["digit"])
    assert abs(np.log(K) - np.log(G.KHINCHIN)) < max(4.0 * se_ln, 0.02)


def test_mixing_decays_at_the_wirsing_scale():
    """★ 균일 → Gauss 의 KS 감쇠 — 비가 Wirsing 0.3037 로 위에서 접근 (실측 0.36, 0.32)."""
    ks = G.mixing_decay()
    r = [ks[i + 1] / ks[i] for i in range(2)]
    assert all(0.25 < x < 0.48 for x in r), r
    assert ks[3] < ks[0] / 15.0


def test_golden_orbit_is_measure_zero_and_double_precision_leaves_it():
    """★★ **반증을 게이트로** — λ(황금비)=2lnφ≠보편값, 이탈은 예측 스텝 [30,45]."""
    lam, dig, th, bad = G.golden_orbit_lyapunov()
    assert abs(lam - th) < 1e-6
    assert all(d == 1 for d in dig)
    assert 30 <= bad <= 45, bad
    assert abs(th - G.LYAPUNOV) > 1.4          # 보편값과 뚜렷이 다르다


def test_epoch_pooling_has_no_stationary_density():
    """★★ **함정 기록** — 에폭당 풀링(에라 x 를 a 번 반복)은 Gauss 가 아니다.

    유도: 풀링 x-밀도 ∝ Σ_j 1/(j+x) 발산.  실측 KS 0.110 vs 에라당 0.005.
    """
    m = _map()
    pooled = np.repeat(m["x"], m["digit"])
    ks_era, ks_pool = G.ks_to_gauss(m["x"]), G.ks_to_gauss(pooled)
    assert ks_pool > 10.0 * ks_era
    assert ks_pool > 0.08
    assert G.ks_to_uniform(pooled) < ks_pool   # 오히려 균일에 가깝다 (유도와 일치)


# ═══════════════════════════════════════ 에라 분해 (구조)
def test_eras_from_a_hand_built_sequence():
    us = [3.7, 2.7, 1.7, 1.42857, 2.3333, 1.3333]
    eras, tail = G.eras_from_u(us, drop_first=False)
    assert [(round(u, 3), d, round(x, 3)) for u, d, x in eras] == \
        [(3.7, 3, 0.7), (1.429, 1, 0.429), (2.333, 2, 0.333)]
    assert tail is False


def test_consistent_prefix_cuts_at_the_first_junk_row():
    """★ 벽 바닥의 병리 행(D1b: u 52 대신 24)을 그 자리에서 자른다."""
    us = [3.7, 2.7, 1.7, 1.42857, 24.0, 23.0]
    assert G.consistent_prefix(us) == 4
    assert G.consistent_prefix([3.7, 2.7, 1.7]) == 3


def test_era_x_never_needs_a_floor():
    """★ x 는 끝 에폭 u−1 로 읽으므로 (0,1) 을 벗어날 수 없다 — floor 뒤집힘 함정 회피."""
    d = _ode()
    assert (d["x"] > 0.0).all() and (d["x"] < 1.0).all()
    # 구조 불변식: u_시작 ≈ digit + x  (ODE 잡음 이내)
    gap = np.abs(d["u_start"] - d["digit"] - d["x"])
    assert gap.max() < 0.02, gap.max()


# ═══════════════════════════════════════ ① ODE → 닫힌형 (편향이 잡음 아래인 것들)
def test_ode_era_density_matches_gauss_and_rejects_uniform():
    """★★ 물리 궤적의 에라-x 가 Gauss 불변밀도다 (KS 0.026 < 임계 0.041)."""
    x = _ode()["x"]
    ks_g, ks_u = G.ks_to_gauss(x), G.ks_to_uniform(x)
    assert ks_g < 0.035
    assert ks_u > 2.0 * ks_g, (ks_g, ks_u)


def test_ode_lyapunov_matches_the_universal_value():
    """★★ **머리기사** — 물리 앙상블의 λ 가 π²/(6 ln2) 와 1σ 로 맞는다 (2.436±0.066).

    균일밀도 대조값 2.0 은 6.6σ 로 배제 — "Gauss 다움" 이 잡음이 아니다.
    """
    lam, se = G.lyapunov_estimate(_ode()["x"])
    assert abs(lam - G.LYAPUNOV) < 3.5 * se
    assert abs(lam - G.LYAPUNOV) < 0.3 * abs(lam - 2.0)


# ═══════════════════════════════════════ ①↔② 검열 편향 (숨기지 않는다)
def test_the_censoring_bias_is_real_and_positive():
    """★★ digit-1 과잉 (0.523 vs GK 0.415, ≈7σ)과 꼬리 결핍 — 편향을 **못박는다**.

    이게 실패하면(ODE 가 GK 와 맞으면) 검열 논의 전체를 다시 써야 한다.
    """
    d = _ode()
    fr, tail = G.digit_fractions(d["digit"])
    se1 = np.sqrt(0.415 * 0.585 / len(d["digit"]))
    assert fr[0] - float(G.gauss_kuzmin(1)) > 5.0 * se1
    assert tail < 0.5 * G.digit_tail(6)
    assert d["censored_tail"] > 0.15 * d["n_traj"]       # 검열이 실제로 흔하다


def test_the_mirror_reproduces_the_bias_direction_and_size():
    """★ 같은 예산의 순수 사상(②)이 ①의 편향을 재현한다 — 편향의 원인이 물리가
    아니라 **프로토콜(검열)** 이라는 증거.

    ★ 정직한 한계: ODE 예산은 내생적(큰 digit 이 τ 를 태움)이라 ②는 주변분포
      근사다 — 2~3σ 급 잔차(digit1 0.558 vs 0.523)는 남는다.  게이트도 그만큼만.
    """
    fo, _ = G.digit_fractions(_ode()["digit"])
    fm, _ = G.digit_fractions(_mirror()["digit"])
    assert fm[0] > float(G.gauss_kuzmin(1)) + 0.05       # 같은 방향
    assert abs(fm[0] - fo[0]) < 0.06                     # 같은 크기급
    lam_o, _ = G.lyapunov_estimate(_ode()["x"])
    lam_m, _ = G.lyapunov_estimate(_mirror()["x"])
    assert abs(lam_m - lam_o) < 0.1


def test_khinchin_is_censored_in_both_dynamical_routes():
    """★ K 는 digit 꼬리가 지배해 검열에 가장 민감 — ①② 모두 결핍, ③만 K₀.

    ODE 로 K₀ 를 "확인"했다고 주장하지 **않기 위한** 게이트다.
    """
    K_o, _ = G.khinchin_estimate(_ode()["digit"])
    K_m, _ = G.khinchin_estimate(_mirror()["digit"])
    K_u, _ = G.khinchin_estimate(_map()["digit"])
    assert K_o < 2.1 and K_m < 2.1
    assert abs(np.log(K_u) - np.log(G.KHINCHIN)) < 0.02
    assert abs(np.log(K_o) - np.log(K_m)) < 0.15


# ═══════════════════════════════════════ 회계
def test_ensemble_bookkeeping_is_consistent():
    d = _ode()
    assert len(d["x"]) == len(d["digit"]) == len(d["u_start"])
    assert len(d["epochs"]) == d["n_traj"]
    assert len(d["x"]) > 800                     # 통계가 실제로 모였다
    assert (d["digit"] >= 1).all()
    # 에폭 회계: 통계에라 + 버린 첫 에라 + 꼬리 ≤ 관측 에폭 합
    assert d["digit"].sum() <= d["epochs"].sum()

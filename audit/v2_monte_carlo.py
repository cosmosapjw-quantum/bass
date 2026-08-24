"""
V2f · **몬테카를로 구조 오라클** — 정확도 오라클이 **아니다**.

★ 역할이 강등된 경위 (PLAN-V2 §3, 4.3): MC 는 광자 10⁶개로 p₂ 를 9 % 로 재는데
  결정론 격자는 32점으로 4e−15 다.  게다가
   · 강한 감쇠 자체가 상관표본의 전제를 파괴하고 (상관계수 0.10),
   · 잡음이 1/(a√N) 이라 우주론적 이방성 a~10⁻⁵ 에서 N~10¹⁶ 이 필요하며,
   · 진동 배경에서 스텝을 늘려도 잡음이 바닥에 붙는다.
  ⇒ **정확도는 V2a 의 결정론 오라클이 담당한다.**

★ 그럼에도 MC 만 볼 수 있는 것이 하나 있다: 충돌 연산자가 **진짜 마르코프 커널**인가.
  구적은 적분값이 맞아도 "위상함수가 실제 확률분포인가", "표본추출이 가능한가",
  "광자 하나하나가 보존되는가" 를 보지 못한다.  이 파일은 **그것만** 확인한다.
  게이트는 5 % 수준이고, 그 이상을 주장하지 않는다.

    python -m audit.v2_monte_carlo
"""
from __future__ import annotations

import numpy as np

P2 = staticmethod if False else (lambda m: 0.5 * (3.0 * m * m - 1.0))


# ═══════════════════════════════════════ 표본추출
def sample_isotropic(n, rng):
    z = rng.uniform(-1.0, 1.0, n)
    ph = rng.uniform(0.0, 2 * np.pi, n)
    s = np.sqrt(np.maximum(0.0, 1 - z * z))
    return np.stack([s * np.cos(ph), s * np.sin(ph), z], 1)


def sample_mu(n, rng, chunk=1.6):
    """Rayleigh 위상함수 (3/8)(1+μ²) 에서 μ 표본추출 (기각법, 상한 3/4).

    ★ 여기서 pdf 를 **표본추출로만** 쓴다 — 적분하지 않는다.  KS 시험이
      "이 표본이 정말 그 pdf 인가" 를 본다 (구조 확인).
    """
    out, need = [], int(n)
    while need > 0:
        m = rng.uniform(-1.0, 1.0, int(need * chunk) + 64)
        keep = m[rng.uniform(0.0, 1.0, len(m)) * 0.75 < 0.375 * (1 + m * m)]
        out.append(keep)
        need -= len(keep)
    return np.concatenate(out)[:int(n)]


def scatter_once(dirs, rng):
    """각 광자를 Rayleigh 위상함수로 1회 산란 (방향만 바뀐다 — 광자 수 보존)."""
    n = len(dirs)
    mu = sample_mu(n, rng)
    phi = rng.uniform(0.0, 2 * np.pi, n)
    a = np.zeros_like(dirs)
    small = np.abs(dirs[:, 0]) < 0.9
    a[small, 0] = 1.0
    a[~small, 1] = 1.0
    e1 = np.cross(dirs, a)
    e1 /= np.linalg.norm(e1, axis=1, keepdims=True)
    e2 = np.cross(dirs, e1)
    st = np.sqrt(np.maximum(0.0, 1 - mu * mu))
    v = (mu[:, None] * dirs + (st * np.cos(phi))[:, None] * e1
         + (st * np.sin(phi))[:, None] * e2)
    return v / np.linalg.norm(v, axis=1, keepdims=True)


# ═══════════════════════════════════════ 구조 게이트 (정확도 아님)
def ks_statistic(N=200_000, seed=0):
    """★ 표본추출된 μ 가 실제로 (3/8)(1+μ²) 를 따르는가 — KS 통계량.

    CDF: F(μ) = (3μ + μ³ + 4) / 8.
    반환 dict(D, critical_5pct) — D < critical 이면 통과 (5 % 유의).
    """
    rng = np.random.default_rng(seed)
    m = np.sort(sample_mu(N, rng))
    F = (3.0 * m + m ** 3 + 4.0) / 8.0
    i = np.arange(1, len(m) + 1)
    D = float(max(np.abs(F - i / len(m)).max(), np.abs(F - (i - 1) / len(m)).max()))
    return dict(D=D, critical_5pct=1.36 / np.sqrt(len(m)), n=len(m))


def photon_number_is_exactly_conserved(N=100_000, rounds=5, seed=0):
    """★ 광자 수는 **정확히** 보존된다 (표본 개수가 안 변한다) — 정수 등식."""
    rng = np.random.default_rng(seed)
    d = sample_isotropic(N, rng)
    counts = [len(d)]
    for _ in range(rounds):
        d = scatter_once(d, rng)
        counts.append(len(d))
        assert np.abs(np.linalg.norm(d, axis=1) - 1.0).max() < 1e-12
    return counts


def kernel_positivity(n_probe=20_000, seed=0):
    """★ 위상함수가 **비음**이고 규격화된다 (확률분포의 최소 조건).

    구적은 적분값만 보므로 이 성질을 못 본다 — MC 쪽이 볼 수 있는 것.
    """
    rng = np.random.default_rng(seed)
    m = rng.uniform(-1.0, 1.0, n_probe)
    p = 0.375 * (1 + m ** 2)
    x, w = np.polynomial.legendre.leggauss(64)
    return dict(min_value=float(p.min()),
                integral=float(np.sum(w * 0.375 * (1 + x ** 2))))


def p2_estimate(N=1_000_000, a=0.3, reps=12, seed=1000):
    """★ p₂ 를 MC 로 — **5 % 게이트**.  이것이 MC 에 기대하는 전부다."""
    vals = []
    for k in range(reps):
        rng = np.random.default_rng(seed + k)
        d = _sample_aniso(N, a, rng)
        d2 = scatter_once(d, rng)
        vals.append(P2(d2[:, 2]).mean() / P2(d[:, 2]).mean())
    v = np.array(vals)
    return dict(mean=float(v.mean()), std=float(v.std()),
                rel_err=float(abs(v.mean() - 0.1) / 0.1),
                sem_rel=float(v.std() / np.sqrt(len(v)) / 0.1))


def _sample_aniso(n, a, rng):
    out, need = [], int(n)
    while need > 0:
        c = sample_isotropic(int(need * 1.6) + 64, rng)
        w = 1.0 + a * P2(c[:, 2])
        keep = c[rng.uniform(0.0, 1.0, len(c)) < w / (1.0 + abs(a))]
        out.append(keep)
        need -= len(keep)
    return np.concatenate(out)[:int(n)]


def noise_floor_scan(Ns=(10_000, 100_000, 1_000_000), a=0.3, reps=12):
    """★ 잡음이 1/√N 로만 준다 — **정확도 오라클이 될 수 없는 이유**를 표로."""
    out = []
    for N in Ns:
        r = p2_estimate(N, a, reps)
        out.append((int(N), r["std"] / 0.1))
    return out


def main():
    print("=" * 72)
    print("V2f · 몬테카를로 **구조** 오라클 (정확도 오라클이 아님)")
    print("=" * 72)
    k = ks_statistic()
    print(f"\n[1] 위상함수 표본추출이 실제 pdf 인가 (KS, n={k['n']})")
    print(f"    D = {k['D']:.5f}   5 % 임계 = {k['critical_5pct']:.5f}   "
          f"{'통과' if k['D'] < k['critical_5pct'] else '실패'}")
    p = kernel_positivity()
    print(f"\n[2] 커널이 확률분포인가")
    print(f"    최소값 = {p['min_value']:.6f} (≥0)   ∫ = {p['integral']:.15f}")
    c = photon_number_is_exactly_conserved()
    print(f"\n[3] 광자 수 보존 (정수 등식): {c}")
    e = p2_estimate()
    print(f"\n[4] p₂ (5 % 게이트, N=10⁶ × 12회)")
    print(f"    평균 {e['mean']:.5f}   1회 표준편차 {e['std']:.5f}   "
          f"상대오차 {100*e['rel_err']:.2f} %")
    print(f"\n[5] ★ 잡음 바닥 — 왜 정확도 오라클이 못 되는가")
    for N, s in noise_floor_scan():
        print(f"    N = {N:9d}:  1회 상대 표준편차 {100*s:6.2f} %")
    print(f"\n    ⇒ 1/√N.  V2a 의 결정론 격자는 32점에 4e−15 다.")


if __name__ == "__main__":
    main()

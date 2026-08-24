"""
V2 설계용 사전측정 — Thomson 충돌항 오라클 후보들의 **달성 가능 정확도**를 잰다.

표적: 다극 감쇠 고유값.  Rayleigh 위상함수 P(mu) = (3/16pi)(1+mu^2) 를
Legendre 전개하면 p_0=1, p_1=0, p_2=1/10, p_{l>=3}=0.
=> 산란 한 번이 l=2 를 정확히 1/10 배로 만든다 (감쇠 9/10).
이 1/10 을 얼마나 정확히 재느냐가 오라클의 능력이다.
"""
import numpy as np

RNG = np.random.default_rng(12345)
P2 = lambda m: 0.5 * (3.0 * m * m - 1.0)


def sample_iso(n, rng):
    z = rng.uniform(-1, 1, n)
    ph = rng.uniform(0, 2 * np.pi, n)
    s = np.sqrt(1 - z * z)
    return np.stack([s * np.cos(ph), s * np.sin(ph), z], 1)


def sample_aniso(n, a, rng):
    """f(n) ∝ 1 + a P2(n_z) 에서 표본추출 (기각법).  <P2> = a/5."""
    out = []
    need = n
    while need > 0:
        c = sample_iso(int(need * 1.6) + 64, rng)
        w = 1.0 + a * P2(c[:, 2])
        keep = c[rng.uniform(0, 1, len(c)) < w / (1.0 + abs(a))]
        out.append(keep)
        need -= len(keep)
    return np.concatenate(out)[:n]


def sample_rayleigh_mu(n, rng):
    """P(mu) ∝ (1+mu^2)*3/8 에서 mu 표본추출 (기각법, 상한 3/4)."""
    out = []
    need = n
    while need > 0:
        m = rng.uniform(-1, 1, int(need * 1.5) + 64)
        keep = m[rng.uniform(0, 1, len(m)) * 0.75 < 0.375 * (1 + m * m)]
        out.append(keep)
        need -= len(keep)
    return np.concatenate(out)[:n]


def scatter(dirs, rng):
    """각 광자를 Rayleigh 위상함수로 1회 산란."""
    n = len(dirs)
    mu = sample_rayleigh_mu(n, rng)
    phi = rng.uniform(0, 2 * np.pi, n)
    # dirs 에 수직인 정규직교쌍
    a = np.zeros_like(dirs)
    idx = np.abs(dirs[:, 0]) < 0.9
    a[idx, 0] = 1.0
    a[~idx, 1] = 1.0
    e1 = np.cross(dirs, a)
    e1 /= np.linalg.norm(e1, axis=1, keepdims=True)
    e2 = np.cross(dirs, e1)
    st = np.sqrt(np.maximum(0.0, 1 - mu * mu))
    return (mu[:, None] * dirs + (st * np.cos(phi))[:, None] * e1
            + (st * np.sin(phi))[:, None] * e2)


def est_plain(N, a, rng):
    """경로 A — 소박한 MC: 산란 전/후 <P2> 를 각각 추정하고 비를 취한다."""
    d0 = sample_aniso(N, a, rng)
    d1 = scatter(d0, rng)
    return P2(d1[:, 2]).mean() / P2(d0[:, 2]).mean()


def est_rb(N, a, rng):
    """경로 B — Rao-Blackwell: 나가는 방향을 표본추출하지 않고 **해석적으로 적분**.

    E[P2(n'_z) | n] = p_2 * P2(n_z)  (Legendre 덧셈정리) 이므로,
    산란 단계의 분산이 0 이 된다.  남는 잡음은 들어오는 분포 표본추출뿐이다.
    ★ 이 항등식 자체가 우리가 검증하려는 대상이므로 오라클로는 순환이다 —
      여기서는 "잡음의 출처가 어디인지" 를 분해하기 위해서만 쓴다.
    """
    d0 = sample_aniso(N, a, rng)
    return 0.1 * P2(d0[:, 2]).mean() / P2(d0[:, 2]).mean()


def est_paired(N, a, rng):
    """경로 C — 상관표본(공통난수): 같은 광자에 대해 (후/전) 을 쌍으로 본다.

    비 추정량 = mean(P2(n')) / mean(P2(n)) 는 위 est_plain 과 같지만,
    분모·분자가 같은 표본에서 오므로 상관이 잡음을 줄인다.  실제 감소량을 잰다.
    """
    d0 = sample_aniso(N, a, rng)
    d1 = scatter(d0, rng)
    num, den = P2(d1[:, 2]), P2(d0[:, 2])
    return num.mean() / den.mean(), np.corrcoef(num, den)[0, 1]


print("=== MC 로 p_2 = 0.1 을 재기 (a = 0.3 이방성) ===")
print(f"{'N':>10} {'plain 평균':>12} {'plain 표준편차':>14} {'상대오차%':>10} {'상관계수':>9}")
for N in (10_000, 100_000, 1_000_000):
    vals, cors = [], []
    for k in range(24):
        r = np.random.default_rng(1000 + k)
        v, c = est_paired(N, 0.3, r)
        vals.append(v); cors.append(c)
    vals = np.array(vals)
    print(f"{N:10d} {vals.mean():12.5f} {vals.std():14.2e} "
          f"{100*vals.std()/0.1:10.2f} {np.mean(cors):9.3f}")

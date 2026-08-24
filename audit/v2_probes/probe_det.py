"""
V2 설계용 사전측정 2 — **결정론적 각도구적**(discrete ordinates) 오라클의 정확도.

같은 표적(p_2 = 1/10)을 몬테카를로 없이 잰다.  산란적분

    (C f)(n) = ∫ dΩ' P(n·n') f(n')      P(mu) = (3/16π)(1+mu^2)

을 Gauss-Legendre(θ) × 균일(φ) 곱격자에서 **직접 이산화**한다.
다극 대수(Legendre 재귀, PSTF, λ_l)를 전혀 쓰지 않는다 — 완전 독립 경로.
"""
import numpy as np

P2 = lambda m: 0.5 * (3.0 * m * m - 1.0)


def grid(nth, nph):
    x, w = np.polynomial.legendre.leggauss(nth)          # cos(theta) 노드
    ph = (np.arange(nph) + 0.5) * 2 * np.pi / nph
    X, PH = np.meshgrid(x, ph, indexing="ij")
    W = np.outer(w, np.full(nph, 2 * np.pi / nph)) / (4 * np.pi)
    s = np.sqrt(1 - X ** 2)
    n = np.stack([s * np.cos(PH), s * np.sin(PH), X], -1).reshape(-1, 3)
    return n, W.ravel()


def collide(f, n, w):
    """C f — 위상함수를 격자 위에서 직접 축약 (다극 전개 미사용)."""
    mu = n @ n.T
    P = (3.0 / 16.0 / np.pi) * (1.0 + mu ** 2) * (4 * np.pi)   # dΩ' 정규화 흡수
    return P @ (w * f)


print("=== 결정론적 각도구적으로 p_2 를 재기 ===")
print(f"{'nth':>5} {'nph':>5} {'점수':>7} {'추정 p_2':>16} {'|오차|':>12}")
for nth, nph in ((4, 8), (6, 12), (8, 16), (12, 24), (16, 32), (24, 48)):
    n, w = grid(nth, nph)
    f = 1.0 + 0.3 * P2(n[:, 2])
    out = collide(f, n, w)
    # l=2 성분 추출도 구적으로 (5/2 는 규격화)
    a_in = 5.0 * np.sum(w * f * P2(n[:, 2])) / np.sum(w * f)
    a_out = 5.0 * np.sum(w * out * P2(n[:, 2])) / np.sum(w * out)
    print(f"{nth:5d} {nph:5d} {len(n):7d} {a_out/a_in:16.12f} {abs(a_out/a_in-0.1):12.2e}")

print()
print("=== 광자수(l=0) 보존 — 충돌항의 독립 게이트 ===")
for nth, nph in ((6, 12), (12, 24)):
    n, w = grid(nth, nph)
    f = 1.0 + 0.3 * P2(n[:, 2]) + 0.2 * n[:, 0] * n[:, 1]
    out = collide(f, n, w)
    print(f"  nth={nth:3d} nph={nph:3d}:  |∫Cf − ∫f|/∫f = "
          f"{abs(np.sum(w*out)-np.sum(w*f))/np.sum(w*f):.3e}")

print()
print("=== l=1 (쌍극) 은 정확히 보존되어야 한다 (p_1 = 0 이 아니라 1/3? 측정한다) ===")
n, w = grid(16, 32)
for l, fn in ((1, lambda v: v[:, 2]),
              (3, lambda v: 0.5 * (5 * v[:, 2] ** 3 - 3 * v[:, 2]))):
    f = 1.0 + 0.3 * fn(n)
    out = collide(f, n, w)
    num = np.sum(w * out * fn(n)) / np.sum(w * f * fn(n))
    print(f"  l={l}:  p_l = {num:.12f}")

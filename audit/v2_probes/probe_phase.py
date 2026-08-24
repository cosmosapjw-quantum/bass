"""
★ 설계 핵심 하나 — **위상함수를 인용하지 않고 재유도**한다.

D-오라클이 우리 코드의 P(mu)=(3/16pi)(1+mu^2) 를 그대로 쓰면 '다극 축약' 만 검증하고
**물리 입력은 검증하지 않는다**.  그래서 Thomson 미분단면적을 편광 기저에서
직접 조립한다:  dsigma/dOmega ∝ (1/2) Σ_{i,j} |ê_i · ê'_j|^2   (입사 비편광, 출사 합산)
"""
import numpy as np


def basis(n):
    a = np.array([1.0, 0, 0]) if abs(n[0]) < 0.9 else np.array([0, 1.0, 0])
    e1 = np.cross(n, a); e1 /= np.linalg.norm(e1)
    return e1, np.cross(n, e1)


def phase_from_dipole(n, np_):
    """편광 기저에서 조립한 위상함수 (규격화 전)."""
    a1, a2 = basis(n)
    b1, b2 = basis(np_)
    return 0.5 * sum((u @ v) ** 2 for u in (a1, a2) for v in (b1, b2))


rng = np.random.default_rng(7)
print(f"{'mu':>8} {'쌍극조립':>14} {'(1+mu^2)/2':>14} {'차이':>10}")
worst = 0.0
for _ in range(8):
    n = rng.normal(size=3); n /= np.linalg.norm(n)
    m = rng.normal(size=3); m /= np.linalg.norm(m)
    mu = float(n @ m)
    got = phase_from_dipole(n, m)
    want = 0.5 * (1 + mu ** 2)
    worst = max(worst, abs(got - want))
    print(f"{mu:8.4f} {got:14.9f} {want:14.9f} {abs(got-want):10.1e}")
print(f"\n최대 차이 = {worst:.2e}   ⇒ (1+mu^2) 형태가 **쌍극복사에서 재유도**된다.")
print("규격화: ∫ (3/16π)(1+mu²) dΩ = 1 (아래에서 구적으로 확인)")

x, w = np.polynomial.legendre.leggauss(8)
print(f"∫ P dΩ = {2*np.pi*np.sum(w*(3/16/np.pi)*(1+x**2)):.15f}")

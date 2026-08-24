"""
F3 · class A tilted 게이지·유도 감사 — 합성 정의의 세 기둥을 잰다.

  (1) 경로 1 (성분 전개 rhs) ≡ 경로 2 (general+fluid 합성) — 무작위 상태 스윕
  (2) 게이지 소거: 일반 프레임 dN 비대각 = 0 (n-대각 유지 회전 W 의 정의)
  (3) LRS 축퇴 측정: N₁→N₂, Σ₁₂≠0 에서 W₁₂ = √3Σ₁₂(N₁+N₂)/(N₁−N₂) 발산
      — _safe 가드는 1e−12 클리핑이라 |ΔN| < 1e−12 에서 |W| ~ 1e12·|Σ₁₂| 로
      **조용히 오답**이 된다.  이 절벽을 수치로 박제한다 (침묵 실패 방지는
      호출자 몫 — LIMITATIONS 문서화).

실행: python -m audit.f3_class_a_tilted_gauge  (패키지 상대 임포트 — 직접 경로 실행은 실패)
"""
from __future__ import annotations

import jax
import numpy as np

jax.config.update("jax_enable_x64", True)
import jax.numpy as jnp  # noqa: E402

from bianchi.charts import class_a_tilted as AT  # noqa: E402


def route_agreement(n_samples=24, seed=7, gamma=1.3):
    """경로 1 vs 경로 2 — 무작위 상태에서 최악 성분차."""
    rng = np.random.default_rng(seed)
    worst = 0.0
    for _ in range(n_samples):
        y = AT.StateAT.from_array(jnp.asarray(np.r_[
            rng.uniform(-0.3, 0.3, 5), rng.uniform(-0.8, 0.8, 3),
            rng.uniform(-0.4, 0.4, 3)]))
        r1 = np.asarray(AT.rhs(0.0, y, {"gamma": gamma}).as_array())
        r2 = np.asarray(AT.rhs_via_general(0.0, y, {"gamma": gamma}).as_array())
        worst = max(worst, float(np.abs(r1 - r2).max()))
    return worst


def gauge_cancellation(seed=3, n_samples=12, gamma=1.3):
    """W 를 넣은 일반 프레임 dN 의 비대각 성분 최댓값 (0 이어야 한다)."""
    rng = np.random.default_rng(seed)
    worst = 0.0
    for _ in range(n_samples):
        y = AT.StateAT.from_array(jnp.asarray(np.r_[
            rng.uniform(-0.3, 0.3, 5), rng.uniform(-0.9, 0.9, 3),
            rng.uniform(-0.4, 0.4, 3)]))
        off = np.asarray(AT.off_diagonal_n_rate(y, {"gamma": gamma}))
        worst = max(worst, float(np.abs(off).max()))
    return worst


def lrs_cliff(s12=0.05):
    """LRS 축퇴 절벽: ΔN = N₁−N₂ 를 줄이며 |W₁₂| 를 잰다."""
    rows = []
    for dn in (1e-2, 1e-4, 1e-8, 1e-12, 0.0):
        y = AT.StateAT.from_array(jnp.asarray(
            [0.1, 0.0, s12, 0.0, 0.0, 0.5 + dn, 0.5, 0.3, 0.1, 0.0, 0.0]))
        w12, _, _ = AT.gauge_W(y)
        rows.append((dn, float(w12)))
    return rows


def report():
    print("route1-route2 worst:", route_agreement())
    print("gauge dN offdiag worst:", gauge_cancellation())
    print("LRS cliff (ΔN, W₁₂):")
    for dn, w in lrs_cliff():
        print(f"  ΔN={dn:.0e}  W12={w:.3e}")


if __name__ == "__main__":
    report()

"""
V2 설계용 사전측정 3 — **진동 배경에서 궤적 오라클의 오차 누적**.

문헌 근거 (van den Hoogen 외, Bianchi VII_0 의 미래):
  진동 각변수가  psi ≈ psi_hat + (sqrt(3)/M) e^{rho tau},  M ∝ e^{-tau}
  ⇒ **진동수가 tau 에 대해 지수적으로 증가**한다.  따라서 고정 구간을 풀려면
    스텝 수가 지수적으로 늘어난다.

여기서 재는 것: 충돌률을 매 스텝 **추정**해야 하는 오라클(MC)과
**정확히 계산**하는 오라클(구적)의 최종 상대오차가 스텝 수에 따라 어떻게 가는가.

모형:  dJ/dtau = -kappa(tau) (1 - p2) J,   kappa = 1 + b sin(omega(tau) tau)
       omega(tau) = omega0 e^{rho tau}   (VII_0 형 진동수 증가)
정확해는 kappa 를 수치적분해 얻는다 (같은 세밀격자에서).
"""
import numpy as np

B, RHO, W0, P2C = 0.6, 1.5, 6.0, 0.9      # p2=0.1 -> (1-p2)=0.9


def kappa(t):
    return 1.0 + B * np.sin(W0 * np.exp(RHO * t) * t)


def exact_logJ(T, nfine=2_000_000):
    t = np.linspace(0, T, nfine)
    return -P2C * np.trapezoid(kappa(t), t)


def run(T, nsteps, mc_N, rng):
    """사다리꼴 적분.  mc_N 이 None 이면 kappa 를 정확히, 아니면 MC 로 추정."""
    ts = np.linspace(0, T, nsteps + 1)
    k = kappa(ts)
    if mc_N is not None:
        # MC 오라클: 매 평가에서 상대잡음 sigma/sqrt(N).
        # probe_mc 측정값: N=1e6 에서 p2 상대오차 9% => sigma_eff ≈ 90
        k = k * (1.0 + 90.0 / np.sqrt(mc_N) * rng.normal(size=k.shape))
    return -P2C * np.trapezoid(k, ts)


T = 1.2
ex = exact_logJ(T)
print(f"정확해 log J(T) = {ex:.9f}   (T={T}, 진동수 {W0:.0f}→{W0*np.exp(RHO*T):.0f})")
print()
print(f"{'nsteps':>8} {'결정론 상대오차':>16} {'MC(N=1e6)':>14} {'MC(N=1e8)':>14}")
for ns in (200, 800, 3200, 12800, 51200):
    det = abs(run(T, ns, None, None) - ex) / abs(ex)
    m6, m8 = [], []
    for s in range(16):
        r = np.random.default_rng(s)
        m6.append(abs(run(T, ns, 1e6, r) - ex) / abs(ex))
        m8.append(abs(run(T, ns, 1e8, r) - ex) / abs(ex))
    print(f"{ns:8d} {det:16.3e} {np.mean(m6):14.3e} {np.mean(m8):14.3e}")

print()
print("★ 해석: 결정론 오차는 스텝을 늘리면 계속 내려간다 (진동을 풀면 됨).")
print("  MC 오차는 스텝을 늘려도 **내려가지 않는다** — 매 평가의 잡음이 독립이라")
print("  적분이 잡음을 평균하지만 1/sqrt(nsteps) 로만 줄고, 애초 바닥이 N 이 정한다.")
print("  즉 진동을 풀려고 스텝을 늘릴수록 '계산은 늘고 정확도는 바닥에 붙는다'.")

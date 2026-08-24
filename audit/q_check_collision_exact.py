"""Q7 사전검증 — 3항 정확 충돌 지수 (★) 가 dense 행렬지수와 일치하는가.

이 스크립트는 PLAN-Q §3 의 식 (★) 을 계획 승인 전에 **반증 시도**한다.
    exp(dt*C) f = P0 f + e^{-x}(f - P0 f - P2 f) + e^{-0.9x} P2 f,  C = nu(K - I)
심판: 격자 위 dense 행렬지수 (scipy.linalg.expm).
"""
import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.linalg import expm

def grid(nt, np_):
    x, wx = leggauss(nt)
    th = np.arccos(x)
    ph = 2*np.pi*np.arange(np_)/np_
    T, P = np.meshgrid(th, ph, indexing="ij")
    W = np.outer(wx, np.full(np_, 2*np.pi/np_)).ravel()
    n = np.stack([np.sin(T)*np.cos(P), np.sin(T)*np.sin(P), np.cos(T)], -1)
    return n.reshape(-1, 3), W

def thomson_matrix(nhat, w):
    c = nhat @ nhat.T
    K = (3.0/(16*np.pi))*(1.0 + c**2)
    return K * w[None, :]                      # (M f)_i = sum_j w_j K_ij f_j

def proj_l(f, nhat, w, l):
    """P_l f — 실수 구면조화 대신 Legendre 덧셈정리로 직접."""
    c = nhat @ nhat.T
    from numpy.polynomial.legendre import legval
    coef = np.zeros(l+1); coef[l] = 1.0
    Pl = legval(c, coef)
    return ((2*l+1)/(4*np.pi)) * (Pl * w[None, :]) @ f

def three_term(f, nhat, w, x):
    P0 = proj_l(f, nhat, w, 0)
    P2 = proj_l(f, nhat, w, 2)
    return P0 + np.exp(-x)*(f - P0 - P2) + np.exp(-0.9*x)*P2

def run(nt=24, npz=24, seed=0):
    nhat, w = grid(nt, npz)
    M = thomson_matrix(nhat, w)
    rng = np.random.default_rng(seed)
    f = 1.0 + 0.7*rng.standard_normal(len(w))
    out = {}
    for x in (0.01, 0.1, 1.0, 5.0, 50.0, 1e3, 1e6):
        ref = expm(x*(M - np.eye(len(w)))) @ f if x <= 50 else None
        got = three_term(f, nhat, w, x)
        if ref is not None:
            out[x] = float(np.abs(got-ref).max()/np.abs(ref).max())
        else:
            out[x] = ("스펙트럼", float(got.min()),
                      float(np.abs(got - proj_l(f, nhat, w, 0)).max()))
    return out, nhat, w, f

if __name__ == "__main__":
    for nt, npz in ((16,16),(24,24),(32,64)):
        o,_,_,_ = run(nt,npz)
        print(f"격자 {nt}x{npz}:")
        for k,v in o.items():
            print(f"   x={k:>8g}  {v}")
    # 고유값 재계산 (하드코딩 금지 게이트의 원형)
    nhat, w = grid(32,64); M = thomson_matrix(nhat, w)
    from numpy.polynomial.legendre import legval
    c = nhat @ nhat.T
    for l in range(6):
        coef = np.zeros(l+1); coef[l]=1.0
        Y = legval(c[:,0], coef)                     # P_l(cos) as test function
        k = (M @ Y)[0] / Y[0]
        print(f"k_{l} = {k:.15f}")

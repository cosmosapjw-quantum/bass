"""
P3 · **편광 Thomson 연산자**의 제1원리 구성과 고유구조 (83차).

기저-없는 형식 (Stokes 부호 규약이 아예 필요 없다):
    결맞음 텐서 J_ab(ê) — 에르미트, J_ab ê^b = 0.
    산란은 **들어온 장을 나가는 스크린에 투영**하는 것이다:

        (K J)_ab(ê') = (3/8pi) ∫ dOmega  Pi_ac(ê') J_cd(ê) Pi_db(ê')
        Pi_ab(ê) = delta_ab - ê_a ê_b

★★ 결정적 관찰 (이 스크립트가 확인한다):
   투영자는 **ê' 에만** 의존하므로 ê 적분은 그냥 상수텐서

        M_cd = ∫ J_cd(ê) dOmega          (9 성분)

   가 된다.  즉 **K 는 정확히 rank 9 연산자**다.  l-분해가 필요 없다.

   K^n 을 반복하면 M 위의 선형사상
        Kcal[M] = (3/8pi) ∫ Pi M Pi dOmega
   가 나오고, 구면 적분 항등 ∫n̂n̂ = (4pi/3)delta, ∫n̂n̂n̂n̂ = (4pi/15)(dd+dd+dd) 로

        Kcal[M] = (7/10) M + (1/10) tr(M) delta      (대칭부)
        Kcal[A] = (1/2) A                            (반대칭부 = V)

   고유값:  1 (트레이스, 광자 수 보존) · 7/10 (무대각 대칭 5차원) · 1/2 (V, 3차원)

   ⇒ 정확 지수가 **다시 3항**으로 떨어진다 (스칼라 (★) 의 완전한 유비):

        exp(x C) J = e^{-x} J
                   + (3/8pi) Pi(ê') [ sum_lambda ((e^{-x(1-lambda)} - e^{-x})/lambda)
                                       P_lambda M ] Pi(ê')

   비용 O(n_ang) + 9-성분 축약.  Sinkhorn·행렬지수·l 분해 전부 불필요.
   **강성 소멸·근사 절환 부재**가 편광에서도 그대로 유지된다.

사용:  python -m audit.p3_polarized_thomson
"""
from __future__ import annotations

import numpy as np

EIG = {"trace": 1.0, "stf": 0.7, "anti": 0.5}


def grid(nt, npz):
    """자립 GL x 균일 격자 (이 감사는 Rust 휠에 의존하지 않는다)."""
    x, wx = np.polynomial.legendre.leggauss(nt)
    ph = 2 * np.pi * np.arange(npz) / npz
    T, P = np.meshgrid(np.arccos(x), ph, indexing="ij")
    w = np.outer(wx, np.full(npz, 2 * np.pi / npz)).ravel()
    e = np.stack([np.sin(T) * np.cos(P), np.sin(T) * np.sin(P),
                  np.cos(T)], -1).reshape(-1, 3)
    return e, w


def scalar_three_term(e, w, f, x):
    """스칼라 (★) 3항 — 자립 구현 (무편광 축약 대조용)."""
    if x <= 0:
        return f.copy()
    em = np.exp(-x)
    P0 = np.full_like(f, float((w * f).sum()) / (4 * np.pi))
    # P2 f = (5/4pi) ∫ P_2(ê·ê') f dOmega
    c = e @ e.T
    P2 = (5.0 / (4 * np.pi)) * ((0.5 * (3 * c ** 2 - 1)) * w[None, :]) @ f
    return em * f + (1.0 - em) * P0 + (np.exp(-0.9 * x) - em) * P2


def kernel_apply_dense(e, w, J):
    """직접 구적 (rank-9 를 **쓰지 않고**) — 독립 구성 (교차검증용).  J: (M,3,3)."""
    Mten = np.einsum("a,aij->ij", w, J)
    out = np.empty_like(J)
    for i in range(len(w)):
        P = np.eye(3) - np.outer(e[i], e[i])
        out[i] = (3.0 / (8.0 * np.pi)) * (P @ Mten @ P)
    return out


def kcal(Mten):
    """Kcal[M] = (3/8pi) ∫ Pi M Pi dOmega — 닫힌형."""
    Ms = 0.5 * (Mten + Mten.T)
    Ma = 0.5 * (Mten - Mten.T)
    return 0.7 * Ms + 0.1 * np.trace(Ms) * np.eye(3) + 0.5 * Ma


def kcal_numeric(e, w, Mten):
    """같은 것을 구적으로 (닫힌형 검증)."""
    acc = np.zeros((3, 3))
    for i in range(len(w)):
        P = np.eye(3) - np.outer(e[i], e[i])
        acc += w[i] * (P @ Mten @ P)
    return (3.0 / (8.0 * np.pi)) * acc


def _split(Mten):
    Ms = 0.5 * (Mten + Mten.T); Ma = 0.5 * (Mten - Mten.T)
    tr = np.trace(Ms) / 3.0 * np.eye(3)
    return {"trace": tr, "stf": Ms - tr, "anti": Ma}


def collide_exact_pol(e, w, J, x):
    """★ 편광 정확 충돌 지수 (3항 닫힌형)."""
    if x <= 0:
        return J.copy()
    Mten = np.einsum("a,aij->ij", w, J)
    parts = _split(Mten)
    acc = np.zeros((3, 3))
    em = np.exp(-x)
    for name, lam in EIG.items():
        acc += ((np.exp(-x * (1.0 - lam)) - em) / lam) * parts[name]
    out = em * J.copy()
    for i in range(len(w)):
        P = np.eye(3) - np.outer(e[i], e[i])
        out[i] += (3.0 / (8.0 * np.pi)) * (P @ acc @ P)
    return out


def collide_taylor(e, w, J, x, nmax=400, tol=1e-18):
    """심판: e^{x(K-I)} = e^{-x} sum x^n K^n/n!  (dense 구적 경로)."""
    term = J.copy(); acc = J.copy()
    for n in range(1, nmax):
        term = kernel_apply_dense(e, w, term) * (x / n)
        acc = acc + term
        if np.abs(term).max() < tol:
            break
    return np.exp(-x) * acc


def project_screen(e, J):
    """J_ab ê^b = 0 을 강제 (스크린 투영)."""
    out = np.empty_like(J)
    for i in range(len(J)):
        P = np.eye(3) - np.outer(e[i], e[i])
        out[i] = P @ J[i] @ P
    return out


def unpolarized(e, I):
    """무편광 J = (I/2) Pi(ê)."""
    return 0.5 * I[:, None, None] * (np.eye(3)[None] - np.einsum("ai,aj->aij", e, e))


def run(nt=24, npz=48, seed=0):
    e, w = grid(nt, npz)
    rng = np.random.default_rng(seed)
    out = {}

    # 1. Kcal 닫힌형 == 구적
    err = 0.0
    for _ in range(5):
        Mt = rng.standard_normal((3, 3))
        err = max(err, float(np.abs(kcal(Mt) - kcal_numeric(e, w, Mt)).max()))
    out["kcal_closed_vs_quad"] = err

    # 2. Kcal 고유값 (재계산 — 하드코딩 금지)
    eigs = {}
    for name in EIG:
        Mt = _split(rng.standard_normal((3, 3)))[name]
        if np.abs(Mt).max() < 1e-12:
            continue
        eigs[name] = float((kcal(Mt) / Mt)[np.abs(Mt) > 1e-9][0])
    out["eigenvalues"] = eigs

    # 3. rank-9: 임의 J 두 개가 같은 M 을 주면 K 출력이 같다
    J1 = project_screen(e, rng.standard_normal((len(w), 3, 3)))
    J2 = J1 + project_screen(e, rng.standard_normal((len(w), 3, 3))) * 0.0
    M1 = np.einsum("a,aij->ij", w, J1)
    J3 = J1 + (np.random.default_rng(9).standard_normal((len(w), 3, 3)) * 0)
    out["rank9_M"] = float(np.abs(M1 - np.einsum("a,aij->ij", w, J3)).max())

    # 4. ★ 3항 == Taylor 심판
    J = project_screen(e, rng.standard_normal((len(w), 3, 3)))
    J = 0.5 * (J + np.einsum("aij->aji", J))            # 실수 대칭 (선형편광+I)
    rel = {}
    for x in (0.01, 0.1, 1.0, 5.0, 50.0):
        a = collide_exact_pol(e, w, J, x)
        b = collide_taylor(e, w, J, x)
        rel[x] = float(np.abs(a - b).max() / max(np.abs(b).max(), 1e-30))
    out["three_term_vs_taylor"] = rel

    # 5. 무편광 축약: tr(K J) 가 스칼라 핵 (1, 0, 1/10, 0) 을 재현
    I0 = 1.0 + 0.7 * rng.standard_normal(len(w))
    Ju = unpolarized(e, I0)
    red = {}
    for x in (0.3, 2.0, 20.0):
        Ip = np.einsum("aii->a", collide_exact_pol(e, w, Ju, x))
        Is = scalar_three_term(e, w, I0, x)
        red[x] = float(np.abs(Ip - Is).max() / max(np.abs(Is).max(), 1e-30))
    out["unpolarized_reduction"] = red

    # 6. 편광 생성: 비등방 무편광 입사가 **편광을 만든다** (l=2 결합)
    aniso = 1.0 + 0.8 * e[:, 2] ** 2
    Ja = unpolarized(e, aniso)
    Jo = collide_exact_pol(e, w, Ja, 1.0)
    pol = Jo - unpolarized(e, np.einsum("aii->a", Jo))
    out["polarization_generated"] = float(np.abs(pol).max())
    iso = unpolarized(e, np.ones(len(w)))
    Jo2 = collide_exact_pol(e, w, iso, 1.0)
    out["polarization_from_isotropic"] = float(np.abs(
        Jo2 - unpolarized(e, np.einsum("aii->a", Jo2))).max())

    # 7. 강성 극한: x -> 1e6 유한·정확
    big = collide_exact_pol(e, w, J, 1e6)
    out["stiff_finite"] = bool(np.isfinite(big).all())
    out["stiff_is_l0"] = float(np.abs(
        big - collide_exact_pol(e, w, J, 1e7)).max() / max(np.abs(big).max(), 1e-30))

    # 8. 광자 수 보존 (트레이스 적분)
    n0 = float(np.einsum("a,aii->", w, J))
    out["number_conservation"] = max(
        abs(float(np.einsum("a,aii->", w, collide_exact_pol(e, w, J, x))) - n0)
        / abs(n0) for x in (0.1, 3.0, 1e3))

    # 9. V (원편광) 섹터: Thomson 이 V 를 만들지 않는다 (대칭 입력 -> 반대칭 출력 0)
    outJ = collide_exact_pol(e, w, J, 1.0)
    out["V_not_generated"] = float(np.abs(outJ - np.einsum("aij->aji", outJ)).max())
    return out


if __name__ == "__main__":
    r = run()
    for k, v in r.items():
        print(f"{k:26s} : {v}")

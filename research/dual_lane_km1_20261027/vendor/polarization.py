"""
P2′·P-C·P-T · **편광 캐리어 · 정확 충돌 · 스크린 수송** (84차).

유도·검증: `docs/P-DERIVATION.md` (D1–D5), 감사 `audit/p1_*`, `audit/p3_*`.

캐리어 (P0 계약): 기저-없는 에르미트 3-텐서 J_ab(ê), J_ab ê^b = 0.
  · 실수 대칭 6 = 세기 I + 선형편광,  반대칭 3 = 원편광 V.  총 **9 성분**.
  · Stokes 부호 규약이 **필요 없다** — 기저를 안 쓰기 때문.

충돌 (D5): K 는 정확히 rank 9.  ê 적분이 M = ∫J dΩ 로 축약되고
    𝒦[M] = (7/10)M + (1/10)tr(M)δ (대칭),  (1/2)A (반대칭)
고유값 (1, 7/10, 1/2) ⇒ 정확 지수가 **3항**:
    exp(xC)J = e^{−x}J + (3/8π)Π(ê)[Σ_λ ((e^{−x(1−λ)}−e^{−x})/λ) P_λ M]Π(ê)

수송 (D1–D3): 스크린 홀로노미가 **배율 1 의 순수 SO(2)**.  구현은 회전계수에서
직접 — 스크린 대표원 W (W_0 = 0, W·p = 0) 의 율은
    dW_a = dV_a − (dV_0/E) p_a   (V = (0, W) 로 4-수송한 뒤 게이지 복원)
이고 텐서는 두 지표에 각각 적용한다.
"""
from __future__ import annotations

import numpy as np

TRACE, STF, ANTI = "trace", "stf", "anti"
EIG = {TRACE: 1.0, STF: 0.7, ANTI: 0.5}
I3 = np.eye(3)


# ═══════════════════════════════════════════════ 캐리어 (P2′)
def screen_proj(e):
    """Π_ab(ê) = δ_ab − ê_aê_b   → (M,3,3)."""
    e = np.asarray(e, float)
    return I3[None] - np.einsum("ai,aj->aij", e, e)


def unpolarized(e, I):
    """무편광 J = (I/2)Π(ê)."""
    return 0.5 * np.asarray(I, float)[:, None, None] * screen_proj(e)


def intensity(J):
    """I = tr J."""
    return np.einsum("aii->a", np.asarray(J, float))


def project_screen(e, J):
    """J → Π J Π  (제약 J_ab ê^b = 0 강제)."""
    P = screen_proj(e)
    return np.einsum("aik,akl,alj->aij", P, np.asarray(J, float), P)


def screen_leak(e, J):
    """제약 이탈 |J_ab ê^b| 의 최대값 (상시 지표)."""
    return float(np.abs(np.einsum("aij,aj->ai", np.asarray(J, float),
                                  np.asarray(e, float))).max())


def pack9(J):
    """(M,3,3) → (M,9)  [대칭 6 (11,22,33,12,13,23) + 반대칭 3 (23,31,12)]."""
    J = np.asarray(J, float)
    S = 0.5 * (J + np.einsum("aij->aji", J))
    A = 0.5 * (J - np.einsum("aij->aji", J))
    return np.stack([S[:, 0, 0], S[:, 1, 1], S[:, 2, 2], S[:, 0, 1],
                     S[:, 0, 2], S[:, 1, 2],
                     A[:, 1, 2], A[:, 2, 0], A[:, 0, 1]], axis=1)


def unpack9(v):
    v = np.asarray(v, float)
    J = np.zeros((len(v), 3, 3))
    J[:, 0, 0], J[:, 1, 1], J[:, 2, 2] = v[:, 0], v[:, 1], v[:, 2]
    J[:, 0, 1] = J[:, 1, 0] = v[:, 3]
    J[:, 0, 2] = J[:, 2, 0] = v[:, 4]
    J[:, 1, 2] = J[:, 2, 1] = v[:, 5]
    J[:, 1, 2] += v[:, 6]; J[:, 2, 1] -= v[:, 6]
    J[:, 2, 0] += v[:, 7]; J[:, 0, 2] -= v[:, 7]
    J[:, 0, 1] += v[:, 8]; J[:, 1, 0] -= v[:, 8]
    return J


def stokes_diagnostic(e, J):
    """(I, Q, U, V) — **진단 전용**.  기저를 여기서만 고르고, 그 사실을 이름에 박는다."""
    e = np.asarray(e, float); J = np.asarray(J, float)
    k = np.argmin(np.abs(e), axis=1)
    m1 = np.zeros_like(e); m1[np.arange(len(e)), k] = 1.0
    m1 = m1 - np.einsum("ai,ai->a", m1, e)[:, None] * e
    m1 /= np.linalg.norm(m1, axis=1)[:, None]
    m2 = np.cross(e, m1)
    j11 = np.einsum("ai,aij,aj->a", m1, J, m1)
    j22 = np.einsum("ai,aij,aj->a", m2, J, m2)
    j12 = np.einsum("ai,aij,aj->a", m1, J, m2)
    j21 = np.einsum("ai,aij,aj->a", m2, J, m1)
    return (j11 + j22, j11 - j22, j12 + j21, j21 - j12)


# ═══════════════════════════════════════════════ 충돌 (P-C)
def _split(M):
    S = 0.5 * (M + M.T); A = 0.5 * (M - M.T)
    tr = np.trace(S) / 3.0 * I3
    return {TRACE: tr, STF: S - tr, ANTI: A}


def kcal(M):
    """𝒦[M] — 닫힌형 (D5)."""
    S = 0.5 * (M + M.T); A = 0.5 * (M - M.T)
    return 0.7 * S + 0.1 * np.trace(S) * I3 + 0.5 * A


def kcal_eigenvalues_numeric(e, w):
    """★ 하드코딩 금지 — 구적으로 재계산 (계약 P0 게이트)."""
    P = screen_proj(e)
    out = []
    for M in (I3, np.diag([1.0, -1.0, 0.0]),
              np.array([[0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, 0.0, 0.0]])):
        K = (3.0 / (8 * np.pi)) * np.einsum("a,aik,kl,alj->ij", w, P, M, P)
        m = np.abs(M) > 1e-9
        out.append(float(K[m][0] / M[m][0]))
    return tuple(out)


def collide(e, w, J, x):
    """★ 편광 정확 충돌 지수 (rank-9 3항).  O(n_ang)."""
    J = np.asarray(J, float)
    if x < 0:
        raise ValueError("nu*dt < 0 — 침묵 폴백 금지 (시간 역행은 명시 호출로)")
    if x == 0:
        return J.copy()
    M = np.einsum("a,aij->ij", np.asarray(w, float), J)
    parts = _split(M)
    em = np.exp(-x)
    acc = np.zeros((3, 3))
    for name, lam in EIG.items():
        acc += _three_term_coeff(x, lam) * parts[name]
    P = screen_proj(e)
    return em * J + (3.0 / (8 * np.pi)) * np.einsum("aik,kl,alj->aij", P, acc, P)


def _three_term_coeff(x, lam):
    """c_λ(x) = (e^{−x(1−λ)} − e^{−x})/λ = e^{−x}·expm1(xλ)/λ.

    ★ 84차 (수치 검증): 원식은 xλ ≲ 1 에서 **파국적 상쇄**를 겪는다 (x=1e−16 에서
    c_0.5 가 정확히 0).  expm1 판은 상쇄가 없다.  xλ > 709 에서만 expm1 이 넘치고
    그 영역은 두 항의 크기 차가 커 상쇄가 없으므로 원식으로 되돌린다."""
    if x * lam < 1.0:
        return np.exp(-x) * np.expm1(x * lam) / lam
    return (np.exp(-x * (1.0 - lam)) - np.exp(-x)) / lam


def collide_taylor(e, w, J, x, nmax=400, tol=1e-18, guard=1e-8):
    """심판: e^{x(K−I)} = e^{−x}Σ xⁿKⁿ/n!  (rank-9 를 쓰지 않는 직접 구적).

    ★ 84차: 이 급수는 x ≳ 250 에서 **조용히 틀린다** (x=400 에서 상대 0.5,
    x=1000 에서 nan) — 항이 n≈x 까지 자란 뒤 e^{−x} 와 상쇄하기 때문이다.
    `collide` 는 같은 x 에서 정확하므로, 가드가 없으면 장래의 시험이 **엉뚱한
    함수를 탓한다**.  자릿수 상실을 추정해 넘으면 거절한다."""
    J = np.asarray(J, float)
    P = screen_proj(e)
    term = J.copy(); acc = J.copy()
    peak = float(np.abs(acc).max()); converged = False
    for n in range(1, nmax):
        M = np.einsum("a,aij->ij", w, term)
        term = (3.0 / (8 * np.pi)) * np.einsum("aik,kl,alj->aij", P, M, P) * (x / n)
        acc = acc + term
        peak = max(peak, float(np.abs(acc).max()))
        if np.abs(term).max() < tol:
            converged = True
            break
    if not converged:
        raise ValueError(f"Taylor 심판 미수렴: x={x} 에서 nmax={nmax} 항 소진")
    out = np.exp(-x) * acc
    scale = max(float(np.abs(out).max()), 1e-300)
    loss = np.finfo(float).eps * peak * np.exp(-x) / scale
    if loss > guard:
        raise ValueError(
            f"Taylor 심판 자릿수 상실: x={x}, 추정 상대오차 {loss:.2e} > {guard:.0e}. "
            "이 영역에서는 `collide` 의 닫힌형이 심판보다 정확하다.")
    return out


# ═══════════════════════════════════════════════ 수송 (P-T)
def _eps():
    E = np.zeros((3, 3, 3))
    for i in range(3):
        for j in range(3):
            for k in range(3):
                E[i, j, k] = (i - j) * (j - k) * (k - i) / 2
    return E


EPS = _eps()


def rotation_coefficients(H, S, R, N, A):
    """Γ^a_bc — `audit.p1_polarized_transport` 와 **같은 유도** (계량 적합 자기검사)."""
    C = np.zeros((4, 4, 4))
    K = H * I3 + S + np.einsum("abc,c->ab", EPS, R)
    for a in range(3):
        for b in range(3):
            C[1 + b, 0, 1 + a] = -K[a, b]
            C[1 + b, 1 + a, 0] = +K[a, b]
    for c in range(3):
        for i in range(3):
            for j in range(3):
                v = sum(EPS[i, j, d] * N[d, c] for d in range(3))
                if c == j:
                    v += A[i]
                if c == i:
                    v -= A[j]
                C[1 + c, 1 + i, 1 + j] = v
    eta = np.diag([-1.0, 1.0, 1.0, 1.0])
    Cl = np.einsum("ad,dbc->abc", eta, C)
    Gl = 0.5 * (-Cl - np.einsum("bca->abc", Cl) + np.einsum("cab->abc", Cl))
    # ★ 계량 적합 자기검사.  `assert` 는 python -O 에서 소거되므로 명시 예외로 둔다
    #   (84차: 이 검사가 오기억 Koszul 을 잡는 유일한 상시 방어선이다).
    bad = float(np.abs(Gl + np.einsum("bac->abc", Gl)).max())
    if bad > 1e-12:
        raise ValueError(f"Γ_(ab)c ≠ 0 — 계량 적합 위반 ({bad:.2e})")
    return np.einsum("ad,dbc->abc", eta, Gl)


def screen_vector_rate(W, p, H, S, R, N, A):
    """dW_a/dt — 스크린 대표원 (W_0 = 0, W·p = 0) 의 율.

    V = (0, W) 를 4-수송한 뒤 게이지 복원:  dW_a = dV_a − (dV_0/E) p_a."""
    G = rotation_coefficients(H, S, R, N, A)
    p = np.atleast_2d(np.asarray(p, float))
    W = np.atleast_2d(np.asarray(W, float))
    E = np.linalg.norm(p, axis=1)
    P4 = np.concatenate([E[:, None], p], axis=1)
    V4 = np.concatenate([np.zeros((len(W), 1)), W], axis=1)
    dV = -np.einsum("abc,nb,nc->na", G, V4, P4) / E[:, None]
    return dV[:, 1:] - (dV[:, 0] / E)[:, None] * p


def momentum_rate(p, H, S, R, N, A):
    """dp^i/dt — **같은 Γ 로부터** 유도한 측지선 (특성선과의 정합 시험용).

    ★ 84차 교훈: 운동량이 맞아도 접속이 틀릴 수 있다 (C_abc 가 (b,c) 반대칭이라
    측지선에서 떨어진다).  역은 성립하므로 Γ 를 고친 뒤에는 이 함수가 Q-tier 의
    독립 특성선 RHS 와 일치하는지 **반드시** 확인한다."""
    G = rotation_coefficients(H, S, R, N, A)
    p = np.atleast_2d(np.asarray(p, float))
    E = np.linalg.norm(p, axis=1)
    P4 = np.concatenate([E[:, None], p], axis=1)
    return -np.einsum("abc,nb,nc->na", G, P4, P4)[:, 1:] / E[:, None]


def direction_rate(e, H, S, R, N, A):
    """dê/dt = P_⊥[dp]/|p| — 측지선 RHS 가 p 에 1차 동차라 |p|=1 에서 계산."""
    e = np.atleast_2d(np.asarray(e, float))
    dp = momentum_rate(e, H, S, R, N, A)
    return dp - np.einsum("ai,ai->a", dp, e)[:, None] * e


def tensor_rate(J, p, H, S, R, N, A):
    """dJ_ab/dt — 두 지표에 스크린 수송을 적용 (D3 의 텐서판)."""
    J = np.asarray(J, float)
    n = len(J)
    out = np.zeros_like(J)
    for k in range(3):                       # 열 벡터 3개를 각각 나른다
        out[:, :, k] += screen_vector_rate(J[:, :, k], p, H, S, R, N, A)
    for k in range(3):
        out[:, k, :] += screen_vector_rate(J[:, k, :], p, H, S, R, N, A)
    return out


def rodrigues(e, psi):
    """ê 축 둘레 ψ 회전 (M,3,3) — 기저-없는 스크린 회전."""
    e = np.asarray(e, float); psi = np.asarray(psi, float)
    c, s = np.cos(psi)[:, None, None], np.sin(psi)[:, None, None]
    K = np.einsum("ijk,ak->aij", EPS, e)
    return c * I3[None] + s * K + (1 - c) * np.einsum("ai,aj->aij", e, e)


def rotate_screen(J, e, psi):
    """J → R J Rᵀ,  R = Rodrigues(ê, ψ).  선형편광은 2ψ 로 돈다 (spin-2)."""
    R = rodrigues(e, psi)
    return np.einsum("aik,akl,ajl->aij", R, np.asarray(J, float), R)


# ═══════════════════════════════════════════════ P6 · 관측량 (진단 전용)
def multipoles_diagnostic(e, w, J, l_max=4):
    """Stokes 다중극 — **진단 전용**.

    ★★ 87차 정정 (외부 리뷰 C2): 원래 여기 "E/B 분해는 **선형이론의 언어**다"
    라고 적었는데 **틀렸다**.  spin-2 장의 전역 E/B 분해는 비섭동적으로도
    정의된다 — 선형 섭동론 전용 언어가 아니다.  격리하는 진짜 이유는 **구현
    쪽**이다: 위의 `argmin|e|` 국소 스크린 게이지가 구면 위에서 불연속이라 그
    위에서 정의한 Q/U 가 각 해상도로 수렴하지 않고, 따라서 전역 spin-2 분해가
    **정량적으로 안정적이지 않다**.  연속적인 스크린 게이지 (또는 spin-weighted
    구면조화 기반) 를 도입하면 정량화할 수 있다 — 그때까지만 diagnostic 이다.
    """
    from numpy.polynomial.legendre import legval
    I, Q, U, V = stokes_diagnostic(e, J)
    out = {}
    for l in range(l_max + 1):
        c = np.zeros(l + 1); c[l] = 1.0
        Pl = legval(e[:, 2], c)
        nrm = (2 * l + 1) / (4 * np.pi)
        out[l] = dict(I=float(nrm * (w * Pl * I).sum()),
                      Q=float(nrm * (w * Pl * Q).sum()),
                      U=float(nrm * (w * Pl * U).sum()),
                      V=float(nrm * (w * Pl * V).sum()))
    return out


def polarization_fraction(e, J):
    """p = √(Q²+U²+V²)/I — 기저-없는 **편광도**.

    ★★ 84차 정정 (독립 검증): 스크린 성분으로 ‖J − (I/2)Π‖_F = √(Q²+U²+V²)/√2
    이므로 **√2 를 곱해야** 실제 편광도가 된다.  고치기 전에는 100 % 선편광에서
    0.7071 을 돌려주었다.  I < 0 (비물리) 은 거절한다 (예전 maximum(I,1e−300) 은
    음의 세기를 눌러 4e300 같은 그럴듯한 유한값을 냈다)."""
    J = np.asarray(J, float)
    I = intensity(J)
    P = J - unpolarized(e, I)
    num = np.sqrt(2.0 * np.einsum("aij,aij->a", P, P))
    if float(np.min(I)) < 0.0:
        raise ValueError("I = tr J < 0 — 비물리 상태 (조용한 폴백 금지)")
    out = np.zeros_like(I)
    nz = I > 0.0
    out[nz] = num[nz] / I[nz]
    if np.any(num[~nz] > 1e-300):
        raise ValueError("I = 0 인데 편광 성분이 0 이 아니다 — 비물리 상태")
    return out


def _delta_coeff(x):
    """c(x) = (6/7)e^{−x} + (1/7)e^{−0.3x} − e^{−0.9x},  c = 0.03x² + O(x³).

    ★ 84차: 직역하면 2차까지 상쇄해 x=1e−8 에서 **부호까지** 틀린다.
    c = e^{−0.9x}g(x), g = (6/7)expm1(−0.1x) + (1/7)expm1(0.6x) 의 급수는
    1차항이 해석적으로 상쇄되어 있다.  x ≤ 1 에서 급수를 쓴다."""
    if abs(x) <= 1.0:
        g = 0.0; fact = 1.0
        for n in range(2, 25):
            fact *= n
            a = ((6.0 / 7.0) * (-0.1) ** n + (1.0 / 7.0) * 0.6 ** n) / fact
            t = a * x ** n
            g += t
            if abs(t) < 1e-19 * max(abs(g), 1e-300):
                break
        return np.exp(-0.9 * x) * g
    return (6.0 / 7.0) * np.exp(-x) + (1.0 / 7.0) * np.exp(-0.3 * x) - np.exp(-0.9 * x)


def unpolarized_delta_closed(x, P2I):
    """★ 편광 tr − 무편광 스칼라의 **닫힌형** (84차).

        ΔI(ê) = [ (6/7)e^{−x} + (1/7)e^{−0.3x} − e^{−0.9x} ] · (P₂I₀)(ê)

    l=2 블록 [[1/10, −√6/10], [−√6/10, 3/5]] (trace 7/10, det 0 ⇒ 고유값 {0, 7/10})
    에서 나온다.  차는 **l=2 를 통해서만** 들어오고 임의 구적에서 정확하다 —
    즉 앨리어싱이 아니라 물리 (E→I 되먹임) 다."""
    return _delta_coeff(float(x)) * np.asarray(P2I, float)


# ═══════════════════════════════════════════════ P5 · 비용
def cost_model(n_ang, n_p=0, n_species=1):
    """저장 바이트/노드 = 9 x 8 = 72.  Mode A/B 상태 크기와 스텝 flop."""
    per_node = 9 * 8
    nodes = n_ang * (n_p if n_p else 1)
    return dict(bytes_per_node=per_node,
                independent_dof=4,                  # 제약 하 실제 자유도 (SVD 실측)
                state_bytes=per_node * nodes * n_species,
                collide_flops=nodes * 161,          # 손 계수 (Rust 커널)
                transport_flops=nodes * 9 * 36)     # 스텐실 x 9 성분

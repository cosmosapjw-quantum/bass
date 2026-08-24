"""
K1 · **운동론 계층 ↔ Einstein 결합** — 물질이 비로소 기하를 움직인다.

지금까지 계층은 고정된 배경 위에서만 풀렸다 (test-field).  `charts/general.py` 에
`Pi` 훅이 있었으나 아무도 채우지 않았고, `tilted_integrate.Background` 는 a(t) 를
**처방**했다.  여기서 그 고리를 닫는다.

Bianchi I (법선 합동, 8πG = 1) 결합계:

    H = √((ρ + σ²)/3)                      ← Friedmann **구속** (진화식이 아니다)
    ȧ_i = (H + σ_i) a_i
    σ̇_i = −3H σ_i + π_i                     ← ★ 계층의 π 가 기하를 움직인다
    (계층)  J̇ = hierarchy_rhs(J, H, σ)

★ 규격화는 **측정으로 확정**했다 (`audit/k1_shear_source_normalization.py`):
    · σ̇^i + θσ^i = 1.000000000000 × (무대각합 공간 Einstein)   잔차 4.8e−16
    · 차트 변수로는  Σ' = −(2−q)Σ + Π,  **Π = π/H²**            잔차 6.7e−16
    · 통제군 Friedmann G_00 = 3H² − σ² 재생산                   잔차 2.1e−14
  문헌 인용이나 손대수가 아니라 계량에서 직접 잰 값이다 (규격화는 문헌마다 갈린다).

★ σ² 규약:  σ² ≡ ½ σ_ab σ^ab = ½ Σ_i σ_i²  (audit 과 동일).

★ H 를 **구속에서 푼다**는 점이 중요하다 — 진화시키지 않으므로 Friedmann 은 설계상
  항상 만족된다.  대신 **Raychaudhuri 와의 정합성**이 자유롭지 않은 검사가 되며,
  그것이 곧 ∇_μT^{μν}=0 (Bianchi 항등식) 이다 → `K3_residual`.
"""
from __future__ import annotations

import numpy as np

from bianchi.matter import freestream as fs
from bianchi.matter import hierarchy as H


# ═══════════════════════════════════════ 물질 공급원 두 갈래
def matter_from_quadrature(a_vec, mass, f0=fs.f_fermi_dirac):
    """★ 기준(reference) 경로 — 정확 구적.  계층을 전혀 쓰지 않는다."""
    rho, p, pi = fs.moments(a_vec, mass, f0)
    return float(rho), float(p), np.asarray(pi, float)


def matter_from_hierarchy(J):
    """시험 경로 — 진화된 계층 상태에서 읽는다."""
    rho = float(np.asarray(J[(0, 0)]).reshape(()))
    p = float(np.asarray(J[(0, 1)]).reshape(())) / 3.0
    pi = np.asarray(J[(2, 0)], float)
    return rho, p, pi


# ═══════════════════════════════════════ 기하
def sigma_sq(sig):
    """σ² ≡ ½ σ_ab σ^ab = ½ Σ σ_i²  (audit 규약)."""
    s = np.asarray(sig, float)
    return 0.5 * float(s @ s)


def hubble_from_constraint(rho, sig):
    """H = √((ρ + σ²)/3) — Friedmann **구속**에서 푼다 (진화시키지 않는다)."""
    val = (rho + sigma_sq(sig)) / 3.0
    if val <= 0.0:
        raise ValueError(f"Friedmann 구속이 음수 H² 를 준다 (ρ+σ² = {3*val:.3e})")
    return float(np.sqrt(val))


def geometry_rhs(a_vec, sig, rho, pi):
    """(ȧ_i, σ̇_i) — Bianchi I 결합 방정식."""
    a = np.asarray(a_vec, float)
    s = np.asarray(sig, float)
    Hb = hubble_from_constraint(rho, s)
    pid = np.asarray(pi, float)
    pid = np.diag(pid) if pid.ndim == 2 else pid
    pid = pid - pid.mean()                      # 무대각합 사영 (수치 표류 방지)
    return a * (Hb + s), -3.0 * Hb * s + pid, Hb


# ═══════════════════════════════════════ ★ K3 · Bianchi 항등식 게이트
def K3_residual(a_vec, sig, mass, source="quadrature", J=None, f0=fs.f_fermi_dirac):
    """★★ Ḣ 를 **두 가지로** 계산해 비교 — 결합이 옳은지 가르는 독립 검사.

      (A) Friedmann 구속을 미분:  6HḢ = ρ̇ + d(σ²)/dt
          ★ σ² ≡ **½**σ_abσ^ab 이므로  d(σ²)/dt = σ_i σ̇_i  (2배가 아니다).
            처음에 2배로 쓰는 실수를 했고, 이 게이트가 잔차 1e−5 로 **즉시 잡아냈다**
            (차이가 정확히 −σ² + σ·π/(6H) 로 떨어져 원인이 특정됐다).
          ρ̇ 는 **에너지 보존**에서: ρ̇ = −3H(ρ+p) − σ^{ab}π_ab
          (H5-b 에서 부호까지 확정된 계층의 l=0 방정식)
      (B) Raychaudhuri:  Ḣ = −H² − (2/3)σ² − (1/6)(ρ+3p)

    두 값이 일치하는 것은 곧 ∇_μT^{μν} = 0 이다.  Friedmann 은 H 를 구속에서 풀기
    때문에 설계상 항상 만족되어 아무것도 잡아내지 못하므로, 이 정합성이 자유롭지 않은
    검사가 된다.

    ★ **한계 (측정으로 확인)**: 이 게이트는 **Π 규격화에 눈이 멀었다**.  π 를 3배·0배·
      −5배로 틀리게 넣어도 잔차가 1.5e−16 로 같다 — σ·π 항이 ρ̇ 와 σ̇ 사이에서
      **정확히 상쇄**되기 때문이다.  규격화까지 보려면 `einstein_residual` 을 쓸 것.
      (처음에 이 게이트가 규격화도 잡는다고 적었는데 **틀렸다**.)
    """
    a = np.asarray(a_vec, float)
    s = np.asarray(sig, float)
    rho, p, pi = (matter_from_quadrature(a, mass, f0) if source == "quadrature"
                  else matter_from_hierarchy(J))
    Hb = hubble_from_constraint(rho, s)
    pid = np.diag(pi) if np.asarray(pi).ndim == 2 else np.asarray(pi, float)
    pid = pid - pid.mean()
    sdot = -3.0 * Hb * s + pid
    # (A) 구속 미분 + 에너지 보존
    sig_pi = float(s @ pid)                       # σ^{ab}π_ab (대각)
    rho_dot = -3.0 * Hb * (rho + p) - sig_pi
    hdot_A = (rho_dot + float(s @ sdot)) / (6.0 * Hb)
    # (B) Raychaudhuri
    hdot_B = -Hb ** 2 - (2.0 / 3.0) * sigma_sq(s) - (rho + 3.0 * p) / 6.0
    scale = max(abs(hdot_A), abs(hdot_B), 1e-300)
    return dict(hdot_constraint=hdot_A, hdot_raychaudhuri=hdot_B,
                rel=abs(hdot_A - hdot_B) / scale, H=Hb, rho=rho, p=p,
                sigma_pi=sig_pi)


# ═══════════════════════════════════════ 결합 적분
def integrate_reference(a0, sig0, mass, t_end, nsteps=200, f0=fs.f_fermi_dirac):
    """기준 궤적 — 물질을 **정확 구적**으로 매 스텝 다시 계산 (계층 미사용).

    ★ 이것이 결합계의 오라클이다: 계층이 아니라 정확해가 기하를 움직인다.
    """
    a = np.asarray(a0, float).copy()
    s = np.asarray(sig0, float).copy()
    s = s - s.mean()
    dt = t_end / nsteps

    def rhs(av, sv):
        rho, p, pi = matter_from_quadrature(av, mass, f0)
        da, ds, Hb = geometry_rhs(av, sv, rho, pi)
        return da, ds, Hb

    hist = {"t": [0.0], "a": [a.copy()], "sigma": [s.copy()]}
    for _ in range(nsteps):
        k1a, k1s, _ = rhs(a, s)
        k2a, k2s, _ = rhs(a + 0.5 * dt * k1a, s + 0.5 * dt * k1s)
        k3a, k3s, _ = rhs(a + 0.5 * dt * k2a, s + 0.5 * dt * k2s)
        k4a, k4s, _ = rhs(a + dt * k3a, s + dt * k3s)
        a = a + dt / 6.0 * (k1a + 2 * k2a + 2 * k3a + k4a)
        s = s + dt / 6.0 * (k1s + 2 * k2s + 2 * k3s + k4s)
        s = s - s.mean()
        hist["t"].append(hist["t"][-1] + dt)
        hist["a"].append(a.copy())
        hist["sigma"].append(s.copy())
    return hist


def integrate_coupled(a0, sig0, mass, t_end, nsteps=200, l_max=4, i_max=2,
                      f0=fs.f_fermi_dirac):
    """★ 결합 궤적 — 물질을 **계층**이 공급한다 (기하와 함께 진화).

    상태: (a_i, σ_i, J^{(i)}_{A_l}).  H 는 매 스텝 Friedmann 구속에서 푼다.
    """
    a = np.asarray(a0, float).copy()
    s = np.asarray(sig0, float).copy()
    s = s - s.mean()
    J = H.J_grid(a, mass, l_max, i_max, f0)
    dt = t_end / nsteps
    keys = [(l, i) for l in range(l_max + 1) for i in range(i_max + 1)]

    def rhs(av, sv, Jv):
        Jc = H.close_i(dict(Jv), 0, i_max)
        for l in range(l_max + 1):
            H.close_i(Jc, l, i_max)
        for l in (l_max + 1, l_max + 2):
            for i in range(-1, i_max + 3):
                Jc[(l, i)] = H._zeros_like_rank(l)
        rho, p, pi = matter_from_hierarchy(Jc)
        da, ds, Hb = geometry_rhs(av, sv, rho, pi)
        sig_mat = np.diag(np.asarray(sv, float))
        dJ = {k: np.asarray(H.hierarchy_rhs(Jc, Hb, sig_mat, k[0], k[1]), float)
              for k in keys}
        return da, ds, dJ

    def axpy(Jv, dJ, c):
        return {k: np.asarray(Jv[k], float) + c * dJ[k] for k in keys}

    hist = {"t": [0.0], "a": [a.copy()], "sigma": [s.copy()]}
    Js = {k: np.asarray(J[k], float) for k in keys}
    for _ in range(nsteps):
        k1a, k1s, k1J = rhs(a, s, Js)
        k2a, k2s, k2J = rhs(a + .5 * dt * k1a, s + .5 * dt * k1s, axpy(Js, k1J, .5 * dt))
        k3a, k3s, k3J = rhs(a + .5 * dt * k2a, s + .5 * dt * k2s, axpy(Js, k2J, .5 * dt))
        k4a, k4s, k4J = rhs(a + dt * k3a, s + dt * k3s, axpy(Js, k3J, dt))
        a = a + dt / 6.0 * (k1a + 2 * k2a + 2 * k3a + k4a)
        s = s + dt / 6.0 * (k1s + 2 * k2s + 2 * k3s + k4s)
        s = s - s.mean()
        Js = {k: Js[k] + dt / 6.0 * (k1J[k] + 2 * k2J[k] + 2 * k3J[k] + k4J[k])
              for k in keys}
        hist["t"].append(hist["t"][-1] + dt)
        hist["a"].append(a.copy())
        hist["sigma"].append(s.copy())
    hist["J"] = Js
    return hist


# ═══════════════════════════════════════ 게이트
def coupling_matters(a0=(1.0, 0.85, 1.2), sig0=(0.05, -0.02, -0.03), mass=0.0,
                     t_end=0.3, nsteps=200):
    """★ 결합이 **실제로 궤적을 바꾸는가** — π 를 끄면 얼마나 달라지는지.

    안 바뀌면 결합했다는 주장이 공허하다.  반환 dict(with_pi, without_pi, rel).
    """
    ref = integrate_reference(a0, sig0, mass, t_end, nsteps)
    a_with = ref["a"][-1]
    s_with = ref["sigma"][-1]

    # π = 0 (완전유체) 로 다시
    a = np.asarray(a0, float).copy()
    s = np.asarray(sig0, float).copy() - np.mean(sig0)
    dt = t_end / nsteps
    for _ in range(nsteps):
        def rhs(av, sv):
            rho, p, _ = matter_from_quadrature(av, mass)
            da, ds, _ = geometry_rhs(av, sv, rho, np.zeros(3))
            return da, ds
        k1a, k1s = rhs(a, s)
        k2a, k2s = rhs(a + .5 * dt * k1a, s + .5 * dt * k1s)
        k3a, k3s = rhs(a + .5 * dt * k2a, s + .5 * dt * k2s)
        k4a, k4s = rhs(a + dt * k3a, s + dt * k3s)
        a = a + dt / 6.0 * (k1a + 2 * k2a + 2 * k3a + k4a)
        s = s + dt / 6.0 * (k1s + 2 * k2s + 2 * k3s + k4s)
        s = s - s.mean()
    return dict(a_with=a_with, a_without=a, sigma_with=s_with, sigma_without=s,
                rel_a=float(np.abs(a_with - a).max() / np.abs(a_with).max()),
                rel_sigma=float(np.abs(s_with - s).max()
                                / max(np.abs(s_with).max(), 1e-300)))


def coupled_trajectory_error(a0=(1.0, 0.85, 1.2), sig0=(0.05, -0.02, -0.03),
                             mass=0.0, t_end=0.3, nsteps=200, l_max=4, i_max=2):
    """★★ 결합 궤적을 **정확 구적 기준**과 대조 (계층이 기하를 옳게 움직이는가)."""
    ref = integrate_reference(a0, sig0, mass, t_end, nsteps)
    cpl = integrate_coupled(a0, sig0, mass, t_end, nsteps, l_max, i_max)
    da = np.abs(cpl["a"][-1] - ref["a"][-1]).max() / np.abs(ref["a"][-1]).max()
    ds = np.abs(cpl["sigma"][-1] - ref["sigma"][-1]).max() / \
        max(np.abs(ref["sigma"][-1]).max(), 1e-300)
    return dict(a=float(da), sigma=float(ds))


# ═══════════════════════════════════════ ★ K3b · Einstein 잔차 (규격화까지 검사)
#
# ★ **K3 의 한계 (측정으로 확인)**: K3 는 Π 규격화에 **눈이 멀었다**.
#   π 를 3배·0배·−5배로 틀리게 넣어도 K3 잔차가 1.5e−16 로 똑같다 —
#   σ·π 항이 에너지식(ρ̇)과 전단식(σ̇) 사이에서 **정확히 상쇄**되기 때문이다:
#       6HḢ = ρ̇ + σ·σ̇ = [−3H(ρ+p) − σ·π] + [−3Hσ·σ + σ·π]      ← π 소거
#   따라서 K3 는 **에너지·운동량 보존**을 검사할 뿐 규격화를 검사하지 못한다.
#   규격화를 보려면 Einstein 방정식 자체를 궤적 위에서 확인해야 한다 → 아래.
def einstein_residual(a_vec, sig, mass, pi_scale=1.0, f0=fs.f_fermi_dirac):
    """★★ 궤적 상태에서 **G_μν = T_μν** 를 직접 확인 — Π 규격화까지 잡는다.

    (a, ȧ, ä) 를 결합 방정식에서 만들어 Einstein 텐서에 넣고 물질 응력과 비교한다:
        ȧ_i = (H + σ_i) a_i
        Ḣ   = −H² − (2/3)σ² − (ρ+3p)/6          (Raychaudhuri)
        σ̇_i = −3H σ_i + pi_scale · π_i
        ä_i = (Ḣ + σ̇_i) a_i + (H + σ_i)² a_i
    `pi_scale ≠ 1` 이면 ä 가 틀어져 G_tf 가 π 에서 벗어난다 → **잔차가 터진다**.

    반환 dict(G00_rel, Gtf_rel) — 각각 |G_00 − ρ|/ρ, max|G_tf − π|/ρ.
    """
    from audit import k1_shear_source_normalization as AUD
    a = np.asarray(a_vec, float)
    s = np.asarray(sig, float)
    s = s - s.mean()
    rho, p, pi = matter_from_quadrature(a, mass, f0)
    pid = np.diag(pi) - np.diag(pi).mean()
    Hb = hubble_from_constraint(rho, s)
    hdot = -Hb ** 2 - (2.0 / 3.0) * sigma_sq(s) - (rho + 3.0 * p) / 6.0
    sdot = -3.0 * Hb * s + pi_scale * pid
    da = (Hb + s) * a
    dda = (hdot + sdot) * a + (Hb + s) ** 2 * a
    r = AUD.evaluate(list(a) + list(da) + list(dda))
    return dict(G00_rel=abs(r["G00"] - rho) / rho,
                Gtf_rel=float(np.abs(r["G_tf"] - pid).max()) / rho)


def shear_damping_with_isotropic_start(sig0=(0.05, -0.02, -0.03), mass=0.0,
                                       t_end=0.3, nsteps=200):
    """★ **등방 a_vec** 에서 시작하면 π 는 순전히 σ 가 만든다 (Misner 점성).

    이때 π 는 σ 를 **감쇠**시켜야 한다 (H4 에서 유도한 η > 0 의 기하학적 귀결).
    ★ 비등방 a_vec 으로 시작하면 π 가 σ 와 무관하게 이미 존재해 σ 를 **키울 수도**
      있다 — 실제로 그렇다 (측정: |σ| 가 0.0065 → 0.147 로 오히려 커진다).
      "이방응력은 늘 전단을 감쇠시킨다" 는 순진한 기대는 **틀렸다**.
    """
    iso = (1.0, 1.0, 1.0)
    with_pi = integrate_reference(iso, sig0, mass, t_end, nsteps)["sigma"][-1]
    a = np.ones(3)
    s = np.asarray(sig0, float) - np.mean(sig0)
    dt = t_end / nsteps
    for _ in range(nsteps):
        def rhs(av, sv):
            rho, p, _ = matter_from_quadrature(av, mass)
            da, ds, _ = geometry_rhs(av, sv, rho, np.zeros(3))
            return da, ds
        k1a, k1s = rhs(a, s)
        k2a, k2s = rhs(a + .5 * dt * k1a, s + .5 * dt * k1s)
        k3a, k3s = rhs(a + .5 * dt * k2a, s + .5 * dt * k2s)
        k4a, k4s = rhs(a + dt * k3a, s + dt * k3s)
        a = a + dt / 6.0 * (k1a + 2 * k2a + 2 * k3a + k4a)
        s = s + dt / 6.0 * (k1s + 2 * k2s + 2 * k3s + k4s)
        s = s - s.mean()
    return dict(with_pi=with_pi, without_pi=s,
                damped=bool(np.abs(with_pi).max() < np.abs(s).max()))

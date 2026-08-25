"""
H'2 · 성분간 운동량 교환 — n-프레임 순수 운동량 모형 (Thomson 원형; 63차).

모형 (B2b 충돌 오라클 전까지):
    n-프레임 4-힘  I_c^0 = 0 (에너지 무교환),  I_c^a ≠ 0.
    정규화 교환원 R_c (q̂ = 3γΩv/G₊ 단위):
        R_c = Σ_d κ_cd Ω_c Ω_d (v_d − v_c),   κ 대칭·영대각
    ⇒ 쌍별 반대칭 ⇒ Σ_c R_c = 0 (총 운동량 보존, 구조적).

유도 (여기서 제1원리로; sympy 항등이 audit/h2 에 박제):
    (ρ_n, q_a) ↔ (ρ, v_a) 야코비안을 I = (0, R) 에 역적용.
    에너지행이 δ(dρ_n) = 0 을 강제 ⇒ **δ(dΩ_c) = 0** (Ω 진화 무변).
    운동량행 역산의 핵심 소거:  G₋ + 2(γ−1)V² = G₊  ⇒
        δ(dv_c) = (G₊_c / (3 γ_c Ω_c)) · [R_c + (2(γ_c−1)/G₋_c) v_c (v_c·R_c)]
    검산 항등:  δ(d q̂_c) = R_c  **정확** (기호·수치 이중 게이트).

두 경로:
    경로 1 `delta_dv_closed` — 위 닫힌식.
    경로 2 `delta_dv_linsolve` — (Ω, q̂) 의 (ρ̂, v)-야코비안을 jax 로 만들어
      선형해 [0, R] 를 푼다 (유도 과정 자체의 독립 재현; 닫힌식 무사용).

규율: species.SpeciesMix 의 Σ Q = 0 계약과 동일 — `exchange_R` 는 구조적으로
만족하고, 시험이 임의 κ 에서 실측한다.
"""
from __future__ import annotations

from bianchi.matter.fluid import G_minus, G_plus, _safe
from bianchi.optional_dependencies import require_jax_x64

jax, jnp = require_jax_x64(feature=__name__)


def validate_kappa(kappa, nc):
    """κ: (NC,NC) 대칭·영대각 — 아니면 총 보존이 깨지므로 명시 거부."""
    k = jnp.asarray(kappa, jnp.float64)
    if k.shape != (nc, nc):
        raise ValueError(f"kappa: ({nc},{nc}) 필요, got {k.shape}")
    if float(jnp.abs(k - k.T).max()) > 0.0:
        raise ValueError("kappa 는 대칭이어야 한다 — 비대칭은 총 운동량 비보존")
    if float(jnp.abs(jnp.diag(k)).max()) > 0.0:
        raise ValueError("kappa 대각은 0 (자기 교환 없음)")
    return k


def exchange_R(Om, V, kappa):
    """R_c = Σ_d κ_cd Ω_c Ω_d (v_d − v_c)  — (NC,3).  Σ_c R_c = 0 구조적."""
    k = jnp.asarray(kappa, jnp.float64)
    w = k * jnp.outer(Om, Om)                          # w_cd = κ_cd Ω_c Ω_d (대칭)
    # Σ_d w_cd (v_d − v_c) = (w @ V)_c − (Σ_d w_cd)·v_c
    return w @ V - jnp.sum(w, axis=1)[:, None] * V


def delta_dv_closed(gam, Om, V, R):
    """경로 1 — 닫힌식.  (NC,3)."""
    gam = jnp.asarray(gam, jnp.float64)
    V2 = jnp.sum(V * V, axis=1)
    Gp = _safe(G_plus(gam, V2))
    Gm = _safe(G_minus(gam, V2))
    vR = jnp.sum(V * R, axis=1)                        # (NC,)
    return (Gp / (3.0 * gam * _safe(Om)))[:, None] * (
        R + (2.0 * (gam - 1.0) / Gm * vR)[:, None] * V)


def delta_dv_linsolve(gam, Om, V, R):
    """경로 2 — (Ω, q̂)(ρ̂, v) 야코비안 선형해 (닫힌식 무사용).

    변수 (ρ̂, v):  Ω = Γ²G₊ ρ̂,   q̂ = 3γ ρ̂ Γ² v.
    소스 (δdΩ, δdq̂) = (0, R_c) 를 성분별 4×4 로 푼다.

    한계 (리뷰 기록): 검증전용 경로 — V→1 에서 야코비안 특이 (닫힌식은
    _safe 가드, 여기는 게이트 도메인 V<1 에서만 쓴다)."""
    gam = jnp.asarray(gam, jnp.float64)
    out = []
    for c in range(V.shape[0]):
        g = gam[c]
        V2c = float(jnp.sum(V[c] * V[c]))
        rho_hat = float(Om[c]) * (1.0 - V2c) / float(_safe(G_plus(g, V2c)))

        def omega_q(z, g=g):
            rho, v = z[0], z[1:]
            V2 = v @ v
            Gam2 = 1.0 / (1.0 - V2)
            return jnp.concatenate([
                jnp.array([Gam2 * G_plus(g, V2) * rho]),
                3.0 * g * rho * Gam2 * v,
            ])

        z0 = jnp.concatenate([jnp.array([rho_hat]), V[c]])
        A = jax.jacfwd(omega_q)(z0)                    # (4,4)
        rhs = jnp.concatenate([jnp.zeros(1), R[c]])
        out.append(jnp.linalg.solve(A, rhs)[1:])       # δdv (δdρ̂ 버림)
    return jnp.stack(out)

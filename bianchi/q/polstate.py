"""
P8 · **편광 채널을 QState 에 결합** + P9b · **부스트 결합** (84–85차).

═══ 분해 (P8) ═══
캐리어를 **진폭 × 모양**으로 쪼갠다:

    J_ab(ê) = Ĝ(ê) · Ĵ_ab(ê) ,     tr Ĵ = 1 ,  Ĵ_ab ê^b = 0

· 진폭 ln Ĝ 은 **기존 Q 층 그대로**다 (`QState.lG`).  로그-공간이라 깊은 붕괴에서
  double 범위를 넘어도 안전하다.
· 모양 Ĵ 는 9 성분 텐서장.  무편광이면 Ĵ = Π(ê)/2.

이 쪼갬이 정확한 이유:
  (a) 지표 수송 `tensor_rate` 는 tr(dJ) = 0 이므로 **진폭을 건드리지 않는다**
      ⇒ 자유흐름에서 I 채널이 스칼라 경로와 **비트 동일**.
  (b) 충돌은 J 에 **선형**이라 공통 인수를 밖으로 뺄 수 있다 (범위 안전).

═══ 부스트 (P9b, D7) ═══
`audit/p9_boost_screen.py` 가 유도·실측했다: 부스트가 유도하는 스크린 사상은
**배율 1 의 등거리**이고 **추가 회전 ψ = 0** 이다 (무작위 400 조합 ≤ 6.7e−16).
계획의 예상 ("광행차가 스크린을 돌린다") 은 기각되었다.  따라서 편광 × 부스트는
새 기계가 필요 없고 세 단계로 끝난다:

    정지계로 부스트 → rank-9 3항 → 되부스트

진폭에는 도플러가 붙고 (Ĝ′ = 𝒟⁴Ĝ, dΩ′ = dΩ/𝒟²) 모양에는 안 붙는다 —
이것이 진폭/모양 분해가 부스트에서도 맞아떨어지는 이유다.
"""
from __future__ import annotations

import numpy as np

from bianchi.backend_policy import (
    BackendPolicy,
    BackendPolicyError,
    select_backend,
)
from bianchi.q import polarization as PL
from bianchi.q.coupled import mat3


def unpolarized_shape(e):
    """Ĵ = Π(ê)/2  (tr = 1)."""
    return 0.5 * PL.screen_proj(np.asarray(e, float))


def _boost_screen_map(v, e):
    """부스트가 유도하는 스크린 사상 S (M,3,3), 옮겨간 방향 ê′ (M,3), 도플러 𝒟.

    D7 (P9a): S 는 배율 1 의 등거리이고 추가 회전이 없다 ⇒ 여기서 만든 S 를
    두 지표에 적용하는 것으로 편광 부스트가 **끝난다**."""
    v = np.asarray(v, float)
    e = np.atleast_2d(np.asarray(e, float))
    v2 = float(v @ v)
    if v2 >= 1.0:
        raise ValueError("|v_b| < 1 이어야 한다")
    if v2 == 0.0:
        S = np.broadcast_to(np.eye(3), (len(e), 3, 3)).copy()
        return S, e.copy(), np.ones(len(e))
    g = 1.0 / np.sqrt(1.0 - v2)
    ve = e @ v
    D = g * (1.0 - ve)                                   # 도플러 𝒟 (E′ = 𝒟E)
    # 광행차: p′ = p + (g−1)(v·p)v/v² − g E v,  E = 1
    pp = e + ((g - 1.0) * ve / v2)[:, None] * v[None, :] - g * v[None, :]
    ep = pp / np.linalg.norm(pp, axis=1)[:, None]
    # 스크린 사영 → 부스트 → 게이지 복원.  Λ 의 작용:
    #   (ΛW)⁰ = −g(v·W),   (ΛW)^i = W^i + (g−1)(v·W)v^i/v²
    P = PL.screen_proj(e)                                # (M,3,3): 열이 사영된 기저
    Pv = np.einsum("aij,j->ai", P, v)                    # (M,3): v·(열 k)
    W0 = -g * Pv                                         # 시간성분 (열별)
    Wsp = P + ((g - 1.0) / v2) * np.einsum("i,ak->aik", v, Pv)
    S = Wsp - np.einsum("ak,ai->aik", W0 / D[:, None], pp)
    return S, ep, D


def boost_shape(Jhat, v, e):
    """모양 Ĵ 를 부스트한다 (D7: 추가 회전 없음).  반환 (Ĵ′, ê′, 𝒟)."""
    S, ep, D = _boost_screen_map(v, e)
    out = np.einsum("aik,akl,ajl->aij", S, np.asarray(Jhat, float), S)
    out = PL.project_screen(ep, out)
    tr = np.einsum("aii->a", out)
    return out / np.maximum(np.abs(tr), 1e-300)[:, None, None], ep, D


class PolQState:
    """`QState` + 편광 모양 채널 Ĵ.  진폭은 위임하고 모양만 여기서 나른다."""

    __slots__ = ("st", "Jhat")

    def __init__(self, st, Jhat=None):
        self.st = st
        _, e, _, _ = st.geometry()
        self.Jhat = (unpolarized_shape(e) if Jhat is None
                     else np.asarray(Jhat, float).reshape(len(e), 3, 3))

    # ──────────────────────────────────────────────────────────── 진단
    def geometry(self):
        return self.st.geometry()

    def polarization_fraction(self):
        _, e, _, _ = self.st.geometry()
        return PL.polarization_fraction(e, self.Jhat)

    def screen_leak(self):
        _, e, _, _ = self.st.geometry()
        return PL.screen_leak(e, self.Jhat)

    def trace_error(self):
        return float(np.abs(np.einsum("aii->a", self.Jhat) - 1.0).max())

    def stokes(self):
        """(I, Q, U, V) — 진단 전용 (기저를 여기서만 고른다)."""
        _, e, _, _ = self.st.geometry()
        lmax = float(np.max(self.st.lG))
        J = np.exp(self.st.lG - lmax)[:, None, None] * self.Jhat
        return PL.stokes_diagnostic(e, J)

    # ──────────────────────────────────────────────────────── 자유흐름
    def rk4_step(self, dtau):
        """진폭은 Q 층 RK4, 모양은 같은 프레임 흐름 위의 지표 수송.

        공변 프레임은 dM/dτ = −(I + Σ − εR)M 이라 물리 방향 흐름의 (H, Σ, R)
        부분만 담는다 (곡률은 Q5b `residual_step`).  모양의 지표 수송도 **같은
        분해**로 (H, Σ, R) 만 쓴다 — 둘이 같은 특성선 위에 있어야 한다."""
        _, e0, _, _ = self.st.geometry()
        H = 1.0
        Sm, R = mat3(self.st.S6), self.st.rot
        Z3, z3 = np.zeros((3, 3)), np.zeros(3)

        def rhs(J, ev):
            return (PL.direction_rate(ev, H, Sm, R, Z3, z3),
                    PL.tensor_rate(J, ev, H, Sm, R, Z3, z3))

        h = float(dtau)
        k1 = rhs(self.Jhat, e0)
        k2 = rhs(self.Jhat + .5 * h * k1[1], e0 + .5 * h * k1[0])
        k3 = rhs(self.Jhat + .5 * h * k2[1], e0 + .5 * h * k2[0])
        k4 = rhs(self.Jhat + h * k3[1], e0 + h * k3[0])
        self.Jhat = self.Jhat + h / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])
        self.st.rk4_step(dtau)
        self._reproject()
        return self

    def _reproject(self):
        """새 ê 에 대해 제약과 tr 을 회복 (RK4 절단오차만큼의 이탈)."""
        _, e, _, _ = self.st.geometry()
        J = PL.project_screen(e, self.Jhat)
        tr = np.einsum("aii->a", J)
        self.Jhat = J / np.maximum(np.abs(tr), 1e-300)[:, None, None]

    # ─────────────────────────────────────────────── Q5b 잔여 이류
    def residual_step(self, dtau, k_theta=6, k_phi=6, substeps=2):
        """곡률 (N, A) 이 만드는 방향흐름은 모양장도 같이 이류한다.

        ★★ 84차 반증 2회 — **무편광 부분을 해석적으로 빼고 이류한다**.
          ① Ĵ 전체를 remap: 무편광에서 편광이 2.97e−4 생겼다 (Bianchi I 은
             2.8e−9 = RK4 절단뿐이라 곡률 항이 원인임이 즉시 드러남).  Δτ 를
             줄여도 안 줄었다 — '누락된 항' 의 서명.
          ② remap 뒤 ê(q̂) 에서 **앞으로** 지표 회전: 끝점이 틀렸다 (remap 이
             실어온 값은 ê(q̂_back) 의 스크린 위에 있다).
          ③ **채택**: Ĵ = Π(ê)/2 + P 로 쪼개 **편차 P 만** 이류·회전한다.
             Π(ê_back) 을 수송하면 **정확히** Π(ê) 이므로 근사가 아니라 닫힌형이다
             ⇒ 무편광은 **어떤 각 해상도에서도** 무편광으로 남는다."""
        if not self.st.residual:
            self.st.residual_step(dtau, k_theta, k_phi, substeps)
            return self
        N6, A3 = np.asarray(self.st.N6, float), np.asarray(self.st.A3, float)
        if np.any(N6) or np.any(A3):
            import bianchi_rustcore as R
            from bianchi.q import comoving as CM
            from bianchi.q.residual import _backtrace
            n = len(self.st.qhat)
            _, e_now, _, _ = self.st.geometry()
            fr = CM.frame_from(self.st.M)
            qb, _ = _backtrace(self.st.M, self.st.qhat, N6, A3, dtau, substeps)
            e_back, _ = CM.phys(fr, qb)
            dev = self.Jhat - unpolarized_shape(e_now)      # tr = 0
            plan = R.qt_plan_from_points(self.st.sph,
                                         np.ascontiguousarray(qb.ravel()),
                                         np.zeros(n), int(k_theta), int(k_phi))
            flat = dev.reshape(n, 9)
            out = np.stack([np.asarray(plan.apply_mode_a(
                np.ascontiguousarray(flat[:, k]), 0.0)) for k in range(9)], axis=1)
            dev = self._rotate_curvature(out.reshape(-1, 3, 3), e_back,
                                         dtau, N6, A3, substeps)
            self.Jhat = unpolarized_shape(e_now) + dev
        self.st.residual_step(dtau, k_theta, k_phi, substeps)
        self._reproject()
        return self

    def _rotate_curvature(self, dev, e_back, dtau, N6, A3, substeps):
        """곡률 (N̂, Â) 부분의 지표 수송 — ê(q̂_back) → ê(q̂), RK2 부분스텝."""
        Nm, Z3, z3 = mat3(N6), np.zeros((3, 3)), np.zeros(3)
        h = float(dtau) / substeps
        ev, J = np.asarray(e_back, float).copy(), np.asarray(dev, float)
        for _ in range(substeps):
            d1 = PL.direction_rate(ev, 0.0, Z3, z3, Nm, A3)
            t1 = PL.tensor_rate(J, ev, 0.0, Z3, z3, Nm, A3)
            em = ev + 0.5 * h * d1
            em /= np.linalg.norm(em, axis=1)[:, None]
            d2 = PL.direction_rate(em, 0.0, Z3, z3, Nm, A3)
            t2 = PL.tensor_rate(J + 0.5 * h * t1, em, 0.0, Z3, z3, Nm, A3)
            ev = ev + h * d2
            ev /= np.linalg.norm(ev, axis=1)[:, None]
            J = J + h * t2
        return J

    # ─────────────────────────────────────────────────────────── 충돌
    def collide(self, nu_dtau, v_b=None):
        """편광 3항 충돌.  `v_b` 를 주면 **전자 정지계**에서 충돌한다 (P9b).

        D7 (P9a): 부스트의 스크린 사상은 배율 1 의 등거리이고 추가 회전이 없다.
        따라서 세 단계로 끝난다 — 부스트 → rank-9 3항 → 되부스트.
        진폭에는 도플러가 붙고 (Ĝ′ = 𝒟⁴Ĝ, dΩ′ = dΩ/𝒟²) 모양에는 안 붙는다."""
        if nu_dtau <= 0.0:
            return self
        _, e, _, lw = self.st.geometry()
        w = np.exp(lw - float(np.max(lw)))
        w = w * (4.0 * np.pi / float(w.sum()))     # Σw = 4π (커널 규격)
        lmax = float(np.max(self.st.lG))
        lg = self.st.lG - lmax
        if v_b is None or not np.any(v_b):
            J = np.exp(lg)[:, None, None] * self.Jhat
            out = PL.collide(e, w, J, float(nu_dtau))
            tr = np.einsum("aii->a", out)
            self.st.lG = lmax + np.log(np.maximum(tr, 1e-300))
            self.Jhat = out / np.maximum(tr, 1e-300)[:, None, None]
            return self
        # ── P9b: 정지계로 옮겨 충돌하고 되돌린다
        v_b = np.asarray(v_b, float)
        Jh_r, e_r, D = boost_shape(self.Jhat, v_b, e)
        lg_r = lg + 4.0 * np.log(D)                 # Ĝ′ = 𝒟⁴ Ĝ
        w_r = w / D ** 2                            # dΩ′ = dΩ / 𝒟²
        w_r = w_r * (4.0 * np.pi / float(w_r.sum()))
        ref = float(np.max(lg_r))
        J_r = np.exp(lg_r - ref)[:, None, None] * Jh_r
        out = PL.collide(e_r, w_r, J_r, float(nu_dtau))
        tr = np.einsum("aii->a", out)
        lg_out = ref + np.log(np.maximum(tr, 1e-300))
        Jh_out = out / np.maximum(tr, 1e-300)[:, None, None]
        # 되부스트 (−v_b): 정지계 노드가 원래 물리 방향으로 정확히 되돌아온다
        Jh_back, _, _ = boost_shape(Jh_out, -v_b, e_r)
        self.st.lG = lmax + (lg_out - 4.0 * np.log(D))
        self.Jhat = Jh_back
        self._reproject()
        return self

    # ─────────────────────────────────────────────────────────── 결합
    def strang_step(self, dtau, nu=0.0, v_b=None):
        h = abs(dtau)
        self.collide(0.5 * nu * h, v_b)
        self.residual_step(0.5 * dtau)
        self.rk4_step(dtau)
        self.residual_step(0.5 * dtau)
        self.collide(0.5 * nu * h, v_b)
        return self


def evolve(ps, dtau, nsteps, nu=0.0, v_b=None):
    for _ in range(int(nsteps)):
        ps.strang_step(dtau, nu, v_b)
    return ps


# ═══════════════════════════════════════════════ P9c · Mode B 편광
def collide_modeb(e, w, J, n_p, x, backend="rust"):
    """Mode B (운동량 격자) 편광 충돌.  J: (M, n_p, 3, 3) 또는 (M*n_p, 3, 3).

    Thomson 핵은 **에너지 교환이 없으므로** 반경 슬라이스마다 같은 연산자다 —
    Mode A 커널을 n_p 번 부르는 것과 **정확히** 같아야 한다 (게이트).
    `backend='python'` 은 참조 구현 (비트급 대조 대상).  두 legacy 별칭은
    각각 명시적 ``rust_required`` / ``python_oracle`` 정책으로 정규화된다."""
    J = np.asarray(J, float).reshape(len(w), int(n_p), 3, 3)
    if not isinstance(backend, (str, BackendPolicy)):
        raise BackendPolicyError(
            "q.polstate.collide_modeb",
            f"backend {backend!r} is not a backend policy; use 'rust', 'python', or a "
            "typed BackendPolicy value",
        )
    aliases = {
        "rust": BackendPolicy.RUST_REQUIRED,
        "python": BackendPolicy.PYTHON_ORACLE,
    }
    selection = select_backend(
        "q.polstate.collide_modeb", policy=aliases.get(backend, backend)
    )
    if selection.policy is BackendPolicy.PYTHON_ORACLE:
        out = np.empty_like(J)
        for jj in range(int(n_p)):
            out[:, jj] = PL.collide(e, w, J[:, jj], float(x))
        return out
    R = selection.native_module
    if R is None:  # select_backend is fail-closed; this guards its return contract.
        raise AssertionError("rust_required selection returned no native module")
    flat = PL.pack9(J.reshape(-1, 3, 3)).ravel()
    o = np.asarray(R.qp_collide_modeb(
        np.ascontiguousarray(np.asarray(e, float).ravel()),
        np.ascontiguousarray(np.asarray(w, float)),
        np.ascontiguousarray(flat), int(n_p), float(x)))
    return PL.unpack9(o.reshape(-1, 9)).reshape(len(w), int(n_p), 3, 3)

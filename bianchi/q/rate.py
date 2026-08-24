"""
Q19 · **B2b 이력 배선** (85차) — x_e(z) 를 실제 적분기까지 잇는 유일한 경로.

★★ 이 모듈이 존재하는 이유 (반증 기록)
84차까지 "B2b 이력이 코드 수정 없이 꽂힌다" 고 적었고 Q15 시험은
    c = Collision.thomson(hist, nu=1.0);  assert m.collision.history is hist;  run(m)
까지만 봤다.  **객체/API 접합 수준에서는 참**이지만, `Model.run()` → Mode A/B
evolve 경로를 따라가면 적분기에 들어가는 것은 여전히 **상수** `collision.nu` 였다.
저장소 전체에 `collision.history` 를 읽어 `thomson_rate(hist, z)` 를 매 스텝
계산하는 경로가 **없었다**.  즉 시간의존 x_e(z) → ν_τ(z) → 충돌 진화까지는
닫혀 있지 않았다.  이 모듈이 그 구간이다.

═══ τ ↔ z (정확) ═══
τ 는 dτ = H dt 로 정의되고 H = d ln a/dt 이므로

    d ln a/dτ = 1        ⇒     ln a(τ) = ln a(τ₀) + (τ − τ₀)
    1 + z(τ) = (1 + z₀) e^{−(τ−τ₀)}

★ 근사가 아니다.  이방 배경에서도 a 는 H = ȧ/a 로 정의된 **평균** 척도인자이므로
  이 관계는 정의에서 곧바로 나온다.

═══ ν_τ = σ_T n_e c / H ═══
n_e = x_e(z) n_H(z) 는 외부 모듈 (B2b) 이 주는 x_e(z) 로 결정된다.  H 는 두 가지가
가능하고 **기본은 모델 자체 H** 다:

  mode="model"  (기본):  H(τ) = H_anchor · e^{lnH(τ) − lnH(τ₀)}
      적분기 상태의 lnH 를 쓴다 ⇒ **이방 배경과 자기일관**.  계약 §1 의
      NO_APPROXIMATION 이 요구하는 쪽 (ΛCDM H 를 몰래 대입하지 않는다).
      H_anchor 는 차원을 붙이는 앵커일 뿐이고 `describe()` 가 인쇄한다.

  mode="lcdm":  H(z) = ΛCDM (history_api 내장과 같은 식)
      외부 모듈의 τ(z)·가시함수와 **정확히** 같은 규약 ⇒ 대조 게이트용.
      이방 배경에서는 숨은 근사이므로 기본값이 아니다.

두 모드의 차이는 `compare_modes()` 가 실측한다 (숨기지 않는다).

═══ lane (87차, 외부 리뷰 C5) ═══
`lane` 은 **필수**다.  두 lane 을 섞으면 재결합 이동이 anisotropic physics 인지
H normalization 차이인지 구분할 수 없기 때문이다.

  lane="internal"       Gauss 구속이 정하는 H 앵커 (Omega_0 에서 유도).
                        "이 기하가 스스로 만드는 재결합 이동" 을 묻는 계산.
                        H_0 가 관측값과 달라도 **정상**이다.
                        외부 H_anchor 지정은 **거절**한다.
  lane="phenomenology"  관측 calibrate 된 (H_0, Omega_i) 앵커.
                        관측과 직접 비교하는 계산.
                        초기자료의 Omega_0 가 앵커와 어긋나면 **예외**를 던진다.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from bianchi.thermo import history_api as HA


@dataclass
class Cosmology:
    """ν_τ 에 차원을 붙이는 데 필요한 최소 집합 (전부 명시)."""

    z0: float = 1500.0            # τ = τ₀ 에서의 적색이동
    h: float = 0.674
    Omega_b_h2: float = 0.0224
    Omega_m_h2: float = 0.143

    def H_lcdm(self, z):
        """ΛCDM H(z) [1/s] — 앵커 및 mode='lcdm' 용."""
        from bianchi.physical import units as U
        from bianchi.thermo import recombination as REC
        z = np.asarray(z, float)
        Om = self.Omega_m_h2 / self.h ** 2
        Or = REC._OMEGA_R_H2 / self.h ** 2
        OL = 1.0 - Om - Or
        return (100.0 * self.h / U.MPC_KM) * np.sqrt(
            Or * (1 + z) ** 4 + Om * (1 + z) ** 3 + OL)

    def rho_rad(self, z):
        """복사 (광자 + 무질량 ν) 밀도 — Ω = ρ/(3H²) 와 **같은 단위**로.

        ρ_r(z) = 3 H_ΛCDM(z)² · Ω_r(z) 로 정의하면 단위 변환이 필요 없다
        (Ω_r(z) 는 무차원 비율이므로 규약 사고가 원천 봉쇄된다)."""
        from bianchi.thermo import recombination as REC
        z = np.asarray(z, float)
        Om = self.Omega_m_h2 / self.h ** 2
        Or = REC._OMEGA_R_H2 / self.h ** 2
        OL = 1.0 - Om - Or
        E2 = Or * (1 + z) ** 4 + Om * (1 + z) ** 3 + OL
        return 3.0 * self.H_lcdm(z) ** 2 * (Or * (1 + z) ** 4 / E2)


class RateSchedule:
    """ν_τ(τ, lnH) — 이력이 적분기로 들어가는 **유일한** 통로.

    `sample()` 이 스텝 경계 τ_k (k = 0..nsteps) 의 배열을 준다.  Strang 앞
    반스텝은 (τ_k, lnH_k), 뒤 반스텝은 (τ_{k+1}, lnH_{k+1}) 을 쓴다 — 대칭이라
    2차가 보존된다.
    """

    def __init__(self, hist, cosmo=None, tau0=0.0, lnH0=0.0, mode="model",
                 H_anchor=None, Omega0=None, strict_history=True, lane=None):
        if hist is None:
            raise ValueError("RateSchedule 은 이력이 있어야 한다 "
                             "(상수 ν 는 Collision.nu 를 쓴다)")
        if mode not in ("model", "lcdm"):
            raise ValueError("mode 는 'model' 또는 'lcdm'")
        # ★★ 87차 (외부 리뷰 C5): **lane 은 필수**다.
        #   두 lane 을 섞으면 나중에 재결합 이동을 봤을 때 그것이 anisotropic
        #   physics 인지 그냥 H normalization 을 다르게 준 것인지 **구분할 수
        #   없다**.  기본값을 두지 않는 이유가 그것이다 — 명시하게 만든다.
        if lane not in ("internal", "phenomenology"):
            raise ValueError(
                "lane 은 필수다 (기본값 없음).  "
                "'internal' = Gauss 구속이 정하는 H (이 기하가 스스로 만드는 "
                "재결합 이동을 묻는 계산; H_0 가 관측값과 달라도 정상), "
                "'phenomenology' = 관측 calibrate 된 (H_0, Omega_i) 앵커 "
                "(관측과 직접 비교하는 계산).  docs/REVIEW-RESPONSE-87.md C5")
        if strict_history:
            rep = HA.validate_history(hist, strict=False)
            checks = rep.get("checks", rep)
            bad = [k for k, v in checks.items() if v is False]
            if bad:
                raise ValueError(
                    f"이력이 B2b 계약을 만족하지 않는다: {bad}.  "
                    "특히 range_guard 가 False 면 범위 밖에서 **조용히 clamp** 하는 "
                    "모듈이라 배선이 틀린 답을 낸다.  "
                    "의도적이면 strict_history=False 로 명시하라.")
        self.hist = hist
        self.cosmo = cosmo or Cosmology()
        self.tau0 = float(tau0)
        self.lnH0 = float(lnH0)
        self.mode = mode
        self.lane = lane
        # ── lane 별 앵커 규칙 (조용한 혼합 금지)
        if lane == "internal":
            if H_anchor is not None and not (isinstance(H_anchor, str)
                                             and H_anchor == "gauss"):
                raise ValueError(
                    "lane='internal' 은 **Gauss 구속이 정하는 앵커만** 쓴다 — "
                    "외부 H_anchor 지정은 거절한다.  관측 앵커를 쓰려면 "
                    "lane='phenomenology' 로 명시하라.")
            if Omega0 is None or not (Omega0 > 0):
                raise ValueError("lane='internal' 은 Gauss 면의 Omega0 > 0 이 필요하다")
            self.H_anchor = float(np.sqrt(self.cosmo.rho_rad(self.cosmo.z0)
                                          / (3.0 * float(Omega0))))
            self.anchor_source = f"gauss(Omega0={float(Omega0):.4g})"
        else:                                    # phenomenology
            if H_anchor is None:
                self.H_anchor = float(self.cosmo.H_lcdm(self.cosmo.z0))
                self.anchor_source = "lcdm(z0)"
            elif isinstance(H_anchor, str):
                raise ValueError("lane='phenomenology' 에서 H_anchor 문자열은 금지 "
                                 "(관측 calibrate 된 값 또는 None)")
            else:
                self.H_anchor = float(H_anchor)
                self.anchor_source = "explicit"
            # Omega 정합 검사 — 경고가 아니라 **예외**
            if Omega0 is not None:
                om_implied = float(self.cosmo.rho_rad(self.cosmo.z0)
                                   / (3.0 * self.H_anchor ** 2))
                rel = abs(om_implied / float(Omega0) - 1.0)
                self.anchor_consistency = rel
                if rel > 1e-3:
                    raise ValueError(
                        f"lane='phenomenology' 인데 초기자료의 Omega_0 = "
                        f"{float(Omega0):.4g} 가 앵커가 함의하는 "
                        f"{om_implied:.4g} 와 {rel:.1%} 어긋난다.  "
                        "관측 calibrate 된 (H_0, Omega_i) 와 정합하는 Bianchi "
                        "초기자료에서 시작해야 한다 (또는 lane='internal').")
        if not (self.H_anchor > 0.0) or not np.isfinite(self.H_anchor):
            raise ValueError(f"H_anchor > 0 이어야 한다 (받은 값 {self.H_anchor})")

    # ─────────────────────────────────────────────────────────── τ ↔ z
    def z_of(self, tau):
        """1 + z = (1+z₀)e^{−(τ−τ₀)} — d ln a/dτ = 1 에서 **정확**."""
        return (1.0 + self.cosmo.z0) * np.exp(
            -(np.asarray(tau, float) - self.tau0)) - 1.0

    def tau_of(self, z):
        return self.tau0 - np.log((1.0 + np.asarray(z, float))
                                  / (1.0 + self.cosmo.z0))

    # ─────────────────────────────────────────────────────── 충돌률
    def A_of(self, tau):
        """A(τ) = σ_T n_e(z(τ)) c  [1/s] — τ 만의 함수 (상태 무관).

        ★ 모양 보존: 스칼라 in → 스칼라 out (다운스트림의 조용한 shape 버그 방지)."""
        scalar = np.ndim(tau) == 0
        z = np.atleast_1d(self.z_of(tau))
        # ★★ 85차 (독립 리뷰 M2): 예전엔 np.maximum(z, 0) 로 눌렀다.  z<0 은
        #   물리적으로 불가능한 요청이고, 누르면 ν 가 **얼어붙은 채** 계속 돈다
        #   (τ 를 더 진행해도 A 가 4.10e−21 로 고정).  게다가 validate_span 이
        #   같은 clamp 를 쓰고 있어 끝점 검사가 이것을 구조적으로 못 잡았다.
        if float(np.min(z)) < 0.0:
            raise ValueError(
                f"z(τ) < 0 (최소 {float(np.min(z)):.4g}) — τ 가 z₀ 로부터 "
                f"ln(1+z₀)={np.log1p(self.cosmo.z0):.4g} 를 넘어 진행했다.  "
                "clamp 하지 않는다 (조용히 ν 가 얼어붙는다).")
        xe = np.atleast_1d(np.asarray(self.hist.x_e(z), float))
        out = (HA.SIGMA_T_CM2 * xe * HA.n_H_cm3(z, self.cosmo.Omega_b_h2)
               * HA.C_CM_S)
        out = np.asarray(out, float).reshape(z.shape)
        return float(out[0]) if scalar else out

    def nu(self, tau, lnH=None):
        """ν_τ.  mode='model' 이면 lnH 가 **필요**하다 (상태 결합)."""
        if self.mode == "lcdm":
            z = self.z_of(tau)
            out = self.A_of(tau) / self.cosmo.H_lcdm(z)
            return float(out) if np.ndim(tau) == 0 else out
        if lnH is None:
            raise ValueError("mode='model' 은 상태의 lnH 가 필요하다 "
                             "(ΛCDM 로 몰래 대체하지 않는다)")
        out = self.A_of(tau) / (self.H_anchor
                                * np.exp(np.asarray(lnH, float) - self.lnH0))
        return float(out) if np.ndim(tau) == 0 and np.ndim(lnH) == 0 else out

    # ───────────────────────────────────── 정의역 검사 (빨리 실패)
    def validate_span(self, dtau, nsteps):
        """run 의 τ 구간이 이력의 z 지지집합 안에 있는지 **먼저** 확인한다.

        ★ 이게 없으면 20분짜리 run 이 중간에 `z 범위 밖 요청` 으로 죽거나 (좋은 경우),
        누가 clamp 를 넣으면 **조용히 틀린 ν** 로 끝까지 돈다 (나쁜 경우).
        스케줄을 만드는 시점에 양 끝을 찔러 보고, 실패하면 요구 z 구간을 담아
        다시 던진다."""
        tau = self.tau0 + float(dtau) * np.array([0.0, float(nsteps)])
        z = self.z_of(tau)
        lo, hi = float(np.min(z)), float(np.max(z))
        if lo < 0.0:
            raise ValueError(f"run 구간이 z<0 으로 간다 (최소 {lo:.4g}) — "
                             f"τ 폭이 ln(1+z₀)={np.log1p(self.cosmo.z0):.4g} 를 넘는다")
        try:
            self.hist.x_e(np.array([lo, hi]))
        except Exception as exc:                    # noqa: BLE001 — 메시지 보강 후 재던짐
            raise ValueError(
                f"이력의 z 지지집합이 run 구간을 못 덮는다: 필요 z ∈ [{lo:.4g}, {hi:.4g}] "
                f"(τ₀={self.tau0:g}, dτ={dtau:g}, nsteps={nsteps}).  "
                f"원 오류: {exc}"
            ) from exc
        return lo, hi

    # ─────────────────────────────────────── 적분기에 넘길 스케줄
    def sample(self, dtau, nsteps):
        """(sched, h_anchor).

        mode='model':  sched = A(τ_k) [1/s],  h_anchor = H_anchor·e^{−lnH₀}
                       ⇒ 커널이 ν = A/(h_anchor·e^{lnH}) 를 매 스텝 계산.
        mode='lcdm' :  sched = ν_τ(τ_k) 자체,  h_anchor = 0.
        """
        self.validate_span(dtau, nsteps)
        tau = self.tau0 + float(dtau) * np.arange(int(nsteps) + 1, dtype=float)
        if self.mode == "lcdm":
            return np.ascontiguousarray(self.nu(tau)), 0.0
        return (np.ascontiguousarray(self.A_of(tau)),
                self.H_anchor * float(np.exp(-self.lnH0)))

    # ───────────────────────────────────────────────────── 진단
    def optical_depth_along(self, dtau, nsteps, lnH_of=None):
        """∫|ν_τ dτ| (사다리꼴).

        ★ 물리 항등: dτ_광학 = σ_T n_e c dt = ν_τ dτ  ⇒ 이 적분이 **광학깊이**다.
        `history_api.optical_depth` 와 대조하면 배선 전체가 한 번에 검증된다."""
        tau = self.tau0 + float(dtau) * np.arange(int(nsteps) + 1, dtype=float)
        lnH = None if lnH_of is None else np.asarray([lnH_of(t) for t in tau], float)
        nu = np.atleast_1d(self.nu(tau, lnH))
        nu = np.asarray(nu, float).ravel()
        trap = getattr(np, "trapezoid", None) or np.trapz
        return abs(float(trap(nu, tau)))

    def compare_modes(self, dtau, nsteps, lnH_of):
        """모델 H 와 ΛCDM H 가 주는 ν 의 상대차 (숨은 근사의 크기를 잰다)."""
        tau = self.tau0 + float(dtau) * np.arange(int(nsteps) + 1, dtype=float)
        lnH = np.asarray([lnH_of(t) for t in tau], float)
        a = self.A_of(tau) / (self.H_anchor * np.exp(lnH - self.lnH0))
        b = self.A_of(tau) / self.cosmo.H_lcdm(self.z_of(tau))
        d = np.abs(a - b) / np.maximum(np.abs(b), 1e-300)
        return dict(max_rel=float(d.max()), mean_rel=float(d.mean()),
                    nu_model=a, nu_lcdm=b, tau=tau)

    def describe(self):
        return (f"B2b 이력 배선 [lane={self.lane}]: "
                f"{getattr(self.hist, 'name', type(self.hist).__name__)}"
                f"  mode={self.mode}"
                f"  z₀={self.cosmo.z0:g}"
                f"  H_anchor={self.H_anchor:.4g} 1/s [{self.anchor_source}]"
                + ("  (H 의 **모양**은 모델, **규모**는 위 앵커)" if self.mode == "model"
                   else "  (ΛCDM H(z) — 외부 모듈 규약 일치, 이방 배경엔 숨은 근사)"))

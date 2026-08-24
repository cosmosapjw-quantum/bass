"""
Q15 · **Python 프론트엔드** (76차).

규율: Python 은 설정·조립·분석만.  스텝 루프는 Rust 커널이 돈다 (R5b).
`Model.summary()` 가 적용된 규약·모드·가정을 **전부 인쇄**한다 — 편의 API 가
물리 규약을 숨기지 못하게.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from bianchi.q import coupled as QC
from bianchi.q import integrate as QI
from bianchi.q import sphere as S
from bianchi.q import species as SP


@dataclass
class Grid:
    n_theta: int = 24
    n_phi: int = 48
    n_p: int = 0                    # 0 이면 Mode A (반경격자 없음)
    lnq_min: float = -6.0
    lnq_max: float = 4.0

    def build(self):
        if self.n_phi % 2:
            raise ValueError("n_phi 는 짝수 (극 반사 규약)")
        return S.sphere(self.n_theta, self.n_phi)

    def mode(self):
        return "B" if self.n_p else "A"


@dataclass
class Collision:
    kernel: str = "thomson"
    nu: float = 0.0
    history: object = None          # B2b IonizationHistory (덕 타이핑)
    v_b: np.ndarray = None
    #: Q19 · ν_τ = σ_T n_e c / H 의 H 규약.  "model" = 모델 자체 H (자기일관, 기본),
    #: "lcdm" = ΛCDM H(z) (외부 모듈 규약과 일치하지만 이방 배경엔 숨은 근사).
    rate_mode: str = "model"

    @staticmethod
    def thomson(hist=None, nu=0.0, rate_mode="model"):
        """★ Q19: `hist` 를 주면 ν 는 **매 스텝 이력에서** 계산된다.

        85차 이전에는 이 객체가 이력을 보관만 하고 적분기는 상수 `nu` 를 썼다 —
        접합은 되었지만 소비가 안 되던 구간이 여기서 닫힌다.  `nu` 는 이력이
        없을 때만 쓰이는 상수 대체값이다."""
        return Collision("thomson", nu, hist, rate_mode=rate_mode)

    @staticmethod
    def none():
        return Collision("thomson", 0.0, None)


@dataclass
class Model:
    type: str = "I"
    sigma: np.ndarray = None
    n: np.ndarray = None
    a: np.ndarray = None
    grid: Grid = field(default_factory=Grid)
    collision: Collision = field(default_factory=Collision.none)
    species: list = field(default_factory=list)
    tau_span: tuple = (0.0, -10.0)
    nsteps: int = 2000
    lnH: float = 0.0
    #: Q19 · 이력을 쓸 때 ν 에 차원을 붙이는 데 필요한 최소 집합 (전부 명시).
    cosmology: object = None
    #: Q20 · H 앵커 **lane** (87차, 외부 리뷰 C5).  이력을 쓸 때 **필수**다.
    #: "internal" = Gauss 구속이 정하는 H, "phenomenology" = 관측 calibrate 된 앵커.
    lane: str = None
    #: Q19 · ν 의 **절대 규모**를 정하는 앵커.  None = ΛCDM H(z₀) (외부 모듈
    #: 대조 기준선), "gauss" = 모델 자신의 Ω₀ 에서 유도 (자기일관), 또는 값 [1/s].
    #: ★ 앵커는 "차원만 붙이는 것" 이 아니다 — `summary()` 가 출처를 인쇄한다.
    H_anchor: object = None

    def __post_init__(self):
        from bianchi import algebra as AL
        # ★ 85차 (독립 리뷰 m6): 이력이 없으면 rate_mode 가 검증되지 않아
        #   오타가 조용히 통과했다.  이력 유무와 무관하게 여기서 막는다.
        if self.collision.rate_mode not in ("model", "lcdm"):
            raise ValueError("Collision.rate_mode 는 'model' 또는 'lcdm'")
        if self.n is None or self.a is None:
            if self.type not in AL.CANONICAL:
                raise ValueError(f"알 수 없는 유형 {self.type} — "
                                 f"{list(AL.CANONICAL)}")
            n, a = AL.CANONICAL[self.type]
            self.n = np.diag(np.asarray(n, float) * 0.3) if self.n is None else self.n
            self.a = np.asarray(a, float) * 0.3 if self.a is None else self.a
        if self.sigma is None:
            self.sigma = (np.diag([0.0, 0.15, -0.15]) if np.any(self.a)
                          else np.diag([0.2, -0.1, -0.1]))
        self.n = np.atleast_2d(self.n) if np.ndim(self.n) == 2 else np.diag(np.ravel(self.n))

    # ------------------------------------------------------------------
    def schedule(self):
        """Q19 · 이력이 있으면 `RateSchedule`, 없으면 None (상수 ν 경로).

        ★ 이것이 x_e(z) 가 적분기로 들어가는 **유일한** 통로다."""
        if self.collision.history is None:
            return None
        from bianchi.q.rate import Cosmology, RateSchedule
        om0 = None
        if self.lane == "internal" or (isinstance(self.H_anchor, str)
                                       and self.H_anchor == "gauss"):
            import numpy as _np
            K, _ = QC.QState(self.grid.build(), self.sigma, self.n,
                             self.a, self.lnH).curvature()
            om0 = 1.0 - float(_np.trace(_np.asarray(self.sigma)
                                        @ _np.asarray(self.sigma)) / 6.0) - K
        return RateSchedule(self.collision.history,
                            self.cosmology or Cosmology(),
                            tau0=float(self.tau_span[0]), lnH0=float(self.lnH),
                            mode=self.collision.rate_mode,
                            H_anchor=self.H_anchor, Omega0=om0, lane=self.lane)

    def build(self):
        """Mode A 면 QState, Mode B 면 ModeBState — 둘 다 같은 Rust 전-루프로 간다."""
        sph = self.grid.build()
        if self.grid.n_p:
            from bianchi.q.modeb import planck_state
            return planck_state(sph, n_p=self.grid.n_p,
                                lnq_min=self.grid.lnq_min,
                                lnq_max=self.grid.lnq_max,
                                Sigma=self.sigma, N=self.n, A=self.a,
                                lnH=self.lnH)
        st0 = QC.QState(sph, self.sigma, self.n, self.a, self.lnH)
        K, _ = st0.curvature()
        Om0 = 1.0 - float(np.trace(np.asarray(self.sigma) @ np.asarray(self.sigma)) / 6.0) - K
        if Om0 <= 0:
            raise ValueError(f"Gauss 면 위 Ω₀ = {Om0:.4g} ≤ 0 — 초기자료 불가")
        return QC.on_gauss_surface(sph, self.sigma, self.n, self.a, Om0, self.lnH)

    def summary(self):
        """★ 숨은 가정 금지 — 적용된 규약·모드·근사 여부를 전부 인쇄."""
        from bianchi.q import contract as C
        sched = self.schedule()
        mode = ("B (완전 f — 분광 관측량 가능, 자유흐름 정확 항등)"
                if self.grid.n_p else "A (에너지-가중 각밀도 — 1모멘트)")
        lines = [
            f"Bianchi {self.type}  ·  τ ∈ {self.tau_span}  ·  {self.nsteps} 스텝",
            f"격자: {self.grid.n_theta}×{self.grid.n_phi} 방향"
            + (f" × {self.grid.n_p} 반경" if self.grid.n_p else "") + f"   Mode {mode}",
            f"충돌: {self.collision.kernel}  "
            + (sched.describe() + "  ⇒ ν 는 **매 스텝** 계산 (상수 아님)"
               if sched is not None else f"ν={self.collision.nu} (상수 — 이력 없음)"),
            f"프레임: 공변 (H·Σ·R 흡수, 보간 0회)   상태: ln Ĝ (로그공간)",
            "절단 없음: " + ", ".join(C.NO_APPROXIMATION),
            "남는 이산화 축: " + ", ".join(C.DISCRETIZATION),
            "잔여 곡률 이류: 켬 (Q5b) — class B Codazzi 는 각 해상도로 수렴 (2.45차)",
        ]
        return "\n".join(lines)


def run(model: Model, events=(), keep_every=0, fast=True):
    """단일 run.  `fast=True` 면 **Rust 전-루프** (Python 스텝 루프 0회).

    사건 검출이 필요하면 fast=False (Python 참조 적분기가 사건을 잡는다)."""
    st = model.build()
    t0, t1 = model.tau_span
    dtau = (t1 - t0) / model.nsteps
    # ★★ Q19: 이력이 있으면 여기서 **소비**된다.  85차 이전에는 이 줄이 없어서
    #   `collision.history` 가 보관만 되고 적분기는 상수 ν 를 썼다.
    sched = model.schedule()
    if model.grid.n_p:
        from bianchi.q import modeb as MB
        st.v_b = model.collision.v_b if st.v_b is None else st.v_b
        st, traj = MB.evolve(st, dtau, model.nsteps, nu=model.collision.nu,
                             kernel=model.collision.kernel,
                             keep_every=keep_every, sched=sched)
        return st, traj, []
    if fast and not events:
        from bianchi.q import fast as QF
        st, traj = QF.evolve(st, dtau, model.nsteps, nu=model.collision.nu,
                             kernel=model.collision.kernel,
                             keep_every=keep_every, sched=sched,
                             v_b=model.collision.v_b)
        return st, traj, []
    return QI.integrate(st, dtau, model.nsteps, nu=model.collision.nu,
                        kernel=model.collision.kernel, events=events,
                        keep_every=keep_every, v_b=model.collision.v_b,
                        sched=sched)

"""
Q9 · **다성분 볼츠만** — component 별 f (76차).

사용자 규정의 "각 cosmological component별 boltzmann 방정식들".
종마다 독립 격자 상태를 갖고, 종별로 Mode·질량·충돌을 고른다.
유체로 다루는 것이 정확한 성분 (Λ, 단일흐름 CDM) 은 `Kind.FLUID` 로 **명시** —
"격자인 척" 하지 않는다.

성분간 운동량 교환은 H'2 의 `exchange_R` 계약을 승계 (κ 대칭·영대각 ⇒ ΣQ = 0 구조적).
"""
from __future__ import annotations

import enum

import numpy as np

from bianchi.q import comoving as CM
from bianchi.q import sphere as S


class Kind(enum.Enum):
    PHOTON = "photon"
    NEUTRINO = "neutrino"
    CDM = "cdm"
    BARYON = "baryon"
    DARK_ENERGY = "dark_energy"
    FLUID = "fluid"


#: 종별 기본 상태방정식 (𝒫/Ω) — 격자 종은 구적이 결정하므로 참고값.
W_DEFAULT = {Kind.PHOTON: 1 / 3, Kind.NEUTRINO: 1 / 3, Kind.CDM: 0.0,
             Kind.BARYON: 0.0, Kind.DARK_ENERGY: -1.0, Kind.FLUID: 1 / 3}


class Species:
    """한 성분.  grid=True 면 격자 (절단 없음), 아니면 유체 캐리어."""

    __slots__ = ("kind", "mass", "grid", "lG", "w_eq", "nu", "name", "v")

    def __init__(self, kind, sph=None, mass=0.0, lG=None, w_eq=None,
                 nu=0.0, name=None, v=None):
        self.kind = Kind(kind) if not isinstance(kind, Kind) else kind
        self.mass = float(mass)
        self.grid = lG is not None or (sph is not None and
                                       self.kind in (Kind.PHOTON, Kind.NEUTRINO))
        self.lG = None if lG is None else np.asarray(lG, float)
        if self.grid and self.lG is None:
            self.lG = np.zeros(int(sph.n))
        self.w_eq = W_DEFAULT[self.kind] if w_eq is None else float(w_eq)
        self.nu = float(nu)
        self.name = name or self.kind.value
        self.v = np.zeros(3) if v is None else np.asarray(v, float)

    def is_grid(self):
        return self.grid and self.lG is not None


def exchange_Q(species, Omegas, kappa):
    """H'2 승계: R_c = Σ_d κ_cd Ω_c Ω_d (v_d − v_c).  Σ_c R_c = 0 구조적."""
    k = np.asarray(kappa, float)
    nc = len(species)
    if k.shape != (nc, nc):
        raise ValueError(f"kappa: ({nc},{nc}) 필요")
    if np.abs(k - k.T).max() > 0.0:
        raise ValueError("kappa 는 대칭이어야 한다 — 비대칭은 총 운동량 비보존")
    if np.abs(np.diag(k)).max() > 0.0:
        raise ValueError("kappa 대각은 0")
    V = np.stack([s.v for s in species])
    Om = np.asarray(Omegas, float)
    w = k * np.outer(Om, Om)
    return w @ V - np.sum(w, axis=1)[:, None] * V


def total_sources(species, sph, M, lnH):
    """Σ_c (Ω_c, Π_c) — 격자 종은 구적, 유체 종은 상태방정식."""
    qhat, w_com = S.nodes(sph)
    fr = CM.frame_from(M)
    e, mu = CM.phys(fr, qhat)
    lw = CM.ln_phys_weights(fr, w_com, mu)
    Om_tot, Pi_tot, P_tot, per = 0.0, np.zeros((3, 3)), 0.0, []
    for s in species:
        if s.is_grid():
            ln_rho, _, pi_r = CM.moments_log(lw, s.lG, e)
            Om = float(np.exp(ln_rho - np.log(3.0) - 2.0 * lnH))
            Pi = 3.0 * Om * pi_r
            P = s.w_eq * Om
        else:
            Om = float(getattr(s, "_omega", 0.0))
            Pi = np.zeros((3, 3))
            P = s.w_eq * Om
        Om_tot += Om
        Pi_tot = Pi_tot + Pi
        P_tot += P
        per.append((s.name, Om))
    return Om_tot, Pi_tot, P_tot, per

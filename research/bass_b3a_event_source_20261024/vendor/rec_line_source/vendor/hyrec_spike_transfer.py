"""Source-identical original-HyRec spike transfer with directional rescaling.

The October-2012 ``HyRec/hydrogen.c`` source computes the virtual-state optical
thickness in its FLRW redshift variable and updates the outgoing distortion as

``Dfminus = Dfplus + (Dfeq - Dfplus) * (1 - exp(-Dtau))``.

For a homogeneous anisotropic characteristic the delta-spike crossing time is
set by the local logarithmic frequency speed.  On a branch with no frequency
speed zero, the directional optical thickness is therefore the FLRW value
multiplied by ``H / abs(-d log(nu)/dt)``.  A zero or sign-changing speed is an
event and must be localized by the trajectory controller before this local map
is evaluated.
"""
from __future__ import annotations

from dataclasses import dataclass
import math


SOURCE_FILE = "HyRec/hydrogen.c"
SOURCE_LINES = (521, 524, 525, 780, 781, 787, 789)


@dataclass(frozen=True)
class SpikeTransferResult:
    f_out: float
    tau_directional: float
    transmission: float
    absorbed_fraction: float
    source_file: str = SOURCE_FILE
    source_lines: tuple[int, ...] = SOURCE_LINES


@dataclass(frozen=True)
class OriginalHyRecSpikeTransfer:
    """One original-HyRec virtual spike on a fixed characteristic branch."""

    tau_flrw: float
    f_equilibrium: float
    H_s_inv: float

    def __post_init__(self) -> None:
        tau = float(self.tau_flrw)
        equilibrium = float(self.f_equilibrium)
        hubble = float(self.H_s_inv)
        if not (math.isfinite(tau) and tau >= 0.0):
            raise ValueError("tau_flrw must be finite and nonnegative")
        if not math.isfinite(equilibrium):
            raise ValueError("f_equilibrium must be finite")
        if not (math.isfinite(hubble) and hubble > 0.0):
            raise ValueError("H_s_inv must be positive and finite")
        object.__setattr__(self, "tau_flrw", tau)
        object.__setattr__(self, "f_equilibrium", equilibrium)
        object.__setattr__(self, "H_s_inv", hubble)

    def directional_optical_depth(
        self,
        *,
        minus_dlognu_dt_s_inv: float,
    ) -> float:
        speed = float(minus_dlognu_dt_s_inv)
        if not math.isfinite(speed):
            raise ValueError("frequency speed must be finite")
        if speed == 0.0:
            raise ValueError(
                "frequency-speed zero requires event localization before spike transfer"
            )
        return self.tau_flrw * self.H_s_inv / abs(speed)

    def transfer(
        self,
        *,
        f_in: float,
        minus_dlognu_dt_s_inv: float,
    ) -> SpikeTransferResult:
        incoming = float(f_in)
        if not math.isfinite(incoming):
            raise ValueError("f_in must be finite")
        tau = self.directional_optical_depth(
            minus_dlognu_dt_s_inv=minus_dlognu_dt_s_inv
        )
        absorbed = -math.expm1(-tau)
        transmission = 1.0 - absorbed
        outgoing = incoming + (self.f_equilibrium - incoming) * absorbed
        return SpikeTransferResult(
            f_out=outgoing,
            tau_directional=tau,
            transmission=transmission,
            absorbed_fraction=absorbed,
        )

    def jvp(
        self,
        *,
        f_in: float,
        minus_dlognu_dt_s_inv: float,
        d_f_in: float = 0.0,
        d_f_equilibrium: float = 0.0,
        d_tau_flrw: float = 0.0,
        d_H_s_inv: float = 0.0,
        d_minus_dlognu_dt_s_inv: float = 0.0,
    ) -> float:
        incoming = float(f_in)
        speed = float(minus_dlognu_dt_s_inv)
        tau = self.directional_optical_depth(
            minus_dlognu_dt_s_inv=speed
        )
        transmission = math.exp(-tau)
        absorbed = 1.0 - transmission

        if self.tau_flrw == 0.0:
            d_tau = self.H_s_inv / abs(speed) * float(d_tau_flrw)
        else:
            d_tau = tau * (
                float(d_tau_flrw) / self.tau_flrw
                + float(d_H_s_inv) / self.H_s_inv
                - float(d_minus_dlognu_dt_s_inv) / speed
            )
        return (
            transmission * float(d_f_in)
            + absorbed * float(d_f_equilibrium)
            + (self.f_equilibrium - incoming) * transmission * d_tau
        )

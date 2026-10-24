"""Conservative Bianchi-I photon phase-space map in logarithmic form.

For a non-tilted normal-comoving axisymmetric Bianchi I background, the three
spatial translation Killing momenta are constant on free null geodesics.
The face -> initial map is exact in continuum (up to supplied finite-shear
clock quadrature and binary64 arithmetic), without a ray ODE integrator.

p_i = a exp(beta_i) E n_i, beta=(-b,-b,2b),
B=b_initial-b_face, R²=exp(2B)(1-mu_face²)+exp(-4B)mu_face².
E_initial/E_face=exp(L_face-L_initial)*R,
dOmega_initial/dOmega_face=R^-3.

The cubic product of energy ratio and angular Jacobian is the positive
volume factor exp(3 delta L); it is independent of B. It is NOT a photon
number/energy *integral* of an arbitrary collision-driven radiation field.
"""
from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np

from full_bianchi_hyrec.background.axisymmetric_bianchi_i import (
    AxisymmetricBianchiIBackground,
)


_METHOD="rec_lrs_bi_killing_phase_volume_v1"


@dataclass(frozen=True)
class AxisymmetricPhaseVolumeMap:
    """Immutable vector arrays, one face->initial free-streaming null map."""

    initial_directions: np.ndarray
    energy_initial_over_face: np.ndarray
    solid_angle_initial_over_face: np.ndarray
    cubic_phase_space_normalized: np.ndarray
    log_R: np.ndarray
    l_initial: float
    l_face: float
    delta_b_initial_minus_face: float
    method_identity: str = _METHOD

    def __post_init__(self):
        data={
            "initial_directions": (len(self.energy_initial_over_face),3),
            "energy_initial_over_face": (len(self.energy_initial_over_face),),
            "solid_angle_initial_over_face": (len(self.energy_initial_over_face),),
            "cubic_phase_space_normalized": (len(self.energy_initial_over_face),),
            "log_R": (len(self.energy_initial_over_face),),
        }
        for name,shape in data.items():
            arr=np.array(getattr(self,name),dtype=float,copy=True)
            if arr.shape!=shape or not np.all(np.isfinite(arr)):
                raise ValueError(f"invalid nonfinite phase map {name}")
            arr.setflags(write=False)
            object.__setattr__(self,name,arr)



@dataclass(frozen=True)
class PreparedAxisymmetricPhaseVolume:
    """Physically identified fixed-interval photon measure transform.

    Prepare the expensive positive-rate Bianchi-I shear quadrature exactly
    once for this source and endpoint pair, then evaluate arbitrarily many
    directional vectors without repeating background integration. The full
    source SHA and numerical method identity are explicit outputs.
    """

    model_source_sha256: str
    l_initial: float
    l_face: float
    delta_b_initial_minus_face: float
    delta_l: float
    method_identity: str = _METHOD

    def map(self, face_directions) -> AxisymmetricPhaseVolumeMap:
        face=np.asarray(face_directions,dtype=float)
        if face.ndim!=2 or face.shape[1]!=3 or face.shape[0]<1:
            raise ValueError("face_directions requires nonempty (N,3) rays")
        if not np.all(np.isfinite(face)):
            raise ValueError("nonfinite ray")
        lengths=np.linalg.norm(face,axis=1)
        if np.any(~np.isfinite(lengths)) or np.any(lengths<=0):
            raise ValueError("unnormalizable ray")
        unit=face/lengths[:,None]

        B=self.delta_b_initial_minus_face
        mu2=unit[:,2]*unit[:,2]
        # Analytically R²=exp(2B)[1+mu²*expm1(-6B)].
        # Computing log R via log1p retains tiny shear effects that are lost
        # when sqrt(R²) rounds to unity near machine precision.
        log_R=B+0.5*np.log1p(mu2*math.expm1(-6*B))
        log_energy=self.delta_l+log_R
        gamma=np.exp(log_energy)
        jac=np.exp(-3*log_R)
        initial=np.empty_like(unit)
        initial[:,:2]=unit[:,:2]*np.exp((B-log_R))[:,None]
        initial[:,2]=unit[:,2]*np.exp(-2*B-log_R)
        normalized=gamma*gamma*gamma*jac*math.exp(-3*self.delta_l)
        if (
            not np.all(np.isfinite(gamma))
            or not np.all(gamma>0)
            or not np.all(np.isfinite(jac))
            or not np.all(jac>0)
            or not np.all(np.isfinite(normalized))
        ):
            raise FloatingPointError("phase-volume transfer became nonfinite")
        return AxisymmetricPhaseVolumeMap(
            initial_directions=initial,
            energy_initial_over_face=gamma,
            solid_angle_initial_over_face=jac,
            cubic_phase_space_normalized=normalized,
            log_R=log_R,
            l_initial=self.l_initial,
            l_face=self.l_face,
            delta_b_initial_minus_face=B,
        )


def prepare_axisymmetric_phase_space_map(
    source: AxisymmetricBianchiIBackground,
    l_initial: float,
    l_face: float,
) -> PreparedAxisymmetricPhaseVolume:
    """Source-bound one-time positive-rate shear quadrature, then cheap maps."""
    if not isinstance(source,AxisymmetricBianchiIBackground):
        raise TypeError("source requires AxisymmetricBianchiIBackground")
    inc=source.interval_log(float(l_initial),float(l_face))
    return PreparedAxisymmetricPhaseVolume(
        model_source_sha256=source.source_sha256,
        l_initial=float(l_initial),
        l_face=float(l_face),
        delta_b_initial_minus_face=-inc.delta_b,
        delta_l=inc.delta_l,
    )


def axisymmetric_phase_space_map(
    source: AxisymmetricBianchiIBackground,
    l_initial: float,
    l_face: float,
    face_directions,
) -> AxisymmetricPhaseVolumeMap:
    """One-shot exact Bianchi-I energy/angle/phase-volume array.

    For many successive photon-array calls at identical fixed geometry,
    use prepare_axisymmetric_phase_space_map(...).map(face_directions)
    to avoid rerunning the scalar positive-rate shear integral.
    """
    return prepare_axisymmetric_phase_space_map(
        source,l_initial,l_face,
    ).map(face_directions)


__all__=(
    "AxisymmetricPhaseVolumeMap",
    "PreparedAxisymmetricPhaseVolume",
    "prepare_axisymmetric_phase_space_map",
    "axisymmetric_phase_space_map",
)

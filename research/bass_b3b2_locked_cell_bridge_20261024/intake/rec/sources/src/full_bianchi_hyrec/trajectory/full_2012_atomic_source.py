"""Source-equivalent FLRW HyRec October-2012 FULL hydrogen atomic one-step.

Reconstructs the **actual instant** populateTS_2photon -> solve_real_virt ->
outgoing history from the immutable original 2012 tables, reusing separately
verified REC effective atomic rates, 2-photon/Raman coupling, and diffusion.

State roles: 2 real and 311 virtual departures are algebraic at a single
proper thermodynamic state; the accepted fminus arrays are causal history.
The module does not solve a coupled time integration, He recombination, or
Bianchi photon collision. It requires q=0, fsR=meR=1 original source.

Public temperatures K, number density m^-3, H s^-1, photon occupations
dimensionless; source internal rate normalization is cgs + eV and s^-1.
All arrays exposed by results are immutable copies.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import math
from pathlib import Path

import numpy as np
from scipy.linalg import solve_banded

from full_bianchi_hyrec.recoil.original_hyrec_native import (
    populate_original_hyrec_diffusion,
)
from full_bianchi_hyrec.trajectory.hmla_flrw import (
    HMLAFlrwSource, KB_NATIVE_EV_K, LYA_FACT_CM3,
)
from full_bianchi_hyrec.trajectory.hyrec_two_photon_raman import (
    OriginalHyRecTwoPhotonRamanTable,
)
from full_bianchi_hyrec.trajectory.primitive_rates import (
    IONIZATION_ENERGY_EV, SAHA_COEFFICIENT_CGS,
)

NVIRT=311
START_DIFF=100
STOP_DIFF=180
LYA_BELOW=139
LYA_ABOVE=140
HPC_EV_CM=1.239841874331e-4
E32_EV=1.8886508433247664
E42_EV=2.5496786384884356


@lru_cache(maxsize=3)
def _canonical_twophoton_table(archive: Path) -> OriginalHyRecTwoPhotonRamanTable:
    return OriginalHyRecTwoPhotonRamanTable.from_archive(archive)


def _readonly(value, shape, name):
    array=np.asarray(value,dtype=np.float64)
    if array.shape != shape or not np.all(np.isfinite(array)):
        raise ValueError(f"{name}: invalid nonfinite array or shape")
    result=np.array(array,copy=True)
    result.setflags(write=False)
    return result


def _original_escape_factors(tau):
    """Literal October-2012 C source evaluation order, including rounding.

    The source switches at tau=1e-6 between a small-tau series and
    1-(1-exp(-tau))/tau. That latter expression exhibits cancellation in
    binary64 near the switch. This function deliberately reproduces the C
    order for strict source parity. The stable formulation is audited
    independently and NOT silently substituted into this historical source.
    """
    t=np.asarray(tau,dtype=float)
    if np.any(t<0) or not np.all(np.isfinite(t)):
        raise ValueError("invalid physical optical depth")
    p=np.empty_like(t)
    survive=np.empty_like(t)
    small=t<=1e-6
    p[small]=.5*t[small]-t[small]*t[small]/6.0
    survive[small]=t[small]-.5*t[small]*t[small]
    if np.any(~small):
        z=t[~small]
        # Scalar libm matches the original C exp() rounding at the branch.
        # NumPy's vector exp can differ by one ulp, which cancellation here
        # amplifies near tau=1e-6 in strict source-point parity checks.
        transmission=np.fromiter((math.exp(-float(value)) for value in z),
                                 dtype=np.float64,count=z.size)
        p[~small]=1.-(1.-transmission)/z
        survive[~small]=1.-transmission
    return p,survive


def accurate_escape_factors(tau):
    """Continuum-equivalent stable alternative, NOT original C binary64 mode.

    For t < 0.03, the power series removes cancellation in
      1 - (1-exp(-t))/t = t/2 - t^2/6 + t^3/24 - ...
    For larger depths the expm1 path has adequate precision.
    This is useful for science-focused stability studies, but the
    historical source-parity function above deliberately remains default.
    """
    t=np.asarray(tau,dtype=np.float64)
    if not np.all(np.isfinite(t)) or np.any(t<0):
        raise ValueError("invalid optical depth")
    p=np.empty_like(t)
    small=t<.03
    q=t[small]
    p[small]=q*(.5+q*(-1/6+q*(1/24+q*(-1/120
                        +q*(1/720-q/5040)))))
    if np.any(~small):
        z=t[~small]
        p[~small]=1+np.expm1(-z)/z
    survive=-np.expm1(-t)
    return p,survive


@dataclass(frozen=True)
class OriginalFullAtomicSnapshot:
    Trr: np.ndarray
    Trv: np.ndarray
    Tvr: np.ndarray
    Tvv: np.ndarray
    sr: np.ndarray
    sv: np.ndarray
    Dtau: np.ndarray
    Alpha_cgs: np.ndarray
    DAlpha_cgs: np.ndarray
    Beta_s_inv: np.ndarray
    incoming_virtual: np.ndarray
    incoming_lyman: np.ndarray
    nH_cgs: float
    H_s_inv: float
    xHII: float
    xe: float
    Tm_eV: float
    Tr_eV: float
    saha_ratio: float
    coupling_identity: str = "HyRec_Oct2012_FULL_populateTS_2photon_q0"

    def __post_init__(self):
        for name,shape in (
            ("Trr",(2,2)),("Trv",(2,NVIRT)),("Tvr",(2,NVIRT)),
            ("Tvv",(3,NVIRT)),("sr",(2,)),("sv",(NVIRT,)),
            ("Dtau",(NVIRT,)),("Alpha_cgs",(2,)),("DAlpha_cgs",(2,)),
            ("Beta_s_inv",(2,)),("incoming_virtual",(NVIRT,)),
            ("incoming_lyman",(2,)),
        ):
            object.__setattr__(self,name,_readonly(getattr(self,name),shape,name))
        if np.any(self.Dtau<0) or np.any(self.Tvv[0]<=0):
            raise ValueError("invalid virtual optical depth or diagonal")
        if not (0<=self.xHII<1 and self.xe>=self.xHII and self.H_s_inv>0
                and self.nH_cgs>0 and self.Tm_eV>0 and self.Tr_eV>0):
            raise ValueError("invalid thermodynamic reference state")

    def instantaneous_schur_solution(self):
        """2+311 algebraic solve with one **three-column 80-bin** LAPACK pass.

        No dense 311^3 inversion. Outside 100:180, Tvv is diagonal and
        exact division is used. The 80×80 tridiagonal diffusion region is
        solved for (sv,Tvr_2s,Tvr_2p) simultaneously, after which a 2×2
        Schur matrix remains. Respects Tvv[1]=sub and Tvv[2]=super.
        """
        # Three RHS columns; each virtual state's source and response to
        # the two real departures uses the SAME Tvv factorization.
        cols=np.column_stack((self.sv,self.Tvr.T))
        inv=np.empty_like(cols)
        inv[:START_DIFF]=cols[:START_DIFF]/self.Tvv[0,:START_DIFF,None]
        inv[STOP_DIFF:]=cols[STOP_DIFF:]/self.Tvv[0,STOP_DIFF:,None]
        diag=self.Tvv[0,START_DIFF:STOP_DIFF]
        lower=self.Tvv[1,START_DIFF:STOP_DIFF]
        upper=self.Tvv[2,START_DIFF:STOP_DIFF]
        ab=np.zeros((3,len(diag)),dtype=np.float64)
        ab[1]=diag
        ab[0,1:]=upper[:-1]
        ab[2,:-1]=lower[1:]
        inv[START_DIFF:STOP_DIFF]=solve_banded(
            (1,1),ab,cols[START_DIFF:STOP_DIFF],
            check_finite=False,overwrite_ab=True,
        )
        source_inv=inv[:,0]
        response_inv=inv[:,1:]
        schur=self.Trr-self.Trv@response_inv
        rhs=self.sr-self.Trv@source_inv
        det=float(np.linalg.det(schur))
        if not np.isfinite(det) or det<=0:
            raise FloatingPointError("source Schur complement determinant not positive")
        real=np.linalg.solve(schur,rhs)
        virtual=source_inv-response_inv@real
        if not np.all(np.isfinite(virtual)):
            raise FloatingPointError("nonfinite virtual population")
        return _readonly(real,(2,),"real"),_readonly(virtual,(NVIRT,),"virtual")

    def relative_matrix_residual(self,real,virtual):
        real=np.asarray(real,dtype=float)
        v=np.asarray(virtual,dtype=float)
        r=self.Trr@real+self.Trv@v-self.sr
        vv=self.Tvr.T@real+self.Tvv[0]*v-self.sv
        vv[1:]+=self.Tvv[1,1:]*v[:-1]
        vv[:-1]+=self.Tvv[2,:-1]*v[1:]
        lhs_scale=max(
            np.max(np.abs(self.sr)),np.max(np.abs(self.sv)),
            np.max(np.abs(self.Trr@real)),np.max(np.abs(self.Tvv[0]*v)),
            1e-280,
        )
        return float(max(np.max(np.abs(r)),np.max(np.abs(vv)))/lhs_scale)


@dataclass(frozen=True)
class FullOutgoingAtomicResult:
    real_departures: np.ndarray
    virtual_departures: np.ndarray
    outgoing_virtual: np.ndarray
    outgoing_lyman: np.ndarray
    average_virtual: np.ndarray
    dxHII_dln_a: float
    normalized_matrix_residual: float
    source_mode: str = "REC_HYREC2012_FULL_H_ATOMIC_SOURCE_STEP_NOT_TRAJECTORY"

    def __post_init__(self):
        for key,shape in (("real_departures",(2,)),
                          ("virtual_departures",(NVIRT,)),
                          ("outgoing_virtual",(NVIRT,)),
                          ("outgoing_lyman",(3,)),
                          ("average_virtual",(NVIRT,))):
            object.__setattr__(self,key,_readonly(getattr(self,key),shape,key))


def populate_original_full_atomic(
    source: HMLAFlrwSource, *, z:float,
    xHII:float, xe:float,Tm_K:float,
    incoming_virtual, incoming_lyman,
) -> OriginalFullAtomicSnapshot:
    """Original C populateTS_2photon including real/virtual/diffusion.

    The original quiescent q=0 Hubble and baryon density are used with the
    *same native source rates* as PR #91. The two-photon table has the same
    source archive SHA-256, normalized A2s value, and physical bin ordering.
    """
    incoming=_readonly(incoming_virtual,(NVIRT,),"fplus_virtual")
    ly=_readonly(incoming_lyman,(2,),"fplus_lyman")
    if not all(map(math.isfinite,(z,xHII,xe,Tm_K))):
        raise ValueError("nonfinite physical input")
    if not (z>=0 and 0<=xHII<1 and xe>=xHII and xe<=1+2*source.f_he
            and Tm_K>0 and Tm_K<=source.tcmb0_K*(1+z)*(1+1e-12)):
        raise ValueError("invalid physical xHII/xe/Tm input")
    H,nH_m3=source.cosmology(z)
    nH=nH_m3*1e-6
    Tr=KB_NATIVE_EV_K*source.tcmb0_K*(1+z)
    Tm=KB_NATIVE_EV_K*Tm_K
    x1s=1-xHII
    rate=source.table.evaluate(
        radiation_temperature_eV_rescaled=Tr,
        matter_to_radiation_temperature_ratio=Tm/Tr,
    )
    table=_canonical_twophoton_table(Path(source.table.archive_path))
    energy=table.energy_eV
    if not np.array_equal(rate.A1s_s_inv,table.A1s_s_inv):
        raise ValueError("atomic and photon source tables do not share identity")
    coupling=table.evaluate_canonical_coupling(radiation_temperature_eV=Tr)
    # C uses Tvr=-real->virtual, Trv=-virtual->real.
    Tvr=-np.array(coupling.real_to_virtual_s_inv,copy=True)
    Trv=-np.array(coupling.virtual_to_real_s_inv,copy=True)
    # The source's 80-bin tridiagonal diffusion rates are already available
    # from REC's independently ported original-C function.
    tab=np.column_stack((energy,table.integrated_rates_s_inv.T))
    diff=populate_original_hyrec_diffusion(tab,Tm_K)
    a_up=np.array(diff.Aup_s_inv,copy=True)
    a_dn=np.array(diff.Adn_s_inv,copy=True)
    ly_rate=LYA_FACT_CM3*H/(nH*x1s)
    beta=rate.beta_s_inv
    alpha=rate.alpha_m3_s*1e6
    dalpha=rate.delta_alpha_m3_s*1e6
    saha=(SAHA_COEFFICIENT_CGS*Tr*math.sqrt(Tr)
          *math.exp(-IONIZATION_ENERGY_EV/Tr)/nH)
    dxe2=xe*xHII-saha*x1s
    R=rate.R_2p2s_s_inv
    lyb=math.exp(-E32_EV/Tr)
    lyg=math.exp(-E42_EV/Tr)
    rr=np.array([
        [beta[0]+3*R+3*ly_rate*(1.664786871919931*lyb+1.953125*lyg),
         -R],
        [-3*R,beta[1]+R+ly_rate],
    ],dtype=float)
    # Original C adds the sum of -Tvr *before* line-centre diffusion rates.
    rr[0,0]-=float(np.sum(Tvr[0]))
    rr[1,1]-=float(np.sum(Tvr[1]))
    rr[1,1]+=diff.A2p_dn_s_inv+diff.A2p_up_s_inv
    sr=np.array([
        nH*(saha*x1s*dalpha[0]+alpha[0]*dxe2)
        +3*ly_rate*x1s*1.664786871919931*ly[1],
        nH*(saha*x1s*dalpha[1]+alpha[1]*dxe2)
        +3*ly_rate*x1s*ly[0],
    ],dtype=float)
    # Source C calculates Gamma and Delta_tau BEFORE adjusting the
    # neighboring Ly-alpha 2p/virtual couplings below.
    gamma=-(Trv[0]+Trv[1])+a_up+a_dn
    tau=(gamma*x1s*(HPC_EV_CM/energy)**3*nH/(8*math.pi*H))
    p_survive,_=_original_escape_factors(tau)
    vv=np.zeros((3,NVIRT),dtype=float)
    vv[0]=np.where(
        tau>0,gamma/np.maximum(p_survive,np.finfo(float).tiny),
        2/(x1s*(HPC_EV_CM/energy)**3*nH/(8*math.pi*H)),
    )
    vv[1,START_DIFF+1:LYA_BELOW+1]=-a_up[START_DIFF:LYA_BELOW]
    vv[1,LYA_ABOVE+1:STOP_DIFF]=-a_up[LYA_ABOVE:STOP_DIFF-1]
    vv[2,START_DIFF:LYA_BELOW]=-a_dn[START_DIFF+1:LYA_BELOW+1]
    vv[2,LYA_ABOVE:STOP_DIFF-1]=-a_dn[LYA_ABOVE+1:STOP_DIFF]
    # Cross-bin source 2p diffusion, exactly the native 139/140 branches.
    Tvr[1,LYA_BELOW]-=diff.A2p_dn_s_inv
    Trv[1,LYA_BELOW]-=a_up[LYA_BELOW]
    Tvr[1,LYA_ABOVE]-=diff.A2p_up_s_inv
    Trv[1,LYA_ABOVE]-=a_dn[LYA_ABOVE]
    sv=vv[0]*x1s*incoming*(1-p_survive)
    return OriginalFullAtomicSnapshot(
        Trr=rr,Trv=Trv,Tvr=Tvr,Tvv=vv,sr=sr,sv=sv,Dtau=tau,
        Alpha_cgs=alpha,DAlpha_cgs=dalpha,Beta_s_inv=beta,
        incoming_virtual=incoming,incoming_lyman=ly,
        nH_cgs=nH,H_s_inv=H,xHII=xHII,xe=xe,Tm_eV=Tm,
        Tr_eV=Tr,saha_ratio=saha,
    )


def complete_original_full_atomic(snapshot:OriginalFullAtomicSnapshot
                                  )->FullOutgoingAtomicResult:
    """Solve and generate an UNCOMMITTED outgoing history candidate."""
    r,v=snapshot.instantaneous_schur_solution()
    x1s=1-snapshot.xHII
    tau=snapshot.Dtau
    pi,transmit=_original_escape_factors(tau)
    eq=np.zeros(NVIRT,dtype=float)
    # Original C has a no-source exact transparent branch for tau<=1e-30.
    active=tau>1e-30
    neighbors=np.zeros(NVIRT,dtype=float)
    neighbors[1:]+=v[:-1]*snapshot.Tvv[1,1:]
    neighbors[:-1]+=v[1:]*snapshot.Tvv[2,:-1]
    eq[active]=(
        -(r@snapshot.Tvr[:,active])-neighbors[active]
    )/(x1s*pi[active]*snapshot.Tvv[0,active])
    outgoing=snapshot.incoming_virtual.copy()
    outgoing[active]+=(
        eq[active]-snapshot.incoming_virtual[active]
    )*transmit[active]
    ly_out=np.array([
        r[1]/(3*x1s),
        r[0]/x1s*math.exp(-E32_EV/snapshot.Tr_eV),
        r[0]/x1s*math.exp(-E42_EV/snapshot.Tr_eV)
    ])
    dx_e=-(np.sum(
        snapshot.nH_cgs*(
            snapshot.saha_ratio*x1s*snapshot.DAlpha_cgs
            +snapshot.Alpha_cgs*(snapshot.xe*snapshot.xHII-
                  snapshot.saha_ratio*x1s))
         -r*snapshot.Beta_s_inv
    ))/snapshot.H_s_inv
    return FullOutgoingAtomicResult(
        real_departures=r,virtual_departures=v,
        outgoing_virtual=outgoing,outgoing_lyman=ly_out,
        average_virtual=v/x1s,dxHII_dln_a=float(dx_e),
        normalized_matrix_residual=snapshot.relative_matrix_residual(r,v)
    )

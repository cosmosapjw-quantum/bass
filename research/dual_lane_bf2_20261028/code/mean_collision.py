"""BF2 exact common-frame mean collision decomposition, not a closure.

Use the unchanged BF1 positive spatial projector and KM2A cold polarized
Thomson generator. All cells refer to the SAME normal observer, physical
angular labels, and screen convention before this module is called.
nu=n_e_star*sigma_T*c is proper-density opacity, beta=v_e/c. Units may be
scaled consistently by T_star. No small-amplitude expansion, projection of
signed fluctuations, weight renormalization, PDE/Einstein evolution or
frequency-domain validity certification is performed here.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import sys
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'vendor'))
from spatial_projection import SpatialProjector
from tilted_collision import TiltedThomson,radiation_tensor,expected_fourforce


def _matter(nu,beta,count):
    nu=np.asarray(nu,float);beta=np.asarray(beta,float)
    if nu.shape!=(count,) or beta.shape!=(count,3):
        raise ValueError('One opacity and normal-frame velocity per spatial cell required')
    if not np.isfinite(nu).all() or np.any(nu<0):
        raise ValueError('Finite nonnegative proper-density opacities required')
    if not np.isfinite(beta).all() or np.any(np.sum(beta*beta,axis=1)>=1):
        raise ValueError('Finite subluminal velocities required, including vacuum representatives')
    return nu,beta


def mean_electron_current(nu,beta,projector):
    """Return mean rate-scaled number current, its norm, and its rest velocity.

    nu*U is c*sigma_T times n_e_star*U (U=u_e/c). A mean current defines a
    comparison frame, NOT a cold single-fluid collision closure. Its proper
    norm need not equal mean(nu). Exact vacuum uses a tagged zero representative.
    """
    nu,beta=_matter(nu,beta,len(projector.p))
    gamma=1/np.sqrt(1-np.sum(beta*beta,axis=1))
    current=projector.mean(nu[:,None]*gamma[:,None]*np.c_[np.ones(len(nu)),beta])
    if current[0]==0:return current,0.,np.zeros(3)
    mag=float(np.linalg.norm(current[1:]));norm2=(current[0]-mag)*(current[0]+mag)
    if norm2<=0:raise ValueError('Mean current not numerically timelike; no clipping')
    return current,float(np.sqrt(norm2)),current[1:]/current[0]


@dataclass
class CollisionSplit:
    mean_carrier: np.ndarray
    local_collision: np.ndarray
    mean_collision: np.ndarray
    baseline: np.ndarray
    opacity_correlation: np.ndarray
    velocity_dispersion: np.ndarray
    velocity_radiation: np.ndarray
    measure_term: np.ndarray
    background_rate: np.ndarray
    fluctuation_rate: np.ndarray
    reference_beta: np.ndarray
    mean_opacity: float
    current_opacity: float
    current_beta: np.ndarray
    current_surrogate: np.ndarray
    current_density_correction: np.ndarray
    current_frame_correction: np.ndarray


def split_collision(n,w,J,nu,beta,projector:SpatialProjector,reference_beta=None):
    """Compute local physics first, then an EXACT three-remainder identity.

    L_b = unit-opacity full-polarized generator at velocity b.
    mean(C) = mean(nu)*L_ref(mean(J))
      + L_ref mean((nu-mean(nu))*(J-mean(J)))
      + mean(nu*(L_b-L_ref)mean(J))
      + mean(nu*(L_b-L_ref)(J-mean(J))).
    Individual terms depend on reference_beta; their sum does not. The default
    reference is the mean electron-current rest frame. Optional explicit
    reference_beta changes the bookkeeping only, never the local collisions.
    Physical-volume Pdot is a separate term in background_rate.
    """
    J=np.asarray(J,float);count=len(projector.p)
    if J.ndim!=4 or J.shape[0]!=count or J.shape[2:]!=(3,3) or not np.isfinite(J).all():
        raise ValueError('Finite common-frame carrier (space,direction,3,3) required')
    nu,beta=_matter(nu,beta,count)
    _,nuc,bc=mean_electron_current(nu,beta,projector)
    br=bc if reference_beta is None else np.asarray(reference_beta,float)
    opref=TiltedThomson(n,w,br)
    if J.shape[1]!=len(opref.n):raise ValueError('Angular labels and carrier disagree')
    meanJ=projector.mean(J);dJ=J-meanJ;nb=float(projector.mean(nu))
    refbar=opref.rhs(meanJ,1.)
    baseline=nb*refbar
    opacity=opref.rhs(projector.mean((nu-nb)[:,None,None,None]*dJ),1.)
    local=np.empty_like(J);vr=np.zeros_like(meanJ);vd=np.zeros_like(meanJ)
    cache={}
    for x in range(count):
        key=tuple(beta[x])
        if key not in cache:cache[key]=TiltedThomson(n,w,beta[x])
        op=cache[key]
        # All provided carriers are checked even in vacuum. No hidden clipping.
        local[x]=op.rhs(J[x],nu[x])
        if nu[x]:
            vd+=projector.p[x]*nu[x]*(op.rhs(meanJ,1.)-refbar)
            vr+=projector.p[x]*nu[x]*(op.rhs(dJ[x],1.)-opref.rhs(dJ[x],1.))
    meanC=projector.mean(local);measure=projector.mean_pdot(J)
    bg=meanC+measure;delta_rate=local-bg[None]
    opc=TiltedThomson(n,w,bc);Lc=opc.rhs(meanJ,1.)
    surrogate=nuc*Lc
    return CollisionSplit(meanJ,local,meanC,baseline,opacity,vd,vr,measure,bg,
                          delta_rate,opref.beta.copy(),nb,nuc,bc.copy(),surrogate,
                          (nb-nuc)*refbar,nuc*(refbar-Lc))


def force_budget(n,w,J,nu,beta,projector,result=None):
    """Covariant cell forces and the exact mean-frame work-correlation identity.

    Cell elasticity is F0_x=beta_x.Fspatial_x. In general mean(F0) need not
    vanish in the mean-current frame. The nonzero mean-frame contraction is
    mean((beta-beta_current).Fspatial), up to local quadrature residuals.
    No opposite material force or matter evolution is supplied here.
    """
    nu,beta=_matter(nu,beta,len(projector.p))
    r=split_collision(n,w,J,nu,beta,projector) if result is None else result
    expected=[];measured=[];scales=[]
    for x in range(len(nu)):
        T=radiation_tensor(n,w,J[x]);F=radiation_tensor(n,w,r.local_collision[x])[0]
        expected.append(expected_fourforce(T,beta[x],nu[x]));measured.append(F)
        scales.append(max(1.,nu[x]*abs(T[0,0])))
    expected=np.asarray(expected);measured=np.asarray(measured);scales=np.asarray(scales)
    avg=projector.mean(measured);bc=r.current_beta
    elastic=measured[:,0]-np.einsum('xi,xi->x',beta,measured[:,1:])
    covariance=float(projector.mean(np.einsum('xi,xi->x',beta-bc,measured[:,1:])))
    defect=float(avg[0]-bc@avg[1:])
    return {'cell_force':measured.tolist(),'covariant_cell_force':expected.tolist(),
            'mean_force':avg.tolist(),'mean_covariant_force':projector.mean(expected).tolist(),
            'max_relative_force_residual':float(np.max(abs(measured-expected)/scales[:,None])),
            'max_relative_local_elasticity':float(np.max(abs(elastic)/scales)),
            'mean_frame_elastic_defect':defect,'velocity_force_correlation':covariance,
            'mean_local_elastic_residual':float(projector.mean(elastic)),
            'work_identity_residual':float(defect-covariance-projector.mean(elastic))}

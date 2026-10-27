"""Per-sector SI stress and energy-equivalent four-force adapter.

T is J/m3. cQ is J/(m3 s), with x0=ct. Rates never alter state stress.
"""
import numpy as np
from binding import ROUND, real


def si_to_core(scale, tensors, cQ, core, *, check=True):
    T=np.asarray(tensors); ns=len(T)
    T=real(T,(ns,4,4),'sector stress'); q=real(cQ,(ns,4),'cQ')
    rho=T[:,0,0]; flux=T[:,0,1:]
    spatial=T[:,1:,1:]
    # Algebraic tr(Tij)/3, evaluated about one diagonal entry so an exactly
    # isotropic represented tensor retains exactly zero pi. No stress projection.
    p=spatial[:,0,0]+((spatial[:,1,1]-spatial[:,0,0])+(spatial[:,2,2]-spatial[:,0,0]))/3
    pi=spatial.copy()
    # Exact algebraic trace removal via pairwise differences preserves tiny
    # represented anisotropy without cancellation through a rounded mean.
    # This evaluates the physical decomposition; it does not project stress.
    for i in range(3):
        j,k=[v for v in range(3) if v!=i]
        pi[:,i,i]=((spatial[:,i,i]-spatial[:,j,j])+(spatial[:,i,i]-spatial[:,k,k]))/3
    if check:
        if np.any(rho<0): raise ValueError('negative sector density')
        for i in range(ns):
            sector_scale=max(abs(rho[i]),float(np.max(np.abs(T[i]))))
            if np.max(np.abs(T[i]-T[i].T)) > ROUND*sector_scale:
                raise ValueError('asymmetric physical sector stress')
            if abs(np.trace(pi[i])) > ROUND*sector_scale:
                raise ValueError('physical stress is not STF on sector scale')
    alpha=scale.density_factor
    rho_hat=alpha*rho; flux_hat=alpha*flux
    UJ=alpha*scale.time_s*q
    source=core.Source(alpha*p,alpha*pi,UJ[:,0],UJ[:,1:])
    source.arrays(ns,balanced=True)
    return rho_hat,flux_hat,source


def core_to_si(scale,rho,flux,source):
    p,pi,_,_=source.arrays(len(rho))
    T=np.zeros((len(rho),4,4)); a=scale.density_factor
    T[:,0,0]=rho/a; T[:,0,1:]=flux/a; T[:,1:,0]=flux/a
    T[:,1:,1:]=(p[:,None,None]*np.eye(3)+pi)/a
    return T


def endpoint_bridge(endpoint,fixture,core,*,evaluate_rhs=False):
    scale=core.FixedScale(fixture['L_m']); alpha=scale.density_factor
    hats=np.array([endpoint['rho_R'],endpoint['rho_X'],endpoint['rho_gamma']])
    T=np.zeros((3,4,4)); T[:,0,0]=hats/alpha
    T[2,1:,1:]=(hats[2]*np.eye(3)/3+np.asarray(endpoint['pi_gamma']))/alpha
    rho,flux,source=si_to_core(scale,T,np.zeros((3,4)),core)
    back=core_to_si(scale,rho,flux,source)
    scales=np.max(np.abs(T),axis=(1,2))
    residual=np.divide(back-T,scales[:,None,None],out=np.zeros_like(T),where=scales[:,None,None]>0)
    if np.any((scales==0)&np.any(back!=T,axis=(1,2))): raise ArithmeticError('vacuum roundtrip changed')
    gamma_scale=scales[2]
    trace_residual=(np.trace(T[2,1:,1:])-T[2,0,0])/gamma_scale if gamma_scale>0 else 0.
    if np.max(np.abs(residual))>ROUND or abs(trace_residual)>ROUND: raise ArithmeticError('endpoint representation tolerance')
    result=dict(tau=endpoint['tau'],proper_time_s=endpoint['physical_time_s'],fixed_L_m=fixture['L_m'],
        sector_names=['lower_rest_R','excitation_X','radiation'],T_SI_J_m3=T,rho_hat=rho,flux_hat=flux,
        pressure_hat=source.pressure,pi_hat=source.pi,cQ_SI_J_m3_s=np.zeros((3,4)),
        U=source.energy_transfer,J=source.momentum_transfer,
        source_timing='FINITE_SOURCE_KICKS_ALREADY_APPLIED_TO_SAVED_STATE',
        flux_closure='EXACT_ANTIPODAL_ZERO_VECTOR_IN_SELECTED_MODEL',
        saved_scalar_flux_residual=endpoint['flux_relative'],
        signed_roundtrip_residual_on_sector_scale=residual,radiation_trace_residual=trace_residual,
        historical_numerical_errors={k:endpoint[k] for k in ['hamiltonian','x_exact_error','count_relative','work_relative','monitor_relative']})
    if evaluate_rhs:
        sigma=np.diag([endpoint['sigma1'],endpoint['sigma2'],-endpoint['sigma1']-endpoint['sigma2']])
        state=core.State(endpoint['h'],sigma,np.zeros((3,3)),np.zeros(3),endpoint['alpha'],rho,flux)
        actual=core.State.unpack(core.rhs(endpoint['tau'],state.pack(),source))
        h=endpoint['h']; p=source.pressure; pi=source.pi
        expected_h=-h*h-np.sum(sigma*sigma)/3-np.sum(rho+3*p)/6
        expected_sigma=-3*h*sigma+np.sum(pi,axis=0)
        expected_rho=-3*h*(rho+p)-np.einsum('ab,iab->i',sigma,pi)
        expected_flux=-4*h*flux-flux@sigma.T
        rhs_res=dict(dh=actual.h-expected_h,dsigma=actual.sigma-expected_sigma,
            drho=actual.rho-expected_rho,dflux=actual.flux-expected_flux)
        # These algebraic equations are compared on their own derivative scales.
        checks=[(rhs_res['dh'],abs(expected_h)),(rhs_res['dsigma'],max(float(np.max(np.abs(expected_sigma))),1.)),
                (rhs_res['drho'],float(np.max(np.abs(expected_rho)))),(rhs_res['dflux'],1.)]
        if any(np.max(np.abs(r))>ROUND*s for r,s in checks): raise ArithmeticError('core Bianchi-I RHS mismatch')
        result['core_rhs_signed_residuals']=rhs_res
    return result

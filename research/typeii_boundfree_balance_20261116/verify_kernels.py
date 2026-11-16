#!/usr/bin/env python3
"""Independent phase-space, angular-frame, atomic reference and equilibrium tests."""
import json,math
import numpy as np
from scipy.integrate import quad
from scipy.special import logsumexp
from numpy.polynomial.legendre import leggauss
from boundfree import *

def run():
    q=LEVELS[1,0];y=1+q['K']/q['chi'];eps=np.sqrt(y-1)
    alpha_fs=7.2973525643e-3;a0=5.29177210544e-11
    f=np.ones_like(eps);nonzero=eps>0
    f[nonzero]=np.arctan(eps[nonzero])/eps[nonzero]
    den=np.ones_like(eps);den[nonzero]=-np.expm1(-2*np.pi/eps[nonzero])
    analytic=512*np.pi**2/3*alpha_fs*a0*a0/y**4*np.exp(-4*f)/den
    ground_gap=float(max(abs(q['sigma']/analytic-1)))
    check(ground_gap<5e-4,'author 1s table versus independent Coulomb formula')
    balance=[];velocity=[];order=[];frames=[];adaptive=[]
    for lev in LEVELS:
        for T,eta in [(820.3755,0.),(3000.,0.),(8000.,.7)]:
            r=rates(T,T,0.,lev,eta=eta)
            err=abs(r['log_alpha']-r['log_photo']-log_saha(T,lev,eta))
            check(err<3e-11,'finite-band detailed balance '+str(lev))
            balance.append(err)
    for lev in [(1,0),(2,0),(2,1),(3,2),(5,0),(10,0)]:
        r=rates(3000.,2800.,.05,lev,order=4)
        av=velocity_alpha(3000.,2800.,.05,lev)
        gap=abs(av/r['alpha_m3_s']-1);check(gap<2e-8,'velocity-space Milne normalization')
        velocity.append({'level':list(lev),'relative_gap':gap})
        r8=rates(3000.,2800.,.05,lev,order=8)
        gap=max(abs(np.expm1(r8['log_photo']-r['log_photo'])),abs(np.expm1(r8['log_alpha']-r['log_alpha'])))
        check(gap<2e-8,'segment quadrature convergence');order.append(gap)
    for lev in [(1,0),(2,0),(2,1),(3,2)]:
        T=3000.;b=.05;g=1/np.sqrt(1-b*b)
        K,w=quadrature(lev,6);E=LEVELS[lev]['chi']+K
        mu,mw=leggauss(48);D=g*(1-b*mu)
        normal_occ=log_nbar(E[:,None]/D[None,:],T,0.)
        normal_mon=logsumexp(normal_occ+np.log(mw/2)[None,:]-2*np.log(D)[None,:],axis=1)
        direct=log_nbar(E,T,b)
        logbase=np.log(w)+2*np.log(E)+np.log(sigma(E,lev))
        frame_gap=abs(np.expm1(logsumexp(logbase+normal_mon)-logsumexp(logbase+direct)))
        check(frame_gap<2e-11,'angular aberration-frame equivalence')
        frames.append({'level':list(lev),'relative_gap':float(frame_gap)})
        # Independent QUAD integration in dimensionless kinetic energy over the
        # exact finite source support, with source knots supplied as breakpoints.
        chi=LEVELS[lev]['chi'];thot=T*np.sqrt((1+b)/(1-b));scale=KB*thot
        sig0=float(sigma(chi,lev));shift=chi/scale
        def f(y):
            e=chi+scale*y
            return (e/chi)**2*float(sigma(e,lev))/sig0*float(np.exp(log_nbar(e,T,b)+shift))
        edge=LEVELS[lev]['K']/scale
        val,err=quad(f,0,float(edge[-1]),points=edge[1:-1],limit=2000,epsabs=1e-11,epsrel=1e-11)
        logref=np.log(A*chi**2*sig0*scale)+np.log(val)-shift
        got=rates(T,2800.,b,lev,order=6)
        delta=float(abs(np.expm1(logref-got['log_photo'])))
        check(delta<2e-8,'adaptive forward rate comparison')
        adaptive.append({'level':list(lev),'relative_gap':delta,'quad_estimate':err/val})
    energies=[];eqmom=[]
    for lev in [(1,0),(2,0),(2,1),(5,0),(10,9)]:
        r=rates(3000.,2800.,.05,lev)
        s=net_sources(r,2e5,3e7,3e7)
        scale=sum(abs(s[k]) for k in ('Q_photon','Q_kinetic','Q_ionization'))
        err=abs(s['energy_residual'])/scale;check(err<1e-12,'number/energy exchange')
        energies.append(err)
        r=rates(3000.,3000.,0.,lev)
        # Both collision-number and kinetic moments vanish independently at
        # common-temperature Planck/Saha equilibrium, not just their energy sum.
        nprod=1.;ni=np.exp(log_saha(3000.,lev));s=net_sources(r,ni,1.,1.)
        rate_scale=max(ni*r['photo_s'],r['alpha_m3_s'])
        err=max(abs(s['F_ion_m3_s'])/rate_scale,abs(s['Q_kinetic'])/(rate_scale*KB*3000))
        check(err<2e-10,'spectral thermal equilibrium moments');eqmom.append(err)
    source_round=max(v['photon_column_rounding_max_J']/RY for v in LEVELS.values())
    out={'source_states':len(LEVELS),'finite_support_balance_cases':len(balance),'max_log_balance_residual':max(balance),
         'independent_ground_Coulomb_max_relative_gap':ground_gap,'ground_Coulomb_acceptance':5e-4,
         'independent_velocity_cases':velocity,'max_segment4_8_relative_gap':max(order),
         'two_frame_photoionization_cases':frames,'adaptive_energy_cases':adaptive,
         'energy_conservation_max_relative_residual':max(energies),'thermal_number_and_kinetic_equilibrium_max_relative_residual':max(eqmom),
         'source_rounding_max_photon_column_Ry':source_round,
         'warnings':['all rates are on finite original support; no unbounded-energy rate claim','rounding and interpolation error separate from detailed-balance and quadrature identities','author table is nl-resolved/unpublished in its own header; not exact machine algebra']}
    (ROOT/'KERNEL_VERIFICATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':run()

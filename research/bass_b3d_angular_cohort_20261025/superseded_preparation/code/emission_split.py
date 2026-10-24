"""Frozen B3c1 diagonal Einstein/exact source split, workflow 1.0.0.

Six geometry coordinates and a normalized expansion-work ledger are integrated.
All material densities and packet moments are reconstructed, not integrated.
"""
from __future__ import annotations
from dataclasses import dataclass, replace
import math
import numpy as np
from scipy.integrate import solve_ivp, quad
from scipy.optimize import brentq
import finite_exchange as fx
from vendor import core, kinetic

CARD=fx.owner.CARDS['H_LYA_EFFECTIVE_2P']
S0=np.array([-.4,.1,.3]); X0=.1; T=.02
N0=8*math.pi/(CARD.g*CARD.wavelength_m**3)
M0=1.67262192595e-27+9.1093837139e-31
RHO0=N0*(M0*core.C_SI**2+CARD.energy_J*X0)
H0=math.sqrt((8*math.pi*core.G_SI/core.C_SI**2)*RHO0/(3-np.dot(S0,S0)/2))
SCALE=core.FixedScale(core.C_SI/H0)
PSTAR=CARD.energy_J/core.C_SI
U0=SCALE.density_factor*CARD.energy_J*(N0*X0)
RESOLUTION=4096*np.finfo(float).eps


def diagonal(x,y): return np.array([x,y,-x-y])


class SplitModel:
    def __init__(self, *, prescribed=False, initial_photons=None):
        if initial_photons is not None:
            raise ValueError('frozen initial photon support must be exactly vacuum; blue stock forbidden')
        self.prescribed=prescribed
        self.y=np.array([1.,S0[0],S0[1],0.,0.,0.,0.])
        self.tau=0.; self.x=X0
        self.k_birth=np.empty((0,3)); self.w_birth=np.empty(0)
        self.alpha_birth=np.empty(0);self.beta_birth=np.empty((0,3))
        self.applied=frozenset();self.reactions=0;self.nfev=0
        self.history=[];self.transactions=[]
        self.record('initial')

    def identity(self):
        # Each accepted source evaluation has a current-geometry/stock epoch.
        epoch=f'tau={self.tau.hex()};alpha={float(self.y[3]).hex()};C={self.reactions}'
        return fx.Identity('B3C1_COLD_EMISSION',CARD.id,CARD.population_scope,epoch,SCALE,PSTAR)

    def geometry(self,y):
        return float(y[0]),diagonal(y[1],y[2]),float(y[3]),diagonal(y[4],y[5])

    def photons(self,y,identity=None):
        _,_,alpha,beta=self.geometry(y)
        da=alpha-self.alpha_birth
        k=self.k_birth*np.exp(-da[:,None]-(beta-self.beta_birth))
        w=self.w_birth*np.exp(-3*da)
        return fx.PhotonStock(identity or self.identity(),k,w,np.zeros(len(w)),self.applied)

    def components(self,y,identity=None):
        h,sigma,alpha,_=self.geometry(y)
        if h<=0 or np.min(h+sigma)<=0:raise ValueError('strict positive directional expansion required')
        N=N0*math.exp(-3*alpha);nu=N*self.x;nl=N-nu
        photons=self.photons(y,identity)
        rho,flux,p,pi=fx.photon_moments(photons)
        state=core.State(h,np.diag(sigma),np.zeros((3,3)),np.zeros(3),alpha,
            np.array([SCALE.density_factor*CARD.energy_J*nu,
                      SCALE.density_factor*M0*core.C_SI**2*N,rho]),
            np.array([np.zeros(3),np.zeros(3),flux]))
        source=core.Source(np.array([0.,0.,p]),np.array([np.zeros((3,3)),np.zeros((3,3)),pi]),np.zeros(3),np.zeros((3,3)))
        return state,source,photons,N,nu,nl

    def rhs(self,t,y):
        state,source,_,_,_,_=self.components(y)
        dy=core.rhs(t,state.pack(),source)
        # Positive expression equivalent to -u', divided by initial excitation.
        h,sigma,_,_=self.geometry(y)
        Pi=source.pi[2]+np.eye(3)*source.pressure[2]
        work=(3*h*state.rho[0]+3*h*state.rho[2]+np.dot(h+sigma,np.diag(Pi)))/U0
        return np.array([dy[0],dy[1],dy[2],dy[15],sigma[0],sigma[1],work])

    def react(self,dtau,*,f_plus=0.,frame=fx.FRAME,owner_mode='standalone_detached'):
        if f_plus!=0:raise ValueError('zero incoming blue trace required')
        identity=replace(self.identity(),frame=frame)
        state,source,photons,N,nu,nl=self.components(self.y,identity)
        h,sigma,alpha,beta=self.geometry(self.y)
        line=fx.owner.LineState(CARD.id,CARD.population_scope,nl,nu,h/SCALE.time_s,
            f_plus,np.diag(sigma/h),'FROZEN_SYNTHETIC_B3C1',owner_mode=owner_mode)
        # Exact owner multiplication order: state sector owns stored n_u.
        state.rho[0]=SCALE.density_factor*CARD.energy_J*line.n_u_m3
        population=fx.PopulationStock(identity,line.n_u_m3,line.n_l_m3,self.applied)
        result=fx.commit_emission(line=line,source_identity=identity,state_identity=identity,
            state=state,source=source,population=population,photons=photons,
            scale=SCALE,Pstar=PSTAR,dt_s=SCALE.time_s*dtau,
            transfer_id=f'emission-{self.reactions}',atomic_sector=0,photon_sector=2)
        n_old=len(photons.w); added=result['photons']; n_new=len(added.w)-n_old
        self.k_birth=np.concatenate((self.k_birth,added.k[n_old:]))
        self.w_birth=np.concatenate((self.w_birth,added.w[n_old:]))
        self.alpha_birth=np.concatenate((self.alpha_birth,np.full(n_new,alpha)))
        self.beta_birth=np.concatenate((self.beta_birth,np.tile(beta,(n_new,1))))
        self.x=result['line'].x;self.applied=result['population'].applied
        self.reactions+=1
        self.transactions.append(dict(tau=self.tau,dtau=dtau,epoch=identity.epoch,
            transfer_id=result['physical_transfer_key'],n_u_before=nu,n_u_after=result['population'].n_u_m3,
            down=result['ledger']['down_m3'],up=result['ledger']['up_m3'],
            source_H_s_inv=line.H_s_inv,source_S=line.S.tolist(),source_N=line.N,
            source_x0=line.x,source_x1=result['line'].x,
            path_depth_ratio=result['ledger']['owner_map']['path_depth_ratio'],
            path_qmax=result['ledger']['owner_map']['path_qmax'],
            log_root_residual=result['ledger']['owner_map']['log_root_residual'],
            gross_difference_residual_over_gross=result['ledger']['gross_difference_residual_over_gross'],
            rest_energy_change=float(result['state'].rho[1]-state.rho[1]),
            outgoing_U=result['source'].energy_transfer.tolist(),outgoing_J=result['source'].momentum_transfer.tolist(),
            residuals=result['residuals']))
        self.record('C')

    def drift(self,dtau,rtol=2e-12,atol=2e-14):
        if self.prescribed:
            self.y[3]+=dtau;self.y[4:6]+=S0[:2]*dtau
        else:
            sol=solve_ivp(self.rhs,(self.tau,self.tau+dtau),self.y,method='DOP853',
                rtol=rtol,atol=atol,max_step=dtau)
            if not sol.success:raise ArithmeticError(sol.message)
            self.y=sol.y[:,-1];self.nfev+=sol.nfev
        self.tau+=dtau
        self.record('A')

    def record(self,stage):
        state,source,ph,N,_,_=self.components(self.y)
        h,sigma,alpha,beta=self.geometry(self.y)
        ng=float(np.sum(ph.w))/(SCALE.density_factor*CARD.energy_J)
        tensor=kinetic.tensor(ph.k,ph.w,ph.mass) if len(ph.w) else np.zeros((4,4))
        work_residual=abs((state.rho[0]+state.rho[2])/U0+self.y[6]-1.)
        row=dict(tau=self.tau,stage=stage,h=h,sigma=sigma.tolist(),alpha=alpha,beta=beta.tolist(),
            geometry=np.r_[h,sigma,alpha,beta].tolist(),x=self.x,N=N,n_gamma=ng,
            rho_exc=float(state.rho[0]),rho_rest=float(state.rho[1]),rho_gamma=float(state.rho[2]),
            tensor=tensor.tolist(),constraint=float(core.relative_constraint(state.pack())),
            constraints=core.constraints(state.pack()).tolist(),
            atom_count_error=abs(math.exp(3*alpha)*N/N0-1),
            excitation_photon_count_error=abs(math.exp(3*alpha)*(N*self.x+ng)/(N0*X0)-1),
            energy_work_error=work_residual,W_over_u0=float(self.y[6]),
            m_min=float(np.min(h+sigma)),packet_energy_max=float(np.max(np.linalg.norm(ph.k,axis=1))) if len(ph.w) else 0.,
            packet_weight_min=float(np.min(ph.w)) if len(ph.w) else None,packets=len(ph.w))
        self.history.append(row)
        return row


def trajectory(steps,*,scheme='strang',prescribed=False,rtol=2e-12,atol=2e-14):
    model=SplitModel(prescribed=prescribed);dt=T/steps
    for _ in range(steps):
        if scheme=='strang':model.react(dt/2);model.drift(dt,rtol,atol);model.react(dt/2)
        elif scheme=='lie':model.react(dt);model.drift(dt,rtol,atol)
        else:raise ValueError(scheme)
    return dict(steps=steps,scheme=scheme,prescribed=prescribed,rtol=rtol,atol=atol,
                nfev=model.nfev,final=model.history[-1],history=model.history,transactions=model.transactions)


def distance(a,b):
    return dict(geometry=float(np.max(np.abs(np.array(a['geometry'])-b['geometry']))),
        x=abs(a['x']-b['x'])/b['x'],photon_number=abs(a['n_gamma']-b['n_gamma'])/b['n_gamma'],
        photon_tensor=float(np.max(np.abs(np.array(a['tensor'])-b['tensor'])))/b['rho_gamma'])


def order(a,b):
    if min(a,b)<=RESOLUTION:return dict(value=None,status='ROUNDING_UNRESOLVED')
    return dict(value=math.log2(a/b),status='RESOLVED')


def prescribed_oracle():
    """Independent residual/root and quadrature in exact exposure variable v."""
    g=CARD.g;z=(g+1)*X0/g
    K=8*math.pi*math.expm1(3*T)/(3*N0*CARD.wavelength_m**3)
    def residual(v):return g*v+(g+1)*X0*math.expm1(-v)-K
    v=brentq(residual,0.,K/(g-(g+1)*X0),xtol=5e-324,rtol=4*np.finfo(float).eps)
    eta=8*math.pi/(g*N0*CARD.wavelength_m**3)
    def s_at(vv):return math.log1p(3*(vv+z*math.expm1(-vv))/eta)/3
    def angular(vv,index):
        a=np.exp(-(1+S0)*(T-s_at(vv)));rc=math.sqrt(np.dot(a,a)/3)
        ax=2*(1+S0)/15*a
        val=float(np.sum(ax)+.6*rc) if index==0 else float(ax[index-1]+a[index-1]**2/(5*rc))
        return math.exp(-vv)*val
    values=[];errors=[]
    for index in range(4):
        val,err=quad(lambda vv:angular(vv,index),0.,v,epsabs=2e-13,epsrel=2e-12)
        values.append(val);errors.append(err)
    pref=SCALE.density_factor*CARD.energy_J*N0*math.exp(-3*T)*X0
    tensor=np.diag(np.array(values)*pref)
    return dict(x=X0*math.exp(-v),n_gamma=N0*math.exp(-3*T)*X0*(-math.expm1(-v)),
        rho_gamma=float(tensor[0,0]),tensor=tensor.tolist(),geometry=np.r_[1.,S0,T,S0*T].tolist(),
        v=v,scalar_residual=residual(v),quadrature_dimensionless_values=values,
        quadrature_estimated_absolute_errors=errors,epsabs=2e-13,epsrel=2e-12)

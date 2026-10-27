"""Frozen B3c cold-atom finite-angular source/background model.

Geometry comes from the unchanged core; emission comes from the unchanged
actual LINE01/B3b owner. This module executes nothing on import.
"""
from dataclasses import dataclass, replace, asdict
import math
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
from vendor import core, kinetic, finite_exchange as exchange

ROOT = Path(__file__).resolve().parents[1]
owner = exchange.owner
C = 299792458.0
G = 6.67430e-11
M_LOWER = 1.6735e-27
EPS = np.finfo(float).eps
CARD = owner.CARDS['H_LYA_EFFECTIVE_2P']
GATE = 2e-8
COUNT_GATE = 5e-12


def diagonal(first, second):
    return np.diag([first, second, -first-second])


def shape_beta(q):
    return np.array([q[4], q[5], -q[4]-q[5]])


@dataclass(frozen=True)
class Fixture:
    name: str
    initial_shear: np.ndarray
    x0: float
    N0: float
    scale: core.FixedScale
    Pstar: float

    @property
    def Escale(self):
        return self.scale.density_factor * CARD.energy_J * self.N0

    @property
    def X0(self):
        return self.Escale * self.x0

    @property
    def R0(self):
        return self.scale.density_factor * M_LOWER * C*C * self.N0

    @property
    def K0(self):
        return 8*math.pi/(self.N0*CARD.wavelength_m**3)

    def metadata(self):
        return dict(name=self.name, S0=self.initial_shear.tolist(), x0=self.x0,
                    N0_m3=self.N0, nu=self.N0*CARD.wavelength_m**3/(8*math.pi),
                    L_m=self.scale.length_m, H0_s_inv=C/self.scale.length_m,
                    Pstar=self.Pstar, R0=self.R0, X0=self.X0, Escale=self.Escale,
                    lower_mass_kg=M_LOWER, mass_status='CHOSEN_MODEL_PARAMETER',
                    card=asdict(CARD), frame='non_tilted_matter_rest_tetrad',
                    closure='cold_detached_recoil_free_f_plus_zero',
                    angular_model='actual_fourteen_ray_cohorts_not_continuum')


def fixture(name='ISO', x0=.3):
    x0=owner.finite_scalar(x0,'x0',nonnegative=True)
    if x0>=CARD.g/(CARD.g+1):raise ValueError('strict non-inverted initial fraction required')
    if name not in ('ISO','ANISO'):raise ValueError('frozen fixture must be ISO or ANISO')
    S=np.zeros((3,3)) if name=='ISO' else diagonal(.15,-.05)
    N0=8*math.pi/CARD.wavelength_m**3
    L2=(3-float(np.sum(S*S))/2)*C**4/(8*math.pi*G*N0*(M_LOWER*C*C+CARD.energy_J*x0))
    return Fixture(name,S,x0,N0,core.FixedScale(math.sqrt(L2),c=C,G=G),CARD.energy_J/C)


def whole_window_bounds(model, tau_end=.1):
    s0=float(np.linalg.norm(model.initial_shear))
    qmin=1-(1+3*tau_end)*(s0+math.sqrt(6)*tau_end)
    depth=(CARD.A_s_inv*CARD.wavelength_m**3*model.N0*math.exp(-3*tau_end)
           *(CARD.g-(CARD.g+1)*model.x0)
           /(8*math.pi*(C/model.scale.length_m)*(1+s0+math.sqrt(6)*tau_end)))
    if qmin<=0 or depth<owner.THICK_THRESHOLD:raise ValueError('frozen whole-window domain bound failed')
    return dict(chi=tau_end,s0=s0,qmin_lower_bound=qmin,
                optical_depth_lower_bound=depth,required_log1p_1e8=owner.THICK_THRESHOLD,
                interpretation='continuous_model_bounds_not_interval_enclosures')


@dataclass
class RunState:
    model: Fixture
    q: np.ndarray
    x: float
    photons: exchange.PhotonStock
    monitor_rho: np.ndarray
    work: float=0.
    tau: float=0.


def initial_state(model):
    identity=exchange.Identity('BASS_B3C_COLD_ATOM',CARD.id,CARD.population_scope,
                              model.name+':manufactured_initial_tau0',
                              model.scale,model.Pstar)
    q=np.array([1.,model.initial_shear[0,0],model.initial_shear[1,1],0.,0.,0.])
    return RunState(model,q,model.x0,exchange.PhotonStock.vacuum(identity),
                    np.array([model.R0,model.X0,0.]))


def packets_at(photons, q_start, q_stage):
    da=float(q_stage[3]-q_start[3])
    db=shape_beta(q_stage)-shape_beta(q_start)
    with np.errstate(over='raise',invalid='raise',under='ignore'):
        k=photons.k*np.exp(-da-db)[None,:]
        w=photons.w*math.exp(-3*da)
    if len(w) and (np.any(w<=0) or not np.all(np.isfinite(k)) or not np.all(np.isfinite(w))):
        raise ArithmeticError('positive characteristic packet underflow/overflow')
    return replace(photons,k=k,w=w)


def closure(model,q,x,photons):
    if np.iscomplexobj(q) or q.shape!=(6,) or not np.all(np.isfinite(q)):
        raise ValueError('finite real six-variable geometry required')
    if q[0]<=0 or not math.isfinite(x) or not (0<=x<CARD.g/(CARD.g+1)):
        raise ValueError('expanding positive non-inverted state required')
    N=model.N0*math.exp(-3*q[3])
    if not math.isfinite(N) or N<=0:raise ArithmeticError('positive atom count underflow/overflow')
    sigma=diagonal(q[1],q[2]);S=sigma/q[0]
    if 1+float(np.min(np.diag(S)))<=0:raise ValueError('non-expanding photon direction')
    nu=N*x;nl=N-nu
    if x>0 and nu<=0:raise ArithmeticError('positive upper state underflow')
    pop=exchange.PopulationStock(photons.identity,nu,nl,photons.applied)
    rho,flux,p,pi=exchange.photon_moments(photons)
    if len(photons.w) and np.any(photons.w<=0):raise ArithmeticError('positive photon stock required')
    # X uses exactly the source owner's multiplication and the same population.
    rho_X=model.scale.density_factor*CARD.energy_J*pop.n_u_m3
    rho_R=model.scale.density_factor*M_LOWER*C*C*N
    state=core.State(float(q[0]),sigma,np.zeros((3,3)),np.zeros(3),float(q[3]),
                     np.array([rho_R,rho_X,rho]),np.array([np.zeros(3),np.zeros(3),flux]))
    source=core.Source(np.array([0.,0.,p]),np.array([np.zeros((3,3)),np.zeros((3,3)),pi]),
                       np.zeros(3),np.zeros((3,3)))
    state.validate();source.arrays(3)
    if np.any(state.rho<0):raise ArithmeticError('negative owned sector')
    return state,source,pop,S


def transport(run,delta):
    """RK4 geometry and independent energy/work quadratures; no projection."""
    if delta<=0 or not math.isfinite(delta):raise ValueError('positive finite transport duration required')
    q0=run.q.copy();photons0=run.photons
    def derivative(q):
        photons=packets_at(photons0,q0,q)
        state,source,_,_=closure(run.model,q,run.x,photons)
        derivative=core.State.unpack(core.rhs(run.tau,state.pack(),source),3)
        geometry=np.array([derivative.h,derivative.sigma[0,0],derivative.sigma[1,1],
                           derivative.alpha,state.sigma[0,0],state.sigma[1,1]])
        work=-math.exp(3*q[3])*(state.h*state.rho[2]+float(np.sum(state.sigma*source.pi[2])))
        return np.r_[geometry,derivative.rho,work]
    a=derivative(q0);b=derivative(q0+delta*a[:6]/2)
    c=derivative(q0+delta*b[:6]/2);d=derivative(q0+delta*c[:6])
    change=delta*(a+2*b+2*c+d)/6
    q1=q0+change[:6];photons1=packets_at(photons0,q0,q1)
    closure(run.model,q1,run.x,photons1) # Actual endpoint domain, no clipping.
    return RunState(run.model,q1,run.x,photons1,run.monitor_rho+change[6:9],
                    run.work+float(change[9]),run.tau+delta)


def source_arguments(run,dtau,transfer_id):
    state,source,pop,S=closure(run.model,run.q,run.x,run.photons)
    line=owner.LineState(CARD.id,CARD.population_scope,pop.n_l_m3,pop.n_u_m3,
                         state.h*C/run.model.scale.length_m,0.,S,
                         'B3C_DECLARED_MANUFACTURED_COLD_ATOMS',
                         angular_provenance='B3C_DIAGONAL_BIANCHI_I_FINITE14')
    return dict(line=line,source_identity=run.photons.identity,state_identity=run.photons.identity,
                state=state,source=source,population=pop,photons=run.photons,
                scale=run.model.scale,Pstar=run.model.Pstar,
                dt_s=run.model.scale.length_m/C*dtau,transfer_id=transfer_id,
                atomic_sector=1,photon_sector=2)


def source_kick(run,dtau,transfer_id,interval_start,interval_end):
    kwargs=source_arguments(run,dtau,transfer_id)
    result=exchange.commit_emission(**kwargs)
    pressure,pi,U,J=result['source'].arrays(3)
    if np.any(U!=0) or np.any(J!=0):raise ArithmeticError('already applied source must have zero U/J')
    pop=result['population']
    x=pop.n_u_m3/(pop.n_u_m3+pop.n_l_m3)
    kick=result['state'].rho-kwargs['state'].rho
    after=RunState(run.model,run.q.copy(),x,result['photons'],
                   run.monitor_rho+kick,run.work,run.tau)
    closure(run.model,after.q,after.x,after.photons)
    receipt=dict(transfer_id=transfer_id,physical_transfer_key=result['physical_transfer_key'],
                 interval_start_tau=interval_start,interval_end_tau=interval_end,
                 deposition_epoch_tau=run.tau,source_subflow_duration_tau=dtau,
                 source_subflow_duration_s=kwargs['dt_s'],global_time_advanced_by_source=0.,
                 midpoint_N_m3=kwargs['line'].N,midpoint_H_s_inv=kwargs['line'].H_s_inv,
                 midpoint_S=kwargs['line'].S,upper_before_m3=kwargs['population'].n_u_m3,
                 upper_after_m3=pop.n_u_m3,lower_before_m3=kwargs['population'].n_l_m3,
                 lower_after_m3=pop.n_l_m3,sector_kick=kick,
                 already_applied_U=U,already_applied_J=J,
                 ledger=result['ledger'],residuals=result['residuals'],tolerance=result['tolerance'],
                 applied_history_count=len(result['photons'].applied),
                 pi_kind=result['pi_kind'])
    return after,receipt,result,kwargs


def exact_population(alpha,model):
    """Independent monotone bisection; never calls the owner's root solver."""
    if model.x0==0:return 0.
    if not math.isfinite(alpha) or alpha<0:raise ValueError('oracle expects finite alpha>=0')
    omega=model.K0*math.expm1(3*alpha)/(3*CARD.g)
    if omega==0:return model.x0
    z0=-(CARD.g+1)*model.x0/CARD.g
    lo=-omega/(1+z0)-1.;hi=0.
    def F(u):return math.fsum((u,z0*math.expm1(u),omega))
    if not F(lo)<0 or F(hi)<0:raise ArithmeticError('independent root bracket failed')
    for _ in range(100):
        mid=(lo+hi)/2
        if mid==lo or mid==hi:break
        if F(mid)<0:lo=mid
        else:hi=mid
    u=min((lo,hi),key=lambda z:abs(F(z)))
    return model.x0*math.exp(u)


def diagnostics(run):
    model=run.model
    state,source,pop,S=closure(model,run.q,run.x,run.photons)
    a=run.q[3];volume=math.exp(3*a);N=pop.n_u_m3+pop.n_l_m3
    n_gamma=float(np.sum(run.photons.w))/(model.scale.density_factor*C*model.Pstar)
    out=dict(tau=run.tau,physical_time_s=run.tau*model.scale.length_m/C,
             h=float(run.q[0]),sigma1=float(run.q[1]),sigma2=float(run.q[2]),
             alpha=float(a),beta1=float(run.q[4]),beta2=float(run.q[5]),
             x=run.x,rho_R=float(state.rho[0]),rho_X=float(state.rho[1]),
             rho_gamma=float(state.rho[2]),pi_gamma=source.pi[2].copy(),
             photon_number_m3=n_gamma,atom_number_relative=abs(volume*N/model.N0-1),
             hamiltonian=abs(float(core.constraints(state.pack())[0]))/max(1.,float(np.sum(np.abs(state.rho)))),
             photon_packets=len(run.photons.w),qmin=1+float(np.min(np.diag(S))))
    if model.x0==0:
        if run.x!=0 or len(run.photons.w)!=0 or n_gamma!=0 or state.rho[1]!=0 or state.rho[2]!=0:
            raise ArithmeticError('exact vacuum branch produced photons or excitation')
        out.update(exact_vacuum=True,x_exact_error=None,count_relative=None,work_relative=None,
                   monitor_relative=[abs(run.monitor_rho[0]-state.rho[0])/model.R0,None,None],
                   flux_relative=None)
    else:
        out.update(exact_vacuum=False,
                   x_exact_error=abs(run.x-exact_population(a,model))/model.x0,
                   count_relative=abs(volume*(N*run.x+n_gamma)-model.N0*model.x0)/(model.N0*model.x0),
                   work_relative=abs(volume*(state.rho[1]+state.rho[2])-model.X0-run.work)/model.X0,
                   monitor_relative=(np.abs(run.monitor_rho-state.rho)/np.array([model.R0,model.X0,model.X0])).tolist(),
                   flux_relative=float(np.linalg.norm(state.flux[2]))/model.X0)
    return out


def integrate_fixture(model,nsteps,tau_end=.1,wrong_start_placement=False):
    if not isinstance(nsteps,int) or nsteps<=0:raise ValueError('positive integer nsteps required')
    whole_window_bounds(model,tau_end)
    run=initial_state(model);path=[diagnostics(run)];receipts=[]
    dt=tau_end/nsteps
    for index in range(nsteps):
        t0=run.tau;t1=(index+1)*dt
        if wrong_start_placement:
            run,receipt,_,_=source_kick(run,dt,f'{model.name}:WRONG_START:n{nsteps}:i{index}',t0,t1)
            run=transport(run,dt)
        else:
            run=transport(run,dt/2)
            run,receipt,_,_=source_kick(run,dt,f'{model.name}:MIDPOINT:n{nsteps}:i{index}',t0,t1)
            run=transport(run,dt/2)
        receipts.append(receipt);path.append(diagnostics(run))
    if abs(run.tau-tau_end)>64*EPS*max(1.,tau_end):raise ArithmeticError('global clock mismatch')
    return dict(model=model.metadata(),nsteps=nsteps,tau_end=tau_end,
                method='REJECTED_FIRST_ORDER_START_PLACEMENT' if wrong_start_placement else 'STRANG_MIDPOINT_RK4_CHARACTERISTICS',
                path=path,source_history=receipts,final_state=run)


def isotropic_reference(model,tau_end=.1):
    if model.name!='ISO' or model.x0<=0:raise ValueError('positive ISO reference required')
    def rhs(t,y):
        h,a,x,r=y;d=CARD.g-(CARD.g+1)*x
        exp3=math.exp(3*a)
        rhoR=model.R0/exp3;rhoX=model.Escale*x/exp3;rhoG=model.Escale*r
        return [-h*h-(rhoR+rhoX+2*rhoG)/6,h,
                -model.K0*h*exp3*x/d,-4*h*r+model.K0*h*x/d]
    result=solve_ivp(rhs,(0.,tau_end),[1.,0.,model.x0,0.],method='DOP853',
                     rtol=2e-12,atol=2e-14,dense_output=True)
    if not result.success:raise ArithmeticError('independent ISO DOP853 failed: '+result.message)
    return result,dict(method='DOP853',rtol=2e-12,atol=2e-14,dense_output=True,
                       status=int(result.status),success=bool(result.success),message=result.message,
                       nfev=int(result.nfev),njev=int(result.njev),nlu=int(result.nlu),
                       tau_start=0.,tau_end=tau_end,physical_time_end_s=tau_end*model.scale.length_m/C,
                       independent_variables=['h','alpha','x','r_radiation_over_Escale'],
                       endpoint=result.y[:,-1].tolist())


def jsonable(value):
    if isinstance(value,np.ndarray):return value.tolist()
    if isinstance(value,np.generic):return value.item()
    if isinstance(value,dict):return {str(k):jsonable(v) for k,v in value.items()}
    if isinstance(value,(tuple,list)):return [jsonable(v) for v in value]
    if isinstance(value,frozenset):return [jsonable(v) for v in sorted(value)]
    return value

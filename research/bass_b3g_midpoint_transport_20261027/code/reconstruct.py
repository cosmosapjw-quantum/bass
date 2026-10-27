"""Frozen saved-data algebra; no trajectory integration."""
from pathlib import Path
import sys, math, itertools
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
OLD=ROOT.parent/'bass_b3g_actual_cohort_binding_20261025'
sys.path.insert(0,str(OLD/'code'))
from binding import ROUND,C,real,reused_modules,write_json
from transport import diagonal_bound,determinant_bound
from geometry import si_to_core

def midpoint(ep,receipt,fixture):
    d=float(receipt['source_subflow_duration_tau'])/2
    if not math.isfinite(d) or d<=0: raise ValueError('positive source duration required')
    h=float(ep['h']); s=np.array([ep['sigma1'],ep['sigma2'],-ep['sigma1']-ep['sigma2']])
    rm=ep['rho_R']+ep['rho_X']; rg=ep['rho_gamma']; pi=real(ep['pi_gamma'],(3,3),'pi')
    if rm<=0 or rg<0:raise ValueError('stage matter/radiation positivity')
    rmm=rm*math.exp(3*d*1.01); rgm=rg*math.exp(d*(4*1.01+.2))
    Mh=1.01**2+3*.2**2/3+(rmm+2*rgm)/6
    Ms=np.full(3,3*1.01*.2+2*rgm/3)
    if abs(h)+d*Mh>1.01 or np.any(abs(s)+d*Ms>.2) or h-d*Mh<=.2:raise ValueError('stage box refused')
    Vh=(2*abs(h)+d*Mh)*d*Mh+np.sum((2*abs(s)+d*Ms)*d*Ms)/3+(rm*math.expm1(3*d*1.01)+2*rg*math.expm1(d*(4*1.01+.2)))/6
    Vs=3*(abs(h)*d*Ms+abs(s)*d*Mh+d*d*Mh*Ms)+abs(np.diag(pi))+2*rgm/3
    hm=float(receipt['midpoint_H_s_inv'])*fixture['L_m']/C
    S=real(receipt['midpoint_S'],(3,3),'S');sm=hm*np.diag(S)
    x0=np.array([ep['alpha'],ep['beta1'],ep['beta2']]);v0=np.array([h,s[0],s[1]]);v1=np.array([hm,sm[0],sm[1]])
    x=x0+d*(v0+v1)/2
    analytic=d*d*np.array([Vh,Vs[0],Vs[1]])/12
    empirical=ROUND*np.maximum(1,np.maximum(abs(x0),abs(x)))
    def expand(a):return np.array([a[0],a[1],a[2],a[1]+a[2]])
    return dict(coordinates=np.array([x[0],x[1],x[2],-x[1]-x[2]]),analytic=expand(analytic),empirical=expand(empirical),delta=d,stage_Mh=Mh,stage_Ms=Ms,stage_margin_h=1.01-abs(h)-d*Mh,stage_margin_sigma=.2-abs(s)-d*Ms,alpha_density_diagnostic=-math.log(receipt['midpoint_N_m3']/fixture['N0_m3'])/3,endpoint_clock_discrepancy=receipt['interval_end_tau']-receipt['interval_start_tau']-2*d)

def mapped(mid,final,operational=True):
    x=mid['coordinates'];rad=mid['analytic']+(mid['empirical'] if operational else 0)
    da=final['alpha']-x[0];bf=np.array([final['beta1'],final['beta2'],-final['beta1']-final['beta2']])
    rec=diagonal_bound(da+bf-x[1:],rad[0]+rad[1:]);det=determinant_bound(da,float(rad[0]),beta_exactly_stf=True)
    return np.diag(rec['Rhat_diagonal']),rec['eR'],det['Dhat'],det['bound']

def q14():
    n=np.concatenate([np.eye(3),-np.eye(3),np.array(list(itertools.product([-1.,1.],repeat=3)))/math.sqrt(3)])
    return n,np.array([1/15]*6+[3/40]*8)

def compensated(tensors):
    a=np.asarray(tensors);return np.array([math.fsum(a[:,i,j]) for i in range(4) for j in range(4)]).reshape(4,4)

def geometry_check(ep,fixture,radiation,core):
    scale=core.FixedScale(fixture['L_m']);a=scale.density_factor
    T=np.zeros((3,4,4));T[0,0,0]=ep['rho_R']/a;T[1,0,0]=ep['rho_X']/a;T[2]=radiation
    rho,flux,source=si_to_core(scale,T,np.zeros((3,4)),core)
    h=ep['h'];sigma=np.diag([ep['sigma1'],ep['sigma2'],-ep['sigma1']-ep['sigma2']])
    state=core.State(h,sigma,np.zeros((3,3)),np.zeros(3),ep['alpha'],rho,flux)
    actual=core.State.unpack(core.rhs(ep['tau'],state.pack(),source))
    dh=-h*h-np.sum(sigma*sigma)/3-np.sum(rho+3*source.pressure)/6
    ds=-3*h*sigma+np.sum(source.pi,axis=0)
    dr=-3*h*(rho+source.pressure)-np.einsum('ab,iab->i',sigma,source.pi)
    df=-4*h*flux-flux@sigma.T
    gamma=float(rho[2])
    scales=dict(dh=h*h+np.sum(sigma*sigma)/3+(np.sum(abs(rho))+3*np.sum(abs(source.pressure)))/6,
        dsigma=max(3*abs(h)*float(np.max(abs(sigma))),sum(float(np.max(abs(v))) for v in source.pi),gamma),
        drho=float(np.max(3*abs(h)*(abs(rho)+abs(source.pressure))+np.einsum('ab,iab->i',abs(sigma),abs(source.pi)))),
        dflux=max((4*abs(h)+float(np.linalg.norm(sigma,2)))*float(np.max(abs(flux))),abs(h)*gamma))
    raw=dict(dh=actual.h-dh,dsigma=actual.sigma-ds,drho=actual.rho-dr,dflux=actual.flux-df)
    residual={key:normalize_residual(value,scales[key]) for key,value in raw.items()}
    saved=np.asarray(ep['pi_gamma']);newpi=source.pi[2]
    return dict(raw_rhs_residuals=raw,rhs_scales=scales,normalized_rhs_residuals=residual,signed_delta_hdot=-(2*a*radiation[0,0]-2*ep['rho_gamma'])/6,signed_delta_sigmadot=newpi-saved,cQ=np.zeros((3,4)),U=source.energy_transfer,J=source.momentum_transfer)


def normalize_residual(raw,scale):
    raw=np.asarray(raw)
    if not np.all(np.isfinite(raw)) or not math.isfinite(scale) or scale<0:raise ValueError('invalid derivative residual/scale')
    if scale==0:
        if np.any(raw!=0):raise ArithmeticError('nonzero derivative on zero equation scale')
        return np.zeros_like(raw)
    result=raw/scale
    if np.max(abs(result))>ROUND:raise ArithmeticError('core RHS equation-scale mismatch')
    return result

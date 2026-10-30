#!/usr/bin/env python3
"""CE1-AF: actual original-six-cell coupled Einstein--Vlasov quadrupole/shear-work physics.

Not a new continuum angular interval certificate or production CMB sky. Frozen positive
six-cell Gauss-Legendre ray quadratures. Original massless, diagonal Bianchi-I,
Lambda=0, proper u=t/Tstar, metric (-,+,+,+).
"""
from __future__ import annotations
import csv, hashlib, json, math, sys, argparse
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp, cumulative_simpson

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'input'))
from cellwise_gl_rust import make_cell_rays,frozen_source_identity,SHEAR
SOURCE_SHA='022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035'
HISTORY_SHA={6:'6eff8cd9f31d027bbee55720332302b6fbad71b3639b5809aab6b9ce6f53e489',8:'1398980ec71662494273e05eb4bd52a78f6e6c7f208702638da6c739698f7502'}
T_END=.08
C20=math.sqrt(5/(16*math.pi))
C22=math.sqrt(15/(32*math.pi))


def sky_moments(ray2,mass,ell):
    ell=np.asarray(ell,dtype=float)
    q=ray2*np.exp(-2*ell[None,:]);rad=np.sqrt(np.sum(q,axis=1))
    if np.any(rad<=0):raise ArithmeticError('Nonpositive massless energy')
    x=q/(rad[:,None]**2)
    w=mass*rad
    vol=math.exp(-float(np.sum(ell)))
    E=vol*float(np.sum(w));P=vol*np.sum(w[:,None]*x,axis=0)
    R=vol*np.einsum('a,ai,aj->ij',w,x,x,optimize=True)
    # New physical l=2 fractional sky: even real a20 and a22 (m=+-2 conjugates)
    f0=3*P[2]/E-1
    f2=(P[0]-P[1])/E
    alpha20=4*math.pi*C20*f0
    alpha22=4*math.pi*C22*f2
    C2=(alpha20**2+2*alpha22**2)/5
    C2raw=(E/(4*math.pi))**2*C2
    return E,P,R,alpha20,alpha22,C2,C2raw


def physical_snapshot(ray2,mass,u,y):
    ell=y[:3];h=y[3:]
    E,P,R,a20,a22,C2,C2raw=sky_moments(ray2,mass,ell)
    H=float(np.mean(h));shear=h-H;pi=P-E/3
    work=float(shear@pi)
    shear_energy=float(.5*(shear@shear))
    shear_energy_prime=float(-6*H*shear_energy+work)
    q0=3*P[2]/E-1;q2=(P[0]-P[1])/E
    work_from_l2=float(E/2*(shear[2]*q0+(shear[0]-shear[1])*q2))
    theta=float(sum(h))
    sigma_prime=-theta*shear+pi
    Edot=-theta*E-float(h@P)
    Pdot=-(theta+2*h)*P+R@h
    return dict(u=float(u),ell=ell.copy(),h=h.copy(),E=float(E),P=P.copy(),R=R.copy(),
        theta=theta,H=H,sigma=shear.copy(),Pi=pi.copy(),
        shear_work=work,shear_work_from_l2=work_from_l2,
        shear_energy=shear_energy,shear_energy_prime=shear_energy_prime,sigma_prime=sigma_prime.copy(),
        shear_cancellation_residual=float((-4*H*E-work)+(-6*H*shear_energy+work)+4*H*E+6*H*shear_energy),
        alpha20=float(a20),alpha22=float(a22),C2_fractional=float(C2),C2_raw_energy=float(C2raw),
        dE_du=float(Edot),dP_du=Pdot.copy(),
        hamiltonian_constraint=float(h[0]*h[1]+h[0]*h[2]+h[1]*h[2]-E),
        pressure_trace_gap=float(np.sum(P)-E),fourth_moment_trace_gap=float(np.max(np.abs(R.sum(axis=1)-P))),
        quadrupole_to_work_gap=float(work-work_from_l2),
        conservation_residual=float(Edot+4*H*E+work))


def evolve(gl=8,n=401):
    if not(n>=41 and (n-1)%40==0):raise ValueError('n should include all frozen 41 epochs')
    if frozen_source_identity()!=SOURCE_SHA:raise RuntimeError('Original physical cell source identity drift')
    rays,mass=make_cell_rays(gl)
    ray2=rays*rays
    E0,_,_,*_=sky_moments(ray2,mass,[0.,0.,0.])
    H0=math.sqrt((E0+.5*float(SHEAR@SHEAR))/3)
    y0=np.r_[np.zeros(3),H0+SHEAR]
    def rhs(u,y):
        E,P,R,*_=sky_moments(ray2,mass,y[:3])
        h=y[3:];return np.r_[h,-sum(h)*h+P]
    t=np.linspace(0.,T_END,n)
    sol=solve_ivp(rhs,(0,T_END),y0,method='DOP853',rtol=3e-12,atol=3e-14,t_eval=t)
    if not sol.success:raise RuntimeError(sol.message)
    state=sol.y.T
    snaps=[physical_snapshot(ray2,mass,u,y) for u,y in zip(t,state)]
    if gl in HISTORY_SHA:
        src=ROOT/'input'/f'GL{gl}_DOP853_coupled_41epochs.csv'
        if hashlib.sha256(src.read_bytes()).hexdigest()!=HISTORY_SHA[gl]:raise RuntimeError('Original 41-state source altered')
        with src.open(newline='') as f:rows=list(csv.DictReader(f))
        old=np.array([[float(r['ell'+str(j)]) for j in range(1,4)]+[float(r['h'+str(j)]) for j in range(1,4)] for r in rows])
        assert np.max(np.abs(state[::(n-1)//40]-old))<5e-13
    E=np.array([z['E'] for z in snaps]);W=np.array([z['shear_work'] for z in snaps])
    F=E*np.exp((4/3)*np.sum(state[:,:3],axis=1))/E0
    integral=np.r_[0.,cumulative_simpson(W/E,x=t)]
    identity=np.log(F)+integral
    # Store the integrated anisotropic work and exactly measurable residual of energy evolution.
    for i,z in enumerate(snaps):
        z['cum_shear_work_over_E']=float(integral[i])
        z['volume_compensated_E_ratio']=float(F[i])
        z['volume_compensated_log_balance_residual']=float(identity[i])
    # Scalar identity has no small-signal division: the residual remains reliable for near-zero work.
    summary=dict(GL=gl,rays=len(mass),epochs=n,nfev=sol.nfev,E0=E0,H0=H0,
       E_end=float(E[-1]),C2_initial=snaps[0]['C2_fractional'],C2_final=snaps[-1]['C2_fractional'],
       C2_raw_initial=snaps[0]['C2_raw_energy'],C2_raw_final=snaps[-1]['C2_raw_energy'],
       shear_work_initial=float(W[0]),shear_work_final=float(W[-1]),
       shear_work_sign_changes=int(np.sum(np.signbit(W[:-1])!=np.signbit(W[1:]))),
       shear_energy_initial=snaps[0]['shear_energy'],shear_energy_final=snaps[-1]['shear_energy'],
       shear_energy_prime_initial=snaps[0]['shear_energy_prime'],shear_energy_prime_final=snaps[-1]['shear_energy_prime'],
       integrated_work_over_E=float(integral[-1]),volume_compensated_E_ratio=float(F[-1]),
       max_abs_log_balance_residual=float(np.max(np.abs(identity))),
       max_abs_constraint=float(max(abs(z['hamiltonian_constraint']) for z in snaps)),
       max_abs_pressure_trace=float(max(abs(z['pressure_trace_gap']) for z in snaps)),
       max_abs_fourth_moment_trace=float(max(abs(z['fourth_moment_trace_gap']) for z in snaps)),
       max_abs_quadrupole_work_gap=float(max(abs(z['quadrupole_to_work_gap']) for z in snaps)),
       max_abs_energy_law_residual=float(max(abs(z['conservation_residual']) for z in snaps)))
    return snaps,summary

FIELDS=['GL','u','ell1','ell2','ell3','h1','h2','h3','E','P1','P2','P3',
 'sigma1','sigma2','sigma3','Pi1','Pi2','Pi3','R11','R12','R13','R22','R23','R33',
 'alpha20','alpha22','C2_fractional','C2_raw_energy','shear_work','shear_work_l2',
 'dE_du','dP1_du','dP2_du','dP3_du','cum_shear_work_over_E',
 'volume_compensated_E_ratio','volume_compensated_log_balance_residual','hamiltonian_constraint',
 'shear_energy','shear_energy_prime','sigma1_prime','sigma2_prime','sigma3_prime']

def row(gl,z):
    return [gl,z['u'],*z['ell'],*z['h'],z['E'],*z['P'],*z['sigma'],*z['Pi'],
            z['R'][0,0],z['R'][0,1],z['R'][0,2],z['R'][1,1],z['R'][1,2],z['R'][2,2],
            z['alpha20'],z['alpha22'],z['C2_fractional'],z['C2_raw_energy'],
            z['shear_work'],z['shear_work_from_l2'],z['dE_du'],*z['dP_du'],
            z['cum_shear_work_over_E'],z['volume_compensated_E_ratio'],
            z['volume_compensated_log_balance_residual'],z['hamiltonian_constraint'],
            z['shear_energy'],z['shear_energy_prime'],*z['sigma_prime']]

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--gl-orders',default='6,8,16,64');ap.add_argument('--epochs',type=int,default=401)
    args=ap.parse_args();gls=[int(x) for x in args.gl_orders.split(',')]
    reports={};data=[]
    for gl in gls:
        z,s=evolve(gl,args.epochs);reports[str(gl)]=s
        data.extend([row(gl,x) for x in z]);print('GL',gl,'rays',s['rays'],'Eend',s['E_end'],'C2end',s['C2_final'], 'workInt',s['integrated_work_over_E'],'ratio',s['volume_compensated_E_ratio'],'balance',s['max_abs_log_balance_residual'],flush=True)
    dest=ROOT/'data';dest.mkdir(exist_ok=True,parents=True)
    report=dict(schema='bass.ce1af.original_sixcell_quadrupole_shear_work.v1',source_sha256=SOURCE_SHA,
                scientific_problem='original massless collisionless nonthermal Einstein--Vlasov shear-work and photon quadrupole stress hierarchy',
                time_u=[0,T_END],metric_signature='(-,+,+,+)',
                dimensional_Convention='original project Einstein-scale dimensionless E,P,R and u=t/Tstar; c not additionally set to 1',
                formula='Eprime=-theta E-h.P; Pprime_i=-(theta+2h_i)P_i+sum_j h_j R_ij; Eprime+4HE=-sigma.Pi; sigma_i_prime=-3H sigma_i+Pi_i; shear_energy_prime+6H shear_energy=+sigma.Pi',
                spectral_parent_pr=283,upstream_dag='9/15',ce1='PARTIAL',new_upper_nodes=0,
                derivative_data='Analytic source moment identities; discrete records numerical, not original continuum certification',
                orders=reports,production_ready=False,merge_ready=False,auto_next=False)
    (dest/'CE1AF_SHEAR_QUADRUPOLE_RESULTS.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    with (dest/'CE1AF_PHYSICAL_TIMELINE.csv').open('w',newline='') as f:
        wr=csv.writer(f);wr.writerow(FIELDS);wr.writerows(data)
    print('NEW_PHYSICS_ROWS',len(data),'FIELDS',len(FIELDS));return report

if __name__=='__main__':main()

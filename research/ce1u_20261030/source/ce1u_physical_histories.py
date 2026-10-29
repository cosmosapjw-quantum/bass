#!/usr/bin/env python3
"""CE1-U: self-consistently regenerated GL6/GL8 Einstein-Vlasov physical histories.

Source is the identical original positive six binary64 angular cells,
with a NEW stored Gauss-Legendre ray quadrature. Coordinates u=t/Tstar,
ell=log a, h=dell/du, E=8 pi G Tstar^2 rho_energy/c^2.
No fluid closure, interval solver, collision, temperature, or polarization.
"""
import sys, json, csv, math, hashlib, argparse
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
def _find_root():
    for root in Path(__file__).resolve().parents:
        if (root/'research'/'ce1t_20261030'/'cellwise_gl_rust.py').is_file():
            return root
    raise FileNotFoundError('Frozen CE1-T source not in parent directories')
ROOT=_find_root()
sys.path.insert(0,str(ROOT/'research'/'ce1t_20261030'))
from cellwise_gl_rust import make_cell_rays, frozen_source_identity, SHEAR, sha
END=.08
TIMES=np.linspace(0.,END,41)

def angular(rays,mass,ell,h=None,full=False):
    b=np.exp(-2.*np.asarray(ell,dtype=float))
    q=rays*rays*b
    rr=np.sqrt(np.sum(q,axis=1))
    vv=np.exp(-np.sum(ell)); W=mass*vv*rr
    x=q/(rr[:,None]**2) # s_i² in normal tetrad
    E=float(np.sum(W));P=np.sum(W[:,None]*x,axis=0)
    if not full:return E,P
    assert h is not None
    theta=float(sum(h));B=x@h
    Ep=float(-theta*E-np.dot(h,P))
    Pp=np.sum((W[:,None]*x)*(-theta-2*np.asarray(h)[None,:]+B[:,None]),axis=0)
    # R_ij=integral W*s_i²*s_j², R'_ij from third spatial moment
    R=np.einsum('q,qi,qj->ij',W,x,x)
    Rp=np.empty((3,3))
    for i in range(3):
        for j in range(3):
            Rp[i,j]=float(np.dot(W*x[:,i]*x[:,j],-theta+3*B-2*(h[i]+h[j])))
    # reflect-even quadrupole and hexadecapole exactly from E/P/R
    k20=math.sqrt(5/(16*math.pi));k22=math.sqrt(15/(32*math.pi))
    k40=3/(16*math.sqrt(math.pi));k42=3/8*math.sqrt(5/(2*math.pi));k44=3/16*math.sqrt(35/(2*math.pi))
    a20=k20*(3*P[2]-E);a22=k22*(P[0]-P[1])
    d20=k20*(3*Pp[2]-Ep);d22=k22*(Pp[0]-Pp[1])
    a40=k40*(35*R[2,2]-30*P[2]+3*E)
    a42=k42*(7*(R[0,2]-R[1,2])-(P[0]-P[1]))
    a44=k44*(R[0,0]-6*R[0,1]+R[1,1])
    d40=k40*(35*Rp[2,2]-30*Pp[2]+3*Ep)
    d42=k42*(7*(Rp[0,2]-Rp[1,2])-(Pp[0]-Pp[1]))
    d44=k44*(Rp[0,0]-6*Rp[0,1]+Rp[1,1])
    C2=(a20*a20+2*a22*a22)/5
    C4=(a40*a40+2*a42*a42+2*a44*a44)/9
    C2p=2*(a20*d20+2*a22*d22)/5
    C4p=2*(a40*d40+2*a42*d42+2*a44*d44)/9
    return dict(E=E,P1=float(P[0]),P2=float(P[1]),P3=float(P[2]),Eprime=Ep,
                P1prime=float(Pp[0]),P2prime=float(Pp[1]),P3prime=float(Pp[2]),
                C2=C2,C4=C4,C2prime=C2p,C4prime=C4p,
                a20=a20,a22=a22,a40=a40,a42=a42,a44=a44,
                da20=d20,da22=d22,da40=d40,da42=d42,da44=d44,
                trace_gap=abs(E-sum(P)),continuity_gap=abs(Ep+theta*E+np.dot(h,P)),
                pressure_dot_gap=float(np.max(np.abs(Pp - (-(theta+2*np.array(h))*P +R@h)))))

def rhs(u,y,rays,mass):
    ell,h=y[:3],y[3:];_,P=angular(rays,mass,ell)
    return np.r_[h,-h.sum()*h+P]

def init(rays,mass):
    E0,_=angular(rays,mass,np.zeros(3));s=SHEAR
    H=math.sqrt((E0+.5*np.dot(s,s))/3)
    return np.r_[np.zeros(3),np.asarray(H+s)]

def rk4(rays,mass,steps):
    y=init(rays,mass)
    dt=END/steps
    for k in range(steps):
        t=k*dt
        a=rhs(t,y,rays,mass);b=rhs(t+dt/2,y+dt*a/2,rays,mass)
        c=rhs(t+dt/2,y+dt*b/2,rays,mass);d=rhs(t+dt,y+dt*c,rays,mass)
        y+=dt*(a+2*b+2*c+d)/6
    return y

def solve(n:int,dest:Path):
    frozen_source_identity()
    rays,mass=make_cell_rays(n)
    y0=init(rays,mass)
    integrator=solve_ivp(lambda t,y:rhs(t,y,rays,mass),(0.,END),y0,method='DOP853',
                         rtol=3e-12,atol=3e-14,t_eval=TIMES)
    assert integrator.success,integrator.message
    rows=[]
    for u,y in zip(integrator.t,integrator.y.T):
        ell,h=y[:3],y[3:]
        m=angular(rays,mass,ell,h,full=True)
        C=h[0]*h[1]+h[0]*h[2]+h[1]*h[2]-m['E']
        theta=sum(h)
        rows.append({'u':float(u),**{f'ell{i+1}':float(v) for i,v in enumerate(ell)},
                     **{f'h{i+1}':float(v) for i,v in enumerate(h)},'theta':float(theta),
                     'H_mean':float(theta/3),'sigma2':float(.5*np.dot(h-theta/3,h-theta/3)),
                     'Hamiltonian_C':float(C),**m})
    assert len(rows)==41
    dest.mkdir(parents=True,exist_ok=True)
    with (dest/f'GL{n}_coupled_41epochs.csv').open('w',newline='') as fd:
        wr=csv.DictWriter(fd,fieldnames=list(rows[0]));wr.writeheader();wr.writerows(rows)
    rk={j:rk4(rays,mass,j) for j in (4,8,16,32,64)}
    ref=integrator.y[:,-1]
    data={'source_sha256':frozen_source_identity(),'n':n,'rays':len(mass),'time_grid':41,
          'ray_sha256':sha(rays.tobytes()),'mass_sha256':sha(mass.tobytes()),
          'DOP853_nfev':integrator.nfev,'DOP853_rtol':3e-12,'DOP853_atol':3e-14,
          'GL_ODE_status':'NUMERICAL_NOT_RIGOROUS_IVP_CERTIFICATE',
          'maximum_Hamiltonian_C':max(abs(r['Hamiltonian_C']) for r in rows),
          'maximum_pressure_trace_gap':max(r['trace_gap'] for r in rows),
          'maximum_continuity_gap':max(r['continuity_gap'] for r in rows),
          'maximum_pressure_dot_gap':max(r['pressure_dot_gap'] for r in rows),
          'end':rows[-1],'rk4_endpoint_gaps':{str(j):float(np.max(np.abs(v-ref))) for j,v in rk.items()},
          'rk4_endpoint_h_gaps':{str(j):float(np.max(np.abs(v[3:]-ref[3:]))) for j,v in rk.items()}}
    (dest/f'GL{n}_coupled_summary.json').write_text(json.dumps(data,indent=2)+'\n')
    print(f'GL{n} rays={len(mass)} maxC={data["maximum_Hamiltonian_C"]:.3e} RK4_4_h_gap={data["rk4_endpoint_h_gaps"]["4"]:.3e} C4prime_end={rows[-1]["C4prime"]:.14g}',flush=True)
    return data

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);args=p.parse_args()
    out=Path(args.out)
    result={str(j):solve(j,out) for j in (6,8)}
    (out/'coupled_summary.json').write_text(json.dumps(result,indent=2)+'\n')

#!/usr/bin/env python3
"""CE1AH: constrained coupled Einstein--Vlasov l2/l4 initial-shear tangent response.

Read-only original CE1AF source. Physical tangent about original six-cell Einstein--Vlasov
IVP. Not an exact-continuum numerical certificate, CMB likelihood or thermal sky.
"""
from __future__ import annotations
import csv, hashlib, json, math, argparse, sys
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp, cumulative_simpson

HERE=Path(__file__).resolve().parent
RESEARCH=HERE.parents[1]
ORIG=RESEARCH/'ce1af_20261030'
sys.path.insert(0,str(ORIG/'input'))
from cellwise_gl_rust import make_cell_rays, frozen_source_identity, SHEAR

SOURCE_SHA='022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035'
PARENT_HEAD='4d6a5d9c391bbd5aac1a885ff72b4f33f027e28a'
U=0.08
DIRECTIONS={'A_xy':np.array([1.,-1.,0.]),'B_axial':np.array([1.,1.,-2.])}
BASE_FIELDS=['GL','u','E','H','W','q','C2','C4','energy_ratio','constraint']
TAN_FIELDS=['GL','u','mode','dell1','dell2','dell3','dh1','dh2','dh3','dsigma1','dsigma2','dsigma3',
'dE','dP1','dP2','dP3','dH','dW','dq','dC2','dC4','dalpha20','dalpha22','dalpha40','dalpha42','dalpha44',
'denergy_ratio','d_cumulative_q','dlog_energy_balance','dconstraint']
FD_FIELDS=['GL','u','mode','eps','sign','E','W','q','C2','C4','constraint']


def moment(ray2,mass,ell,with_r=True):
    scaled=ray2*np.exp(-2*np.asarray(ell)[None,:])
    rad=np.sqrt(scaled.sum(axis=1))
    x=scaled/(rad[:,None]**2)
    omega=mass*rad*np.exp(-sum(ell))
    E=float(omega.sum())
    P=np.einsum('a,ai->i',omega,x)
    if with_r:
        R=np.einsum('a,ai,aj->ij',omega,x,x,optimize=True)
        return E,P,R,x,omega
    return E,P,x,omega


def pressure_jacobian(P,R):
    """Exact dP_i/dell_k = -P_i -2 delta_ik P_i + R_ik."""
    return R-P[:,None]-2*np.diag(P)


def normalized_harmonics_and_gradient(x,omega, E):
    """Condon--Shortley real m=0,2,4 coefficients and derivatives d/dell_k.

    Reflection-even rays -> real alpha_20,22,40,42,44 only.
    alpha_lm=4pi (int omega Y_lm)/E. Derivative includes bolometric normalization.
    """
    xx,yy,zz=x.T
    d=xx-yy
    c20=math.sqrt(5/(16*math.pi));c22=math.sqrt(15/(32*math.pi))
    c40=3/(16*math.sqrt(math.pi));c42=3/8*math.sqrt(5/(2*math.pi));c44=3/16*math.sqrt(35/(2*math.pi))
    f=np.array([c20*(3*zz-1),c22*d,
       c40*(35*zz*zz-30*zz+3),
       c42*(7*zz-1)*d,
       c44*(xx*xx-6*xx*yy+yy*yy)])
    # partial derivatives w.r.t. the three x_i=(physical direction cosine)^2
    df=np.zeros((5,len(xx),3),dtype=float)
    df[0,:,2]=3*c20
    df[1,:,0]=c22;df[1,:,1]=-c22
    df[2,:,2]=c40*(70*zz-30)
    df[3,:,0]=c42*(7*zz-1);df[3,:,1]=-c42*(7*zz-1);df[3,:,2]=7*c42*d
    df[4,:,0]=c44*(2*xx-6*yy);df[4,:,1]=c44*(2*yy-6*xx)
    ave=np.einsum('a,ka->k',omega,f)/E
    # d x_i /d ell_k =2 x_i(x_k-delta_ik)
    dxdell=2*x[:,:,None]*(x[:,None,:]-np.eye(3)[None,:,:])
    dy=np.einsum('kai,aij->kaj',df,dxdell,optimize=True)
    # d omega/dell_k = omega*(-1-x_k). Common -1 cancels normalization
    jac=4*math.pi/E*(np.einsum('a,kaj->kj',omega,dy,optimize=True)
          -np.einsum('a,ka,aj->kj',omega,f-ave[:,None],x,optimize=True))
    alpha=4*math.pi*ave
    C2=(alpha[0]**2+2*alpha[1]**2)/5
    C4=(alpha[2]**2+2*alpha[3]**2+2*alpha[4]**2)/9
    return alpha,jac,float(C2),float(C4)


def basic_observables(ray2,mass, y):
    ell=y[:3];h=y[3:]
    E,P,R,x,omega=moment(ray2,mass,ell)
    alpha,jac,C2,C4=normalized_harmonics_and_gradient(x,omega,E)
    H=float(np.mean(h));sig=h-H
    Pi=P-E/3;W=float(sig@Pi);q=W/E
    constraint=float((h[0]*h[1]+h[1]*h[2]+h[0]*h[2])-E)
    return dict(E=E,P=P,R=R,x=x,omega=omega,alpha=alpha,jac=jac,C2=C2,C4=C4,H=H,sig=sig,Pi=Pi,W=W,q=q,C=constraint)


def initial_state(ray2,mass,perturbation=None):
    E0,_,_,_,_=moment(ray2,mass,np.zeros(3))
    sig=SHEAR.copy() if perturbation is None else SHEAR+np.asarray(perturbation)
    if abs(sig.sum())>1e-12:raise ValueError('Non-traceless initial shear')
    H=math.sqrt((E0+0.5*(sig@sig))/3)
    return np.r_[np.zeros(3),H+sig]


def tangent_initial(ray2,mass,mode):
    d=DIRECTIONS[mode]
    y0=initial_state(ray2,mass)
    H0=float(np.mean(y0[3:]))
    dH=float(SHEAR@d)/(6*H0)
    return np.r_[np.zeros(3),dH+d]


def rhs_baseline(ray2,mass,y):
    _,P,*_=moment(ray2,mass,y[:3])
    h=y[3:]
    return np.r_[h,-sum(h)*h+P]


def rhs_full(ray2,mass,z):
    y=z[:6]
    _,P,R,*_=moment(ray2,mass,y[:3]);h=y[3:]
    th=float(sum(h));jp=pressure_jacobian(P,R)
    dy=np.r_[h,-th*h+P]
    tans=[]
    for k in range(2):
        t=z[6+6*k:12+6*k];dell=t[:3];dh=t[3:]
        tans.append(np.r_[dh,-th*dh-h*sum(dh)+jp@dell])
    return np.r_[dy,*tans]


def solve(ray2,mass,epochs=401,eps=1e-4,with_fd=True):
    t=np.linspace(0,U,epochs)
    y0=initial_state(ray2,mass)
    z0=np.r_[y0,tangent_initial(ray2,mass,'A_xy'),tangent_initial(ray2,mass,'B_axial')]
    def rhs(_u,z):return rhs_full(ray2,mass,z)
    s=solve_ivp(rhs,(0,U),z0,method='DOP853',rtol=3e-12,atol=3e-14,t_eval=t)
    if not s.success:raise RuntimeError(s.message)
    states=s.y.T
    finite={}
    if with_fd:
        for name,direction in DIRECTIONS.items():
            for sign in (-1,1):
                pert=sign*eps*direction
                yy=initial_state(ray2,mass,pert)
                sf=solve_ivp(lambda u,y:rhs_baseline(ray2,mass,y),(0,U),yy,
                           method='DOP853',rtol=3e-12,atol=3e-14,t_eval=t)
                if not sf.success:raise RuntimeError(sf.message)
                finite[name,sign]=sf.y.T
    return t,states,finite,s.nfev


def produce(gl=8,epochs=401,eps=1e-4,with_fd=True):
    if frozen_source_identity()!=SOURCE_SHA:raise RuntimeError('Original six-cell source identity changed')
    rays,mass=make_cell_rays(gl);ray2=rays*rays
    tt,states,finite,nfev=solve(ray2,mass,epochs,eps,with_fd)
    base=[];tangent=[];fdrows=[]
    traces={name:[] for name in DIRECTIONS}
    # Moment and harmonic fields along actual original self-consistent dynamical histories.
    for i,(u,z) in enumerate(zip(tt,states)):
        y=z[:6];o=basic_observables(ray2,mass,y)
        e=o['E'];sig=o['sig'];p=o['P'];jp=pressure_jacobian(p,o['R']);alpha=o['alpha']
        F=e*math.exp(4*sum(y[:3])/3)/.9
        base.append([gl,u,e,o['H'],o['W'],o['q'],o['C2'],o['C4'],F,o['C']])
        for k,name in enumerate(DIRECTIONS):
            tan=z[6+6*k:12+6*k];de=tan[:3];dh=tan[3:]
            dE=float((-e*np.ones(3)-p)@de)
            dP=jp@de
            dH=float(dh.mean());dsig=dh-dH;dpi=dP-dE/3
            dW=float(dsig@o['Pi']+sig@dpi)
            dq=(dW-o['q']*dE)/e
            dalpha=o['jac']@de
            dC2=(2*alpha[0]*dalpha[0]+4*alpha[1]*dalpha[1])/5
            dC4=(2*alpha[2]*dalpha[2]+4*alpha[3]*dalpha[3]+4*alpha[4]*dalpha[4])/9
            dF=F*(dE/e+4*sum(de)/3)
            # delta C = sum_i (theta-h_i)delta h_i -delta E
            dC=float((sum(y[3:])-y[3:])@dh-dE)
            tangent.append([gl,u,name,*de,*dh,*dsig,dE,*dP,dH,dW,dq,dC2,dC4,*dalpha,dF,0.,0.,dC])
            traces[name].append(dq)
        if finite:
            for (name,sign),r in finite.items():
                ob=basic_observables(ray2,mass,r[i])
                fdrows.append([gl,u,name,eps,sign,ob['E'],ob['W'],ob['q'],ob['C2'],ob['C4'],ob['C']])
    accum={name:np.r_[0.,cumulative_simpson(np.array(v),x=tt)] for name,v in traces.items()}
    for row in tangent:
        i=int(np.rint(row[1]* (epochs-1)/U))
        mode=row[2]
        row[-3]=float(accum[mode][i])
        # row[-4] = delta F, row[-3] = int delta q, row[-2] = delta log F + int delta q.
    # Re-evaluate exact reference index position from schema (no hidden magic).
    idx={key:TAN_FIELDS.index(key) for key in TAN_FIELDS}
    for row in tangent:
        i=int(np.rint(row[1]*(epochs-1)/U)); name=row[2]
        row[idx['dlog_energy_balance']]=float(row[idx['denergy_ratio']]/base[i][8]+accum[name][i])
    max_base_C=max(abs(r[-1]) for r in base)
    max_tan_C=max(abs(r[-1]) for r in tangent)
    max_resp_log=max(abs(row[idx['dlog_energy_balance']]) for row in tangent)
    # Restore immutable original 41-epoch data identity when available for direct ancestry.
    origdiff=None
    if gl in (6,8) and epochs==401:
        f=ORIG/'input'/f'GL{gl}_DOP853_coupled_41epochs.csv'
        with f.open(newline='') as fh: saved=list(csv.DictReader(fh))
        ys=np.array([[float(x[f'ell{k}']) for k in range(1,4)]+[float(x[f'h{k}']) for k in range(1,4)] for x in saved])
        origdiff=float(np.max(np.abs(states[::10,:6]-ys)))
    summary={'GL':gl,'rays':len(mass),'epochs':epochs,'nfev':nfev,'baseline_constraint_max':max_base_C,
      'tangent_constraint_max':max_tan_C,'response_energy_balance_max':max_resp_log,
      'original_41point_max_state_difference':origdiff,'Eend':base[-1][2],'Wend':base[-1][4],
      'C2end':base[-1][6],'C4end':base[-1][7],
      'response_endpoint':{name:{key:float(next(r for r in tangent[::-1] if r[2]==name)[idx[key]])
      for key in ('dW','dq','dC2','dC4','dE','denergy_ratio','dconstraint')} for name in DIRECTIONS},
      'fd_eps':eps,'fd_rows':len(fdrows)}
    if finite:
        maxerr={};scales={}
        for name in DIRECTIONS:
            rr=[x for x in tangent if x[2]==name]
            for obs,bcol,tcol in [('E',2,'dE'),('W',4,'dW'),('q',5,'dq'),('C2',6,'dC2'),('C4',7,'dC4')]:
                ar_p=np.array([x[['E','W','q','C2','C4'].index(obs)+5] for x in fdrows if x[2]==name and x[4]==1])
                ar_m=np.array([x[['E','W','q','C2','C4'].index(obs)+5] for x in fdrows if x[2]==name and x[4]==-1])
                deriv=(ar_p-ar_m)/(2*eps)
                ana=np.array([x[idx[tcol]] for x in rr])
                maxerr[f'{name}.{obs}']=float(np.max(np.abs(deriv-ana)))
                scales[f'{name}.{obs}']=float(np.max(np.abs(ana)))
        summary['fd_max_abs_errors']=maxerr
        summary['fd_observable_scales']=scales
    return base,tangent,fdrows,summary


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--orders',default='6,8,16')
    ap.add_argument('--epochs',type=int,default=401)
    ap.add_argument('--eps',type=float,default=1e-4)
    ap.add_argument('--output',default=None)
    args=ap.parse_args()
    root=Path(args.output) if args.output else HERE.parent/'data'
    root.mkdir(parents=True,exist_ok=True)
    records=[[],[],[]];r={}
    for gl in [int(v) for v in args.orders.split(',')]:
        b,t,f,s=produce(gl,args.epochs,args.eps,with_fd=gl in (6,8))
        for arr,part in zip(records,(b,t,f)):arr.extend(part)
        r[str(gl)]=s
        print('GL',gl,'rows',len(b),len(t),len(f),'base_C',s['baseline_constraint_max'],
           'tan_C',s['tangent_constraint_max'],'log_balance',s['response_energy_balance_max'],flush=True)
    for file,headers,data in [('CE1AH_BASELINE_PHYSICAL.csv',BASE_FIELDS,records[0]),
                              ('CE1AH_TANGENT_PHYSICAL.csv',TAN_FIELDS,records[1]),
                              ('CE1AH_FINITE_PERTURBED_PHYSICAL.csv',FD_FIELDS,records[2])]:
        with (root/file).open('w',newline='') as fp:
            c=csv.writer(fp);c.writerow(headers);c.writerows(data)
    result={'schema':'bass.ce1ah.original_coupled_Einstein_Vlasov_constraint_preserving_tangent.v1',
       'source_sha256':SOURCE_SHA,'original_parent_pr':286,'original_parent_head':PARENT_HEAD,
       'metric_signature':'(-,+,+,+)','Lambda':0,'collisionless_massless':True,
       'physical_time_u':[0,U],'units':'Original BASS dimensionless E,P,R and proper u=t/Tstar',
       'original_six_cell_unchanged':True,'tangent_initial_directions':{k:v.tolist() for k,v in DIRECTIONS.items()},
       'initial_delta_H_formula':'sigma0.dot(delta_sigma0)/(6*H0); exactly preserves linearized 3H^2=E+0.5sigma^2 constraint',
       'angular_source':'GL positive angular approximation; not certified continuum quadrature enclosure',
       'baseline_rows':len(records[0]),'tangent_rows':len(records[1]),'perturbed_rows':len(records[2]),
       'details':r,'upper_DAG':'9/15','new_upper_node':0,'CE1':'PARTIAL',
       'production_ready':False,'merge_ready':False,'auto_next':False,
       'actual_observation':'normal-frame nonthermal bolometric fractional sky, not CMB temperature or posterior'}
    (root/'CE1AH_PHYSICAL_RESPONSE_RESULTS.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print('CE1AH_PHYSICS_ROWS',*[len(r) for r in records]);return result

if __name__=='__main__':main()

#!/usr/bin/env python3
"""CE1-AE source-locked, true 6D Einstein-Vlasov physical time histories.

Numerical GL angular quadratures for original six positive cells, NOT interval
certification of the exact continuous angular source. Separate strict theorem
for physical continuous-time operator is established in spectral_gap_certificate.py.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math,sys
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
from scipy.interpolate import CubicHermiteSpline

BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE/'input'))
from cellwise_gl_rust import make_cell_rays,frozen_source_identity,SHEAR
SOURCE='022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035'
HISTORY_SHA={6:'6eff8cd9f31d027bbee55720332302b6fbad71b3639b5809aab6b9ce6f53e489',8:'1398980ec71662494273e05eb4bd52a78f6e6c7f208702638da6c739698f7502'}
TMAX=.08
COEFF=math.sqrt(math.pi)*np.asarray([.25,math.sqrt(5)/2,math.sqrt(35)/4])


def angular(ray2,weight,ell):
    q=ray2*np.exp(-2*np.asarray(ell))
    Q=q.sum(axis=1)
    r=np.sqrt(Q)
    weights=weight*r
    directions=q/Q[:,None]
    xx,yy,zz=directions.T
    T=np.column_stack((35*zz*zz-30*zz+3,(xx-yy)*(7*zz-1),xx*xx-6*xx*yy+yy*yy))
    W0=weights.sum()
    vol=np.exp(-sum(ell))
    energy=float(vol*W0)
    pressure=vol*(weights[:,None]*directions).sum(axis=0)
    X=COEFF*((weights@T)/W0)
    return energy,pressure,X


def evolve(n:int,N:int):
    assert frozen_source_identity()==SOURCE
    rays,mass=make_cell_rays(n)
    rays2=rays*rays
    E0,_,_=angular(rays2,mass,[0,0,0])
    H0=math.sqrt((E0+0.5*float(SHEAR@SHEAR))/3)
    y0=np.r_[np.zeros(3),np.array(SHEAR)+H0]
    def rhs(t,y):
        E,P,_=angular(rays2,mass,y[:3])
        h=y[3:]
        return np.r_[h,-sum(h)*h+P]
    times=np.linspace(0,TMAX,N)
    sol=solve_ivp(rhs,(0,TMAX),y0,method='DOP853',rtol=3e-12,atol=3e-14,t_eval=times)
    assert sol.success and sol.y.shape==(6,N)
    values=[]
    for u,y in zip(sol.t,sol.y.T):
        E,P,X=angular(rays2,mass,y[:3]);h=y[3:]
        C=float(h[0]*h[1]+h[0]*h[2]+h[1]*h[2]-E)
        C4=float(X@X)
        C4raw=(E/(4*math.pi))**2*C4
        values.append([u,*y[:3],*h,E,*P,*X,C4,C4raw,C])
    a=np.array(values)
    assert np.all(a[:,4:7]>0)
    assert np.max(np.abs(a[:,-1]))<3e-11
    if n in HISTORY_SHA:
        path=BASE/'input'/f'GL{n}_DOP853_coupled_41epochs.csv'
        assert hashlib.sha256(path.read_bytes()).hexdigest()==HISTORY_SHA[n]
        with path.open() as f: saved=list(csv.DictReader(f))
        old=np.array([[float(r[f'ell{i}']) for i in (1,2,3)]+[float(r[f'h{i}']) for i in (1,2,3)] for r in saved])
        stride=(N-1)//40
        max_delta=float(np.max(np.abs(a[::stride,1:7]-old)))
        assert max_delta<5e-13,(n,max_delta)
    else:max_delta=None
    weights=np.ones(N);weights[1:-1:2]=4;weights[2:-1:2]=2
    weights*=TMAX/(N-1)/3
    X=a[:,11:14]  # columns: u, ell1:3, h1:3, E, P1:3, X1:3
    assert X.shape==(N,3)
    A=np.sqrt(weights[:,None])*X
    _,sig,Vh=np.linalg.svd(A,full_matrices=False)
    G=A.T@A
    G=(G+G.T)/2
    C4avg=float(weights@a[:,-3]/TMAX)
    rawavg=float(weights@a[:,-2]/TMAX)
    evals=sig*sig
    cp={}
    for tmax in (.02,.04,.06,.08):
        m=round(tmax/(TMAX/(N-1)))
        if m%2:raise ArithmeticError('Simpson prefix must have even number of steps')
        subweights=weights[:m+1].copy()
        subweights[0]*=.5 if m else 1
        subweights[-1]=TMAX/(N-1)/3
        # prefix weights interior as standard Simpson, not global endpoint
        subweights[0]=TMAX/(N-1)/3
        cp[f'{tmax:.2f}']={
          'integrated_C4_fractional':float(subweights@a[:m+1,-3]),
          'integrated_C4_raw_energy':float(subweights@a[:m+1,-2])}
    return {'GL':n,'rays':int(len(mass)),'epochs':N,'source_sha256':SOURCE,
            'ray_sha256':hashlib.sha256(rays.tobytes()).hexdigest(),
            'mass_sha256':hashlib.sha256(mass.tobytes()).hexdigest(),
            'nfev':int(sol.nfev),'original_saved_max_state_delta':max_delta,
            'max_Hamiltonian_residual':float(np.max(abs(a[:,-1]))),
            'time_Gram_G':G.tolist(),'time_Gram_eigenvalues_numeric':evals.tolist(),
            'time_Gram_singular_values_numeric':sig.tolist(),
            'numerical_right_eigenvectors':Vh.tolist(),
            'time_avg_C4_fractional':C4avg,'time_avg_C4_raw_energy':rawavg,
            'initial_C4_fractional':float(a[0,-3]),'terminal_C4_fractional':float(a[-1,-3]),
            'initial_C4_raw_energy':float(a[0,-2]),'terminal_C4_raw_energy':float(a[-1,-2]),
            'time_power_cumulants':cp,'not_certified_by_numerical_quadrature':True},a


def hermite_41_gram(n):
    path=BASE/'input'/f'GL{n}_PHYSICAL_TIMEJETS.csv'
    with path.open() as fd: rows=list(csv.DictReader(fd))
    assert len(rows)==41
    t=np.array([float(row['u']) for row in rows])
    X=np.array([[float(row[f'X{i}']) for i in range(3)] for row in rows])
    dX=np.array([[float(row[f'dX{i}']) for i in range(3)] for row in rows])
    herm=CubicHermiteSpline(t,X,dX,axis=0)
    # 4-point Gauss rule integrates the square of each cubic exactly in real arithmetic
    q,w=np.polynomial.legendre.leggauss(4)
    quad_times=[];quad_weights=[]
    for lo,hi in zip(t[:-1],t[1:]):
        quad_times.extend(((hi+lo)/2+(hi-lo)*q/2).tolist())
        quad_weights.extend(((hi-lo)*w/2).tolist())
    mat=np.sqrt(np.asarray(quad_weights)[:,None])*herm(np.asarray(quad_times))
    sig=np.linalg.svd(mat,compute_uv=False)
    return {'GL':n,'interpolant':'cubic Hermite from immutable 41 original-saved 6-cell l4 time jets',
            'quadrature_rule':'4 Gauss nodes per cell; polynomial product degree 6, exact in real arithmetic',
            'epochs_quadrature':len(quad_times),'time_Gram_eigenvalues_numeric':(sig*sig).tolist(),
            'numerical_only':True}


def main():
    p=argparse.ArgumentParser();p.add_argument('--gl-orders',default='6,8,16,64')
    p.add_argument('--dense',type=int,default=401);p.add_argument('--fine',type=int,default=1601)
    args=p.parse_args()
    gls=[int(z) for z in args.gl_orders.split(',')]
    if args.dense<41 or (args.dense-1)%40 or (args.dense-1)%2:raise ValueError('dense N=1+multiple-of-40 and Simpson compatible')
    if (args.fine-1)%(args.dense-1):raise ValueError('fine N nested in dense N')
    data={};records=[]
    for n in gls:
        report,arr=evolve(n,args.dense)
        data[str(n)]=report
        for row in arr:
            records.append([n,*[float(x) for x in row]])
        print('GL',n,'rays',report['rays'],'epochs',report['epochs'],'eig3',report['time_Gram_eigenvalues_numeric'][-1],
              'C4avg',report['time_avg_C4_fractional'],'C4rawavg',report['time_avg_C4_raw_energy'],flush=True)
    for n in (6,8):
        if n not in gls:continue
        fine,_=evolve(n,args.fine)
        data[str(n)]['fine_time_Gram_eigenvalues_numeric']=fine['time_Gram_eigenvalues_numeric']
        data[str(n)]['fine_time_avg_C4_fractional']=fine['time_avg_C4_fractional']
        data[str(n)]['fine_time_avg_C4_raw_energy']=fine['time_avg_C4_raw_energy']
        data[str(n)]['Hermite_from_original_41']=hermite_41_gram(n)
        rel=np.max(abs((np.array(data[str(n)]['time_Gram_eigenvalues_numeric'])-
                        np.array(fine['time_Gram_eigenvalues_numeric']))/
                         np.array(fine['time_Gram_eigenvalues_numeric'])))
        data[str(n)]['max_relative_dense_vs_fine_eigen_difference']=float(rel)
        assert rel<5e-4,(n,rel)
    report={'schema':'bass.ce1ae.original_six_cell_continuous_time_integrated_l4_deterministic_spectrum.v1',
          'parent_pr':281,'parent_head':'f80f03d33a8b98cd49dfb9cda85ae316d868cdf6',
          'original_source_sha256':SOURCE,'time_domain_u':[0,.08],
          'time_measure':'unweighted du (dimensionless proper time t/Tstar), not probability over skies',
          'kernel':'K4(u,v)=X(u) dot X(v); physical sky bolometric nonthermal',
          'data':data,'UPPER_DAG':'9/15','CE1':'PARTIAL',
          'production_ready':False,'merge_ready':False,'auto_next':False,
          'claim_boundary':'All continuous-time G numbers NUMERICALLY_CHECKED GL quadratures, true continuum lower separate rigorous derivative lemma; not observed CMB'}
    (BASE/'data'/'CONTINUOUS_TIME_INTEGRATED_PHYSICS.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    with (BASE/'data'/'COUPLED_SIXCELL_DENSE_TIME_SKY.csv').open('w',newline='') as f:
        wr=csv.writer(f);wr.writerow(['GL','u','ell1','ell2','ell3','h1','h2','h3','E','P1','P2','P3','X40','X42','X44','C4_fractional','C4_raw_energy','Hamiltonian_C']);wr.writerows(records)
    print('TOTAL original coupled physical records',len(records))
    return report

if __name__=='__main__':main()

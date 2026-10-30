#!/usr/bin/env python3
"""New original BASS GL6/GL8 six-cell physical angular l4 time jets and K4 time kernels.
Read immutable 41-state DOP853 geometry. This is numerically evaluated sky data;
not the continuum initial-jet interval certificate in initial_jet_certificate.py.
"""
import csv,json,hashlib,math,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
ORIGINAL=ROOT/'original_source'
sys.path.insert(0,str(ORIGINAL))
from cellwise_gl_rust import make_cell_rays,frozen_source_identity
EXPECTED='022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035'
HISTORY_SHA={6:'6eff8cd9f31d027bbee55720332302b6fbad71b3639b5809aab6b9ce6f53e489',8:'1398980ec71662494273e05eb4bd52a78f6e6c7f208702638da6c739698f7502'}
CFAC=4*np.pi*np.array([3/(16*np.sqrt(np.pi)), 3/8*np.sqrt(5/(2*np.pi)), 3/16*np.sqrt(35/(2*np.pi))])
SCALE=np.array([1.,math.sqrt(2),math.sqrt(2)])/3

def jets(ray,weight,ell,h):
    Bfac=np.exp(-2*np.asarray(ell));q=ray*ray*Bfac;Q=q.sum(axis=1);rr=np.sqrt(Q)
    x=q/Q[:,None];W=weight*rr
    vol=np.exp(-sum(ell));E=vol*sum(W);P=vol*((W[:,None]*x).sum(axis=0))
    a=-(sum(h))*h+P
    B=x@h;xp=2*x*(B[:,None]-h[None,:]);Cp=np.sum(x*(h*h),axis=1)
    Bdot=2*(B*B-Cp)+x@a
    xpp=4*x*(B[:,None]-h[None,:])**2+2*x*(Bdot[:,None]-a[None,:]);
    Wp=-B;Wpp=2*Cp-B*B-x@a
    xx,yy,zz=x.T;dx,dy,dz=xp.T;ddx,ddy,ddz=xpp.T
    T=np.array([35*zz*zz-30*zz+3,(xx-yy)*(7*zz-1),xx*xx-6*xx*yy+yy*yy])
    Tp=np.array([(70*zz-30)*dz,(dx-dy)*(7*zz-1)+7*(xx-yy)*dz,(2*xx-6*yy)*dx+(2*yy-6*xx)*dy])
    Tpp=np.array([(70*zz-30)*ddz+70*dz*dz,(ddx-ddy)*(7*zz-1)+14*(dx-dy)*dz+7*(xx-yy)*ddz,(2*xx-6*yy)*ddx+(2*yy-6*xx)*ddy+2*dx*dx-12*dx*dy+2*dy*dy])
    M=T@W;Mp=(Tp+T*Wp)@W;Mpp=(Tpp+2*Tp*Wp+T*Wpp)@W
    E0=W.sum();E0p=W@Wp;E0pp=W@Wpp
    f=M/E0;fp=(Mp-f*E0p)/E0;fpp=(Mpp-f*E0pp-2*fp*E0p)/E0
    X=f*CFAC*SCALE;Xp=fp*CFAC*SCALE;Xpp=fpp*CFAC*SCALE
    return {'alpha':(f*CFAC).tolist(),'X':X.tolist(),'dX_du':Xp.tolist(),'d2X_du2':Xpp.tolist(),
            'E':float(E),'pressure':P.tolist(),'hprime':a.tolist(),'C4':float(X@X),
            'C4prime':float(2*X@Xp),'C4second':float(2*(Xp@Xp+X@Xpp)),
            'jac_ell_shear_work':'direct collisionless exact GL angular source; initial time independent of H_common by normalized cancellation'}

def run(n):
    assert frozen_source_identity()==EXPECTED
    ray,mass=make_cell_rays(n)
    csvpath=ROOT/'input'/f'GL{n}_DOP853_coupled_41epochs.csv'
    assert hashlib.sha256(csvpath.read_bytes()).hexdigest()==HISTORY_SHA[n]
    rows=list(csv.DictReader(csvpath.open())); assert len(rows)==41
    result=[]
    for r in rows:
        ell=np.array([float(r[f'ell{i}']) for i in range(1,4)])
        h=np.array([float(r[f'h{i}']) for i in range(1,4)])
        v=jets(ray,mass,ell,h);result.append({'u':float(r['u']),**v})
    U=np.array([r['u'] for r in result]);X=np.array([r['X'] for r in result]);D=np.array([r['dX_du'] for r in result]);DD=np.array([r['d2X_du2'] for r in result])
    S=X.T@X;lam=np.linalg.eigvalsh(S)[::-1]
    out=ROOT/'data'/f'GL{n}_ORIGINAL_L4_TIMEJET_41.csv'
    with out.open('w',newline='') as fo:
        writer=csv.writer(fo)
        writer.writerow(['u','E','P1','P2','P3','alpha40','alpha42','alpha44','X0','X1','X2','dX0','dX1','dX2','d2X0','d2X1','d2X2','C4','C4prime','C4second'])
        for r in result:writer.writerow([r['u'],r['E'],*r['pressure'],*r['alpha'],*r['X'],*r['dX_du'],*r['d2X_du2'],r['C4'],r['C4prime'],r['C4second']])
    with (ROOT/'data'/f'GL{n}_ORIGINAL_L4_K4_TIME_DERIV_1681.csv').open('w',newline='') as fo:
        writer=csv.writer(fo);writer.writerow(['u','v','K4','dK4_du','dK4_dv','d2K4_dudv','status'])
        for i in range(41):
            for j in range(41):
                writer.writerow([U[i],U[j],float(X[i]@X[j]),float(D[i]@X[j]),float(X[i]@D[j]),float(D[i]@D[j]),'original-frozen-binary64-geometry-GL-only'])
    fder=np.gradient([r['C4'] for r in result],U,edge_order=2)
    # Finite-difference on 0.002 grid is diagnostic, not error certificate
    diag={'schema':'bass.ce1ac.original_GL_l4_timejet_physics.v1','order':n,'rays':len(mass),'n_states':len(rows),'pairs':41**2,
          'original_source_sha256':EXPECTED,'frozen_history_sha256':HISTORY_SHA[n],
          'initial':result[0],'final':result[-1],
          'sampled_Gram_eigenvalues_numeric':lam.tolist(),
          'sampled_Gram_third_eigenvalue_status':'NUMERICAL_ONLY_NOT_CONTINUUM_CERTIFIED',
          'max_K4_symmetry_gap':float(np.max(abs(X@X.T-(X@X.T).T))),
          'max_K4_time_derivative_exchange_gap':float(np.max(abs(D@X.T-(X@D.T).T))),
          'max_41pt_C4prime_vs_3pt_gradient_gap':float(np.max(abs(fder-np.array([r['C4prime'] for r in result])))),
          'status':'NEW_ORIGINAL_PHYSICAL_DATA_NUMERICALLY_CHECKED; no thermal CMB or ensemble likelihood',
          'upper_DAG':'9/15','CE1':'PARTIAL','production_ready':False,'auto_next':False}
    (ROOT/'data'/f'GL{n}_L4_TIMEJET_SUMMARY.json').write_text(json.dumps(diag,indent=2)+'\n')
    print('GL',n,'Eend',result[-1]['E'],'C4dot(0)',result[0]['C4prime'],'C4dot(end)',result[-1]['C4prime'],'sample lam',lam,flush=True)
    return diag
if __name__=='__main__':
    for n in [6,8]:run(n)

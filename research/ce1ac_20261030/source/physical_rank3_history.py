"""CE1-AC: real original-positive-cell coupled Einstein-Vlasov l=4 time-history data.

GL6 and GL8 reuse original exact saved 41-epoch geometry; GL16 and GL64 are new
source-locked self-consistent DOP853 numerical solutions (NOT interval-certified).
"""
from __future__ import annotations
import csv,hashlib,json,math,sys
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
BASE=Path(__file__).resolve().parents[1]
from source_paths import SRC,REPLAY,INPUT
sys.path.insert(0,str(SRC))
sys.path.insert(0,str(REPLAY))
from cellwise_gl_rust import make_cell_rays,frozen_source_identity
from replay_dop853 import init,rhs,EXPHASH
SOURCE='022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035'
TIMES=np.linspace(0.,.08,41)


def compute(n):
    assert frozen_source_identity()==SOURCE
    rays,mass=make_cell_rays(n)
    if n in (6,8):
        p=INPUT/f'GL{n}_DOP853_coupled_41epochs.csv'
        assert hashlib.sha256(p.read_bytes()).hexdigest()==EXPHASH[n]
        with p.open() as f:rows=list(csv.DictReader(f))
        y=np.asarray([[float(row[f'ell{i}']) for i in (1,2,3)]+[float(row[f'h{i}']) for i in (1,2,3)] for row in rows],dtype=np.float64)
        t=np.asarray([float(row['u']) for row in rows]);nfev=None;origin='ORIGINAL_CE1AA_SAVED_DOP853_BINARY64_41';
        assert len(rows)==41 and np.array_equal(t,TIMES)
    else:
        y0=init(rays,mass)
        sol=solve_ivp(lambda t,y:rhs(t,y,rays,mass),(0.,.08),y0,method='DOP853',
                      rtol=3e-12,atol=3e-14,t_eval=TIMES)
        assert sol.success and sol.y.shape==(6,41)
        y=sol.y.T;t=sol.t;nfev=sol.nfev;origin='FRESH_GL_SOURCE_COUPLED_DOP853_NUMERICAL'
    raw=(rays*rays)
    X=[];physical=[]
    scale=math.sqrt(math.pi)*np.asarray([.25,math.sqrt(5)/2,math.sqrt(35)/4])
    for u,row in zip(t,y):
        ell,h=row[:3],row[3:]
        q=raw*np.exp(-2*ell)
        rr=np.sqrt(np.sum(q,axis=1)); w=mass*rr
        uvec=q/(rr[:,None]**2)
        xx,yy,zz=uvec.T
        T=np.stack([35*zz*zz-30*zz+3,(xx-yy)*(7*zz-1),xx*xx-6*xx*yy+yy*yy],axis=1)
        ave=(w@T)/np.sum(w)
        x=ave*scale
        X.append(x)
        E=float(np.sum(w)*np.exp(-ell.sum()))
        P=np.exp(-ell.sum())*(w[:,None]*uvec).sum(axis=0)
        C=h[0]*h[1]+h[0]*h[2]+h[1]*h[2]-E
        physical.append({'u':float(u),'ell':list(map(float,ell)),'h':list(map(float,h)),
                         'E':E,'P':P.tolist(),'Hamiltonian_C':float(C),
                         'X40':float(x[0]),'X42':float(x[1]),'X44':float(x[2])})
    X=np.asarray(X)
    S=X.T@X
    eig=np.linalg.eigvalsh(S)[::-1]
    # Thin QR gives useful singular-value check without squaring conditioning.
    svals=np.linalg.svd(X,compute_uv=False)
    phi3=np.linalg.svd(X,full_matrices=False)[2][-1,:]
    triple=np.linalg.det(X[[0,20,40],:])
    return {'GL':n,'rays':len(mass),'provenance':origin,'source_sha256':SOURCE,
            'ray_sha256':hashlib.sha256(rays.tobytes()).hexdigest(),
            'mass_sha256':hashlib.sha256(mass.tobytes()).hexdigest(),
            'fresh_solver_rhs_evals':nfev,
            'initial_X':X[0].tolist(),'terminal_X':X[-1].tolist(),
            'gram_eigenvalues_numeric':eig.tolist(),
            'svd_squared_eigenvalues':(svals**2).tolist(),
            'smallest_right_singular_vector':phi3.tolist(),
            'three_epoch_0_020_040_det_X_numeric':float(triple),
            'max_Hamiltonian_C':max(abs(row['Hamiltonian_C']) for row in physical),
            'states':physical}

def main():
    results={str(n):compute(n) for n in (6,8,16,64)}
    out=BASE/'data'/'PHYSICAL_41_EPOCH_GL6_GL8_GL16_GL64.json'
    out.write_text(json.dumps({'schema':'bass.ce1ac.positive_six_cell_physical_time_modes.v1',
                               'assertions':{'actual_physical_model':'massless collisionless original six positive cell Bianchi I',
                                             'continuous_angular_source_certified_by_GL64':False,
                                             'GL16_GL64_IVP_certified':False,
                                             '41_epoch_rank3_exact_continuum_certified':False},
                               'results':results},indent=2)+'\n')
    with (BASE/'data'/'PHYSICAL_41_EPOCH_JET_TIMELINES.csv').open('w',newline='') as f:
        wr=csv.writer(f);wr.writerow(['GL','u','ell1','ell2','ell3','h1','h2','h3','E','P1','P2','P3','Hamiltonian_C','X40','X42','X44'])
        for n,dat in results.items():
            for row in dat['states']:
                wr.writerow([n,row['u'],*row['ell'],*row['h'],row['E'],*row['P'],row['Hamiltonian_C'],row['X40'],row['X42'],row['X44']])
    for n,v in results.items():print(n,'rays',v['rays'],'evals',v['fresh_solver_rhs_evals'],'eigen3',v['gram_eigenvalues_numeric'][-1],
                                    'svd_eigen3',v['svd_squared_eigenvalues'][-1],'triple',v['three_epoch_0_020_040_det_X_numeric'],
                                    'Cmax',v['max_Hamiltonian_C'])
    return results
if __name__=='__main__':main()

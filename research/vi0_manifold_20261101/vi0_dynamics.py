"""BASS VI0 exact class-A constraint propagation and covariant scalar Kato frame lift.

Independent, pure NumPy/SymPy source-equivalent mathematical implementation.
No production import, no polarized Boltzmann or type-II migration.
Source PR #310 HEAD: 71adfbb2948f6c23725a01dfc048e90623a9eab5.
BASS source original main: 9c6506e4e2087129a8b674ff10438e5db1a55c9d.
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import numpy as np
import sympy as sp
from scipy.integrate import solve_ivp

HERE = Path(__file__).resolve().parent
ORIGINAL_MAIN = '9c6506e4e2087129a8b674ff10438e5db1a55c9d'
PARENT_PR = 310
PARENT_HEAD = '71adfbb2948f6c23725a01dfc048e90623a9eab5'
ORIGINAL_BLOBS = {
    'bianchi/conventions.py':'09cbbf1046f292506a009bd45a0598ec0da65da5',
    'bianchi/matter/fluid.py':'41905ff26914b2a7931ce2281d67b25fbde273b5',
    'bianchi/charts/general.py':'115aec90df83d097904695817b6aa337d5ba76ee',
    'bianchi/charts/class_a.py':'305438f3f82919390282d469bca7d3185451aed9',
    'compiler/lowering/rust_typeii.py':'108fe5810af80c251b0c82fda517c57c3ee0c3fb',
    'generated/rust/typeii/typeii_kato.rs':'9c8d49b6d42daf28734b4d439ca50f6535ee3519',
    'docs/superpowers/specs/2026-08-21-g-dyn-manifold-vi0-design.md':'fff778b7ac55a2580097fa4780eefd7b41cea77c',
}
EPS=np.zeros((3,3,3),dtype=int)
for i,j,k in [(0,1,2),(1,2,0),(2,0,1)]:
    EPS[i,j,k]=1; EPS[i,k,j]=-1
AXES=np.array([[1.,0,0],[-1.,0,0],[0,1.,0],[0,-1.,0],[0,0,1.],[0,0,-1.]])
WEIGHTS=np.ones(6)/6 # w/(4 pi), original 6-axis fixture; not a quadrature certification


def original_source_guard(root:Path):
    """Check original committed Git blob bytes on an actual GitHub checkout."""
    for path, expected in ORIGINAL_BLOBS.items():
        data=(root/path).read_bytes()
        got=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\x00'+data).hexdigest()
        if got!=expected: raise ValueError(f'ORIGINAL_OWNER_BLOB_DRIFT {path} {got}')
    return len(ORIGINAL_BLOBS)


def physical_chart(z,gamma):
    """Return exact PR310 positively-rooted 7D VI0 chart as array-valued state.

    z=(Sigma_plus,Sigma_minus,N22,minus_N33,v1,v2,v3).
    Complex-step differentiation is accepted for local analytic derivative checks.
    """
    sp_,sm_,p,r=z[:4]; v=np.asarray(z[4:7]); v2=v@v
    gp=1+(gamma-1)*v2
    omstar=1-sp_**2-sm_**2-(p+r)**2/12
    beta=3*gamma**2/gp**2*(v[0]**2/(p+r)**2+v[1]**2/r**2+v[2]**2/p**2)
    om=2*omstar/(1+np.sqrt(1+4*beta*omstar))
    m=3*gamma*om/gp
    b23=m*v[0]/(p+r);b13=-m*v[1]/r;b12=-m*v[2]/p
    S=np.array([[-2*sp_,b12,b13],
                [b12,sp_+np.sqrt(3)*sm_,b23],
                [b13,b23,sp_-np.sqrt(3)*sm_]])
    N=np.diag([0*p,p,-r])
    return om,S,N,v


def checked_chart(z,gamma):
    z=np.asarray(z,float)
    sp_,sm_,p,r=z[:4]; v=z[4:]
    if not (0<gamma<2 and p>0 and r>0 and v@v<1 and
            1-sp_**2-sm_**2-(p+r)**2/12>0):
        raise ValueError('Outside regular physical VI0 eigenframe chart')
    return physical_chart(z,gamma)


def scalar_matter(om,S,N,v,gamma):
    v2=v@v;gp=1+(gamma-1)*v2;gm=1-(gamma-1)*v2
    s2=np.trace(S@S)/6
    qdec=2*s2+.5*((3*gamma-2)+(2-gamma)*v2)*om/gp
    Pi=3*gamma*om/gp*(np.outer(v,v)-v2/3*np.eye(3))
    Q=3*gamma*om/gp*v
    return qdec,Pi,Q,gp,gm


def eigenframe_W(S,N):
    """Unique smooth VI0 principal-frame spin for distinct N eigenvalues.
    W_ij=-(n_i+n_j)/(n_j-n_i)*Sigma_ij .
    """
    nn=np.diag(N)
    W=np.zeros((3,3))
    for i,j in [(0,1),(0,2),(1,2)]:
        gap=nn[j]-nn[i]
        if abs(gap)<1e-12:raise ValueError('Degenerate eigenframe')
        W[i,j]=-(nn[i]+nn[j])*S[i,j]/gap
        W[j,i]=-W[i,j]
    return W


def ambient_rhs(om,S,N,v,gamma, *,wrong_frame=False,drop_torque=False):
    """BASS general.rhs and matter.fluid RHS with explicit covariant rotation.

    qdec = deceleration (NOT N33 or second VI0 curvature).
    No numerical projection of constraints is performed here.
    """
    qdec,Pi,Q,gp,gm=scalar_matter(om,S,N,v,gamma)
    W=eigenframe_W(S,N)
    S3=2*N@N-np.trace(N)*N
    S3-=np.trace(S3)/3*np.eye(3)
    Sd=(qdec-2)*S-S3+Pi+W@S-S@W
    Nd=qdec*N+S@N+N@S+W@N-N@W
    sv2=v@v;svv=v@S@v
    T=((3*gamma-4)*(1-sv2)+(2-gamma)*svv)/gm
    dv=T*v-S@v+(0 if wrong_frame else W@v)
    if not drop_torque:
        dv-=np.einsum('abc,b,c->a',EPS,v,N@v)
    od=(om/gp)*(2*qdec-(3*gamma-2)+(2*qdec*(gamma-1)-(2-gamma))*sv2-gamma*svv)
    return od,Sd,Nd,dv,qdec,W,Pi,Q


def reduced_rhs(time,z,gamma):
    om,S,N,v=checked_chart(z,gamma)
    od,Sd,Nd,vd,*_=ambient_rhs(om,S,N,v,gamma)
    return np.array([-Sd[0,0]/2,(Sd[1,1]-Sd[2,2])/(2*np.sqrt(3)),
                     Nd[1,1],-Nd[2,2],*vd],float)


def residuals(om,S,N,v,gamma):
    _,_,Q,_,_=scalar_matter(om,S,N,v,gamma)
    mom=np.einsum('abc,bd,cd->a',EPS,N,S)
    K=np.trace(N@N)/6-np.trace(N)**2/12
    return np.r_[om+np.trace(S@S)/6+K-1,mom-Q]


def propagation_residual(om,S,N,v,gamma, *,wrong_frame=False,drop_torque=False):
    """Direct Frechet derivative DC dot F against exact constraint ODE."""
    od,Sd,Nd,vd,qdec,W,Pi,Q=ambient_rhs(om,S,N,v,gamma,
                         wrong_frame=wrong_frame,drop_torque=drop_torque)
    _,_,_,gp,_=scalar_matter(om,S,N,v,gamma)
    gp_dot=2*(gamma-1)*(v@vd)
    Qd=3*gamma*((od* v+om*vd)/gp-om*v*gp_dot/gp**2)
    Jd=np.einsum('abc,bd,cd->a',EPS,Nd,S)+np.einsum('abc,bd,cd->a',EPS,N,Sd)
    Kd=np.trace(N@Nd)/3-np.trace(N)*np.trace(Nd)/6
    actual=np.r_[od+np.trace(S@Sd)/3+Kd,Jd-Qd]
    C=residuals(om,S,N,v,gamma)
    expected=np.r_[2*qdec*C[0],((2*qdec-2)*np.eye(3)-S+W)@C[1:]]
    return actual-expected, actual, expected


def chart_tangency(z,gamma):
    """Complex-step DG(z) f7(z) = full source RHS, with no finite-diff cancellation."""
    dz=reduced_rhs(0,z,gamma)
    h=1e-27
    o,S,N,v=physical_chart(np.asarray(z,complex)+1j*h*dz,gamma)
    predicted=np.r_[o.imag/h,S.imag.ravel()/h,N.imag.ravel()/h,v.imag/h]
    om,S0,N0,v0=checked_chart(z,gamma)
    od,Sd,Nd,vd,*_=ambient_rhs(om,S0,N0,v0,gamma)
    actual=np.r_[od,Sd.ravel(),Nd.ravel(),vd]
    return float(np.max(abs(actual-predicted)))


def scalar_projector(v,n=AXES,w=WEIGHTS):
    v=np.asarray(v,float);n=np.asarray(n,float);w=np.asarray(w,float)
    vv=v@v; dots=n@v; q=1-dots
    if not (0<=vv<1 and np.min(q)>0 and np.all(w>0)):
        raise ValueError('Unphysical scalar projector')
    r=(1-vv)**2/q**4
    a=w*q;den=a@r
    return np.outer(r,a)/den


def projector_lift(v,vd,n,nd,w=WEIGHTS):
    """Total Pdot with moving ray labels; screen/polarized physics excluded.

    Scalar r=(1-v²)^2/(1-v.n)^4, a=w(1-v.n).
    n' has PURE rotating-frame contribution W n, plus future physical ray transport.
    """
    v=np.asarray(v,float);vd=np.asarray(vd,float);n=np.asarray(n,float)
    nd=np.asarray(nd,float);w=np.asarray(w,float)
    V2=v@v;qs=1-n@v
    rate_n=nd@v+n@vd
    r=(1-V2)**2/qs**4;a=w*qs;D=a@r
    rd=r*(-4*(v@vd)/(1-V2)+4*rate_n/qs)
    ad=-w*rate_n
    P=np.outer(r,a)/D
    Pd=(np.outer(rd,a)+np.outer(r,ad))/D-P*(ad@r+a@rd)/D
    K=Pd@P-P@Pd
    return P,Pd,K


def symbolic_class_a_certificate():
    """Exact unrestricted class-A geometric momentum and curvature identities.
    No Lie-group VI0 specialization, no numerical rank or sample involved.
    """
    x=sp.symbols('s0:5');y=sp.symbols('n0:6');z=sp.symbols('p0:5')
    w=sp.symbols('w0:3');q=sp.symbols('q_dec')
    S=sp.Matrix([[x[0],x[2],x[3]],[x[2],x[1],x[4]],
                 [x[3],x[4],-x[0]-x[1]]])
    N=sp.Matrix([[y[0],y[3],y[4]],[y[3],y[1],y[5]],
                 [y[4],y[5],y[2]]])
    Pi=sp.Matrix([[z[0],z[2],z[3]],[z[2],z[1],z[4]],
                  [z[3],z[4],-z[0]-z[1]]])
    W=sp.Matrix([[0,w[0],w[1]],[-w[0],0,w[2]],[-w[1],-w[2],0]])
    B=2*N*N-sp.trace(N)*N;S3=B-sp.trace(B)/3*sp.eye(3)
    Sd=(q-2)*S-S3+Pi+W*S-S*W
    Nd=q*N+S*N+N*S+W*N-N*W
    def cross_con(A,B):
        return sp.Matrix([sum(sp.LeviCivita(i,j,k)*A[j,m]*B[k,m]
                              for j in range(3) for k in range(3) for m in range(3))
                          for i in range(3)])
    J=cross_con(N,S)
    Jd=cross_con(Nd,S)+cross_con(N,Sd)
    expect=(2*q-2)*J-S*J+W*J+cross_con(N,Pi)
    moment=[sp.expand(t) for t in Jd-expect]
    K=(sp.trace(N*N)/6-sp.trace(N)**2/12)
    Kd=sp.trace(N*Nd)/3-sp.trace(N)*sp.trace(Nd)/6
    kr=sp.expand(Kd-2*q*K-sp.trace(S*S3)/3)
    g,V2,Svv,T=sp.symbols('gamma V2 Svv T')
    GP=1+(g-1)*V2;GM=1-(g-1)*V2
    TT=((3*g-4)*(1-V2)+(2-g)*Svv)/GM
    A=(3*g-2)+(2-g)*V2
    # For Q=3gamma Omega v/G+, the coefficient of v in Qdot minus (2q-2).
    qratio=sp.factor(-A/GP+TT-2*(g-1)*(TT*V2-Svv)/GP-g*Svv/GP+2)
    if moment!=[0,0,0] or kr!=0 or qratio!=0:
        raise AssertionError({'moment':moment,'curvature':kr,'fluid':qratio})
    return {'class_A_momentum_polynomial_residuals':list(map(int,moment)),
            'class_A_curvature_polynomial_residual':str(kr),
            'gamma_law_Q_evolution_symbolic_residual':str(qratio),
            'gauss_propagation':'C_Gdot=2qdec*C_G',
            'momentum_propagation':'Cdot=[(2qdec-2)I-Sigma+W] C'}


def physical_histories(cases=12,epochs=41,end=.2):
    rng=np.random.default_rng(31120261101)
    rows=[];summary=[]
    for i in range(cases):
        sp0,sm0=rng.uniform(-.11,.11,2)
        p,r=rng.uniform(.3,.62,2)
        v=rng.uniform(-.14,.14,3)
        gamma=(1.0,1.1,1.3333333333333333,1.65)[i%4]
        z0=np.r_[sp0,sm0,p,r,v]
        t=np.linspace(0,end,epochs)
        sol=solve_ivp(lambda t,y: reduced_rhs(t,y,gamma),(0,end),z0,t_eval=t,
                rtol=2e-11,atol=2e-13,method='DOP853')
        if not sol.success:raise RuntimeError(sol.message)
        mxG=mxC=mxF=0.
        for tt,z in zip(sol.t,sol.y.T):
            om,S,N,v=checked_chart(z,gamma)
            C=residuals(om,S,N,v,gamma)
            gap,_,_=propagation_residual(om,S,N,v,gamma)
            tangent=chart_tangency(z,gamma)
            mxG=max(mxG,abs(C[0]));mxC=max(mxC,float(max(abs(C[1:]))))
            mxF=max(mxF,float(max(abs(gap))),tangent)
            qdec,Pi,Q,gp,gm=scalar_matter(om,S,N,v,gamma)
            rows.append([i,gamma,float(tt),*map(float,z),float(om),float(qdec),
                         float(np.linalg.norm(v)),float(C[0]),float(max(abs(C[1:]))),
                         float(max(abs(gap))),float(tangent)])
        summary.append({'case':i,'gamma':gamma,'max_Gauss':mxG,
                        'max_Codazzi':mxC,'max_constraint_propagation_residual':mxF,
                        'endpoint_Omega':float(om),'endpoint_curvature_parameters':list(map(float,z[2:4])),
                        'endpoint_tilt':list(map(float,v))})
    return rows,summary


def run(save:Path=HERE/'data'):
    save=Path(save);save.mkdir(parents=True,exist_ok=True)
    formal=symbolic_class_a_certificate()
    trajectories,summaries=physical_histories()
    # An exact VI0 state generates gauge W and nonzero apparent Pdot if grid is frozen.
    om,S,N,v=checked_chart([.09,-.03,.55,.36,.12,-.10,.07],4/3)
    W=eigenframe_W(S,N)
    vd=W@v;nd=AXES@W.T
    P,PD,K=projector_lift(v,vd,AXES,nd)
    _,bad_pd,_=projector_lift(v,vd,AXES,np.zeros_like(AXES))
    pure_gauge=float(np.max(np.abs(PD)));bad_gauge=float(np.max(np.abs(bad_pd)))
    if pure_gauge>5e-15 or bad_gauge<1e-4:
        raise AssertionError({'gauge_correct':pure_gauge,'wrong_grid':bad_gauge})
    head=['case','gamma','u','Sigma_plus','Sigma_minus','N22','minus_N33','v1','v2','v3',
          'Omega','q_deceleration','tilt_magnitude','Gauss','max_abs_Codazzi',
          'propagation_max_defect','chart_tangency_max_defect']
    with (save/'VI0_DYNAMIC_PHYSICAL_HISTORIES.csv').open('w',newline='') as f:
        ww=csv.writer(f);ww.writerow(head);ww.writerows(trajectories)
    payload={
        'schema':'bass.vi0_eigenframe_constraint_propagation_and_gauge_lift.v1',
        'parent_PR':PARENT_PR,'immutable_parent_head':PARENT_HEAD,
        'original_main_head':ORIGINAL_MAIN,'original_git_blob_sha1':ORIGINAL_BLOBS,
        'science':'VI0 full gamma-law class-A constraints propagated by source-owned geometric and fluid RHS; pure eigenframe rotation cancels from co-rotated scalar angular projector',
        'formal_exact':formal,'VII0_boundary': 'NOT_CLAIMED',
        'physical_trajectory_count':len(summaries),'time_sampled_physical_states':len(trajectories),
        'max_Gauss':max(x['max_Gauss'] for x in summaries),
        'max_Codazzi':max(x['max_Codazzi'] for x in summaries),
        'max_direct_derivative_and_chart_error':max(x['max_constraint_propagation_residual'] for x in summaries),
        'co_rotated_pure_W_projector_rate_max':float(pure_gauge),
        'wrong_static_angular_grid_spurious_projector_rate_max':float(bad_gauge),
        'owner_status':'SCOPED_CONSTRAINT_PROPAGATION_AND_KATO_FRAME_LIFT_DERIVED_AND_NUMERICALLY_CHECKED',
        'G_DYN_MANIFOLD_VI0_FULL':'PARTIAL',
        'P_MIG_II_PREFLIGHT':'OPEN',
        'JOIN_J1':'HOLD','upper_BASS_DAG_scoped_source_mapped':'9/15',
        'new_fully_completed_upper_nodes':0,
        'new_production_ready_nodes':0,
        'not_derived':['general_physical_angular_Liouville_nprime','polarized_P8_screen',
                       'all_VI0_degenerate_gauge_branches','nonprincipal_full_transport',
                       'VI0_original_production_Rust','P_MIG_II_PREFLIGHT'],
        'native_subagent':'NOT_RUN','distinct_author_validation':'NOT_RUN',
        'production_ready':False,'merge_ready':False,'auto_next':False,
    }
    (save/'VI0_DYNAMIC_RESULTS.json').write_text(json.dumps(payload,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
    print('VI0_REAL_DYNAMICS',json.dumps({k:payload[k] for k in [
          'physical_trajectory_count','time_sampled_physical_states',
          'max_Gauss','max_Codazzi','max_direct_derivative_and_chart_error',
          'co_rotated_pure_W_projector_rate_max','wrong_static_angular_grid_spurious_projector_rate_max']},indent=2))
    return payload


if __name__=='__main__':run()

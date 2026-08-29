"""Test-only dense reference for the existing scalar fixed-node AEM2 donor.

No bianchi/native/generated runtime imports.  This independently constructs
quadrature matrices and uses SciPy dense expm, not production Arnoldi/Krylov.
It does NOT implement angular advection, polarized trajectories, or a new
physical Kato source.  The source donor subtracts K in the middle stage.

Conventions: (-,+,+,+), e = future photon propagation, beta = v_e/c, axis=1
for the aligned Type-II lane.  State[4] is beta's second spatial component,
not beta squared.  tau and optical depth are dimensionless; no c=1 assumption.
Reference cost: O(K M^3) time, O(M^2) workspace plus O(K M) history.
"""
from __future__ import annotations
import itertools
import numpy as np
from scipy.linalg import expm

PI = np.pi


def lebedev26() -> tuple[np.ndarray, np.ndarray]:
    """Same established quadrature, independently ordered in explicit loops."""
    nodes, weights = [], []
    for axis in range(3):
        for sign in (-1., 1.):
            n=np.zeros(3);n[axis]=sign;nodes.append(n);weights.append(4*PI/21)
    for zero_axis in range(3):
        axes=[i for i in range(3) if i!=zero_axis]
        for s,t in itertools.product((-1.,1.),repeat=2):
            n=np.zeros(3);n[axes]=np.array([s,t])/np.sqrt(2.)
            nodes.append(n);weights.append(16*PI/105)
    for signs in itertools.product((-1.,1.),repeat=3):
        nodes.append(np.array(signs)/np.sqrt(3.));weights.append(9*PI/70)
    return np.asarray(nodes), np.asarray(weights)


def _grid(e, w, velocity=0.0, axis=1):
    e=np.asarray(e,dtype=float);w=np.asarray(w,dtype=float)
    if e.ndim!=2 or e.shape[1]!=3 or w.shape!=(len(e),) or len(e)==0:
        raise ValueError('grid shape mismatch')
    if not np.isfinite(e).all() or not np.isfinite(w).all() or np.any(w<=0):
        raise ValueError('nonfinite or nonpositive grid data')
    if not np.all(np.abs(np.linalg.norm(e,axis=1)-1)<1e-10):
        raise ValueError('directions must be unit vectors')
    if isinstance(axis,(bool,np.bool_)) or not isinstance(axis,(int,np.integer)) or axis not in (0,1,2):
        raise ValueError('axis must be an integer 0, 1 or 2')
    if not np.isfinite(velocity) or abs(np.real(velocity))>=1:
        raise ValueError('velocity must have absolute real part below one')
    return e,w


def boost(e, velocity, axis=1):
    """Lorentz 4-vector boost; beta is dimensionless and e points with p."""
    e=np.asarray(e,dtype=float)
    _grid(e,np.ones(len(e)),velocity,axis)
    g=1/np.sqrt(1-velocity*velocity)
    energy=g*(1-velocity*e[:,axis])
    momentum=e.copy();momentum[:,axis]=g*(e[:,axis]-velocity)
    return momentum/energy[:,None],energy


def paired_grid(rest_e, rest_w, velocity, axis=1):
    rest_e,rest_w=_grid(rest_e,rest_w,velocity,axis)
    normal_e,_=boost(rest_e,-velocity,axis)
    _,D=boost(normal_e,velocity,axis)
    return normal_e,rest_w*D**2


def scalar_collision(e,w,velocity,axis=1):
    """Dense raw Thomson generator with direction-dependent normal-frame rate."""
    e,w=_grid(e,w,velocity,axis)
    ep,D=boost(e,float(velocity),axis)
    cosines=ep@ep.T
    gain=3/(16*PI)*(1+cosines*cosines)*(w/D**2)[None,:]
    rest=gain-np.eye(len(e))
    rate=1-velocity*e[:,axis]
    return (rate/D**4)[:,None]*rest*(D**4)[None,:]


def projector(e,w,velocity,axis=1):
    """Rank-one equilibrium projector; accepts complex v for reference AD."""
    e,w=_grid(e,w,velocity,axis)
    rate=1-velocity*e[:,axis]
    D=rate/np.sqrt(1-velocity*velocity)
    right=D**-4
    left=w*rate/(4*PI)
    denominator=left@right
    if not np.isfinite(denominator) or abs(denominator)==0:
        raise ValueError('singular equilibrium pairing')
    return np.outer(right,left)/denominator,right,left


def kato(e,w,velocity,velocity_derivative,axis=1):
    """Complex-step dP/dv and commutator, not a production derivative copy."""
    if not np.isfinite(velocity_derivative): raise ValueError('nonfinite velocity derivative')
    P=projector(e,w,velocity,axis)[0]
    derivative=projector(e,w,velocity+1e-30j,axis)[0].imag/1e-30
    Pdot=velocity_derivative*derivative
    return Pdot@P-P@Pdot


def tilt_rate(state,gamma):
    """Simplified algebraic form of rhs(state,gamma)[4], not a new EOS law."""
    s=np.asarray(state,dtype=float)
    if s.shape!=(5,) or not np.isfinite(s).all() or not np.isfinite(gamma):
        raise ValueError('invalid Type-II background')
    beta=s[4];den=1-(gamma-1)*beta*beta
    if abs(beta)>=1 or den<=0: raise ValueError('invalid tilt denominator')
    return beta*(1-beta*beta)*(3*gamma-4-s[0]-np.sqrt(3)*s[1])/den


def scalar_transport(e,state):
    """Exactly the donor's diagonal bolometric action, NOT full Liouville."""
    e=np.asarray(e,dtype=float);s=np.asarray(state,dtype=float)
    if s.shape!=(5,) or not np.isfinite(s).all(): raise ValueError('background shape')
    root3=np.sqrt(3.)
    shear=np.array([[-2*s[0],0,root3*s[2]],
                    [0,s[0]+root3*s[1],0],
                    [root3*s[2],0,s[0]-root3*s[1]]])
    return np.diag(-4*(1+np.einsum('ni,ij,nj->n',e,shear,e)))


def phi1_action(matrix,vector,h):
    """phi_1(hA)b via a block exponential; no inverse of singular A."""
    A=np.asarray(matrix,dtype=float);b=np.asarray(vector,dtype=float)
    n=len(b)
    if A.shape!=(n,n) or not np.isfinite(A).all() or not np.isfinite(b).all() or not np.isfinite(h):
        raise ValueError('invalid phi1 arguments')
    if h==0:return b.copy()
    aug=np.zeros((n+1,n+1));aug[:n,:n]=h*A;aug[:n,n]=b
    return expm(aug)[:n,n]


def scalar_step(e,w,q1,mid,q3,opacity,h,gamma,opacity_scale,y,axis=1):
    """Dense evaluation of typeii_runtime::kato_aem2_step, fixed_grid_raw only."""
    q1,mid,q3=[np.asarray(s,dtype=float) for s in (q1,mid,q3)]
    if any(s.shape!=(5,) or not np.isfinite(s).all() for s in (q1,mid,q3)):
        raise ValueError('invalid background samples')
    e,w=_grid(e,w,mid[4],axis);y=np.asarray(y,dtype=float)
    if y.shape!=(len(e),) or not np.isfinite(y).all():raise ValueError('state shape')
    if not np.isfinite([opacity,h,opacity_scale]).all() or h<=0 or opacity<0 or opacity_scale<0:
        raise ValueError('invalid step or opacity')
    K1=kato(e,w,q1[4],tilt_rate(q1,gamma),axis)
    Km=kato(e,w,mid[4],tilt_rate(mid,gamma),axis)
    K3=kato(e,w,q3[4],tilt_rate(q3,gamma),axis)
    ym=expm(0.5*h*K1)@y
    Aeff=scalar_transport(e,mid)-Km
    C=opacity_scale*opacity*scalar_collision(e,w,mid[4],axis)
    half=expm(0.5*h*C)@ym
    midpoint=half+0.5*h*phi1_action(C,Aeff@half,0.5*h)
    middle=expm(h*C)@ym+h*phi1_action(C,Aeff@midpoint,h)
    return expm(0.5*h*K3)@middle


def scalar_history(initial,e,w,q1,mid,q3,opacity,step_size,gamma,opacity_scale,axis=1):
    """Row 0 input, then accepted scalar reference states on fixed input nodes."""
    e,w=_grid(e,w,0,axis)
    q1,mid,q3=[np.asarray(s,dtype=float) for s in (q1,mid,q3)]
    h=np.asarray(step_size,dtype=float);op=np.asarray(opacity,dtype=float)
    if h.ndim!=1: raise ValueError('step_size must be one-dimensional')
    count=len(h)
    if count<1 or any(s.shape!=(count,5) for s in (q1,mid,q3)) or op.shape!=(count,):
        raise ValueError('trajectory plan shape mismatch')
    initial=np.asarray(initial,dtype=float)
    if initial.shape!=(len(e),) or not np.isfinite(initial).all():
        raise ValueError('initial state must be a finite node vector')
    history=np.empty((count+1,len(e)));history[0]=initial
    for k in range(count):
        history[k+1]=scalar_step(e,w,q1[k],mid[k],q3[k],op[k],h[k],gamma,opacity_scale,history[k],axis)
    return history


def scalar_diagnostics(e,w,mid,history,axis=1):
    """State-derived raw-slice diagnostics; no assumed exact finite-grid null.

    left_invariant_drift is measured across the FULL step with the same
    midpoint left covector on both endpoints. It includes physical transport
    and is not claimed to vanish. right/equilibrium residuals are aliases.
    """
    e,w=_grid(e,w,0,axis);history=np.asarray(history,dtype=float)
    mid=np.asarray(mid,dtype=float)
    if mid.ndim!=2 or mid.shape[1]!=5 or history.shape!=(len(mid)+1,len(e)):
        raise ValueError('diagnostic history shape mismatch')
    right=[];drift=[];idempotence=[]
    for k,background in enumerate(mid):
        C=scalar_collision(e,w,background[4],axis)
        P,r,left=projector(e,w,background[4],axis)
        right.append(float(np.max(np.abs(C@r))/np.max(np.abs(r))))
        before,after=history[k:k+2]
        scale=max(float(np.max(np.abs(before))),float(np.max(np.abs(after))))
        drift.append(0.0 if scale==0 else float(abs(left@((after-before)/scale))/np.sum(np.abs(left))))
        idempotence.append(float(np.max(np.abs(P@P-P))))
    return {
        'equilibrium_null_residual':np.array(right),
        'right_kernel_residual':np.array(right),
        'left_invariant_drift':np.array(drift),
        'projector_idempotence_residual':np.array(idempotence),
        'positivity_margin':np.min(history,axis=1),
    }


def pack9(matrix):
    m=np.asarray(matrix,dtype=float)
    if m.ndim!=3 or m.shape[1:]!=(3,3):raise ValueError('matrix shape')
    s=(m+np.swapaxes(m,1,2))/2;a=(m-np.swapaxes(m,1,2))/2
    return np.column_stack([s[:,0,0],s[:,1,1],s[:,2,2],s[:,0,1],s[:,0,2],s[:,1,2],a[:,1,2],a[:,2,0],a[:,0,1]])


def unpack9(packed):
    p=np.asarray(packed,dtype=float)
    if p.ndim!=2 or p.shape[1]!=9:raise ValueError('packed shape')
    m=np.zeros((len(p),3,3));m[:,0,0]=p[:,0];m[:,1,1]=p[:,1];m[:,2,2]=p[:,2]
    m[:,0,1]=p[:,3]+p[:,8];m[:,1,0]=p[:,3]-p[:,8]
    m[:,0,2]=p[:,4]-p[:,7];m[:,2,0]=p[:,4]+p[:,7]
    m[:,1,2]=p[:,5]+p[:,6];m[:,2,1]=p[:,5]-p[:,6]
    return m


def polarized_rest_action(e,w,packed,*,gain_multiplier=1.0):
    """Direct O(M^2) common-screen Thomson quadrature at beta=0; no eigenvalues."""
    e,w=_grid(e,w);j=unpack9(packed)
    if len(j)!=len(e) or not np.isfinite(j).all():raise ValueError('coherency shape')
    result=np.empty_like(j)
    for i,direction in enumerate(e):
        P=np.eye(3)-np.outer(direction,direction)
        projected=np.einsum('ab,nbc,cd->nad',P,j,P)
        gain=np.einsum('n,nab->ab',w,projected)*3/(8*PI)
        result[i]=gain_multiplier*gain-j[i]
    return pack9(result)


def polarized_fixture(e):
    e=np.asarray(e,dtype=float);rows=[]
    for n in e:
        seed=np.eye(3)[np.argmin(np.abs(n))];u=seed-(seed@n)*n;u/=np.linalg.norm(u);v=np.cross(n,u)
        I=1+0.12*n[0]-0.07*n[1]*n[2]
        Q=0.18*I*(n[0]**2-n[1]**2);U=0.24*I*n[0]*n[1];V=0.08*I*n[2]
        rows.append(0.5*(I*(np.outer(u,u)+np.outer(v,v))+Q*(np.outer(u,u)-np.outer(v,v))+U*(np.outer(u,v)+np.outer(v,u))-V*(np.outer(u,v)-np.outer(v,u))))
    return pack9(np.asarray(rows))


def normalized_metrics(e,packed):
    """Independent complex-Hermitian eigvalsh and trace-normalized screen test."""
    e=np.asarray(e,dtype=float);m=unpack9(packed)
    e,_=_grid(e,np.ones(len(e)))
    if len(e)!=len(m) or not np.isfinite(m).all():raise ValueError('invalid coherency data')
    minimum=[];leak=[]
    for n,raw in zip(e,m):
        magnitude=np.max(np.abs(raw))
        if magnitude==0:minimum.append(0.0);leak.append(0.0);continue
        scaled=raw/magnitude;I=np.trace(scaled)
        if I<=0: raise ValueError('nonpositive nonzero coherency trace')
        scaled=scaled/I
        S=(scaled+scaled.T)/2;A=(scaled-scaled.T)/2
        H=S+1j*A
        P=np.eye(3)-np.outer(n,n)
        seed=np.eye(3)[np.argmin(np.abs(n))]
        u=seed-(seed@n)*n;u/=np.linalg.norm(u)
        screen=np.column_stack([u,np.cross(n,u)])
        minimum.append(float(np.linalg.eigvalsh(screen.T@H@screen)[0]))
        leak.append(float(np.max(np.abs(scaled-P@scaled@P))))
    return {'minimum_eigenvalue':np.array(minimum),'screen_leakage':np.array(leak)}


def background_fixture(steps=2):
    i=np.arange(steps,dtype=float)
    q1=np.column_stack([0.25+0.004*i,0.05-0.003*i,1/30+0.002*i,0.8-0.01*i,0.08+0.006*i])
    mid=q1+np.array([0.003,-0.002,0.0015,-0.006,0.0025])
    q3=q1+np.array([0.007,-0.004,0.0035,-0.013,0.0055])
    return q1,mid,q3,0.18+0.015*i,8e-4+1e-4*i

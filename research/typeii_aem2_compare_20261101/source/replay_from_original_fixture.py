"""Independent hosted source-bound Type-II original old AEM2 versus Kato replay.

This hosted implementation reads the ORIGINAL checked-in Type-II 401-state
fixture rather than repeating the local RK4 generator; represents the original
finite-tilt scalar collision and the exact Rust AEM2 stage sequence.
Not native Saha, not polarized P8, not a production runtime.
"""
import csv,hashlib,json,math
from pathlib import Path
import numpy as np
from scipy.linalg import expm
from scipy.interpolate import CubicSpline
from scipy.integrate import solve_ivp

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
FIX=REPO/"compiler/validation/typeii_fixture_canonical.json"
AUTH=REPO/"compiler/validation/typeii_fixture_authority.json"
BLOBS={
"compiler/validation/typeii_fixture_canonical.json":"dea22f0fce116b61314b13cea7d0bdd38efe48bc",
"compiler/validation/typeii_fixture_authority.json":"b71372faa7dde85e928802c08c831299ebe99bcd",
"runtime/rust/typeii/typeii_runtime.rs":"71b8a11ea998e91a4be7f95875eca31442e831dc",
"generated/rust/typeii/typeii_collision.rs":"c85616da3a8ce437b59aa8c1ce5adc17904ca50d",
"generated/rust/typeii/typeii_kato.rs":"9c8d49b6d42daf28734b4d439ca50f6535ee3519"}
PI=math.pi;SQ3=math.sqrt(3)

def source_lock():
    for name,sha in BLOBS.items():
        b=(REPO/name).read_bytes()
        got=hashlib.sha1(b"blob "+str(len(b)).encode()+b"\x00"+b).hexdigest()
        if got!=sha:raise RuntimeError(f"ORIGINAL_SOURCE_DRIFT {name}: {got}")
    return len(BLOBS)

class Owner:
    def __init__(self):
        doc=json.loads(FIX.read_text())
        src=json.loads(AUTH.read_text())
        samples=doc["trajectory"]["samples"]
        if len(samples)!=401 or doc["trajectory"]["contract"]["gamma"]!=1.3:
            raise RuntimeError("ORIGINAL_TYPEII_TRAJECTORY_CONTRACT_CHANGED")
        t=np.array([q["tau"] for q in samples])
        self.t=t;self.trajectory=CubicSpline(t,np.array([q["state"] for q in samples]),axis=0)
        self.nu=np.polynomial.Polynomial.fit(
            np.array([x[0] for x in src["opacity_model"]["anchors"]]),
            np.log([x[1] for x in src["opacity_model"]["anchors"]]),2).convert()
        self.samples=samples
    def state(self,t):return np.asarray(self.trajectory(t),float)
    def rate(self,t):return float(np.exp(self.nu(t)))

def grid(name):
    if name=="axis6":
        return np.array([[1.,0,0],[-1.,0,0],[0,1.,0],[0,-1.,0],[0,0,1.],[0,0,-1.]]),np.full(6,4*PI/6)
    a=1/np.sqrt(3);b=1/np.sqrt(2);e=[];w=[]
    for k in range(3):
        for s in (-1.,1.):
            q=np.zeros(3);q[k]=s;e.append(q);w.append(4*PI/21)
    for k in range(3):
        ab=[i for i in range(3) if i!=k]
        for j in (-1.,1.):
            for z in (-1.,1.):
                q=np.zeros(3);q[ab[0]]=j*b;q[ab[1]]=z*b;e.append(q);w.append(16*PI/105)
    for j in (-1.,1.):
        for k in (-1.,1.):
            for z in (-1.,1.):e.append([j*a,k*a,z*a]);w.append(9*PI/70)
    return np.array(e),np.array(w)

def bg_rhs(y):
    sp,sm,s13,n,v=y;g=1.3
    s2=sp**2+sm**2+s13**2;om=1-s2-n**2/12
    gp=1+(g-1)*v*v;gm=1-(g-1)*v*v
    sig=sp+SQ3*sm
    q=2*s2+.5*((3*g-2)+(2-g)*v*v)*om/gp
    T=((3*g-4)*(1-v*v)+(2-g)*sig*v*v)/gm
    return np.array([-(2-q)*sp+n*n/3+g*om*v*v/(2*gp)-3*s13*s13,
       -(2-q)*sm+SQ3*g*om*v*v/(2*gp)+SQ3*s13*s13,
       s13*(-(2-q)+3*sp-SQ3*sm),(q-4*sp)*n,v*(T-sig)])

def boost(e,v):
    gam=1/np.sqrt(1-v*v);mu=e[:,1]
    D=gam*(1-v*mu)
    coeff=(gam*gam/(gam+1))*(v*mu)-gam
    x=np.asarray(e).astype(np.result_type(e,v,1.0)).copy()
    x[:,1]+=coeff*v
    return x/D[:,None],D

def cp(e,w,v,mode):
    if mode=="paired":
        n,_=boost(e,-v);_,d=boost(n,v);wn=w*d**2
    else:n=e.copy();wn=w.copy()
    er,D=boost(n,v)
    q=1-v*n[:,1]
    wr=wn/D**2
    gain=3/(16*PI)*(1+(er@er.T)**2)*wr[None,:]
    C=(q*D**-4)[:,None]*(gain-np.eye(len(n)))*D[None,:]**4
    r=D**-4;a=wn*q/(4*PI);den=a@r
    P=np.outer(r,a)/den
    return C,P,n,wn,r,a

def pv(e,w,v,mode):
    if mode=="paired":return cp(e,w,v+1e-26j,mode)[1].imag/1e-26
    C,P,n,wn,r,a=cp(e,w,v,mode)
    mu=n[:,1];q=1-v*mu
    dr=4*r*(mu/q-v/(1-v*v))
    da=-wn*mu/(4*PI);den=a@r
    return (np.outer(dr,a)+np.outer(r,da))/den-P*(da@r+a@dr)/den

def operator(owner,e,w,t,mode,alpha):
    s=owner.state(t);v=s[4]
    C,P,n,wn,r,a=cp(e,w,v,mode)
    pv0=pv(e,w,v,mode)
    dP=bg_rhs(s)[4]*pv0;K=dP@P-P@dP
    sp,sm,s13=s[:3]
    see=(-2*sp*n[:,0]**2+(sp+SQ3*sm)*n[:,1]**2+
         (sp-SQ3*sm)*n[:,2]**2+2*SQ3*s13*n[:,0]*n[:,2])
    A=np.diag(-4*(1+see))
    return alpha*owner.rate(t)*C,A,K,P

def integ_phi(C,h):
    n=C.shape[0];B=np.zeros((2*n,2*n));B[:n,:n]=h*C;B[:n,n:]=np.eye(n)
    return h*expm(B)[:n,n:]

def initial(owner,e,w,mode):
    _,_,_,P=operator(owner,e,w,0,mode,1)
    z=np.random.default_rng(20261101).random(len(e))
    return P@(1+.2*z)

def step(owner,e,w,t,h,y,mode,alpha,method):
    C,A,K,P=operator(owner,e,w,t+h/2,mode,alpha)
    if method=="old":ym=y;F=A
    else:
        ym=expm(.5*h*operator(owner,e,w,t+h/4,mode,alpha)[2])@y
        F=A-K
    half=expm(.5*h*C)@ym
    mid=half+integ_phi(C,.5*h)@(F@half)
    z=expm(h*C)@ym+integ_phi(C,h)@(F@mid)
    if method=="kato":
        z=expm(.5*h*operator(owner,e,w,t+3*h/4,mode,alpha)[2])@z
    return z

def run():
    n_locked=source_lock();owner=Owner()
    rows=[]
    for gridname in ("axis6","lebedev26"):
        e,w=grid(gridname)
        for mode in ("fixed","paired"):
            for alpha in (1,1000,100000):
                y0=initial(owner,e,w,mode)
                def rhs(t,y):
                    C,A,K,P=operator(owner,e,w,t,mode,alpha)
                    return (C+A)@y
                gold=solve_ivp(rhs,(0,.2),y0,method="Radau",rtol=1e-9,atol=2e-11)
                if not gold.success:raise RuntimeError(gold.message)
                reference=gold.y[:,-1];Pfinal=operator(owner,e,w,.2,mode,alpha)[3]
                for scheme in ("old","kato"):
                    old_error=None
                    for ns in (4,8,16,32):
                        h=.2/ns;y=y0.copy()
                        for k in range(ns):y=step(owner,e,w,k*h,h,y,mode,alpha,scheme)
                        err=np.linalg.norm(y-reference)/np.linalg.norm(reference)
                        defect=np.linalg.norm((np.eye(len(e))-Pfinal)@y)/np.linalg.norm(y)
                        order=None if old_error is None else math.log(old_error/err,2)
                        rows.append(dict(grid=gridname,mode=mode,alpha=alpha,N=ns,
                            method=scheme,relative_error=float(err),endpoint_defect=float(defect),local_order=order))
                        old_error=err
    return dict(schema="bass.typeii.source_recorded_independent_aem2_ci.v1",
      main="9c6506e4e2087129a8b674ff10438e5db1a55c9d",
      original_source_hash_count=n_locked,
      original_fixture_sample_count=len(owner.samples),
      original_fixture_source="original checked-in Type-II 401 state JSON, not an inferred synthetic background",
      opacity_source="receipt-constrained three-anchor log-quadratic proxy, NOT native SahaHistory",
      records=rows,upper_dag="9/15_SCOPED_SOURCE_MAPPED",
      join_J1="0/2_FULL_PASS_HOLD",stageII="11/11_HISTORICAL_NOT_CANONICAL",
      production_ready=False)

def main():
    o=run();out=HERE.parent/"ci_generated";out.mkdir(exist_ok=True)
    (out/"ORIGINAL_TYPEII_AEM2_REPLAY.json").write_text(json.dumps(o,indent=2)+"\n")
    with (out/"ORIGINAL_TYPEII_AEM2_REPLAY.csv").open("w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=list(o["records"][0]));writer.writeheader();writer.writerows(o["records"])
    for alpha in (1000,100000):
        seq=[z for z in o["records"] if z["grid"]=="lebedev26" and z["mode"]=="paired" and z["alpha"]==alpha and z["N"]==32]
        print("ORIGINAL_PAIRED_26",alpha,[(z["method"],z["relative_error"],z["local_order"],z["endpoint_defect"]) for z in seq])
    print("SOURCE_BLOBS",o["original_source_hash_count"],"PASS", "COMPARISON_ROWS",len(o["records"]))
if __name__=="__main__":main()

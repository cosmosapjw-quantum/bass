from __future__ import annotations
import numpy as np
from scipy.linalg import expm
from scipy.interpolate import CubicSpline
from pathlib import Path
import json
PI=np.pi

def proj(e):
    e=np.asarray(e,float); return np.eye(3)[None]-np.einsum('ai,aj->aij',e,e)

def pack9(J):
    J=np.asarray(J,float); S=.5*(J+J.swapaxes(1,2)); A=.5*(J-J.swapaxes(1,2))
    return np.stack([S[:,0,0],S[:,1,1],S[:,2,2],S[:,0,1],S[:,0,2],S[:,1,2],A[:,1,2],A[:,2,0],A[:,0,1]],1)

def unpack9(y):
    y=np.asarray(y,float).reshape(-1,9); J=np.zeros((len(y),3,3))
    J[:,0,0]=y[:,0];J[:,1,1]=y[:,1];J[:,2,2]=y[:,2]
    J[:,0,1]=y[:,3]+y[:,8];J[:,1,0]=y[:,3]-y[:,8]
    J[:,0,2]=y[:,4]-y[:,7];J[:,2,0]=y[:,4]+y[:,7]
    J[:,1,2]=y[:,5]+y[:,6];J[:,2,1]=y[:,5]-y[:,6]
    return J

def aberrate(e,v,axis=1):
    e=np.atleast_2d(np.asarray(e,float)); vv=np.zeros(3);vv[axis]=v
    if abs(v)<1e-15:return e.copy(),np.ones(len(e))
    g=1/np.sqrt(1-v*v);ve=e@vv;D=g*(1-ve)
    ep=(e+(((g-1)*ve/(v*v)-g)[:,None])*vv[None])/D[:,None]
    ep/=np.linalg.norm(ep,axis=1)[:,None]
    return ep,D

def screen_map(e,v,axis=1):
    e=np.atleast_2d(np.asarray(e,float));P=proj(e)
    if abs(v)<1e-15:return P,e.copy(),np.ones(len(e))
    vv=np.zeros(3);vv[axis]=v;g=1/np.sqrt(1-v*v);ep,D=aberrate(e,v,axis)
    Pv=np.einsum('aij,j->ai',P,vv); W0=-g*Pv
    Wsp=P+((g-1)/(v*v))*np.einsum('i,ak->aik',vv,Pv)
    pp=ep*D[:,None]
    S=Wsp-np.einsum('ak,ai->aik',W0/D[:,None],pp)
    return S,ep,D

def paired_from_rest(er,wr,v,axis=1):
    en,_=aberrate(er,-v,axis); er2,D=aberrate(en,v,axis)
    assert np.max(abs(er2-er))<3e-14
    return en,wr*D**2

def equilibrium(e,v,axis=1):
    _,D=aberrate(e,v,axis); return pack9(.5*D[:,None,None]**-4*proj(e)).ravel()

def collision(e,w,v,axis,y):
    e=np.asarray(e,float);w=np.asarray(w,float);J=unpack9(y)
    S,ep,D=screen_map(e,v,axis); Jr=D[:,None,None]**4*np.einsum('aik,akl,ajl->aij',S,J,S)
    wr=w/D**2;M=np.einsum('a,aij->ij',wr,Jr);Pr=proj(ep)
    gain=(3/(8*PI))*np.einsum('aik,kl,alj->aij',Pr,M,Pr); Cr=gain-Jr
    Cn=(1-v*e[:,axis])[:,None,None]*D[:,None,None]**-4*np.einsum('aki,akl,alj->aij',S,Cr,S)
    return pack9(Cn).ravel()

def scalar_collision(e,w,v,axis,I):
    ep,D=aberrate(e,v,axis);wr=w/D**2;gp=D**4*np.asarray(I);M=np.einsum('a,ai,aj->ij',wr*gp,ep,ep);i0=np.sum(wr*gp)
    gain=(3/(16*PI))*(i0+np.einsum('ai,ij,aj->a',ep,M,ep))
    return (1-v*np.asarray(e)[:,axis])*D**-4*(gain-gp)

def left(e,w,v,axis,y):
    J=unpack9(y); return np.sum(w*(1-v*e[:,axis])*np.trace(J,axis1=1,axis2=2))/(4*PI)

def projector(e,w,v,axis,y):
    r=equilibrium(e,v,axis); return r*left(e,w,v,axis,y)/left(e,w,v,axis,r)

def projector_dv(e,w,v,axis,y):
    r=equilibrium(e,v,axis);g=1/np.sqrt(1-v*v);mu=e[:,axis];fac=4*(mu/(1-v*mu)-g*g*v)
    rv=(pack9(unpack9(r)*fac[:,None,None])).ravel()
    def lv(z):
        J=unpack9(z);return np.sum(-w*mu*np.trace(J,axis1=1,axis2=2))/(4*PI)
    den=left(e,w,v,axis,r);denv=lv(r)+left(e,w,v,axis,rv);s=left(e,w,v,axis,y);sv=lv(y)
    return rv*s/den+r*sv/den-r*s*denv/(den*den)

def kato(e,w,v,vd,axis,y):
    py=projector(e,w,v,axis,y);return vd*(projector_dv(e,w,v,axis,py)-projector(e,w,v,axis,projector_dv(e,w,v,axis,y)))

def matrix_of(apply,n):
    eye=np.eye(n);return np.column_stack([apply(eye[:,j]) for j in range(n)])

def grid6():
    e=np.array([[1,0,0],[-1,0,0],[0,1,0],[0,-1,0],[0,0,1],[0,0,-1]],float);return e,np.full(6,4*PI/6)

def metrics():
    er,wr=grid6(); v=.1; en,wn=paired_from_rest(er,wr,v)
    r=equilibrium(en,v,1); cr=collision(en,wn,v,1,r)
    fixed=collision(er,wr,v,1,equilibrium(er,v,1))
    rng=np.random.default_rng(4); y=rng.normal(size=9*len(en)); c=collision(en,wn,v,1,y)
    # V=0: symmetric screen input remains symmetric under generator
    J=np.einsum('aik,akl,alj->aij',proj(en),rng.normal(size=(len(en),3,3)),proj(en));J=.5*(J+J.swapaxes(1,2));cs=unpack9(collision(en,wn,v,1,pack9(J).ravel()))
    vgen=np.max(abs(cs-cs.swapaxes(1,2)))
    # I trace reduction at generator level
    I=1+.3*en[:,2]**2; Ju=.5*I[:,None,None]*proj(en); cp=unpack9(collision(en,wn,v,1,pack9(Ju).ravel())); sc=scalar_collision(en,wn,v,1,I)
    itr=np.max(abs(np.trace(cp,axis1=1,axis2=2)-sc))
    # I-E feedback appears at second order
    Cpol=matrix_of(lambda z: collision(en,wn,v,1,z),9*len(en)); Csc=matrix_of(lambda z: scalar_collision(en,wn,v,1,z),len(en)); x=.15
    Ip=np.trace(unpack9(expm(x*Cpol)@pack9(Ju).ravel()),axis1=1,axis2=2); Is=expm(x*Csc)@I
    feedback=np.max(abs(Ip-Is));
    # projector identities
    py=projector(en,wn,v,1,y);pp=projector(en,wn,v,1,py);pd=projector_dv(en,wn,v,1,y);K=kato(en,wn,v,.03,1,y);kpy=kato(en,wn,v,.03,1,py);pky=projector(en,wn,v,1,K)
    comm=np.max(abs(kpy-pky-.03*pd))
    return dict(paired_null=np.max(abs(cr)),fixed_null=np.max(abs(fixed)),left=abs(left(en,wn,v,1,c)),V_generated=vgen,I_generator_reduction=itr,I_E_feedback=feedback,P2=np.max(abs(pp-py)),K_comm=comm,
                gold=collision(en,wn,v,1,np.arange(9*len(en),dtype=float)/17-1)[:18].tolist())
def tangent_basis(e):
    e=np.asarray(e,float); k=int(np.argmin(np.abs(e))); a=np.zeros(3);a[k]=1.;u=a-(a@e)*e;u/=np.linalg.norm(u);v=np.cross(e,u);return u,v

def physical_random_state(e,seed=11):
    rng=np.random.default_rng(seed);J=[]
    for ei in e:
        u,v=tangent_basis(ei);B=rng.normal(size=(2,2))+1j*rng.normal(size=(2,2));H=B@B.conj().T
        s=H[0,0].real*np.outer(u,u)+H[1,1].real*np.outer(v,v)+H[0,1].real*(np.outer(u,v)+np.outer(v,u))
        a=H[0,1].imag*(np.outer(u,v)-np.outer(v,u));J.append(s+a)
    return pack9(np.asarray(J)).ravel()

def cone_min_eig(e,y):
    J=unpack9(y);mn=np.inf; leak=0.
    for ei,ji in zip(e,J):
        u,v=tangent_basis(ei);S=.5*(ji+ji.T);A=.5*(ji-ji.T)
        H=np.array([[u@S@u,u@S@v+1j*(u@A@v)],[v@S@u+1j*(v@A@u),v@S@v]],complex)
        mn=min(mn,float(np.linalg.eigvalsh(H).min()));leak=max(leak,float(np.linalg.norm(ji@ei)))
    return mn,leak

def extended_metrics():
    out=metrics();er,wr=grid6();v=.1;en,wn=paired_from_rest(er,wr,v);n=9*len(en)
    C=matrix_of(lambda z: collision(en,wn,v,1,z),n);yp=physical_random_state(en)
    cone={}
    for x in (.2,2.,20.):
        z=expm(x*C)@yp;mn,leak=cone_min_eig(en,z);cone[str(x)]={'min_eig':mn,'screen_leak':leak}
    out['cone']=cone
    I=1+.8*en[:,2]**2;Ju=.5*I[:,None,None]*proj(en);y0=pack9(Ju).ravel();Csc=matrix_of(lambda z: scalar_collision(en,wn,v,1,z),len(en))
    xs=np.array([.02,.04,.08,.16]);ds=[]
    for x in xs:
        Ip=np.trace(unpack9(expm(x*C)@y0),axis1=1,axis2=2);Is=expm(x*Csc)@I;ds.append(float(np.max(abs(Ip-Is))))
    out['I_E_feedback_scaling']={'x':xs.tolist(),'diff':ds,'order':float(np.polyfit(np.log(xs),np.log(ds),1)[0])}
    return out

def lebedev26():
    a=1/np.sqrt(3.0);b=1/np.sqrt(2.0);pts=[];w=[]
    for k in range(3):
        for s in (-1.,1.):
            x=np.zeros(3);x[k]=s;pts.append(x);w.append(4*PI/21)
    for zero in range(3):
        idx=[i for i in range(3) if i!=zero]
        for s1 in (-1.,1.):
            for s2 in (-1.,1.):
                x=np.zeros(3);x[idx[0]]=s1*b;x[idx[1]]=s2*b;pts.append(x);w.append(16*PI/105)
    for sx in (-1.,1.):
        for sy in (-1.,1.):
            for sz in (-1.,1.):pts.append([sx*a,sy*a,sz*a]);w.append(9*PI/70)
    return np.asarray(pts),np.asarray(w)

def physical_screen_random(e,seed=91):
    rng=np.random.default_rng(seed);J=rng.normal(size=(len(e),3,3));P=proj(e);J=np.einsum('aik,akl,alj->aij',P,J,P);return pack9(J).ravel()

def kato_endpoint_order(schedule_path: Path | None = None):
    e,w=lebedev26(); rng=np.random.default_rng(1)
    if schedule_path is None:
        schedule_path=Path(__file__).with_name('typeII_v_schedule.json')
    data=json.loads(Path(schedule_path).read_text())
    dt=float(data['dt']); T=float(data['T']); ts=np.arange(len(data['v2']))*dt
    vs=CubicSpline(ts,np.asarray(data['v2'],float)); vds=CubicSpline(ts,np.asarray(data['v2dot'],float))
    v0=float(vs(0.0)); y0=projector(e,w,v0,1,rng.normal(size=9*len(e)))
    hs=np.array([.05,.025,.0125,.00625,.003125]); errs=[]
    for h in hs:
        y=y0.copy()
        for k in range(int(round(T/h))):
            tm=(k+.5)*h; vm=float(vs(tm)); vd=float(vds(tm))
            K=matrix_of(lambda z:kato(e,w,vm,vd,1,z),len(y)); y=expm(h*K)@y
        vf=float(vs(T)); py=projector(e,w,vf,1,y); errs.append(float(np.linalg.norm(y-py)/np.linalg.norm(y)))
    return {'h':hs.tolist(),'defect':errs,'order':float(np.polyfit(np.log(hs[-4:]),np.log(errs[-4:]),1)[0]),
            'source':data.get('source','unknown')}

def quadrature_audit():
    rec=[]
    for name,(er,wr) in [('grid6',grid6()),('lebedev26',lebedev26())]:
        for v in (.02,.05,.1,.2):
            rf=equilibrium(er,v,1);cf=collision(er,wr,v,1,rf)
            en,wn=paired_from_rest(er,wr,v);rp=equilibrium(en,v,1);cp=collision(en,wn,v,1,rp)
            y=physical_screen_random(en,seed=int(1000*v)+len(en));cy=collision(en,wn,v,1,y)
            rec.append({'grid':name,'n':len(er),'v':v,'fixed_null':float(np.max(abs(cf))),'paired_null':float(np.max(abs(cp))),'paired_left':float(abs(left(en,wn,v,1,cy)))})
    return rec

def stokes_to_pack(e,z):
    e=np.asarray(e,float); z=np.asarray(z,float).reshape(len(e),4); Js=[]
    for ei,(I,Q,U,V) in zip(e,z):
        u,v=tangent_basis(ei)
        Js.append(.5*I*(np.outer(u,u)+np.outer(v,v))
                  +.5*Q*(np.outer(u,u)-np.outer(v,v))
                  +.5*U*(np.outer(u,v)+np.outer(v,u))
                  +.5*V*(np.outer(u,v)-np.outer(v,u)))
    return pack9(np.asarray(Js)).ravel()

def pack_to_stokes(e,y):
    out=[]
    for ei,j in zip(np.asarray(e,float),unpack9(y)):
        u,v=tangent_basis(ei); S=.5*(j+j.T); A=.5*(j-j.T)
        out.extend([u@S@u+v@S@v,u@S@u-v@S@v,2*u@S@v,2*u@A@v])
    return np.asarray(out)

def rest_spectrum_metrics():
    e,w=lebedev26(); n=4*len(e); eye=np.eye(n)
    C=np.column_stack([pack_to_stokes(e,collision(e,w,0.0,1,stokes_to_pack(e,eye[:,j]))) for j in range(n)])
    ev=np.linalg.eigvals(C); imag=float(np.max(np.abs(ev.imag))); r=ev.real
    expected={0.0:1,-0.3:5,-0.5:3,-1.0:n-9}
    counts={str(k):int(np.sum(np.abs(r-k)<2e-11)) for k in expected}
    dev=max(float(np.partition(np.abs(r-k),count-1)[count-1]) for k,count in expected.items())
    return {'dimension':n,'max_imag':imag,'counts':counts,'max_cluster_deviation':dev}

def quadrupole_polarization_metrics():
    e,w=lebedev26(); P=proj(e)
    def pol_amp(c):
        vals=[]
        for ei,j in zip(e,unpack9(c)):
            u,v=tangent_basis(ei); S=.5*(j+j.T)
            vals.append(np.hypot(u@S@u-v@S@v,2*u@S@v))
        return float(np.max(vals))
    iso=np.ones(len(e)); ani=1.0+0.8*(e[:,2]**2-1.0/3.0)
    yiso=pack9(.5*iso[:,None,None]*P).ravel(); yani=pack9(.5*ani[:,None,None]*P).ravel()
    ciso=collision(e,w,0.0,1,yiso); cani=collision(e,w,0.0,1,yani)
    return {'isotropic_polarization':pol_amp(ciso),'quadrupole_polarization':pol_amp(cani),
            'isotropic_collision_null':float(np.max(np.abs(ciso)))}

def run_validation():
    m=extended_metrics()
    m['quadrature']=quadrature_audit()
    m['kato_endpoint']=kato_endpoint_order()
    m['rest_spectrum']=rest_spectrum_metrics()
    m['I_E_quadrupole']=quadrupole_polarization_metrics()
    # gold is a unit-test fixture, not a summary metric
    m.pop('gold',None)
    return m

if __name__=='__main__':
    print(json.dumps(run_validation(),indent=2,sort_keys=True))

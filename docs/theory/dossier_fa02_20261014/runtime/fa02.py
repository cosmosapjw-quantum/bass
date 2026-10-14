"""FA-02: exact fixed-detector cap under a boost and two pointing coordinates.
Uses only FA-01's prescribed Kasner test sector. The three parameters are
(chi, eta, zeta), with sky pointing R3(eta) R2(-zeta) and standard e1 boost.
The observer analyzer is projected observer e2, not a freely reset pixel basis.
"""
from __future__ import annotations
import json,time,sys
from pathlib import Path
import numpy as np
from numpy.polynomial.legendre import leggauss
from jets import Jet, matrix, TERMS
ROOT=Path(__file__).resolve().parents[1]
P=np.array([[.7,.1+.05j],[.1-.05j,.3]],complex)
J2=np.array([[0.,-1.],[1.,0.]])
M3=1.0004; M4=1.000800032

def cap_nodes(delta,nr=8,nphi=16):
    if not 0<delta<=.02:raise ValueError('0<delta<=0.02 required')
    x,w=leggauss(nr);t=(x+1)/2
    r=2*np.arcsin(np.sqrt(t)*np.sin(delta/2))
    ph=np.arange(nphi)*2*np.pi/nphi
    r,ph=np.meshgrid(r,ph,indexing='ij')
    m=np.stack([np.cos(r),np.sin(r)*np.cos(ph),np.sin(r)*np.sin(ph)],axis=-1).reshape(-1,3)
    return m,np.repeat(w/(2*nphi),nphi)

def mapping(m,params,jets=False):
    if jets:
        ch,et,ze=[Jet.var(float(p),i) for i,p in enumerate(params)]
        sh,gh=ch.sinh(),ch.cosh();se,ce=et.sin(),et.cos();sz,cz=ze.sin(),ze.cos()
    else:
        ch,et,ze=np.asarray(params)
        sh,gh=np.sinh(ch),np.cosh(ch);se,ce=np.sin(et),np.cos(et);sz,cz=np.sin(ze),np.cos(ze)
    # Pointing is the physical cap rotation. Its axes do not replace the analyzer field.
    wx=ce*(cz*m[:,0]-sz*m[:,2])-se*m[:,1]
    wy=se*(cz*m[:,0]-sz*m[:,2])+ce*m[:,1]
    wz=sz*m[:,0]+cz*m[:,2]
    A=gh+sh*wx # E_normal(observer)/E_new_observer
    n1=(sh+gh*wx)/A;n2=wy/A;n3=wz/A
    sqrt=lambda z:z.sqrt() if jets else np.sqrt(z)
    den=sqrt(1-wy*wy)*sqrt(A*A-wy*wy)
    co=(A-gh*wy*wy)/den
    si=sh*wy*wz/den
    if jets:rot=matrix(co,-si,si,co)
    else:rot=np.stack([np.stack([co,-si],-1),np.stack([si,co],-1)],-2)
    return (n1,n2,n3),A,rot,(wx,wy,wz)

def coefficients(x,n,A,jets=False):
    n1,n2,n3=n
    sqrt=lambda z:z.sqrt() if jets else np.sqrt(z)
    den=sqrt(1-(1-x*x)*n3*n3);d=sqrt(1-n2*n2);h2=1-n3*n3
    a=(n1*n1+x*n2*n2*n3*n3/den)/(h2*d)
    b=n1*n2*n3*(1-x/den)/(h2*d)
    c=-n2*n3/(den*d);f=n1/(den*d)
    if jets:
        T=matrix(a,b,c,f)
        Ps=T.T@P@T
        G=matrix(.2+.2*c*c,.2*c*f-.3*n1/den,.2*c*f+.3*n1/den,.2+.2*f*f)
        w=M3+.1*M4*A*x**(-2/3)*den
        return w[...,None,None]*Ps,G
    T=np.stack([np.stack([a,b],-1),np.stack([c,f],-1)],-2)
    Ps=np.swapaxes(T,-1,-2)@P@T
    G=np.stack([np.stack([.2+.2*c*c,.2*c*f-.3*n1/den],-1),
                np.stack([.2*c*f+.3*n1/den,.2+.2*f*f],-1)],-2)
    w=M3+.1*M4*A*x**(-2/3)*den
    return w[...,None,None]*Ps,G

def transfer(m,params,steps=256,jets=False):
    n,A,rot,nw=mapping(m,params,jets)
    if jets:
        F=Jet.const(np.zeros((len(m),2,2),complex))
        def rhs(x,f):
            src,G=coefficients(x,n,A,True)
            return src-G@f-f@G.T
    else:
        F=np.zeros((len(m),2,2),complex)
        def rhs(x,f):
            src,G=coefficients(x,n,A,False)
            return src-G@f-f@np.swapaxes(G,-1,-2)
    dx=.5/steps
    for k in range(steps):
        x=.5+dx*k
        k1=rhs(x,F);k2=rhs(x+dx/2,F+dx/2*k1)
        k3=rhs(x+dx/2,F+dx/2*k2);k4=rhs(x+dx,F+dx*k3)
        F=F+dx/6*(k1+2*k2+2*k3+k4)
    return rot@F@rot.T if jets else rot@F@np.swapaxes(rot,-1,-2)

def mean(params,delta=.02,nr=8,nphi=16,steps=256,jets=False):
    if np.max(np.abs(np.imag(params)))==0 and sum(abs(float(np.real(p))) for p in params)>.02000000001:
        raise ValueError('real family requires |chi|+|eta|+|zeta|<=0.02')
    m,w=cap_nodes(delta,nr,nphi);F=transfer(m,params,steps,jets)
    if jets:return Jet(np.einsum('n,knij->kij',w,F.c))
    return np.einsum('n,nij->ij',w,F)

def stokes(F):
    return np.asarray([np.trace(F),F[0,0]-F[1,1],F[0,1]+F[1,0],1j*(F[0,1]-F[1,0])])
def norm(F):return float(np.linalg.svd(F,compute_uv=False).sum())
def json_matrix(F):return {'real':np.real(F).tolist(),'imag':np.imag(F).tolist()}

def main():
    start=time.time()
    jt=mean((0.,0.,0.),jets=True,nr=6,nphi=16,steps=256)
    jr=mean((0.,0.,0.),jets=True,nr=8,nphi=24,steps=512)
    v=np.array([.5,.3,-.2])
    rec=[]
    for t in [.005,.01,.02]:
        par=t*v
        f=mean(par,nr=10,nphi=24,steps=512)
        fc=mean(par,nr=6,nphi=16,steps=256)
        lin=jr.c[0]+sum(par[i]*jr.c[i+1] for i in range(3))
        quad=jr.value(par)
        rec.append({'l1_parameter_radius':t,'params':par.tolist(),'stokes':np.real(stokes(f)).tolist(),
        'first_order_error_trace_norm':norm(f-lin),'second_order_error_trace_norm':norm(f-quad),
        'refinement_trace_norm':norm(f-fc),
        'uniform_first_bound':.9*(t/.2)**2/(1-t/.2),
        'uniform_second_bound':.9*(t/.2)**3/(1-t/.2),
        'first_prediction':np.real(stokes(lin)).tolist(),'second_prediction':np.real(stokes(quad)).tolist()})
    # Separate signed directions distinguish all second-order and mixed responses.
    checks=[]
    for vec in [[1,0,0],[0,1,0],[0,0,1],[0,.5,.5],[.5,.5,0]]:
        vv=np.array(vec,float);hh=.001
        fp=mean(hh*vv,nr=6,nphi=16,steps=512)
        fm=mean(-hh*vv,nr=6,nphi=16,steps=512)
        f0=mean([0,0,0],nr=6,nphi=16,steps=512)
        d1=sum(vv[i]*jr.c[i+1] for i in range(3))
        d2=2*(jr.value(vv)-jr.c[0]-d1)
        checks.append({'direction':vv.tolist(),'h':hh,
        'first_difference_max':float(np.max(np.abs((fp-fm)/(2*hh)-d1))),
        'second_difference_max':float(np.max(np.abs((fp-2*f0+fm)/hh**2-d2)))})
    out={'model':'FA-02 fixed-detector observer boost/pointing family',
      'domain':{'parameter_l1_max':.02,'cap_max':.02,'x':[.5,1.],'band':[.98,1.02]},
      'coefficient_convention':str(TERMS),
      'jet_matrix':json_matrix(jr.c),'jet_stokes_coefficients':np.real(np.stack([stokes(c) for c in jr.c])).tolist(),
      'jet_refinement_max_abs':float(np.max(np.abs(jr.c-jt.c))),
      'finite_parameter_checks':rec,'directional_checks':checks,
      'holomorphic_envelope':{'radius':.2,'trace_norm_bound':.9,'real_domain_radius':.02,'derivative_margin':.18},
      'empirical_provider_errors':None,'external_independent_review':False,
      'elapsed_seconds':time.time()-start}
    (ROOT/'runtime/RESULTS.json').write_text(json.dumps(out,indent=2))
    print(json.dumps(out,indent=2))
if __name__=='__main__':main()

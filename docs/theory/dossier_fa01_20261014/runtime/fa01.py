"""FA-01: prescribed off-axis Kasner polarized transfer.
Units: x=t/t_o; spectral/calibration factors follow OSM and AP-OPTICS.
No empirical input is inferred. All screen matrices below use right-handed
observer analyzers and the exact normal-gauge parallel screen.
"""
from __future__ import annotations
import json, time
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp, quad
from numpy.polynomial.legendre import leggauss

ROOT=Path(__file__).resolve().parents[1]
P=np.array([[.7,.1+.05j],[.1-.05j,.3]],complex)
P3=np.zeros((3,3),complex); P3[1:,1:]=P
K3=np.diag([.4,.4,.8])
J2=np.array([[0.,-1.],[1.,0.]])
G0=np.diag([.2,.4])+.3*J2
m3=1.0004; m4=1.000800032

def analyzers(n):
    n=np.atleast_2d(n)
    a=np.array([0.,1.,0.])[None,:]-n[:,1,None]*n
    a/=np.sqrt(1-n[:,1]**2)[:,None]
    b=np.cross(n,a)
    return np.stack([a,b],axis=-1)

def geometry(x,n):
    n=np.atleast_2d(n)
    den=np.sqrt(1-(1-x*x)*n[:,2]**2)
    q=x**(-2/3)*den
    e=n*np.array([1.,1.,x])[None,:]/den[:,None]
    h=np.sqrt(n[:,0]**2+n[:,1]**2)
    k=np.stack([-n[:,1]/h,n[:,0]/h,np.zeros(len(n))],axis=-1)
    t=np.cross(e,k)
    B=np.stack([k,t],axis=-1)
    B0=np.stack([k,np.cross(n,k)],axis=-1)
    Ao=analyzers(n)
    C=np.swapaxes(B0,-1,-2)@Ao
    S=B@C
    Ps=np.swapaxes(S,-1,-2)@P3@S
    Ks=np.swapaxes(S,-1,-2)@K3@S
    G=.5*Ks+.3*e[:,0,None,None]*J2
    return q,e,S,Ps,G

def ray_transfer(n,steps=512):
    """Two energy polynomial carriers, integrated in x, all rays in a batch."""
    n=np.atleast_2d(np.asarray(n,float))
    if np.max(np.abs(np.sum(n*n,axis=1)-1))>2e-12:
        raise ValueError('unit observer directions required')
    F=np.zeros((len(n),2,2,2),complex)
    def rhs(x,F):
        q,_,_,Ps,G=geometry(x,n)
        B=np.stack([Ps,q[:,None,None]*Ps],axis=1)
        return B-G[:,None]@F-F@np.swapaxes(G,-1,-2)[:,None]
    h=.5/steps
    for k in range(steps):
        x=.5+k*h
        k1=rhs(x,F); k2=rhs(x+h/2,F+h*k1/2)
        k3=rhs(x+h/2,F+h*k2/2); k4=rhs(x+h,F+h*k3)
        F+=h/6*(k1+2*k2+2*k3+k4)
    return F

def stokes(F):
    return np.array([np.trace(F).real,(F[0,0]-F[1,1]).real,
                     2*F[0,1].real,-2*F[0,1].imag])

def cap_nodes(delta,nr=8,nphi=16):
    # Integrate t=(1-cos(rho))/(1-cos(delta)) without small-area cancellation.
    g,w=leggauss(nr); t=(g+1)/2
    rho=2*np.arcsin(np.sqrt(t)*np.sin(delta/2))
    phi=2*np.pi*np.arange(nphi)/nphi
    rr,pp=np.meshgrid(rho,phi,indexing='ij')
    n=np.stack([np.cos(rr),np.sin(rr)*np.cos(pp),np.sin(rr)*np.sin(pp)],-1).reshape(-1,3)
    weights=np.repeat(w/2/nphi,nphi)
    return n,weights

def cap_mean(delta,nr=8,nphi=16,steps=512,chi=0.):
    nw,w=cap_nodes(delta,nr,nphi)
    if chi==0:
        n=nw; rot=np.broadcast_to(np.eye(2),(len(n),2,2)); invD=np.ones(len(n))
    else:
        beta=np.tanh(chi); gam=np.cosh(chi)
        n=nw.copy()
        n[:,0]=(nw[:,0]+beta)/(1+beta*nw[:,0])
        n[:,1:]=nw[:,1:]/(gam*(1+beta*nw[:,0]))[:,None]
        invD=gam*(1+beta*nw[:,0])
        old=analyzers(n)
        # Boost and add the null gauge term so the polarization has w-time component 0.
        pulled=old.copy(); pulled[:,0,:]+= (gam-1)*old[:,0,:]
        pulled+=gam*beta*nw[:,:,None]*old[:,0,None,:]
        rot=np.swapaxes(analyzers(nw),-1,-2)@pulled
    F=ray_transfer(n,steps)
    band=m3*F[:,0]+.1*m4*invD[:,None,None]*F[:,1]
    band=rot@band@np.swapaxes(rot,-1,-2)
    return np.einsum('n,nij->ij',w,band),{
        'min_eigenvalue':float(np.min(np.linalg.eigvalsh(band))),
        'max_rotation_orthogonality_error':float(np.max(np.abs(rot@np.swapaxes(rot,-1,-2)-np.eye(2))))}

def central_and_quadratic():
    """Angular quadratic coefficient from the differentiated transfer IVP.
    C=azimuthal mean of the rho^2 coefficient; sphere Laplacian=4C.
    This IVP is new angular work; no old test suite is invoked.
    """
    def rhs(x,y):
        F,C=y.reshape(2,2,2)
        q=x**(-2/3); w=m3+.1*m4*q
        T2=-.25*np.diag([1.,x*x])
        P2=T2.T@P+P@T2
        G2=np.array([[0.,.075*(1+x*x)],[-.075*(1+x*x),-.1*x*x]])
        w2=-.025*m4*q*(1-x*x)
        dF=w*P-G0@F-F@G0.T
        dC=w*P2+w2*P-G0@C-C@G0.T-G2@F-F@G2.T
        return np.stack([dF,dC]).ravel()
    sol=solve_ivp(rhs,(.5,1),np.zeros(8,complex),method='DOP853',rtol=2e-13,atol=2e-15)
    if not sol.success: raise RuntimeError(sol.message)
    return sol.y[:,-1].reshape(2,2,2)

def moment(delta,k):
    # Exact spherical area expectation, stably evaluated.
    return quad(lambda t:(2*np.arcsin(np.sqrt(t)*np.sin(delta/2)))**k,0,1,
                epsabs=1e-20,epsrel=3e-13)[0]

def main():
    start=time.time(); F0,C=central_and_quadratic()
    records=[]
    for delta in [.005,.01,.02]:
        coarse,_=cap_mean(delta,6,12,256)
        fine,diag=cap_mean(delta,10,24,512)
        pred=F0+moment(delta,2)*C
        rem=fine-pred
        m4rad=moment(delta,4)
        records.append({'delta_rad':delta,'stokes':stokes(fine).tolist(),
          'central_stokes':stokes(F0).tolist(),'first_corrected_stokes':stokes(pred).tolist(),
          'remainder_stokes':stokes(rem).tolist(),
          'remainder_trace_norm':float(np.sum(np.abs(np.linalg.eigvalsh(rem)))),
          'uniform_remainder_bound_per_stokes':1.61/(.4-.02)**4*m4rad,
          'spherical_second_moment':moment(delta,2),'spherical_fourth_moment':m4rad,
          'refinement_max_abs':float(np.max(np.abs(coarse-fine))),**diag})
    actual,diag=cap_mean(.02,10,24,512,chi=.02)
    # the unchanged beam is physically different from the boosted one.
    outputs={'model':'FA-01 exact prescribed Kasner; analytic screens and numerical linear transfer',
      'central_stokes':stokes(F0).tolist(),'quadratic_mean_C_stokes':stokes(C).tolist(),
      'spherical_laplacian_stokes':stokes(4*C).tolist(),'caps':records,
      'actual_observer':{'rapidity':.02,'cap_rad':.02,'fixed_band':[.98,1.02],
       'stokes':stokes(actual).tolist(),**diag},
      'uniform_envelope':{'analytic_radius':.4,'real_cap_max':.02,'complex_transfer_trace_bound':1.61,
       'fourth_directional_derivative_bound':24*1.61/.38**4,
       'semantics':'proved analytic upper expressions; displayed decimals not interval-certified execution'},
      'elapsed_seconds':time.time()-start,'empirical_provider_error':None}
    (ROOT/'runtime'/'RESULTS.json').write_text(json.dumps(outputs,indent=2))
    print(json.dumps(outputs,indent=2))
if __name__=='__main__':main()

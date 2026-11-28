"""Coefficient of the archived C3X discrete midpoint + rest Thomson split, evaluated without finite amplitude subtraction."""
from pathlib import Path
import sys,json,hashlib,time,numpy as np
D=Path(__file__).resolve().parent;P=D.parent;E=P/'r118c4d_precision_jet';F=P/'r118c4f_robust_transfer';X=P/'r118c3x_native_coefficients';L=P/'r118c3l_reachable_sky'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,o):(D/n).write_text(json.dumps(o,indent=2)+'\n')
ns={'__file__':str(E/'bass.py'),'__name__':'prior'};exec(compile((E/'bass.py').read_text(),str(E/'bass.py'),'exec'),ns)
ld=np.longdouble;cd=np.clongdouble
OG,ON,OM,OL,T0,K0=[ld(str(ns[k])) for k in ['OG','ON','OM','OL','T0','K0']]
J,W,ident=ns['harmonic']();J=J.astype(cd);W=W.astype(cd);ii,jj=np.triu_indices(5,1)
z=np.load(F/'TRAIN_CONTROLS.npz');controls={k:z['control_'+k].astype(ld) for k in ['old','new']}
controls['generic']=np.array([[.13,.07,.01,.03,.04,.06,.02],[-.12,.01,.09,-.08,.04,.03,-.02],[.04,.02,.06,.01,.07,.08,.03],[.03,-.04,.02,.03,.05,-.02,.04],[.02,.01,-.03,.05,-.01,.03,-.02]],dtype=ld)
controls['collinear']=np.outer(np.array([.2,.1,.05,-.03,.04],ld),np.array([1,.6,-.2,.5,.1,-.1,.7],ld));controls['zero']=np.zeros((5,7),ld)
clock=np.genfromtxt(L/'clock.csv',names=True,delimiter=',');a0=ld(1)/1601;cut=np.log(ld(1)/(21*a0));end=np.log(ld('.2')/a0)
def bg_table(t,nr):
 x,w,_=ns['gl'](nr);y=30*(1+x);w=30*w;f=1/(1+np.exp(y));m=np.array([.001,.006,.05],ld);V=1/(1+np.exp(-ld('.5')*((y-8)/ld('1.4'))**2+ld('.5')*((y-ld('.7'))/ld('1.4'))**2));v=np.stack([V,1-V]);fac=ON/(3*np.sum(w*y**3*f));cold=OM+ON-fac*np.sum(w*y*y*f*np.hypot(y[None,:],m[:,None]/T0))
 out=np.empty((len(t),8),ld)
 for l in range(0,len(t),512):
  tt=t[l:l+512];a=a0*np.exp(tt);ee=np.hypot(y[None,None,:],a[:,None,None]*m[None,:,None]/T0);rho=np.sum(w*y*y*f*ee,axis=(1,2));tr=np.sum(w*y**4*f/ee,axis=(1,2));G=np.sum(w*y**4*f/ee*(ld(2)/3-ld(2)/15*(y/ee)**2),axis=(1,2));F=np.einsum('tmr,vr->tmv',ld(2)/15*w*y**5*f*(1-f)/ee,v,optimize=False)
  out[l:l+len(tt),0]=(cold*a+OG+fac*rho)/a**4;out[l:l+len(tt),1]=(OG+fac*tr)/a**4;out[l:l+len(tt),2]=fac*G/a**4;out[l:l+len(tt),3:]=0 # overwrite below using 6 source terms in separate array
  if l==0:src=np.empty((len(t),3,2),ld)
  src[l:l+len(tt)]=fac*F/a[:,None,None]**4
 return out[:,:3],src
def solve(n,nr,labels):
 tt=np.r_[np.linspace(ld(0),cut,n+1),np.linspace(cut,end,n//4+1)[1:]];dt=np.diff(tt);mid=(tt[:-1]+tt[1:])/2;ts=np.empty(2*len(dt),ld);ts[::2]=tt[:-1];ts[1::2]=mid;bg,src=bg_table(ts,nr)
 ne=np.interp(ts.astype(float),clock['u'],clock['ne_m3']).astype(ld);C=np.stack([controls[k] for k in labels]);csrc=C[:,:,1:].transpose(0,2,1).reshape(len(C),3,2,5);jall=np.einsum('tmv,amvk->tak',src,csrc,optimize=False)
 S=C[:,:,0].copy();B=np.zeros_like(S);I=np.zeros_like(S);P0=np.zeros_like(S);BB=np.zeros((len(C),7),cd);ww=np.zeros((len(C),10),ld);h=np.sqrt(bg[0,0]+OL);a=a0;maxg=ld(0);maxw=ld(0)
 def split(S,I,P0,BB,ww,d,tau):
  hh=d/2
  # At this Taylor order intensity from the unpolarized monopole has zero B3 source.
  def bs(P):
   return np.einsum('kij,ai,aj->ak',J[1],S,P,optimize=False)
  def wedge(P):return S[:,ii]*P[:,jj]-S[:,jj]*P[:,ii]
  I=I-4*hh*S;BB=BB+hh*bs(P0);ww=ww+hh*wedge(P0)
  e=np.exp(-tau);f=np.exp(-ld('.3')*tau)*(-np.expm1(-ld('.7')*tau))/ld('.7')
  NI=e*I+f*(ld('.1')*I-ld('.4')*P0);NP=e*P0+f*(-ld('.15')*I+ld('.6')*P0)
  BB=e*BB+hh*bs(NP);ww=e*ww+hh*wedge(NP);NI=NI-4*hh*S
  return NI,NP,BB,ww
 def rhs(i,s,b,it,hh):
  rho,tr,g=bg[i];q=(rho+tr-2*OL)/(2*hh*hh);a0t=a0*np.exp(ts[i]);p=jall[i]-g*b+ld(2)/15*OG/a0t**4*it
  return q,(q-2)*s+3*p/(hh*hh)
 hist=[]
 for k,du in enumerate(dt):
  i=2*k;q,f=rhs(i,S,B,I,h);sm=S+du/2*f;bm=B+du/2*S;hm=h*np.exp(-du/2*(1+q))
  im,pm,_,_=split(S,I,P0,BB,ww,du/2,K0*(ne[i]+ne[i+1])/2/h*du/2)
  qm,fm=rhs(i+1,sm,bm,im,hm)
  I,P0,BB,ww=split(sm,I,P0,BB,ww,du,K0*ne[i+1]/hm*du)
  B+=du*sm;S+=du*fm;h*=np.exp(-du*(1+qm))
  maxg=max(maxg,abs(1-(bg[i,0]+OL)/(h*np.exp(du*(1+qm)))**2))
  if (k+1) in [n,len(dt)]:hist.append(dict(epoch=int(k+1==len(dt)),h=float(h),S=S.astype(float).tolist(),I=I.astype(float).tolist(),P=P0.astype(float).tolist()))
 Wb=np.einsum('ki,ai->ak',W,ww);assert np.all(np.isfinite(BB));assert np.linalg.norm(BB-Wb)<ld('1e-14')*max(ld(1),np.linalg.norm(BB))
 return BB,ww,S,I,P0,h,hist,float(maxg),np.linalg.norm(BB-Wb,axis=1)
def main():
 cases=[];allB=[];native=json.loads((F/'NATIVE_16384.json').read_text())['results']
 labels=['old','new','generic','collinear','zero']
 for n in [2048,4096,8192,16384,32768]:
  t=time.monotonic();b,w,s,i,p,h,hist,g,diff=solve(n,192,labels);allB.append(b)
  row=dict(n=n,nr=192,seconds=time.monotonic()-t,background_h=float(h),stage_gauss_max=g,controls={k:dict(B2_norm=float(np.linalg.norm(x)),B2_re=x.real.astype(float).tolist(),B2_im=x.imag.astype(float).tolist(),direct_wedge_abs=float(d)) for k,x,d in zip(labels,b,diff)},history=hist)
  if n==16384:
   for k,x in zip(labels[:2],b[:2]):
    y=np.array(native[k]['B2_re'])+1j*np.array(native[k]['B2_im']);row['controls'][k]['native_finite_difference_gap']=float(np.linalg.norm(x-y))
  cases.append(row);print(n,{k:v['B2_norm'] for k,v in row['controls'].items()},flush=True)
 assert all(np.linalg.norm(x[-1])==0 for x in allB)
 arr=np.stack(allB);out=dict(rows=cases,labels=labels,successive_vector_diff=np.linalg.norm(np.diff(arr,axis=0),axis=2).astype(float).tolist(),native_16384=native,source=dict(native=sha(X/'native.rs'),thomson_archive=sha(X/'ops/owned_thomson.rs.gz'),vlasov_archive=sha(X/'ops/owned_vlasov.rs.gz'),clock=sha(L/'clock.csv'),control=sha(F/'TRAIN_CONTROLS.npz'),generator=ident),scope='direct Taylor coefficient of source-owned discrete midpoint + exact rest-electron collision split at zero anisotropy, longdouble; not a compiled native AD solver; h0 evolved using Raychaudhuri midpoint, actual clock, generator numerical')
 np.savez_compressed(D/'DISCRETE_B2.npz',n=np.array([2048,4096,8192,16384,32768]),labels=np.array(labels),B2=arr)
 write('DISCRETE_B2.json',out)
if __name__=='__main__':main()

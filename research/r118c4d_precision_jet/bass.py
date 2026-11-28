"""C4D fixed physical controls: all clock knots, matched DP5 arithmetic, actual B3 coefficient and radial jets."""
from pathlib import Path
import sys,json,hashlib,time,numpy as np
from numpy.polynomial.legendre import leggauss
from itertools import combinations
D=Path(__file__).resolve().parent;P=D.parent;S=P/'r118c3s_radial_envelope';B=P/'r118c4b_temporal_mask';C3=P/'r118c4c_conditioned_transfer';A4=P/'r118c4a_robust_wedge'
sys.path.insert(0,str(S));from envelope import OG,ON,OM,OL,T0,K0,CLOCK,EARLY
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,o):(D/n).write_text(json.dumps(o,indent=2)+'\n')
Z=np.load(B/'REFINED_CONTROLS.npz');H=Z['H'];A=Z['A'][list(Z['labels']).index('refit_intermediate')];control=A@H
ns={'__file__':str(A4/'bass.py'),'__name__':'prior'};exec(compile((A4/'bass.py').read_text(),ns['__file__'],'exec'),ns);P1=ns['P1'];P3=ns['P3'];vec=ns['vec'];wedge=ns['wedge']
ii,jj=np.array(list(combinations(range(5),2))).T
def harmonic():
 from radial_jets import gen,Y00,M,harm_to_stf
 ops=gen();d=np.sqrt(8/3);k=np.sqrt(4*np.pi/15)
 def stfh(v):
  a=np.zeros(M,complex);a[8]=k*(v[0]-1j*v[2]);a[6]=np.sqrt(2)*k*v[1];a[7]=k*(-v[3]+1j*v[4]);a[4]=a[8].conjugate();a[5]=-a[7].conjugate();return a
 zero=np.zeros(3*M,complex);zero[0]=Y00;J=np.zeros((2,7,5,5),complex);checks=[]
 for j,e in enumerate(np.eye(5)):
  a=stfh(e);pol=np.r_[np.zeros(M),d*a,d*a];intensity=np.r_[a,np.zeros(2*M)]
  g=ops[j]@zero;checks.append(float(np.linalg.norm(harm_to_stf(g)+4*e)))
  for i in range(5):
   for q,y in enumerate([intensity,pol]):
    f=(ops[i]@y).reshape(3,M);J[q,:,i,j]=.5j*(f[1,9:16]-f[2,9:16])/Y00
 # Actual native generator bilinear forms, including finite symmetric defects.
 Jp=J[1];anti=(Jp-Jp.transpose(0,2,1))/2;W=anti[:,ii,jj]
 sym=np.linalg.norm((Jp+Jp.transpose(0,2,1))/2);n=np.linalg.norm(Jp)
 out=dict(monopole_stf_max=max(checks),intensity_to_B3_norm=float(np.linalg.norm(J[0])),polarized_bilinear_norm=float(n),symmetric_relative=float(sym/max(n,1e-300)),spin1_projection_relative=float(np.linalg.norm(W@P1)/np.linalg.norm(W)),generator_sha256=sha(P/'r118c3o_analytic_s3/generator.csv'),scope='numerical bilinear source in source-owned spin convention; no exact generator coefficients asserted')
 return J,W,out
def gl(n):
 # Refine Gauss-Legendre roots and weights in actual platform long double.
 ld=np.longdouble;x=leggauss(n)[0].astype(ld)
 for _ in range(5):
  p0=np.ones_like(x);p1=x.copy()
  for j in range(2,n+1):p0,p1=p1,((2*j-1)*x*p1-(j-1)*p0)/j
  dp=n*(p0-x*p1)/(1-x*x);x-=p1/dp
 p0=np.ones_like(x);p1=x.copy()
 for j in range(2,n+1):p0,p1=p1,((2*j-1)*x*p1-(j-1)*p0)/j
 dp=n*(p0-x*p1)/(1-x*x);w=2/((1-x*x)*dp*dp)
 assert abs(w.sum()-2)<1e-15
 return x,w,float(np.max(abs(p1)))
def integrate(kind,nr,sub):
 start=time.monotonic();dtype={'f64':np.float64,'ld':np.longdouble,'mf64':np.float64,'mld':np.longdouble}[kind];D0=dtype;matched=kind.startswith('m')
 def q(x):return D0(str(x))
 J,W,ident=harmonic();Jr=np.concatenate([J.real,J.imag],axis=1).astype(dtype)
 e=np.genfromtxt(EARLY,names=True,delimiter=',',dtype=dtype);l=np.genfromtxt(CLOCK,names=True,delimiter=',',dtype=dtype)
 a0=e['a'][0];cut=np.log(1/(q(21)*a0));end=np.log(q(.2)/a0);x,w,glres=gl(nr);y=(30*(1+x)).astype(dtype);w=(30*w).astype(dtype);f=1/(1+np.exp(y))
 m=np.array([q(.001),q(.006),q(.05)],dtype=dtype);C=control.T.astype(dtype);fac=q(ON)/(3*np.sum(w*y**3*f));a1=-q(.5)*((y-q(.7))/q(1.4))**2;a2=-q(.5)*((y-q(8))/q(1.4))**2
 v=1/(1+np.exp(a2-a1));V=np.stack([v,1-v]);src=C[1:].reshape(3,2,5)
 cold=q(OM)+q(ON)-fac*np.sum(w*y*y*f*np.hypot(y[None,:],m[:,None]/q(T0)))
 bgw=w*y*y*f;bgp=w*y**4*f;bgj=(q(2)/15)*w*y**5*f*(1-f)
 def bg(t,ne):
  a=a0*np.exp(t);en=np.hypot(y[None,:],a*m[:,None]/q(T0));rho=np.sum(bgw*en,axis=1);pt=np.sum(bgp/en,axis=1);G=np.sum(bgp/en*(q(2)/3-q(2)/15*(y/en)**2))
  j=np.einsum('mr,vr,msk->mk',bgj/en,V,src) if False else np.einsum('mr,vr,mvk->k',bgj/en,V,src)
  h2=(cold*a+q(OG)+fac*rho.sum())/a**4+q(OL);qd=(cold*a+2*q(OG)+fac*(rho+pt).sum())/(2*h2*a**4)-q(OL)/h2;k=q(K0)*ne/np.sqrt(h2)
  return a,h2,qd,k,j,G
 def rhs(t,z,ne):
  a,h2,qd,k,j,G=bg(t,ne);s,b,I,P=z[:20].reshape(4,5);ww=z[20:30];bb=z[30:]
  stress=(fac*(j-G*b)+q(2)/15*q(OG)*I)/a**4
  bs=np.einsum('kij,i,j->k',Jr[0],s,I)+np.einsum('kij,i,j->k',Jr[1],s,P)
  return np.r_[(qd-2)*s+3*stress/h2,s,-4*s-k*(q(.9)*I+q(.4)*P),-k*(q(.15)*I+q(.4)*P),s[ii]*P[jj]-s[jj]*P[ii]-k*ww,bs-k*bb]
 def r(a,b):return dtype(a)/dtype(b)
 # Dormand-Prince fifth-order weights, exact rational construction in target dtype.
 c=[0,r(1,5),r(3,10),r(4,5),r(8,9),dtype(1)]
 A0=[[],[r(1,5)],[r(3,40),r(9,40)],[r(44,45),-r(56,15),r(32,9)],[r(19372,6561),-r(25360,2187),r(64448,6561),-r(212,729)],[r(9017,3168),-r(355,33),r(46732,5247),r(49,176),-r(5103,18656)]]
 weights=[r(35,384),0,r(500,1113),r(125,192),-r(2187,6784),r(11,84)]
 def interp(t,x,y):
  if t<=x[0]:return y[0]
  if t>=x[-1]:return y[-1]
  j=np.searchsorted(x,t,side='right')-1;return y[j]+(y[j+1]-y[j])*(t-x[j])/(x[j+1]-x[j])
 clocks=[(np.r_[dtype(0),e['u'][(e['u']>0)&(e['u']<cut)],cut],e['u'],e['ne_m3'],sub),(np.r_[cut,cut+l['u'][(l['u']>0)&(l['u']<end-cut)],end],cut+l['u'],l['ne_m3'],1)]
 mesh_sha=None
 if matched:
  ef=np.genfromtxt(EARLY,names=True,delimiter=',');lf=np.genfromtxt(CLOCK,names=True,delimiter=',')
  a0=dtype(ef['a'][0]);c0=float(np.log(1/(21*ef['a'][0])));e0=float(np.log(.2/ef['a'][0]))
  cut=dtype(c0);end=dtype(e0)
  e1=ef['u'];l1=c0+lf['u'];tol=1e-14
  early=np.unique(np.r_[0.,e1[(e1>tol)&(e1<c0-tol)],c0]);late=np.unique(np.r_[c0,l1[(l1>c0+tol)&(l1<e0-tol)],e0])
  clocks=[(early.astype(dtype),e1.astype(dtype),ef['ne_m3'].astype(dtype),sub),(late.astype(dtype),l1.astype(dtype),lf['ne_m3'].astype(dtype),1)]
  mesh_sha=hashlib.sha256(early.tobytes()+late.tobytes()).hexdigest()
 z=np.zeros(44,dtype=dtype);z[:5]=C[0];nstep=0;hist=[]
 for u,xx,ne,nsub in clocks:
  for left,right in zip(u[:-1],u[1:]):
   nl,nr0=interp(left,xx,ne),interp(right,xx,ne)
   for j0 in range(nsub):
    t=left+(right-left)*j0/nsub;h=(right-left)/nsub;st=[]
    for j in range(6):
     y0=z.copy()
     for a,v0 in zip(A0[j],st):y0+=h*a*v0
     k=rhs(t+c[j]*h,y0,nl+(nr0-nl)*(j0+c[j])/nsub);st.append(k)
    for a,k in zip(weights,st):z+=h*a*k
    nstep+=1
   if len(hist)==0 or len(hist)%1024==0:pass
  hist.append(z.copy())
 assert np.isfinite(z).all()
 w0=z[20:30];bd=z[30:37]+1j*z[37:44];bw=W.astype(np.clongdouble)@w0.astype(np.longdouble)
 target=P1@wedge(Z['A'][list(Z['labels']).index('baseline')],np.array(json.loads((S/'RADIAL_FINE.json').read_text())['M']));norm=float(np.linalg.norm(target))
 tag=f'{kind}_{nr}_{sub}';np.savez_compressed(D/(tag+'.npz'),state=z,history=np.array(hist),J=J,W=W,control=control)
 out=dict(kind=kind,nr=nr,early_subdivisions=sub,steps=nstep,rhs_evaluations=6*nstep,mantissa=np.finfo(dtype).nmant,matched_grid_sha256=mesh_sha,gl_polynomial_residual=glres,seconds=time.monotonic()-start,spin3_relative=float(np.linalg.norm(P3.astype(dtype)@w0)/norm),spin1_relative=float(np.linalg.norm(P1.astype(dtype)@w0-target)/norm),wedge=[str(v) for v in w0],B2_direct_norm=float(np.linalg.norm(bd)),B2_wedge_norm=float(np.linalg.norm(bw)),B2_direct_wedge_abs=float(np.linalg.norm(bd-bw)),B2_re=[float(x) for x in bd.real],B2_im=[float(x) for x in bd.imag],harmonic=ident,clock_hashes=[sha(EARLY),sha(CLOCK)],control_sha256=sha(B/'REFINED_CONTROLS.npz'),scope='all represented clock knots, fixed DP5, actual physical source, extended arithmetic only; not arbitrary precision or exact continuum')
 write(tag+'.json',out);print(tag,out,flush=True)
def jet(nt):
 from radial_jets import solve
 t0=time.monotonic();u,s,m,b=solve(control,nt,192,8);tag=f'jet_{nt}';np.savez_compressed(D/(tag+'.npz'),t=u,S=s,monopole=m,B=b,control=control)
 out=dict(nt=nt,nr=192,nmu=8,seconds=time.monotonic()-t0,B3_order1_to5=np.linalg.norm(b[:,9:16],axis=1).tolist(),B2_re=b[1,9:16].real.tolist(),B2_im=b[1,9:16].imag.tolist(),scope='existing source-owned fourth-order geometry/fifth-order harmonic jet, fixed uniform RK4 and radial interpolation; not exact event segmented')
 write(tag+'.json',out);print(tag,out,flush=True)
def analysis():
 rows=[json.loads(p.read_text()) for p in sorted(D.glob('ld_*.json'))+sorted(D.glob('f64_*.json'))+sorted(D.glob('mld_*.json'))+sorted(D.glob('mf64_*.json'))];jets=[json.loads(p.read_text()) for p in sorted(D.glob('jet_*.json'))];d={f"{x['kind']}_{x['nr']}_{x['early_subdivisions']}":x for x in rows};compar=[]
 for a,b in [('f64_192_16','ld_192_16'),('ld_192_16','ld_192_32'),('ld_192_32','ld_256_32'),('mf64_192_16','mld_192_16'),('mld_192_16','mld_192_32')]:
  if a not in d or b not in d:continue
  x,y=d[a],d[b];u=np.array(x['wedge'],np.longdouble);v=np.array(y['wedge'],np.longdouble);compar.append(dict(a=a,b=b,wedge_relative=float(np.linalg.norm(u-v)/np.linalg.norm(v)),B2_absolute=float(np.linalg.norm(np.array(x['B2_re'])+1j*np.array(x['B2_im'])-np.array(y['B2_re'])-1j*np.array(y['B2_im'])))))
 prior=json.loads((C3/'NATIVE.json').read_text())['results']['candidate'];out=dict(rows=rows,comparisons=compar,jets=jets,prior_native=prior,scope='matched arithmetic vs mesh refinement; compare direct coefficient and nonlinear jet, no exact cancellation claim')
 write('PRECISION_SUMMARY.json',out);print('analysis',compar,flush=True)
if __name__=='__main__':
 if sys.argv[1]=='integrate':integrate(sys.argv[2],int(sys.argv[3]),int(sys.argv[4]))
 elif sys.argv[1]=='jet':jet(int(sys.argv[2]))
 else:analysis()

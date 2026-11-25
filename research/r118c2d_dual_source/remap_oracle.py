"""Independent positive dual-moment remap reference using a scalar
mean inversion and direct GL quadrature. Zero collision time; actual
C2C signed live boundary fixture, not a new physical trajectory."""
import argparse,pathlib,json,hashlib,subprocess
import numpy as np
from scipy.optimize import brentq
from numpy.polynomial.legendre import leggauss
from scipy.constants import c,h
P=pathlib.Path
p=argparse.ArgumentParser();p.add_argument('--final',type=P,required=True);p.add_argument('--binary',type=P,required=True);p.add_argument('--lift',type=P,required=True);p.add_argument('--out',type=P,required=True);a=p.parse_args()
out=a.out;out.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(P(p).read_bytes()).hexdigest()
r=json.loads((a.final/'RESULTS.json').read_text());row=next(q for q in r['cases'] if q['case']=='live_time_8')
gp=P(row['command'][1]);case=P(row['command'][2]);s=case.read_text().split()
s[1]='0';cas=out/'drift_only.txt';cas.write_text(' '.join(s)+'\n')
cmd=[str(a.binary.resolve()),str(gp),str(cas),str(out/'drift_only')];subprocess.run(cmd,check=True,capture_output=True)
src=np.load(a.lift,allow_pickle=False);nu0=float(src['nu0']);dnu=float(src['dnu']);b=dnu/nu0
with gp.open('rb') as f:
 assert f.read(8)==b'RECPOS01';n,na,nb=np.fromfile(f,dtype='<u4',count=3)
 q=np.fromfile(f,dtype='<f8',count=4*na).reshape(na,4);mode=np.fromfile(f,dtype='<f8',count=3*n).reshape(n,3)
weights=q[:,3];pos=5;x=np.array(s[pos:pos+n],float);pos+=n;clock=np.array(s[pos:pos+na],float);pos+=na
f=np.array(s[pos:pos+n*na],float).reshape(n,na);pos+=n*na
assert s[pos]=='1';pos+=1;ext=int(s[pos]);extent=float(s[pos+1]);pos+=2
drift=np.array(s[pos:pos+2*na],float).reshape(2,na);pos+=2*na
outer=np.array(s[pos:],float).reshape(na,2*ext)
bounds=x.reshape(35,2);idx=np.argsort(bounds[:,0]);edges=np.r_[np.linspace(-extent,-21.25,ext+1)[:-1],bounds[idx,0],21.25,np.linspace(21.25,extent,ext+1)[1:]]
nc=len(edges)-1
M=np.zeros((na,nc,2));M[:,ext:ext+35,:]=(f*mode[:,0,None]*weights[None,:]).reshape(35,2,na)[idx].transpose(2,0,1)
z,w=leggauss(48);t=(1+z)/2;w=w/2
fac=8*np.pi*nu0**2*dnu/c**3
for j in list(range(ext))+list(range(ext+35,nc)):
 l,r=edges[j:j+2];v=fac*(r-l)*w*(1+b*(l+(r-l)*t))**2
 i=j if j<ext else j-35
 M[:,j,0]=outer[:,i]*weights*(v@(1-t));M[:,j,1]=outer[:,i]*weights*(v@t)
N0=M.sum()
def mean(k):
 # For reference use high-order quadrature for moderate tilt,
 # analytic mean in very large tilt where underflow-safe formula matters.
 if k<1e-3:return .5-k/12+k**3/720
 if k>100:return 1/k
 v=w*np.exp(-k*t);return (v@t)/v.sum()
def reconstruct(L,R):
 N=L+R
 if N==0:return 0.,0.,False
 flip=R>L;y=min(L,R)/N
 if y==0:return N,np.inf,flip
 K=brentq(lambda k:mean(k)-y,0,1/y,xtol=1e-12)
 return N,K,flip
esc=0.;escx=0.;work=0.;nsteps=int(s[2])
for step in range(nsteps):
 for half in range(2):
  for ray in range(na):
   dz=drift[int(step>=nsteps//2),ray]/nsteps
   m=M[ray];y=np.zeros_like(m);delta=np.expm1(dz)
   pre=edges+np.expm1(-dz)*(1/b+edges)
   work+=delta*(m.sum()/b+np.sum(m* np.c_[edges[:-1],edges[1:]]))
   for i,(L,R) in enumerate(m):
    N,K,flip=reconstruct(L,R)
    if N==0:continue
    l,r=edges[i:i+2];width=r-l
    if not np.isfinite(K):
     x0=r if flip else l;xx=x0+delta*(1/b+x0)
     if xx<edges[0] or xx>edges[-1]:esc+=N;escx+=N*xx;continue
     j=min(np.searchsorted(edges,xx,side='right')-1,nc-1);rr=(xx-edges[j])/(edges[j+1]-edges[j])
     y[j]+=N*np.array([1-rr,rr]);continue
    # Integrate the reconstructed normalized density on preimage intervals
    # directly; Gauss integration evaluates both target hat weights.
    norm=1 if K<1e-12 else -np.expm1(-K)/K
    split=np.r_[-np.inf,pre,np.inf]
    for j,(a0,b0) in enumerate(zip(split[:-1],split[1:])):
     u=max(0.,(a0-l)/width);v=min(1.,(b0-l)/width)
     if v<=u:continue
     u0=u+(v-u)*t;xx=l+width*u0;xx+=delta*(1/b+xx)
     ww=N*(v-u)*w*np.exp(-K*(1-u0 if flip else u0))/norm
     if j==0 or j==nc+1:esc+=ww.sum();escx+=ww@xx;continue
     j-=1;rr=(xx-edges[j])/(edges[j+1]-edges[j]);y[j]+=[ww@(1-rr),ww@rr]
   M[ray]=y
actual=np.genfromtxt(out/'drift_only/full.tsv',names=True,delimiter='\t')
obs=np.stack([actual['left_mass'],actual['right_mass']],axis=-1).reshape(M.shape)
hist=np.genfromtxt(out/'drift_only/history.tsv',names=True,delimiter='\t')
err=float(np.sum(abs(obs-M))/N0);esc_err=float(abs(hist['escape_mass'][-1]-esc)/N0)
xerr=float(abs(hist['escape_x'][-1]-escx)/(N0*extent));workerr=float(abs(hist['work_x'][-1]-work)/(N0*extent))
assert max(err,esc_err,xerr,workerr)<2e-10,(err,esc_err,xerr,workerr)
r=dict(command=cmd,relative_endpoint_l1=err,escape_error=esc_err,escape_x_error=xerr,work_x_error=workerr,input_sha256=sha(cas),hashes={p.name:sha(p) for p in (out/'drift_only').iterdir()})
(out/'ORACLE.json').write_text(json.dumps(r,indent=2)+'\n');print(r,flush=True)

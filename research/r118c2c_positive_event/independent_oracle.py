"""Independent high precision pair and frequency-remap oracles.
No native pair formula or detuning overlap routines reused."""
import argparse,pathlib,sys,hashlib,json,subprocess
import numpy as np
import mpmath as mp
from scipy.integrate import solve_ivp
from scipy.constants import h,c
P=pathlib.Path
p=argparse.ArgumentParser();p.add_argument('--binary',type=P,required=True);p.add_argument('--final',type=P,required=True);p.add_argument('--out',type=P,required=True);a=p.parse_args()
root=a.out.resolve();root.mkdir(exist_ok=False);exe=a.binary.resolve();sha=lambda p:hashlib.sha256(P(p).read_bytes()).hexdigest()
mp.mp.dps=80
pair=[]
for i,(f0,f1,dt) in enumerate([(1.,0.,1e-9),(1.,0.,.2),(1.,0.,10.),(0.,1e3,100.),(1e-18,1e-18,1e9),(1e3,1e-20,1e9),(0.,0.,1e9),(1/9,1/4,1e9)]):
 gp=root/f'pair_{i}.bin';case=root/f'pair_{i}.txt';dest=root/f'pair_{i}'
 # Two source states with one ordinate. Independent synthetic event.
 g=[2.,3.];z=[.1,.2];W=.05
 with gp.open('wb') as f:
  f.write(b'RECPOS01');np.array([2,1,1],dtype='<u4').tofile(f);np.array([0.,0.,1.,1.],dtype='<f8').tofile(f)
  np.array([[g[0],g[0]*z[0],1e-27],[g[1],g[1]*z[1],1.1e-27]],dtype='<f8').tofile(f)
  np.array([0,1],dtype='<u4').tofile(f);np.array([W],dtype='<f8').tofile(f)
 case.write_text(f'rec_positive_case_v1\n{dt:.17g} 1\n1\n{f0:.17g} {f1:.17g}\n0\n')
 cmd=[str(exe),str(gp),str(case),str(dest)];subprocess.run(cmd,check=True,capture_output=True)
 s=np.genfromtxt(dest/'state.tsv',names=True,delimiter='\t');obs=s['final_mass']
 x,y=mp.mpf(f0)*mp.mpf(g[0]),mp.mpf(f1)*mp.mpf(g[1]);m=x+y
 if m==0:ref=np.zeros(2)
 else:
  # 80-digit matrix exponential of projectivized system, shifted
  # by its trace plus discriminant to avoid huge exponentiation.
  aa=mp.mpf(W)/(mp.mpf(g[1])*mp.mpf(z[1]));bb=mp.mpf(W)/(mp.mpf(g[0])*mp.mpf(z[0]))
  B=mp.matrix([[aa*(1+m/g[0]),aa],[bb,bb*(1+m/g[1])]])
  eigen=mp.eig(B,left=False,right=False);shift=max(eigen)
  yv=mp.expm((B-shift*mp.eye(2))*mp.mpf(dt))*mp.matrix([x,y])
  ref=np.array([float(m*yv[j]/sum(yv)) for j in range(2)])
 err=float(np.sum(abs(obs-ref))/max(float(m),1e-300))
 assert err<2e-12,(i,obs,ref,err)
 q=dict(case=i,initial=[f0,f1],dt=dt,relative_l1=err,command=cmd,hashes={p.name:sha(p) for p in dest.iterdir()})
 if dt<11 and m>0:
  def rhs(t,x):
   f=x/g;flux=W*((1+f[0])*f[1]/z[1]-f[0]*(1+f[1])/z[0]);return [flux,-flux]
  ode=solve_ivp(rhs,(0,dt),[f0*g[0],f1*g[1]],method='DOP853',rtol=1e-12,atol=1e-15)
  q['dop853_relative_l1']=float(np.sum(abs(obs-ode.y[:,-1]))/float(m));assert q['dop853_relative_l1']<1e-11
 pair.append(q)
# Drift-only: reuse actual live input but zero physical collision time.
# 50/80 digit arithmetic is unnecessary for the mesh oracle: longdouble
# on normalized absolute frequency avoids catastrophic subtraction.
base=P(a.final)/'live_time_8.txt';token=base.read_text().split()
assert token[0]=='rec_positive_case_v1';token[1]='0'
case=root/'drift_only.txt';case.write_text(' '.join(token)+'\n')
rec=json.loads((a.final/'RESULTS.json').read_text());r=next(x for x in rec['cases'] if x['case']=='live_time_8')
gp=P(r['command'][1]);dest=root/'drift_only';cmd=[str(exe),str(gp),str(case),str(dest)];subprocess.run(cmd,check=True,capture_output=True)
with gp.open('rb') as f:
 assert f.read(8)==b'RECPOS01';n,na,nb=np.fromfile(f,dtype='<u4',count=3)
 dirs=np.fromfile(f,dtype='<f8',count=4*na).reshape(na,4)
 mode=np.fromfile(f,dtype='<f8',count=3*n).reshape(n,3)
k0=3;clock=np.array(token[k0:k0+na],float);k0+=na
initial=np.array(token[k0:k0+n*na],float).reshape(n,na);k0+=n*na
assert token[k0]=='1';k0+=1
nu,dnu,ext,extent=map(float,token[k0:k0+4]);ext=int(ext);k0+=4
bounds=np.array(token[k0:k0+2*n],float).reshape(n,2);k0+=2*n
idx=np.argsort(bounds[:,0]);shift=np.array(token[k0:k0+2*na],float).reshape(2,na);k0+=2*na
outside=np.array(token[k0:],float).reshape(na,2*ext)
edges=np.r_[np.linspace(-extent,-21.25,ext+1)[:-1],bounds[idx,0],21.25,np.linspace(21.25,extent,ext+1)[1:]]
# Independent quadrature in relative physical frequency y=nu/nu0.
ld=np.longdouble;v=1+ld(dnu)/ld(nu)*edges.astype(ld)
def i2(l,r):
 return (r-l)*(l*l+l*r+r*r)/3
vol=i2(v[:-1],v[1:]);fac=8*ld(np.pi)*ld(nu)**3/ld(c)**3
m=np.zeros((na,len(vol)),dtype=ld)
m[:,:ext]=outside[:,:ext]*dirs[:,3,None]*fac*vol[:ext]
m[:,-ext:]=outside[:,ext:]*dirs[:,3,None]*fac*vol[-ext:]
m[:,ext:ext+n]=(initial[idx]*mode[idx,0,None]*dirs[:,3][None,:]).T
esc=ld(0)
N0=m.sum()
for k in range(int(token[2])):
 for half in range(2):
  for j in range(na):
   d=ld(shift[int(k>=int(token[2])//2),j])/int(token[2])
   # Integrate donor phase density over preimages of target bounds.
   pre=v*np.exp(-d)
   l=np.maximum(v[:-1,None],pre[None,:-1]);u=np.minimum(v[1:,None],pre[None,1:])
   T=np.where(u>l,i2(l,u),0.)/vol[:,None]
   q=m[j]@T;esc+=m[j].sum()-q.sum();m[j]=q
actual=np.genfromtxt(dest/'full.tsv',names=True,delimiter='\t')['mass'].reshape(m.shape)
err=float(np.sum(abs(actual-m))/N0)
assert err<5e-11,(err,)
meta=dict(s.split('=',1) for s in (dest/'run.txt').read_text().splitlines() if '=' in s)
hist=np.genfromtxt(dest/'history.tsv',names=True,delimiter='\t')
escape_err=abs(float(esc)-hist['escape_mass'][-1])/float(N0)
assert escape_err<5e-11 and float(meta['max_core_number_defect'])<2e-12
# Independent cumulative number across COM faces, native action zero.
ncom0=float(np.sum(initial*mode[:,0,None]*dirs[:,3][None,:]));ncom1=float(m[:,ext:ext+n].sum())
ledger=float(meta['red_in'])+float(meta['blue_in'])-float(meta['red_out'])-float(meta['blue_out'])
assert abs(ncom1-ncom0-ledger)/float(N0)<5e-11
drift=dict(command=cmd,relative_l1=err,escape_defect=float(escape_err),core_balance_relative=abs(ncom1-ncom0-ledger)/float(N0),hashes={p.name:sha(p) for p in dest.iterdir()})
# Independent normal-frame photon momentum moment for native normal-clock
# graph; weights are the normal-slice masses. Not an independent atom event.
r=next(x for x in rec['cases'] if x['case']=='normal_clock');d=P(r['command'][3]);state=np.genfromtxt(d/'state.tsv',names=True,delimiter='\t')
beta=np.array([.3,.1,0.]);gamma=1/np.sqrt(1-beta@beta)
bd=dirs[:,:3]@beta;pH=mode[:,2,None]
pn0=gamma*pH*(1+bd[None,:]);pnv=pH[:,:,None]*(dirs[None,:,:3]+((gamma-1)/(beta@beta)*bd+gamma)[None,:,None]*beta)
q=state['mass_action'].reshape(n,na)
qn=np.r_[np.sum(q*pn0),np.sum(q[:,:,None]*pnv,axis=(0,1))]
qh=np.array([r['run'][f'action_q_{i}'] for i in range(4)])
boost=np.r_[gamma*(qh[0]+beta@qh[1:]),qh[1:]+((gamma-1)*(beta@qh[1:])/(beta@beta)+gamma*qh[0])*beta]
force_gap=float(np.max(abs(qn-boost))/np.sum(abs(q*pn0)));assert force_gap<2e-12
out=dict(pair=pair,drift=drift,normal_force_relative_gap=force_gap)
(root/'ORACLE.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
print('pair max',max(q['relative_l1'] for q in pair),'drift',drift,'force',force_gap,flush=True)

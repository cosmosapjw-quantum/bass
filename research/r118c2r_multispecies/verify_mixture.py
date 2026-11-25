import hashlib,json,sys,gzip
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D.parent/'r118c2p_massive_feedback'))
from massive import Species,OG0,ON0,OM,OL,H0,TNU_EV,C,SIG
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
sources=json.loads((D/'SOURCES.json').read_text())
for p,h in sources.items():assert sha(p)==h
E=np.array([np.diag([1.,-1.,0.])/np.sqrt(2),np.diag([-1.,-1.,2.])/np.sqrt(6),
 [[0,1/np.sqrt(2),0],[1/np.sqrt(2),0,0],[0,0,0]],
 [[0,0,1/np.sqrt(2)],[0,0,0],[1/np.sqrt(2),0,0]],
 [[0,0,0],[0,0,1/np.sqrt(2)],[0,1/np.sqrt(2),0]]])
def tensor(x):return np.einsum('...a,aij->...ij',x,E)
def comm(a,b):return a@b-b@a
def inv(a,b):return np.sum(comm(tensor(a),tensor(b))**2,axis=(-1,-2))/2
cases={'misaligned':([.001,.05],[[0,1,0,0,0],[0,0,.6,.8,0]]),'equal_mass':([.01,.01],[[0,1,0,0,0],[0,0,.6,.8,0]]),'aligned':([.001,.05],[[0,1,0,0,0],[0,.7,0,0,0]])}
results={};native_hash={};series={}
for history in ('rei_q256','bass_cross'):
 raw=np.genfromtxt(D/(history+'.csv'),names=True,delimiter=',')
 u=raw['u'];ne=raw['ne_m3'];assert u[0]==0 and np.all(np.diff(u)>0)
 for case,(m,J) in cases.items():
  J=np.array(J,float);sp=[Species(m0,256) for m0 in m]
  cold=OM+ON0-sum(s.moments(1.)[0]/2 for s in sp)
  def moment(t,b):
   a=np.exp(t)/21
   r,p,chi,dc=np.array([s.moments(a) for s in sp]).T/2
   den=cold*a+OG0+r.sum();P=OG0/3+p.sum()
   total=den+OL*a**4
   dH=-1.5*(den+P)/total
   pi=chi@(J-b)/total
   loss=-dc@np.sum((J-b)**2,axis=1)
   mem=chi@np.sum((J-b)**2,axis=1)
   return OG0/total,dH,pi,mem,loss,H0*np.sqrt(total/a**4),chi,dc,total
  def rhs(t,v):
   S,A,B,b=v[:20].reshape(4,5);og,dH,pi,mem,loss,H,*_=moment(t,b)
   k=C*SIG*np.interp(t,u,ne)/H
   ds=-(3+dH)*S+.4*og*A+3*pi
   da=-4*S-k*(.9*A+.4*B);db=-k*(.15*A+.4*B)
   dloss=20*(S@S)/og+k*(1.8*(A@A)+1.6*(A@B)+32/15*(B@B))+30*loss/OG0
   return np.r_[ds,da,db,S,dloss]
  def L(t,v):
   S,A,B,b=v[:20].reshape(4,5);og,_,_,mem,*_=moment(t,b)
   return 10*(S@S)/og+A@A+8/3*(B@B)+30*mem/OG0
  sol=solve_ivp(rhs,(u[0],u[-1]),np.zeros(21),method='DOP853',rtol=2e-11,atol=2e-14,max_step=.002,dense_output=True)
  assert sol.success
  ts=np.linspace(u[0],u[-1],2049);v=sol.sol(ts).T;pi=np.array([moment(t,b)[2] for t,b in zip(ts,v[:,15:20])])
  cc=inv(v[:,:5],pi)
  norm=np.sum(v[:,:5]**2,axis=1)*np.sum(pi**2,axis=1);cn=np.divide(cc,norm,out=np.zeros_like(cc),where=norm>0)
  assert np.max(cn)<=1+1e-12
  ls=np.array([L(t,x) for t,x in zip(ts,v)]);balance=abs(ls[-1]+v[-1,20]-ls[0])/ls[0]
  assert balance<1e-8 and max(np.diff(ls))/ls[0]<1e-10
  errors=[];natives=[]
  for n in (512,1024,2048):
   name=f'{history}_{case}_{n}.csv';p=D/name
   if p.exists():native_hash[name]=sha(p)
   else:
    p=p.with_suffix('.csv.gz')
    with gzip.open(p,'rb') as z:native_hash[name]=hashlib.file_digest(z,'sha256').hexdigest()
   r=np.genfromtxt(p,names=True,delimiter=',');assert len(r)==n+1
   ys=np.column_stack([r[f'{k}{i}'] for k in ('S','A','B','beta') for i in range(5)])
   err=float(np.max(abs(ys[-1]-v[-1,:20])));errors.append(err)
   npv=np.column_stack([r[f'Pi{i}'] for i in range(5)])
   npinv=inv(ys[:,:5],npv)
   assert np.max(abs(npinv-r['C']))<1e-25+1e-12*np.max(r['C'])
   natives.append(dict(n=n,endpoint_error=err,max_C=float(max(r['C'])),balance=float(abs(r['L'][-1]+r['loss'][-1]-r['L'][0])/r['L'][0])))
  assert errors[-1]<2e-8 and errors[-1]<errors[0]
  if case!='misaligned':assert max(cc)<1e-32 and natives[-1]['max_C']<1e-28
  onset=[]
  if case=='misaligned':
   # Pi'=sum weights' J since beta'=0 at u=0
   og,dH,P0,_,_,_,chi,dc,total=moment(0,np.zeros(5))
   P1=(dc-(4+2*dH)*chi)@J/total
   target=1.5*comm(tensor(P0),tensor(P1))
   coeff=float(.5*np.sum(target*target));assert coeff>0
   ss=solve_ivp(rhs,(0,.01),np.zeros(21),method='DOP853',rtol=1e-12,atol=1e-20,max_step=1e-4,dense_output=True);assert ss.success
   for t in (1e-2,1e-3,1e-4):
    z=ss.sol(t);p=moment(t,z[15:20])[2];c=comm(tensor(z[:5]),tensor(p))
    er=float(np.linalg.norm(c/t**2-target)/np.linalg.norm(target))
    onset.append(dict(u=t,relative=er,C_over_u4=float(.5*np.sum(c*c)/t**4),analytic_coeff=coeff))
   assert onset[-1]['relative']<1e-3 and onset[-1]['relative']<onset[0]['relative']
  row=dict(history=history,case=case,masses=m,initial_memories=J.tolist(),S_end=v[-1,:5].tolist(),B_end=v[-1,10:15].tolist(),Pi_end=pi[-1].tolist(),max_C=float(max(cc)),C_end=float(cc[-1]),max_normalized_C=float(max(cn)),C_normalized_end=float(cn[-1]),balance=float(balance),native=natives,onset=onset,orders=np.log2(np.array(errors[:-1])/np.array(errors[1:])).tolist())
  results[history+'_'+case]=row;series[history+'_'+case]=np.column_stack([ts,v,pi,cc,cn,ls])
  print(history,case,'Cmax',row['max_C'],'Cnormmax',row['max_normalized_C'],'end norm',row['C_normalized_end'],'Bnorm',np.linalg.norm(row['B_end']),'native gaps',errors,'balance',balance,'onset',onset[-1] if onset else None,flush=True)
np.savez_compressed(D/'SERIES.npz',**series)
out=dict(status='PASS_SCOPED_MULTISPECIES_NATIVE_GEOMETRY_STAGE',scope='linear perturbation FD source-only initial shear zero, native actual geometry stage sampled on prescribed FLRW background with epsilon=1e-5, exact input knots, not full nonlinear geometry owner',cases=results,sources=sources,native_csv_sha256=native_hash)
(D/'RESULTS.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')

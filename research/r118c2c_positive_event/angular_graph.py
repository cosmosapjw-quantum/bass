"""Positive discrete ordinates from source density, not signed harmonics.
Symmetric diagonal scaling fixes off-diagonal angular monopoles; same-cell
uses a global transport moment normalization (P1-1), not a raw gain integral.
"""
import argparse,sys,pathlib,json,hashlib,time
import numpy as np
from scipy.special import eval_legendre
from scipy.integrate import trapezoid
from scipy.linalg import norm
from scipy.integrate import lebedev_rule
P=pathlib.Path
p=argparse.ArgumentParser();p.add_argument('--source',type=P,required=True);p.add_argument('--out',type=P,required=True);p.add_argument('--orders',nargs='+',type=int,default=[7,11,17,29,53]);p.add_argument('--export',nargs='+',type=int,default=[7,11,17]);args=p.parse_args()
root=args.out.resolve();root.mkdir(exist_ok=False,parents=True)
src=np.load(args.source/'SOURCE_MEASURE.npz',allow_pickle=False)
r=json.loads((args.source/'SOURCE_RESULTS.json').read_text());rby={(x['i'],x['j']):x for x in r['pairs']}
g=src['mode_measure'];pi=src['equilibrium_weight'];pairs=src['pairs'];offset=src['offset']
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def symmetric_scale(K,w):
 # Matrix symmetry is never broken by the scaling; solve d*(K@(w*d))=1.
 z=K@w
 if np.any(z<=0):raise ValueError('zero angular support')
 d=1/np.sqrt(z)
 for it in range(2000):
  row=d*(K@(w*d))
  err=np.max(abs(row-1))
  if err<3e-13:break
  if not np.all(np.isfinite(row)) or np.any(row<=0):raise ValueError('invalid symmetric scaling')
  d/=np.sqrt(row)
 else:raise ValueError(('symmetric scaling nonconvergence',err))
 return K*d[:,None]*d[None,:],float(err),it+1,float(np.max(abs(d-1)))
def graph(order):
 t=time.monotonic();d,w=lebedev_rule(order);d=d.T;w=w/w.sum()
 if np.any(w<=0):raise ValueError('nonpositive angular rule')
 a=len(w);dot=np.clip(d@d.T,-1,1);np.fill_diagonal(dot,1.)
 # Evaluate same angle-pair arguments identically in both directions.
 dot=(dot+dot.T)/2; ww=w[:,None]*w[None,:]
 pl=np.array([eval_legendre(l,dot) for l in range(25)])
 # l1..4 directional eigenfunction residual (normalized source scales).
 # e_z, P_l(e_z), and rotating orientation probe e_x.
 yz=np.array([eval_legendre(l,d[:,2]) for l in range(1,5)])
 yx=np.array([eval_legendre(l,d[:,0]) for l in range(1,5)])
 W=[];details=[];st=0.;tot=np.zeros(2);norms=[]
 for k,(i,j) in enumerate(pairs):
  sl=slice(offset[k],offset[k+1]);mu=src['mu'][sl];q=src['density'][sl];aw=src['weight'][sl];record=rby[i,j]
  I=float(aw@q);assert I>0
  # Piecewise linear interpolation of the actual positive source density.
  # At the measure-zero endpoints use nearest sampled positive value;
  # same-cell coincident angles have zero transfer and are removed.
  B=np.interp(dot,mu,q)/I
  assert np.min(B)>=0 and np.all(np.isfinite(B))
  raw_mono=float(np.sum(ww*B))
  if i!=j:
   B,err,its,scale=symmetric_scale(B,w)
   Wk=I*ww*B
   mom=np.einsum('lab,ab->l',pl,Wk)/I
   ref=np.array(record['direct_moments'])/I
   eig=0.
   for Y in (yz,yx):
    conv=B@(w[:,None]*Y.T)
    eig=max(eig,float(np.max(abs(conv-Y.T*ref[1:5]))))
   detail=dict(i=int(i),j=int(j),type='pair',raw_mono_error=abs(raw_mono-1),row_defect=err,scaling_iterations=its,max_scaling_change=scale,moment_max=float(np.max(abs(mom-ref))),moment_l1_l4=float(np.max(abs(mom[1:5]-ref[1:5]))),moment_l1=float(abs(mom[1]-ref[1])),eigen_l1_l4=eig,source_scale=I)
   tot[0]+=I;norms.append((I,detail['moment_l1_l4']))
  else:
   # R=(1-mu)K/pi. Restore gain only off coincident angles.
   # Normalize the total angular first transport moment to source R integral.
   np.fill_diagonal(B,0.)
   mass=float(np.sum(ww*B))
   if mass<=0:raise ValueError('zero same-cell transport')
   B/=mass
   K=np.divide(B,1-dot,out=np.zeros_like(B),where=(1-dot)>1e-14)
   Wk=pi[i]*I*ww*K
   mom=np.einsum('lab,ab->l',pl-1,Wk)/(pi[i]*I)
   ref=np.array(record['direct_moments'])/I
   eig=0.
   for Y in (yz,yx):
    conv=K@(w[:,None]*Y.T)-(K@w)[:,None]*Y.T
    eig=max(eig,float(np.max(abs(conv-Y.T*ref[1:5]))))
   detail=dict(i=int(i),j=int(j),type='same',raw_transport_error=abs(mass-1),moment_max=float(np.max(abs(mom-ref))),moment_l1_l4=float(np.max(abs(mom[1:5]-ref[1:5]))),moment_l1=float(abs(mom[1]-ref[1])),eigen_l1_l4=eig,source_scale=I)
   tot[1]+=I
  assert np.all(np.isfinite(Wk)) and np.min(Wk)>=0
  assert np.max(abs(Wk-Wk.T))<=2e-15*np.max(Wk)
  Wk=(Wk+Wk.T)/2
  details.append(detail)
  if order in args.export:W.append(Wk)
 if order in args.export:
  dest=root/f'graph_o{order}.bin'
  # Little-endian typed binary: header; counts; angle dir,weight; mode/pi/p;
  # blocks in source pair order, full row-major symmetric angular matrix.
  with dest.open('wb') as f:
   f.write(b'RECPOS01');np.array([len(g),a,len(pairs)],dtype='<u4').tofile(f)
   np.asarray(np.c_[d,w],dtype='<f8').tofile(f)
   np.asarray(np.c_[g,pi,src['momentum_scale']],dtype='<f8').tofile(f)
   for (i,j),k in zip(pairs,W):
    np.asarray([i,j],dtype='<u4').tofile(f);np.asarray(k,dtype='<f8',order='C').tofile(f)
  digest=sha(dest)
 else:digest=None
 pair=[v for v in details if v['type']=='pair'];same=[v for v in details if v['type']=='same']
 report=dict(order=order,angles=a,graph_sha256=digest,source_measure_sha256=sha(args.source/'SOURCE_MEASURE.npz'),wall_s=time.monotonic()-t,max_row_defect=max(v['row_defect'] for v in pair),max_scaling_iterations=max(v['scaling_iterations'] for v in pair),max_pair_l1_l4=max(v['moment_l1_l4'] for v in pair),weighted_pair_l1_l4=sum(x*y for x,y in norms)/sum(x for x,y in norms),max_same_l1_l4=max(v['moment_l1_l4'] for v in same),weighted_same_l1_l4=sum(v['source_scale']*v['moment_l1_l4'] for v in same)/tot[1],pair_max_l1=max(v['moment_l1'] for v in pair),same_max_l1=max(v['moment_l1'] for v in same),max_pair_eigen_l1_l4=max(v['eigen_l1_l4'] for v in pair),max_same_eigen_l1_l4=max(v['eigen_l1_l4'] for v in same),details=details)
 (root/f'GRAPH_o{order}.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
 print({k:v for k,v in report.items() if k!='details'},flush=True)
 return report
reports=[]
for order in args.orders:
 try:reports.append({k:v for k,v in graph(order).items() if k!='details'})
 except Exception as e:reports.append(dict(order=order,error=repr(e)));print('FAILED',order,repr(e),flush=True)
(root/'GRAPH_RESULTS.json').write_text(json.dumps(reports,indent=2,allow_nan=False)+'\n')

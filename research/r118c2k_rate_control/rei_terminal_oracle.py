"""Independent continuum integration of recovered fixed-q two-moment closure.
This tests the selected bounded-exponential closure, not the unique spectrum.
Validate against original C2J checkpoint's actually reported native rates.
"""
import argparse,json,math,hashlib
from pathlib import Path
import numpy as np
from scipy.optimize import brentq
from numpy.polynomial.legendre import leggauss
p=argparse.ArgumentParser();p.add_argument('--segments',type=Path,required=True);p.add_argument('--old',type=Path,required=True);p.add_argument('--bass',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
pars=[(13.60,.4298,5.475e4,32.88,2.963,0.,0.,0.),(24.59,13.61,949.2,1.469,3.188,2.039,.4434,2.136),(54.42,1.720,1.369e4,32.88,2.963,0.,0.,0.)]
bind=np.array([13.598434599702,24.587389011,54.41776]);C=2.99792458e10
def sig(E):
 out=[]
 for eth,e0,s0,ya,p,yw,y0,y1 in pars:
  x=E/e0-y0;y=np.sqrt(x*x+y1*y1)
  out.append(np.where(E>=eth,s0*((x-1)**2+yw*yw)*y**(p/2-5.5)*(1+np.sqrt(y/ya))**(-p)*1e-18,0.))
 return np.array(out)
def mean(b):
 if b<1e-3:return .5-b/12+b**3/720-b**5/30240
 if b>700:return 1/b
 return 1/b-1/np.expm1(b)
def quadr(n,u,lo,hi,scale,order):
 if lo==hi:return np.array([lo*scale]),np.array([n])
 lower=u-lo*n;upper=hi*n-u
 if lower<=upper:m=lo+lower/n
 else:m=hi-upper/n
 if m<lo or m>hi:raise ValueError('support')
 if m==lo or m==hi:return np.array([m*scale]),np.array([n])
 width=hi-lo;flip=m>(hi+lo)/2
 d=(hi-m if flip else m-lo)/width
 b=0. if d==.5 else brentq(lambda b:mean(b)-d,0,max(2.,2/d),xtol=1e-14)
 x,w=leggauss(order)
 # distance t in [0,1] from dominant endpoint. Integrate y=b*t
 # in steep cells, truncating only exponentially tiny tails.
 norm=max(1.,b);end=min(norm,60.) if b>1 else 1.
 cuts=[0.,end]
 for edge in [13.60,24.59,54.42]:
  t=(hi-edge/scale)/width if flip else (edge/scale-lo)/width
  y=t*norm
  if 0<y<end:cuts.append(y)
 cuts.extend(float(k) for k in np.arange(2.,end,2.))
 cuts=sorted(set(cuts));ys=[];ws=[]
 for l,r in zip(cuts[:-1],cuts[1:]):
  y=(l+r)/2+(r-l)*x/2
  ys.extend(y/norm);ws.extend((r-l)*w/2*np.exp(-b*y/norm))
 t=np.array(ys);ww=np.array(ws);q=hi-width*t if flip else lo+width*t
 ww=n*ww/ww.sum()
 assert abs(ww@q-u)<2e-12*u
 return q*scale,ww
def calc(check,nh,order):
 lines=check.read_text().splitlines();assert lines[0]=='AXBI_CHECKPOINT_V4'
 x=np.fromstring(lines[1],sep=' ');scale=(1/21)/x[0]
 n,u,lo,hi=[np.fromstring(lines[i],sep=' ') for i in (4,5,6,7)]
 pn,pu=[np.fromstring(lines[i],sep=' ') for i in (8,9)]
 E=[];N=[]
 for ni,ui,l,r in zip(n,u,lo,hi):
  if ni==0:continue
  e,w=quadr(ni,ui,l,r,scale,order);E.extend(e);N.extend(w)
 E=np.array(E);N=np.array(N);s=sig(E)
 return dict(gamma=(C*nh*(s@N)).tolist(),heat=(C*nh*((s*(E[None,:]-bind[:,None]))@N)).tolist(),active_N=float(N.sum()),active_U=float(E@N),passive_N=float(pn.sum()),passive_U=float(pu.sum()*scale),z=float(1/x[0]-1))
rows=[]
for label,root in [('q16',a.segments/'extend16'),('q32',a.segments/'resume32'),('q64',a.segments/'fresh64'),('prior_native_check',a.old/'long32')]:
 # read only final row, avoiding dtype overhead on huge history.
 with (root/'history.csv').open() as f:head=f.readline().strip().split(',')
 import subprocess
 last=subprocess.check_output(['tail','-1',str(root/'history.csv')],text=True).strip().split(',')
 h=dict(zip(head,last));nh=float(h['nH_proper_cm3'])
 q=calc(root/'checkpoint.txt',nh,32);r=calc(root/'checkpoint.txt',nh,64)
 gap=max(abs(np.array(q['gamma'])/np.array(r['gamma'])-1));assert gap<1e-9
 if label=='prior_native_check':
  want=np.array([float(h[k]) for k in ('Gamma_HI_per_s','Gamma_HeI_per_s','Gamma_HeII_per_s')]);r['native_relative']=float(max(abs(np.array(r['gamma'])/want-1)))
  assert r['native_relative']<1e-8
 r.update(case=label,quadrature_gap=float(gap),checkpoint_sha256=hashlib.sha256((root/'checkpoint.txt').read_bytes()).hexdigest())
 rows.append(r);print(label,r)
t=json.loads(a.bass.read_text());b=next(x for x in t['cases'] if '_n32768_' in x['case'])
a.out.write_text(json.dumps(dict(scope='fixed-q terminal closure independently reconstructed; GL32/64; old native endpoint cross-check',cases=rows,bass=b),indent=2)+'\n')

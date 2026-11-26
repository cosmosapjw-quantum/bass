"""Signed native response probe generator and analysis."""
from pathlib import Path
import numpy as np,json,sys
from linear_response import D,solve,CLOCK,memory
MASSES={'base':[.001,.006,.05],'dispersed':[.0001,.004,.1]}
def prepare():
 for label,m in MASSES.items():
  for j in range(4):
   for sign in [1,-1]:
    c=np.zeros((4,5));c[j,0]=sign*.005
    np.savetxt(D/f'{label}_{j}_{sign}.ctrl',np.r_[m,c.ravel()][None,:],fmt='%.17e')
 # Independent smaller amplitude parity case on the prior orthogonal control.
 c=np.loadtxt(D.parent/'r118c3h_reachability/orthogonal125.controls')*.25
 for sign in [1,-1]:np.savetxt(D/f'parity_{sign}.ctrl',np.r_[MASSES['base'],(sign*c).ravel()][None,:],fmt='%.17e')
def read(label):
 p=D/(label+'.geom');ls=p.read_text().splitlines();assert ls[-1].startswith('gauss=')
 return np.genfromtxt(ls[:-1],names=True,delimiter=','),float(ls[-1].split('=')[1])
def analyze():
 clock=np.genfromtxt(CLOCK,names=True,delimiter=',');rows={}
 for name,m in MASSES.items():
  mode=[];errors=[];gauss=[]
  ref=np.load(D/f'linear_{name}.npz')
  for j in range(4):
   a,g=read(f'{name}_{j}_1');b,k=read(f'{name}_{j}_-1');assert np.array_equal(a['u'],b['u'])
   v=(a['S0']-b['S0'])/.01;expected=np.interp(a['u'],ref['u'],ref['s'][:,j]);err=np.linalg.norm(v-expected)/np.linalg.norm(expected)
   cross=max(np.linalg.norm((a[f'S{i}']-b[f'S{i}'])/.01) for i in range(1,5))/np.linalg.norm(v)
   mode.append(v);errors.append(dict(mode=j,relative=float(err),cross=float(cross)));gauss.extend([abs(g),abs(k)])
  M=memory(a['u'],np.array(mode).T,(a['h']+b['h'])/2,clock);sv=np.linalg.svd(M,compute_uv=False)
  rows[name]=dict(errors=errors,sv=sv.tolist(),ratio=float(sv[2]/sv[0]),gauss_max=max(gauss),scope='native finite-amplitude signed response; tiny skew singular value susceptible to finite differencing and interpolation')
 def B(label):
  a=np.genfromtxt(D/(label+'.csv'),names=True,delimiter=',');z=a['ell']==3;return a['re'][z]+1j*a['im'][z]
 eps=.003125;E=(B('parity_1')+B('parity_-1'))/(2*eps**2);O=(B('parity_1')-B('parity_-1'))/(2*eps**3)
 cos=np.vdot(E,O).real/(np.linalg.norm(E)*np.linalg.norm(O))
 rows['parity']=dict(eps=eps,even_norm=float(np.linalg.norm(E)),odd_norm=float(np.linalg.norm(O)),real_cosine=float(cos),orthogonal_fraction=float(np.sqrt(max(0,1-cos*cos))))
 (D/'NATIVE.json').write_text(json.dumps(rows,indent=2)+'\n');print(rows,flush=True)
if __name__=='__main__':
 if sys.argv[1]=='prepare':prepare()
 else:analyze()

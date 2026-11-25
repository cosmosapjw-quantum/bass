"""Independent full angular-matrix frequency-domain oracle for two frozen
Thomson half cells of the manufactured FLRW tracer. No Rust source solve,
no Mellin closure in the oracle. Directly solve 9*N-dimensional system
for the occupation on 384 frequency quadrature nodes. Also test the raw log
moments by independent polynomial input columns. All frequencies are material
frame, in units k_B T_ref/h; centered isotropic geometry in between.
"""
import sys, pathlib, json, csv, hashlib, numpy as np, scipy.linalg as la
from scipy.special import gamma,zeta
from numpy.polynomial.legendre import leggauss
root=pathlib.Path(sys.argv[1]); beta=np.array([0.2,-0.1,0.05])
g=(1-beta@beta)**-.5; k=g*g/(1+g); alpha=1-1/np.sqrt(2)
I=np.eye(3); G=3/(8*np.pi)
results=[]
for scheme in ('backward-euler','sdirk2'):
 p=root/scheme/'spectral_normal.tsv'
 rows=list(csv.DictReader(p.open(),delimiter='\t'))
 e=np.array([[float(r['e_'+i]) for i in 'xyz'] for r in rows]);w=np.array([float(r['weight']) for r in rows])
 d=g*(1-e@beta); ep=(e+(k*(e@beta)-g)[:,None]*beta)/d[:,None]
 P=I-ep[:,:,None]*ep[:,None,:];wu=w/d**2
 A=G*np.einsum('i,ijk->jk',wu,P)
 vals,vecs=la.eigh(A);N=(vecs*vals**-.5)@vecs.T
 gp=P@N
 # Flatten full 3x3 tensor, no packed source reduction.
 L=np.zeros((len(e)*9,len(e)*9))
 for i in range(len(e)):
    block=G*d[i]*np.kron(gp[i],gp[i])
    for j in range(len(e)):
        L[i*9:(i+1)*9,j*9:(j+1)*9]=wu[j]*block
    L[i*9:(i+1)*9,i*9:(i+1)*9]-=d[i]*np.eye(9)
 h=.15 if scheme=='backward-euler' else alpha*.15
 fac=la.lu_factor(np.eye(len(L))-h*L)
 def cell(a):
    b=la.lu_solve(fac,a)
    return b if scheme=='backward-euler' else la.lu_solve(fac,a+(1+np.sqrt(2))*(b-a))
 def solve(a):return cell(cell(a))
 # Direct solve across material-frame frequencies, with exact Planck input
 # at Doppler-shifted temperatures. Quadrature is in log(x).
 t,wt=leggauss(384);ell=14.5*t-7.5; x=np.exp(ell); wx=14.5*wt
 z=x[None,:]/d[:,None]
 f=np.exp(-z)/(-np.expm1(-z))
 occ=(P.reshape(-1,9)[:,:,None]*.5*f[:,None,:]).reshape(len(L),len(x))
 out=solve(occ).reshape(len(e),3,3,len(x))
 inv=I+(k*(-beta)+g*e)[:,:,None]*(-beta)[None,None,:]
 def back(v):return inv@v@np.swapaxes(inv,-1,-2)
 pred={}
 for pwr in [3,4]:
    material=np.einsum('ijkl,l->ijk',out,wx*x**pwr)/(gamma(pwr)*zeta(pwr))
    pred['B'+str(pwr)]=back(material)/d[:,None,None]**pwr
 ln=np.log(d)
 loginput=(.5*P[:,:,:,None]*np.stack([np.ones_like(ln),ln,ln**2],axis=1)[:,None,None,:]).reshape(len(L),3)
 raw=solve(loginput).reshape(len(e),3,3,3)
 raw=[back(raw[:,:,:,i]) for i in range(3)]
 pred['M0']=raw[0];pred['M1']=raw[1]-ln[:,None,None]*raw[0]
 pred['M2']=raw[2]-2*ln[:,None,None]*raw[1]+ln[:,None,None]**2*raw[0]
 errors={}
 for key,v in pred.items():
    idx=[(0,0),(1,1),(2,2),(0,1),(0,2),(1,2)];s=['xx','yy','zz','xy','xz','yz']
    oracle=np.stack([v[:,i,j] for i,j in idx],axis=1)
    actual=np.array([[float(r[key+'_'+ij]) for ij in s] for r in rows])
    errors[key]=float(np.max(np.abs(oracle-actual)))
    assert errors[key]<5e-10,(scheme,key,errors[key])
 results.append(dict(scheme=scheme,n_directions=len(e),dense_unknowns=len(L),frequency_nodes=len(x),frequency_log_bounds=[-22,7],input_sha256=hashlib.sha256((root/scheme/'spectral_normal.tsv').read_bytes()).hexdigest(),errors=errors))
print(json.dumps(results,indent=2))
(root/'FREQUENCY_ORACLE.json').write_text(json.dumps(results,indent=2)+'\n')

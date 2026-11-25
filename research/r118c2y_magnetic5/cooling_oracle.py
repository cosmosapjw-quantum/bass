"""Direct birth-frame integral on actual accepted live geometry."""
import numpy as np,json,hashlib
from pathlib import Path
from scipy.linalg import expm
from numpy.polynomial.legendre import leggauss
D=Path(__file__).resolve().parent;H=Path('/home/cosmosapjw/Downloads')
p=H/'bass_r118c2y_whole/history.csv';q=H/'bass_r118c2y_iso/history.csv'
r=np.genfromtxt(p,names=True,delimiter=',');s=np.genfromtxt(q,names=True,delimiter=',')
assert np.array_equal(r['a'],s['a'])
for k in ('T','xHII','xHeII','xHeIII','ne','J0','source'):
    assert np.array_equal(r[k],s[k]),k
a=r['a'];du=np.diff(np.log(a));am=a[:-1]*np.exp(du/2)
F=np.stack([r[f'F{i}{j}'] for i in range(3) for j in range(3)],axis=1).reshape(-1,3,3)
T=np.stack([r[f'S{i}'] for i in range(5)],axis=1)
def mat(v):
    x,y,z,p,q=v;rr=1/np.sqrt(2);t=1/np.sqrt(6)
    return np.array([[rr*x-t*y,rr*z,rr*p],[rr*z,-rr*x-t*y,rr*q],[rr*p,rr*q,2*t*y]])
fm=np.array([expm(mat(v)*h/2)@f for v,h,f in zip(T,du,F)])
birth=(s['escape'][1:]-a[:-1]/a[1:]*s['escape'][:-1])/(am/a[1:])
assert min(birth)>=0
inv=np.linalg.inv(F[-1]).T;rows=[]
for nt,np0 in ((8,16),(16,32),(32,64)):
    x,w=leggauss(nt);phi=2*np.pi*np.arange(np0)/np0;mu,t=np.meshgrid(x,phi,indexing='ij')
    n=np.stack([np.sqrt(1-mu*mu)*np.cos(t),np.sqrt(1-mu*mu)*np.sin(t),mu],axis=-1).reshape(-1,3)
    ww=np.repeat(w/2/np0,np0)
    U=0.;P=np.zeros((3,3));flux=np.zeros(3)
    for b,m,aa in zip(birth,fm,am):
        v=n@(aa/a[-1]*inv@m.T).T;e=np.linalg.norm(v,axis=1)
        U+=b*(ww@e);P+=b*np.einsum('a,ai,aj->ij',ww/e,v,v);flux+=b*(ww@v)
    pi=P-U*np.eye(3)/3;pn=np.linalg.norm(pi)
    row=dict(nmu=nt,nphi=np0,U=float(U),P=P.tolist(),pi_norm=float(pn),Pyz=float(P[1,2]),flux_norm=float(np.linalg.norm(flux)),energy_relative=float(abs(U/r['escape'][-1]-1)),pi_relative=float(abs(pn/r['cool_pi_norm'][-1]-1)))
    rows.append(row);print(row,flush=True)
assert rows[-1]['energy_relative']<1e-12 and rows[-1]['pi_relative']<1e-7
out=dict(status='SCOPED_INDEPENDENT_BIRTH_FRAME_ORACLE',source_sha=hashlib.sha256(p.read_bytes()).hexdigest(),iso_sha=hashlib.sha256(q.read_bytes()).hexdigest(),gas_history_byte_values_equal=True,rows=rows,scope='direct physical emission-angle quadrature, reconstructed accepted source increments from matched iso history, no scattering or spectral absorption')
(D/'COOLING_ORACLE.json').write_text(json.dumps(out,indent=2)+'\n')

from r118c3g_stage_driver_20261126 import *
import numpy as np
from itertools import combinations
def BASS():
 r= repos['BASS'][0]; d=folder('BASS')
 p=r/'research/r118c3c_memory_kernel/WEDGE.json';j=json.loads(p.read_text());P3=2*np.array(j['gram']);pairs=np.array(j['pairs']);i,jj=pairs.T
 E=np.zeros((5,3,3));E[0]=np.diag([1,-1,0])/np.sqrt(2);E[1]=np.diag([-1,-1,2])/np.sqrt(6)
 for k,(a,b) in enumerate(((0,1),(0,2),(1,2)),2):E[k,a,b]=E[k,b,a]=1/np.sqrt(2)
 axes=np.eye(3);L=[]
 for o in axes:
  x,y,z=o;O=np.array([[0,-z,y],[z,0,-x],[-y,x,0]])
  M=np.array([[np.trace(a@(O@b-b@O)) for b in E] for a in E]);L.append(M[i,jj])
 L=np.array(L).T;U,_,_=np.linalg.svd(L,full_matrices=False);assert np.linalg.norm(P3-(np.eye(10)-U@U.T))<1e-12
 def measure(A):
  Q,s,_=np.linalg.svd(A,full_matrices=True);assert s[-1]>1e-10
  W=Q[:,:4];n=Q[:,4];D=np.array([W[i,k]*W[jj,l]-W[i,l]*W[jj,k] for k,l in combinations(range(4),2)]).T
  assert np.linalg.norm(D.T@D-np.eye(6))<1e-12
  ev=np.linalg.eigvalsh(np.einsum('i,ijk->jk',n,E))
  sing=np.linalg.svd(P3@D,compute_uv=False)
  return dict(normal=n.tolist(),normal_eigenvalues=ev.tolist(),min_eigengap=float(np.min(np.diff(ev))),sigma_min=float(sing[-1]),projected_singular_values=sing.tolist())
 rows={}
 for name in ('small','base','large','angle','fine'):
  g=r/'research/r118c3f_four_memory'/(name+'.geom');a=np.genfromtxt(g.read_text().splitlines()[:-1],names=True,delimiter=',');S=np.array([a[f'S{k}'][0] for k in range(5)]);S/=np.linalg.norm(S)
  A=np.stack([S,np.array([0,1,0,0,0]),np.array([0,0,.6,.8,0]),np.array([0,0,0,1,0])],axis=1)
  rows[name]=measure(A)
 rows['axial_control']=measure(np.eye(5)[:,[0,2,3,4]])
 rows['triaxial_control']=measure(np.eye(5)[:,[1,2,3,4]])
 assert rows['axial_control']['sigma_min']<1e-12 and rows['triaxial_control']['sigma_min']>0.01
 write('BASS','R7.json',dict(status='DERIVED_NUMERICALLY_CHECKED_LEADING_SPAN',projector_residual=float(np.linalg.norm(P3-(np.eye(10)-U@U.T))),rows=rows,source_sha=sha(p)))
 print('BASS', {k:v['sigma_min'] for k,v in rows.items()},flush=True)
def REC():
 r=repos['REC'][0];p=r/'research/r118c2w_causal/FULL_128.npz';v=np.load(p);eta=-np.log1p(v['z']);a=eta[128]-eta[63];g=r/'research/r118c3f_directional_history/FINAL_RESULTS.json';j=json.loads(g.read_text());look=min(x['min_lookback'] for x in j['directions'].values())
 # volume overlap on partition, exact integrated q^2 dq for piecewise constant occupation
 e=np.geomspace(.1,4,129);f=1/np.expm1(np.sqrt(e[:-1]*e[1:]));rows=[]
 N=float(np.diff(e**3)@f/3)
 for shift in [.95,1.,1.05]:
  t=e*shift;L=np.maximum(e[:-1,None],t[None,:-1]);R=np.minimum(e[1:,None],t[None,1:]);M=np.maximum(0,R**3-L**3)/3;out=f@M
  lost=N-out.sum();assert lost>=-1e-13
  rows.append(dict(shift=shift,total=N,represented=float(out.sum()),outside=float(lost),closure=float(N-out.sum()-lost)))
 write('REC','R7.json',dict(status='LOCAL_CAUSAL_STEP_AND_CANONICAL_STOCK_ORACLE',source_sha=sha(p),history_sha=sha(g),span=float(a),min_lookback=look,step_ratio={n:float(a/n/look) for n in [64,128,256]},initial_x=float(v['xHII'][63]),initial_T=float(v['T'][63]),stock=rows))
 print('REC',a,look,rows,flush=True)
def REI():
 r=repos['REI'][0];p=r/'research/r118c3f_signed_thermal';sys.path.insert(0,str(p));from signed import SignedKompaneets
 rows=[]
 for low in [1e-10,1e-6,1e-3]:
  for n in [128,256,512,1024,2048,4096]:
   s=SignedKompaneets(np.geomspace(low,60,n+1));th=.2;f=s.rhs(np.zeros(n),th);j=s.flux(np.zeros(n),th);target=4*(1-1/th)*np.pi**4/15;mom=float(s.x@f)
   assert abs(mom+np.diff(s.x)@j)<1e-10 and abs(f.sum())<1e-10
   rows.append(dict(xmin=low,n=n,moment=mom,relative=mom/target-1,number_residual=float(f.sum()),energy_residual=float(mom+np.diff(s.x)@j)))
 write('REI','R7.json',dict(status='INSTANTANEOUS_PLANCK_MOMENT_CUTOFF_SCAN',rows=rows,source_sha=sha(p/'signed.py')))
 print('REI',rows[-1],flush=True)
if __name__=='__main__':
 assert all((x['stage'],x['repo']) in {(f'R{i}',k) for i in range(1,7) for k in repos} for x in map(json.loads,receipt.read_text().splitlines()))
 assert len({(x['stage'],x['repo']) for x in map(json.loads,receipt.read_text().splitlines())})==18
 # Persist script for each repository as self-contained evidence with a shared driver reference.
 for k,fn in [('BASS',BASS),('REC',REC),('REI',REI)]:fn()
 batch('R7')
 b=json.loads((folder('BASS')/'R7.json').read_text());c=json.loads((folder('REC')/'R7.json').read_text());e=json.loads((folder('REI')/'R7.json').read_text())
 note('R8',[
  'Computed principal-angle bounds on actual leading spans: '+str({k:round(v['sigma_min'],8) for k,v in b['rows'].items()})+'. Axial control admits pure spin1; triaxial control does not. Existing physical histories remain unoptimized; no full nonlinear obstruction admitted.',
  'Causal step ratios h/min(delay)='+str(c['step_ratio'])+'. Local accepted-history feedback is executable; no reason to wait for H+He. Canonical stock overlap is conservative with exterior amount ledgered; physical exterior reaction mapping not solved.',
  'At fixed theta=0.2, xmin=1e-10, instantaneous Planck moment errors: '+str({v['n']:v['relative'] for v in e['rows'] if v['xmin']==1e-10})+'. Grid/cutoff can be tested independently of time integration; live gas residual still separate.'])
 note('R9',[
  'Implementation contract: function principal_bound(A,P3) returns normal spectrum, six singular values, minimum projected fraction, rejecting degenerate span and invalid projector. Native control mass/angle/shape can be varied only in research example. Use normalized physical wedge and retain absolute B3 and Gauss residual.',
  'Implementation contract: causal shared-gas endpoint solve uses fixed prefix, actual H, canonical ray histories, both angular-on/off. Two independent time resolutions plus BE check; store accepted x,T, outgoing and residuals; local window only. Canonical remap accepts nonnegative piecewise constant occupation, distinct exterior ledger.',
  'Implementation contract: re-evaluate signed moment grid at xmin=[1e-10,1e-6,1e-3], n up to 4096; opt-in implicit fixed-composition sequence couples evolving gas T to signed Compton and FF energy at each stage. Never update state until root accepted, preserve external source ownership.'])
 note('R10',[
  'R1–R9 theory and finite checks complete for scoped principal-angle result. Next C1–C10: implement reusable projector check and control scan, verify native physical cases where available. Triple directional donor remains local-only until full validated coverage.',
  'R1–R9 theory and causal preflight complete. Next: actual local shared x,T with canonical history, paired control; preserve source locks and causal guard. Independent physical momentum stock remap; external reaction coupling open.',
  'R1–R9 theory and instantaneous frequency check complete. Next: refine nonlinear actual-clock spectral replay, opt-in gas-cell and cutoff ledger. Production/live H+He remains unpromoted.'])

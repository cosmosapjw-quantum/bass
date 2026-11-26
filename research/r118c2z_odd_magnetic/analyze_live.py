"""C2Z joint and independent axis/initial-transient comparisons."""
import json,hashlib,gzip
from pathlib import Path
import numpy as np
D=Path(__file__).resolve().parent;B=D.parents[1];I=Path('/home/cosmosapjw/worktrees/rei-htt-thomson-20261124');H=Path('/home/cosmosapjw/Downloads')
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def kv(p):return dict(x.split('=',1) for x in p.read_text().splitlines() if '=' in x)
def bits(s):return np.asarray([int(x,16) for x in s.split()],dtype=np.uint64).view(np.float64)
def root(n):return H/('bass_r118c2z_final_'+n)
def read(p,f):return np.atleast_1d(np.genfromtxt(p/f,names=True,delimiter=','))
fields=('T','xHII','xHeIII','J0','Pyz','cool_pi_norm','ne','h')
cases={};data={};reports={}
specs={'base':('base',4,35),'time':('base',4,35),'freq':('freq',4,67),'angle':('angle',8,35),'joint':('joint',8,67),'joint_tail':('joint',8,67),'late':('late',4,35),'late_tail':('late',4,35),'freq_time':('freq',4,67),'angle_time':('angle',8,35),'freq_time2':('freq',4,67),'early100':('freq',4,67),'early200':('freq',4,67)}
for n,(config,nmu,ne) in specs.items():
 p=root(n);assert int((D/('final_'+n+'.exit')).read_text())==0,n
 ret=kv(p/'RETURN.txt');c=kv(p/'config.cfg')
 assert (p/'config.cfg').read_bytes()==(D/(config+'.cfg')).read_bytes()
 r=read(p,'history.csv');e=read(p,'error_components.csv')
 assert np.all(np.isfinite(r.view(float))) and np.all(np.isfinite(e.view(float))) and np.all(np.diff(r['a'])>0)
 assert int(ret['accepted'])==r['accepted'][-1] and len(e)==2*(len(r)-1)
 v=np.stack([e[k] for k in e.dtype.names[3:]],axis=1)
 assert np.array_equal(e['accepted'].reshape(-1,2)[:,0],r['accepted'][1:]) and np.array_equal(e['accepted'].reshape(-1,2)[:,1],r['accepted'][1:])
 assert np.all(e['stage'].reshape(-1,2)==[0,1])
 assert np.array_equal(e['a'][1::2],r['a'][1:]) and np.array_equal(v[1::2].max(axis=1),r['local_error'][1:])
 assert max(v.ravel())<float(c['local_target']) and max(abs(r['ledger']))<float(c['energy_budget_ev_per_h'])
 assert max(abs(r['gauss']))<1e-8 and min(r['escape'])>=0
 cp=p/'checkpoint';man=(cp/'MANIFEST').read_text().splitlines();assert man[0]=='C2Z_JOINT_V2' and man[1]==sha(B/'_rustcore/target/release/c2z_live_rei_bridge') and int(man[2].split()[-1])==nmu
 for line in man[3:]:
  h,f=line.split();assert sha(cp/f)==h
 head,ident=(cp/'rei.txt').read_text().split('\nGENERAL_SOURCE_IDENTITY\n',1);l=head.splitlines()
 assert l[0]=='AXBI_CHECKPOINT_V8_GENERAL' and (I/'rust/rei_microphysics/src/axbi_covariant_driver.rs').read_text() in ident
 reg=bits(l[24]);ref=reg[:9].reshape(3,3);rr=reg[9:].reshape(-1,4);nr=len(rr);assert nr==2*nmu*nmu
 points=bits(l[25]).reshape(-1,11);a,h=points[-1,:2];f=points[-1,2:].reshape(3,3)
 assert a==r['a'][-1] and h==r['h'][-1]
 ray=rr[:,:3]@ref@np.linalg.inv(a*f);scale=np.linalg.norm(ray,axis=1);direc=ray/scale[:,None];rep=np.repeat(scale,ne)
 u=np.zeros(nr*ne)
 for k,lo,hi in ((19,0,13.6),(4,13.6,24.59),(15,24.59,54.42),(11,54.42,np.inf)):
  N,U,x,y=[np.fromstring(l[j],sep=' ') for j in range(k,k+4)];assert len(N)==nr*ne and min(N)>=0 and np.all(U>=x*N) and np.all(U<=y*N)
  m=N>0;assert np.all(x[m]*rep[m]>=lo-1e-12) and np.all(y[m]*rep[m]<=hi+1e-12)
  u+=U
 energy=u.reshape(nr,ne).sum(axis=1)*scale;P=np.einsum('a,ai,aj->ij',energy,direc,direc)
 assert abs(energy.sum()-r['J0'][-1])<1e-13 and abs(P[1,2]-r['Pyz'][-1])<1e-13
 assert np.max(abs(energy@direc))<1e-12*energy.sum()
 files={str(f.relative_to(p)):sha(f) for f in list(p.iterdir())+list(cp.iterdir()) if f.is_file()}
 for file in list(p.iterdir())+list(cp.iterdir()):
  if file.is_file():
   tag=str(file.relative_to(p)).replace('/','_')
   (D/(n+'_'+tag+'.gz')).write_bytes(gzip.compress(file.read_bytes(),mtime=0))
 winners=dict(zip(e.dtype.names[3:],map(int,np.bincount(v.argmax(axis=1),minlength=v.shape[1]))))
 cases[n]=dict(config=config,rays=nr,frequency_cells=ne,raw=str(p),hashes=files,return_=ret,terminal={k:float(r[k][-1]) for k in ('a','z',*fields,'ledger','gauss','local_error')},max_ledger=float(max(abs(r['ledger']))),max_gauss=float(max(abs(r['gauss']))),max_stage_error=float(max(v.ravel())),winners=winners,rows=len(r))
 data[n]=r;reports[n]=e
 print(n,ret['status'],ret['accepted'],float(r['z'][-1]),winners,flush=True)
for n in ('base','time','freq','angle','joint_tail','freq_time','angle_time','freq_time2'):
 assert cases[n]['return_']['status']=='COMPLETE',n
 assert abs(data[n]['z'][-1]-19.8)<1e-10
for n in ('early100','early200'):assert cases[n]['return_']['status']=='CHECKPOINT_COUNT'
for n in ('joint','late'):
 t=n+'_tail';assert cases[n]['return_']['status']=='WALL_CAP'
 assert np.array_equal(data[n][-1],data[t][0])
 data[n]=np.concatenate([data[n],data[t][1:]]);reports[n]=np.concatenate([reports[n],reports[t]])
 assert int(cases[t]['return_']['accepted'])==len(data[n])-1
cases['joint']['joined_terminal']=cases['joint_tail']['terminal'];cases['late']['joined_terminal']=cases['late_tail']['terminal']
def comparison(n,m):
 a,b=data[n],data[m];zmin=max(a['z'][-1],b['z'][-1]);zz=np.linspace(zmin,20.,4001)
 vals={}
 for k in fields:
  x=np.interp(zz,a['z'][::-1],a[k][::-1]);y=np.interp(zz,b['z'][::-1],b[k][::-1]);norm=max(abs(y).max(),1e-300)
  mask=zz<=19.999
  vals[k]=dict(terminal_relative=float((x[0]-y[0])/max(abs(y[0]),1e-300)),peak_normalized=float(max(abs(x-y))/norm),post_initial_peak_normalized=float(max(abs(x[mask]-y[mask]))/norm))
 same=len(a)==len(b) and np.max(abs(a['a']-b['a']))<1e-14
 return dict(same_grid=bool(same),fields=vals)
comparisons={f'{n}_{m}':comparison(n,m) for n,m in (('base','time'),('base','angle'),('time','freq_time'),('time','angle_time'),('freq_time','joint'),('angle_time','joint'),('freq_time','freq_time2'),('base','joint'))}
a=data['early100'];b=data['early200'];assert len(a)==101 and len(b)==201
assert np.max(abs(a['a']-b['a'][::2]))<1e-14
u=np.log(b['a']/b['a'][0]);t=u/(2.1842852410855023e-18*b['h'][0]);J=b['J0'];scale=J[-1]
early=dict(z_end=float(b['z'][-1]),seconds_end=float(t[-1]),J0_end=float(scale),max_shared_J0_relative=float(max(abs(a['J0']-J[::2]))/scale),time_to_half_s=float(np.interp(.5*scale,J,t)),time_to_90_s=float(np.interp(.9*scale,J,t)))
# Direct compare early accepted endpoints at u=1e-5 and 2e-5 with coarser histories.
for n in ('freq_time','freq_time2'):
 r=data[n];x=np.log(r['a']/r['a'][0])
 early[n]=[dict(u=float(q),J0=float(j),fine=float(np.interp(q,u,J)),relative=float((j-np.interp(q,u,J))/scale)) for q,j in zip(x[1:3],r['J0'][1:3]) if q<=u[-1]+1e-12]
out=dict(status='SCOPED_LIVE_AXIS_AND_TRANSIENT',cases=cases,comparisons=comparisons,early=early,late_status=cases['late_tail']['return_']['status'])
(D/'LIVE.json').write_text(json.dumps(out,indent=2)+'\n')
print('comparisons',json.dumps(comparisons,indent=2)[:12000]);print('early',early)

import hashlib,json,re,gzip
from pathlib import Path
import numpy as np
D=Path(__file__).resolve().parent;B=D.parents[1];H=Path('/home/cosmosapjw/Downloads')
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def j(p):return json.loads(p.read_text())
def kv(p):return dict(x.split('=',1) for x in p.read_text().splitlines() if '=' in x)
for n in ('physics_build','physics_run','checkpoint_green','bridge_build','channels_build','channels','secondary','lib_tests','regression','live_first','live_refined','live_split4','live_resume4'):
 assert int((D/(n+'.exit')).read_text())==0,n
for n in ('live_whole','live_resume','reject_tampered','reject_wrongstep','reject_wrongfeedback'):assert int((D/(n+'.exit')).read_text())!=0
for n in ('tampered','wrongstep','wrongfeedback'):assert 'joint checkpoint identity mismatch' in (D/('reject_'+n+'.log')).read_text()
for n in ('PHYSICS_INPUT.sha256','BRIDGE.sha256','CHANNEL_BINARY.sha256'):
 for l in (D/n).read_text().splitlines():
  h,p=l.split(maxsplit=1);assert sha(B/p)==h,p
for p,h in j(D.parent/'r118c2r_multispecies/SOURCES.json').items():assert sha(p)==h
names=('triax_1','triax_2','triax_4','triax_8','lrs','shape','triax_ref','triax_l8')
phys={}
for n in names:
 p=D/(n+'.csv');r=np.genfromtxt(p,names=True,delimiter=',');assert np.all(np.isfinite(r.view(float))) and abs(r['a'][-1]-.2)<1e-12
 assert max(abs(r['gauss']))<1e-5
 phys[n]=dict(sha=sha(p),rows=len(r),terminal={k:float(r[k][-1]) for k in ('B3','B5','E2','S0','S1','B3im_m2','gauss')},max_gauss=float(max(abs(r['gauss']))))
amp=np.array([.1,.05,.025,.0125]);v=np.array([phys[n]['terminal']['B3'] for n in names[:4]])
power=np.log2(v[:-1]/v[1:]);assert max(abs(power-3))<.002 and phys['lrs']['terminal']['B3']<1e-13
shape=phys['shape']['terminal']['B3']/v[0];assert abs(shape/abs(np.cos(.9))-1)<1e-4
assert abs(phys['triax_ref']['terminal']['B3']/v[0]-1)<1e-5
channels=[]
for n in (512,1024):
 p=D/f'channels_{n}.csv';r=np.genfromtxt(p,names=True,delimiter=',',dtype=None,encoding='utf8')
 c=(r['re']+1j*r['im']).reshape(4,7)
 channels.append(dict(n=n,sha=sha(p),norms=np.linalg.norm(c,axis=1).tolist(),total=float(np.linalg.norm(c.sum(axis=0))),m2_im=c[:,5].imag.tolist()))
assert abs(channels[-1]['total']/(v[-1]/amp[-1]**3)-1)<1e-4
cases={}
for n in ('whole','first','refined','resume','split4','resume4'):
 p=H/('bass_r118c2x_'+n);r=np.atleast_1d(np.genfromtxt(p/'history.csv',names=True,delimiter=','))
 assert np.all(np.isfinite(r.view(float))) and max(abs(r['ledger']))<1e-8 and max(abs(r['gauss']))<1e-8 and max(r['local_error'])<.00016
 ret=kv(p/'RETURN.txt') if (p/'RETURN.txt').exists() else None
 c=dict(path=str(p),status=ret,rows=len(np.atleast_1d(r)),history_sha=sha(p/'history.csv'),terminal={k:float(np.atleast_1d(r[k])[-1]) for k in ('z','h','ne','T','xHII','xHeIII','J0','Pyz','source','escape','cmb','ledger','gauss','accepted','rhs','rejected')},max_ledger=float(max(abs(np.atleast_1d(r['ledger'])))),max_gauss=float(max(abs(np.atleast_1d(r['gauss'])))),max_local=float(max(np.atleast_1d(r['local_error']))))
 for f in p.iterdir():
  if f.is_file():(D/(n+'_'+f.name+'.gz')).write_bytes(gzip.compress(f.read_bytes(),mtime=0))
 q=p/'checkpoint'
 if q.exists():
  files={f.name:sha(f) for f in q.iterdir()};c['checkpoint']=files
  man=(q/'MANIFEST').read_text().splitlines()
  assert man[1]==sha(B/'_rustcore/target/release/c2x_live_rei_bridge')
  for l in man[3:]:
   h,f=l.split();assert files[f]==h
  for f in q.iterdir():(D/(n+'_ck_'+f.name+'.gz')).write_bytes(gzip.compress(f.read_bytes(),mtime=0))
 cases[n]=c
p=H/'bass_r118c2x_refined';a=H/'bass_r118c2x_split4';b=H/'bass_r118c2x_resume4'
x=(a/'history.csv').read_bytes().splitlines(keepends=True);y=(b/'history.csv').read_bytes().splitlines(keepends=True)
assert x[-1]==y[1] and b''.join(x+y[2:])==(p/'history.csv').read_bytes()
assert cases['refined']['checkpoint']==cases['resume4']['checkpoint']
assert int(cases['refined']['status']['accepted'])==1853 and int(cases['split4']['status']['accepted'])==400
assert cases['first']['status']['rejected']=='200' and cases['whole']['status'] is None and cases['resume']['status'] is None
sec=j(D/'SECONDARY.json');assert sec['source_sha']==cases['refined']['history_sha']
assert abs(sec['rows'][-1]['total_pi_norm']/sec['rows'][0]['total_pi_norm']-1)<1e-10
nt=sum(map(int,re.findall(r'test result: ok\. (\d+) passed;', (D/'regression.log').read_text())))
assert nt==10 and '189 passed; 0 failed' in (D/'lib_tests.log').read_text()
out=dict(status='PASS_SCOPED_JOINT_RESTART_AND_CUBIC_TRIAXIAL',parent='2bab4044bad274e7ef119f5b7427b602c16713f0',rei_commit='77c6c809f9a07f0b312ee50a8ae1cf702541d250',physics=phys,power=power.tolist(),shape_ratio=shape,shape_prediction=float(abs(np.cos(.9))),channels=channels,cases=cases,restart_byte_identical=True,secondary=sec,lib_tests=189,targeted_tests=nt,production_admission='HOLD_FULL_INTERVAL_SECONDARY_MOMENT_OWNER_AND_JOINT_RESOLUTION',native_subagent='NOT_RUN')
(D/'RESULTS.json').write_text(json.dumps(out,indent=2)+'\n')
print(out['status'],'powers',power,'shape',shape,'channels',channels[-1]['total'],'terminal',cases['refined']['terminal'],'tests',nt)

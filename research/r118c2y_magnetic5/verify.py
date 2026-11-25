import json,hashlib,re,gzip
from pathlib import Path
import numpy as np
D=Path(__file__).resolve().parent;B=D.parents[1];H=Path('/home/cosmosapjw/Downloads');I=Path('/home/cosmosapjw/worktrees/rei-htt-thomson-20261124')
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def j(p):return json.loads(Path(p).read_text())
def kv(p):return dict(x.split('=',1) for x in p.read_text().splitlines() if '=' in x)
for n in ('cooling_green','bridge_build','vector_build','vector','cooling_oracle','lib_tests','regression','live_whole','live_iso','live_split','live_resume','shape015','shape030','shape045','shape_m030','half030','lrs_pi6','v10','v05','v025','v10p','v05p','v025p','v05m','v05ref'):
 assert int((D/(n+'.exit')).read_text())==0,n
for n in ('BRIDGE.sha256','PHYSICS_INPUT.sha256','VECTOR_BINARY.sha256'):
 for l in (D/n).read_text().splitlines():
  h,p=l.split(maxsplit=1);assert sha(B/p)==h,p
P=D.parent/'r118c2x_triaxial';prior=j(P/'ACCEPTANCE.json')
amp=np.array([.1,.05,.025,.0125]);vals=[]
for name in ('triax_1','triax_2','triax_4','triax_8'):
 p=P/(name+'.csv');assert sha(p)==prior['physics'][name]['sha']
 vals.append(float(np.genfromtxt(p,names=True,delimiter=',')['B5'][-1]))
power=np.log2(np.array(vals[:-1])/np.array(vals[1:]));assert max(abs(power-4))<.005
shape=[]
for name,phi in [('shape015',.15),('shape030',.3),('shape045',.45),('shape_m030',-.3),('half030',.3),('lrs_pi6',np.pi/6)]:
 p=D/(name+'.csv');r=np.genfromtxt(p,names=True,delimiter=',')
 assert abs(r['a'][-1]-.2)<1e-12 and np.all(np.isfinite(r.view(float)))
 a=.05 if name=='half030' else .1;v=float(r['B5'][-1]);ratio=v/(vals[0]*(a/.1)**4)
 shape.append(dict(name=name,sha=sha(p),amp=a,phi=phi,B5=v,ratio=ratio,prediction=float(abs(np.cos(3*phi)))))
assert shape[-1]['B5']<1e-13 and max(abs(x['ratio']-x['prediction']) for x in shape)<.01
vectors={}
for p in sorted(D.glob('v*.csv')):
 r=np.genfromtxt(p,names=True,delimiter=',');b=r['re']+1j*r['im'];t=r['template_re']+1j*r['template_im']
 c=np.vdot(t,b)/np.vdot(t,t);err=float(np.linalg.norm(b-c*t)/np.linalg.norm(b))
 assert len(b)==11 and err<.01
 vectors[p.stem]=dict(sha=sha(p),coefficient_re=float(c.real),coefficient_im=float(c.imag),orthogonal_relative=err)
assert len(vectors)==8
for suffix in ('','p'):
 assert vectors['v025'+suffix]['orthogonal_relative']<vectors['v05'+suffix]['orthogonal_relative']<vectors['v10'+suffix]['orthogonal_relative']
cases={};data={}
for n in ('whole','iso','split','resume'):
 p=H/('bass_r118c2y_'+n);r=np.genfromtxt(p/'history.csv',names=True,delimiter=',');ret=kv(p/'RETURN.txt')
 assert len(r)==int(ret['accepted'])+1 if n!='resume' else len(r)==int(ret['accepted'])-600+1
 assert ret['status']==('CHECKPOINT_COUNT' if n=='split' else 'COMPLETE') and ret['rejected']=='1'
 assert np.all(np.isfinite(r.view(float))) and np.all(np.diff(r['a'])>0)
 assert max(abs(r['ledger']))<1e-8 and max(abs(r['gauss']))<1e-8 and max(r['local_error'])<.00016
 assert min(r['escape'])>=0 and min(r['cool_pi_norm'])>=0
 if n!='split':assert r['z'][-1]==18 and int(ret['accepted'])==3535
 c=p/'checkpoint';files={f.name:sha(f) for f in c.iterdir()};assert len(files)==6
 man=(c/'MANIFEST').read_text().splitlines();assert man[0]=='C2Y_JOINT_V1' and man[1]==sha(B/'_rustcore/target/release/c2y_live_rei_bridge')
 for l in man[3:]:
  h,f=l.split();assert files[f]==h
 # native ordered stock is exact binary64 hexadecimal text
 q=np.array([int(x,16) for x in (c/'cooling.txt').read_text().split()],dtype=np.uint64).view(np.float64);assert len(q)==128 and min(q)>=0 and np.isfinite(q).all()
 if n=='iso':assert np.all(q==0)
 for f in p.iterdir():
  if f.is_file():(D/(n+'_'+f.name+'.gz')).write_bytes(gzip.compress(f.read_bytes(),mtime=0))
 for f in c.iterdir():(D/(n+'_ck_'+f.name+'.gz')).write_bytes(gzip.compress(f.read_bytes(),mtime=0))
 data[n]=r;cases[n]=dict(raw=str(p),history_sha=sha(p/'history.csv'),hashes=files,return_=ret,terminal={k:float(r[k][-1]) for k in ('z','h','T','xHII','xHeIII','ne','J0','escape','cmb','cool_pi_norm','cool_Pyz','source','ledger','gauss','local_error')},max_ledger=float(max(abs(r['ledger']))),max_gauss=float(max(abs(r['gauss']))),max_error=float(max(r['local_error'])))
a=H/'bass_r118c2y_split';b=H/'bass_r118c2y_resume';c=H/'bass_r118c2y_whole'
x=(a/'history.csv').read_bytes().splitlines(keepends=True);y=(b/'history.csv').read_bytes().splitlines(keepends=True)
assert x[-1]==y[1] and b''.join(x+y[2:])==(c/'history.csv').read_bytes()
assert cases['whole']['hashes']==cases['resume']['hashes']
sec=j(D/'COOLING_ORACLE.json');assert sec['source_sha']==cases['whole']['history_sha'] and sec['iso_sha']==cases['iso']['history_sha']
assert sec['rows'][-1]['energy_relative']<1e-12 and sec['rows'][-1]['pi_relative']<1e-7
n=sum(map(int,re.findall(r'test result: ok\. (\d+) passed;', (D/'regression.log').read_text())));assert n==11
assert '189 passed; 0 failed' in (D/'lib_tests.log').read_text()
r=data['whole'];s=data['iso'];assert np.array_equal(r['a'],s['a']);ds=np.stack([r[f'S{k}']-s[f'S{k}'] for k in range(5)],axis=1)
out=dict(status='PASS_SCOPED_B5_COOLING_LIVE_RESTART',parent='a078a7c03ba4327277bc447b5761fd40b9ccdc51',rei_commit='bfcaed21ffc4000fe6162fd05a6651af062bf955',B5_amplitudes=amp.tolist(),B5_norms=vals,power=power.tolist(),shape=shape,vectors=vectors,cases=cases,restart_byte_identical=True,cooling_oracle=sec,max_delta_h=float(max(abs(r['h']-s['h']))),max_delta_s=float(max(np.linalg.norm(ds,axis=1))),lib_tests=189,targeted_tests=n,production_admission='HOLD_FULL_INTERVAL_TIME_FREQUENCY_ANGULAR_AND_SECONDARY_SPECTRUM',native_subagent='NOT_RUN')
(D/'RESULTS.json').write_text(json.dumps(out,indent=2)+'\n')
print(out['status'],'powers',power,'terminal',cases['whole']['terminal'],'tests',n)

import hashlib,json,re,gzip
from pathlib import Path
import numpy as np
D=Path(__file__).resolve().parent
B=D.parents[1]; H=Path('/home/cosmosapjw/Downloads'); I=Path('/home/cosmosapjw/worktrees/rei-htt-thomson-20261124')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
for f in ('physics','external_green','bridge_build','bridge_final_build','lib_tests','regression'):
 assert int((D/(f+'.exit')).read_text())==0,f
for l in (D/'BRIDGE_FINAL.sha256').read_text().splitlines():
 s,p=l.split(maxsplit=1);assert sha(B/p)==s,p
assert sha(H/'bass_r118c2w_bridge_v1')==(D/'BRIDGE_V1_ORIGINAL.sha256').read_text().split()[0]
ph=json.loads((D/'PHYSICS.json').read_text())
assert sha(D.parent/'r118c2r_multispecies/rei_q256.csv')==ph['source_sha']
for p,h in json.loads((D.parent/'r118c2r_multispecies/SOURCES.json').read_text()).items():assert sha(p)==h
assert ph['cases']['aligned']['final_Bnorm']==0
for n in ('diagonal','rotating'):assert ph['cases'][n]['onset'][-1]['coefficient_relative']<.001
err=np.array([r['stress_error'] for r in ph['nonlinear_stress']]);assert np.all(err[:-1]/err[1:]>7.9)
cases={}
for n in ('fine','control','coarse','long_fine','long_control','long_coarse','final_fine','final_control','final_coarse'):
 assert int((D/('live_'+n+'.exit')).read_text())==0,n
 p=H/('bass_r118c2w_'+n); r=np.genfromtxt(p/'history.csv',delimiter=',',names=True)
 ret=dict(x.split('=',1) for x in (p/'RETURN.txt').read_text().splitlines())
 assert ret['status']=='COMPLETE' and int(ret['rejected'])==0
 assert len(r)==int(ret['accepted'])+1
 assert all(np.isfinite(r[k]).all() for k in r.dtype.names)
 assert np.all(np.diff(r['a'])>0) and abs(r['z'][0]-20)<1e-12
 assert abs(r['z'][-1]-(19.8 if n.startswith(('long_','final_')) else 19.99))<1e-10
 assert np.max(r['local_error'])<.00016
 assert np.max(abs(r['ledger']))<1e-8
 assert np.max(abs(r['gauss']))<1e-8
 assert np.max(abs(r['Pxx']+r['Pyy']+r['Pzz']-r['J0']))<1e-12
 F=np.stack([r[f'F{i}{j}'] for i in range(3) for j in range(3)],axis=-1).reshape(-1,3,3)
 assert np.max(abs(np.linalg.det(F)-1))<1e-8
 ledger=r['J0']+r['thermal']+r['binding']-(r['thermal'][0]+r['binding'][0])-r['source']+r['escape']+r['cmb']+r['work']
 assert np.max(abs(ledger-r['ledger']))<1e-12
 if n.startswith('final_'):
  assert sha(p/'history.csv')==sha(H/('bass_r118c2w_long_'+n[6:])/'history.csv')
  ident=(p/'rei_source_identity.txt').read_text()
  for f in ('general_history.rs','general_angular.rs','axbi_covariant_driver.rs'):assert (I/'rust/rei_microphysics/src'/f).read_text() in ident,f
  for f in p.iterdir():
   if f.is_file():(D/(n+'_'+f.name+'.gz')).write_bytes(gzip.compress(f.read_bytes(),mtime=0))
 cases[n]={'path':str(p),'hashes':{f.name:sha(f) for f in p.iterdir() if f.is_file()},'return':ret,'max_ledger':float(np.max(abs(r['ledger']))),'max_local_error':float(np.max(r['local_error'])),'terminal':{k:float(r[k][-1]) for k in ('z','h','ne','T','xHII','J0','thermal','binding','escape','cmb','source','work','gauss')}}
nt=sum(map(int,re.findall(r'test result: ok\. (\d+) passed;', (D/'regression.log').read_text())))
assert nt==9 and '189 passed; 0 failed' in (D/'lib_tests.log').read_text()
j=dict(status='PASS_SCOPED_LIVE_GENERAL_BRIDGE_AND_ALIGNMENT',parent='a19c78b841eafceb792cbd6cf616e41f6968de53',rei_commit='3821603988d2e5a4a769b0a234aad6c419f2e43b',cases=cases,physics=ph,lib_tests=189,targeted_tests=nt,scope='z20 to 19.8; gas and UV live, isotropic secondary radiation closure; no resolved tiny H feedback claim; production pins unchanged',production_admission='HOLD_FULL_INTERVAL_AND_RESTART',native_subagent='NOT_RUN')
(D/'RESULTS.json').write_text(json.dumps(j,indent=2)+'\n')
print('verified',len(cases),'runs',nt,'targeted tests',cases['final_fine']['max_ledger'])

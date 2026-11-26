import json,hashlib,re,gzip
from pathlib import Path
import numpy as np
D=Path(__file__).resolve().parent;B=D.parents[1];H=Path('/home/cosmosapjw/Downloads');I=Path('/home/cosmosapjw/worktrees/rei-htt-thomson-20261124')
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def j(p):return json.loads(Path(p).read_text())
def kv(p):return dict(x.split('=',1) for x in p.read_text().splitlines() if '=' in x)
for n in ('build','orders_build','bridge_build','spectral','lib_tests','regression','a10','a05','a025','a0125','ref','single10','single05','single025','p12','p12ref','p25','psingle','live_off','live_grey','live_table','live_fine','live_split','live_resume','live_fine_off','live_late_table'):
 assert int((D/(n+'.exit')).read_text())==0,n
for fn in ('INPUT.sha256','ORDERS.sha256','BRIDGE.sha256'):
 for line in (D/fn).read_text().splitlines():
  h,p=line.split(maxsplit=1);assert sha(B/p)==h,p
ls=(3,5,7);phy={};pert={};vec={}
for n in ('a10','a05','a025','a0125','ref','single10','single05','single025'):
 p=D/(n+'.csv');r=np.genfromtxt(p,names=True,delimiter=',');assert len(r)==33 and np.all(np.isfinite(r.view(float)))
 q=D/(n+'.geom');gauss=float(q.read_text().splitlines()[-1].split('=')[1]);assert abs(gauss)<1e-5
 b={l:(r['re']+1j*r['im'])[r['ell']==l] for l in ls};vec[n]=b
 phy[n]=dict(sha=sha(p),geometry_sha=sha(q),norm=[float(np.linalg.norm(b[l])) for l in ls],gauss=gauss)
a=np.array([phy[n]['norm'] for n in ('a10','a05','a025','a0125')]);powers=np.log2(a[:-1]/a[1:])
assert abs(powers[-1,0]-2)<.1 and abs(powers[-1,1]-3)<.1
assert abs(phy['ref']['norm'][0]/a[0,0]-1)<1e-4
for n in ('p12','p12ref','p25','psingle'):
 p=D/(n+'.csv');r=np.genfromtxt(p,names=True,delimiter=',');assert len(r)==132
 vals={l:[(r['re']+1j*r['im'])[(r['ell']==l)&(r['order']==k)] for k in range(1,5)] for l in ls}
 pert[n]=dict(sha=sha(p),norm=[[float(np.linalg.norm(v)) for v in vals[l]] for l in ls])
 if n=='p12ref':
  for l,k in zip(ls,(2,3,4)):assert max(np.linalg.norm(v) for v in vals[l][:k-1])==0
 if n in ('p12ref','p25','psingle'):
  ref,ep={'p12ref':('a0125',.0125),'p25':('a025',.025),'psingle':('single025',.025)}[n]
  pert[n]['native_relative']=[float(np.linalg.norm(vec[ref][l]-sum(ep**k*v for k,v in enumerate(vals[l],1)))/np.linalg.norm(vec[ref][l])) for l in ls]
assert pert['p12ref']['native_relative'][0]<3e-5
lead=[pert['p12ref']['norm'][j][j+1] for j in range(3)];lead0=[pert['p12']['norm'][j][j+1] for j in range(3)]
assert max(abs(np.array(lead)/lead0-1))<2e-8
cases={};data={}
for n in ('off','grey','table','fine','split','resume','fine_off','late_table'):
 p=H/('bass_r118c3b_'+n);r=np.genfromtxt(p/'history.csv',names=True,delimiter=',');s=np.genfromtxt(p/'secondary_spectrum.csv',names=True,delimiter=',');err=np.genfromtxt(p/'error_components.csv',names=True,delimiter=',');ret=kv(p/'RETURN.txt')
 assert len(s)==len(r) and len(err)==2*(len(r)-1) and np.array_equal(s['a'],r['a'])
 assert ret['status']==('CHECKPOINT_COUNT' if n=='split' else 'COMPLETE') and np.all(np.diff(r['a'])>0)
 assert max(abs(r['ledger']))<1e-8 and max(abs(r['gauss']))<1e-8 and max(r['local_error'])<.00016
 assert min(s['FF_abs_U'])>=0 and max(abs(s['FF_U']+s['FF_work']-s['FF_birth']))<1e-10*max(s['FF_birth'])
 assert max(abs(s['y_Compton']*4*s['BB_U']-r['cmb']-s['FF_abs_U']))<1e-13*max(abs(r['cmb']))
 cp=p/'checkpoint';files={str(f.relative_to(p)):sha(f) for f in list(p.iterdir())+list(cp.iterdir()) if f.is_file()}
 man=(cp/'MANIFEST').read_text().splitlines();assert man[0]=='C3B_JOINT_V1' and man[1]==sha(B/'_rustcore/target/release/c3b_live_rei_bridge') and len(man)==9
 for line in man[3:]:
  h,f=line.split();assert files['checkpoint/'+f]==h
 head,ident=(cp/'rei.txt').read_text().split('\nGENERAL_SOURCE_IDENTITY\n',1);assert head.startswith('AXBI_CHECKPOINT_V10_GENERAL')
 assert (I/'rust/rei_microphysics/src/ff_balance.rs').read_text() in ident
 assert (I/'research/r118c3b_ff_balance/gauntff.dat').read_text() in ident
 for f in list(p.iterdir())+list(cp.iterdir()):
  if f.is_file():(D/(n+'_'+str(f.relative_to(p)).replace('/','_')+'.gz')).write_bytes(gzip.compress(f.read_bytes(),mtime=0))
 cases[n]=dict(raw=str(p),files=files,return_=ret,terminal={k:float(r[k][-1]) for k in ('z','T','xHII','xHeIII','h','escape','cmb','ledger','gauss')},spectrum={k:float(s[k][-1]) for k in s.dtype.names[2:]},max_ledger=float(max(abs(r['ledger']))),max_gauss=float(max(abs(r['gauss']))))
 data[n]=(r,s)
a=H/'bass_r118c3b_split';b=H/'bass_r118c3b_resume';p=H/'bass_r118c3b_table'
for f in ('history.csv','secondary_spectrum.csv','error_components.csv'):
 x=(a/f).read_bytes().splitlines(keepends=True);y=(b/f).read_bytes().splitlines(keepends=True)
 assert b''.join(x+y[1 if f=='error_components.csv' else 2:])==(p/f).read_bytes()
for f in (p/'checkpoint').iterdir():assert sha(f)==sha(b/'checkpoint'/f.name)
assert sha(H/'bass_r118c3b_off/history.csv')==sha(H/'bass_r118c3a_short/history.csv')
effects={}
for n,m in (('table','off'),('fine','fine_off')):
 r=data[n][0];q=data[m][0];assert np.array_equal(r['a'],q['a'])
 effects[n]=dict(deltaT=float(r['T'][-1]-q['T'][-1]),delta_x=float(r['xHII'][-1]-q['xHII'][-1]))
assert abs(effects['table']['deltaT']/effects['fine']['deltaT']-1)<.001
s=j(D/'SPECTRAL.json');assert s['gaunt_sha']==sha(I/'research/r118c3b_ff_balance/gauntff.dat')
for r in s['rows']:
 for f,h in r['hashes'].items():assert sha(H/('bass_r118c3b_'+r['name'])/f)==h
 assert abs(r['effective_stage_relative'])<1e-4 and abs(r['absorption_relative'])<1e-8 and abs(r['emission_relative'])<1e-8
nt=sum(map(int,re.findall(r'test result: ok\. (\d+) passed;', (D/'regression.log').read_text())));assert nt==12
assert '189 passed; 0 failed' in (D/'lib_tests.log').read_text()
out=dict(status='PASS_SCOPED_MULTISTF_AND_GAUNT_PLANCK_FEEDBACK',parent='4dca20d24c96dc657ba3e97addc3d0fe02cd7fb3',rei_commit='b02edcc45c1a55f8a88176254d912df24876ffa7',physics=phy,powers=powers.tolist(),perturbative=pert,live=cases,matched_effect=effects,spectral=s,restart_byte_identical=True,lib_tests=189,targeted_tests=nt,production_admission='HOLD_EVOLVING_DISTORTED_SPECTRAL_RADIATION_AND_FULL_REC',native_subagent='NOT_RUN')
(D/'RESULTS.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],effects,'lead',lead)

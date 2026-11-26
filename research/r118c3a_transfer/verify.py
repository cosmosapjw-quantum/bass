import hashlib,json,re,gzip
from pathlib import Path
import numpy as np
D=Path(__file__).resolve().parent;B=D.parents[1];H=Path('/home/cosmosapjw/Downloads');I=Path('/home/cosmosapjw/worktrees/rei-htt-thomson-20261124')
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def j(p):return json.loads(Path(p).read_text())
def kv(p):return dict(x.split('=',1) for x in p.read_text().splitlines() if '=' in x)
for n in ('high_build','orders_build','exact','spectrum_green','bridge_build','spectral_oracle','lib_tests','regression','live_short','live_split','live_resume','live_long','a80','a40','a20','a10','shape','lrs','time','ell','k4one','k4two','k4ref','k3two'):
 assert int((D/(n+'.exit')).read_text())==0,n
for fn in ('HIGH.sha256','ORDERS.sha256','BRIDGE.sha256'):
 for line in (D/fn).read_text().splitlines():
  h,p=line.split(maxsplit=1);assert sha(B/p)==h,p
exact=j(D/'EXACT.json');assert [(r['STF_I2_power'],r['STF_I3_term']) for r in exact]==[('5/714','-2/1547'),('356/124355','-192/124355')]
physics={};orders={}
ls=(3,5,7,9,11)
for name in ('a80','a40','a20','a10','shape','lrs','time','ell'):
 p=D/(name+'.csv');r=np.genfromtxt(p,names=True,delimiter=',');assert len(r)==75 and np.all(np.isfinite(r.view(float)))
 rows=[]
 for l in ls:
    m=r['ell']==l;b=(r['re']+1j*r['im'])[m];t=(r['template_re']+1j*r['template_im'])[m]
    norm=float(np.linalg.norm(b));tn=float(np.linalg.norm(t));c=np.vdot(t,b)/np.vdot(t,t) if tn>1e-12 else 0j
    rows.append(dict(ell=l,norm=norm,template_norm=tn,coefficient_re=float(c.real),coefficient_im=float(c.imag),orthogonal_relative=float(np.linalg.norm(b-c*t)/norm)))
 physics[name]=dict(sha=sha(p),rows=rows)
for name in ('k4one','k4two','k4ref','k3two'):
 p=D/(name+'.csv');r=np.genfromtxt(p,names=True,delimiter=',');assert len(r)==525
 rows=[]
 for l in ls:
  k=(l+1)//2+1;norm=lambda n:float(np.linalg.norm((r['re']+1j*r['im'])[(r['ell']==l)&(r['order']==n)]))
  rows.append(dict(ell=l,order=k,coefficient=norm(k),lower_max=max(norm(n) for n in range(1,k))))
 orders[name]=dict(sha=sha(p),rows=rows)
assert max(x['lower_max'] for x in orders['k4ref']['rows'])<1e-18
assert all(abs(x['coefficient']/y['coefficient']-1)<1e-6 for x,y in zip(orders['k4ref']['rows'],orders['k4two']['rows']))
assert max(x['norm'] for x in physics['lrs']['rows'])<1e-13
for lidx,k in [(3,6),(4,7)]:
 v=np.array([physics[n]['rows'][lidx]['norm'] for n in ('a80','a40','a20','a10')])
 power=np.log2(v[:-1]/v[1:]);assert abs(power[1]-k)<.12
cases={}
for n in ('short','long','split','resume'):
 p=H/('bass_r118c3a_'+n);r=np.genfromtxt(p/'history.csv',names=True,delimiter=',');s=np.genfromtxt(p/'secondary_spectrum.csv',names=True,delimiter=',');err=np.genfromtxt(p/'error_components.csv',names=True,delimiter=',');ret=kv(p/'RETURN.txt')
 assert len(s)==len(r) and len(err)==2*(len(r)-1) and np.array_equal(s['a'],r['a'])
 assert ret['status']==('CHECKPOINT_COUNT' if n=='split' else 'COMPLETE') and np.all(np.diff(r['a'])>0)
 assert max(abs(r['ledger']))<1e-8 and max(abs(r['gauss']))<1e-8 and max(r['local_error'])<.00016
 bins=np.stack([s[f'bin{k}'] for k in range(12)],axis=1);assert min(bins.ravel())>=0
 assert max(abs(bins.sum(axis=1)-s['FF_U']))<1e-12*max(s['FF_U'])
 assert max(abs(s['FF_U']+s['FF_work']-s['FF_birth']))<1e-10*max(s['FF_birth'])
 assert np.max(abs(s['y']*4*s['BB_U']-r['cmb']))<1e-14*max(abs(r['cmb']))
 cp=p/'checkpoint';files={str(f.relative_to(p)):sha(f) for f in list(p.iterdir())+list(cp.iterdir()) if f.is_file()}
 man=(cp/'MANIFEST').read_text().splitlines();assert man[0]=='C3A_JOINT_V1' and man[1]==sha(B/'_rustcore/target/release/c3a_live_rei_bridge') and len(man)==9
 for line in man[3:]:
  h,f=line.split();assert files['checkpoint/'+f]==h
 head,ident=(cp/'rei.txt').read_text().split('\nGENERAL_SOURCE_IDENTITY\n',1);assert head.startswith('AXBI_CHECKPOINT_V9_GENERAL')
 assert (I/'rust/rei_microphysics/src/igm_thermal.rs').read_text() in ident
 for f in list(p.iterdir())+list(cp.iterdir()):
  if f.is_file():(D/(n+'_'+str(f.relative_to(p)).replace('/','_')+'.gz')).write_bytes(gzip.compress(f.read_bytes(),mtime=0))
 cases[n]=dict(raw=str(p),files=files,return_=ret,terminal={k:float(r[k][-1]) for k in ('z','T','xHII','xHeIII','h','escape','cmb','ledger','gauss')},spectrum={k:float(s[k][-1]) for k in s.dtype.names[2:]},max_ledger=float(max(abs(r['ledger']))),max_gauss=float(max(abs(r['gauss']))),ff_ledger_relative=float(max(abs(s['FF_U']+s['FF_work']-s['FF_birth']))/max(s['FF_birth'])))
a=H/'bass_r118c3a_split';b=H/'bass_r118c3a_resume';p=H/'bass_r118c3a_short'
for f in ('history.csv','secondary_spectrum.csv','error_components.csv'):
 x=(a/f).read_bytes().splitlines(keepends=True);y=(b/f).read_bytes().splitlines(keepends=True)
 assert b''.join(x+y[1 if f=='error_components.csv' else 2:])==(p/f).read_bytes()
for f in (p/'checkpoint').iterdir():assert sha(f)==sha(b/'checkpoint'/f.name)
assert sha(p/'history.csv')==sha(H/'bass_r118c2z_final_time/history.csv')
s=j(D/'SPECTRAL_ORACLE.json');assert s['Y_energy_over_planck']>3.999999999
for k in ('short','long'):
 for path,h in s[k]['inputs'].items():assert sha(path)==h
 assert s[k]['rows'][-1]['bin_l1']<1e-8
assert s['short']['gray_absorption']['net_redshifted']<0<s['long']['gray_absorption']['net_redshifted']
nt=sum(map(int,re.findall(r'test result: ok\. (\d+) passed;', (D/'regression.log').read_text())));assert nt==12
assert '189 passed; 0 failed' in (D/'lib_tests.log').read_text()
out=dict(status='PASS_SCOPED_HIGH_ODD_CHANNELS_GRAY_SPECTRUM',parent='5f75ce73b75af4c846f500ce4208d93b22eec3ca',rei_commit='52e7d84d47e1e85a8926755bdc130845e23cc4e0',physics=physics,orders=orders,exact=exact,live=cases,oracle=s,restart_byte_identical=True,lib_tests=189,targeted_tests=nt,production_admission='HOLD_PHYSICAL_NET_SPECTRAL_RADIATIVE_EXCHANGE',native_subagent='NOT_RUN')
(D/'RESULTS.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],nt,'long',cases['long']['terminal'])

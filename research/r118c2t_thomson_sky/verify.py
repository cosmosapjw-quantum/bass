import hashlib,json,re
from pathlib import Path
import numpy as np
D=Path(__file__).resolve().parent;B=D.parents[1]
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
for f in ('green.exit','owner.exit','spin.exit','spin_n32.exit','spin_n64.exit','spin_reproduction.exit','handoff.exit','lib_tests.exit','regression.exit'):assert int((D/f).read_text())==0
assert '189 passed; 0 failed' in (D/'lib_tests.log').read_text()
src=json.loads((D.parent/'r118c2r_multispecies/SOURCES.json').read_text())
for p,h in src.items():assert sha(p)==h
assert sha(D/'NE.csv')==sha(D.parent/'r118c2r_multispecies/rei_q256.csv')
cases={}
for p in sorted(D.glob('owned*.csv')):
 r=np.genfromtxt(p,names=True,delimiter=',')
 assert np.all(np.isfinite(r.view(float))) and abs(r['a'][-1]-.2)<1e-13 and np.min(r['min_screen'])>0
 assert np.max(abs(r['det']-1))<1e-10 and max(r['collision'])<5e-12 and np.max(r['Eodd'])<1e-12 and np.max(r['Beven'])<1e-12
 cases[p.stem]=dict(rows=len(r),gauss=float(max(abs(r['gauss']))),collision=float(max(r['collision'])),min_screen=float(min(r['min_screen'])),terminal={k:float(r[k][-1]) for k in ('h','S0','S1','S2','S3','S4','E2','B3','Eodd','Beven','photon')},sha=sha(p))
assert len(cases)==8
free=np.genfromtxt(D/'owned_0.03_512_6_free.csv',names=True,delimiter=',')
old=np.genfromtxt(D.parent/'r118c2s_geometry/owner_0.03_512_32_8.csv',names=True,delimiter=',')
gap=max(float(np.max(abs(free[k]-old[k]))) for k in ('h','S0','S1','S2','S3','S4','F00','F01','F02','F10','F11','F12','F20','F21','F22'))
assert gap<1e-9
assert cases['owned_0.03_512_4_scatter']['gauss']<cases['owned_0.03_256_4_scatter']['gauss']/3.9
r=np.genfromtxt(D/'spin.csv',names=True,delimiter=',',dtype=None,encoding='utf8');s=np.genfromtxt(D/'spin_n64.csv',names=True,delimiter=',',dtype=None,encoding='utf8')
assert len(r)==len(s)==96 and sha(D/'spin.csv')==sha(D/'spin_n32.csv')
assert max(s['Eodd'])<1e-12 and max(s['Beven'])<1e-12 and max(s['B3'][s['case']=='aligned'])<1e-12
f=s[(s['lmax']==10)&(s['case']!='aligned')]
orders={}
for mode in ('seed','born'):
 for case in ('AB','BA','loop'):
  z=s[(s['lmax']==10)&(s['mode']==mode)&(s['case']==case)]
  orders[mode+'_'+case]=np.log2(z['B3'][:-1]/z['B3'][1:]).tolist()
assert abs(orders['seed_AB'][-1]-1)<.01 and abs(orders['seed_loop'][-1]-2)<.01 and abs(orders['born_AB'][-1]-2)<.01
m=(s['lmax']==10)&(s['case']!='aligned')
refine=float(max(abs(r['B3'][m]/s['B3'][m]-1)));assert refine<2e-4
seed=s[(s['lmax']==10)&(s['mode']=='seed')]
assert max(seed['ref_gap'])<3e-8
h=s[(s['lmax']==8)&(s['case']!='aligned')]
assert np.array_equal(h['eps'],f['eps']) and np.array_equal(h['case'],f['case']) and np.array_equal(h['mode'],f['mode'])
l_gap=float(max(abs(h['B3']/f['B3']-1)));assert l_gap<2e-3
for line in (D/'HANDOFF.sha256').read_text().splitlines():
 hh,p=line.split(maxsplit=1);assert sha(p)==hh
out=dict(status='PASS_SCOPED_OWNED_REST_THOMSON_AND_ORDERED_SKY',parent='6f631f4e97310c173bcbd1ad73f7d01c8f09c3f3',cases=cases,source_raw=src,input_ne_sha=sha(D/'NE.csv'),free_control_max_absolute_gap=gap,spin_native_runs=192,spin_orders=orders,spin_time_relative=refine,spin_lmax_relative=l_gap,seed_max_reference_gap=float(max(seed['ref_gap'])),max_forbidden=float(max(max(s['Eodd']),max(s['Beven']))),lib_tests=189,targeted_tests=sum(int(x) for x in re.findall(r'test result: ok\. (\d+) passed;', (D/'regression.log').read_text())),scope='exact represented massive species, nonlinear H/S/F and harmonic photon field, rest elastic Thomson, prescribed actual C2Q q256 ne, no thermal/recoil feedback; independent pulse sky',production_admission='HOLD_LIVE_GAS_AND_GENERAL_GEOMETRY_COUPLING',native_subagent='NOT_RUN')
(D/'RESULTS.json').write_text(json.dumps(out,indent=2)+'\n')
print({k:v for k,v in out.items() if k not in ('cases','source_raw')})

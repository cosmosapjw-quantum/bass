import json,hashlib,re
from pathlib import Path
import numpy as np
D=Path(__file__).resolve().parent
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def j(p):return json.loads(p.read_text())
for f in ('green.exit','uv_green.exit','uv_coupled_test.exit','uv_build.exit','uv_run.exit','uv_refine.exit','lib_tests.exit','regression.exit','history_sign.exit'):assert int((D/f).read_text())==0
assert 'cases=75' in (D/'green.log').read_text() and '189 passed; 0 failed' in (D/'lib_tests.log').read_text()
g=j(D/'GAS.json')
for p,h in g['sources'].items():assert sha(p)==h
for line in (D/'UV_BINARY.sha256').read_text().splitlines():
 h,p=line.split(maxsplit=1);assert sha(p)==h
cases={};data={};rho0=3*299792458.**2*(2.1842852410855023e-18)**2/(8*np.pi*6.67430e-11)
for p in sorted(D.glob('uv_*.csv')):
 r=np.genfromtxt(p,names=True,delimiter=',');assert np.all(np.isfinite(r.view(float))) and abs(r['a'][-1]-.2)<1e-13
 assert min(r['UV'])>=0 and max(abs(r['ledger']))<2e-10*max(r['emitted'][-1],1)
 P=np.stack([r['Pxx'],r['Pxy'],r['Pxz'],r['Pxy'],r['Pyy'],r['Pyz'],r['Pxz'],r['Pyz'],r['Pzz']],axis=1).reshape(-1,3,3)
 assert max(abs(np.trace(P,axis1=1,axis2=2)-r['UV']))<1e-9*max(r['UV'][-1],1)
 pi=P-r['UV'][:,None,None]*np.eye(3)/3
 norm=np.linalg.norm(pi,axis=(1,2));assert np.all(norm<=np.sqrt(2/3)*r['UV']+1e-10)
 fac=g['nh0']*1.602176634e-19/rho0/r['a']**3/r['h']**2
 row=dict(rows=len(r),sha=sha(p),gauss=float(max(abs(r['gauss']))),ledger=float(max(abs(r['ledger']))),h=float(r['h'][-1]),UV=float(r['UV'][-1]),work=float(r['work'][-1]),reservoir=float(r['reservoir'][-1]),emitted=float(r['emitted'][-1]),births=float(r['births'][-1]),pi_norm=float(norm[-1]),J2z=float(1.5*r['Pzz'][-1]-.5*r['UV'][-1]),max_Omega_UV=float(max(fac*r['UV'])),max_pi_over_crit=float(max(fac*norm)))
 cases[p.stem]=row;data[p.stem]=r
assert len(cases)==11
pairs=[]
for n,q,amp in [(256,64,1),(512,64,1),(512,128,1),(1024,128,1),(512,64,10000)]:
 x=data[f'uv_{n}_{q}_{amp}_on'];y=data[f'uv_{n}_{q}_{amp}_off'];s=np.array([x[f'S{i}'] for i in range(5)]);d=s-np.array([y[f'S{i}'] for i in range(5)])
 pairs.append(dict(n=n,q=q,amp=amp,h_relative=float(x['h'][-1]/y['h'][-1]-1),shear_relative=float(np.linalg.norm(d[:,-1])/np.linalg.norm(s[:,-1])),max_shear_abs=float(max(np.linalg.norm(d,axis=0)))))
assert all(x['h_relative']<0 for x in pairs)
assert abs(pairs[-1]['h_relative']/10000/pairs[1]['h_relative']-1)<1e-4
h=j(D/'HISTORY_SIGN.json');assert h['status']=='DERIVED_SIGN_AND_CANCELLATION_NUMERIC'
r=dict(status='PASS_SCOPED_MAGNETIC_KERNEL_UV_RESERVOIR',parent='f6e56a22d94943cb270bc4640b97a8816a2ce65f',basis_cases=75,history=h,uv_cases=cases,pairs=pairs,gas_sources=g,gas_sha=sha(D/'GAS.csv'),lib_tests=189,targeted_tests=sum(int(x) for x in re.findall(r'test result: ok\. (\d+) passed;', (D/'regression.log').read_text())),production_admission='HOLD_UV_SPECTRAL_STRESS_AND_LIVE_GAS_ENERGY',native_subagent='NOT_RUN')
(D/'RESULTS.json').write_text(json.dumps(r,indent=2)+'\n')
print('pairs',pairs,'max UV omega physical',max(v['max_Omega_UV'] for k,v in cases.items() if '_1_' in k))

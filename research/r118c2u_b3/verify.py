import json,hashlib,re
from pathlib import Path
import numpy as np
D=Path(__file__).resolve().parent;P=D.parent/'r118c2t_thomson_sky'
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
j=json.loads((P/'RESULTS.json').read_text())
g=P/'owned_0.03_512_6_scatter.csv';assert sha(g)==j['cases'][g.stem]['sha']
assert sha(P/'NE.csv')==j['input_ne_sha']
for p,h in j['source_raw'].items():assert sha(p)==h
w=json.loads((D/'WEAK_SOURCES.json').read_text())
for p,h in w.items():assert sha(p)==h
for f in ('green.exit','build.exit','history.exit','orders.exit','lib_tests.exit','regression.exit'):assert int((D/f).read_text())==0
assert 'basis pairs=25' in (D/'green.log').read_text()
rows={}
for name in ('c2t','weak'):
 r=np.genfromtxt(D/(name+'.csv'),names=True,delimiter=',',dtype=None,encoding='utf8')
 assert len(r)==8 and max(r['forbidden'])<2e-15
 f=r[r['n']==1024];assert np.all(np.diff(f['relative_vector_error'])<0)
 assert f['relative_vector_error'][-1]<.021
 assert abs(f['analytic_B3'][0]/(f['analytic_B3'][-1]*64)-1)<1e-11
 rows[name]=[{k:(x[k].item()) for k in r.dtype.names} for x in f]
r=np.genfromtxt(D/'orders_1024.csv',names=True,delimiter=',');s=np.genfromtxt(D/'orders_512.csv',names=True,delimiter=',')
v=(r['re']+1j*r['im']).reshape(4,7);q=(s['re']+1j*s['im']).reshape(4,7);m=r['monopole'].reshape(4,7)[:,0]
assert np.linalg.norm(v[0])==0
assert np.linalg.norm(v[1]-q[1])/np.linalg.norm(v[1])<1e-6
assert abs(np.linalg.norm(v[1])/rows['c2t'][0]['analytic_B3']-1)<1e-10
order=[]
for x in rows['c2t']:
 a=x['scale'];native=x['native_B3'];cub=np.linalg.norm(v[1]*a*a+v[2]*a**3)
 quart=np.linalg.norm(sum(v[i]*a**(i+1) for i in range(4)))/(1+sum(m[i]*a**(i+1) for i in range(4)))
 order.append(dict(scale=a,native=native,quadratic=float(np.linalg.norm(v[1]*a*a)),cubic=float(cub),quartic=float(quart),cubic_norm_relative=float(abs(cub/native-1)),quartic_norm_relative=float(abs(quart/native-1))))
assert order[0]['quartic_norm_relative']<2e-6
assert '189 passed; 0 failed' in (D/'lib_tests.log').read_text()
out=dict(status='PASS_SCOPED_B3_ANALYTIC_AND_ACTUAL_HISTORY',parent='7436754661dfaa2cec6cc98bbba41ace0f783121',basis_pairs=25,history_runs=16,order_runs=2,history=rows,orders=order,order_norms=np.linalg.norm(v,axis=1).tolist(),geometry_sha=sha(g),ne_sha=sha(P/'NE.csv'),weak_ne_sha=sha(D/'WEAK_NE.csv'),weak_sources=w,lib_tests=189,targeted_tests=sum(int(x) for x in re.findall(r'test result: ok\. (\d+) passed;', (D/'regression.log').read_text())),production_admission='HOLD_LIVE_GEOMETRY_GAS_AND_OBSERVATIONAL_MAPPING',native_subagent='NOT_RUN')
(D/'RESULTS.json').write_text(json.dumps(out,indent=2)+'\n');print('orders',order)

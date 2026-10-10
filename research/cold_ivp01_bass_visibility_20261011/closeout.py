"""Read stored campaign only; no build, test, example, solver or chemistry launch."""
import hashlib,json,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[1]; EV=HERE/'evidence'
raw=json.loads((EV/'CAMPAIGN_RAW.json').read_text()); v=json.loads((EV/'VALIDATION.json').read_text())
def parsed(name):
 r=next(r for r in raw if r['name']==name)
 return {s.split()[0]:list(map(float,s.split()[1:])) for s in r['stdout'].splitlines()}
base=parsed('id0:n32'); doubled=parsed('density_x2'); tail=parsed('tail_0.25'); eps=2**-52
for key,bound in [('survival','survival_bound'),('mass','mass_bound')]:
 for i,(a,b,limit) in enumerate(zip(base[key],doubled[key],base[bound])):
  excess=max(0.,abs(a-b)-limit)
  assert excess<=64*eps,(key,i,excess)
  v['checks'].append({'name':f'observed_opacity_bound:{key}:{i}','value':excess,'limit':64*eps,'pass':True})
for i,(a,b) in enumerate(zip(base['mass'],tail['mass'])):
 err=abs(b-a*__import__('math').exp(-.25)); assert err<=64*eps
 v['checks'].append({'name':f'tail_mass_scale:{i}','value':err,'limit':64*eps,'pass':True})
v['status']='IMPLEMENTATION_VALIDATION_PASS_PENDING_ASTRA_REVIEW'
(EV/'VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n')
diff=subprocess.run(['git','diff','--check'],cwd=ROOT,capture_output=True,text=True)
assert diff.returncode==0,diff.stderr
(EV/'DIFF_CHECK.json').write_text(json.dumps({'exit_code':diff.returncode,'stdout':diff.stdout,'stderr':diff.stderr},indent=2)+'\n')
source=json.loads((EV/'SOURCE_PRELAUNCH.json').read_text())['source_hashes']
assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in source.items())
dag={'node':'COLD_IVP01_BASS_FINITE_VISIBILITY01','execution':'IMPLEMENTATION_VALIDATION_PASS','independent_astra_decision':'PENDING','publication':'NOT_AUTHORIZED','scientific_admission':'HOLD','next_executable_action':'Fresh Astra read-only diff/raw evidence review; parent controller recomputes scoped READY DAG after decision','claim_ceiling':v['claim_ceiling']}
(HERE/'DAG.json').write_text(json.dumps(dag,indent=2)+'\n')

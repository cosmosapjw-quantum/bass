"""One bounded case per child; JSON written immediately on success."""
from pathlib import Path
import json,sys
import emission_split as es
ROOT=Path(__file__).resolve().parents[1]
mode=sys.argv[1]
if mode=='controls':
    out={'oracle':es.prescribed_oracle(),'runs':[]}
    for scheme in ['lie','strang']:
        for n in [16,32,64]:
            run=es.trajectory(n,scheme=scheme,prescribed=True)
            run['oracle_error']=es.distance(run['final'],out['oracle']);out['runs'].append(run)
    target=ROOT/'results/prescribed_controls.json'
else:
    n=int(sys.argv[2]);tight=mode=='tight'
    out=es.trajectory(n,rtol=2e-13 if tight else 2e-12,atol=2e-15 if tight else 2e-14)
    target=ROOT/f'results/{mode}_{n}.json'
target.write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
print(json.dumps({'output':str(target),'mode':mode,'steps':out.get('steps'),'nfev':out.get('nfev')}))

"""Secondary bounded falsification, independent of the stored-source enclosure code."""
import json,sys
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'package'))
from bianchi.nonperturbative.einstein_tabulated_source import TabulatedRadiation,certified_tabulated_pressure
from science_verify import MU,PHI,WEIGHTS, independent_continuum

rng=np.random.default_rng(1952)
rows=[]
for refine in (1,2,4):
    s=TabulatedRadiation(MU,PHI,WEIGHTS,refinement=refine,backend='python_oracle')
    b=certified_tabulated_pressure(s,[0.,0.,0.],[.08,.08,.08])
    for k in range(12):
        ell=rng.uniform(0.,.08,3)
        E,p=independent_continuum(s,ell,nt=40)
        ed,pd=s.moments(ell)
        gap=float(np.max(np.abs(p-pd)))
        if gap > b['max_pressure_upper']:
            raise AssertionError((refine,k,gap,b['max_pressure_upper']))
        rows.append({'refine':refine,'ell':ell.tolist(),'gap':gap,'source_upper':b['max_pressure_upper'],'gap_to_bound':gap/b['max_pressure_upper']})
# conservation derivative from direct finite difference, not used for certificate
s=TabulatedRadiation(MU,PHI,WEIGHTS,refinement=2,backend='python_oracle')
max_d=0.
for ell in [(0.,0.,0.),(.01,.03,.06),(.04,.02,.05)]:
    e,p=s.moments(ell)
    h=1e-5
    for j in range(3):
        ep=np.array(ell);em=np.array(ell);ep[j]+=h;em[j]-=h
        fd=(s.moments(ep)[0]-s.moments(em)[0])/(2*h)
        max_d=max(max_d,abs(fd+e+p[j]))
assert max_d<3e-9,max_d
assert max(row['gap_to_bound'] for row in rows)<1.
res={'cases':len(rows),'maximum_ratio':max(row['gap_to_bound'] for row in rows),'maximum_energy_derivative_residual':max_d,'all_within_predicted_uniform_bound':True,'records':rows}
(R/'evidence/STRESS_RESULTS.json').write_text(json.dumps(res,indent=2)+'\n')
print(json.dumps({k:v for k,v in res.items() if k!='records'},indent=2))

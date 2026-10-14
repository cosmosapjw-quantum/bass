"""One bounded check pass. Floating comparisons are not interval certificates."""
from pathlib import Path
import json,time,hashlib
import numpy as np
from fa03 import solve_moments,solve_energy,full_quadratic,p
R=Path(__file__).resolve().parents[1]
t0=time.monotonic();base=(.008,.010);opts=dict(nr=3,nphi=12,steps=64)
J=solve_moments(*base,jets=True,**opts)
np.savez(R/'evidence/fa03_jet.npz',coefficients=J)
checks={};values={}
grey=p.solve_cap(*base,jets=True,**opts)
checks['grey_jet_norm']=float(np.max(np.abs(J[0]-grey)))
checks['grey_energy_norm']=p.trnorm(solve_energy(*base,0,**opts)-J[0,0])
he=1e-3
fp=solve_energy(*base,he,**opts);fm=solve_energy(*base,-he,**opts);f0=solve_energy(*base,0,**opts)
checks['slope_finite_difference_error']=p.trnorm((fp-fm)/(2*he)-J[3,0])
checks['second_epsilon_finite_difference_error']=p.trnorm((fp-2*f0+fm)/he**2-J[5,0])
for i,name in enumerate(['chi','psi']):
    h=1e-4;plus=list(base);minus=list(base);plus[i]+=h;minus[i]-=h
    vp=solve_moments(*plus,**opts)[3];vm=solve_moments(*minus,**opts)[3]
    checks['mixed_'+name+'_finite_difference_error']=p.trnorm((vp-vm)/(2*h)-J[3,1+i])
refined=solve_moments(*base,steps=128,nr=3,nphi=12)
checks['time_refinement_max_state_error']=max(p.trnorm(refined[i]-J[i,0]) for i in range(6))
angular=solve_moments(*base,steps=64,nr=5,nphi=20)
checks['angular_refinement_max_state_error']=max(p.trnorm(angular[i]-J[i,0]) for i in range(6))
values['stokes_base']=p.stokes(J[0,0]).tolist()
values['stokes_d_epsilon']=p.stokes(J[3,0]).tolist()
values['stokes_d_chi_epsilon']=p.stokes(J[3,1]).tolist()
values['stokes_d_psi_epsilon']=p.stokes(J[3,2]).tolist()
values['stokes_d_epsilon_epsilon']=p.stokes(J[5,0]).tolist()
finite=[]
for h in [.02,.01,.005]:
    dx=np.array([.3,-.15,1.])*h
    F=solve_energy(*(np.array(base)+dx[:2]),dx[2],**opts)
    quadratic=full_quadratic(J,dx)
    linear=J[0,0]+dx[0]*J[0,1]+dx[1]*J[0,2]+dx[2]*J[3,0]
    finite.append(dict(dx=dx.tolist(),linear_error=p.trnorm(F-linear),quadratic_error=p.trnorm(F-quadratic),linear_analytic_bound=125*h*h,quadratic_analytic_bound=1250*h**3,min_eigenvalue=float(np.linalg.eigvalsh(F).min())))
checks['minimum_finite_psd_eigenvalue']=min(c['min_eigenvalue'] for c in finite)
# Negative controls: mean-energy collapse and scaling rotation are not the specified model.
meanonly=solve_energy(*base,.1,ne=1,**opts)
correct=solve_energy(*base,.1,ne=8,**opts)
checks['mean_energy_surrogate_discrepancy']=p.trnorm(meanonly-correct)
limits={'grey_jet_norm':2e-14,'grey_energy_norm':2e-14,'slope_finite_difference_error':1e-8,'second_epsilon_finite_difference_error':5e-8,'mixed_chi_finite_difference_error':1e-7,'mixed_psi_finite_difference_error':1e-7,'time_refinement_max_state_error':2e-9,'angular_refinement_max_state_error':2e-10}
verdict={k:checks[k]<v for k,v in limits.items()}
verdict['positive_finite_examples']=checks['minimum_finite_psd_eigenvalue']>0
verdict['nonzero_mean_energy_bias']=checks['mean_energy_surrogate_discrepancy']>1e-6
verdict['finite_remainders_below_analytic_bounds']=all(c['linear_error']<c['linear_analytic_bound'] and c['quadratic_error']<c['quadratic_analytic_bound'] for c in finite)
out={'scope':'binary64 empirical affected-obligation checks only','base':base,'configuration':opts,'checks':checks,'predeclared_limits':limits,'verdict':verdict,'all_checks_passed':all(verdict.values()),'values':values,'finite':finite,'elapsed_s':time.monotonic()-t0,'empirical_provider_error':None,'continuum_certificate':None}
(R/'evidence/FA03_CHECKS.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out,indent=2));raise SystemExit(0 if out['all_checks_passed'] else 1)

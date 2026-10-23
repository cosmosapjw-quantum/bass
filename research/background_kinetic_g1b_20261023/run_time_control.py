"""Targeted time-grid controls after equal-NFEV tolerance pairs were observed.

No old case is overwritten/replayed: this explicitly halves the step ceiling.
"""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
os.environ.setdefault('OMP_NUM_THREADS','1')
from pathlib import Path
import json,time
import numpy as np
from scipy.integrate import solve_ivp
import run_curved as rc
ROOT=Path(__file__).resolve().parent

def main():
    out=ROOT/'evidence/time_step_001';out.mkdir(exist_ok=False)
    rc.dump(out/'CONTRACT.json',dict(reason='default/tight pairs both317 RHS; add distinct max_step .02 control at same grid',
            inherited_gate=rc.GATE,old_runs_replayed=0,new_runs=2,scope='V/VIII r8 a14, tau0..0.8',
            reference='curved_002 default max_step .04',atol=2e-14,rtol=2e-12))
    results=[]
    for family in ('V','VIII'):
        model,z0,info=rc.make_case(family,8,14);start=time.perf_counter();env=np.zeros(3)
        def fun(t,z):
            nonlocal env
            env=np.maximum(env,rc.check_envelope(z))
            return model.rhs(t,z)
        sol=solve_ivp(fun,(0.,.8),z0,method='DOP853',t_eval=np.linspace(0,.8,33),rtol=2e-12,atol=2e-14,max_step=.02)
        if not sol.success:raise RuntimeError(sol.message)
        ds=[rc.diagnostics(model,z) for z in sol.y.T];obs=np.array([d['observable'] for d in ds])
        values={key:np.array([d[key] for d in ds]) for key in ('mismatch','core_constraint','kinetic_constraint','minimum_weight')}
        raw=out/(family+'_half_step.npz')
        np.savez_compressed(raw,tau=sol.t,state=sol.y,observable=obs,mass=model.mass,sectors=model.sectors,**values)
        with np.load(ROOT/'evidence/curved_002'/f'{family}_r8_a14.npz') as f:
            observable_error=rc.compare_observables(obs,f['observable'])
            state_error=rc.compare_observables(sol.y,f['state'])
        row=dict(family=family,nfev=sol.nfev,observable_error=observable_error,full_state_error=state_error,
                 max_RHS_envelope=env.tolist(),maxima={k:float(values[k].max()) for k in ('mismatch','core_constraint','kinetic_constraint')},
                 raw_sha256=rc.sha(raw),raw_bytes=raw.stat().st_size,elapsed_s=time.perf_counter()-start,
                 source=dict(rc.source_lock(),**{'run_time_control.py':rc.sha(Path(__file__))}),initial=info)
        rc.dump(out/(family+'.json'),row);results.append(row);print(json.dumps(row),flush=True)
    result=dict(status='PASS_SCOPED' if max(x['full_state_error'] for x in results)<rc.GATE and max(max(x['maxima'].values()) for x in results)<rc.GATE else 'FAIL',
                additional_IVPs=2,old_replays=0,cases=results)
    rc.dump(out/'RESULTS.json',result)
    return result
if __name__=='__main__':main()

#!/usr/bin/env python3
"""Bounded angular-constraint versus angular-refinement measurement campaign.

Creates new output only. It does not run a coupled Einstein evolution or native
finite-bin deposition. All source-frame weights are frozen for every d sweep.
"""
from __future__ import annotations
import argparse
from collections import Counter
from dataclasses import asdict
from functools import lru_cache
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import resource
import subprocess
import sys
import time
import numpy as np
import scipy
from scipy.integrate import quad
from angular_balance import lrs_rule,project as project2
from angular_p24 import project,feasibility,ALGORITHM_ID
from shear_response import response,moments,derivative_diagnostics

BIRTH_B=[-.6,-.4,-.3,-.2,0.,.2,.3,.4,.6,.8,1.]
N_MU=[8,16,32,64,128]
D_SWEEP=[-.2,-.1,-.05,-.02,-.01,0.,.01,.02,.05,.1,.2]


@lru_cache(maxsize=512)
def continuum(d):
    if d==0:return {'F':1.,'G':0.,'A':0.,'quad_estimated_error':0.}
    a,c=math.exp(2*d),math.exp(-4*d)
    def rr(mu):return math.sqrt(a*(1-mu*mu)+c*mu*mu)
    def dd(mu):return (c*mu*mu-a*(1-mu*mu)/2)/rr(mu)
    f,ef=quad(rr,0,1,epsabs=2e-14,epsrel=2e-14,limit=100)
    g,eg=quad(dd,0,1,epsabs=2e-14,epsrel=2e-14,limit=100)
    return {'F':f,'G':g,'A':g/f,'quad_estimated_error':ef+eg}


def array(v):
    if isinstance(v,np.ndarray):return v.tolist()
    if isinstance(v,np.floating):return float(v)
    if isinstance(v,np.integer):return int(v)
    raise TypeError(type(v).__name__)


def write_json(path,value):
    with path.open('x') as f:json.dump(value,f,indent=2,default=array,allow_nan=False);f.write('\n')


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--rust-probe',type=Path);args=ap.parse_args()
    args.out.mkdir(parents=True,exist_ok=False);out=args.out.resolve();here=Path(__file__).resolve().parent
    start=time.monotonic();rows=[];successful=[];summary=Counter()
    source_names=['angular_balance.py','angular_p24.py','shear_response.py','test_s3.py','run_s3_campaign.py']
    sources={n:hashlib.sha256((here/n).read_bytes()).hexdigest() for n in source_names}
    for n in N_MU:
        for b in BIRTH_B:
            mu,q=lrs_rule(b,n)
            for mode in ['prior','P2','P24']:
                rec={'id':f'b{b:+.2f}_n{n}_{mode}','birth_b':b,'n_mu':n,'constraint':mode,
                     'P24_feasibility':asdict(feasibility(mu))}
                try:
                    if mode=='prior':weights=q.copy()
                    elif mode=='P2':weights=project2(mu,q).weights
                    else:
                        projected=project(mu,q);weights=projected.weights
                        rec.update(multipliers=projected.multipliers,iterations=projected.iterations,
                                   evaluations=projected.evaluations,kl=projected.kl)
                    rec.update(status='MEASURED',weights=weights,mu=mu,prior=q,
                               min_weight=float(weights.min()),normalization_defect=abs(math.fsum(weights)-1),
                               diagnostics=derivative_diagnostics(mu,weights))
                    rec['response']=[dict(d=d,**response(d,mu,weights),
                        A_error=response(d,mu,weights)['A']-continuum(d)['A']) for d in D_SWEEP]
                    h=1e-5
                    rec['central_A_prime_h1e_5']=(response(h,mu,weights)['A']-response(-h,mu,weights)['A'])/(2*h)
                    rec['derivative_error']=rec['central_A_prime_h1e_5']-rec['diagnostics']['A_prime']
                    assert rec['min_weight']>0 and rec['normalization_defect']<=5e-16
                    if mode in ['P2','P24']:
                        assert abs(rec['diagnostics']['moments'][2])<=3.5e-15 # independent Legendre recurrence roundoff
                    if mode=='P24':
                        # Actual constraint gate uses the algorithm's direct polynomial, not this recurrence.
                        assert max(abs(projected.residuals))<=3e-15
                        successful.append(rec)
                except (ValueError,ArithmeticError) as error:
                    rec.update(status='REJECTED',error=str(error),failure_class=(
                        'support_feasibility' if str(error).startswith('INFEASIBLE') else
                        'numerical_feasibility_unresolved' if str(error).startswith('FEASIBILITY_UNRESOLVED') else
                        'numerical_algorithm'))
                rows.append(rec);summary[(mode,rec['status'],rec.get('error',''))]+=1
    write_json(out/'ANGULAR_CAMPAIGN.json',{'rows':rows,'source_sha256':sources,
        'continuum_reference':[dict(d=d,**continuum(d)) for d in D_SWEEP]})
    fixtures=out/'P24_INPUT.txt'
    with fixtures.open('x') as f:
        f.write(f'{ALGORITHM_ID} {len(successful)}\n')
        for r in successful:
            f.write(f"{r['id']} {r['n_mu']}\n")
            for m,q in zip(r['mu'],r['prior']):f.write(f'{m:.17e} {q:.17e}\n')
    write_json(out/'P24_EXPECTED.json',{'schema':ALGORITHM_ID,'cases':successful})

    # Cross-check adaptive integration against a distinct GL rule and an 80-digit
    # binomial integral at small d. This is a measured reference agreement.
    lm,lw=np.polynomial.legendre.leggauss(256);lw/=math.fsum(lw)
    ref_errors=[abs(response(d,lm,lw)['A']-continuum(d)['A']) for d in D_SWEEP]
    from decimal import Decimal,localcontext
    import importlib.util
    spec=importlib.util.spec_from_file_location('independent_s3',here/'evidence_s3/theory_independent.py')
    independent=importlib.util.module_from_spec(spec);spec.loader.exec_module(independent)
    decimal_errors=[]
    with localcontext() as ctx:
        ctx.prec=80
        for d in [-.02,-.01,.01,.02]:
            decimal_errors.append(abs(float(independent.continuum_response_decimal(Decimal(str(d))))-continuum(d)['A']))
    assert max(ref_errors+decimal_errors)<3e-13
    measured=[r for r in rows if r['status']=='MEASURED']
    matched=[]
    for p24 in successful:
        p2=next(r for r in rows if r['n_mu']==p24['n_mu'] and r['birth_b']==p24['birth_b'] and r['constraint']=='P2')
        for a,b in zip(p24['response'],p2['response']):
            matched.append({'id':p24['id'],'d':a['d'],'P2_error':b['A_error'],'P24_error':a['A_error']})
    write_json(out/'MATCHED_CONSTRAINT_COMPARISON.json',matched)

    os.environ.setdefault('MPLCONFIGDIR',str(out/'mpl_cache'))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.size':10,'axes.grid':True,'grid.alpha':.22,'figure.dpi':150})
    fig,axs=plt.subplots(1,2,figsize=(11.5,4.2),constrained_layout=True)
    birth=.3;d_grid=np.geomspace(1e-4,.3,64);colors={'prior':'#71717a','P2':'#d97706','P24':'#0369a1'}
    for mode in ['prior','P2','P24']:
        row=next(r for r in rows if r['birth_b']==birth and r['n_mu']==8 and r['constraint']==mode)
        err=[abs(response(float(d),row['mu'],row['weights'])['A']-continuum(float(d))['A']) for d in d_grid]
        axs[0].loglog(d_grid,np.maximum(err,1e-16),label=mode,color=colors[mode],lw=1.8)
    axs[0].set(xlabel=r'$d=b(x)-b(u)$',ylabel=r'$|\mathcal A_Q-\mathcal A_{iso}|$',title='Same 8 rays: change constraints')
    axs[0].legend()
    for mode in ['prior','P2','P24']:
        errors=[]
        for n in N_MU:
            row=next(r for r in rows if r['birth_b']==birth and r['n_mu']==n and r['constraint']==mode)
            errors.append(abs(response(.2,row['mu'],row['weights'])['A']-continuum(.2)['A']))
        axs[1].loglog(N_MU,np.maximum(errors,1e-16),'o-',label=mode,color=colors[mode],lw=1.5)
    axs[1].set(xlabel='Angular rays',ylabel=r'$|\mathcal A_Q-\mathcal A_{iso}|$',title=r'Fixed $d=0.2$: refine angular rays')
    axs[1].set_xticks(N_MU,[str(n) for n in N_MU]);axs[1].legend()
    fig.suptitle(r'Frozen birth weights, $b(u)=0.3$; spectral owner unchanged',fontsize=12)
    fig.savefig(out/'S3_ANGULAR_RESPONSE.png');fig.savefig(out/'S3_ANGULAR_RESPONSE.pdf');plt.close(fig)

    testcmd=[sys.executable,'-m','unittest','-v','test_s3']
    tested=subprocess.run(testcmd,cwd=here,text=True,capture_output=True,timeout=60)
    (out/'TEST_S3.log').write_text('$ '+' '.join(testcmd)+'\n'+tested.stdout+tested.stderr+f'\nEXIT_CODE={tested.returncode}\n')
    assert tested.returncode==0
    receipt={'schema':'bass.s3.angular_campaign.v1','status':'PASS_SCOPED_MEASUREMENT_AND_CONSTRAINTS',
        'source_sha256':sources,'python':sys.version,'numpy':np.__version__,'scipy':scipy.__version__,
        'test_command':testcmd,'test_exit':tested.returncode,'new_tests':14,
        'parameter_grid':{'birth_b':BIRTH_B,'n_mu':N_MU,'d':D_SWEEP,'constraints':['prior','P2','P24']},
        'attempted_rules':len(rows),'measured_rules':len(measured),'rejected_rules':len(rows)-len(measured),
        'measured_response_points':len(measured)*len(D_SWEEP),'P24_success_cases':len(successful),
        'counts':[{'constraint':k[0],'status':k[1],'error':k[2],'count':v} for k,v in sorted(summary.items())],
        'reference_max_GL256_agreement_error':max(ref_errors),'reference_max_Decimal80_agreement_error':max(decimal_errors),
        'max_derivative_central_difference_error':max(abs(r['derivative_error']) for r in measured),
        'wall_seconds':time.monotonic()-start,'maxrss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        'continuum_accuracy_admission':False,'native_finite_bin_admission':False,'coupled_shear_evolution':'NOT_RUN',
        'figure_floor':1e-16,'fixed_source_weights':True,'angular_refinement_and_constraints_separate':True}
    write_json(out/'RETURN_S3_CAMPAIGN.json',receipt)
    print(json.dumps(receipt,indent=2))


if __name__=='__main__':main()

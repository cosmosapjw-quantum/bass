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
import warnings
import resource
import subprocess
import sys
import time
import numpy as np
import scipy
from scipy.integrate import quad
from angular_balance import lrs_rule,project as project2
from angular_p24 import project,feasibility,legendre24,ALGORITHM_ID
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
    with warnings.catch_warnings(record=True) as observed:
        warnings.simplefilter('always')
        f,ef=quad(rr,0,1,epsabs=2e-14,epsrel=2e-14,limit=100)
        g,eg=quad(dd,0,1,epsabs=2e-14,epsrel=2e-14,limit=100)
    return {'F':f,'G':g,'A':g/f,'quad_estimated_error':ef+eg,
            'warnings':[str(w.message) for w in observed]}


def array(v):
    if isinstance(v,np.ndarray):return v.tolist()
    if isinstance(v,np.floating):return float(v)
    if isinstance(v,np.integer):return int(v)
    raise TypeError(type(v).__name__)


def write_json(path,value):
    with path.open('x') as f:json.dump(value,f,indent=2,default=array,allow_nan=False);f.write('\n')



def validate_reused_measurements(saved, sources):
    """Admit only the exact fixed-grid measurement schema with checked inputs.

    This re-evaluates cheap deterministic kernels and certificates, never either
    KL optimizer. Cached moments/statuses are evidence to verify, not gates to
    trust. A different support/runtime representation requires new evidence.
    """
    for name in ['angular_balance.py','angular_p24.py','shear_response.py','test_s3.py']:
        if saved.get('source_sha256',{}).get(name) != sources[name]:
            raise ValueError('MEASUREMENT_DEPENDENCY_CHANGED:'+name)
    rows=saved.get('rows',[])
    expected={(b,n,mode) for n in N_MU for b in BIRTH_B for mode in ['prior','P2','P24']}
    keys=[(r.get('birth_b'),r.get('n_mu'),r.get('constraint')) for r in rows]
    if len(keys)!=len(expected) or len(set(keys))!=len(keys) or set(keys)!=expected:
        raise ValueError('MEASUREMENT_GRID_CHANGED')
    references=saved.get('continuum_reference',[])
    if [r.get('d') for r in references]!=D_SWEEP:
        raise ValueError('MEASUREMENT_REFERENCE_GRID_CHANGED')
    for r in references:
        if any(not math.isfinite(r[k]) for k in ['F','G','A','quad_estimated_error']):
            raise ValueError('MEASUREMENT_REFERENCE_NONFINITE')
        actual=continuum(r['d'])
        if any(r[k]!=actual[k] for k in ['F','G','A']):
            raise ValueError('MEASUREMENT_REFERENCE_CHANGED')
    ref={r['d']:r for r in references}
    support_cache={}
    checked=[]
    for original in rows:
        r=dict(original);b,n,mode=r['birth_b'],r['n_mu'],r['constraint']
        if isinstance(b,bool) or isinstance(n,bool) or not isinstance(n,int) or r.get('id')!=f'b{b:+.2f}_n{n}_{mode}':
            raise ValueError('MEASUREMENT_ROW_ID_CHANGED')
        if (b,n) not in support_cache:
            mu,q=lrs_rule(b,n);support_cache[b,n]=(mu,q,asdict(feasibility(mu)))
        expected_mu,expected_q,certificate=support_cache[b,n]
        if r.get('P24_feasibility')!=certificate:
            raise ValueError('MEASUREMENT_FEASIBILITY_CHANGED')
        p2,p4=legendre24(expected_mu)
        expected_error=None
        if mode=='P2' and not (np.all(p2==0) or p2.min()<0<p2.max()):
            expected_error='INFEASIBLE_ANGULAR_SUPPORT'
        elif mode=='P24' and certificate['status']!='STRICT_INTERIOR':
            expected_error=certificate['status']
        if r.get('status')=='REJECTED':
            if (expected_error is None or r.get('error')!=expected_error or
                not expected_error.startswith('INFEASIBLE') or
                r.get('failure_class')!='support_feasibility'):
                raise ValueError('MEASUREMENT_REJECTION_UNVERIFIED')
            checked.append(r);continue
        if r.get('status')!='MEASURED' or expected_error is not None:
            raise ValueError('MEASUREMENT_STATUS_CHANGED')
        for name in ['mu','prior','weights']:
            v=np.asarray(r.get(name),dtype=float)
            if v.shape!=(n,) or not np.isfinite(v).all():
                raise ValueError('MEASUREMENT_ARRAY_DOMAIN:'+name)
            r[name]=v
        mu,q,w=r['mu'],r['prior'],r['weights']
        if not np.array_equal(mu,expected_mu) or not np.array_equal(q,expected_q):
            raise ValueError('MEASUREMENT_SOURCE_FRAME_CHANGED')
        if (np.any(w<=0) or np.max(abs(w-w[::-1]))>5e-14 or
            abs(math.fsum(w)-1)>5e-16):
            raise ValueError('MEASUREMENT_POSITIVE_PARITY_NORMALIZATION')
        if mode=='prior' and not np.array_equal(w,q):
            raise ValueError('MEASUREMENT_PRIOR_CHANGED')
        if mode in ['P2','P24'] and abs(math.fsum(w*p2))>3e-15:
            raise ValueError('MEASUREMENT_P2_CONSTRAINT')
        if mode=='P24' and abs(math.fsum(w*p4))>3e-15:
            raise ValueError('MEASUREMENT_P4_CONSTRAINT')
        diagnostics=derivative_diagnostics(mu,w)
        cached=dict(r.get('diagnostics',{}))
        cached['moments']={int(k):v for k,v in cached.get('moments',{}).items()}
        if (cached!=diagnostics or r.get('min_weight')!=float(w.min()) or
            r.get('normalization_defect')!=abs(math.fsum(w)-1)):
            raise ValueError('MEASUREMENT_DIAGNOSTICS_CHANGED')
        if [v.get('d') for v in r.get('response',[])]!=D_SWEEP:
            raise ValueError('MEASUREMENT_RESPONSE_GRID_CHANGED')
        for v in r['response']:
            actual=response(v['d'],mu,w)
            if (any(v.get(k)!=actual[k] for k in ['F','G','A']) or
                v.get('A_error')!=actual['A']-ref[v['d']]['A']):
                raise ValueError('MEASUREMENT_RESPONSE_CHANGED')
        central=(response(1e-5,mu,w)['A']-response(-1e-5,mu,w)['A'])/(2e-5)
        if (r.get('central_A_prime_h1e_5')!=central or
            r.get('derivative_error')!=central-diagnostics['A_prime']):
            raise ValueError('MEASUREMENT_DERIVATIVE_CHANGED')
        r['diagnostics']=diagnostics;checked.append(r)
    return checked


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--reuse-measurements',type=Path);args=ap.parse_args()
    args.out.mkdir(parents=True,exist_ok=False);out=args.out.resolve();here=Path(__file__).resolve().parent
    start=time.monotonic();rows=[];successful=[];summary=Counter()
    source_names=['angular_balance.py','angular_p24.py','shear_response.py','test_s3.py','run_s3_campaign.py']
    sources={n:hashlib.sha256((here/n).read_bytes()).hexdigest() for n in source_names}
    measurement_sources=sources
    if args.reuse_measurements:
        saved=json.loads(args.reuse_measurements.read_text())
        measurement_sources=saved['source_sha256']
        rows=validate_reused_measurements(saved,sources)
        for r in rows:
            if r['status']=='MEASURED' and r['constraint']=='P24':successful.append(r)
            summary[(r['constraint'],r['status'],r.get('error',''))]+=1
    else:
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
                            assert abs(rec['diagnostics']['moments'][2])<=3e-15
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
    write_json(out/'ANGULAR_CAMPAIGN.json',{'rows':rows,'source_sha256':measurement_sources,'report_source_sha256':sources,
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
    axs[0].set(xlabel=r'$d=b(x)-b(u)$',ylabel=r'$|\mathcal{A}_Q-\mathcal{A}_{iso}|$',title='Same 8 rays: change constraints')
    axs[0].legend()
    for mode in ['prior','P2','P24']:
        errors=[]
        for n in N_MU:
            row=next(r for r in rows if r['birth_b']==birth and r['n_mu']==n and r['constraint']==mode)
            errors.append(abs(response(.2,row['mu'],row['weights'])['A']-continuum(.2)['A']))
        axs[1].loglog(N_MU,np.maximum(errors,1e-16),'o-',label=mode,color=colors[mode],lw=1.5)
    axs[1].set(xlabel='Angular rays',ylabel=r'$|\mathcal{A}_Q-\mathcal{A}_{iso}|$',title=r'Fixed $d=0.2$: refine angular rays')
    axs[1].set_xticks(N_MU,[str(n) for n in N_MU]);axs[1].legend()
    fig.suptitle(r'Frozen birth weights, $b(u)=0.3$; spectral owner unchanged',fontsize=12)
    fig.savefig(out/'S3_ANGULAR_RESPONSE.png');fig.savefig(out/'S3_ANGULAR_RESPONSE.pdf');plt.close(fig)

    testcmd=[sys.executable,'-m','unittest','-v','test_s3']
    tested=subprocess.run(testcmd,cwd=here,text=True,capture_output=True,timeout=60)
    (out/'TEST_S3.log').write_text('$ '+' '.join(testcmd)+'\n'+tested.stdout+tested.stderr+f'\nEXIT_CODE={tested.returncode}\n')
    assert tested.returncode==0
    receipt={'schema':'bass.s3.angular_campaign.v1','status':'PASS_SCOPED_MEASUREMENT_AND_CONSTRAINTS',
        'source_sha256':sources,'measurement_source_sha256':measurement_sources,
        'reused_measurements':str(args.reuse_measurements) if args.reuse_measurements else None,
        'python':sys.version,'numpy':np.__version__,'scipy':scipy.__version__,
        'test_command':testcmd,'test_exit':tested.returncode,'new_tests':14,
        'parameter_grid':{'birth_b':BIRTH_B,'n_mu':N_MU,'d':D_SWEEP,'constraints':['prior','P2','P24']},
        'attempted_rules':len(rows),'measured_rules':len(measured),'rejected_rules':len(rows)-len(measured),
        'measured_response_points':len(measured)*len(D_SWEEP),'P24_success_cases':len(successful),
        'counts':[{'constraint':k[0],'status':k[1],'error':k[2],'count':v} for k,v in sorted(summary.items())],
        'reference_max_GL256_agreement_error':max(ref_errors),'reference_max_Decimal80_agreement_error':max(decimal_errors),
        'max_derivative_central_difference_error':max(abs(r['derivative_error']) for r in measured),
        'wall_seconds':time.monotonic()-start,'maxrss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        'continuum_accuracy_admission':False,'native_finite_bin_admission':False,'coupled_shear_evolution':'NOT_RUN',
        'reference_warnings':[{'d':float(d),'messages':continuum(float(d)).get('warnings',[])} for d in d_grid if continuum(float(d)).get('warnings')],
        'figure_floor':1e-16,'fixed_source_weights':True,'angular_refinement_and_constraints_separate':True}
    write_json(out/'RETURN_S3_CAMPAIGN.json',receipt)
    print(json.dumps(receipt,indent=2))


if __name__=='__main__':main()

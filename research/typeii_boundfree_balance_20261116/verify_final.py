#!/usr/bin/env python3
"""One bounded same-author hostile pass and fresh reproducibility verification."""
import ast,json,os,subprocess,sys,hashlib
from pathlib import Path
import numpy as np
from scipy.special import logsumexp
from numpy.polynomial.legendre import leggauss
from boundfree import *
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[1]

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run_program(name,optimized=False):
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
    cmd=[sys.executable]+(['-O'] if optimized else [])+[str(HERE/name)]
    p=subprocess.run(cmd,cwd=REPO,env=env,capture_output=True,text=True,timeout=120)
    (HERE/(Path(name).stem+('_OPTIMIZED' if optimized else '_NORMAL')+'.log')).write_text(p.stdout+p.stderr)
    check(p.returncode==0,'verification program failed: '+name+' '+p.stderr[-1200:])
    return {'program':name,'optimized':optimized,'exit':p.returncode}

def main():
    receipts=[]
    for opt in (False,True):receipts.append(run_program('test_bridge.py',opt))
    receipts.append(run_program('verify_kernels.py'))
    kd=sha(HERE/'KERNEL_VERIFICATION.json')
    receipts.append(run_program('verify_kernels.py',True));check(kd==sha(HERE/'KERNEL_VERIFICATION.json'),'kernel optimized drift')
    science=['SOURCE_AND_NETWORK_RESULTS.json','LEVEL_BOUND_FREE_SOURCE.csv','ALL_LEVEL_FINITE_BAND_PROBES.csv',
             'NETWORK_Planck_common_T.csv','NETWORK_boost_common_T.csv','NETWORK_boost_parent_Tm.csv']
    before={n:sha(HERE/n) for n in science}
    receipts.append(run_program('source_campaign.py',True))
    check(all(sha(HERE/n)==h for n,h in before.items()),'optimized source/network replay changed data')
    for name in ('boundfree.py','verify_kernels.py','source_campaign.py','verify_final.py'):
        tree=ast.parse((HERE/name).read_text());check(not any(isinstance(n,ast.Assert) for n in ast.walk(tree)),'removable science assert: '+name)
    # Fresh source identity including the original protected BASS physics files.
    lock=json.loads((REPO/'research/typeii_host_preflight_20261101/SOURCE_LOCK.json').read_text())['original_git_blobs_sha1']
    for rel,want in lock.items():
        got=subprocess.check_output(['git','hash-object',rel],cwd=REPO,text=True).strip()
        check(got==want,'original BASS source drift: '+rel)
    check(sha(HERE/'sources/h1.px.txt')==SOURCE_HASH,'author table drift')
    # Low-temperature quadrature regression, without tolerance relaxation.
    cold=(820.3755,778.5117916097918,.027504334639193155,(1,0))
    a=rates(*cold);b=rates(*cold,order=12)
    coldgap=max(abs(np.expm1(a['log_photo']-b['log_photo'])),abs(np.expm1(a['log_alpha']-b['log_alpha'])))
    check(coldgap<3e-8,'cold source regression')
    # Literal angular integration, plus the analytic zero-beta limit.
    mu,w=leggauss(128);angerrs=[]
    for beta in (0.,1e-10,.05,.2):
        G=1/np.sqrt(1-beta*beta)
        for x in (.01,.5,10.,300.,1000.):
            E=x*KB*3000;u=G*x*(1+beta*mu)
            ln=-u-np.log(-np.expm1(-u))
            direct=logsumexp(ln+np.log(w/2))
            got=float(log_nbar(E,3000.,beta));err=abs(np.expm1(got-direct));angerrs.append(float(err))
            check(err<3e-10,'literal boosted occupation disagreement')
    # The independent velocity-space coefficient detects wrong prefactors;
    # the following explicit altered kernels would destroy detailed balance.
    lev=(10,0);r=rates(8000.,8000.,0.,lev)
    deficit=1-r['alpha_spontaneous_m3_s']/r['alpha_m3_s']
    check(deficit>.05,'omitted stimulation counterexample absent')
    rs=rates(3000.,3000.,0.,(2,0));rp=rates(3000.,3000.,0.,(2,1))
    correct=np.exp(rp['log_alpha']-rp['log_photo']-rs['log_alpha']+rs['log_photo'])
    wrong_weight=correct/3
    check(abs(correct-3)<1e-10 and abs(wrong_weight-1)<1e-10,'2p statistical-weight falsifier')
    wrong_e_spin=2.*rp['alpha_m3_s']/rp['photo_s']/np.exp(log_saha(3000.,(2,1)))
    check(abs(wrong_e_spin-2)<1e-10,'electron spin factor not detected')
    b=.04314981235304731;tn=3000.7755;tm=3000.745332620247
    boosted=rates(tn,tm,b,(2,0));teq=tn*((1+b*b/3)/(1-b*b))**.25
    scalar=rates(teq,tm,0.,(2,0));scalarerr=float(np.expm1(scalar['log_photo']-boosted['log_photo']))
    check(abs(scalarerr)>.02,'single energy-equivalent blackbody counterexample')
    # Change in the photon/kinetic moments is not a violation of E=chi+K.
    r=rates(3000.,2800.,.05,(2,1));s=net_sources(r,2e5,3e7,3e7)
    wrong_energy_residual=s['Q_photon']+s['Q_kinetic']
    check(abs(wrong_energy_residual)>0 and abs(wrong_energy_residual+s['Q_ionization'])<1e-12*max(abs(wrong_energy_residual),abs(s['Q_ionization'])),'ionization-energy ledger falsifier')
    # Invalid microscopic, spectral and clock inputs are rejected; no extrapolation.
    invalid=[('nonfinite',lambda:rates(np.nan,3000.,0.,(2,0))),('negative_temperature',lambda:rates(3000.,-1.,0.,(2,0))),
        ('superluminal',lambda:rates(3000.,3000.,1.,(2,0))),('unsupported_level',lambda:rates(3000.,3000.,0.,(11,0))),
        ('out_of_table',lambda:sigma((LEVELS[2,0]['chi']+LEVELS[2,0]['Kmax'])*1.01,(2,0))),
        ('negative_energy',lambda:sigma(-1.,(2,0))),('singular_cross_section_argument',lambda:capture_sigma(0.,(2,0))),
        ('negative_eta',lambda:rates(3000.,3000.,0.,(2,0),eta=-1.)),('bad_order',lambda:rates(3000.,3000.,0.,(2,0),order=1)),
        ('negative_density',lambda:net_sources(r,-1.,1.,1.)),('invalid_clock',lambda:proper_to_normal_fraction([1.],1.,.9,1.))]
    rejected=[]
    for label,call in invalid:
        try:call()
        except ValueError:rejected.append(label)
        else:raise RuntimeError('invalid input accepted: '+label)
    # Correct proper fraction clock: it does not produce an extra relative flux.
    transformed=proper_to_normal_fraction([-3.,3.],2.,1.01,4.)
    check(max(abs(transformed-np.array([-3.,3.])/(2.*1.01*4.)))<1e-15,'proper reaction clock')
    out={'analytic_contracts':13,'normal_and_optimized_unit_executions':26,'actual_program_runs':receipts,
         'optimized_science_data_sha256':before,'kernel_optimized_sha256':kd,
         'source_author_table_sha256':SOURCE_HASH,'original_BASS_blobs':len(lock),
         'literal_angular_cases':len(angerrs),'max_literal_angular_relative_gap':max(angerrs),
         'cold_default8_vs12_rate_relative_gap':float(coldgap),
         'omitted_stimulated_capture_equilibrium_relative_defect_n10s_T8000':float(deficit),
         'correct_Planck_2p_over_2s':float(correct),'wrong_equal_g_Planck_2p_over_2s':float(wrong_weight),
         'wrong_missing_electron_spin_stationary_ratio_factor':float(wrong_e_spin),
         'energy_matched_blackbody_2s_photo_relative_error_z1100':scalarerr,
         'omit_ionization_energy_relative_ledger_error':float(abs(wrong_energy_residual)/sum(abs(s[k]) for k in ('Q_photon','Q_kinetic','Q_ionization'))),
         'invalid_cases_rejected':rejected,'native_subagent':'NOT_RUN','distinct_author_referee':'NOT_RUN',
         'review':'same-author hostile, not genuinely blind or independent',
         'limits':['finite source energy support','unaligned nonrelativistic hydrogen nl states','no bound-bound cascades or effective-rate elimination','no helium excited-state network','no thermal/radiation/momentum feedback','no new native HYREC xe or optical depth']}
    (HERE/'VERIFICATION_AND_HOSTILE.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ('optimized_science_data_sha256','actual_program_runs')},indent=2))
if __name__=='__main__':main()

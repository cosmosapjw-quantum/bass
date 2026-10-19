#!/usr/bin/env python3
"""Compile unchanged pinned REI and measure new S7 finite-bin cohort obligations.

Prepare a contract first, publish it with the source, then run. Native owner
staging is reused from S3; none of the completed S2/S3/S6 campaigns are invoked.
The runner accepts a clean git preregistration, or an independently obtained
Git-data readback receipt in an API-backed workspace without a .git checkout.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
from fractions import Fraction
import gzip
import hashlib
import io
import json
import math
import os
from pathlib import Path
import resource
import shutil
import signal
import subprocess
import time

# Set these before NumPy loads BLAS. A pre-existing larger environment value
# must not silently consume workers outside this runner's declared budget.
for _thread_env in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[_thread_env] = '1'
import numpy as np
import angular_balance
import angular_p24
from run_native_adapter import REI_SHA, SOURCE_ID, RAM, DISK, digest, blob, stage_owner, verify_owner
from s6_io import write_json_once

ROOT = Path(__file__).resolve().parent
REPO = 'cosmosapjw-quantum/bass'
LANE = 'research/bass_isotropy_response_20261018/'
PINNED = ('native_cohort_probe.rs', 'run_native_cohorts.py', 'test_native_cohorts.py',
          'native_adapter.rs', 'balance.rs', 'balance_p24.rs', 'run_native_adapter.py',
          'native_owner_manifest.json', 'angular_balance.py', 'angular_p24.py', 's6_io.py')
BUILD = ('native_cohort_probe.rs', 'native_adapter.rs', 'balance.rs', 'balance_p24.rs')
MAX_RAW_BYTES = 64*1024**2
REUSE_RUN01 = {
    'source_publication_commit': '2865f60bf0a247eaab4997c222ad82ae22a4c8fa',
    'preregistration_sha256': 'f90a0fd7af186b56f2e1bc12ee305a8916301e4917b41a5d8d9b800a62e7e8d8',
    'files_sha256': {
        'NATIVE_COHORTS.jsonl': '4b544414a434abfb56edbf38c89807aa221b3083185bcfc2499e9f53f6db8122',
        'ANALYSIS.json': '8f776e49214a054951ed941c8fac50f3624735dc546ee0305918d2a2f488b8ee',
        'RETURN_NATIVE_COHORTS.json': 'afc45dd4f0ceada6093528a93162485c82ed4596ffef7ba865c50464de2c6949',
    },
    'changed_files_allowed_for_reanalysis': ['run_native_cohorts.py', 'test_native_cohorts.py'],
}


def matrix():
    rows = []
    def add(block, n=16, ne=96, cps=32, k=16, b0=0., mode='P2P4', slab=False):
        rows.append(dict(case_id=f'{block}_{len(rows):03}', block=block, n_mu=n, n_energy=ne,
                         cells_per_segment=cps, cohorts=k, b0=b0, beta=.2, x_observe=1., mode=mode, slab=slab))
    for b in (0., .6, .9):
        for n in (8, 16, 32):
            for mode in ('prior', 'P2', 'P2P4'):
                add('angular', n=n, b0=b, mode=mode)
    for k in (8, 32, 64, 128):
        for mode in ('prior', 'P2', 'P2P4'):
            add('birth_time', k=k, mode=mode)
    for ne in (24, 48, 96, 192):
        add('slab_bins', ne=ne, cps=64, slab=True)
    for cps in (8, 16, 32):
        add('slab_panels', cps=cps, slab=True)
    for k in (8, 32):
        add('slab_birth_time', k=k, cps=64, slab=True)
    for n in (8, 32):
        add('slab_angular', n=n, cps=64, slab=True)
    add('slab_large_b', n=32, b0=.6, cps=64, slab=True)
    return rows


def contract():
    return {
        'schema': 'bass.native.cohorts.s7.preregistration.v2',
        'analysis_revision': {
            'revision': 2,
            'reason': 'Run01 exposed a multiplication-association false moment rejection; exact dyadic arithmetic corrects the validator.',
            'timing': 'Prepared after run01 observations and before R2 reanalysis; not a new preregistered physical prediction.',
            'arithmetic': 'Exact Fraction sum(alpha_i * P_l(mu_i)) on stored binary64 inputs, without renormalizing alpha.',
            'gate': '3/10^15 exactly; the existing separate normalization and all physical gates remain unchanged.',
            'native_execution': 'Unchanged; reanalysis must bind the exact original raw data and execution receipt.',
        },
        'reuse_from': json.loads(json.dumps(REUSE_RUN01)),
        'owner_repo': 'cosmosapjw-quantum/rei_bianchi', 'owner_commit': REI_SHA, 'source_id': SOURCE_ID,
        'pinned_sha256': {n: digest((ROOT/n).read_bytes()) for n in PINNED},
        'physics': {'signature': '(-,+,+,+)', 'a_perp': 'a exp(-b)', 'a_parallel': 'a exp(2b)',
                    's': 'dot b', 'Sigma': 'sqrt(3)|s|/H', 'H_per_s': 1e-16,
                    'a': 'exp(x)/21', 'b': 'b0 + beta*x', 'birth_interval_x': [0, .8],
                    'dt_birth': '0.8 / cohorts / H', 'redshift': '21 exp(-u)-1',
                    'source_rate': 'unchanged AxbiSource::at_redshift',
                    'per_h_continuity': 'dU_per_H/dx + U_per_H + 2 beta DeltaP_per_H = 0 between births',
                    'density_conversion': 'U_physical = nH0/a^3 * U_per_H; physical equation has +4U',
                    'coupled_Einstein_native': False, 'reactive_history': False},
        'scope': ['actual unchanged-owner finite-bin multiple births',
                  'positive weights fixed at each birth, no survivor reprojection',
                  'prescribed collisionless geometry and unchanged anisotropic old stock',
                  'one final frozen-opacity backward-Euler slab',
                  'independent source-cell integration with unchanged owner cross sections'],
        'matrix': matrix(),
        'gates': {
            'moment_absolute': 3e-15, 'reflection_absolute': 5e-14, 'source_frame_mu_absolute': 5e-14,
            'photon_source_relative': 3e-14, 'native_kernel_relative': 3e-14,
            'native_ledger_relative': 1e-11, 'continuity_relative': 1e-11,
            'reference_32_64_relative': 1e-11, 'reference_age_96_192_relative': 1e-10,
            'birth_midpoint_ratio': [3.5, 4.5], 'birth_ratio_error_floor': 1e-12,
            'large_b_n32_P24_angular_accuracy_target': 1e-6,
            'slab_n_energy_192_relative_accuracy_target': 1e-4,
        },
        'failure_policy': 'All support/numerical/accuracy-target failures are retained. No negative weights or tolerance relaxation.',
        'admission': {'REI_production': False, 'full_EoR': False, 'merge': False},
        'limits': {'additional_workers': 16, 'ram_bytes': RAM, 'disk_bytes': DISK, 'job_seconds': 1800},
        'predictions_before_execution': [
            'Native collisionless total N/U agree with the frozen-cohort discrete R,D calculation.',
            'The physical-density continuity equation differs from the per-H equation by a^-3.',
            'Large-b P2/P24 support failures can occur, and n_mu<=32 does not guarantee continuum accuracy.',
            'A merged two-moment absorption closure can differ from separately retained cohorts; bin and panel changes are separate.',
        ],
    }


def verify_publication(prereg_path, prereg, receipt_path=None):
    current = {n: digest((ROOT/n).read_bytes()) for n in prereg['pinned_sha256']}
    if current != prereg['pinned_sha256']:
        raise ValueError('SOURCE_CHANGED_AFTER_PREREGISTRATION')
    # The published contract is an executable input, not a source of new
    # tolerances or permission to omit an implementation hash. Compare every
    # schema, gate, identity, limit, matrix row and pinned-key entry exactly.
    if prereg != contract():
        raise ValueError('PREREGISTRATION_CONTRACT_CHANGED')
    if receipt_path:
        r = json.loads(Path(receipt_path).read_text())
        commit = r.get('commit', '')
        if (r.get('schema') != 'bass.git.preregistered.file.v1' or r.get('repo') != REPO
                or len(commit) != 40 or any(x not in '0123456789abcdef' for x in commit)
                or r.get('path') != LANE+'evidence_s7_native/PREREGISTRATION_R2.json'
                or r.get('remote_readback') is not True
                or r.get('git_blob_sha') != blob(prereg_path.read_bytes())
                or r.get('sha256') != digest(prereg_path.read_bytes())):
            raise ValueError('PREREGISTRATION_REMOTE_RECEIPT_IDENTITY')
        return {'method': 'independent_git_data_connector_readback', 'commit': commit,
                'receipt_sha256': digest(Path(receipt_path).read_bytes()), 'git_blob_sha': r['git_blob_sha']}
    git = ['git', '-C', str(prereg_path.parent)]
    name = prereg_path.name
    if subprocess.run(git+['ls-files', '--error-unmatch', name], capture_output=True).returncode:
        raise ValueError('PREREGISTRATION_NOT_TRACKED_NEED_VERIFIED_READBACK')
    if subprocess.run(git+['diff', '--quiet', 'HEAD', '--', name], capture_output=True).returncode:
        raise ValueError('PREREGISTRATION_NOT_COMMITTED_CLEAN')
    p = subprocess.run(git+['log', '-1', '--format=%H', '--', name], capture_output=True, text=True, check=True)
    return {'method': 'clean_git_preregistration', 'commit': p.stdout.strip()}


def case_csv(rows):
    keys = ('case_id', 'block', 'n_mu', 'n_energy', 'cells_per_segment', 'cohorts', 'b0', 'beta', 'x_observe', 'mode', 'slab')
    return ''.join(','.join(str(int(r[k])) if k == 'slab' else str(r[k]) for k in keys)+'\n' for r in rows)


def source_rate(u):
    zp = 21.*np.exp(-u)
    sfr = .015*zp**2.7/(1.+(zp/2.9)**5.6)
    log_yield = 1./(.00038*.002**.227+.01858)-math.log10(2.55)
    return .2*10.**log_yield*sfr/(3.085677581491367e24**3*1.88e-7)


def kernels(d, mu):
    a = np.exp(2*d)*(1-mu*mu)
    b = np.exp(-4*d)*mu*mu
    r = np.sqrt(a+b)
    return r, (b-.5*a)/r


def exact_moments(mu, alpha):
    """Evaluate the original discrete functional with exact dyadic inputs."""
    if len(mu)!=len(alpha):raise ValueError('EXACT_MOMENT_SHAPE')
    ms=[Fraction.from_float(float(m)) for m in mu]
    ws=[Fraction.from_float(float(a)) for a in alpha]
    zs=[m*m for m in ms]
    norm=sum(ws,Fraction(0))
    m2=sum((w*(3*z-1)/2 for w,z in zip(ws,zs)),Fraction(0))
    m4=sum((w*(35*z*z-30*z+3)/8 for w,z in zip(ws,zs)),Fraction(0))
    return norm,m2,m4


def read_native_raw(path):
    """Read plain JSONL or its repository gzip representation without staging."""
    path=Path(path)
    compressed_path=path if path.suffix=='.gz' else path.with_name(path.name+'.gz')
    if path.suffix!='.gz' and path.exists():
        with path.open('rb') as f:raw=f.read(MAX_RAW_BYTES+1)
    else:
        packed=compressed_path.read_bytes()
        meta_path=compressed_path.parent/'RAW_STORAGE.json'
        meta=json.loads(meta_path.read_text()) if meta_path.exists() else None
        if meta and (meta.get('schema')!='bass.lossless.raw_storage.v1' or meta.get('gzip_sha256')!=digest(packed)):
            raise ValueError('RAW_STORAGE_IDENTITY')
        with gzip.GzipFile(fileobj=io.BytesIO(packed),mode='rb') as f:raw=f.read(MAX_RAW_BYTES+1)
        if meta and (meta.get('raw_sha256')!=digest(raw) or meta.get('raw_bytes')!=len(raw)):
            raise ValueError('RAW_STORAGE_CONTENT_IDENTITY')
    if len(raw)>MAX_RAW_BYTES:raise ValueError('RAW_INPUT_TOO_LARGE')
    return raw


def verify_existing_run(existing, prereg):
    """Reject substituted outputs, old receipts, or changed native dependencies."""
    spec=prereg['reuse_from']
    for name,sha in spec['files_sha256'].items():
        raw=read_native_raw(existing/name) if name=='NATIVE_COHORTS.jsonl' else (existing/name).read_bytes()
        if digest(raw)!=sha:
            raise ValueError('REUSE_ARTIFACT_IDENTITY:'+name)
    previous=json.loads((existing/'RETURN_NATIVE_COHORTS.json').read_text())
    if (previous.get('owner_commit')!=REI_SHA or previous.get('source_id')!=SOURCE_ID
            or previous.get('publication',{}).get('commit')!=spec['source_publication_commit']
            or previous.get('preregistration_sha256')!=spec['preregistration_sha256']
            or previous.get('native_output_sha256')!=spec['files_sha256']['NATIVE_COHORTS.jsonl']
            or set(previous.get('pinned_sha256',{}))!=set(PINNED)):
        raise ValueError('REUSE_EXECUTION_IDENTITY')
    allowed=set(spec['changed_files_allowed_for_reanalysis'])
    if any(previous['pinned_sha256'][n]!=prereg['pinned_sha256'][n] for n in PINNED if n not in allowed):
        raise ValueError('REUSE_NATIVE_INPUT_CHANGED')
    if not any(c.get('label')=='measure_native_cohorts' and c.get('exit_code')==0 for c in previous['commands']):
        raise ValueError('REUSE_NATIVE_NOT_COMPLETED')
    return previous


def check_birth_geometry(row, birth, index, gates):
    """Bind reported rays to the declared reference frame and birth history."""
    u=.8*(index+.5)/row['cohorts']; expected_b=row['b0']+row['beta']*u
    expected_mu,expected_prior=angular_balance.lrs_rule(expected_b,row['n_mu'])
    mu=np.asarray(birth['mu'])
    if (abs(birth['u']-u)>2e-16 or mu.shape!=(row['n_mu'],)
            or abs(birth['b']-expected_b)>2e-16 or abs(birth['z']-(21*math.exp(-u)-1))>5e-14
            or abs(birth['dt_s']/(.8/row['cohorts']/1e-16)-1)>gates['photon_source_relative']):
        raise ValueError('BIRTH_GEOMETRY_OR_TIME_IDENTITY')
    if not np.isfinite(mu).all() or max(abs(mu-expected_mu))>gates['source_frame_mu_absolute']:
        raise ValueError('SOURCE_FRAME_BINDING')
    return expected_mu,expected_prior


def check_failure_witness(row, gates):
    """A rejection must concern this case's actual first reported birth ray set."""
    index=row.get('failed_birth')
    if isinstance(index,bool) or not isinstance(index,int) or not 0<=index<row['cohorts']:
        raise ValueError('FAILURE_BIRTH_INDEX')
    u=.8*(index+.5)/row['cohorts']; reported_u=row.get('failed_u')
    if not isinstance(reported_u,(int,float)) or not math.isfinite(reported_u) or abs(reported_u-u)>2e-16:
        raise ValueError('FAILURE_BIRTH_TIME')
    mu=np.asarray(row['support_mu'],dtype=float)
    expected_mu,_=angular_balance.lrs_rule(row['b0']+row['beta']*u,row['n_mu'])
    if (mu.shape!=expected_mu.shape or not np.isfinite(mu).all()
            or max(abs(mu-expected_mu))>gates['source_frame_mu_absolute']):
        raise ValueError('FAILURE_SOURCE_FRAME_BINDING')
    return mu


def continuous_reference(row, order):
    """Same finite angular rule, continuous birth-time GL quadrature."""
    nodes, weights = np.polynomial.legendre.leggauss(order)
    us = .4*(nodes+1.)
    qs = .4*weights*source_rate(us)/1e-16
    angular = []
    for u in us:
        mu, prior = angular_balance.lrs_rule(row['b0']+row['beta']*float(u), row['n_mu'])
        alpha = (prior if row['mode']=='prior' else
                 angular_balance.project(mu, prior).weights if row['mode']=='P2' else angular_p24.project(mu, prior).weights)
        r, d = kernels(row['beta']*(row['x_observe']-u), mu)
        angular.append([math.fsum(alpha*r), math.fsum(alpha*d)])
    angular = np.asarray(angular)
    scaled = qs*np.exp(us-row['x_observe'])
    mean = math.fsum(b['u_birth']/b['source_amount'] for b in row['births'])/len(row['births'])
    return np.asarray([math.fsum(qs), mean*math.fsum(scaled*angular[:, 0]), mean*math.fsum(scaled*angular[:, 1])])


def validate(path, prereg):
    def reject(v):
        raise ValueError('NATIVE_NONFINITE_JSON:'+v)
    recs = [json.loads(l, parse_constant=reject) for l in read_native_raw(path).decode('utf-8').splitlines() if l.strip()]
    if not recs:
        raise ValueError('MISSING_COMPLETION')
    done = recs.pop()
    if (done.get('schema')!='bass.native.cohorts.s7.complete.v1' or done.get('rows')!=len(prereg['matrix'])
            or done.get('owner_commit')!=REI_SHA or done.get('source_id')!=SOURCE_ID or len(recs)!=len(prereg['matrix'])):
        raise ValueError('COMPLETION_IDENTITY')
    expected = {r['case_id']:r for r in prereg['matrix']}
    if len({r.get('case_id') for r in recs})!=len(recs) or {r.get('case_id') for r in recs}!=set(expected):
        raise ValueError('CASE_GRID')
    g = prereg['gates']; failures = []; support = []; measured = []; metrics = []
    def check(ok, tag, row, value=None):
        if not bool(ok):
            failures.append({'case_id':row['case_id'], 'gate':tag, 'value':value})
    for row in recs:
        if any(row.get(k)!=v for k,v in expected[row['case_id']].items()) or row.get('schema')!='bass.native.cohorts.s7.row.v1':
            raise ValueError('CASE_IDENTITY')
        if row['status']!='MEASURED':
            if row['status'] not in ('FEASIBILITY_FAILURE', 'NUMERICAL_FAILURE'):
                raise ValueError('UNKNOWN_FAILURE_CLASS')
            mu = check_failure_witness(row,g); z=mu*mu
            if row['mode']=='P2':
                independent = 'INFEASIBLE_ANGULAR_SUPPORT' if not (z.min()<1/3<z.max()) else 'STRICT_INTERIOR'
                bounds = {'z_min':float(z.min()),'z_max':float(z.max())}
            else:
                f = angular_p24.feasibility(mu); independent=f.status; bounds=vars(f)
            check(row['failure']==independent, 'FEASIBILITY_INDEPENDENT', row, independent)
            support.append({k:row[k] for k in ('case_id','status','failure','failed_birth','failed_u','b0','n_mu','mode')} | {'independent':bounds})
            continue
        measured.append(row)
        if len(row['births'])!=row['cohorts'] or row.get('source_id')!=SOURCE_ID:
            raise ValueError('BIRTH_HISTORY_IDENTITY')
        pred_n = []; pred_u=[]; pred_p=[]; iso_u=[]; iso_p=[]; moments=[]; exact_values=[]; witnesses=[]
        iso_mu, iso_w = np.polynomial.legendre.leggauss(256); iso_w*=.5
        for j,birth in enumerate(row['births']):
            u=.8*(j+.5)/row['cohorts']; mu=np.asarray(birth['mu']); alpha=np.asarray(birth['alpha']); energy=np.asarray(birth['energy_alpha'])
            if abs(birth['u']-u)>2e-16 or mu.shape!=(row['n_mu'],) or alpha.shape!=mu.shape or energy.shape!=mu.shape:
                raise ValueError('BIRTH_INPUT_IDENTITY')
            expected_mu,expected_prior=check_birth_geometry(row,birth,j,g)
            if not np.isfinite(mu).all() or not np.isfinite(alpha).all() or not np.isfinite(energy).all():
                raise ValueError('BIRTH_NONFINITE')
            check(np.all(alpha>0) and np.all(energy>0) and abs(math.fsum(alpha)-1)<g['moment_absolute'], 'POSITIVE_NORMALIZED',row)
            check(max(abs(mu-expected_mu))<=g['source_frame_mu_absolute'],'SOURCE_FRAME_BINDING',row,max(abs(mu-expected_mu)))
            if row['mode']=='prior':
                check(max(abs(alpha-expected_prior))<=g['source_frame_mu_absolute'],'PRIOR_JACOBIAN_BINDING',row,max(abs(alpha-expected_prior)))
            check(max(abs(mu+mu[::-1]))<=g['reflection_absolute'] and max(abs(alpha-alpha[::-1]))<=g['reflection_absolute'], 'REFLECTION',row)
            m2,m4=angular_p24.legendre24(mu); v2=math.fsum(alpha*m2); v4=math.fsum(alpha*m4)
            norm,e2,e4=exact_moments(mu,alpha); exact_values.append([float(e2),float(e4)])
            if row['mode']!='prior':
                exact_gate=Fraction(str(g['moment_absolute']))
                check(abs(e2)<=exact_gate and (row['mode']!='P2P4' or abs(e4)<=exact_gate), 'MOMENTS',row,[float(e2),float(e4)])
                if abs(e2)>exact_gate*Fraction(29,30) or (row['mode']=='P2P4' and abs(e4)>exact_gate*Fraction(29,30)):
                    witnesses.append({'birth_index':j,'f64_moments':[v2,v4],
                                      'exact_moments':[[str(e2.numerator),str(e2.denominator)],[str(e4.numerator),str(e4.denominator)]],
                                      'exact_weight_sum':[str(norm.numerator),str(norm.denominator)],
                                      'normalized_exact_moments_diagnostic':[float(e2/norm),float(e4/norm)]})
            check(abs(birth['n_birth']/birth['source_amount']-1)<=g['photon_source_relative'], 'PHOTON_SOURCE',row)
            check(abs(birth['source_amount']/(float(source_rate(u))*.8/row['cohorts']/1e-16)-1)<=g['photon_source_relative'], 'OWNER_EMISSIVITY',row)
            r,d=kernels(row['beta']*(row['x_observe']-u),mu)
            ir,id_=kernels(row['beta']*(row['x_observe']-u),iso_mu)
            amplitude=birth['u_birth']*math.exp(u-row['x_observe'])
            pred_n.append(birth['n_birth']);pred_u.append(amplitude*math.fsum(energy*r));pred_p.append(amplitude*math.fsum(energy*d))
            iso_u.append(amplitude*math.fsum(iso_w*ir));iso_p.append(amplitude*math.fsum(iso_w*id_));moments.append([v2,v4])
        un=math.fsum(pred_u);pn=math.fsum(pred_p); nn=math.fsum(pred_n)
        kernel_res=max(abs(row['n_final']-nn)/nn,abs(row['u_final']-un)/un,abs(row['stress_final']-pn)/un)
        check(kernel_res<=g['native_kernel_relative'],'FROZEN_NATIVE_KERNEL',row,kernel_res)
        # The unchanged prior injects source panels directly into old cells;
        # its floating-point association differs from adding a summed birth.
        # The angular adapter itself adds one complete increment and is exact.
        check(row['survivors_bitwise_frozen'] and (row['max_cell_add_absolute']==0. if row['mode']!='prior'
              else row['max_cell_add_relative']<=g['native_ledger_relative']),'OLD_STOCK_PRESERVATION',row)
        add_res=max(abs(row['combined_n']-row['old_n']-row['n_final'])/row['combined_n'],
                    abs(row['combined_u']-row['old_u']-row['u_final'])/row['combined_u'],
                    abs(row['combined_stress']-row['old_stress']-row['stress_final'])/row['combined_u'])
        check(add_res<=g['native_ledger_relative'],'OLD_STOCK_ADDITIVITY',row,add_res)
        check(max(row['max_increment_ledger_n_relative'],row['max_increment_ledger_u_relative'])<=g['native_ledger_relative'],'NATIVE_INCREMENT_LEDGER',row)
        check(max(abs(row['energy_continuity_per_h_relative']),abs(row['energy_continuity_half_h_relative']))<=g['continuity_relative'],'ENERGY_CONTINUITY',row)
        iso_a=math.fsum(iso_p)/math.fsum(iso_u)
        metric={k:row[k] for k in expected[row['case_id']]}
        metric.update(native_kernel_relative=kernel_res,continuum_same_births_a=iso_a,
                      angular_a_error=row['a_response']-iso_a, a_response=row['a_response'],
                      max_weight_moments=np.max(np.abs(moments),axis=0).tolist(),
                      max_exact_weight_moments=np.max(np.abs(exact_values),axis=0).tolist(),
                      exact_moment_boundary_witnesses=witnesses,
                      max_native_ledger_relative=max(row['max_increment_ledger_n_relative'],row['max_increment_ledger_u_relative']),
                      continuity_relative=max(abs(row['energy_continuity_per_h_relative']),abs(row['energy_continuity_half_h_relative'])))
        if row['b0']==.6 and row['n_mu']==32 and row['mode']=='P2P4':
            check(abs(metric['angular_a_error'])<=g['large_b_n32_P24_angular_accuracy_target'],'LARGE_B_ANGULAR_ACCURACY_TARGET',row,metric['angular_a_error'])
        if row['slab']:
            s=row['absorption']; r32=np.asarray(s['reference32']);r64=np.asarray(s['reference64']); obs=np.asarray([s['after_n'],s['after_u'],s['after_stress'],s['binding_ev_per_h'],s['heat_ev_per_h']])
            scale=np.asarray([s['before_n'],s['before_u'],s['before_u'],s['before_u'],s['before_u']])
            ref_res=max(abs(r32-r64)/scale); error=(obs-r64)/scale
            metric.update(slab_reference_relative=ref_res,slab_errors_relative_to_before=error.tolist(),
                          merged_minus_separate_relative=[(s['after_n']-s['separate_cohort_n'])/s['before_n'],
                                                         (s['after_u']-s['separate_cohort_u'])/s['before_u'],
                                                         (s['after_stress']-s['separate_cohort_stress'])/s['before_u']],
                          slab_ledger_relative=max(abs(s['ledger_n_relative']),abs(s['ledger_u_relative'])))
            check(ref_res<=g['reference_32_64_relative'],'DIRECT_SPECTRAL_REFERENCE',row,ref_res)
            check(metric['slab_ledger_relative']<=g['native_ledger_relative'],'SLAB_LEDGER',row,metric['slab_ledger_relative'])
            if row['n_energy']==192:
                check(max(abs(error[:2]))<=g['slab_n_energy_192_relative_accuracy_target'],'SLAB_FINE_BIN_ACCURACY_TARGET',row,max(abs(error[:2])))
        metrics.append(metric)
    age=[]
    for mode in ('prior','P2','P2P4'):
        group=sorted([r for r in measured if r['b0']==0. and r['n_mu']==16 and r['mode']==mode
                      and r['cells_per_segment']==32 and r['n_energy']==96 and not r['slab']],key=lambda r:r['cohorts'])
        ref96=continuous_reference(group[0],96);ref192=continuous_reference(group[0],192)
        check(max(abs(ref192-ref96)/np.asarray([ref192[0],ref192[1],ref192[1]]))<=g['reference_age_96_192_relative'],'AGE_REFERENCE',group[0])
        errors=[]
        for row in group:
            native_v=np.asarray([row['n_final'],row['u_final'],row['stress_final']]); err=native_v-ref192
            errors.append({'cohorts':row['cohorts'],'absolute_error':err.tolist()})
        ratios=[]
        for before,after in zip(errors,errors[1:]):
            if after['cohorts']!=2*before['cohorts']:
                continue
            for j,quantity in enumerate(('photon','energy','stress')):
                if abs(after['absolute_error'][j])>g['birth_ratio_error_floor']:
                    ratio=abs(before['absolute_error'][j]/after['absolute_error'][j]);ratios.append({'cohorts':before['cohorts'],'quantity':quantity,'ratio':ratio})
                    lo,hi=g['birth_midpoint_ratio'];check(lo<=ratio<=hi,'BIRTH_MIDPOINT_RATIO',group[0],ratio)
        age.append({'mode':mode,'continuous_reference':ref192.tolist(),'reference_96_192':(ref96-ref192).tolist(),'errors':errors,'ratios':ratios})
    integrity=[f for f in failures if not f['gate'].endswith('_ACCURACY_TARGET')]
    return {'schema':'bass.native.cohorts.s7.analysis.v2','rows':len(recs),'measured':len(measured),
            'moment_arithmetic': 'Exact Fraction unnormalized weighted sums on stored dyadic alpha/mu; fixed decimal gate3/10^15; f64 moments retained as diagnostics.',
            'support_or_numerical_failures':support,'gate_failures':failures,'integrity_gates_pass':not integrity,
            'accuracy_targets_pass':not failures,'metrics':metrics,'birth_time':age,
            'status':'PASS_SCOPED_NATIVE_COHORTS' if not failures else 'COMPLETED_WITH_RETAINED_GATE_FAILURES'}


def revalidate_existing(a):
    if not 1<=a.timeout<=1800:raise ValueError('EXECUTION_LIMIT')
    prereg_path=a.prereg.resolve();prereg=json.loads(prereg_path.read_text())
    published=verify_publication(prereg_path,prereg,a.publication_receipt)
    previous=verify_existing_run(a.revalidate_existing.resolve(),prereg)
    out=a.out.resolve()
    if out.exists():raise FileExistsError(out)
    out.mkdir(parents=True);started=time.monotonic()
    receipt={'schema':'bass.native.cohorts.s7.reanalysis.v2','started_utc':datetime.now(timezone.utc).isoformat(),
             'status':'STARTED','native_rerun':False,'new_compilation':False,
             'old_execution_publication':previous['publication'], 'original_status':previous['status'],
             'new_analysis_publication':published,'preregistration_sha256':digest(prereg_path.read_bytes()),
             'pinned_sha256':prereg['pinned_sha256'],'reused_artifacts_sha256':prereg['reuse_from']['files_sha256'],
             'limits':{'additional_workers':1,'blas_threads':1,'ram_bytes':RAM,'disk_bytes':DISK,'job_seconds':a.timeout},
             'numpy_version':np.__version__}
    try:
        resource.setrlimit(resource.RLIMIT_AS,(RAM,RAM));resource.setrlimit(resource.RLIMIT_FSIZE,(DISK,DISK));signal.alarm(a.timeout)
        analysis=validate(a.revalidate_existing.resolve()/'NATIVE_COHORTS.jsonl',prereg)
        write_json_once(out/'ANALYSIS_R2.json',analysis,indent=2)
        receipt.update(status=analysis['status'],rows=analysis['rows'],measured=analysis['measured'],
                       integrity_gates_pass=analysis['integrity_gates_pass'],accuracy_targets_pass=analysis['accuracy_targets_pass'],
                       analysis_sha256=digest((out/'ANALYSIS_R2.json').read_bytes()))
        verify_existing_run(a.revalidate_existing.resolve(),prereg)
        if prereg['pinned_sha256']!={n:digest((ROOT/n).read_bytes()) for n in PINNED}:raise ValueError('SOURCE_CHANGED_DURING_REANALYSIS')
        receipt['disk_bytes_used']=sum(p.stat().st_size for p in out.rglob('*') if p.is_file())
        if receipt['disk_bytes_used']>DISK:raise RuntimeError('DISK_LIMIT')
    except Exception as e:
        receipt.update(status='FAILED',failure_class=type(e).__name__,failure=str(e));raise
    finally:
        signal.alarm(0);receipt['elapsed_seconds']=time.monotonic()-started
        receipt['python_peak_rss_kib_linux']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        receipt['admission']={'REI_production':False,'full_EoR':False,'merge':False,'native_coupled_Einstein':False,'full_reactive_history':False}
        write_json_once(out/'RETURN_NATIVE_COHORTS_R2.json',receipt,indent=2)
    return receipt


def run(a):
    if not 1<=a.workers<=16 or not 1<=a.timeout<=1800:
        raise ValueError('EXECUTION_LIMIT')
    prereg_path=a.prereg.resolve(); prereg=json.loads(prereg_path.read_text())
    published=verify_publication(prereg_path,prereg,a.publication_receipt)
    out=a.out.resolve()
    if out.exists():
        raise FileExistsError(out)
    out.mkdir(parents=True);started=time.monotonic();deadline=started+a.timeout
    receipt={'schema':'bass.native.cohorts.s7.execution.v1','started_utc':datetime.now(timezone.utc).isoformat(),
             'status':'STARTED','owner_commit':REI_SHA,'source_id':SOURCE_ID,'publication':published,
             'preregistration_sha256':digest(prereg_path.read_bytes()),'pinned_sha256':prereg['pinned_sha256'],
             'limits':{'additional_workers':a.workers,'native_threads':1,'ram_bytes':RAM,'disk_bytes':DISK,'job_seconds':a.timeout},'commands':[]}
    def limit():
        resource.setrlimit(resource.RLIMIT_AS,(RAM,RAM));resource.setrlimit(resource.RLIMIT_FSIZE,(DISK,DISK))
    def command(label,args):
        left=deadline-time.monotonic()
        if left<=0:raise TimeoutError('JOB_SECONDS')
        env=os.environ.copy();env.update(RUST_TEST_THREADS='1',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1')
        t=time.monotonic()
        try:
            p=subprocess.run(list(map(str,args)),capture_output=True,timeout=left,env=env,preexec_fn=limit)
        except subprocess.TimeoutExpired as e:
            (out/(label+'.stdout')).write_bytes(e.stdout or b'');(out/(label+'.stderr')).write_bytes(e.stderr or b'');raise
        (out/(label+'.stdout')).write_bytes(p.stdout);(out/(label+'.stderr')).write_bytes(p.stderr)
        receipt['commands'].append({'label':label,'args':list(map(str,args)),'seconds':time.monotonic()-t,'exit_code':p.returncode})
        if p.returncode:raise RuntimeError('COMMAND_FAILED:'+label)
        return p.stdout.decode(errors='replace')
    try:
        resource.setrlimit(resource.RLIMIT_AS,(RAM,RAM));resource.setrlimit(resource.RLIMIT_FSIZE,(DISK,DISK))
        signal.alarm(a.timeout)
        manifest=json.loads((ROOT/'native_owner_manifest.json').read_text())
        if manifest['commit']!=REI_SHA:raise ValueError('OWNER_IDENTITY')
        if a.owner_root:
            owner=a.owner_root.resolve();receipt['owner_verification']=verify_owner(owner,manifest)
        else:
            owner=out/'owner_source';receipt['owner_verification']=stage_owner(owner,manifest,a.rei_repo,a.workers)
        rustc=a.rustc or shutil.which('rustc')
        if not rustc:raise FileNotFoundError('COMPILER_MISSING')
        receipt['rustc_version']=command('compiler_version',[rustc,'-Vv'])
        build=out/'build';build.mkdir()
        for n in BUILD:(build/n).write_bytes((ROOT/n).read_bytes())
        rlib=build/'librei_microphysics.rlib'
        command('compile_owner',[rustc,'--crate-name','rei_microphysics','--crate-type','rlib','--edition=2021','-O','-C','codegen-units=1',owner/'rust/rei_microphysics/src/lib.rs','-o',rlib])
        command('compile_probe',[rustc,'--edition=2021','-O','-C','codegen-units=1',build/'native_cohort_probe.rs','--extern','rei_microphysics='+str(rlib),'-o',build/'native_cohort_probe'])
        (out/'CASES.csv').write_text(case_csv(prereg['matrix']))
        command('measure_native_cohorts',[build/'native_cohort_probe',out/'CASES.csv',out/'NATIVE_COHORTS.jsonl'])
        analysis=validate(out/'NATIVE_COHORTS.jsonl',prereg)
        write_json_once(out/'ANALYSIS.json',analysis,indent=2)
        receipt.update(status=analysis['status'],rows=analysis['rows'],measured=analysis['measured'],integrity_gates_pass=analysis['integrity_gates_pass'],
                       accuracy_targets_pass=analysis['accuracy_targets_pass'],native_output_sha256=digest((out/'NATIVE_COHORTS.jsonl').read_bytes()),
                       analysis_sha256=digest((out/'ANALYSIS.json').read_bytes()))
        receipt['artifacts_sha256']={p.name:digest(p.read_bytes()) for p in (rlib,build/'native_cohort_probe')}
        receipt['artifact_note']='Build-path dependent; raw JSONL SHA256 is the numeric reproducibility key.'
        verify_owner(owner,manifest)
        if prereg['pinned_sha256']!={n:digest((ROOT/n).read_bytes()) for n in prereg['pinned_sha256']}:
            raise ValueError('SOURCE_CHANGED_DURING_RUN')
        receipt['disk_bytes_used']=sum(p.stat().st_size for p in out.rglob('*') if p.is_file())
        if receipt['disk_bytes_used']>DISK:raise RuntimeError('DISK_LIMIT')
    except Exception as e:
        receipt.update(status='FAILED',failure_class=type(e).__name__,failure=str(e))
        raise
    finally:
        signal.alarm(0);receipt['elapsed_seconds']=time.monotonic()-started
        receipt['children_peak_rss_kib_linux']=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
        receipt['python_peak_rss_kib_linux']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        receipt['admission']={'REI_production':False,'full_EoR':False,'merge':False,'native_coupled_Einstein':False,'full_reactive_history':False}
        write_json_once(out/'RETURN_NATIVE_COHORTS.json',receipt,indent=2)
    return receipt


def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path);p.add_argument('--prereg',type=Path,default=ROOT/'evidence_s7_native/PREREGISTRATION_R2.json')
    p.add_argument('--prepare',action='store_true');p.add_argument('--publication-receipt',type=Path)
    p.add_argument('--revalidate-existing',type=Path,help='Reanalyse exactly pinned run01 raw files; do not compile or execute native code.')
    p.add_argument('--owner-root',type=Path);p.add_argument('--rei-repo',type=Path);p.add_argument('--rustc')
    p.add_argument('--workers',type=int,default=4);p.add_argument('--timeout',type=int,default=1800)
    a=p.parse_args()
    if a.prepare:
        a.prereg.parent.mkdir(parents=True,exist_ok=True);write_json_once(a.prereg,contract(),indent=2)
        print(json.dumps({'preregistration':str(a.prereg),'cases':len(matrix()),'status':'PREPARED_NOT_EXECUTED'}));return
    if not a.out:p.error('--out required for execution')
    r=revalidate_existing(a) if a.revalidate_existing else run(a);print(json.dumps({k:r[k] for k in ('status','rows','measured','integrity_gates_pass','accuracy_targets_pass','elapsed_seconds')}))
    if not r['integrity_gates_pass']:raise SystemExit(2)


if __name__=='__main__':main()

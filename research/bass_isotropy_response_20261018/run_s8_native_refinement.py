#!/usr/bin/env python3
"""Published-input-only S8 native angular refinement; never reruns S7 cases."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
from fractions import Fraction
from functools import lru_cache
import hashlib
import json
import math
import os
from pathlib import Path
import resource
import shutil
import signal
import struct
import subprocess
import time

for _key in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[_key] = '1'
import numpy as np
import angular_p24
import run_native_cohorts as s7
from run_native_adapter import REI_SHA, SOURCE_ID, RAM, DISK, digest, blob, stage_owner, verify_owner
from s6_io import write_json_once

ROOT = Path(__file__).resolve().parent
REPO = 'cosmosapjw-quantum/bass'
LANE = 'research/bass_isotropy_response_20261018/'
PREREG_REL = 'evidence_s8_native/PREREGISTRATION.json'
PINNED = ('native_angular_refinement.rs', 'run_s8_native_refinement.py', 'test_s8_native_refinement.py',
          'native_adapter.rs', 'balance.rs', 'balance_p24.rs', 'run_native_adapter.py',
          'native_owner_manifest.json', 'angular_balance.py', 'angular_p24.py', 's6_io.py',
          'run_native_cohorts.py', 'native_cohort_probe.rs', 'test_native_cohorts.py')
BUILD = ('native_angular_refinement.rs', 'native_adapter.rs', 'balance.rs', 'balance_p24.rs')
REUSED = {
    'evidence_s7_native/run01/NATIVE_COHORTS.jsonl': '4b544414a434abfb56edbf38c89807aa221b3083185bcfc2499e9f53f6db8122',
    'evidence_s7_native/run01/ANALYSIS.json': '8f776e49214a054951ed941c8fac50f3624735dc546ee0305918d2a2f488b8ee',
    'evidence_s7_native/run01/RETURN_NATIVE_COHORTS.json': 'afc45dd4f0ceada6093528a93162485c82ed4596ffef7ba865c50464de2c6949',
    'evidence_s7_native/revalidate_r2/ANALYSIS_R2.json': 'f544d08069e758de3fde2af15702e1358151ab3a3b31f58d0096b218bb78485c',
    'evidence_s7_native/revalidate_r2/RETURN_NATIVE_COHORTS_R2.json': '505ab16d01034bece450df379a400a0aa591aa4725426ec7556e16288754c456',
}


def matrix():
    return [dict(case_id=f'b{int(10*b)}_n{n}_{mode}', n_mu=n, b0=b, mode=mode,
                 n_energy=96, cells_per_segment=32, cohorts=16, beta=.2, x_observe=1.)
            for b in (.6, .9) for n in (64, 128, 256) for mode in ('prior', 'P2', 'P2P4')]


def contract():
    return {
        'schema': 'bass.native.angular.s8.preregistration.v1',
        'owner_commit': REI_SHA, 'source_id': SOURCE_ID,
        'pinned_sha256': {n: digest((ROOT/n).read_bytes()) for n in PINNED},
        'matrix': matrix(),
        'reuse_from': {'physical_execution_commit': '2865f60bf0a247eaab4997c222ad82ae22a4c8fa',
                      'analysis_publication_commit': 'c689dcf151a9b3a6ba830d2a7f4fe8cc6a68385a',
                      'files_sha256': REUSED, 'n_mu': 32, 'b0': [.6, .9],
                      'historical_internal_moment_tolerance': 3e-15,
                      'new_orders_internal_moment_tolerance': 1e-15,
                      'reuse_rule': 'Read the SHA-bound S7 evidence; do not recompile or execute n32 S7 rows.'},
        'physical_convention': {'signature': '(-,+,+,+)', 'a_perp': 'a exp(-b)', 'a_parallel': 'a exp(2b)',
                                's': 'dot b', 'Sigma': 'sqrt(3)|s|/H',
                                'a': 'exp(x)/21', 'H_per_s': 1e-16, 'nH0_cm3': 1.88e-7,
                                'birth_u': '.8*(j+.5)/16', 'birth_dt_s': '.8/16/H',
                                'stock_units': ['photons/H', 'eV/H'],
                                'energy_continuity': 'U_H_prime + U_H + 2*b_prime*DeltaP_H = 0'},
        'construction': {
            'angular_only': 'Clone original AxbiSource(...,32); replace only public angular_cells with mirrored GL64/128/256. Original owner and spectral integrals remain unchanged.',
            'same_support': 'Each new n and b uses exactly the same serialized reference nodes and birth mu for prior/P2/P24.',
            'old_stock': 'Keep n32 original transport plus state as an immutable separate block; sum native N/U/stress with new refined cohort blocks at the same geometry. No remesh or deposition onto the old mesh.',
            'old_stock_input': {'polar_indices': [0, 31], 'polar_q_ev': 5., 'polar_number_each_per_h': .0025,
                                'equatorial_indices': [15, 16], 'equatorial_q_ev': 40., 'equatorial_number_each_per_h': .001},
            'control': 'Separate same-grid synthetic anisotropic stock checks additive injection and untouched cells; it is not the old n32 block.',
            'spectral': 'Original source cells32/segment and native bins96, q=[.01,5000] eV fixed.',
            'observable': 'A_new=DeltaP_new/U_new; old stock cannot dilute the angular accuracy observable.',
        },
        'gates': {'moment_absolute': 3e-15, 'normalization_absolute': 3e-15,
                  'reflection_absolute': 5e-14, 'source_frame_mu_absolute': 5e-14,
                  'reference_gl_node_absolute': 5e-14, 'reference_gl_weight_absolute': 5e-14,
                  'reference_gl_normalization_absolute': 3e-14, 'native_prior_absolute': 5e-14,
                  'photon_source_relative': 3e-14, 'native_kernel_relative': 3e-14,
                  'native_ledger_relative': 1e-11, 'continuity_relative': 1e-11,
                  'continuum_reference_128_256_relative': 1e-12,
                  'angular_accuracy_absolute': 1e-6, 'finest_accuracy_order': 256},
        'moment_arithmetic': 'Exact unnormalized Fraction sum alpha_i*P_l(mu_i) on stored binary64; exact decimal gate3/10^15. Normalization checked separately. Native projection caller uses1e-15 internal margin only for new n>32.',
        'accuracy_scope': 'Report1e-6 target status at every new n; campaign finest-order gate applies to all six n256 rows. Retain lower-order failures and all feasibility witnesses. GL128/256 reference controls angular kernels only.',
        'limits': {'additional_workers_max': 4, 'native_threads': 1, 'blas_threads': 1,
                   'ram_bytes': RAM, 'disk_bytes': DISK, 'job_seconds_max': 1800,
                   'cases': 18, 'max_stored_cohort_cell_bytes': 16*256*96*32},
        'skill_context_used': {'name': 'physmath-research-loop', 'version': '1.3.0',
                               'package': 'c40/physmath-research-loop', 'selected_stages': 'C2-C9',
                               'resources_read': ['SKILL.md', 'references/POLICY_INTEGRATION.md', 'references/CODING_LOOP.md'],
                               'publication_boundary': 'Development tests then root publication/backups/readback before scientific campaign.',
                               'reviewer': '/root/s6_rank1'},
        'admission': {'REI_production': False, 'full_EoR': False, 'native_Einstein_feedback': False,
                      'full_reactive_history': False, 'continuum_spectral_accuracy': False},
    }


def verify_publication(path, prereg, receipt_path=None):
    if set(prereg.get('pinned_sha256', {})) != set(PINNED) or prereg != contract():
        raise ValueError('PREREGISTRATION_CONTRACT_CHANGED')
    if receipt_path:
        r = json.loads(Path(receipt_path).read_text())
        commit = r.get('commit', '')
        if (r.get('schema') != 'bass.git.preregistered.file.v1' or r.get('repo') != REPO
                or len(commit) != 40 or any(c not in '0123456789abcdef' for c in commit)
                or r.get('path') != LANE+PREREG_REL or r.get('remote_readback') is not True
                or r.get('git_blob_sha') != blob(path.read_bytes()) or r.get('sha256') != digest(path.read_bytes())):
            raise ValueError('PUBLICATION_RECEIPT_IDENTITY')
        return {'method': 'independent_git_data_connector_readback', 'commit': commit,
                'receipt_sha256': digest(Path(receipt_path).read_bytes()), 'git_blob_sha': r['git_blob_sha']}
    git = ['git', '-C', str(path.parent)]
    if subprocess.run(git+['ls-files', '--error-unmatch', path.name], capture_output=True).returncode:
        raise ValueError('PREREGISTRATION_NOT_TRACKED')
    if subprocess.run(git+['diff', '--quiet', 'HEAD', '--', path.name], capture_output=True).returncode:
        raise ValueError('PREREGISTRATION_NOT_COMMITTED')
    commit = subprocess.run(git+['log', '-1', '--format=%H', '--', path.name], capture_output=True, text=True, check=True).stdout.strip()
    return {'method': 'clean_git_preregistration', 'commit': commit}


def load_baseline():
    data = {}
    for name, sha in REUSED.items():
        raw = s7.read_native_raw(ROOT/name) if name.endswith('.jsonl') else (ROOT/name).read_bytes()
        if digest(raw) != sha:
            raise ValueError('REUSED_S7_IDENTITY:'+name)
        data[name] = raw
    receipt = json.loads(data['evidence_s7_native/run01/RETURN_NATIVE_COHORTS.json'])
    r2 = json.loads(data['evidence_s7_native/revalidate_r2/RETURN_NATIVE_COHORTS_R2.json'])
    if (receipt['owner_commit'] != REI_SHA or receipt['source_id'] != SOURCE_ID
            or receipt['publication']['commit'] != '2865f60bf0a247eaab4997c222ad82ae22a4c8fa'
            or r2['new_analysis_publication']['commit'] != 'c689dcf151a9b3a6ba830d2a7f4fe8cc6a68385a'):
        raise ValueError('REUSED_S7_PROVENANCE')
    for name in ('native_cohort_probe.rs', 'native_adapter.rs', 'balance.rs', 'balance_p24.rs', 'native_owner_manifest.json'):
        if digest((ROOT/name).read_bytes()) != receipt['pinned_sha256'][name]:
            raise ValueError('REUSED_NATIVE_OWNER_DEPENDENCY_CHANGED:'+name)
    rawrows = [json.loads(l) for l in data['evidence_s7_native/run01/NATIVE_COHORTS.jsonl'].splitlines()]
    baseline = [r for r in rawrows if r.get('block') == 'angular' and r.get('n_mu') == 32 and r.get('b0') in (.6, .9)]
    analysis = json.loads(data['evidence_s7_native/revalidate_r2/ANALYSIS_R2.json'])
    if len(baseline) != 6:
        raise ValueError('REUSED_S7_BASELINE_ROWS')
    return baseline, analysis


@lru_cache(maxsize=8)
def gl(n):
    x, w = np.polynomial.legendre.leggauss(n)
    return x, .5*w


def reference_rule(row, gates):
    nu = np.asarray(row['reference_nu'], dtype=float)
    q = np.asarray(row['reference_count_fraction'], dtype=float)
    expected_nu, expected_q = gl(row['n_mu'])
    if (nu.shape != expected_nu.shape or q.shape != nu.shape or not np.isfinite(nu).all()
            or not np.isfinite(q).all() or np.any(q <= 0) or np.any(np.abs(nu) >= 1)
            or np.any(np.diff(nu) <= 0) or np.max(np.abs(nu+nu[::-1])) > gates['reflection_absolute']
            or np.max(np.abs(q-q[::-1])) > gates['reflection_absolute']
            or abs(math.fsum(q)-1) > gates['reference_gl_normalization_absolute']
            or np.max(np.abs(nu-expected_nu)) > gates['reference_gl_node_absolute']
            or np.max(np.abs(q-expected_q)) > gates['reference_gl_weight_absolute']):
        raise ValueError('REFERENCE_GL_SUPPORT_IDENTITY')
    return nu, q


def birth_rule(nu, q, b):
    # Jacobian has one power of the solid-angle map: dmu/dnu=R_b^-3.
    rb = np.sqrt(np.exp(2*b)*(1-nu*nu)+np.exp(-4*b)*nu*nu)
    mu = np.exp(-2*b)*nu/rb
    prior = q/(rb**3)
    return mu, prior/math.fsum(prior)


def check_birth_frame(row, birth, j, nu, q, gates):
    u = .8*(j+.5)/16; b = row['b0']+.2*u
    expected_mu, prior = birth_rule(nu, q, b)
    mu = np.asarray(birth['mu'], dtype=float)
    if (abs(birth['u']-u)>2e-16 or abs(birth['b']-b)>2e-16
            or abs(birth['z']-(21*math.exp(-u)-1))>5e-14
            or abs(birth['dt_s']/(.8/16/1e-16)-1)>gates['photon_source_relative']
            or mu.shape != expected_mu.shape or not np.isfinite(mu).all()
            or np.max(np.abs(mu-expected_mu))>gates['source_frame_mu_absolute']):
        raise ValueError('BIRTH_SOURCE_FRAME_IDENTITY')
    actual_prior = np.asarray(birth['prior'], dtype=float)
    if (actual_prior.shape != mu.shape or not np.isfinite(actual_prior).all()
            or np.max(np.abs(actual_prior-prior))>gates['native_prior_absolute']):
        raise ValueError('BIRTH_PRIOR_JACOBIAN_IDENTITY')
    return mu, actual_prior


def check_failure(row, nu, q, gates):
    j = row.get('failed_birth')
    if isinstance(j, bool) or not isinstance(j, int) or not 0 <= j < 16:
        raise ValueError('FAILURE_BIRTH_INDEX')
    u = .8*(j+.5)/16
    if not isinstance(row.get('failed_u'), (int, float)) or not math.isfinite(row['failed_u']) or abs(row['failed_u']-u)>2e-16:
        raise ValueError('FAILURE_BIRTH_TIME')
    mu = np.asarray(row['support_mu'], dtype=float)
    expected, _ = birth_rule(nu, q, row['b0']+.2*u)
    if mu.shape != expected.shape or not np.isfinite(mu).all() or np.max(np.abs(mu-expected))>gates['source_frame_mu_absolute']:
        raise ValueError('FAILURE_SOURCE_FRAME_IDENTITY')
    if row['mode'] == 'P2':
        z = mu*mu
        independent = 'INFEASIBLE_ANGULAR_SUPPORT' if not (z.min()<1/3<z.max()) else 'STRICT_INTERIOR'
        witness = {'z_min': float(z.min()), 'z_max': float(z.max())}
    else:
        f = angular_p24.feasibility(mu); independent = f.status; witness = vars(f)
    if row['status'] == 'FEASIBILITY_FAILURE' and row['failure'] != independent:
        raise ValueError('FAILURE_FEASIBILITY_WITNESS')
    return {'independent_status': independent, 'geometry': witness}


def old_state_identity(row):
    if row.get('old_n_mu') != 32 or row.get('old_cell_count') != 3072:
        raise ValueError('OLD_BLOCK_GRID_CHANGED')
    packed = []
    for label in ('before', 'after'):
        vectors = [[0]*3072 for _ in range(4)]; seen = set()
        for item in row['old_sparse_'+label]:
            if len(item)!=5 or isinstance(item[0],bool) or not isinstance(item[0],int) or not 0<=item[0]<3072 or item[0] in seen:
                raise ValueError('OLD_BLOCK_SPARSE_INPUT')
            seen.add(item[0])
            for j, word in enumerate(item[1:]):
                if not isinstance(word,str) or len(word)!=16 or any(c not in '0123456789abcdef' for c in word):
                    raise ValueError('OLD_BLOCK_BIT_PATTERN')
                vectors[j][item[0]]=int(word,16)
        raw=b''.join(struct.pack('<Q',word) for vec in vectors for word in vec)
        h=0xcbf29ce484222325
        for byte in raw:
            h=((h^byte)*0x100000001b3)&((1<<64)-1)
        if f'{h:016x}' != row['old_digest_'+label+'_fnv1a64']:
            raise ValueError('OLD_BLOCK_DIGEST_IDENTITY')
        packed.append(raw)
    if packed[0] != packed[1]:
        raise ValueError('OLD_BLOCK_MUTATED')
    if packed[0] != old_input_bytes():
        raise ValueError('OLD_BLOCK_INPUT_CHANGED')
    return digest(packed[0])


def old_input_bytes():
    """Independent exact binary64 encoding of the declared four native deltas."""
    vectors = [[0.0]*3072 for _ in range(4)]
    edges = [.01*math.exp(math.log(5000/.01)*i/96) for i in range(97)]
    for ray,q,number in ((0,5.,.0025),(31,5.,.0025),(15,40.,.001),(16,40.,.001)):
        energy_bin = sum(edge <= q for edge in edges)-1
        k = 96*ray+energy_bin
        for vec,value in zip(vectors,(number,q*number,q,q)):
            vec[k]=value
    return b''.join(struct.pack('<d',value) for vec in vectors for value in vec)


def require_finite(value):
    if isinstance(value,float) and not math.isfinite(value):raise ValueError('NATIVE_NONFINITE_VALUE')
    if isinstance(value,dict):
        for v in value.values():require_finite(v)
    elif isinstance(value,list):
        for v in value:require_finite(v)


def decision_flags(failures):
    """Verified support absence limits the target; a solver error fails integrity."""
    target_gates={'FINEST_ANGULAR_ACCURACY_TARGET','FINEST_ORDER_UNAVAILABLE'}
    return {'integrity_gates_pass':not any(f['gate'] not in target_gates for f in failures),
            'finest_accuracy_targets_pass':not any(f['gate'] in target_gates for f in failures)}


def validate(path, prereg, baseline):
    def reject(v):
        raise ValueError('NATIVE_NONFINITE_JSON:'+v)
    recs=[json.loads(l,parse_constant=reject) for l in Path(path).read_text().splitlines() if l.strip()]
    require_finite(recs)
    if not recs:
        raise ValueError('MISSING_NATIVE_COMPLETION')
    done=recs.pop(); expected={r['case_id']:r for r in prereg['matrix']}
    if (done.get('schema')!='bass.native.angular.s8.complete.v1' or done.get('rows')!=len(expected)
            or done.get('owner_commit')!=REI_SHA or done.get('source_id')!=SOURCE_ID
            or len(recs)!=len(expected) or {r.get('case_id') for r in recs}!=set(expected)):
        raise ValueError('NATIVE_COMPLETION_OR_CASE_MATRIX')
    g=prereg['gates']; failures=[]; support=[]; metrics=[]; node_sets={}; birth_node_sets={}; spectral_digest=None; old_digests=set()
    def check(ok,tag,row,value=None):
        if not bool(ok):failures.append({'case_id':row['case_id'],'gate':tag,'value':value})
    for row in recs:
        if row.get('schema')!='bass.native.angular.s8.row.v1' or any(row.get(k)!=v for k,v in expected[row['case_id']].items()) or row.get('internal_moment_tolerance')!=1e-15:
            raise ValueError('NATIVE_ROW_IDENTITY')
        nu,q=reference_rule(row,g); support_key=(row['b0'],row['n_mu'])
        reference_bytes=np.asarray([nu,q],dtype='<f8').tobytes()
        if support_key in node_sets and reference_bytes!=node_sets[support_key]:raise ValueError('CONSTRAINTS_CHANGED_SUPPORT')
        node_sets[support_key]=reference_bytes
        if row['status']!='MEASURED':
            if row['status'] not in ('FEASIBILITY_FAILURE','NUMERICAL_FAILURE') or row['mode']=='prior':raise ValueError('UNKNOWN_NATIVE_FAILURE')
            witness=check_failure(row,nu,q,g)
            support.append({k:row[k] for k in ('case_id','status','failure','failed_birth','failed_u','n_mu','b0','mode')}|witness)
            if row['status']=='NUMERICAL_FAILURE':check(False,'PROJECTION_NUMERICAL_FAILURE',row,row['failure'])
            continue
        if row.get('source_id')!=SOURCE_ID or len(row['births'])!=16:raise ValueError('NATIVE_BIRTH_COUNT_OR_OWNER')
        check(row.get('spectral_bits_identical') is True and row.get('source_rate_bits_identical') is True,'SPECTRAL_SOURCE_OWNER',row)
        if spectral_digest is None:spectral_digest=row['spectral_digest_fnv1a64']
        if spectral_digest!=row['spectral_digest_fnv1a64']:raise ValueError('SPECTRAL_BITS_CHANGED_BETWEEN_CASES')
        old_sha=old_state_identity(row);old_digests.add(old_sha)
        check(row.get('survivors_bitwise_frozen') is True,'FROZEN_SURVIVOR_BLOCKS',row)
        pn=[];pu=[];pp=[];qu=[];qp=[];iso={order:[[],[]] for order in (128,256)}; exact=[]; photon_m=[]; energy_m=[]
        birth_digests=[]
        for j,birth in enumerate(row['births']):
            mu,prior=check_birth_frame(row,birth,j,nu,q,g)
            birth_key=(row['b0'],row['n_mu'],j);mu_bytes=np.asarray(mu,dtype='<f8').tobytes()
            if birth_key in birth_node_sets and mu_bytes!=birth_node_sets[birth_key]:raise ValueError('CONSTRAINTS_CHANGED_BIRTH_NODES')
            birth_node_sets[birth_key]=mu_bytes
            alpha=np.asarray(birth['alpha'],dtype=float);ea=np.asarray(birth['energy_alpha'],dtype=float);na=np.asarray(birth['photon_alpha'],dtype=float)
            if any(x.shape!=mu.shape or not np.isfinite(x).all() for x in (alpha,ea,na)):raise ValueError('NATIVE_BIRTH_WEIGHT_DOMAIN')
            norm,m2,m4=s7.exact_moments(mu,alpha)
            check(np.all(alpha>0) and np.all(ea>0) and np.all(na>0),'POSITIVE_NATIVE_BIRTH',row,j)
            check(abs(norm-1)<=Fraction(str(g['normalization_absolute'])),'WEIGHT_NORMALIZATION',row,float(norm-1))
            check(np.max(np.abs(alpha-alpha[::-1]))<=g['reflection_absolute'] and np.max(np.abs(mu+mu[::-1]))<=g['reflection_absolute'],'BIRTH_REFLECTION',row,j)
            if row['mode']=='prior':check(np.max(np.abs(alpha-prior))<=g['native_prior_absolute'],'PRIOR_WEIGHT_IDENTITY',row,j)
            else:
                gate=Fraction(str(g['moment_absolute']))
                check(abs(m2)<=gate and (row['mode']!='P2P4' or abs(m4)<=gate),'EXACT_BIRTH_MOMENTS',row,{'birth':j,'M2':float(m2),'M4':float(m4)})
            exact.append([float(m2),float(m4)])
            photon_m.append([float(v) for v in s7.exact_moments(mu,na)[1:]])
            energy_m.append([float(v) for v in s7.exact_moments(mu,ea)[1:]])
            u=.8*(j+.5)/16; amount=float(s7.source_rate(u))*.8/16/1e-16
            check(abs(birth['source_amount']/amount-1)<=g['photon_source_relative'] and abs(birth['n_birth']/amount-1)<=g['photon_source_relative'],'OWNER_PHOTON_SOURCE',row,j)
            r,d=s7.kernels(.2*(1-u),mu);amp=birth['u_birth']*math.exp(u-1)
            pn.append(birth['n_birth']);pu.append(amp*math.fsum(ea*r));pp.append(amp*math.fsum(ea*d))
            qu.append(amp*math.fsum(alpha*r));qp.append(amp*math.fsum(alpha*d))
            for order in iso:
                x,w=gl(order);rr,dd=s7.kernels(.2*(1-u),x)
                iso[order][0].append(amp*math.fsum(w*rr));iso[order][1].append(amp*math.fsum(w*dd))
            birth_digests.append(digest(np.asarray([mu,alpha],dtype='<f8').tobytes()))
        n=math.fsum(pn);u=math.fsum(pu);p=math.fsum(pp)
        kernel_error=max(abs(row['n_final']-n)/n,abs(row['u_final']-u)/u,abs(row['stress_final']-p)/u,
                         abs(row['predicted_u']-u)/u,abs(row['predicted_stress']-p)/u)
        check(kernel_error<=g['native_kernel_relative'],'NATIVE_R_D_KERNEL',row,kernel_error)
        native_v=np.array([row['n_final'],row['u_final'],row['stress_final']]);old=np.asarray(row['old_values']);combined=np.asarray(row['combined_block_values'])
        baseline_old=next(r for r in baseline if r['b0']==row['b0'] and r['mode']=='prior')
        expected_old=np.array([baseline_old['old_n'],baseline_old['old_u'],baseline_old['old_stress']])
        old_error=max(abs(old-expected_old)/np.array([expected_old[0],expected_old[1],expected_old[1]]))
        check(old_error<=g['native_ledger_relative'],'REUSED_OLD32_OBSERVATION',row,old_error)
        block_error=max(abs(combined-old-native_v)/np.array([combined[0],combined[1],combined[1]]))
        check(block_error<=g['native_ledger_relative'],'MULTIGRID_NATIVE_BLOCK_SUM',row,block_error)
        ci=np.asarray(row['same_grid_control_initial']);cf=np.asarray(row['same_grid_control_final'])
        control_error=max(abs(cf-ci-native_v)/np.array([cf[0],cf[1],cf[1]]))
        ledger=max(row['max_increment_ledger_n_relative'],row['max_increment_ledger_u_relative'],row['max_native_reported_ledger_relative'],control_error)
        check(ledger<=g['native_ledger_relative'],'FINITE_BIN_TRANSFER_LEDGER',row,ledger)
        check(row['max_cell_add_absolute']==0 if row['mode']!='prior' else row['max_cell_add_relative']<=g['native_ledger_relative'],'SAME_GRID_INCREMENT_PRESERVATION',row)
        check(max(abs(v) for v in row['energy_continuity_relative'])<=g['continuity_relative'],'PER_H_CONTINUITY',row,row['energy_continuity_relative'])
        ref={order:[math.fsum(v) for v in pair] for order,pair in iso.items()}
        ref_error=max(abs(np.asarray(ref[128])-ref[256]))/ref[256][0]
        check(ref_error<=g['continuum_reference_128_256_relative'],'CONTINUUM_ANGULAR_REFERENCE',row,ref_error)
        ref_a=ref[256][1]/ref[256][0];observed_a=row['stress_final']/row['u_final'];err=observed_a-ref_a
        check(abs(row['a_response']-observed_a)<=g['native_kernel_relative'],'NEW_ONLY_OBSERVABLE',row)
        target=abs(err)<=g['angular_accuracy_absolute']
        if row['n_mu']==g['finest_accuracy_order']:check(target,'FINEST_ANGULAR_ACCURACY_TARGET',row,err)
        metrics.append({**expected[row['case_id']],'a_response':observed_a,'continuum_a':ref_a,'angular_a_error':err,'accuracy_target_met':target,
                        'discrete_alpha_a_error':math.fsum(qp)/math.fsum(qu)-ref_a,
                        'native_minus_discrete_alpha_a':observed_a-math.fsum(qp)/math.fsum(qu),
                        'max_exact_weight_moments':np.max(np.abs(exact),axis=0).tolist(),
                        'max_photon_moments_diagnostic':np.max(np.abs(photon_m),axis=0).tolist(),
                        'max_energy_moments_diagnostic':np.max(np.abs(energy_m),axis=0).tolist(),
                        'native_kernel_relative':kernel_error,'native_transfer_ledger_relative':ledger,
                        'old_block_sha256':old_sha,'old32_reuse_relative':old_error,'native_block_sum_relative':block_error,
                        'continuum_reference_relative':ref_error,'birth_mu_alpha_sha256':birth_digests})
    if len(old_digests)>1:raise ValueError('OLD_BLOCK_CHANGED_ACROSS_REFINEMENT')
    finest={r['case_id'] for r in prereg['matrix'] if r['n_mu']==g['finest_accuracy_order']}
    for case_id in finest-{r['case_id'] for r in metrics}:failures.append({'case_id':case_id,'gate':'FINEST_ORDER_UNAVAILABLE','value':None})
    all_ok=not failures
    return {'schema':'bass.native.angular.s8.analysis.v1','rows':len(recs),'measured':len(metrics),
            'status':'PASS_SCOPED_FINEST_NATIVE_ANGULAR' if all_ok else 'COMPLETED_WITH_RETAINED_FAILURES',
            **decision_flags(failures),
            'gate_failures':failures,'support_or_numerical_failures':support,'metrics':metrics,
            'lower_resolution_target_failures':[r['case_id'] for r in metrics if not r['accuracy_target_met'] and r['n_mu']<256],
            'old_block_sha256':next(iter(old_digests),None),'reused_s7_science_rerun':False}


def run(a):
    if not 1<=a.workers<=4 or not 1<=a.timeout<=1800:raise ValueError('EXECUTION_LIMIT')
    path=a.prereg.resolve();prereg=json.loads(path.read_text());published=verify_publication(path,prereg,a.publication_receipt)
    baseline,old_analysis=load_baseline()
    out=a.out.resolve()
    if out.exists():raise FileExistsError(out)
    out.mkdir(parents=True);start=time.monotonic();deadline=start+a.timeout
    receipt={'schema':'bass.native.angular.s8.execution.v1','started_utc':datetime.now(timezone.utc).isoformat(),'status':'STARTED',
             'owner_commit':REI_SHA,'source_id':SOURCE_ID,'publication':published,'preregistration_sha256':digest(path.read_bytes()),
             'pinned_sha256':prereg['pinned_sha256'],'reused_s7_sha256':REUSED,'reused_s7_science_rerun':False,
             'numpy_version':np.__version__,'limits':prereg['limits']|{'additional_workers':a.workers,'job_seconds':a.timeout},'commands':[]}
    def limit():
        resource.setrlimit(resource.RLIMIT_AS,(RAM,RAM));resource.setrlimit(resource.RLIMIT_FSIZE,(DISK,DISK))
    def command(label,args):
        left=deadline-time.monotonic()
        if left<=0:raise TimeoutError('JOB_SECONDS')
        t=time.monotonic()
        try:p=subprocess.run(list(map(str,args)),capture_output=True,timeout=left,preexec_fn=limit,env={**os.environ,'RUST_TEST_THREADS':'1'})
        except subprocess.TimeoutExpired as e:
            (out/(label+'.stdout')).write_bytes(e.stdout or b'');(out/(label+'.stderr')).write_bytes(e.stderr or b'');raise
        (out/(label+'.stdout')).write_bytes(p.stdout);(out/(label+'.stderr')).write_bytes(p.stderr)
        receipt['commands'].append({'label':label,'args':list(map(str,args)),'seconds':time.monotonic()-t,'exit_code':p.returncode})
        if p.returncode:raise RuntimeError('COMMAND_FAILED:'+label)
        return p.stdout.decode(errors='replace')
    try:
        limit();signal.alarm(a.timeout)
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
        for name in BUILD:(build/name).write_bytes((ROOT/name).read_bytes())
        rlib=build/'librei_microphysics.rlib'
        command('compile_owner',[rustc,'--crate-name','rei_microphysics','--crate-type','rlib','--edition=2021','-O','-C','codegen-units=1',owner/'rust/rei_microphysics/src/lib.rs','-o',rlib])
        command('compile_refinement',[rustc,'--edition=2021','-O','-C','codegen-units=1',build/'native_angular_refinement.rs','--extern','rei_microphysics='+str(rlib),'-o',build/'native_angular_refinement'])
        (out/'CASES.csv').write_text(''.join(f"{r['case_id']},{r['n_mu']},{r['b0']},{r['mode']}\n" for r in prereg['matrix']))
        write_json_once(out/'REUSED_S7_BASELINE.json',{'reused_sha256':REUSED,'rows':baseline,
                        'metrics':[r for r in old_analysis['metrics'] if r['case_id'] in {r['case_id'] for r in baseline}],
                        'failures':[r for r in old_analysis['support_or_numerical_failures'] if r['case_id'] in {r['case_id'] for r in baseline}],
                        'historical_inner_tolerance':3e-15,'new_orders_inner_tolerance':1e-15,'native_reexecution':False},indent=2)
        command('measure_native_refinement',[build/'native_angular_refinement',out/'CASES.csv',out/'NATIVE_ANGULAR_REFINEMENT.jsonl'])
        analysis=validate(out/'NATIVE_ANGULAR_REFINEMENT.jsonl',prereg,baseline)
        write_json_once(out/'ANALYSIS.json',analysis,indent=2)
        receipt.update({k:analysis[k] for k in ('status','rows','measured','integrity_gates_pass','finest_accuracy_targets_pass')})
        receipt['raw_sha256']=digest((out/'NATIVE_ANGULAR_REFINEMENT.jsonl').read_bytes());receipt['analysis_sha256']=digest((out/'ANALYSIS.json').read_bytes())
        receipt['compiled_artifact_sha256']={p.name:digest(p.read_bytes()) for p in (rlib,build/'native_angular_refinement')}
        verify_owner(owner,manifest);load_baseline()
        if prereg!=contract():raise ValueError('SOURCE_CHANGED_DURING_RUN')
        receipt['disk_bytes_used']=sum(p.stat().st_size for p in out.rglob('*') if p.is_file())
        if receipt['disk_bytes_used']>DISK:raise RuntimeError('DISK_LIMIT')
    except Exception as e:
        receipt.update(status='FAILED',failure_class=type(e).__name__,failure=str(e));raise
    finally:
        signal.alarm(0);receipt['elapsed_seconds']=time.monotonic()-start
        receipt['children_peak_rss_kib_linux']=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
        receipt['python_peak_rss_kib_linux']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        receipt['admission']=prereg['admission'];write_json_once(out/'RETURN_NATIVE_ANGULAR_REFINEMENT.json',receipt,indent=2)
    return receipt


def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path);p.add_argument('--prereg',type=Path,default=ROOT/PREREG_REL)
    p.add_argument('--prepare',action='store_true');p.add_argument('--publication-receipt',type=Path)
    p.add_argument('--owner-root',type=Path);p.add_argument('--rei-repo',type=Path);p.add_argument('--rustc')
    p.add_argument('--workers',type=int,default=4);p.add_argument('--timeout',type=int,default=1800)
    a=p.parse_args()
    if a.prepare:
        a.prereg.parent.mkdir(parents=True,exist_ok=True);write_json_once(a.prereg,contract(),indent=2)
        print(json.dumps({'status':'PREPARED_NOT_EXECUTED','cases':len(matrix()),'path':str(a.prereg)}));return
    if not a.out:p.error('--out required')
    r=run(a);print(json.dumps({k:r[k] for k in ('status','rows','measured','integrity_gates_pass','finest_accuracy_targets_pass','elapsed_seconds')}))
    if not r['integrity_gates_pass']:raise SystemExit(2)


if __name__=='__main__':main()

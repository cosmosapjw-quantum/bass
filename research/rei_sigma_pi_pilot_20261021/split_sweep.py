#!/usr/bin/env python3
"""Independent signed (Sigma, Pi_m, Pi_r) adapter to the unchanged C15 owner."""
from __future__ import annotations
import argparse
import csv
from dataclasses import replace
import glob
import hashlib
import json
import math
from pathlib import Path
import platform
import sys
import traceback

import sweep as prior
from sigma_pi_map import initial_seed, invariants

LANE = Path(__file__).resolve().parent
CONTRACT = LANE/'SPLIT_CONTRACT.json'
OWNER_REF = prior.OWNER_REF
canonical, digest, write_json = prior.canonical, prior.digest, prior.write_json


def parameters(Sigma=0., orientation=0, alpha_m=0., alpha_r=0.):
    return replace(prior.parameters(Sigma, orientation, alpha_r),
                   massive_quadrupole=alpha_m)


class PreparedContext(prior.PreparedContext):
    """Reuse fixed source preparation, with independent fresh component seeds.

    No owner evolution method, reduction, solver, or physical gate is changed.
    """
    def __init__(self):
        super().__init__()
        fixed = self.shared
        self.calibration = {
            'H_base_per_s': self.calibration['H_base_per_s'],
            'massive_J01': self.calibration['massive_J01'],
            'matter_stress_per_alpha_Pa': fixed['mass_ref_density']*self.calibration['massive_J01']/5,
            'radiation_stress_per_alpha_Pa': (fixed['E_gamma0']/fixed['a0']**4 +
                                             fixed['E_nu0']/fixed['a0']**4)/5,
            'kappa_time': self.calibration['kappa_time']}

    def model(self, params):
        import numpy as np
        owner = prior.load_owner()
        if params != parameters(params.Sigma_initial, params.orientation,
                                params.massive_quadrupole, params.gamma_quadrupole):
            raise ValueError('SPLIT_FIXED_PARAMETER_OR_GAMMA_NU_SEED_MISMATCH')
        model = object.__new__(owner.EinsteinBoltzmann)
        model.__dict__.update(self.shared)
        model.params = params
        # Exactly the original owner initializer's expression and order.
        model.massive_weight = (model.massive.rw[:,None]/model.massive.norm)*(
            model.massive.wmu*(1+params.massive_quadrupole*model.massive.p2))[None,:]
        if np.any(model.massive_weight < 0):
            raise ValueError('SOURCE_BASS_MASSIVE_POSITIVE_VLASOV_WEIGHTS')
        model.iterations = 0
        model.rhs_evals = 0
        return model


def signed_grid(contract=None):
    contract = contract or json.loads(CONTRACT.read_text())
    result = []
    signs = lambda x: (0,) if x == 0 else (-1,1)
    for sigma in contract['grid']['Sigma_half']:
        for pm in contract['grid']['Pi_m_half']:
            for pr in contract['grid']['Pi_r_half']:
                for ss in signs(sigma):
                    for sm in signs(pm):
                        for sr in signs(pr):
                            result.append({'case_id':f'split_{len(result):04d}',
                                'Sigma_half_requested':sigma,
                                'Pi_m_half_requested':pm,'Pi_r_half_requested':pr,
                                'shear_sign_requested':ss,
                                'matter_stress_sign_requested':sm,
                                'radiation_stress_sign_requested':sr,
                                'signed_Sigma_requested':ss*sigma,
                                'signed_Pi_m_requested':sm*pm,
                                'signed_Pi_r_requested':sr*pr,
                                'signed_Pi_total_requested':sm*pm+sr*pr,
                                'nominal_cancellation':sm*pm+sr*pr == 0})
    return result


def seed_for(case, context):
    cal = context.calibration
    def component(prefix, sign_key, weight):
        return initial_seed(Sigma_half=case['Sigma_half_requested'],
            Pi_half=case[f'Pi_{prefix}_half_requested'],
            shear_sign=case['shear_sign_requested'], stress_sign=case[sign_key],
            H_base=cal['H_base_per_s'], stress_per_alpha=cal[weight],
            kappa_time=cal['kappa_time'])
    matter = component('m','matter_stress_sign_requested','matter_stress_per_alpha_Pa')
    radiation = component('r','radiation_stress_sign_requested','radiation_stress_per_alpha_Pa')
    return {'alpha_m':matter['common_P2_alpha'],'alpha_r':radiation['common_P2_alpha'],
            'H_initial_per_s':matter['H_initial_per_s'],
            's_initial_per_s':matter['s_initial_per_s'],
            'D_m_initial_requested_Pa':matter['delta_pressure_initial_Pa'],
            'D_r_initial_requested_Pa':radiation['delta_pressure_initial_Pa'],
            'Pi_m_half_negative_cap':matter['Pi_half_negative_cap'],
            'Pi_m_half_positive_cap':matter['Pi_half_positive_cap'],
            'Pi_r_half_negative_cap':radiation['Pi_half_negative_cap'],
            'Pi_r_half_positive_cap':radiation['Pi_half_positive_cap']}


def normalize_row(row):
    """Compute physical components from this row, sum tensors, then take norm."""
    owner = prior.load_owner()
    s,H = row['s_inv_s'],row['H']
    dm = row['Pi_massive']
    dr = row['Pi_gamma']+row['Pi_nu']+row['Pi_UV']
    dt = dm+dr
    kt = 3*owner.KAPPA
    total = invariants(s=s,H=H,delta_pressure=dt,kappa_time=kt)
    out = dict(total)
    factor = kt/(math.sqrt(3)*H*H)
    out.update({'signed_Sigma':math.sqrt(3)*s/H,
        'D_m_Pa':dm,'D_r_Pa':dr,'D_total_Pa':dt,'D_physical_Pa':dt,
        'signed_Pi_m':factor*dm,'signed_Pi_r':factor*dr,
        'signed_Pi_total':factor*dt,'signed_Pi':factor*dt,
        'Pi_m_half':factor*abs(dm),'Pi_r_half':factor*abs(dr),
        'Pi_total_half':total['Pi_half'],
        'Pi_m_frobenius':math.sqrt(2)*factor*abs(dm),
        'Pi_r_frobenius':math.sqrt(2)*factor*abs(dr),
        'Pi_total_frobenius':total['Pi_frobenius'],
        'shear_work_m_J_m3_s':2*s*dm,
        'shear_work_r_J_m3_s':2*s*dr,
        'shear_work_total_J_m3_s':2*s*dt,
        'Pi_component_norm_sum':factor*(abs(dm)+abs(dr)),
        'cancellation_fraction':1-abs(dt)/(abs(dm)+abs(dr)) if abs(dm)+abs(dr) > 0 else 0.})
    for label in ('m','r','total'):
        value = out[f'Pi_{label}_half']
        signed = out[f'signed_Pi_{label}']
        out[f'stress_{label}_sign'] = 1 if signed > 0 else -1 if signed < 0 else 0
        out[f'Pi_{label}_orientation_status'] = ('RESOLVED' if value >= 3e-13
            else 'NUMERICALLY_UNRESOLVED_BELOW_PI_3E-13')
    out['Pi_orientation_status'] = out['Pi_total_orientation_status']
    out['work_sum_residual_J_m3_s'] = (out['shear_work_m_J_m3_s']+
        out['shear_work_r_J_m3_s']-out['shear_work_total_J_m3_s'])
    row.update(out)
    return row


def initial_record(model, state):
    # Reuse the prior owner-initial raw extraction. Replace normalization with
    # the explicitly grouped matter+radiation tensor sum above.
    return normalize_row(prior.initial_record(model,state))


def initial_checks(case, row):
    errors = {'Sigma_initial_abs':abs(row['Sigma_half']-case['Sigma_half_requested']),
        'Pi_m_initial_abs':abs(row['Pi_m_half']-case['Pi_m_half_requested']),
        'Pi_r_initial_abs':abs(row['Pi_r_half']-case['Pi_r_half_requested']),
        'signed_Sigma_initial_abs':abs(row['signed_Sigma']-case['signed_Sigma_requested']),
        'signed_Pi_m_initial_abs':abs(row['signed_Pi_m']-case['signed_Pi_m_requested']),
        'signed_Pi_r_initial_abs':abs(row['signed_Pi_r']-case['signed_Pi_r_requested']),
        'signed_Pi_total_initial_abs':abs(row['signed_Pi_total']-case['signed_Pi_total_requested'])}
    if any(value > 3e-13 for value in errors.values()):
        raise RuntimeError(f'SPLIT_INITIAL_INVARIANT_MISMATCH {errors}')
    return errors


def run_case(case, context, nsteps):
    seed = seed_for(case,context)
    params = parameters(case['Sigma_half_requested'],case['shear_sign_requested'],
                        seed['alpha_m'],seed['alpha_r'])
    model = context.model(params)
    initial = initial_record(model,model.initial())
    checks = initial_checks(case,initial)
    result = model.run(nsteps=nsteps,compress=True,feedback=True)
    for row in result['history']:
        normalize_row(row)
        if not (row['H'] > 0 and 10000 <= row['Tgas_K'] <= 24000 and
                0 <= row['x_HII'] <= 1 and 0 <= row['x_HeII'] <= 1):
            raise RuntimeError('SPLIT_PHYSICAL_DOMAIN')
    errors = result['errors']
    gates = {key:bool(value) for key,value in {
        'number_5e-12':errors['photochemical_number_abs_max'] <= 5e-12,
        'energy_5e-11':errors['photochemical_energy_eV_H_abs_max'] <= 5e-11,
        'gamma_monopole_3e-9':errors['gamma_number_monopole_abs_max'] <= 3e-9,
        'nu_monopole_3e-9':errors['nu_number_monopole_abs_max'] <= 3e-9,
        'initial_mapping_3e-13':all(v <= 3e-13 for v in checks.values()),
        'positive_matter_P2':-1 <= seed['alpha_m'] <= 2,
        'positive_radiation_P2':-1 <= seed['alpha_r'] <= 2,
        'finite_success_json':True}.items()}
    if not all(gates.values()):
        raise RuntimeError(f'SPLIT_ORIGINAL_GATE_FAILURE {gates}')
    output = {'case':case,'seed':seed,'calibration':context.calibration,
              'initial':initial,'numeric_checks':checks,'gates':gates,
              'owner_result':result}
    canonical(output)  # exact scalar export, strict nonfinite rejection
    return output


def source_binding():
    prior.verify_snapshot()
    files = [p for p in prior.SNAPSHOT.rglob('*') if p.is_file() and p.suffix in ('.py','.csv','.json')]
    files += [Path(__file__),CONTRACT,LANE/'sweep.py',LANE/'sigma_pi_map.py',
              prior.CONTRACT,prior.SOURCE_MANIFEST]
    bound = [{'path':str(p.resolve()),'sha256':digest(p)} for p in sorted(set(files))]
    source = hashlib.sha256(canonical([{'path':str(Path(x['path']).relative_to(LANE)),
                                       'sha256':x['sha256']} for x in bound])).hexdigest()
    import numpy, scipy
    toolchain = {'python':platform.python_version(),'numpy':numpy.__version__,
                 'scipy':scipy.__version__}
    return source,bound,toolchain


def prepare(args):
    contract = json.loads(CONTRACT.read_text())
    if not 2 <= args.nsteps <= 1024 or args.group_size < 1:
        raise ValueError('SPLIT_PREPARE_STEP_OR_GROUP_DOMAIN')
    out = Path(args.out).resolve()
    cases = signed_grid(contract)
    if len(cases) != contract['grid']['distinct_cases']:
        raise ValueError('SPLIT_CONTRACT_CASE_COUNT')
    source,bound,toolchain = source_binding()
    science = {'contract':contract,'cases':cases,'nsteps':args.nsteps,'compress':True,'feedback':True}
    binding = {'source':source,'input':hashlib.sha256(canonical(science)).hexdigest(),
               'toolchain':hashlib.sha256(canonical(toolchain)).hexdigest()}
    context = PreparedContext()
    seeds = [seed_for(case,context) for case in cases]
    source_bound = list(bound)
    jobs = []
    for i in range(0,len(cases),args.group_size):
        jid = f'split_group_{i//args.group_size:03d}'
        path = out/'inputs'/f'{jid}.json'
        data = {'schema':'rei.sigma_pi_split.group_input.v1','science_binding':binding,
                'toolchain':toolchain,'nsteps':args.nsteps,'cases':cases[i:i+args.group_size],
                'owner_ref':OWNER_REF,'bound_files':source_bound}
        write_json(path,data,immutable=True)
        bound.append({'path':str(path),'sha256':digest(path)})
        jobs.append({'id':jid,'argv':[sys.executable,str(Path(__file__).resolve()),
            'run-group','--input',str(path),'--output','{attempt_dir}/result.json'],
            'outputs':['result.json'],'cwd':str(LANE),'memory_mb':384,'timeout_s':1800})
    metadata = {'case_count':len(cases),'group_size':args.group_size,'nsteps':args.nsteps,
        'alpha_m_abs_max':max(abs(x['alpha_m']) for x in seeds),
        'alpha_r_abs_max':max(abs(x['alpha_r']) for x in seeds),
        'nominal_cancellation_cases':sum(c['nominal_cancellation'] for c in cases)}
    write_json(out/'manifest.json',{'schema':'rei.shared_case_science.v1',
        'science_binding':binding,'bound_files':bound,'jobs':jobs,'toolchain':toolchain,
        'split_pilot':metadata},immutable=True)
    print(json.dumps({'manifest':str(out/'manifest.json'),'jobs':len(jobs),**metadata}))


def run_group(args):
    data = json.loads(Path(args.input).read_text())
    if data['schema'] != 'rei.sigma_pi_split.group_input.v1' or data['owner_ref'] != OWNER_REF:
        raise ValueError('SPLIT_GROUP_SCHEMA_OR_OWNER')
    for item in data['bound_files']:
        if digest(item['path']) != item['sha256']:
            raise ValueError(f"BOUND_INPUT_BYTE_IDENTITY_MISMATCH: {item['path']}")
    import numpy, scipy
    actual = {'python':platform.python_version(),'numpy':numpy.__version__,'scipy':scipy.__version__}
    if actual != data['toolchain']:
        raise ValueError(f'TOOLCHAIN_MISMATCH {actual}')
    context = PreparedContext()
    result = {'schema':'rei.sigma_pi_split.group_result.v1',
        'science_binding':data['science_binding'],'owner_ref':OWNER_REF,
        'nsteps':data['nsteps'],'cases':[]}
    output = Path(args.output)
    active_case = None
    try:
        for active_case in data['cases']:
            result['cases'].append(run_case(active_case,context,data['nsteps']))
            write_json(output.with_name(output.stem+'.checkpoint.json'),result)
        result['status'] = 'SUCCEEDED'
        write_json(output,result)
    except Exception:
        write_json(output.with_name(output.stem+'.failure.json'),
            {'status':'FAILED','case':active_case,'traceback':traceback.format_exc(),
             'completed_cases':[c['case']['case_id'] for c in result['cases']]})
        raise


def aggregate(args):
    manifest = json.loads(Path(args.manifest).read_text())
    patterns = args.result_files or []
    paths = [Path(path) for pattern in patterns for path in glob.glob(pattern)]
    if args.scope:
        paths += prior.result_paths_from_scope(args.scope)
    if not paths:
        raise ValueError('NO_SUCCESSFUL_SPLIT_RESULT_FILES')
    found,provenance = {},[]
    for path in sorted(set(p.resolve() for p in paths)):
        data = json.loads(path.read_text())
        if (data.get('schema') != 'rei.sigma_pi_split.group_result.v1' or
            data.get('status') != 'SUCCEEDED' or data['science_binding'] != manifest['science_binding'] or
            data.get('owner_ref') != OWNER_REF or data.get('nsteps') != manifest['split_pilot']['nsteps']):
            raise ValueError(f'SPLIT_RESULT_SCHEMA_SCIENCE_OR_STATUS_MISMATCH {path}')
        provenance.append({'path':str(path),'sha256':digest(path)})
        for case in data['cases']:
            cid = case['case']['case_id']
            if cid in found and canonical(found[cid]) != canonical(case):
                raise ValueError(f'CONFLICTING_SPLIT_DUPLICATE_CASE {cid}')
            found[cid] = case
    expected = {c['case_id']:c for c in signed_grid()}
    if set(found)-set(expected):
        raise ValueError('UNEXPECTED_SPLIT_CASE_ID')
    summaries,histories = [],[]
    for cid,data in sorted(found.items()):
        if data['case'] != expected[cid] or not all(data['gates'].values()):
            raise ValueError(f'SPLIT_CASE_CONTRACT_OR_GATE_MISMATCH {cid}')
        owner_result = data['owner_result']
        if (owner_result['nsteps'] != manifest['split_pilot']['nsteps'] or
            len(owner_result['history']) != manifest['split_pilot']['nsteps'] or
            owner_result['history'][-1]['a'] != .2):
            raise ValueError(f'SPLIT_COMPLETE_HISTORY_MISMATCH {cid}')
        meta = data['case']
        final = data['owner_result']['final']
        summaries.append({**meta,'alpha_m':data['seed']['alpha_m'],'alpha_r':data['seed']['alpha_r'],
            **{f'initial_{k}':v for k,v in prior.scalar_row(data['initial']).items()},
            **{f'final_{k}':v for k,v in prior.scalar_row(final).items()},
            **data['numeric_checks'],**data['owner_result']['errors']})
        for step,row in enumerate([data['initial']]+data['owner_result']['history']):
            histories.append({**meta,'step':step,**prior.scalar_row(row)})
    out = Path(args.out)
    out.mkdir(parents=True,exist_ok=True)
    for name,rows in (('cases.csv',summaries),('history.csv',histories)):
        fields = list(dict.fromkeys(key for row in rows for key in row))
        with (out/name).open('w',newline='') as handle:
            writer = csv.DictWriter(handle,fieldnames=fields)
            writer.writeheader();writer.writerows(rows)
    missing = sorted(set(expected)-set(found))
    cancellation = [r for r in summaries if r['nominal_cancellation']]
    write_json(out/'summary.json',{'schema':'rei.sigma_pi_split.aggregate.v1',
        'status':'COMPLETE' if not missing else 'PARTIAL','case_count':len(found),
        'expected_case_count':len(expected),'missing_case_ids':missing,
        'science_binding':manifest['science_binding'],'owner_ref':OWNER_REF,
        'nsteps':manifest['split_pilot']['nsteps'],'source_grid':'8X8','L':8,
        'norm':'half_contraction','a_start':.1999,'a_end':.2,'z_start':1/.1999-1,'z_end':4.,
        'all_stored_gates_pass':True,'result_files':provenance,
        'manifest_sha256':digest(args.manifest),'nominal_cancellation_cases':len(cancellation),
        'nonzero_component_cancellation_cases':sum(r['Pi_m_half_requested']>0 for r in cancellation),
        'component_definitions':{'matter':'D_m=Pi_massive; isotropic gas/dust contribute zero anisotropic stress',
            'radiation':'D_r=Pi_gamma+Pi_nu+Pi_UV; each evaluated at the actual current state',
            'total':'D_total=D_m+D_r, then take norm; component norm sum is diagnostic only'},
        'claim':'Preliminary conditional independent matter/radiation response in warm near-z4 LRS Bianchi I; no full EoR or donor/escape Q^a closure or convergence claim.'})
    print(json.dumps({'out':str(out.resolve()),'cases':len(found),'missing':len(missing)}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command',required=True)
    p = sub.add_parser('prepare');p.add_argument('--out',required=True)
    p.add_argument('--nsteps',type=int,default=64);p.add_argument('--group-size',type=int,default=3)
    p.set_defaults(func=prepare)
    p = sub.add_parser('run-group');p.add_argument('--input',required=True);p.add_argument('--output',required=True)
    p.set_defaults(func=run_group)
    p = sub.add_parser('aggregate');p.add_argument('--manifest',required=True);p.add_argument('--scope')
    p.add_argument('--result-files',nargs='+');p.add_argument('--out',required=True);p.set_defaults(func=aggregate)
    args = parser.parse_args();args.func(args)


if __name__ == '__main__':
    main()

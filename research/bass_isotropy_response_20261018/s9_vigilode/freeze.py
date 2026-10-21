#!/usr/bin/env python3
"""Freeze the bounded S9 experiment before publication and any campaign run."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent

def main():
    source_paths=['Cargo.toml','Cargo.lock','src/lib.rs','src/main.rs','tests/adapter_contracts.rs',
        'prepare.py','prepare_input.py','analyze.py','campaign.py','build_binding.py','test_runner_guards.py',
        'freeze.py','VIGILODE_SOURCE.json']
    digest=lambda p:hashlib.sha256((HERE/p).read_bytes()).hexdigest()
    cases=[]
    for arm in ['mf_into_ls','small_clock4']:
        for level,rtol in enumerate([1e-8,1e-10,1e-12]):
            cases.append({'name':f'closed_{arm}_r{level}','model':'S8_closed_donor',
                'claim_role':'primary_fine' if level==2 else 'tolerance_diagnostic',
                'solver':{'arm':arm,'rtol':rtol,'atol':rtol/100,'initial_step':1e-3,
                    'max_step':0.04,'max_attempts':100000,'linear_rtol':1e-13,'linear_atol':1e-15}})
        cases.append({'name':f'flrw_{arm}_fine','model':'analytic_FLRW','claim_role':'analytic_control',
            'solver':{'arm':arm,'rtol':1e-12,'atol':1e-14,'initial_step':1e-3,
                'max_step':0.04,'max_attempts':100000,'linear_rtol':1e-13,'linear_atol':1e-15}})
    prereg={'schema':'BASS_S9_VIGILODE_PREREGISTRATION_V1',
        'question':'Can actual pinned VigilODE integrate the closed manufactured donor with immutable birth memory, analytic JVP/Ft, and exact event restarts while preserving the S8 contracts?',
        'state':['h=H/Hstar','b','y=s/Hstar'],'metric_signature':'(-,+,+,+)',
        'a_perp':'a exp(-b)','a_parallel':'a exp(2b)','Sigma':'sqrt(3)*abs(y)/h',
        'source_sha256':{p:digest(p) for p in source_paths},
        'input_sha256':{p:digest(p) for p in ['inputs/base.json','reference/S8_PRIMAL.json','INPUT_PROVENANCE.json']},
        'unchanged_balance_owner_sha256':hashlib.sha256((HERE.parent/'balance_p24.rs').read_bytes()).hexdigest(),
        'vigilode_source':'a21d573980f66fe02891bd216153443b5352f921',
        'vigilode_publication':'ac1cd2a4738c2441c92e5fdae5f70aba35e53544',
        'fixed_spectral_owner':'0e25846433170d0f420c4cda44a0bedbf02cd177',
        'S8_primary_source':'4508e5de9a9f2c5ad1fc7c9a9f53983305e8f613',
        'S8_resume_source':'2e6b4a150559b0bea52938896a901f6d438f3582',
        'cases':cases,'integration_count':len(cases),
        'reference_policy':'Reuse the existing 153 S8 primal rows; no S8 ODE rerun and no reference birth b(u) in solver inputs.',
        'event_policy':'Land exactly on every fixed birth x, transfer positive donor energy with continuous h,b,y, append newly admitted isotropic cohort, restart a fresh driver/workspace and immutable bank.',
        'angular_policy':{'new_birth_mode':'P24','nodes':16,'projection_internal_tol':1e-15,
            'moment_gate_exact':'3/1000000000000000','reflection_abs':0,
            'grid':'Original NumPy leggauss coordinate nodes/weights; b(u) computed by the native primary state',
            'angular_refinement':False,'new_moment_constraint_change':False,
            'scope':'The prior P24 admission algorithm is reused. This S9 matrix isolates the ODE adapter and event cache contract.'},
        'linear_policy':'Actual Gmres into least-squares workspace, restart8/maxiter40; analytic JVP and explicit analytic partial_t; no mass, no preconditioner, no inner-forcing path.',
        'small_policy':'Actual SmallProblem<4> uses autonomous [h,b,y,x], xprime=1, analytic 4x4 Jacobian with Ft as column4; default fixed-size direct solver.',
        'gates':{'hamiltonian_relative':1e-11,'cohort_energy_relative':1e-11,
            'event_energy_relative':1e-13,'donor_endpoint_relative':3e-14,
            'fine_reference_abs':1e-9,'clock_abs':1e-12},
        'gate_reasoning':{'conservation':'Preserve the established S7/S8 Hamiltonian, cohort-energy, event-energy and donor gates unchanged.',
            'fine_reference_abs':'A predeclared absolute 1e-9 bound on h,b,y for the fine bootstrap client comparison; this is a numerical comparison against an existing numerical reference, not a rigorous solution enclosure.',
            'refinement':'All three tolerances are retained. Output clipping can produce an error floor, so no fabricated power-law or timing superiority is required.',
            'clock_abs':'The exact auxiliary solution is x itself; compare the evolved clock at every requested point.'},
        'negative_development_controls':['invalid/negative exact-moment input','positive but non-P24 support',
            'reflection perturbation and immutable hash change','zero/nonfinite background','nonzero donor-transfer RHS/Ft/Jacobian cache jumps',
            'independent num-dual directional JVP/Ft and omitted-Ft controls'],
        'failure_policy':'Record feasibility, unresolved geometry, angular precision, exact-admission, stock-contract, solver, timeout and input/I/O failures separately. No negative weights, relaxed tolerance, oracle birth state or silent support change.',
        'limits':{'workers':1,'additional_worker_cap':16,'ram_bytes':16*1024**3,'disk_bytes':4*1024**3,'job_seconds':1800},
        'publication_order':['source and prereg freeze','GitHub source readback','Dropbox readback','Drive readback','bounded campaign','raw results and DAG publication','dual backup readback'],
        'not_admitted':['continuum angular accuracy','native finite-bin photon/energy conservation',
            'actual REI/MD14 owner feedback','full birth-memory parameter tangent in this new native client',
            'generic continuous residual authority','dense interpolation accuracy','portable speedup claim',
            'REI production','full EoR','merge'],
        'skill_policy':'User-selected physmath-research-loop policy; reuse evidence, independent theory/package review, typed gates and no automatic production expansion'}
    path=HERE/'PREREGISTRATION.json'
    path.write_text(json.dumps(prereg,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'preregistration_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                     'cases':len(cases),'new_scientific_campaign_executed':False}))

if __name__=='__main__':main()

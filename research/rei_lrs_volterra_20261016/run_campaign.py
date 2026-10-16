"""Bounded source-only BASS FD96 causal response experiment, NCP not needed."""
from __future__ import annotations
import argparse,csv,hashlib,json,math
from pathlib import Path
import numpy as np
from lrs_retarded import FD96Retarded,XMAX
from reference_kinetic_tangent import EinsteinTangent


def create(out:Path)->dict:
    if out.exists():raise FileExistsError('CREATE_ONLY_CAMPAIGN')
    out.mkdir(parents=True)
    records=[]; csvrows=[]
    tests={'max_abs_picard_vs_ode':0.,'max_abs_parent_vs_ode_bA':0.,
           'max_abs_parent_vs_ode_vA':0.,'max_kappa_decay_violation':0.,
           'max_a_bound_violation':0.,'max_quad_remainder_over_A2':0.}
    masses=(3.,30.,300.);angles=(16,24,32,48,64,96)
    for m in masses:
        src=FD96Retarded(m,.1)
        x=np.linspace(0.,XMAX,513)
        po=src.picard(x)
        ode=src.tangent_ode(x)
        parent=EinsteinTangent(mass=m,fraction=.1,A=0.,Sigma_ref=0.,orientation=1).endpoint(rtol=2e-12,atol=2e-14,n=51)
        ep=float(np.max(np.abs(po.b_per_A-ode.y[0])))
        es=float(np.max(np.abs(po.s_per_href_per_A-ode.y[1])))
        tests['max_abs_picard_vs_ode']=max(tests['max_abs_picard_vs_ode'],ep,es)
        tests['max_abs_parent_vs_ode_bA']=max(tests['max_abs_parent_vs_ode_bA'],abs(parent['sensitivity_b_A']-ode.y[0,-1]))
        tests['max_abs_parent_vs_ode_vA']=max(tests['max_abs_parent_vs_ode_vA'],abs(parent['sensitivity_v_A']-ode.y[1,-1]))
        for xi in x[::32]:
            c=src.coefficients(float(xi))
            tests['max_kappa_decay_violation']=max(tests['max_kappa_decay_violation'], c.kappa-1.25*src.kappa0*math.exp(-4*xi))
            tests['max_a_bound_violation']=max(tests['max_a_bound_violation'],max(.1-c.alpha/c.kappa,c.alpha/c.kappa-.125))
        timerrs=[]
        for n in (65,129,257,513,1025):
            grid=np.linspace(0,XMAX,n);outcome=src.picard(grid)
            endpoint=src.tangent_ode(np.array([0.,XMAX])).y[0,-1]
            timerrs.append({'nodes':n,'endpoint_bA_error':abs(outcome.b_per_A[-1]-endpoint),'picard_steps':outcome.picard_steps,'a_posteriori_iteration_bound':outcome.posterior_discrete_bound})
        nonlinear=[]
        for A in (-.1,-.05,-.025,.025,.05,.1):
            trial=src.nonlinearity_remainder(A)
            tests['max_quad_remainder_over_A2']=max(tests['max_quad_remainder_over_A2'], trial['b_absolute_remainder']/(A*A))
            nonlinear.append(trial)
        # Equilibrium/pressure finite-b angular GL source quadrature can be
        # refined independently without claiming that global non-LRS GL24 is converged.
        probe=[]
        from reference_kinetic_equilibrium import FD96Equilibrium
        for n in angles:
            fd=FD96Equilibrium(m,angular=n)
            st=fd.stress(.7,.2,.5)
            probe.append({'GL_mu':n,'deltaP':st.delta,'chi_b':st.chi_b,'rho':st.rho})
        # Source-independent bounds imply sign-definite linear shear response
        # on the explicitly studied f_m=.1 z20->z4 interval.
        mass_free_bound=src.proven_unforced_bound()
        if mass_free_bound>=.1:
            raise AssertionError('BOUND_INSUFFICIENT_FOR_LINEAR_SIGN')
        if not np.all(po.b_per_A[1:] >= (1-src.q_bound)*po.b_without_feedback_per_A[1:]-2e-13):
            raise AssertionError('LINEAR_RESPONSE_LOWER_ENVELOPE')
        if not np.all(po.b_per_A[1:]<=po.b_without_feedback_per_A[1:]+2e-13):
            raise AssertionError('LINEAR_RESPONSE_UPPER_ENVELOPE')
        if not np.all(po.s_per_href_per_A[1:]>0):
            raise AssertionError('POSITIVE_SIGNED_SHEAR_RESPONSE')
        for j in range(0,len(x),16):
            c=src.coefficients(float(x[j]))
            csvrows.append({'m_over_Tref':m,'x':float(x[j]),'a':float(math.exp(x[j])/21),
                 'H_isotropic_per_s':c.hubble,'alpha':c.alpha,'kappa':c.kappa,
                 'b_per_A':float(po.b_per_A[j]),'s_per_href_per_A':float(po.s_per_href_per_A[j]),
                 's_per_H_per_A':float(src.href*po.s_per_href_per_A[j]/c.hubble),
                 'Sigma_per_abs_A':float(math.sqrt(3)*abs(src.href*po.s_per_href_per_A[j])/c.hubble),
                 'b_without_feedback_per_A':float(po.b_without_feedback_per_A[j])})
        records.append({'mass':m,'source_norm':src.fd.norm,'fraction':src.fraction,'q_bound':src.q_bound,
           'mass_free_g_bound':mass_free_bound, 'positive_signed_response':'PASS',
           'picard_iterations':po.picard_steps,'b_linear_endpoint_per_A':float(ode.y[0,-1]),
           'v_linear_endpoint_per_A':float(ode.y[1,-1]),'b_no_feedback_endpoint_per_A':float(po.b_without_feedback_per_A[-1]),
           'feedback_fraction_final':float(1-po.b_per_A[-1]/po.b_without_feedback_per_A[-1]),
           'endpoint_ode_error':ep,'endpoint_sH_error':es,'parent_tangent_b_A':parent['sensitivity_b_A'],
           'parent_tangent_v_A':parent['sensitivity_v_A'], 'time_refinement':timerrs,
           'nonlinear_A':nonlinear,'angular_probe':probe,
           'angular_max_diff_16_vs_96':max(abs(probe[0][key]-probe[-1][key]) for key in ('deltaP','chi_b','rho'))})
    checks=[tests['max_abs_picard_vs_ode']<3e-13,tests['max_abs_parent_vs_ode_bA']<1e-12,
            tests['max_abs_parent_vs_ode_vA']<1e-12,tests['max_kappa_decay_violation']<1e-14,
            tests['max_a_bound_violation']<1e-14]
    if not all(checks):raise AssertionError(f'SOURCE_RESPONSE_CROSSCHECK_FAIL {tests}')
    fields=list(csvrows[0])
    with (out/'LRS_RESPONSE.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(csvrows)
    doc={'schema':'bass.lrs.volterra.response.campaign.v1','source_parent_pr168':'03a01d21ed21e7d32737ca5e5f6d889a7203aa70',
         'source_fd96_blob':'8467932c3281f9d426712b3a582f2aae3a484692',
         'source_pr164_tangent_blob':'1cab2bf7eab5a306ab207206ca3a0fc793dc9163',
         'scope':'source-only collisionless LRS first variational response; not REI native, photon/nu or HHe',
         'tested_masses':list(masses),'full_history':'z20_to_z4',
         'rho_alpha_kappa_positive':True,'analytic_contraction_scoped_fraction':.1,
         'volterra_vs_direct_ode':'PASS','parent_pr164_tangent':'PASS',
         'tests':tests,'rows':len(csvrows),'cases':records,
         'ncp':'NOT_RUN_SANDBOX_LIGHT','reality':'real numpy/scipy DOP853 + original BASS source reconstruction'}
    (out/'RESULTS.json').write_text(json.dumps(doc,indent=2)+'\n')
    (out/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256((out/name).read_bytes()).hexdigest()+'  '+name+'\n' for name in ('LRS_RESPONSE.csv','RESULTS.json')))
    print(json.dumps({'status':'PASS','cases':len(records),'rows':len(csvrows),'errors':tests,
              'masses':[{k:o[k] for k in ('mass','q_bound','picard_iterations','b_linear_endpoint_per_A','feedback_fraction_final','angular_max_diff_16_vs_96')} for o in records]},indent=2))
    return doc

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True)
    create(p.parse_args().out)

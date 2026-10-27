"""Sole production entry point for the frozen endpoint-channel transaction."""
import hashlib,json,platform,sys,traceback
from datetime import datetime,timezone
from mp_b import *
from unit_inputs import load
from endpoint_maps import prepare
from native_clock import NativeClock
from variable_operator import VariableOperator
from finite_solver import finite_endpoints,all_moments
from owners_endpoint import assemble_owners
from core_bridge_endpoint import consume
from controls_endpoint import analytic_control
from certified_quad import CERTIFICATES

RESULT=ROOT/'results';RESULT.mkdir(exist_ok=True)
state=dict(schema='BASS_ENDPOINT_CHANNEL_RESULT_V1',status='STARTED',new_B3i_rhs_invocations=0,
    requested_executor_model='gpt-6.1-sol',observed_executor_runtime_model=None,
    original_DAG=dict(completed=28,total=88,delta=0),old_source_runs_replayed=0,old_tests_consume_plot_reruns=0,
    numerical_bound_qualification='analytic truncation plus declared MP arithmetic allowance, conditional on admitted saved input values',
    physical_radii=dict(eS=None,en=None,eE=None,geometry=None,temporal=None,total=None),global_radius=None,L4=False)

def save(stage,updates=None):
    if updates:state.update(updates)
    state['last_stage']=stage;state['checks']=CHECKS;state['quadrature_and_analytic_bounds']=CERTIFICATES
    write(RESULT/'ENDPOINT_PARTIAL.json',state)
    print('SAVED '+stage,flush=True)


def parity(data,maps):
    op=data['ops'][1];diag=maps['right_source_diagnostics'];R=diag['Ralpha0'];g=op['x1s'];TR=op['TR'];c=data['constants']
    M=maps['M1'].copy();M[1,1]+=R
    nativeM=mp.matrix(op['M']);matrix_errors=[[abs(M[i,j]-nativeM[i,j])/max(abs(M[i,j]),abs(nativeM[i,j]),m('1e-100')) for j in range(2)] for i in range(2)]
    # Native s_eff is in departure variables. Add its saved absolute
    # Wiener shift and the independently reconstructed diffusion correction.
    # Explicit elimination of the stored absolute virtual source uses the
    # independently native full virtual matrix, not the new positive source.
    lower=op['Tvv'][1];upper=op['Tvv'][2]
    # Sparse solve retains the actual source diagonal and neighbor entries.
    rhs=[[op['absolute_source_virtual'][i]+diag['diffusion_only_d_virtual'][i]] for i in range(311)]
    av,_=thomas(op['Tvv'][0],lower,upper,rhs)
    b_abs=mp.matrix(op['absolute_source_real'])+mp.matrix(diag['diffusion_only_d_real'])-mp.matrix(op['Trv'])*mp.matrix([x[0] for x in av])
    bnew=maps['b1'].copy();bnew[1]+=3*R*g*(data['source_packet']['knots'][1]['incoming_lyman_alpha_beta'][0]+mp.exp(-c['E21']/TR))
    source_errors=[abs(bnew[i]-b_abs[i])/max(abs(bnew[i]),abs(b_abs[i]),m('1e-100')) for i in range(2)]
    check('right source operator parity with stored native reduction',max(x for row in matrix_errors for x in row)<=m('5e-11'),matrix_errors,m('5e-11'))
    check('right absolute diffusion-completed source parity',max(source_errors)<=m('5e-11'),source_errors,m('5e-11'))
    check('right native virtual absolute shift parity',max(diag['absolute_positive_source_vs_native_shift_relative'])<=m('5e-11'),max(diag['absolute_positive_source_vs_native_shift_relative']),m('5e-11'))
    # Reassemble V(a+Bp)=S+emission*p to check every affine coefficient.
    defects=[]
    for i in range(311):
        for j in range(3):
            vals=diag['virtual_a'] if j==0 else [row[j-1] for row in diag['virtual_B']]
            actual=diag['virtual_diag'][i]*vals[i]+(diag['virtual_lower'][i]*vals[i-1] if i else 0)+(diag['virtual_upper'][i]*vals[i+1] if i<310 else 0)
            if j==0:expected=diag['virtual_source'][i]
            else:
                expected=-op['two_photon_pre_diffusion_Tvr'][j-1][i]
                if j==2 and i==139:expected+=op['A2p_dn']
                if j==2 and i==140:expected+=op['A2p_up']
            gross=abs(diag['virtual_diag'][i]*vals[i])+(abs(diag['virtual_lower'][i]*vals[i-1]) if i else 0)+(abs(diag['virtual_upper'][i]*vals[i+1]) if i<310 else 0)+abs(expected)
            defects.append(abs(actual-expected)/gross if gross else abs(actual-expected))
    check('right all virtual affine identities from positive eliminated maps',max(defects)<=ARITH,max(defects),ARITH)
    return dict(matrix_entry_relative=matrix_errors,absolute_source_entry_relative=source_errors,virtual_affine_max_gross_relative=max(defects),native_Ralpha_rounding_relative=diag['Ralpha_relative_difference'],tolerance=m('5e-11'))


def main():
    save('entered')
    data=load();save('saved_inputs_loaded',dict(source_identities=data['original_source_hashes']))
    maps=prepare(data);save('right_maps_constructed',dict(endpoint_maps=maps))
    state['endpoint_source_parity']=parity(data,maps);save('source_parity_passed')
    state['analytic_control']=analytic_control();save('new_analytic_control_passed')
    clock=NativeClock(data);state['clock']=clock.report()
    check('new normalized proper clock exact model endpoints',clock.theta(m(0))==(m(0),m(0)) and clock.theta(clock.h)==(m(1),m(0)))
    check('new proper clock bounded and positive',clock.T>clock.T_error,dict(T=clock.T,T_error=clock.T_error))
    save('new_native_clock_bounded')
    model=VariableOperator(clock,maps,data)
    fin=finite_endpoints(model,lambda x:save('endpoint_progress',dict(finite_solution_progress=x)))
    fin.update(h=clock.h,NH_reference=clock.NH,T_new=clock.T,T_error=clock.T_error,right_H_s_inv=clock.H(clock.h),
      Nin_saved=m(data['tube']['independent_reference']['N_in_m3']),Uin_saved=m(data['tube']['independent_reference']['U0_J_m3']))
    save('q2_endpoints_passed',dict(finite_solution=fin))
    fin['moments'],fin['direct_alpha']=all_moments(model,fin,lambda x:save('moment_progress',dict(moment_progress=x)))
    save('m3_shared_moments_bounded')
    owner=assemble_owners(data,maps,fin);save('finite_tagged_owners_passed',dict(finite_owners=owner))
    old=data['prior']['finite_owners'];qss=data['prior']['baseline_correction']
    state['baseline_differences']=dict(kind='selected finite-model differences; not old quadrature error or physical radii',
      new_minus_frozen_left_Nout=owner['Nout_new']-m(old['Nout_new']),new_minus_frozen_left_Uout0=owner['Uout0_new']-m(old['Uout0_new']),
      new_minus_QSS_Nout=owner['Nout_new']-m(qss['old_reference_Nout']),new_minus_QSS_Uout0=owner['Uout0_new']-m(qss['old_reference_Uout0']))
    save('all_transaction_checks_before_rhs_passed')
    state['core_consumption']=consume(data,fin,owner,state)
    state['software']=dict(python=sys.version,mpmath=mp.__version__,platform=platform.platform())
    state['status']='PASS_CONDITIONAL_NUMERICAL_TRANSACTION_PENDING_ROOT_ADMISSION';save('completed')
    write(RESULT/'ENDPOINT_RESULT.json',state)

if __name__=='__main__':
    try:main()
    except BaseException as exc:
        state['status']='FAILED_STOPPED_NO_AUTOMATIC_RETRY';state['failure']=dict(type=type(exc).__name__,message=str(exc),traceback=traceback.format_exc());save('failed')
        write(RESULT/'ENDPOINT_FAILURE.json',state);traceback.print_exc();sys.exit(1)

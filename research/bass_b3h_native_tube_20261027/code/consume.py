"""One selected finite input consumption; refuses atomic transaction."""
import hashlib
import json
import math
from pathlib import Path
import numpy as np
from tube import ROOT, C_SI, load, require_atomic_interval
from reference import evaluate


def main():
    t=load(); result=t.integrate(); reference=evaluate(t.packet)
    errors={key:(result[key]-float(reference[key]))/float(reference[key]) for key in ['N_in_m3','U0_J_m3','proper_duration_s']}
    if max(map(abs,errors.values())) > 2e-11:
        raise ArithmeticError('selected input number/energy/duration reference tolerance failed')
    N,U=result['N_in_m3'],result['U0_J_m3']
    trans=t.transport(N,U)
    if max(abs(trans[k]) for k in ['number_relative_residual','energy_relative_residual'])>2e-13:
        raise ArithmeticError('transport tolerance failed')
    T=np.diag([U,U/3,U/3,U/3]); T1=np.diag([trans['U1_J_m3']]+[trans['U1_J_m3']/3]*3)
    snapshot=t.packet['single_snapshot_only']; snap_eta=-math.log1p(snapshot['z']['value'])
    snap_H=t.H(snap_eta); snap_n=t.nH(snap_eta)
    snapshot_residuals={'H_relative':(snap_H-snapshot['H_sInv']['value'])/snapshot['H_sInv']['value'],
      'nH_relative':(snap_n-1e6*snapshot['nH_cm3']['value'])/(1e6*snapshot['nH_cm3']['value'])}
    if max(map(abs,snapshot_residuals.values()))>2e-11:
        raise ArithmeticError('native source snapshot normalization tolerance failed')
    try: require_atomic_interval(None)
    except ValueError as exc: atomic_refusal=str(exc)
    else: raise ArithmeticError('missing atomic packet accepted')
    lower=min(s['physical_trace_lower_bound'] for s in result['segments'])
    if lower<0 or result['capacity_mu_m3']<=0 or result['crossing_redshift_work_J_m3']<=0:
        raise ArithmeticError('capacity/positivity acceptance failed')
    out=dict(schema='BASS_B3H_NATIVE_INCOMING_TUBE_RESULT_V1',status='PARTIAL_NATIVE_FINITE_PHOTON_TUBE_ATOMIC_INPUT_OPEN',
      input_sha256=hashlib.sha256((ROOT/'inputs/FINITE_TUBE_INPUT_SLICE.json').read_bytes()).hexdigest(),
      source=t.packet['source'],reference_override=dict(original_metadata=t.packet['selection']['reference'],
      actual='left endpoint eta_ref=exact eta0+5126*h; primary rounded only after local coordinate construction',authorized_by='controller frozen contract'),
      native_clock=dict(cell_indices=t.packet['selection']['cell_indices'],eta_ref_primary=t.eta_ref,delta_eta=t.h,lag_primary=t.lag,
        shifted_knots_local_u=t.knots,strict_past=True,lag_minus_native_cell_width=t.causal_margin_lower_bound,
        strict_past_certificate='each right interpolation sample is at most one h later than query; lag-h>0; per-segment margin also checked',latest_needed_source_index=max(t.packet['incoming']['source_indices']),
        right_endpoint_accepted_prefix_count=t.packet['selection']['accepted_count_at_right_endpoint']),
      representation=dict(frame='scalar FLRW isotropic rest frame q=1',signature='(-,+,+,+)',x0='ct',c_m_s=C_SI,
        G_m3=t.G,E21_eV=t.E,E21_J=t.E_J,J_volume='exp(3*u)',energy_pullback='E0=E21_J*exp(u)',
        incoming_shell_E0_J=[t.E_J,t.E_J*math.exp(t.h)],shell_origin='pullback of native line-crossing capacity',
        dN_dE0='G*exp(3*u)*f_in(u)/E0; u=log(E0/E21_J)',angular_measure='dOmega/(4*pi)'),
      primary=result,independent_reference=reference,signed_primary_reference_relative=errors,
      T0_J_m3=T.tolist(),T1_J_m3=T1.tolist(),vector_flux0_J_m2_s=[0.,0.,0.],transport=trans,
      crossing_line_energy_J_m3=t.E_J*N,crossing_work_subtraction_check_J_m3=U-t.E_J*N,
      nH_reference_m3=t.nH(t.eta_ref),nH_reference_role='normalization only; not an atomic level stock',
      source_snapshot_check=dict(eta_from_actual_snapshot_z=snap_eta,H_reconstructed_s_inv=snap_H,nH_reconstructed_m3=snap_n,
        signed_relative_residuals=snapshot_residuals),
      physical_radii=dict(eS=None,en=None,eE=None,geometry=None,temporal=None,total=None),
      conditional_transaction=dict(status='NOT_RUN_INPUT_DEPENDENT',atomic_packet=None,refusal=atomic_refusal,
        native_direct_pair_recoil_heat_ionization_eV=[0.,0.,0.],zero_owner_note='bound source direct-pair convention; does not supply atomic interval stocks',
        needed=['x1s(eta)','xr_p(eta)','opacity/tau(eta)','actual atom level stocks and QSS refill history','matching atomic stock/refill energy bookkeeping under source-owned zero direct-pair recoil convention'],
        hypothetical='D_up=integral A*f_in*dmu, D_down=integral A*f_s*dmu; 0<=A<=1 implies D_up<=N_in only',
        actual_upward_debit=None,actual_downward_debit=None,atomic_kick=None,B3i_RHS=None),
      acceptance=dict(primary_reference_N_U_duration_limit=2e-11,transport_limit=2e-13,positive_capacity=True,
        physical_trace_lower_bound=lower,numerical_representation_checks_pass=True,physical_accuracy_certified=False),
      provenance=dict(requested_implementation_model='gpt-6.1-sol',observed_runtime_model=None))
    (ROOT/'results/TUBE_RESULT.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
    rows=[]
    for u in sorted(set(np.linspace(0,t.h,129).tolist()+t.edges)):
        f=t.departure(u)+t.wien(u)
        rows.append([u,t.departure(u),t.wien(u),f,math.exp(3*u),math.exp(4*u),t.E_J*math.exp(u)])
    np.savetxt(ROOT/'results/TUBE_TRACE.csv',rows,delimiter=',',header='u,departure,wien,f_in,J_volume,energy_weight,E0_J',comments='')
    print(json.dumps(dict(status=out['status'],N_in_m3=N,U0_J_m3=U,signed_reference_relative=errors,transport_residuals=[trans['number_relative_residual'],trans['energy_relative_residual']]),indent=2))


if __name__=='__main__': main()

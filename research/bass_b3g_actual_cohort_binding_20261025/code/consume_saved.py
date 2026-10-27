"""Single frozen saved-input postprocessor. No integration or owner re-query."""
import csv
import hashlib
import numpy as np
from binding import ROOT,read_json,verify_inputs,reused_modules,bind_birth,write_json
from geometry import endpoint_bridge
from readiness import native_source_binding
from transport import diagonal_records,determinant_bound


def main():
    manifest=verify_inputs(); finite,core=reused_modules()
    results=ROOT/'results'; results.mkdir(exist_ok=True)
    validation=read_json('inputs/b3c/raw/VALIDATION.json')
    fixtures={r['name']:r for r in validation['fixtures']}
    births=[]; endpoints=[]
    for label in ('ISO','ANISO'):
        fixture=fixtures[label]
        rel=f'inputs/b3c/raw/{label}_N256_SOURCE_HISTORY.json'
        snapshot=dict(path=rel,sha256=hashlib.sha256((ROOT/rel).read_bytes()).hexdigest(),
            archive_sha256='0d3a911d7fc1b567c0e915cd655af94bff44495849bd0e7ce1bcb778a94bd1b2')
        source=read_json(rel); path=read_json(f'inputs/b3c/raw/{label}_N256_PATH.json')
        if len(source)!=256 or len(path)!=257: raise ValueError('frozen saved input row counts')
        for receipt in source:
            row=bind_birth(receipt,fixture,snapshot,finite); row['fixture']=label; births.append(row)
        for i,ep in enumerate(path):
            row=endpoint_bridge(ep,fixture,core,evaluate_rhs=i in (0,len(path)-1))
            row['fixture']=label; row['endpoint_index']=i; endpoints.append(row)
    native_root='inputs/rec_native/research/rec_line_native_owner_20261023'
    native=native_source_binding(read_json(native_root+'/inputs/STORED_NATIVE_LYA_STATE.json'),
        read_json(native_root+'/provenance/SOURCE_PARTITION_FACTS.json'),read_json('inputs/rec_history/HISTORY_ADMISSION.json'))
    transport=dict(schema='G1C_CONDITIONAL_TRANSPORT_V1',
        actual_final_cohort_R=None,status='INPUT_DEPENDENT',
        missing_fields=['midpoint_beta_birth','midpoint_beta_interpolation_error_bound'],
        alpha_birth_status='NOMINAL_LOG_DENSITY_RECONSTRUCTION_NOT_ORIGINAL_ALPHA_BYTES',
        alpha_birth_numerical_error_bound=None,
        supplied_diagonal_example=None,
        birth_identity=diagonal_records(np.zeros(3),physical=np.zeros(3),numerical=np.zeros(3),
            provenance='BIRTH_IDENTITY_SAME_EVENT_AND_FRAME; numerical identity construction exact'),
        final_determinant_physical_radius=None,
        duhamel_status='NO_INTERVAL_WIDE_PHYSICAL_ETA_OR_NUMERICAL_DEFECT_ENVELOPES_SUPPLIED',
        Ahat_definition='EXACT_MATHEMATICAL_NOMINAL_FIELD; coefficient reconstruction error belongs numerical defect D',
        sample_residuals_used_as_envelopes=False)
    write_json(results/'BIRTH_ROWS.json',dict(schema='B3G_ACTUAL_BIRTH_ROWS_V1',rows=births))
    columns=['fixture','transfer_id','tau_birth','proper_seconds','n_b_m3','E_b_J','energy_J_m3','pi_xx_J_m3','pi_yy_J_m3','pi_zz_J_m3','energy_residual','spatial_max_abs_residual','pi_max_abs_residual','upper_stock_residual','total_atom_stock_residual']
    with (results/'BIRTH_ROWS.csv').open('w',newline='') as out:
        writer=csv.DictWriter(out,fieldnames=columns); writer.writeheader()
        for row in births:
            writer.writerow(dict(fixture=row['fixture'],transfer_id=row['transfer_id'],tau_birth=row['tau_birth'],
                proper_seconds=row['proper_seconds'],n_b_m3=row['n_b_m3'],E_b_J=row['E_b_J'],energy_J_m3=row['T_J_m3'][0,0],
                pi_xx_J_m3=row['pi_J_m3'][0,0],pi_yy_J_m3=row['pi_J_m3'][1,1],pi_zz_J_m3=row['pi_J_m3'][2,2],
                energy_residual=row['signed_representation_residuals']['energy'],
                spatial_max_abs_residual=np.max(np.abs(row['signed_representation_residuals']['spatial'])),
                pi_max_abs_residual=np.max(np.abs(row['signed_representation_residuals']['pi'])),
                upper_stock_residual=row['signed_atom_stock_residuals']['upper_loss'],
                total_atom_stock_residual=row['signed_atom_stock_residuals']['total_atoms']))
    write_json(results/'SAVED_ENDPOINT_BRIDGE.json',dict(schema='B3I_SECTOR_ENDPOINT_BRIDGE_V1',rows=endpoints))
    write_json(results/'NATIVE_SOURCE_READINESS.json',native)
    write_json(results/'CONDITIONAL_TRANSPORT.json',transport)
    maxima=lambda fields, rows: {key:max(float(np.max(np.abs(row[key]))) for row in rows) for key in fields}
    representation={key:max(float(np.max(np.abs(row['signed_representation_residuals'][key]))) for row in births)
        for key in births[0]['signed_representation_residuals']}
    stocks={key:max(abs(row['signed_atom_stock_residuals'][key]) for row in births) for key in births[0]['signed_atom_stock_residuals']}
    rhs_rows=[r for r in endpoints if 'core_rhs_signed_residuals' in r]
    summary=dict(schema='B3G_SAVED_CONSUMER_SUMMARY_V1',status='IMPLEMENTATION_VERIFIED_SCOPED',
        source_scope=births[0]['source_model'],actual_birth_receipts=len(births),saved_geometry_endpoints=len(endpoints),
        algebraic_core_rhs_evaluations=len(rhs_rows),new_IVPs=0,new_owner_solves=0,
        birth_representation_max_abs=representation,atom_stock_max_abs=stocks,
        endpoint_max_abs=maxima(['signed_roundtrip_residual_on_sector_scale','radiation_trace_residual'],endpoints),
        core_rhs_max_abs={key:max(float(np.max(np.abs(r['core_rhs_signed_residuals'][key]))) for r in rhs_rows) for key in ['dh','dsigma','drho','dflux']},
        physical_source_energy_radius=None,physical_total_error=None,physical_target_2e8_certified=False,
        actual_final_cohort_transport='INPUT_DEPENDENT',calibrated_REC_geometry='INPUT_DEPENDENT',
        physical_finite_absorption=native['finite_donor_readiness']['physical_finite_absorption'],
        whole_BASS_physical_completion=None,L4=False,independent_scientific_review='PENDING_ROOT_DECISION',
        immutable_input_count=len(manifest['files']),historical_convergence_evidence='REUSED_UNCHANGED_B3C_AND_G1B_NO_REPLAY')
    write_json(results/'SUMMARY.json',summary)
    print('Saved 512 actual births, 514 sector geometry endpoints, 4 algebraic core RHS checks; physical claims remain conditional.')


if __name__=='__main__': main()

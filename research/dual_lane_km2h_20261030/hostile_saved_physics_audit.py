"""Independent readback arithmetic of saved KM2H actual physics, imports NO BASS RHS.

A self-hostile cross-route review of 30 full stress epochs and source table.
Not a distinct-author independent scientific implementation or interval proof.
"""
from __future__ import annotations
import argparse,json,hashlib
from pathlib import Path
import numpy as np

C=299792458.0
SIGMA_T=6.6524587051e-29
FLRW_SHA='7f2c47c70dfab95e9ababed481db2c8d78429c0402ba1a85faeccb73df14d4da'


def audit(source:Path,flrw:Path,output:Path):
    x=json.loads(source.read_text())
    if hashlib.sha256(flrw.read_bytes()).hexdigest()!=FLRW_SHA:raise ValueError('HOSTILE_FLRW_SOURCE_SHA_MISMATCH')
    tab=np.genfromtxt(flrw,delimiter=',',names=True)
    s={'n_epochs':0,'n_cases':len(x['cases']),'n_GL24_rows':0,
       'max_total_energy_stress_closure_abs':0.,'max_charge_source_abs':0.,
       'max_free_proton_electron_number_difference':0.,'max_mass_partition_abs':0.,
       'max_thomson_from_SI_rel':0.,'max_raw_thomson_force_gap_definition_abs':0.,
       'max_source_xe_linear_interpolation_abs':0.,'max_BASS_Hamiltonian_normalized':0.,
       'max_BASS_momentum_normalized':0.,'max_zeta_minus_detA_abs':0.}
    for name,k in x['cases'].items():
        assert len(k['epochs'])==5 and len(k['balances']['force_gap_time_rows'])==24
        assert len(k['dense_physical_curve_41epochs'])==41
        s['n_GL24_rows']+=24
        for row in k['epochs']:
            s['n_epochs']+=1
            rho=row['rho_total'];pg=row['rho_photon'];rb=row['total_baryon_density']
            s['max_total_energy_stress_closure_abs']=max(s['max_total_energy_stress_closure_abs'],abs(rho-pg-rb))
            s['max_charge_source_abs']=max(s['max_charge_source_abs'],abs(row['charge_C_m3']))
            s['max_free_proton_electron_number_difference']=max(s['max_free_proton_electron_number_difference'],abs(row['ne_free_rest_m3']-row['np_free_rest_m3']))
            sf=row['charged_mass_fractions_and_neutral_mass_fractions']
            s['max_mass_partition_abs']=max(s['max_mass_partition_abs'],abs(sum(sf.values())-1))
            nu_from_source=row['ne_free_rest_m3']*SIGMA_T*C*(k['Tstar_years']*365.25*86400)
            s['max_thomson_from_SI_rel']=max(s['max_thomson_from_SI_rel'],abs(nu_from_source/row['nu_rest_tstar']-1))
            f_raw=np.asarray(row['photon_raw_force'])
            f_cov=np.asarray(row['photon_covariant_force'])
            gap=np.asarray(row['photon_force_discrete_gap'])
            s['max_raw_thomson_force_gap_definition_abs']=max(s['max_raw_thomson_force_gap_definition_abs'],float(np.max(abs(f_raw-f_cov-gap))))
            source_col='xe_class_per_H' if k['source_type']=='class' else 'xe_hyrec_per_H'
            xe=np.interp(row['z_volume_proxy'],tab['z'],tab[source_col])
            if k['source_type']=='frozen_hyrec':xe=float(tab['xe_hyrec_per_H'][1199])
            s['max_source_xe_linear_interpolation_abs']=max(s['max_source_xe_linear_interpolation_abs'],abs(xe-row['xe_external_per_hydrogen']))
            s['max_BASS_Hamiltonian_normalized']=max(s['max_BASS_Hamiltonian_normalized'],abs(row['hamiltonian_normalized']))
            s['max_BASS_momentum_normalized']=max(s['max_BASS_momentum_normalized'],abs(row['momentum_constraint_normalized']))
            s['max_zeta_minus_detA_abs']=max(s['max_zeta_minus_detA_abs'],abs(row['electron_zeta']-row['detA']))
    s['GL16_external_vs_frozen_tau_mean']=x['cases']['GL16_hyrec']['ray_optical_depth_mean']-x['cases']['GL16_frozen_hyrec']['ray_optical_depth_mean']
    s['GL16_external_vs_frozen_shear_norm']=x['cases']['GL16_hyrec']['shear_source_norm']-x['cases']['GL16_frozen_hyrec']['shear_source_norm']
    s['GL16_external_vs_class_tau_mean']=x['cases']['GL16_hyrec']['ray_optical_depth_mean']-x['cases']['GL16_class']['ray_optical_depth_mean']
    s['source_exact_sha256']=hashlib.sha256(source.read_bytes()).hexdigest()
    s['flrw_exact_sha256']=hashlib.sha256(flrw.read_bytes()).hexdigest()
    s['scope']='INDEPENDENT_SAVED_DATA_ARITHMETIC_NOT_ANOTHER_EINSTEIN_PHOTON_SOLVER'
    s['full_angular_continuum_verification']='NOT_RUN'
    if not (s['n_epochs']==30 and s['n_GL24_rows']==144 and
        s['max_total_energy_stress_closure_abs']<5e-13 and
        s['max_charge_source_abs']==0 and s['max_free_proton_electron_number_difference']==0 and
        s['max_mass_partition_abs']<5e-15 and s['max_thomson_from_SI_rel']<4e-12 and
        s['max_raw_thomson_force_gap_definition_abs']<2e-12 and
        s['max_source_xe_linear_interpolation_abs']<2e-6 and
        s['max_BASS_Hamiltonian_normalized']<5e-8 and
        s['max_BASS_momentum_normalized']<5e-8 and
        s['max_zeta_minus_detA_abs']<5e-9):
        raise ArithmeticError('HOSTILE_SAVED_PHYSICS_AUDIT_FAILED '+json.dumps(s,indent=2))
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(s,indent=2,sort_keys=True)+'\n')
    print('KM2H_HOSTILE_SAVED_DATA_AUDIT_PASS',json.dumps({k:v for k,v in s.items() if k.startswith('max_') or k.startswith('n_')},sort_keys=True),flush=True)
    return s

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True)
    p.add_argument('--flrw',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    x=p.parse_args();audit(x.source,x.flrw,x.output)

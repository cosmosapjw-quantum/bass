#!/usr/bin/env python3
"""Source-qualified FLRW recombination regression; no Bianchi transfer.

Uses fresh native HYREC-2 output and CLASS native FLRW background/thermodynamics.
The CLASS HyRec2020 atom module shares scientific C source with HYREC-2, hence
this is an execution/path consistency check, not model-independent validation.
"""
from __future__ import annotations
import argparse, hashlib, json, re, sys
from pathlib import Path
import numpy as np
from scipy.integrate import cumulative_trapezoid
from scipy.interpolate import PchipInterpolator
from scipy.optimize import brentq

MPC_M = 3.0856775814913673e22
SIGMA_T = 6.6524587051e-29  # m^2
LIGHT_C = 299792458.0  # m/s
EXPECTED = {
    'HYREC-2-master.zip': 'f0b8bba1547ae9da83a0e663f57056884c689683396e1cf9a58bee1904040ac0',
    'class_public-master.zip': 'd1b2e1ce2b49de472e2cca9a327dc51c351e75bc0a2ad37d2e6538df76b289b7',
    'HYREC_native': '1ac2ddad6aa0e3c4080883c71479e2e398669468e4813075ec61bca86b7afc40',
    'CLASS_thermo': '43e38f89b97db00b9ffc65125fe8c2e2871e3ce8b6583cb4146a1636187aeb06',
    'CLASS_background': 'c1abe910f79ffc7c2b57abd545d063f6c7725b1e3267f81c9631c2e9805f76c9',
}
COLUMNS = [
    'z','xe_hyrec_per_H','xe_class_per_H','Tm_hyrec_K','Tb_class_K',
    'kappa_prime_hyrec_Mpc_inverse','kappa_prime_class_Mpc_inverse',
    'tau_hybrid_class_H_z1_anchor','tau_class',
    'g_eta_hybrid_Mpc_inverse','g_eta_class_Mpc_inverse',
    'n_e_hyrec_per_m3','Gamma_T_hyrec_per_s','Gamma_T_over_H_class'
]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def check_hash(path, expected, name):
    h=sha(path)
    if h!=expected:
        raise ValueError(f'ORIGINAL_SOURCE_BYTE_LOCK_FAILED {name} {h} != {expected}')
    return h


def build(root:Path,source_parent:Path,output:Path)->dict:
    root=Path(root);source_parent=Path(source_parent);output=Path(output)
    out_h=root/'hyrec_run/output_xe.dat'
    out_c=root/'class_run/flrw_regression_00_thermodynamics.dat'
    out_b=root/'class_run/flrw_regression_00_background.dat'
    log=root/'class_run/run_stdout.log'
    hashes={
        'HYREC_2_uploaded_source_zip_sha256':check_hash(source_parent/'HYREC-2-master.zip',EXPECTED['HYREC-2-master.zip'],'HYREC-2 ZIP'),
        'CLASS_uploaded_source_zip_sha256':check_hash(source_parent/'class_public-master.zip',EXPECTED['class_public-master.zip'],'CLASS ZIP'),
        'HYREC_native_output_sha256':check_hash(out_h,EXPECTED['HYREC_native'],'HYREC native output'),
        'CLASS_native_thermodynamics_sha256':check_hash(out_c,EXPECTED['CLASS_thermo'],'CLASS thermodynamics'),
        'CLASS_native_background_sha256':check_hash(out_b,EXPECTED['CLASS_background'],'CLASS background'),
    }
    old=source_parent/'BASS_KM2H_20261030'
    regression_references={
        'HYREC_native':old/'upstream/HYREC-2-master/output_xe.dat',
        'CLASS_thermo':old/'class_same_parameters_00_thermodynamics.dat',
        'CLASS_background':old/'class_same_parameters_00_background.dat'
    }
    source_paths={'HYREC_native':out_h,'CLASS_thermo':out_c,'CLASS_background':out_b}
    matches={name:source_paths[name].read_bytes()==p.read_bytes() for name,p in regression_references.items()}
    if not all(matches.values()): raise AssertionError('FLRW_REFERENCE_OUTPUT_BYTE_IDENTITY_FAILED')

    h=np.loadtxt(out_h);t=np.loadtxt(out_c);bg=np.loadtxt(out_b)
    if h.shape!=(8000,3) or not np.array_equal(h[:,0],np.arange(8000,0,-1)):
        raise ValueError('HYREC original native redshift grid mismatch')
    if not np.all(np.diff(t[:,1])>0) or not np.all(np.diff(bg[:,0])<0):
        raise ValueError('CLASS native background/thermal z grid not monotone')
    # CLASS native table is ascending in z; background table descending.
    bg=bg[::-1]
    z=np.arange(1,1601,dtype=float)
    ix=t[:,1]<=1750
    ib=bg[:,0]<=1750
    te=t[ix];be=bg[ib]
    xc=PchipInterpolator(te[:,1],te[:,3])(z)
    Tc=PchipInterpolator(te[:,1],te[:,7])(z)
    H=PchipInterpolator(be[:,0],be[:,3])(z)
    kp=PchipInterpolator(te[:,1],te[:,4])(z)
    transmission=PchipInterpolator(te[:,1],te[:,5])(z)
    xe=h[8000-z.astype(int),1]
    Tm=h[8000-z.astype(int),2]
    assert np.all(xc>0) and np.all(xe>0) and np.all(H>0)
    mask=(z>=300)&(z<=1500)
    rec=(z>=800)&(z<=1500)
    nh_candidates=kp/(xc*(1+z)**2*SIGMA_T*MPC_M)
    nh0=float(np.median(nh_candidates[mask]))
    nhspread=float(np.max(abs(nh_candidates[mask]/nh0-1)))
    # A 10^-8 source contract on recombination domain, not a new continuum theorem.
    if not (0.1<nh0<0.4 and nhspread<1e-8):raise AssertionError('FLRW_HYDROGEN_NUMBER_DENSITY_IDENTITY_FAILED')
    # HYREC has no z=0 in native table. Use CLASS optical depth at z=1 as
    # an EXPLICIT boundary and CLASS H(z), then integrate the HYREC opacity DIFFERENCE.
    tau_c=-np.log(transmission)
    delta_k_dz=kp/H*(xe/xc-1.)
    delta_tau=cumulative_trapezoid(delta_k_dz,z,initial=0.)
    tau_h=tau_c+delta_tau
    kh=kp*xe/xc
    gv_h=kh*np.exp(-tau_h)
    gv_c=kp*transmission
    ne=nh0*xe*(1+z)**3
    Gamma=ne*SIGMA_T*LIGHT_C
    H_per_sec=H*LIGHT_C/MPC_M
    Gamma_H=Gamma/H_per_sec
    kh_independent=ne*SIGMA_T*MPC_M/(1+z)
    residual=float(np.max(abs(kh_independent[mask]/kh[mask]-1)))
    if residual>=1e-8:raise AssertionError('FLRW_CONFORMAL_OPACITY_DIMENSIONAL_IDENTITY_FAILED')
    # Native CLASS visibility identity also checked at native (not interpolated) nodes.
    class_g_native_relative=float(np.max(abs(te[:,6]/(te[:,4]*te[:,5])-1)))
    if class_g_native_relative>1e-9:raise AssertionError('CLASS_VISIBILITY_NATIVE_IDENTITY_FAILED')
    native_log=log.read_text()
    m_rec=re.search(r'maximum of visibility function\) at z =\s*([0-9.]+)',native_log)
    m_star=re.search(r'optical depth crosses one at z_\* =\s*([0-9.]+)',native_log)
    if not (m_rec and m_star):raise ValueError('Expected official CLASS thermodynamics log missing')
    z_rec_class=float(m_rec.group(1)); z_star_class=float(m_star.group(1))
    z_star_h=float(brentq(lambda q:float(PchipInterpolator(z,tau_h)(q)-1),1000,1200))
    mask_peaks=(z>=1000)&(z<=1200)
    # This is intentionally only a unit-z gridded estimate, not CLASS native z_rec.
    z_h_peak_grid=float(z[mask_peaks][np.argmax(gv_h[mask_peaks])])

    xe_rel=xe/xc-1
    temp_abs=np.abs(Tm-Tc)
    max_rel=float(np.max(abs(xe_rel[rec])))
    max_temperature=float(np.max(temp_abs[rec]))
    tau_abs=float(np.max(abs(tau_h[rec]-tau_c[rec])))
    # Scoped regression limits, not independent theoretical error bounds.
    if not(max_rel<3e-4 and max_temperature<0.8 and tau_abs<3e-4):
        raise AssertionError('FLRW_HYREC_CLASS_EMPIRICAL_DIFFERENCE_GATE_FAILED')
    if abs(z_star_h-z_star_class)>0.1:
        raise AssertionError('FLRW_OPTICAL_DEPTH_UNITY_DIFFERENCE_GT_0.1_RED_SHIFT')
    data=np.column_stack((z,xe,xc,Tm,Tc,kh,kp,tau_h,tau_c,gv_h,gv_c,ne,Gamma,Gamma_H))
    output.mkdir(parents=True,exist_ok=True)
    out_table=output/'flrw_recombination_regression_1to1600.csv'
    np.savetxt(out_table,data,delimiter=',',header=','.join(COLUMNS),comments='',fmt='%.13e')
    snapshots=[]
    for zz in (300,500,800,900,1000,1050,1080,1089,1100,1150,1200,1300,1400,1500,1600):
        i=zz-1
        snapshots.append({'z':zz,'xe_hyrec':float(xe[i]),'xe_class':float(xc[i]),'relative_xe_diff':float(xe_rel[i]),'Tm_hyrec_K':float(Tm[i]),'Tb_class_K':float(Tc[i]),'Delta_T_K':float(Tm[i]-Tc[i]),'tau_hybrid':float(tau_h[i]),'tau_class':float(tau_c[i]),'kappa_prime_hyrec_Mpc_inverse':float(kh[i]),'kappa_prime_class_Mpc_inverse':float(kp[i]),'Gamma_over_H':float(Gamma_H[i])})
    report={
        'schema':'bass.km2h.flrw_native_dual_run_regression.v1',
        'scope':'FLRW_ONLY; no Bianchi I evolution or selfconsistent anisotropic recombination',
        'date':'2026-10-30',
        'cosmological_input':{'h':0.6735837,'T_cmb_K':2.7255,'Omega_b':0.0494142797907188,'Omega_cdm':0.2630065123740622,'Omega_cb':0.31242079216478097,'Omega_k':0,'YHe':0.245,'N_ncdm':1,'m_ncdm_eV':0.06,'Neff':3.046,'reionization':'none'},
        'output_native_byte_identity':matches,'sources_sha256':hashes,
        'flrw_table_rows':1600,'HYREC_native_rows':int(len(h)),
        'CLASS_native_thermodynamics_rows':int(len(t)),
        'CLASS_native_background_rows':int(len(bg)),
        'nH_today_from_CLASS_per_m3':nh0,'nH0_relative_identity_max_z300to1500':nhspread,
        'conformal_opacity_identity_max_z300to1500':residual,
        'CLASS_native_visibility_identity_max':class_g_native_relative,
        'xe_max_relative_diff_z800to1500':max_rel,
        'xe_max_relative_diff_at_z':int(z[rec][np.argmax(abs(xe_rel[rec]))]),
        'xe_relative_diff_z1100':float(xe_rel[1099]),
        'temperature_max_absolute_diff_K_z800to1500':max_temperature,
        'tau_max_absolute_diff_z800to1500':tau_abs,
        'CLASS_z_rec_from_native_stdout':z_rec_class,
        'CLASS_z_star_from_native_stdout':z_star_class,
        'HYREC_CLASS_H_HYBRID_z_star':z_star_h,
        'HYREC_CLASS_H_HYBRID_visibility_peak_grid_z_resolution_1':z_h_peak_grid,
        'Gamma_over_H_at_z1100':float(Gamma_H[1099]),
        'tau_hybrid_boundary':'tau_CLASS(z=1) plus integral of [kappa_CLASS_prime/H_CLASS*(xe_HYREC/xe_CLASS -1)] dz; no native HYREC FLRW optical depth direct independent',
        'HyRec2020_CLASS_HYREC2_shared_atomic_source':True,
        'cross_check_scope':'execution path/FLRW parameter matching; NOT independent atom physics',
        'tests_status':'PENDING_PYTEST','frozen_BASS_upper_DAG':'9/15','KM2':'PARTIAL',
        'production_ready':False,'merge_ready':False,'auto_next':False,
        'samples':snapshots,
    }
    (output/'flrw_regression_evidence.json').write_text(json.dumps(report,indent=2,sort_keys=True,ensure_ascii=False)+'\n')
    print(json.dumps({k:report[k] for k in ['flrw_table_rows','CLASS_z_rec_from_native_stdout','CLASS_z_star_from_native_stdout','HYREC_CLASS_H_HYBRID_z_star','xe_max_relative_diff_z800to1500','xe_relative_diff_z1100','temperature_max_absolute_diff_K_z800to1500','conformal_opacity_identity_max_z300to1500']},indent=2))
    return report


if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--regression-dir',type=Path,required=True)
    ap.add_argument('--originals-dir',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    build(args.regression_dir,args.originals_dir,args.output)

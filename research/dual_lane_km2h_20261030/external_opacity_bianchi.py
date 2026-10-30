"""KM2H: original BASS full polarized Einstein-Bianchi I with externally prescribed HYREC/CLASS xe.

This is a conditional FLRW microphysics sensitivity experiment, NOT anisotropic
recombination, not a CLASS-calibrated or observed Bianchi universe.  Original P8
collision, photon ray angular initial data, Einstein equations and gauge immutable.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from scipy.interpolate import PchipInterpolator
from numpy.polynomial.legendre import leggauss

from research.dual_lane_km2g_20261030.neutral_baryons import (
    NeutralHydrogenEinstein, verify_unchanged_physics,
    C_M_S, SIGMA_T_M2, M_E_KG, M_P_KG, G_SI, E_CHARGE_C, JULIAN_YEAR_S)
from tilted_collision import expected_fourforce
from curved_tilt import linear_collision

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
TABLE=HERE/'source_data/flrw_recombination_regression_1to1600.csv'
FLRW_SHA='7f2c47c70dfab95e9ababed481db2c8d78429c0402ba1a85faeccb73df14d4da'
PARENT_KM2G_BLOB='c5939affd04f84d8a3ec84f57fdaa92a38345fc0'
PARENT_GIT_HEAD='0815ff69fb8be7123deb04a09fc54f15fbf6edd1'
ZREF=1200.
YHE=.245
MPC_M=3.0856775814913673e22
OPACITY_MODES=('hyrec','class','frozen_hyrec')


def git_blob_sha(path:Path)->str:
    raw=path.read_bytes()
    return hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()


def exact_source_guards():
    source=verify_unchanged_physics()
    p=ROOT/'research/dual_lane_km2g_20261030/neutral_baryons.py'
    if git_blob_sha(p)!=PARENT_KM2G_BLOB:
        raise ValueError('PARENT_KM2G_BLOB_CHANGED')
    source[str(p.relative_to(ROOT))]=PARENT_KM2G_BLOB
    actual=hashlib.sha256(TABLE.read_bytes()).hexdigest()
    if actual!=FLRW_SHA:
        raise ValueError('FLRW_NATIVE_SOURCE_TABLE_SHA_CHANGED')
    source[str(TABLE.relative_to(ROOT))]=actual
    return source


class SourceLockedFLRW:
    def __init__(self):
        exact_source_guards()
        x=np.genfromtxt(TABLE,delimiter=',',names=True)
        if len(x)!=1600 or not np.array_equal(x['z'],np.arange(1,1601)):
            raise ValueError('FLRW_NATIVE_RECOMBINATION_GRID_CHANGED')
        if not np.all(np.isfinite(x.view((float,len(x.dtype.names))))):
            raise ValueError('FLRW_TABLE_NONFINITE')
        self.z=x['z'].copy()
        self.hyrec=PchipInterpolator(self.z,x['xe_hyrec_per_H'],extrapolate=False)
        self.class_xe=PchipInterpolator(self.z,x['xe_class_per_H'],extrapolate=False)
        self.Tm=PchipInterpolator(self.z,x['Tm_hyrec_K'],extrapolate=False)
        Hsi=x['Gamma_T_hyrec_per_s']/x['Gamma_T_over_H_class']
        self.H_class_SI=PchipInterpolator(self.z,Hsi,extrapolate=False)
        self.nH0_class=.18998243579319968
        self.Href=float(self.H_class_SI(ZREF))
        if not 0<self.Href<1e-12:
            raise ValueError('Original CLASS H dimensionalization not physical')
        self.sha256=FLRW_SHA

    def xe(self,z,mode):
        z=float(z)
        if not 900<=z<=1200:
            raise ValueError(f'FLRW_EXTERNAL_HISTORY_SUPPORT_900_TO_1200_EXCEEDED z={z}')
        if mode=='hyrec':value=float(self.hyrec(z))
        elif mode=='class':value=float(self.class_xe(z))
        elif mode=='frozen_hyrec':value=float(self.hyrec(ZREF))
        else:raise ValueError('Unknown FLRW opacity scenario')
        if not 0<value<1:raise ValueError('FLRW_EXTERNAL_XE_NOT_IN_POST_HELIUM_DOMAIN')
        return value


class ExternalFLRWOpacityBianchi(NeutralHydrogenEinstein):
    def __init__(self,*,ntheta=12,end=.25,opacity_mode='hyrec',tstar_years=None):
        self.external=SourceLockedFLRW()
        self.opacity_mode=opacity_mode
        if opacity_mode not in OPACITY_MODES:raise ValueError('Unsupported external opacity choice')
        # Only initial H is matched; the Bianchi universe is not CLASS.
        donor=NeutralHydrogenEinstein(ntheta=ntheta,end=end,Tstar_years=10_000_000.)
        self.reference_H_dimless=donor.H0
        matched_years=donor.H0/(self.external.Href*JULIAN_YEAR_S)
        if tstar_years is None:tstar_years=matched_years
        self.matched_tstar_years=matched_years
        super().__init__(ntheta=ntheta,end=end,Tstar_years=float(tstar_years))
        self.nu0_all_H=self.nu0
        self.xe_ref=self.external.xe(ZREF,opacity_mode)
        self.nu0=self.nu0_all_H*(1-YHE)*self.xe_ref
        self.nH_rest0=(1-YHE)*self.n_rest_initial_m3
        self.rho_rest_baryon0=self.M0*self.energy_unit_J_m3/(self.gamma0*C_M_S**2)
        self.hydrogen_mass_approx=M_P_KG+M_E_KG
        if abs(self.nH_rest0*self.hydrogen_mass_approx/((1-YHE)*self.rho_rest_baryon0)-1)>1e-13:
            raise ArithmeticError('HYDROGEN_DENSITY_CONSTRUCTION_WRONG')
        self.initial_density_mismatch_to_class=self.nH_rest0 / (self.external.nH0_class*(1+ZREF)**3)
        self.original_init_J_hash=hashlib.sha256(np.ascontiguousarray(self.j0).tobytes()).hexdigest()
        self.original_init_rays_hash=hashlib.sha256(np.ascontiguousarray(self.n0).tobytes()).hexdigest()

    def zvol(self,zeta):
        return (1+ZREF)*float(zeta)**(1/3)-1

    def fields(self,t,y,derivative=False):
        # The parent builds the original P8 polarization, original streaming,
        # normal ray geometry and Einstein stress. Override ONLY its opacity
        # and the corresponding physical collision/force, without replacing J.
        d=super().fields(t,y,derivative)
        z=self.zvol(d['zeta'])
        xe=self.external.xe(z,self.opacity_mode)
        nu=d['nu']*(xe/self.xe_ref)
        cf=expected_fourforce(d['T'],d['beta'],nu)
        d.update(nu=nu,cf=cf,zvol=z,xe_external=xe)
        if derivative:
            coll=linear_collision(d['op'],d['J'],nu)
            intensity=np.trace(coll,axis1=1,axis2=2)
            f_raw=np.r_[np.dot(d['w'],intensity),np.einsum('n,n,ni->i',d['w'],intensity,d['n'])]
            d.update(coll=coll,force_raw=f_raw)
        return d

    def measure_external(self,t,y):
        d=self.fields(float(t),y,False)
        r=self.measure(t,y)
        z=d['zvol'];xe=d['xe_external']; gamma=d['gamma'];zeta=d['zeta']
        nH=self.nH_rest0*zeta*self.gamma0/gamma
        ne=nH*xe
        direct=ne*SIGMA_T_M2*C_M_S*self.Tstar_seconds
        if abs(direct/d['nu']-1)>2e-12:
            raise ArithmeticError('DIRECT_SI_OPACITY_DOES_NOT_EQUAL_ORIGINAL_THOMSON')
        R=float(r['rho_electron']); q=np.asarray(r['q_electron']); P=np.asarray(r['P_electron'])
        fractions={
            'free_e':(1-YHE)*xe*(M_E_KG/(M_E_KG+M_P_KG)),
            'free_p':(1-YHE)*xe*(M_P_KG/(M_E_KG+M_P_KG)),
            'H_neutral':(1-YHE)*(1-xe),
            'He_neutral':YHE,
        }
        if abs(sum(fractions.values())-1)>3e-15:raise ArithmeticError('BARYON_SPECIES_MASS_PARTITION_WRONG')
        if abs(r['q_total'][0])+abs(r['q_total'][1])+abs(r['q_total'][2])>1e-5:
            raise ArithmeticError('EINSTEIN_MOMENTUM_CONSTRAINT_BROKEN')
        R_species={k:float(v*R) for k,v in fractions.items()}
        # Compute neutrality rather than assuming a zero output by construction.
        ne_free=ne
        np_free=xe*nH
        charge=E_CHARGE_C*(np_free-ne_free)
        spatial_current=charge*gamma*np.asarray(r['beta_electron'])*C_M_S
        f=np.asarray(r['photon_covariant_force'])
        # Existing bulk momentum is shared by all four species. Pair creation
        # and atom recombination are imposed as external fraction changes.
        return {**r,
            'z_volume_proxy':float(z), 'xe_external_per_hydrogen':float(xe),
            'Tm_external_K_DIAGNOSTIC_ONLY':float(self.external.Tm(z)),
            'nH_rest_m3':float(nH),'ne_free_rest_m3':float(ne),
            'np_free_rest_m3':float(np_free),'nH_neutral_rest_m3':float(nH*(1-xe)),
            'charge_C_m3':float(charge),'charged_e_p_current_A_m2':spatial_current.tolist(),
            'nu_rest_from_SI':float(direct),
            'total_baryon_density':float(R),
            'charged_mass_fractions_and_neutral_mass_fractions':fractions,
            'species_energy':R_species,
            'species_momentum':{k:(v*q).tolist() for k,v in fractions.items()},
            'species_pressure':{k:(v*P).tolist() for k,v in fractions.items()},
            'photon_anisotropic_pressure':(np.asarray(r['P_photon'])-np.eye(3)*np.trace(r['P_photon'])/3).tolist(),
            'H_BASS_over_H_FLRW_zvol':float((r['H']/self.Tstar_seconds)/self.external.H_class_SI(z)),
            'nH_BASS_over_H_FLRW':float(nH/(self.external.nH0_class*(1+z)**3)),
            'free_Thomson_force':f.tolist(),
            'mass_fraction_sum':float(sum(fractions.values())),
            'original_source_same':True,
        }


def run_science(output:Path,*,orders=(12,16),modes=OPACITY_MODES,end=.25):
    source=exact_source_guards()
    cases={}
    for n in orders:
        for mode in modes:
            model=ExternalFLRWOpacityBianchi(ntheta=n,opacity_mode=mode,end=end)
            sol=model.solve(rtol=1e-11,atol=1.5e-13)
            rows=[model.measure_external(float(t),sol.sol(float(t))) for t in np.linspace(0,end,5)]
            ctrl=model.conservation_integrals(sol,order=24)
            depth=model.optical_depth(sol,order=24)
            h=max(x['hamiltonian_normalized'] for x in rows)
            mom=max(x['momentum_constraint_normalized'] for x in rows)
            if h>=5e-8 or mom>=5e-8:
                raise ArithmeticError('ORIGINAL_EINSTEIN_CONSTRAINT_BROKEN')
            if max(abs(x['electron_number_vs_tetrad_detA_error']) for x in rows)>3e-9:
                raise ArithmeticError('COLD_BARYON_NUMBER_INVARIANT_BROKEN')
            if ctrl['Hamiltonian_source_balance_abs']>=5e-8 or ctrl['momentum_constraint_balance_max_abs']>=5e-8:
                raise ArithmeticError('FLRW_EXTERNAL_OPACITY_CONSTRAINT_PROPAGATION_FAILED')
            key=f'GL{n}_{mode}'
            dense=[]
            # Dense scientific plots from ACTUAL dense-output ODE states.
            # Do not redundantly recompute the expensive full P8 source moment
            # (which is already independently evaluated at 5 source epochs/GL24).
            for tt in np.linspace(0.,end,41):
                d=model.fields(float(tt),sol.sol(float(tt)),False)
                H=float(d['H']); zvol=d['zvol']; gamma=float(d['gamma'])
                zeta=float(d['zeta']);xe=float(d['xe_external'])
                nH=model.nH_rest0*zeta*model.gamma0/gamma
                pg=np.asarray(d['Pgamma']);pig=pg-np.eye(3)*np.trace(pg)/3
                shear=np.asarray(d['sigma'])
                src=np.linalg.norm(shear-zeta*model.sigma0)
                dense.append({
                    'u':float(tt),'z_vol':float(zvol),
                    'x_e':xe,'T_m_K_diagnostic':float(model.external.Tm(zvol)),
                    'nu_rest':float(d['nu']),'H_dimless':H,
                    'photon_rho':float(d['rho_gamma']),'baryon_rho':float(d['Re']),
                    'photon_pi_norm':float(np.linalg.norm(pig)),
                    'sourced_shear_norm':float(src),
                    'hydrogen_proper_number_m3':float(nH),
                    'free_electron_number_m3':float(nH*xe),
                    'H_BASS_over_H_CLASS':float((H/model.Tstar_seconds)/model.external.H_class_SI(zvol)),
                })
            cases[key]={
               'n_theta':n,'n_phi':2*n,'source_type':mode,
               'initial_flrw_z_ref':ZREF,'Tstar_years':model.Tstar_years,
               'Tstar_matched_years':model.matched_tstar_years,
               'flrw_xe_ref':model.xe_ref,'nu0':model.nu0,
               'ratio_nH_BASS_to_CLASS_initial':model.initial_density_mismatch_to_class,
               'H0_dimensionless':model.H0,'H0_CLASS_matched':bool(abs(model.Tstar_years-model.matched_tstar_years)/model.Tstar_years<1e-12),
               'parent_original_photon_J_hash':model.original_init_J_hash,
               'parent_original_photon_rays_hash':model.original_init_rays_hash,
               'epochs':rows,
               'dense_physical_curve_41epochs':dense,
               'balances':ctrl,
               'optical_depth_ray_list':depth.tolist(),
               'ray_optical_depth_min':float(np.min(depth)),
               'ray_optical_depth_max':float(np.max(depth)),
               'ray_optical_depth_mean':float(np.mean(depth)),
               'ray_optical_depth_quadrature_weighted_mean':float(np.average(depth,weights=model.w0)),
               'max_Hamiltonian_norm':h,'max_momentum_norm':mom,
               'shear_source_norm':ctrl['sourced_shear_difference_from_unsourced_dilution'],
               'n_fev':int(sol.nfev),
            }
            print('KM2H_BIANCHI_PHY',key,'z_end',f'{rows[-1]["z_volume_proxy"]:.9f}',
                  'xe_end',f'{rows[-1]["xe_external_per_hydrogen"]:.9g}',
                  'tau_mean',f'{np.mean(depth):.10g}',
                  'shear',f'{cases[key]["shear_source_norm"]:.12g}',
                  'ham',f'{h:.4g}','mom',f'{mom:.4g}',flush=True)
    # Reject a trivial rewrite: time-varying xe must materially change P8 photons
    # and actual sourced spacetime shear from frozen xe on identical initial data.
    g=cases['GL16_hyrec'];f=cases['GL16_frozen_hyrec'];c=cases['GL16_class']
    delta_tau=g['ray_optical_depth_mean']-f['ray_optical_depth_mean']
    delta_shear=g['shear_source_norm']-f['shear_source_norm']
    delta_photon=np.max(abs(np.asarray(g['epochs'][-1]['photon_anisotropic_pressure'])-np.asarray(f['epochs'][-1]['photon_anisotropic_pressure'])))
    if abs(delta_tau)<.05 or abs(delta_shear)<1e-6 or delta_photon<1e-6:
        raise ArithmeticError('PHYSICAL_DYNAMIC_IONIZATION_EFFECT_NOT_DEMONSTRATED')
    if abs(g['epochs'][-1]['xe_external_per_hydrogen']-g['epochs'][0]['xe_external_per_hydrogen'])<.01:
        raise ArithmeticError('RECOMBINATION_HISTORY_NOT_ACTUALLY_USED')
    if abs(c['ray_optical_depth_mean']-g['ray_optical_depth_mean'])>.05:
        raise ArithmeticError('CLASS_HYREC_SOURCE_CROSSCHECK_FAILED')
    result={
     'schema':'bass.km2h.external_flrw_opacity_Einstein_Bianchi_I.v1',
     'date':'2026-10-30','parent_PR':282,'parent_head':PARENT_GIT_HEAD,
     'scope':'EXPLORATORY_EXTERNAL_FLRW_MICROPHYSICS, not anisotropic recombination IVP or observed cosmology',
     'parent_physics_original_blobs':source,'flrw_input_sha256':FLRW_SHA,
     'FLRW_input':'real native user HYREC-2 and CLASS FLRW, 1600-row fixed table',
     'metric_signature':'(-,+,+,+)', 'Lambda':0.,
     'ionization_source_redshift':'z_vol=(1+zref)*zeta^(1/3)-1, zref=1200; proxy only',
     'electron_nH_definition':'xe=n_e_free/n_H_all, not electron/baryon fraction',
     'opacity':'nu_rest=xe(zvol)*nHrest0*zeta*gamma0/gamma*sigma_T*c*Tstar',
     'conditional_chemistry':'externally prescribed xe; no reaction-energy, atom binding, thermal pressure or independent species slip',
     'sources_mass_partition':'free e/p, neutral H, neutral He at fixed YHe=.245; shared U by assumption',
     'background_calibration':'H_BASS(0)/Tstar=H_CLASS(zref), but rho_b source mismatch explicit',
     'cases':cases,
     'physical_differences_gl16':{
        'HYREC_vs_frozen_tau_mean':float(delta_tau),
        'HYREC_vs_frozen_shear_source_norm':float(delta_shear),
        'HYREC_vs_frozen_photon_pi_max_abs':float(delta_photon),
        'HYREC_vs_CLASS_tau_mean':float(g['ray_optical_depth_mean']-c['ray_optical_depth_mean']),
     },
     'upper_dag':'9/15','km2':'PARTIAL','new_upper_completed':0,
     'production_ready':False,'merge_ready':False,'auto_next':False,
     'angular_continuum_certificate':'NOT_RUN',
     'full_Einstein_Boltzmann_recombination':'NOT_RUN',
     'different_author_independent_review':'NOT_RUN','native_subagent':'NOT_RUN',
     'observer_CMB_prediction':'NOT_CLAIMED',
    }
    output.parent.mkdir(exist_ok=True,parents=True)
    output.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n')
    return result


if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--orders',default='12,16')
    ap.add_argument('--modes',default='hyrec,class,frozen_hyrec')
    args=ap.parse_args()
    run_science(args.output,orders=tuple(int(i) for i in args.orders.split(',')),modes=tuple(args.modes.split(',')))

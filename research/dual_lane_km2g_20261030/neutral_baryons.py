"""KM2G: exactly charge-neutral Coulomb-locked e+p with source-locked polarized BASS photons.

Reuses original KM2F Einstein, KM1/2A Thomson and all original ray data.
New physics is separately resolved electron+proton stresses, non-dissipative
internal force partition, and opacity fixed by the dimensional baryon density.
No finite Coulomb slip, Maxwell evolution, recombination or thermal spectra.
"""
from __future__ import annotations
import argparse, hashlib, json, math
from pathlib import Path
import numpy as np
from numpy.polynomial.legendre import leggauss
from research.dual_lane_km2f_20261030.einstein_bianchi import EinsteinCoupledBianchi, full_source_guard

# NIST/CODATA 2022 values (central values), c and e exact in SI.
C_M_S = 299792458.0
G_SI = 6.67430e-11
SIGMA_T_M2 = 6.6524587051e-29
M_E_KG = 9.1093837139e-31
M_P_KG = 1.67262192595e-27
E_CHARGE_C = 1.602176634e-19
JULIAN_YEAR_S = 365.25*86400.0
SRC_PARENT = '29ee9114856d493dac2f5e8328c145050169c13e'
KM2F_BLOB = '457790df7aba6d82326ac6f3be5814851b970b1d'
ROOT = Path(__file__).resolve().parents[2]
PARENT = ROOT/'research/dual_lane_km2f_20261030/einstein_bianchi.py'


def git_blob_sha(path:Path)->str:
    raw=path.read_bytes()
    return hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()


def verify_unchanged_physics()->dict:
    originals=full_source_guard()
    sha=git_blob_sha(PARENT)
    if sha!=KM2F_BLOB:
        raise ValueError(f'FROZEN_KM2F_PHOTON_EINSTEIN_BLOB_MISMATCH {sha}')
    originals[str(PARENT.relative_to(ROOT))]=sha
    return originals


class NeutralHydrogenEinstein(EinsteinCoupledBianchi):
    """n_e^*=n_p^*, U_e=U_p, cold pressureless ideal Coulomb-locked hydrogen.

    All matter bulk momentum and Einstein rhs remain the *original KM2F* equations
    with total ion+electron inertia. Here ν0 is DERIVED from physical masses,
    G, σ_T, kappa, initial dimensionless energy and Tstar, not separately tuned.
    """
    def __init__(self, *, ntheta=12,end=.25,Tstar_years=10_000_000.,
                 scattering_switch=1.,inertia_ratio=3.,kappa=.003,
                 source_seed=(.3,-.4,.2)):
        self.scattering_switch=float(scattering_switch)
        if not np.isfinite(self.scattering_switch) or self.scattering_switch not in (0.0, 1.0):
            raise ValueError('Scattering cross-section switch must be exactly 0 or 1')
        # Zero is only an explicit SIGMA_T=0 negative control, not an
        # electron ionization fraction or recombination model.
        self.Tstar_years=float(Tstar_years)
        if not np.isfinite(self.Tstar_years) or not 1e3<=self.Tstar_years<=1e9:
            raise ValueError('Finite positive dimensionful Tstar range required')
        if kappa<=0:raise ValueError('Positive gravitational coupling required for dimensional normalization')
        self.Tstar_seconds=self.Tstar_years*JULIAN_YEAR_S
        self.mass_baryon=M_E_KG+M_P_KG
        self.electron_fraction=M_E_KG/self.mass_baryon
        self.proton_fraction=M_P_KG/self.mass_baryon
        verify_unchanged_physics()
        # Original photon INITIAL SOURCE and constrained initial electron beta
        # are independent of the temporary nu0 value used to construct rays.
        super().__init__(ntheta=ntheta,end=end,nu0=1.3,kappa=kappa,
                         inertia_ratio=inertia_ratio,source_seed=source_seed)
        self.energy_unit_J_m3=self.kappa*C_M_S**2/(8*math.pi*G_SI*self.Tstar_seconds**2)
        self.n_lab_initial_m3=self.M0*self.energy_unit_J_m3/(self.mass_baryon*C_M_S**2)
        self.n_rest_initial_m3=self.n_lab_initial_m3/self.gamma0
        self.rest_density_mass_kg_m3=self.n_rest_initial_m3*self.mass_baryon
        self.derived_nu0=self.n_rest_initial_m3*SIGMA_T_M2*C_M_S*self.Tstar_seconds
        self.nu0=self.derived_nu0*self.scattering_switch
        if not np.isfinite(self.nu0) or not 0<=self.nu0<=1000.:
            raise ValueError('Out-of-scope physical Thomson opacity')

    def measure_species(self,t,y):
        base=self.measure(float(t),y)
        R=base['rho_electron'];qb=np.array(base['q_electron'],float)
        Pb=np.array(base['P_electron'],float)
        fb=np.array(base['photon_covariant_force'],float)
        Ee,Ep=self.electron_fraction*R,self.proton_fraction*R
        qe,qp=self.electron_fraction*qb,self.proton_fraction*qb
        Pe,Pp=self.electron_fraction*Pb,self.proton_fraction*Pb
        # Incoming forces for species (photon receives +F_gamma).
        # Coulomb force electron +mu_p F_gamma; proton -mu_p F_gamma.
        fem_coul=self.proton_fraction*fb
        fpo_coul=-self.proton_fraction*fb
        fem_photon=-fb
        fem_net=-self.electron_fraction*fb  # Stable exact algebraic net: avoid subtracting two large 4-forces
        fpo_net=fpo_coul
        gamma=float(base['gamma_electron'])
        zeta=float(base['electron_zeta'])
        proper_ratio=zeta*self.gamma0/gamma
        ne=self.n_rest_initial_m3*proper_ratio
        np_=ne
        be=np.array(base['beta_electron'],float)
        # Proper four-current is exactly zero for equal n and U: numerical check
        # reported as independent charge and current algebra.
        charge_n=E_CHARGE_C*(np_-ne)
        current_3=E_CHARGE_C*(np_-ne)*gamma*be*C_M_S
        assert abs(charge_n)<1e-100 and not np.any(current_3)
        original_R=float(base['rho_total'])
        if np.max(np.abs(Ee+Ep-R))>1e-12 or np.max(abs(qe+qp-qb))>1e-12:
            raise ArithmeticError('Species rest-mass stress partition failed')
        if np.max(abs(fem_net+fpo_net+fb))>1e-12:
            raise ArithmeticError('Internal Coulomb transfer failed total-force balance')
        sigma=base['sigma'];H=base['H'];B=H*np.eye(3)+np.array(sigma)
        # Species equations are exact after imposing the Coulomb constraint.
        species_energy_source={
            'electron':float(-3*H*Ee-np.sum(B*Pe)+fem_net[0]),
            'proton':float(-3*H*Ep-np.sum(B*Pp)+fpo_net[0])}
        species_momentum_source={
            'electron':(-(4*H*np.eye(3)+np.array(sigma))@qe+fem_net[1:]).tolist(),
            'proton':(-(4*H*np.eye(3)+np.array(sigma))@qp+fpo_net[1:]).tolist()}
        nu_direct=ne*SIGMA_T_M2*C_M_S*self.Tstar_seconds*self.scattering_switch
        if abs(nu_direct-base['nu_rest_tstar'])>3e-12:
            raise ArithmeticError('Original Thomson ray ν differs from derived neutral electron ν')
        result={**base,
            # Parent KM2F's `rho_electron` field denotes the WHOLE dust stress
            # here; explicit aliases disambiguate the physical ion+electron sum.
            'rho_baryon_total':float(R),'q_baryon_total':qb.tolist(),
            'P_baryon_total':Pb.tolist(),
            'rho_electron_species':float(Ee),'rho_proton_species':float(Ep),
            'q_electron_species':qe.tolist(),'q_proton_species':qp.tolist(),
            'P_electron_species':Pe.tolist(),'P_proton_species':Pp.tolist(),
            'proper_n_electron_m3':float(ne),'proper_n_proton_m3':float(np_),
            'charge_density_C_m3':float(charge_n),'electric_current_Am2':current_3.tolist(),
            'n_lab_electron_m3':float(ne*gamma),'n_lab_proton_m3':float(np_*gamma),
            'Thomson_electron_rate_from_SI':float(nu_direct),
            'photon_force_on_electron':fem_photon.tolist(),
            'Coulomb_force_on_electron':fem_coul.tolist(),
            'Coulomb_force_on_proton':fpo_coul.tolist(),
            'net_force_on_electron':fem_net.tolist(),
            'net_force_on_proton':fpo_net.tolist(),
            'electron_energy_source':species_energy_source['electron'],
            'proton_energy_source':species_energy_source['proton'],
            'electron_momentum_source':species_momentum_source['electron'],
            'proton_momentum_source':species_momentum_source['proton'],
            'proton_share_of_recoil':float(self.proton_fraction),
            'electron_share_of_recoil':float(self.electron_fraction),
            'locked_pair_ideal':True,
        }
        return result

    def optical_depth(self,sol,end=None,order=24):
        horizon=self.end if end is None else float(end)
        if not 0<=horizon<=self.end:raise ValueError('Optical depth horizon beyond original geometry')
        x,w=leggauss(order)
        dt=horizon*(x+1)/2
        out=np.zeros(self.N)
        for t,weight in zip(dt,horizon*w/2):
            fields=self.fields(float(t),sol.sol(float(t)))
            out+=weight*fields['nu']*fields['op'].D
        return out


def physics_run(output:Path,*,orders=(12,16),time_scales=(10_000_000.,3_000_000.,57_883_065.06488644),
                end=.25,fast=False):
    src=verify_unchanged_physics()
    cases={}
    for Tstar in time_scales:
        for n in orders if not fast else orders[:1]:
            model=NeutralHydrogenEinstein(ntheta=n,end=end,Tstar_years=Tstar)
            sol=model.solve()
            records=[model.measure_species(float(t),sol.sol(float(t))) for t in np.linspace(0,end,5)]
            balances=model.conservation_integrals(sol,order=24)
            depth=model.optical_depth(sol)
            endp=records[-1]
            max_h=max(abs(a['hamiltonian_normalized']) for a in records)
            max_m=max(abs(a['momentum_constraint_normalized']) for a in records)
            max_charge=max(abs(a['charge_density_C_m3']) for a in records)
            max_current=max(float(np.max(np.abs(np.asarray(a['electric_current_Am2'])))) for a in records)
            if max_h>1e-7 or max_m>1e-7 or max_charge!=0 or max_current!=0:
                raise ArithmeticError('Neutral multi-species Einstein constraint not preserved')
            if balances['Hamiltonian_source_balance_abs']>2e-8 or balances['momentum_constraint_balance_max_abs']>2e-8:
                raise ArithmeticError('Species source does not preserve Bianchi I constraints')
            if max(a['nu_rest_tstar'] for a in records)<=0:
                raise ArithmeticError('Original electron Thomson opacity unexpectedly absent')
            key=f'GL{n}_TstarYears{int(Tstar)}'
            cases[key]={
                'Tstar_years':Tstar,'n_theta':n,'n_phi':2*n,'rays':model.N,
                'initial_gamma':model.gamma0,'initial_electron_beta':model.beta0.tolist(),
                'mass_ratio_proton_over_electron':M_P_KG/M_E_KG,
                'electron_mass_fraction':model.electron_fraction,
                'proton_mass_fraction':model.proton_fraction,
                'rho_unit_J_m3':model.energy_unit_J_m3,
                'n_rest_initial_per_m3':model.n_rest_initial_m3,
                'n_lab_initial_per_m3':model.n_lab_initial_m3,
                'nu0_physical_derived':model.nu0,
                'optical_depth_ray_first':float(depth[0]),
                'optical_depth_min':float(np.min(depth)),
                'optical_depth_max':float(np.max(depth)),
                'physics_epochs':records,
                'constraint_integrals':balances,
                'max_normalized_Hamiltonian':max_h,
                'max_normalized_momentum':max_m,
                'final_sourced_shear_norm':balances['sourced_shear_difference_from_unsourced_dilution'],
                'actual_baryon_beta_end':endp['beta_electron'],
                'actual_H_end':endp['H'],
                'actual_rho_gamma_end':endp['rho_photon'],
                'actual_rho_baryon_end':endp['rho_electron'],
                'original_full_photon_source_retained':True,
                'original_photon_initial_J0_sha256':hashlib.sha256(np.ascontiguousarray(model.j0).tobytes()).hexdigest(),
                'original_photon_initial_ray_sha256':hashlib.sha256(np.ascontiguousarray(model.n0).tobytes()).hexdigest(),
                'scoped_Coulomb_lock':True,
                'angular_continuum_certificate':'NOT_RUN',
            }
            print('KM2G_NEUTRAL_EINSTEIN_PHYSICS',key,
                'nu0',f'{model.nu0:.8g}','tau_minmax',f'{np.min(depth):.5g}',f'{np.max(depth):.5g}',
                'Hfin',f'{endp["H"]:.12g}','Hamiltonian',f'{max_h:.4g}',
                'Q',f'{max_m:.4g}',flush=True)
    # Contrasts across actually different physical SI time scales are not
    # approximating a single real cosmological epoch/abundance.
    overview={
        'schema':'bass.km2g.charge_neutral_baryon_polarized_Einstein_Bianchi_I.v1',
        'repo':'cosmosapjw-quantum/bass','source_base_pr278':SRC_PARENT,
        'original_source_git_blobs':src,
        'physical_units':'SI m kg s J, c present; dimensionless BASS normal u=t/Tstar',
        'constants_CODATA2022':{'electron_mass_kg':M_E_KG,'proton_mass_kg':M_P_KG,
            'Thomson_sigma_m2':SIGMA_T_M2,'speed_of_light_m_s':C_M_S,'G_m3_kg_s2':G_SI,
            'elementary_charge_C':E_CHARGE_C,'Julian_year_seconds':JULIAN_YEAR_S},
        'parent_photon_data_exact':'unchanged original KM2E normal ray source + P8 angular coherency',
        'physics':'cold exactly neutral H plasma, instantaneous ideal Coulomb momentum lock, full original P8 photon Einstein Bianchi I',
        'R_baryon_over_original_photon_rho_initial':3.,'Einstein_kappa':.003,
        'experiment_horizon_u':end,
        'species_electron_proton_mass_proper_opacity':'derived, not independently selected',
        'source_owner':'original KM2A/C/D/E and Einstein KM2F unchanged',
        'charge_neutrality':'J_em^a=0 identically under n_e=n_p and U_e=U_p',
        'species_force_sharing':'photon F_gamma, electron -mu_e F_gamma, proton -mu_p F_gamma, Coulomb e:+mu_p F_gamma p:-mu_p F_gamma',
        'cases':cases,
        'upper_dag':'9/15','km2':'PARTIAL','new_upper_completed':0,
        'production_ready':False,'merge_ready':False,'auto_next':False,
        'Einstein_full_formal_verification':'NOT_RUN',
        'photon_blackbody_and_ionization_history':'NOT_AVAILABLE_NOT_CLAIMED',
        'finite_Coulomb_rate_Maxwell':'NOT_RUN',
        'native_subagent':'NOT_RUN','distinct_author_R6_C9':'NOT_RUN',
    }
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(overview,sort_keys=True,indent=2,allow_nan=False)+'\n')
    return overview


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--orders',default='12,16')
    p.add_argument('--time-scales',default='10000000,3000000,57883065.06488644')
    a=p.parse_args()
    physics_run(a.output,orders=tuple(int(x) for x in a.orders.split(',')),
                time_scales=tuple(float(x) for x in a.time_scales.split(',')))

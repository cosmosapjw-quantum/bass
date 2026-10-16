"""BASS PR169 source-preserving Einstein history + age-dependent photon diagnostics.

Photons are test-radiation only.  The original BASS Einstein IVP includes an
isotropic Ω_r background; never add the following radiation energy or stress to
that background without replacing the corresponding stock/energy-owner.
"""
from __future__ import annotations
import csv,json,hashlib,math,sys,pathlib,argparse
import numpy as np
from born_photon_stress import BornIsotropicRadiation,XMAX,angular_f_delta
from coupled_lrs_gamma import integrate as integrate_old_gamma, gamma_contraction_bound
HERE=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(HERE/'pr169_original'))
from reference_kinetic_tangent import EinsteinTangent,AREF,OMEGA_R


def build_case(mass:float,amplitude:float,source_mode:str,*,nodes:int=65,
               n_birth:int=64,n_mu:int=64):
    if source_mode not in ('old_only','source_only','old_plus_source'):
        raise ValueError('SOURCE_CASE_UNKNOWN')
    model=EinsteinTangent(mass=float(mass),fraction=.1,A=float(amplitude),
                         Sigma_ref=0.,orientation=1)
    sol=model.solution(rtol=2e-12,atol=2e-14,n=nodes)
    if not sol.success:raise ArithmeticError('BASS_PR164_SOLUTION_FAILURE')
    def y_at(x):
        xx=np.asarray(x,dtype=float)
        return sol.sol(xx)
    def beta(x):return np.asarray(y_at(x))[0]
    def beta_prime(x):
        xx=np.atleast_1d(x)
        v=np.asarray(y_at(xx))[1]
        out=[]
        for u,vi,bi in zip(xx,v,np.asarray(beta(xx))):
            M,H,_,_=model.field(float(u),float(bi),float(vi))
            out.append(model.href*float(vi)/H)
        return np.array(out)
    source_shape=lambda x: .25*np.exp(-.8*np.asarray(x))*(1+.15*np.sin(4*np.asarray(x)))
    if source_mode=='old_only':
        source=lambda x:np.zeros_like(np.asarray(x,dtype=float))
        initial=1.0
    elif source_mode=='source_only':
        source=source_shape
        initial=0.0
    else:
        source=source_shape
        initial=1.0
    photons=BornIsotropicRadiation(beta,source,bprime=beta_prime,
                     rho_old=initial,n_birth=n_birth,n_mu=n_mu)
    xs=np.linspace(0.,XMAX,nodes)
    ode=photons.memory_ode(xs)
    rows=[]
    max_memo=0.;min_pperp=1e99;min_ppar=1e99
    for i,x in enumerate(xs):
        p=photons.point(float(x))
        M,H,_,_=model.field(float(x),float(p.b),float(np.asarray(y_at(x))[1]))
        cm=model.cm
        rad_value=OMEGA_R/AREF**4*math.exp(-4*x) # isotropic Ωr in original BASS.
        # If entire pre-existing Ωr were a collisionless OLD cohort, this is the
        # single-species anisotropic pressure in critical-density units.
        _,d_old=angular_f_delta(p.b-photons.b0,n_mu)
        gamma_old_full_rad=OMEGA_R/AREF**4*math.exp(-4*x)*d_old
        massive=cm*M.delta
        # This ratio is conditional: f_c=1 replacement of the original isotropic Ωr.
        ratio=gamma_old_full_rad/massive if abs(massive)>1e-20 else 0.0
        max_memo=max(max_memo,abs(p.isotropic_rho-ode.y[0,i]),
                     abs(p.memory_b-ode.y[1,i]))
        min_pperp=min(min_pperp,(p.rho-p.delta)/3)
        min_ppar=min(min_ppar,(p.rho+2*p.delta)/3)
        rows.append(dict(mass=mass,initial_A=amplitude,mode=source_mode,
            x=float(x),a=float(AREF*math.exp(x)),b=p.b,
            signed_s_over_H=float(np.asarray(beta_prime(np.array([x])))[0]),
            isotropic_reference_Omega_r_density=rad_value,
            photon_rho=p.rho,photon_pbar=p.rho/3.,
            photon_delta=p.delta,photon_delta_linear=p.delta_linear,
            photon_delta_quadratic=p.delta_quadratic,
            born_isotropic_rho=p.isotropic_rho,memory_b=p.memory_b,
            radiation_rho_enhancement=p.rho-p.isotropic_rho,
            massive_delta_crit_norm=massive,
            existing_Omega_r_full_free_stream_delta_crit_norm=gamma_old_full_rad,
            conditional_full_radiation_vs_massive_delta_ratio=ratio,
            source_per_x=p.source_per_x))
    ledger=photons.ledger(XMAX,n_time=64)
    delta=np.array([z['photon_delta'] for z in rows]);linear=np.array([z['photon_delta_linear'] for z in rows]);
    iso=np.array([z['born_isotropic_rho'] for z in rows]);ph=np.array([z['photon_rho'] for z in rows]);
    absrel=np.max(np.abs(delta-linear))/max(np.max(np.abs(delta)),1e-30)
    summary=dict(mass=mass,A=amplitude,mode=source_mode,source='smooth_manufactured_not_native_REI',
       final_b=rows[-1]['b'],final_signed_s_over_H=rows[-1]['signed_s_over_H'],
       final_photon_delta=rows[-1]['photon_delta'],
       final_photon_delta_linear=rows[-1]['photon_delta_linear'],
       max_abs_linear_error=float(np.max(np.abs(delta-linear))),
       max_fractional_linear_error=float(absrel),
       max_relative_rho_enhancement=float(np.max((ph-iso)/np.maximum(iso,1e-30))),
       max_memory_U_M_vs_independent_DOP853=float(max_memo),
       ledger=ledger,positive_pressures=(min_pperp>=-1e-12 and min_ppar>=-1e-12),
       min_pperp=min_pperp,min_ppar=min_ppar,
       conditional_full_old_radiation_vs_massive_delta_ratio_endpoint=rows[-1]['conditional_full_radiation_vs_massive_delta_ratio'],
       source_claim='0.25 exp(-0.8 x)(1+0.15 sin4x) per log a; not native MD14')
    return rows,summary


def refinement():
    # A genuinely nontrivial shape on a fixed manufactured geometry, isolating
    # Gaussian quadrature from the tiny-b actual BASS response and roundoff.
    b=lambda x:.28*np.sin(1.6*np.asarray(x))+.02*np.asarray(x)
    bp=lambda x:.448*np.cos(1.6*np.asarray(x))+.02
    S=lambda x:.32*(1+.22*np.cos(3.7*np.asarray(x)))
    rho0=.6;x=1.18
    ref=BornIsotropicRadiation(b,S,rho_old=rho0,n_birth=256,n_mu=256,bprime=bp).point(x)
    table=[]
    for n_age,n_angle in [(8,96),(12,96),(16,96),(24,96),(48,96),(64,8),(64,12),(64,16),(64,24),(64,32),(64,64),(128,128)]:
        p=BornIsotropicRadiation(b,S,rho_old=rho0,n_birth=n_age,n_mu=n_angle,bprime=bp).point(x)
        table.append(dict(n_age=n_age,n_mu=n_angle,
          rho_abs_err=abs(p.rho-ref.rho),delta_abs_err=abs(p.delta-ref.delta),
          F_rho=p.rho,D=p.delta))
    return {'reference':{'n_age':256,'n_mu':256,'rho':ref.rho,'delta':ref.delta},'table':table}


def run(output:pathlib.Path):
    if output.exists():raise FileExistsError('CREATE_ONLY_CAMPAIGN')
    output.mkdir(parents=True)
    rows=[];cases=[]
    for m in (3.,30.,300.):
      for A in (-.5,.5):
        for mode in ('old_only','source_only','old_plus_source'):
            rr,r=build_case(m,A,mode)
            rows.extend(rr);cases.append(r)
    with (output/'HISTORY.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    all_ledgers=max(abs(c['ledger']['energy_residual']) for c in cases)
    max_linear=max(c['max_fractional_linear_error'] for c in cases)
    max_memory=max(c['max_memory_U_M_vs_independent_DOP853'] for c in cases)
    gamma_tests=[]
    for m in (3.,30.,300.):
        independent=integrate_old_gamma(m,0.)
        response=integrate_old_gamma(m,1.)
        gamma_tests.append(dict(mass=m,reference_b_per_A=float(independent.b_per_A[-1]),
           old_full_Omega_r_b_per_A=float(response.b_per_A[-1]),
           fractional_shear_suppression=float(1-response.b_per_A[-1]/independent.b_per_A[-1]),
           proven_gamma_q_bound=response.gamma_q_bound,
           conservative_total_q_bound=response.universal_q_bound,
           note='Conditional f_gamma=1 old-photon replacement of isotropic Omega_r, not injected source or native REI'))
    data={'schema':'bass.pr170.source_age_photon_bass_history.v1',
          'parent_bass_pr169':'6fb32b51390e4f722692505bf7a3ace2448aada6',
          'parent_pr164_git_blob':'1cab2bf7eab5a306ab207206ca3a0fc793dc9163',
          'scope':'passive bolometric photons on exact BASS source-only LRS Einstein history; no gamma feedback to geometry',
          'count_cases':len(cases),'count_rows':len(rows),'tested_masses':[3,30,300],
          'tested_A':[-.5,.5],'modes':['old_only','source_only','old_plus_source'],
          'max_abs_energy_ledger':all_ledgers,
          'max_fractional_linear_stress_error':max_linear,
          'max_abs_memory_U_M_ode_difference':max_memory,
          'cases':cases,'refinement_manufactured':refinement(),
          'conditional_initial_radiation_Einstein_feedback':gamma_tests,
          'explicit_nonclaims':['actual REI spectral birth counts','any b-feedback or new Einstein solution',
                'actual anisotropic photon opacity or Thomson','full EoR','momentum Q^a gas counterpart']}
    (output/'RESULTS.json').write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')
    import hashlib
    (output/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256((output/q).read_bytes()).hexdigest()+'  '+q+'\n' for q in ('HISTORY.csv','RESULTS.json')))
    assert all(c['positive_pressures'] for c in cases)
    assert all_ledgers<2e-8 and max_memory<1e-9
    print(json.dumps({k:data[k] for k in ('count_cases','count_rows','max_abs_energy_ledger','max_fractional_linear_stress_error','max_abs_memory_U_M_ode_difference')},indent=2))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=pathlib.Path,required=True)
    run(ap.parse_args().out)

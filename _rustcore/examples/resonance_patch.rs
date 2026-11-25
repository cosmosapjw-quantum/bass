//! Local frozen material-frame resonance benchmark. No feedback on BASS
//! accepted histories, no angular transport; only conditional frequency
//! drift and conservative local scalar diffusion.
use bianchi_rustcore::homogeneous_sky::resonance::{
    self, AtomicLine, DiffusionProfile, Material, Patch, Species, H_PLANCK, KB,
};
use rec_microphysics::species_thermal::ReferenceHistory;
use std::{
    env, fs,
    io::{BufWriter, Write},
    path::Path,
};
fn run() -> Result<(), Box<dyn std::error::Error>> {
    let a: Vec<String> = env::args().skip(1).collect();
    if a.len() != 16 {
        return Err("usage: resonance_patch OUT REF|benchmark SOURCE_ETA H|He voigt|dipole uniform|stretched EXTENT INTERVALS s|eta DURATION STEPS pulse|wien|planck|bose-pulse|physical-pulse|bose-high PSCATTER DOPPLER DRIFT_FIRST DRIFT_SECOND".into());
    }
    let out = Path::new(&a[0]);
    if out.exists() {
        return Err("output directory exists".into());
    }
    let eta: f64 = a[2].parse()?;
    let species = match a[3].as_str() {
        "H" => Species::HI,
        "He" => Species::HeI,
        _ => return Err("invalid species".into()),
    };
    let p_sc: f64 = a[12].parse()?;
    let (line, m) = if a[1] == "benchmark" {
        if eta != 0. {
            return Err("benchmark source eta must be zero".into());
        }
        (
            if species == Species::HI {
                AtomicLine::hydrogen()
            } else {
                AtomicLine::helium()
            },
            Material::new(3000., 250e6, 1., p_sc)?,
        )
    } else {
        let reference = ReferenceHistory::parse(&fs::read_to_string(&a[1])?)
            .map_err(|e| format!("REC reference parse: {e:?}"))?;
        resonance::from_reference(&reference, eta, species, p_sc)?
    };
    let profile = match a[4].as_str() {
        "voigt" => DiffusionProfile::Voigt,
        "dipole" => DiffusionProfile::DipoleMoment,
        _ => return Err("invalid diffusion profile".into()),
    };
    let stretched = match a[5].as_str() {
        "uniform" => false,
        "stretched" => true,
        _ => return Err("invalid mesh".into()),
    };
    let p = Patch::with_profile(line, m, a[6].parse()?, a[7].parse()?, stretched, profile)?;
    let duration: f64 = a[9].parse()?;
    let steps: usize = a[10].parse()?;
    let d: f64 = a[13].parse()?;
    let drift: [f64; 2] = [a[14].parse()?, a[15].parse()?];
    if !duration.is_finite()
        || duration < 0.
        || steps == 0
        || steps > 100_000
        || !d.is_finite()
        || d <= 0.
        || drift.iter().any(|v| !v.is_finite())
    {
        return Err("invalid local clock".into());
    }
    if drift[0] != drift[1] && steps % 2 != 0 {
        return Err("drift switch requires even steps".into());
    }
    let seconds = match a[8].as_str() {
        "s" => duration,
        "eta" => duration * d / m.hubble_s,
        _ => return Err("clock must be s or eta".into()),
    };
    if !seconds.is_finite() {
        return Err("clock overflow".into());
    }
    let dt = seconds / steps as f64;
    let dt_eta = dt * m.hubble_s / d;
    let eps0 = H_PLANCK * p.calibration.nu0_hz / (KB * m.temperature_k);
    let bump = |x: f64| (-0.5 * ((x - 2.) / 0.4).powi(2)).exp();
    let (initial, nonlinear, normalized) = match a[11].as_str() {
        "pulse" => {
            let mut x: Vec<_> =
                p.x.iter()
                    .zip(&p.volume)
                    .map(|(&x, w)| w * bump(x))
                    .collect();
            let s = x.iter().sum::<f64>();
            if s <= 0. {
                return Err("pulse unresolved".into());
            }
            for v in &mut x {
                *v /= s;
            }
            (x, false, true)
        }
        "wien" => (p.wien((-eps0).exp())?, false, false),
        "planck" => (p.bose(0.)?, true, false),
        "bose-pulse" => (
            p.x.iter()
                .zip(&p.volume)
                .map(|(&x, w)| 0.01 * w * bump(x))
                .collect(),
            true,
            false,
        ),
        "bose-high" => (
            p.x.iter()
                .zip(&p.volume)
                .map(|(&x, w)| 0.5 * w * bump(x))
                .collect(),
            true,
            false,
        ),
        "physical-pulse" => {
            let mut q = p.bose(0.)?;
            for (x, v) in p.x.iter().zip(&mut q) {
                *v *= 1. + 0.5 * bump(*x)
            }
            (q, true, false)
        }
        _ => return Err("invalid initial state".into()),
    };
    let n0 = initial.iter().sum::<f64>();
    if n0 <= 0. || !n0.is_finite() {
        return Err("invalid initial mass".into());
    }
    let e0 = p.full_energy_j(&initial)?;
    let mut mass = initial.clone();
    let mut escape_n = 0.;
    let mut escape_e = 0.;
    let mut work = 0.;
    let mut scatter = 0.;
    let mut flux = 0.;
    let mut spread = 0.;
    let mut max_n: f64 = 0.;
    let mut max_c: f64 = 0.;
    let mut max_e: f64 = 0.;
    let mut max_bose: f64 = 0.;
    let mut max_it = 0;
    let mut hist = vec![(0., n0, e0, 0., 0., 0., 0., 0.)];
    for i in 0..steps {
        let dz = dt_eta * drift[if i < steps / 2 { 0 } else { 1 }] * 0.5;
        let apply = |mass: &[f64],
                     escape_n: &mut f64,
                     escape_e: &mut f64,
                     work: &mut f64,
                     spread: &mut f64,
                     max_n: &mut f64,
                     max_e: &mut f64|
         -> Result<Vec<f64>, String> {
            if dz == 0. {
                return Ok(mass.to_vec());
            }
            let q = p.shift_log(mass, dz)?;
            *escape_n += q.escaped_mass;
            *escape_e += q.escaped_energy_j;
            *work += q.work_j;
            *spread += q.numerical_second_detuning_moment;
            *max_n = max_n.max(q.number_defect);
            *max_e = max_e.max(q.energy_defect);
            Ok(q.mass)
        };
        mass = apply(
            &mass,
            &mut escape_n,
            &mut escape_e,
            &mut work,
            &mut spread,
            &mut max_n,
            &mut max_e,
        )?;
        let q = if nonlinear {
            let q = p.bose_step(&mass, dt)?;
            max_it = max_it.max(q.iterations);
            max_bose = max_bose.max(q.nonlinear_scaled_residual);
            q.step
        } else {
            p.be_audit(&mass, dt)?
        };
        let ns = mass.iter().sum::<f64>();
        let escale = H_PLANCK * p.calibration.doppler_width_hz;
        max_n = max_n.max(q.number_defect);
        max_c = max_c.max(q.continuity_l1);
        let err = (q.energy_change_j - q.flux_energy_j).abs() / escale / ns.max(f64::MIN_POSITIVE);
        if !err.is_finite() {
            return Err("nonfinite local scattering energy residual".into());
        }
        max_e = max_e.max(err);
        scatter += q.energy_change_j;
        flux += q.flux_energy_j;
        mass = q.mass;
        mass = apply(
            &mass,
            &mut escape_n,
            &mut escape_e,
            &mut work,
            &mut spread,
            &mut max_n,
            &mut max_e,
        )?;
        hist.push((
            (i + 1) as f64 * dt,
            mass.iter().sum::<f64>(),
            p.full_energy_j(&mass)?,
            escape_n,
            escape_e,
            work,
            scatter,
            flux,
        ));
    }
    let e1 = p.full_energy_j(&mass)?;
    let n1 = mass.iter().sum::<f64>();
    let balance_n = (n1 + escape_n - n0).abs() / n0;
    let balance_e = (e1 + escape_e - e0 - work - scatter).abs() / e0;
    let c = p.calibration;
    fs::create_dir_all(out)?;
    let mut f = BufWriter::new(fs::File::create(out.join("grid.tsv"))?);
    writeln!(
        f,
        "x\tnu_hz\tphase_volume\tinitial_mass\tfinal_mass\tup_s\tdown_s"
    )?;
    for i in 0..p.x.len() {
        writeln!(
            f,
            "{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}",
            p.x[i],
            c.nu0_hz + c.doppler_width_hz * p.x[i],
            p.volume[i],
            initial[i],
            mass[i],
            p.up.get(i).copied().unwrap_or(0.),
            p.down.get(i).copied().unwrap_or(0.)
        )?;
    }
    f.flush()?;
    let mut f = BufWriter::new(fs::File::create(out.join("history.tsv"))?);
    writeln!(f,"t_s\tmass\tenergy_j\tescape_mass\tescape_energy_j\tdrift_work_j\tredistribution_energy_j\tflux_energy_j")?;
    for (t, n, e, bn, be, w, q, fl) in hist {
        writeln!(
            f,
            "{t:.17e}\t{n:.17e}\t{e:.17e}\t{bn:.17e}\t{be:.17e}\t{w:.17e}\t{q:.17e}\t{fl:.17e}"
        )?;
    }
    f.flush()?;
    let mut f = BufWriter::new(fs::File::create(out.join("profile.tsv"))?);
    writeln!(
        f,
        "x\tvoigt_H\tdipole_H\tscatter_s\tdiffusion_voigt_x_s\tdiffusion_dipole_x_s"
    )?;
    for x in [
        0., 0.125, 0.25, 0.5, 1., 2., 3., 4., 5., 8., 10., 20., 40., 100., 1000.,
    ] {
        writeln!(
            f,
            "{x:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}",
            resonance::voigt_h(c.damping, x)?,
            resonance::voigt_dipole_moment(c.damping, x)?,
            c.scattering_rate(x)?,
            c.diffusion_x_model(x, DiffusionProfile::Voigt)?,
            c.diffusion_x_model(x, DiffusionProfile::DipoleMoment)?
        )?;
    }
    f.flush()?;
    let mut f = BufWriter::new(fs::File::create(out.join("run.txt"))?);
    writeln!(f,"scope=frozen_scalar_local_material_patch_conditional_drift_no_feedback\nsource={}\nsource_eta={eta:.17e}\nline={}\nprofile={}\nmesh={}\ninit={}\nnormalized_pulse={normalized}\nsteps={steps}\nduration_s={seconds:.17e}\nduration_eta={:.17e}\ndoppler_clock={d:.17e}\np_scatter={:.17e}\nT_m_k={:.17e}\nn_ground_m3={:.17e}\nH_s={:.17e}\nnu0_hz={:.17e}\na21_s={:.17e}\nf_lu={:.17e}\natom_mass_kg={:.17e}\ndoppler_fraction={:.17e}\ndoppler_width_hz={:.17e}\nvoigt_a={:.17e}\nsigma_integral_m2_hz={:.17e}\nrate_scale_s={:.17e}\npeak_scattering_s={:.17e}\npeak_scattering_per_eta={:.17e}\nK_log_voigt_peak_s={:.17e}\nstatic_sobolev_tau_diagnostic={:.17e}\nrecoil_per_scattering_doppler={:.17e}\nepsilon_doppler={:.17e}\nphase_density_m3={:.17e}\nnumber_defect={balance_n:.17e}\nenergy_balance_defect={balance_e:.17e}\nmax_step_number_defect={max_n:.17e}\nmax_step_continuity_l1={max_c:.17e}\nmax_step_energy_defect={max_e:.17e}\nmax_nonlinear_scaled_residual={max_bose:.17e}\nmax_nonlinear_iterations={max_it}\ndrift_numerical_second_detuning_moment={spread:.17e}\nredistribution_energy_j={scatter:.17e}\nredistribution_flux_energy_j={flux:.17e}\nredistribution_energy_j_per_m3={}\nescaped_mass={escape_n:.17e}\ninitial_mass={n0:.17e}\nfinal_mass={n1:.17e}",
        a[1],line.name,a[4],a[5],a[11],seconds*m.hubble_s/d,m.p_scatter,m.temperature_k,m.n_ground_m3,m.hubble_s,c.nu0_hz,line.a21_s,line.f_lu,line.mass_kg,c.doppler_fraction,c.doppler_width_hz,c.damping,c.sigma_integral_m2_hz,c.rate_scale_s,c.peak_scattering_s,c.peak_scattering_s*d/m.hubble_s,c.diffusion_log(0.)?,c.sobolev_optical_depth,c.recoil_per_scattering_doppler,c.epsilon_doppler,c.phase_density_m3(),if normalized{"not_applicable_normalized_pulse".to_string()}else{format!("{:.17e}",scatter*c.phase_density_m3())})?;
    f.flush()?;
    Ok(())
}
fn main() {
    if let Err(e) = run() {
        eprintln!("{e}");
        std::process::exit(1)
    }
}

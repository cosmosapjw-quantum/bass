//! Generate a deterministic all-m homogeneous CMB template in an observer tetrad.
use bianchi_rustcore::geom::group::BianchiGroup;
use bianchi_rustcore::geom::lie::{invariants, photon_potentials, POTENTIAL_MODES};
use bianchi_rustcore::homogeneous_sky::{
    field::Route,
    frames::{combine, energy_frame, relative_velocity},
    ionization::Ionization,
    material::Material,
    observed_sky,
    replay::los_sky,
    solve::{
        solve_general, solve_general_species_thermal, MatchedRecombination, Settings, Solution,
        SolveOptions,
    },
    CollisionScheme,
};
use bianchi_rustcore::kinetic::lie_hierarchy::lie_data;
use bianchi_rustcore::kinetic::lie_history::{initial_lie_node, required_flux, LieInitial};
use bianchi_rustcore::kinetic::radiation_feedback::{ExpansionEquation, LieUpdate};
use bianchi_rustcore::kinetic::sky_spectrum::{analyze, products, Mode};
use rec_microphysics::species_thermal::ReferenceHistory;
use std::{
    collections::BTreeMap,
    env, fs,
    io::{BufWriter, Write},
    path::{Path, PathBuf},
};

const HELP:&str="homogeneous_sky --out NEW_DIRECTORY [--family I|II|III|IV|V|VI0|VIh[:h]|VIstar|VII0|VIIh[:h]|VIII|IX|FLRW] [--shear 0.08 --duration 0.2 --steps 16 --nmu 10 --nphi 24 --lmax 4] [--tau 0.06 --electron-beta 0.1,0,0 | --material TSV] [--observer-beta 0,0,0] [--feedback auto|active|tracer|recoil] [--expansion-equation raychaudhuri|gauss-reduced] [--dust-fraction 0.2 --baryon-fraction 0.157 --dust-beta 0.12,0,0]. Clock eta=ln(a/a_emit). A material TSV has eta rate_per_eta beta_x beta_y beta_z. Dust fractions refer to initial total matter energy. --lie-ic FILE replaces --family/--shear: three whitespace rows shear/n (11 22 33 12 13 23) and a (1 2 3), Hubble normalized. A nonzero Codazzi flux determines the two streams' coflow.  --ionization FILE --n-h-emit-m3 VALUE --h-emit-s VALUE replace --tau/--material/--electron-beta in recoil mode; FILE has eta xe_per_H. --collision backward-euler|sdirk2 selects the Thomson cell integrator. --lie-update additive|congruence selects the active structure-constant step (congruence preserves Jacobi and h exactly). --omega-lambda X sets Lambda/(3H^2) on the initial slice (active feedback). --los-lmax L [--los-ntheta NT --los-nphi NP] replays the recorded solution along backward characteristics on an observer Gauss-Legendre grid (defaults NT=L+1, NP=2L+2) and writes los_modes.tsv/los_cl.tsv to multipole L. R113: --route rays|harmonic|harmonic-continuum selects the photon representation (harmonic = Lie-generated spin-harmonic PSTF hierarchy; --harmonic-lmax L, default 12, --harmonic-ntheta/--harmonic-nphi collision grid, defaults L+3, 2L+6). --route harmonic-continuum uses grid-free cold Thomson with --harmonic-work-lmax W (explicit W >= harmonic-lmax, <=256; angular grid retained only for diagnostics/REC/output). --neutrino-fraction F puts F of the initial radiation energy in collisionless massless neutrinos (active feedback). --observer-frame normal|host|spectator|radiation|radiation-total chooses the observer velocity on the final slice instead of --observer-beta. lie_constants.tsv lists the Y_LM type constants of the photon generator; run.txt reports the radiation energy frames, stream velocities, local boost and global tilt. --recombination matched --t-unit-k T (T_CMB0 (1+z_emit) in K) corrects the --ionization table by the implicit matched hydrogen TLA response of the transported sky (REC matched_history; writes recombination.tsv); --recombination-stop-eta E holds the offset after eta = E (e.g. where an REI bass_ionization table hands over to reionization). R116-B: --recombination species-thermal --species-reference TSV enables source-owned H/He/W matched history, replaces --ionization and its anchors, requires recoil. One helium owner phase only; tracer thermal ledger, lagged opacity.";
type Error = Box<dyn std::error::Error>;
fn args() -> Result<BTreeMap<String, String>, Error> {
    let mut args = env::args().skip(1);
    let mut output = BTreeMap::new();
    while let Some(k) = args.next() {
        let key = k.strip_prefix("--").ok_or("expected named option")?;
        if ![
            "out",
            "family",
            "lie-ic",
            "ionization",
            "n-h-emit-m3",
            "h-emit-s",
            "shear",
            "duration",
            "steps",
            "nmu",
            "nphi",
            "lmax",
            "tau",
            "electron-beta",
            "material",
            "observer-beta",
            "feedback",
            "expansion-equation",
            "dust-fraction",
            "baryon-fraction",
            "dust-beta",
            "collision",
            "lie-update",
            "omega-lambda",
            "los-lmax",
            "los-ntheta",
            "los-nphi",
            "route",
            "recombination",
            "species-reference",
            "t-unit-k",
            "recombination-stop-eta",
            "harmonic-lmax",
            "harmonic-work-lmax",
            "harmonic-ntheta",
            "harmonic-nphi",
            "neutrino-fraction",
            "observer-frame",
        ]
        .contains(&key)
        {
            return Err(format!("unknown option {k}").into());
        }
        let v = args.next().ok_or("missing option value")?;
        if output.insert(key.to_string(), v).is_some() {
            return Err(format!("repeated {k}").into());
        }
    }
    Ok(output)
}
fn vector(s: &str) -> Result<[f64; 3], Error> {
    let v: Vec<f64> = s.split(',').map(str::parse).collect::<Result<_, _>>()?;
    let v: [f64; 3] = v
        .try_into()
        .map_err(|_| "expected three comma-separated beta components")?;
    if !(v.iter().map(|a| a * a).sum::<f64>() < 1.) {
        return Err("velocity must be finite and subluminal".into());
    }
    Ok(v)
}
fn read_lie(path: &Path) -> Result<LieInitial, Error> {
    let source = fs::read_to_string(path)?;
    let mut rows = BTreeMap::new();
    for (i, line) in source.lines().enumerate() {
        let mut fields = line.split('#').next().unwrap_or("").split_whitespace();
        let Some(label) = fields.next() else { continue };
        let size = match label {
            "shear" | "n" => 6,
            "a" => 3,
            _ => return Err(format!("unknown Lie IC row {label} on line {}", i + 1).into()),
        };
        let values = fields
            .map(str::parse::<f64>)
            .collect::<Result<Vec<_>, _>>()?;
        if values.len() != size || !values.iter().all(|v| v.is_finite()) {
            return Err(format!("Lie IC {label} needs {size} finite entries").into());
        }
        if rows.insert(label, values).is_some() {
            return Err(format!("repeated Lie IC row {label}").into());
        }
    }
    let tensor = |v: &[f64]| [[v[0], v[3], v[4]], [v[3], v[1], v[5]], [v[4], v[5], v[2]]];
    let a = &rows.get("a").ok_or("missing Lie IC a")?;
    Ok(LieInitial {
        shear: tensor(rows.get("shear").ok_or("missing Lie IC shear")?),
        n: tensor(rows.get("n").ok_or("missing Lie IC n")?),
        a: [a[0], a[1], a[2]],
    })
}
fn writer(path: &Path) -> Result<BufWriter<fs::File>, Error> {
    Ok(BufWriter::new(fs::File::create_new(path)?))
}
fn write_modes(dir: &Path, modes: &[Mode], lmax: usize) -> Result<(), Error> {
    write_modes_as(dir, modes, lmax, "modes.tsv", "cl.tsv")
}
fn write_modes_as(
    dir: &Path,
    modes: &[Mode],
    lmax: usize,
    modes_name: &str,
    cl_name: &str,
) -> Result<(), Error> {
    let mut f = writer(&dir.join(modes_name))?;
    write!(f, "ell\tm\tT_re\tT_im\tE_re\tE_im\tB_re\tB_im")?;
    for name in ["TT", "TE", "TB", "EE", "EB", "BB"] {
        write!(f, "\t{name}_re\t{name}_im")?;
    }
    writeln!(f)?;
    let mut sums = vec![[0.; 6]; lmax + 1];
    for mode in modes {
        write!(f, "{}\t{}", mode.ell, mode.m)?;
        for a in &mode.alm {
            write!(f, "\t{:.16e}\t{:.16e}", a[0], a[1])?;
        }
        for (i, x) in products(mode, mode).iter().enumerate() {
            write!(f, "\t{:.16e}\t{:.16e}", x[0], x[1])?;
            sums[mode.ell][i] += x[0];
        }
        writeln!(f)?;
    }
    f.flush()?;
    let mut c = writer(&dir.join(cl_name))?;
    writeln!(c, "ell\tTT\tTE\tTB\tEE\tEB\tBB")?;
    for (ell, row) in sums.iter().enumerate() {
        write!(c, "{ell}")?;
        for x in row {
            write!(c, "\t{:.16e}", x / (2 * ell + 1) as f64)?;
        }
        writeln!(c)?;
    }
    c.flush()?;
    Ok(())
}
fn diagnostics(dir: &Path, sol: &Solution) -> Result<(), Error> {
    let mut f = writer(&dir.join("diagnostics.tsv"))?;
    writeln!(f,"eta\thubble_ratio\tomega_radiation\tomega_dust\tgauss\tcodazzi_x\tcodazzi_y\tcodazzi_z\tjacobi_norm\tsolid_angle\tenergy_integral\tflux_x_over_E\tflux_y_over_E\tflux_z_over_E\tmin_screen_eigenvalue\tmax_screen_leak\tproper_depth\tcollision_energy_defect\thost_beta_x\thost_beta_y\thost_beta_z")?;
    for snap in &sol.history {
        let n = &snap.node;
        let r = &snap.radiation;
        let vals = [
            n.eta,
            n.hubble_ratio,
            n.omega_radiation,
            snap.omega_dust,
            n.gauss_residual,
            n.codazzi_residual[0],
            n.codazzi_residual[1],
            n.codazzi_residual[2],
            n.jacobi_residual.iter().map(|x| x * x).sum::<f64>().sqrt(),
            r.area,
            r.energy,
            r.flux[0],
            r.flux[1],
            r.flux[2],
            r.minimum_screen_eigenvalue,
            r.max_screen_leak,
            snap.proper_depth,
            snap.collision_energy_defect,
            snap.host_beta[0],
            snap.host_beta[1],
            snap.host_beta[2],
        ];
        for (i, x) in vals.iter().enumerate() {
            if i > 0 {
                write!(f, "\t")?;
            }
            write!(f, "{x:.16e}")?;
        }
        writeln!(f)?;
    }
    f.flush()?;
    Ok(())
}
/// Exact frame velocities of the final slice in the normal tetrad (R113 THEORY D8).
struct Frames {
    /// Energy frame of the photons.
    photon: [f64; 3],
    /// Energy frame of photons plus neutrinos (equal to `photon` without neutrinos).
    total: [f64; 3],
    host: Option<[f64; 3]>,
    spectator: Option<[f64; 3]>,
}
fn frame_report(sol: &Solution) -> Result<Frames, Error> {
    let last = sol.history.last().ok_or("empty history")?;
    let photon = energy_frame(last.radiation.flux, last.radiation.pressure)?;
    let total = match &last.neutrino {
        Some(nu) => {
            let (_, f, p) = combine(&[
                (sol.photon_scale, &last.radiation),
                (sol.neutrino_scale, nu),
            ])?;
            energy_frame(f, p)?
        }
        None => photon,
    };
    let (host, spectator) = match &sol.final_dust {
        Some(d) => (Some(d.beam(0)?.beta), Some(d.beam(1)?.beta)),
        None => (None, None),
    };
    Ok(Frames {
        photon,
        total,
        host,
        spectator,
    })
}
/// Y_LM type constants (L <= 2) of the photon generator on the first and last slice.
fn lie_constants(dir: &Path, sol: &Solution) -> Result<(), Error> {
    let mut f = writer(&dir.join("lie_constants.tsv"))?;
    writeln!(
        f,
        "slice\tL\tM\tR_re\tR_im\tU_re\tU_im\tZ_re\tZ_im\tomega_re\tomega_im"
    )?;
    let first = &sol.history[0].node;
    let last = &sol.history.last().ok_or("empty history")?.node;
    for (name, node) in [("initial", first), ("final", last)] {
        let p = photon_potentials(&lie_data(node));
        for k in 0..POTENTIAL_MODES {
            let l = (k as f64).sqrt().floor() as i64;
            let m = k as i64 - l * l - l;
            write!(f, "{name}\t{l}\t{m}")?;
            for c in [p.r[k], p.u[k], p.z[k], p.omega[k]] {
                write!(f, "\t{:.16e}\t{:.16e}", c.re, c.im)?;
            }
            writeln!(f)?;
        }
    }
    f.flush()?;
    Ok(())
}
/// Matched recombination: tabulated total electron fraction x_e, matched offset,
/// and corrected total electron fraction (including helium).
fn recombination_history(dir: &Path, sol: &Solution, ion: &Ionization) -> Result<(), Error> {
    let mut f = writer(&dir.join("recombination.tsv"))?;
    writeln!(f, "eta\txe_table\tdelta_xe\txe")?;
    for snap in &sol.history {
        let table = ion.xe_at(snap.node.eta)?;
        writeln!(
            f,
            "{:.16e}\t{:.16e}\t{:.16e}\t{:.16e}",
            snap.node.eta,
            table,
            snap.delta_xe,
            table + snap.delta_xe
        )?;
    }
    f.flush()?;
    Ok(())
}
/// Species-resolved thermal ledger. Initial interval diagnostics are empty.
fn thermochemistry_history(
    dir: &Path,
    sol: &Solution,
    reference: &ReferenceHistory,
) -> Result<(), Error> {
    let mut f = writer(&dir.join("thermochemistry.tsv"))?;
    writeln!(f,"eta	xp	x_hi	x_heii	x_heiii	x_hei	xe	tm_k	w_k	xp_ref	x_heii_ref	x_heiii_ref	xe_ref	tm_ref_k	delta_xe	delta_tm_k	n_h_m3	h_s	gamma	expansion_ratio	endpoint_expansion_ratio	compton_temperature_k	iterations	scaled_residual	adiabatic_j_per_h	compton_j_per_h	external_j_per_h	matched_thermal_correction_j_per_h	thermal_defect_j_per_h	binding_change_j_per_h")?;
    let fhe = reference.f_he();
    let opt = |v: Option<f64>| v.map(|v| format!("{v:.17e}")).unwrap_or_default();
    for s in &sol.thermochemistry {
        let y = s.state;
        let r = s.reference;
        let d = s.diagnostics;
        let base = [
            s.eta,
            y.xp(),
            y.x_hi,
            y.x_heii,
            y.x_heiii,
            y.x_hei(fhe),
            y.xe(),
            y.tm(fhe),
            y.w_k,
            r.xp(),
            r.x_heii,
            r.x_heiii,
            r.xe(),
            r.tm(fhe),
            y.xe() - r.xe(),
            y.tm(fhe) - r.tm(fhe),
            s.n_h_m3,
            s.h_s,
            s.gamma,
        ];
        let mut values = base.iter().map(|v| format!("{v:.17e}")).collect::<Vec<_>>();
        values.extend([
            opt(s.expansion_ratio),
            opt(s.endpoint_expansion_ratio),
            opt(s.compton_temperature_k),
            d.iterations.to_string(),
        ]);
        values.extend(
            [
                d.scaled_residual,
                d.physical_adiabatic_j_per_h,
                d.physical_compton_j_per_h,
                d.physical_external_j_per_h,
                d.matched_thermal_correction_j_per_h,
                d.thermal_balance_defect_j_per_h,
                d.binding_change_j_per_h,
            ]
            .iter()
            .map(|v| format!("{v:.17e}")),
        );
        writeln!(f, "{}", values.join("\t"))?;
    }
    f.flush()?;
    Ok(())
}
/// Neutrino density, flux and anisotropic stress pi/rho along the history.
fn species(dir: &Path, sol: &Solution) -> Result<(), Error> {
    if sol.neutrinos.is_none() {
        return Ok(());
    }
    let mut f = writer(&dir.join("species.tsv"))?;
    writeln!(
        f,
        "eta\tomega_neutrino\tflux_x\tflux_y\tflux_z\tpi_xx\tpi_yy\tpi_zz\tpi_xy\tpi_xz\tpi_yz"
    )?;
    for snap in &sol.history {
        let nu = snap.neutrino.as_ref().ok_or("missing neutrino moments")?;
        let p = nu.pressure;
        let third = (p[0][0] + p[1][1] + p[2][2]) / 3.0;
        let vals = [
            snap.node.eta,
            snap.omega_neutrino,
            nu.flux[0],
            nu.flux[1],
            nu.flux[2],
            p[0][0] - third,
            p[1][1] - third,
            p[2][2] - third,
            p[0][1],
            p[0][2],
            p[1][2],
        ];
        for (i, x) in vals.iter().enumerate() {
            if i > 0 {
                write!(f, "\t")?;
            }
            write!(f, "{x:.16e}")?;
        }
        writeln!(f)?;
    }
    f.flush()?;
    Ok(())
}
fn run() -> Result<(), Error> {
    let a = args()?;
    let opt = |k: &str, d: &'static str| a.get(k).map(String::as_str).unwrap_or(d);
    let out = PathBuf::from(a.get("out").ok_or("missing --out")?);
    if out.exists() {
        return Err("output directory already exists".into());
    }
    let dur: f64 = opt("duration", "0.2").parse()?;
    let lmax = opt("lmax", "4").parse::<usize>()?;
    let (nmu, nphi) = (
        opt("nmu", "10").parse::<usize>()?,
        opt("nphi", "24").parse::<usize>()?,
    );
    let route = match opt("route", "rays") {
        "rays" => {
            if [
                "harmonic-lmax",
                "harmonic-ntheta",
                "harmonic-nphi",
                "harmonic-work-lmax",
            ]
            .iter()
            .any(|k| a.contains_key(*k))
            {
                return Err("--harmonic-* options require --route harmonic".into());
            }
            if nmu < lmax.saturating_add(1) || nphi < lmax.saturating_mul(2).saturating_add(1) {
                return Err("sampling is below nominal harmonic resolution".into());
            }
            Route::Rays
        }
        "harmonic" | "harmonic-continuum" => {
            let continuum = opt("route", "rays") == "harmonic-continuum";
            if !continuum && a.contains_key("harmonic-work-lmax") {
                return Err("--harmonic-work-lmax requires --route harmonic-continuum".into());
            }
            let l: usize = opt("harmonic-lmax", "12").parse()?;
            let nt = match a.get("harmonic-ntheta") {
                Some(x) => x.parse::<usize>()?,
                None => l + 3,
            };
            let np = match a.get("harmonic-nphi") {
                Some(x) => x.parse::<usize>()?,
                None => 2 * l + 6,
            };
            if nt < lmax.saturating_add(1) || np < lmax.saturating_mul(2).saturating_add(1) {
                return Err("harmonic collision grid is below nominal resolution of --lmax".into());
            }
            if nmu < 4 || nphi < 4 || nphi % 2 != 0 {
                return Err("seed --nmu/--nphi must be >= 4 with even --nphi".into());
            }
            if continuum {
                let work: usize = a
                    .get("harmonic-work-lmax")
                    .ok_or("harmonic-continuum requires --harmonic-work-lmax")?
                    .parse()?;
                if work < l || work > 256 {
                    return Err("invalid continuum work band".into());
                }
                Route::HarmonicContinuum {
                    lmax: l,
                    n_theta: nt,
                    n_phi: np,
                    work_lmax: work,
                }
            } else {
                Route::Harmonic {
                    lmax: l,
                    n_theta: nt,
                    n_phi: np,
                }
            }
        }
        _ => return Err("unknown route (rays, harmonic or harmonic-continuum)".into()),
    };
    let lie = if let Some(path) = a.get("lie-ic") {
        if a.contains_key("family") || a.contains_key("shear") {
            return Err("--lie-ic replaces --family and --shear".into());
        }
        let initial = read_lie(Path::new(path))?;
        if a.contains_key("dust-beta")
            && required_flux(&initial_lie_node(&initial)?)
                .iter()
                .map(|x| x * x)
                .sum::<f64>()
                .sqrt()
                > 1e-12
        {
            return Err("--dust-beta is fixed by Codazzi for this Lie initial slice".into());
        }
        Some(initial)
    } else {
        None
    };
    let species_reference = if opt("recombination", "table") == "species-thermal" {
        if [
            "ionization",
            "n-h-emit-m3",
            "h-emit-s",
            "material",
            "tau",
            "electron-beta",
            "t-unit-k",
            "recombination-stop-eta",
        ]
        .iter()
        .any(|k| a.contains_key(*k))
        {
            return Err(
                "species-thermal replaces optical and recombination anchors; one source owner only"
                    .into(),
            );
        }
        if opt("feedback", "auto") != "recoil" {
            return Err("species-thermal requires recoil".into());
        }
        let path = a
            .get("species-reference")
            .ok_or("missing --species-reference")?;
        Some(
            ReferenceHistory::parse(&fs::read_to_string(path)?)
                .map_err(|e| format!("species reference: {e:?}"))?,
        )
    } else {
        if a.contains_key("species-reference") {
            return Err("--species-reference requires --recombination species-thermal".into());
        }
        None
    };
    let ionization = if let Some(path) = a.get("ionization") {
        if a.contains_key("material") || a.contains_key("tau") || a.contains_key("electron-beta") {
            return Err(
                "--ionization replaces prescribed optical depth and electron motion inputs".into(),
            );
        }
        if opt("feedback", "auto") != "recoil" {
            return Err("--ionization requires --feedback recoil".into());
        }
        Some(Ionization::load(
            Path::new(path),
            a.get("n-h-emit-m3")
                .ok_or("missing --n-h-emit-m3 for --ionization")?
                .parse()?,
            a.get("h-emit-s")
                .ok_or("missing --h-emit-s for --ionization")?
                .parse()?,
        )?)
    } else {
        if a.contains_key("n-h-emit-m3") || a.contains_key("h-emit-s") {
            return Err("density and Hubble anchors require --ionization".into());
        }
        None
    };
    let material = if let Some(path) = a.get("material") {
        if a.contains_key("tau") || a.contains_key("electron-beta") {
            return Err("--material already specifies rate and velocity".into());
        }
        Material::load(Path::new(path))?
    } else {
        Material::constant(
            dur,
            opt("tau", "0").parse()?,
            vector(opt("electron-beta", "0,0,0"))?,
        )?
    };
    let active = match opt("feedback", "auto") {
        "active" | "recoil" => true,
        "tracer" => false,
        "auto" => !material.has_scattering(),
        _ => return Err("unknown feedback setting".into()),
    };
    let expansion = match opt("expansion-equation", "raychaudhuri") {
        "raychaudhuri" => ExpansionEquation::Raychaudhuri,
        "gauss-reduced" => ExpansionEquation::GaussReduced,
        _ => return Err("unknown expansion equation (raychaudhuri or gauss-reduced)".into()),
    };
    if a.contains_key("expansion-equation") && !active {
        return Err("--expansion-equation is an active feedback setting".into());
    }
    let cfg = Settings {
        family: opt("family", "I"),
        shear: opt("shear", "0.08").parse()?,
        duration: dur,
        steps: opt("steps", "16").parse()?,
        nmu,
        nphi,
        active,
        recoil: opt("feedback", "auto") == "recoil",
        dust_fraction: opt("dust-fraction", "0").parse()?,
        dust_beta: vector(opt("dust-beta", "0,0,0"))?,
        collision: CollisionScheme::parse(opt("collision", "backward-euler"))?,
        omega_lambda: opt("omega-lambda", "0").parse()?,
        lie_update: LieUpdate::parse(opt("lie-update", "additive"))?,
    };
    let los = match a.get("los-lmax") {
        Some(v) => {
            let l: usize = v.parse()?;
            let nt = match a.get("los-ntheta") {
                Some(x) => x.parse::<usize>()?,
                None => l + 1,
            };
            let np = match a.get("los-nphi") {
                Some(x) => x.parse::<usize>()?,
                None => 2 * l + 2,
            };
            if nt < l + 1 || np < 2 * l + 1 {
                return Err("line-of-sight grid is below nominal resolution of --los-lmax".into());
            }
            Some((l, nt, np))
        }
        None => {
            if a.contains_key("los-ntheta") || a.contains_key("los-nphi") {
                return Err("--los-ntheta/--los-nphi require --los-lmax".into());
            }
            None
        }
    };
    let recombination = match opt("recombination", "table") {
        "table" => {
            if a.contains_key("t-unit-k") || a.contains_key("recombination-stop-eta") {
                return Err(
                    "--t-unit-k/--recombination-stop-eta require --recombination matched".into(),
                );
            }
            None
        }
        "matched" => {
            if ionization.is_none() {
                return Err("--recombination matched corrects an --ionization table".into());
            }
            Some(MatchedRecombination {
                t_unit_k: a
                    .get("t-unit-k")
                    .ok_or("missing --t-unit-k for --recombination matched")?
                    .parse()?,
                n_h_emit_m3: opt("n-h-emit-m3", "").parse()?,
                h_emit_s: opt("h-emit-s", "").parse()?,
                stop_eta: a
                    .get("recombination-stop-eta")
                    .map(|v| v.parse::<f64>())
                    .transpose()?,
            })
        }
        "species-thermal" => None,
        other => return Err(format!("unknown --recombination {other}").into()),
    };
    let options = SolveOptions {
        route,
        neutrino_fraction: opt("neutrino-fraction", "0").parse()?,
        recombination,
    };
    if a.contains_key("observer-frame") && a.contains_key("observer-beta") {
        return Err("--observer-frame replaces --observer-beta".into());
    }
    let baryon_fraction: f64 = opt("baryon-fraction", "0.5").parse()?;
    let sol = if let Some(reference) = &species_reference {
        solve_general_species_thermal(
            &cfg,
            &material,
            lie.as_ref(),
            expansion,
            baryon_fraction,
            &options,
            reference,
        )?
    } else {
        solve_general(
            &cfg,
            &material,
            lie.as_ref(),
            ionization.as_ref(),
            expansion,
            baryon_fraction,
            &options,
        )?
    };
    let frames = frame_report(&sol)?;
    let observer_frame = a
        .get("observer-frame")
        .map(String::as_str)
        .unwrap_or("explicit_beta");
    let obs = match observer_frame {
        "explicit_beta" => vector(opt("observer-beta", "0,0,0"))?,
        "normal" => [0.; 3],
        "host" => frames
            .host
            .ok_or("--observer-frame host needs massive streams")?,
        "spectator" => frames
            .spectator
            .ok_or("--observer-frame spectator needs massive streams")?,
        "radiation" => frames.photon,
        "radiation-total" => frames.total,
        other => return Err(format!("unknown observer frame {other}").into()),
    };
    let sky = observed_sky(&sol.photons, obs)?;
    let modes = analyze(&sky, lmax)?;
    let los_result = match los {
        Some((l, nt, np)) => {
            let clock = std::time::Instant::now();
            let s = los_sky(&sol.records, obs, nt, np)?;
            let m = s.modes(l)?;
            Some((l, nt, np, s, m, clock.elapsed().as_secs_f64()))
        }
        None => None,
    };
    if let Some(parent) = out.parent().filter(|p| !p.as_os_str().is_empty()) {
        fs::create_dir_all(parent)?;
    }
    fs::create_dir(&out)?;
    write_modes(&out, &modes, lmax)?;
    if let Some((l, _, _, _, m, _)) = &los_result {
        write_modes_as(&out, m, *l, "los_modes.tsv", "los_cl.tsv")?;
    }
    diagnostics(&out, &sol)?;
    lie_constants(&out, &sol)?;
    species(&out, &sol)?;
    if options.recombination.is_some() {
        recombination_history(&out, &sol, ionization.as_ref().ok_or("missing ionization")?)?;
    }
    if let Some(reference) = &species_reference {
        thermochemistry_history(&out, &sol, reference)?;
    }
    let mut f = writer(&out.join("run.txt"))?;
    writeln!(f,"schema=bass.homogeneous_sky.v2\ncodazzi_convention=(D_b sigma^b_a + kappa q_a)/H^2 in the propagation tetrad\nfamily={}\nfeedback={}\nduration={}\nsteps={}\nnmu={}\nnphi={}\nlmax={}\nshear={}\ndust_fraction={}\ndust_beta={:?}\nobserver_beta={:?}",if lie.is_some(){"custom_lie"}else{cfg.family},if cfg.recoil{"active_photons_dust_Thomson_recoil"}else if active{"active_photons_and_optional_dust"}else{"polarized_tracer_on_native_scalar_radiation"},dur,cfg.steps,nmu,nphi,lmax,if lie.is_some(){"custom_tensor".into()}else{cfg.shear.to_string()},cfg.dust_fraction,if sol.initial_dust_mode=="codazzi_coflow"{sol.history[0].host_beta}else{cfg.dust_beta},obs)?;
    writeln!(
        f,
        "initial_dust_mode={}\ninitial_host_beta={:?}\nopacity_source={}",
        sol.initial_dust_mode,
        sol.history[0].host_beta,
        if species_reference.is_some() {
            "species_reference_plus_lagged_delta_xe_times_host_proper_density_over_H"
        } else if ionization.is_some() {
            "xe_times_evolved_host_rest_density_over_H"
        } else {
            "prescribed_rate_per_eta"
        }
    )?;
    if a.contains_key("baryon-fraction") {
        writeln!(f, "initial_baryon_normal_mass_fraction={baryon_fraction}")?;
    }
    if let Some(ic) = &lie {
        writeln!(
            f,
            "lie_shear={:?}\nlie_n={:?}\nlie_a={:?}\nrequired_initial_q_over_E={:?}",
            ic.shear,
            ic.n,
            ic.a,
            required_flux(&sol.history[0].node)
        )?;
    }
    writeln!(
        f,
        "expansion_equation={}",
        if active {
            expansion.name()
        } else {
            "native_qstate"
        }
    )?;
    let first = &sol.history[0].node;
    let last = &sol.history.last().ok_or("empty history")?.node;
    let class = |n: &bianchi_rustcore::kinetic::lie_history::RayNode| {
        let g = BianchiGroup::new(
            [
                n.n[0][0], n.n[1][1], n.n[2][2], n.n[0][1], n.n[0][2], n.n[1][2],
            ],
            n.a,
        );
        let c = g.classify();
        (c.name, c.kappa)
    };
    let (type0, kappa0) = class(first);
    let (type1, kappa1) = class(last);
    writeln!(
        f,
        "lie_update={}\ncollision_scheme={}\nomega_lambda_initial={}\nomega_lambda_final={}\nlie_type_initial={}\nlie_type_final={}\nlie_kappa_inverse_h_initial={:?}\nlie_kappa_inverse_h_final={:?}\nrecorded_steps={}\nrecorded_collision_events={}",
        cfg.lie_update.name(),
        cfg.collision.name(),
        first.omega_lambda,
        last.omega_lambda,
        type0,
        type1,
        kappa0,
        kappa1,
        sol.records.len(),
        sol.records
            .iter()
            .map(|r| r.first.len() + r.second.len())
            .sum::<usize>()
    )?;
    if let Some((l, nt, np, s, _, seconds)) = &los_result {
        writeln!(
            f,
            "los_lmax={l}\nlos_grid=gauss_legendre_{nt}_x_uniform_phi_{np}\nlos_max_landing_error={:e}\nlos_min_intensity={:e}\nlos_min_screen_eigenvalue={:e}\nlos_seconds={seconds:.3}\nlos_threads={}",
            s.max_landing_error,
            s.min_intensity,
            s.min_screen_eigenvalue,
            rayon::current_num_threads()
        )?;
    }
    let inv0 = invariants(&first.n, &first.a);
    let inv1 = invariants(&last.n, &last.a);
    let relative = |frame: [f64; 3], object: [f64; 3]| relative_velocity(frame, object);
    writeln!(
        f,
        "route={}\nneutrino_fraction={}\nlie_h_initial={:?}\nlie_h_final={:?}\nlie_trace_n_initial={:e}\nlie_a_norm_initial={:e}\nobserver_frame={observer_frame}\nobserver_beta_used={:?}\nframe_photon_energy_beta={:?}\nframe_radiation_energy_beta={:?}\nframe_host_beta={:?}\nframe_spectator_beta={:?}\nlocal_boost_observer_vs_radiation={:?}\nglobal_tilt_host_vs_normal={:?}\nglobal_tilt_host_vs_radiation={:?}\nrecombination={}\ndelta_xe_final={:e}",
        sol.route.name(),
        options.neutrino_fraction,
        inv0.h,
        inv1.h,
        inv0.trace_n,
        inv0.a_norm,
        obs,
        frames.photon,
        frames.total,
        frames.host,
        frames.spectator,
        relative(frames.total, obs)?,
        frames.host,
        frames.host.map(|h| relative(frames.total, h)).transpose()?,
        if species_reference.is_some() {"species-thermal"}
        else if options.recombination.is_some() {"matched"} else {"table"},
        sol.history.last().ok_or("empty history")?.delta_xe,
    )?;
    if let Some(r) = &species_reference {
        let a = r.nodes()[0];
        writeln!(f,"species_helium_model={:?}\nspecies_f_he={:.17e}\nspecies_reference_n_h_emit_m3={:.17e}\nspecies_reference_h_emit_s={:.17e}\nspecies_reference_tr_emit_k={:.17e}\nspecies_thermal_energy_feedback=tracer_only\nspecies_coupling=lagged_opacity_BE",r.helium(),r.f_he(),a.n_h_m3,a.h_s,a.tr_k)?;
    }
    writeln!(f,"basis=outward sky opposite photon propagation, HEALPix spin convention\nT=I^(1/4)/angular_mean(I^(1/4))-1\nQ,U=bolometric Stokes/(4 angular_mean(I))\nC_lm=a_lm^X conjugate(a_lm^Y)\ndiagnostics_flux=normal-frame photon propagation\nargv={:?}",env::args().skip(1).collect::<Vec<_>>())?;
    f.flush()?;
    Ok(())
}
fn main() {
    if env::args().any(|s| s == "--help" || s == "-h") {
        println!("{HELP}");
        return;
    }
    if let Err(e) = run() {
        eprintln!("{e}");
        std::process::exit(1);
    }
}

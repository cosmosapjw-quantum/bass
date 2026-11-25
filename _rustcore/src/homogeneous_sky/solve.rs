//! E-fold stepping of the photon distribution with either a native prescribed
//! background or active Einstein feedback of the transported normal-frame stress.
//!
//! R113: one solver for both radiation representations (`field::Route`: Lagrangian
//! rays or the Lie-generated spin-harmonic hierarchy) and an optional collisionless
//! massless neutrino species in the same representation. The legacy entry points
//! (`solve`, `solve_with_inputs`, `solve_with_expansion`, `solve_with_species`)
//! delegate with `SolveOptions::default()` (rays, no neutrinos) and perform the same
//! floating-point operations as R112.
use super::field::{Field, Route};
use super::ionization::Ionization;
use super::material::Material;
use super::rec_bridge::material_directional_sky;
use super::replay::StepRecord;
use super::{scatter_with, CollisionEvent, CollisionScheme, Photon, RadiationMoments};
use crate::kinetic::lie_history::{
    initial_lie_node, radiation_history, radiation_history_from_lie, required_flux, LieInitial,
    RayNode,
};
use crate::kinetic::radiation_feedback::{
    advance_mixture_with_options, refresh_mixture, ExpansionEquation, LieUpdate,
};
use crate::kinetic::tilted_dust::Dust;
use rec_microphysics::anisotropic::{compton_temperature_k, DirectionalSky};
use rec_microphysics::matched_history::{
    anisotropic_peebles_rate, implicit_matched_step, isotropic_peebles_rate, MatchedStep, X_MAX,
};
use rec_microphysics::species_thermal::{
    matched_step as thermal_step, Point as ThermalPoint, ReferenceHistory, State as ThermalState,
    StepDiagnostics as ThermalDiagnostics,
};

pub struct Settings<'a> {
    pub family: &'a str,
    pub shear: f64,
    pub duration: f64,
    pub steps: usize,
    pub nmu: usize,
    pub nphi: usize,
    pub active: bool,
    pub recoil: bool,
    /// Fraction of initial matter energy placed in two counterstreaming dust fluids.
    pub dust_fraction: f64,
    pub dust_beta: [f64; 3],
    /// Time integrator of each Thomson depth cell.
    pub collision: CollisionScheme,
    /// Lambda/(3H^2) on the initial slice (active feedback only).
    pub omega_lambda: f64,
    /// Structure-constant update of the active Einstein step.
    pub lie_update: LieUpdate,
}

/// R113 options beyond the R109-R112 settings. The default reproduces R112.
#[derive(Clone, Debug, PartialEq)]
pub struct SolveOptions {
    /// Representation of photons and neutrinos.
    pub route: Route,
    /// Fraction of the initial radiation energy carried by collisionless massless
    /// neutrinos (active feedback only; 0 disables the species).
    pub neutrino_fraction: f64,
    /// Matched implicit hydrogen recombination on top of the ionization table
    /// (requires `ionization`; None keeps the tabulated history).
    pub recombination: Option<MatchedRecombination>,
}

impl Default for SolveOptions {
    fn default() -> Self {
        Self {
            route: Route::Rays,
            neutrino_fraction: 0.0,
            recombination: None,
        }
    }
}

/// R113 THEORY D9. The tabulated electron fraction x_ref(eta) (an FLRW HYREC
/// history) is corrected by the hydrogen response delta_x of the collapsed-Peebles
/// TLA closure (REC `matched_history`) to the transported sky in the host rest
/// frame, to the host proper density and to the normal expansion:
///
///   x_{n+1} - x_n = x_ref,n+1 - x_ref,n + d_eta [r_ani(x_{n+1})/(gamma H) - r_ref/H_ref].
///
/// The reference is the flat FLRW model with the run's initial Lambda fraction and
/// matter/radiation split, T_ref = t_unit e^-eta, n_H,ref = n_H,emit e^-3eta. The
/// closure is hydrogen only: helium electrons stay as tabulated, the hydrogen
/// fraction is min(x_ref, 1 - 1e-12) (no response while the reference hydrogen is
/// fully ionized), and the matter temperature is the Compton temperature
/// of the material sky. delta_x enters the Thomson cells of the next step (first
/// order operator splitting). Fails closed where the Sobolev expansion of any
/// direction is not positive.
#[derive(Clone, Debug, PartialEq)]
pub struct MatchedRecombination {
    /// Absolute temperature [K] of unit bolometric intensity, T_CMB,0 (1 + z_emit).
    pub t_unit_k: f64,
    /// Proper hydrogen density [m^-3] and Hubble rate [s^-1] of the reference model
    /// at emission (the anchors of the ionization table).
    pub n_h_emit_m3: f64,
    pub h_emit_s: f64,
    /// Last step endpoint e-fold allowed for a matched step (None: the whole run).
    /// Steps ending past `stop_eta` hold the offset constant. Use it to stop the TLA
    /// response at the handover to another physics model (e.g. the REI reionization
    /// segment of an REI `bass_ionization` table), since the closure has no ionizing sources.
    pub stop_eta: Option<f64>,
}

impl MatchedRecombination {
    fn validate(&self) -> Result<(), String> {
        if [self.t_unit_k, self.n_h_emit_m3, self.h_emit_s]
            .iter()
            .all(|v| v.is_finite() && *v > 0.)
            && self.stop_eta.is_none_or(|e| e.is_finite() && e > 0.)
        {
            Ok(())
        } else {
            Err(
                "matched recombination needs finite positive t_unit, n_H,emit, H_emit and stop eta"
                    .into(),
            )
        }
    }
    fn active(&self, end_eta: f64) -> bool {
        self.stop_eta
            .is_none_or(|stop| end_eta <= stop + 32. * f64::EPSILON * (1. + stop))
    }
    /// Reference hydrogen fraction, proper rate dx/dt [s^-1] and H [s^-1] at eta.
    fn reference(
        &self,
        ion: &Ionization,
        eta: f64,
        omega_lambda: f64,
        matter_fraction: f64,
    ) -> Result<(f64, f64, f64), String> {
        let x = ion.xe_at(eta)?.min(X_MAX);
        let e2 = omega_lambda
            + (1. - omega_lambda)
                * (matter_fraction * (-3. * eta).exp()
                    + (1. - matter_fraction) * (-4. * eta).exp());
        if !e2.is_finite() || e2 <= 0. {
            return Err(
                "matched recombination reference expansion squared must be positive".into(),
            );
        }
        let h = self.h_emit_s * e2.sqrt();
        let rate = isotropic_peebles_rate(
            self.t_unit_k * (-eta).exp(),
            self.n_h_emit_m3 * (-3. * eta).exp(),
            h,
            x,
        )
        .map_err(|e| format!("reference recombination rate: {e:?}"))?;
        Ok((x, rate, h))
    }
}

pub struct Snapshot {
    pub node: RayNode,
    pub radiation: RadiationMoments,
    pub omega_dust: f64,
    pub proper_depth: f64,
    pub collision_energy_defect: f64,
    pub host_beta: [f64; 3],
    /// Neutrino moments (None without the species) and their Omega.
    pub neutrino: Option<RadiationMoments>,
    pub omega_neutrino: f64,
    /// Matched recombination offset of the electron fraction (0 when off).
    pub delta_xe: f64,
}
/// Accepted species/thermal state and energy ledger. Interval-dependent
/// quantities on the initial row are None, not fabricated derivatives.
pub struct ThermochemistrySnapshot {
    pub eta: f64,
    pub state: ThermalState,
    pub reference: ThermalState,
    pub n_h_m3: f64,
    pub h_s: f64,
    pub gamma: f64,
    pub expansion_ratio: Option<f64>,
    pub endpoint_expansion_ratio: Option<f64>,
    pub compton_temperature_k: Option<f64>,
    pub diagnostics: ThermalDiagnostics,
}
pub struct Solution {
    /// Nonempty only in the explicit species-thermal route.
    pub thermochemistry: Vec<ThermochemistrySnapshot>,
    pub photons: Vec<Photon>,
    pub history: Vec<Snapshot>,
    pub initial_dust_mode: &'static str,
    /// Accepted steps with their collision events, for line-of-sight replay.
    pub records: Vec<StepRecord>,
    /// Final neutrino sky (rays or harmonic grid samples), if present.
    pub neutrinos: Option<Vec<Photon>>,
    pub route: Route,
    /// Factors converting the photon/neutrino screen energy integrals to Omega H^2/H_emit^2.
    pub photon_scale: f64,
    pub neutrino_scale: f64,
    /// Final massive streams (stream zero is the Thomson host), if present.
    pub final_dust: Option<Dust>,
}

struct CellResult {
    sky: Field,
    nu: Option<Field>,
    dust: Option<Dust>,
    depth: f64,
    energy_defect: f64,
    first: Vec<CollisionEvent>,
    second: Vec<CollisionEvent>,
}

#[allow(clippy::too_many_arguments)]
fn collide_on(
    sky: &mut [Photon],
    dust: &mut Option<Dust>,
    depth: &mut f64,
    energy_defect: &mut f64,
    cells: Vec<(f64, [f64; 3])>,
    photon_scale: f64,
    recoil: bool,
    scheme: CollisionScheme,
) -> Result<Vec<CollisionEvent>, String> {
    let mut events = Vec::new();
    for (tau, b) in cells {
        if recoil {
            let host = dust.as_mut().ok_or("recoil requires massive matter")?;
            *energy_defect += super::recoil::scatter_with_recoil_events(
                sky,
                host,
                tau,
                photon_scale,
                scheme,
                &mut events,
            )?;
        } else {
            events.push(scatter_with(sky, tau, b, scheme)?);
        }
        *depth += tau;
    }
    Ok(events)
}

/// Collisions of one half step. Rays are scattered in place; a harmonic sky is
/// synthesized on its grid, scattered by the same kernels and projected back.
/// Optically empty cells record their zero-depth events without a projection.
fn collide_segment(
    result: &mut CellResult,
    cells: Vec<(f64, [f64; 3])>,
    photon_scale: f64,
    recoil: bool,
    scheme: CollisionScheme,
) -> Result<Vec<CollisionEvent>, String> {
    let CellResult {
        sky,
        dust,
        depth,
        energy_defect,
        ..
    } = result;
    match sky {
        Field::Rays(rays) => collide_on(
            rays,
            dust,
            depth,
            energy_defect,
            cells,
            photon_scale,
            recoil,
            scheme,
        ),
        Field::Harmonic(h) => {
            if let Some(work) = h.continuum_work_lmax {
                let mut events = Vec::new();
                for (tau, b) in cells {
                    if recoil {
                        let host = dust.as_mut().ok_or("recoil requires massive matter")?;
                        *energy_defect += super::harmonic_collision::scatter_with_recoil(
                            h,
                            host,
                            work,
                            tau,
                            photon_scale,
                            scheme,
                            &mut events,
                        )?;
                    } else {
                        let (out, event, _) = super::harmonic_collision::continuum_cell(
                            &h.coefficients,
                            h.lmax(),
                            work,
                            b,
                            tau,
                            scheme,
                        )?;
                        if tau != 0. {
                            let mut next = h.clone();
                            next.coefficients = out;
                            next.moments()?;
                            *h = next;
                        }
                        events.push(event);
                    }
                    *depth += tau;
                }
                return Ok(events);
            }
            if cells.iter().all(|(tau, _)| *tau == 0.0) {
                return collide_on(
                    &mut [],
                    dust,
                    depth,
                    energy_defect,
                    cells,
                    photon_scale,
                    recoil,
                    scheme,
                );
            }
            let before = h.photons()?;
            let mut grid = before.clone();
            let events = collide_on(
                &mut grid,
                dust,
                depth,
                energy_defect,
                cells,
                photon_scale,
                recoil,
                scheme,
            )?;
            h.absorb_delta(&before, &grid)?;
            Ok(events)
        }
    }
}

// Each half samples the host-rest density and H at its own geometric endpoint.
// In a massive stream D=m n_normal, E=gamma D, D(D/E)=m n_proper.
fn host_proper_mass(dust: &Option<Dust>) -> Result<f64, String> {
    let beam = dust
        .as_ref()
        .ok_or("ionization requires a massive host")?
        .beam(0)?;
    let proper = beam.normal_mass_density * (beam.normal_mass_density / beam.energy);
    if !proper.is_finite() || proper <= 0. {
        return Err("host proper mass density must be finite and positive".into());
    }
    Ok(proper)
}
struct Opacity<'a> {
    material: &'a Material,
    ionization: Option<(&'a Ionization, f64)>,
    /// Matched recombination offset of x_e (0 reproduces the table exactly).
    delta_xe: f64,
    strict_species_offset: bool,
}
impl Opacity<'_> {
    fn cells(
        &self,
        start: f64,
        end: f64,
        stage: &RayNode,
        dust: &Option<Dust>,
    ) -> Result<Vec<(f64, [f64; 3])>, String> {
        if let Some((ion, initial_proper)) = self.ionization {
            let ratio = host_proper_mass(dust)? / initial_proper;
            if self.strict_species_offset {
                ion.cells_with_strict_offset(start, end, ratio, stage.hubble_ratio, self.delta_xe)
            } else {
                ion.cells_with_offset(start, end, ratio, stage.hubble_ratio, self.delta_xe)
            }
        } else {
            self.material.cells(start, end)
        }
    }
}

#[allow(clippy::too_many_arguments)]
fn evolve_cell(
    input: &Field,
    neutrinos: Option<&Field>,
    dust: &Option<Dust>,
    l: &RayNode,
    r: &RayNode,
    opacity: &Opacity,
    photon_scale: f64,
    recoil: bool,
    scheme: CollisionScheme,
) -> Result<CellResult, String> {
    let mid = (l.eta + r.eta) * 0.5;
    let mut result = CellResult {
        sky: input.clone(),
        nu: neutrinos.cloned(),
        dust: dust.clone(),
        depth: 0.,
        energy_defect: 0.,
        first: Vec::new(),
        second: Vec::new(),
    };
    let cells = opacity.cells(l.eta, mid, l, &result.dust)?;
    result.first = collide_segment(&mut result, cells, photon_scale, recoil, scheme)?;
    result.sky.geometric(l, r)?;
    if let Some(nu) = result.nu.as_mut() {
        nu.geometric(l, r)?;
    }
    result.dust = move_dust(&result.dust, l, r)?;
    let cells = opacity.cells(mid, r.eta, r, &result.dust)?;
    result.second = collide_segment(&mut result, cells, photon_scale, recoil, scheme)?;
    Ok(result)
}

fn host_beta(d: &Option<Dust>) -> Result<[f64; 3], String> {
    Ok(match d {
        Some(dust) => dust.beam(0)?.beta,
        None => [0.; 3],
    })
}
struct Source {
    rad: f64,
    nu: f64,
    dust: f64,
    flux: [f64; 3],
    pressure: [[f64; 3]; 3],
}
fn source(
    rad: &RadiationMoments,
    photon_scale: f64,
    neutrinos: Option<(&RadiationMoments, f64)>,
    dust: &Option<Dust>,
    node: &RayNode,
) -> Result<Source, String> {
    let photon = rad.energy * photon_scale;
    let d = dust.as_ref().map(Dust::moments).transpose()?;
    let mass = d.as_ref().map_or(0., |x| x.energy);
    let h2 = node.hubble_ratio.powi(2);
    match neutrinos {
        None => {
            let total = photon + mass;
            if !total.is_finite() || total <= 0. || !(h2 > 0.) {
                return Err("invalid active energy".into());
            }
            let flux = std::array::from_fn(|i| {
                (photon * rad.flux[i] + d.as_ref().map_or(0., |x| x.flux[i])) / total
            });
            let pressure = std::array::from_fn(|i| {
                std::array::from_fn(|j| {
                    (photon * rad.pressure[i][j] + d.as_ref().map_or(0., |x| x.pressure[i][j]))
                        / total
                })
            });
            Ok(Source {
                rad: photon / h2,
                nu: 0.,
                dust: mass / h2,
                flux,
                pressure,
            })
        }
        Some((nm, nu_scale)) => {
            let neutrino = nm.energy * nu_scale;
            let total = photon + neutrino + mass;
            if !total.is_finite() || total <= 0. || !(h2 > 0.) || !(neutrino >= 0.) {
                return Err("invalid active energy".into());
            }
            let flux = std::array::from_fn(|i| {
                (photon * rad.flux[i]
                    + neutrino * nm.flux[i]
                    + d.as_ref().map_or(0., |x| x.flux[i]))
                    / total
            });
            let pressure = std::array::from_fn(|i| {
                std::array::from_fn(|j| {
                    (photon * rad.pressure[i][j]
                        + neutrino * nm.pressure[i][j]
                        + d.as_ref().map_or(0., |x| x.pressure[i][j]))
                        / total
                })
            });
            Ok(Source {
                rad: photon / h2,
                nu: neutrino / h2,
                dust: mass / h2,
                flux,
                pressure,
            })
        }
    }
}

fn move_dust(d: &Option<Dust>, a: &RayNode, b: &RayNode) -> Result<Option<Dust>, String> {
    d.as_ref().map(|d| d.advance(a, b)).transpose()
}

fn field_moments(f: &Option<Field>) -> Result<Option<RadiationMoments>, String> {
    f.as_ref().map(Field::moments).transpose()
}

pub fn solve(cfg: &Settings<'_>, mat: &Material) -> Result<Solution, String> {
    solve_with_inputs(cfg, mat, None, None)
}

pub fn solve_with_inputs(
    cfg: &Settings<'_>,
    mat: &Material,
    lie: Option<&LieInitial>,
    ionization: Option<&Ionization>,
) -> Result<Solution, String> {
    solve_with_expansion(cfg, mat, lie, ionization, ExpansionEquation::Raychaudhuri)
}

pub fn solve_with_expansion(
    cfg: &Settings<'_>,
    mat: &Material,
    lie: Option<&LieInitial>,
    ionization: Option<&Ionization>,
    expansion: ExpansionEquation,
) -> Result<Solution, String> {
    solve_with_species(cfg, mat, lie, ionization, expansion, 0.5)
}

/// Opt-in unequal normal-frame rest-mass partition of the two massive streams.
/// Stream zero is the baryonic Thomson host. Legacy entry points use 0.5.
pub fn solve_with_species(
    cfg: &Settings<'_>,
    mat: &Material,
    lie: Option<&LieInitial>,
    ionization: Option<&Ionization>,
    expansion: ExpansionEquation,
    baryon_fraction: f64,
) -> Result<Solution, String> {
    solve_general(
        cfg,
        mat,
        lie,
        ionization,
        expansion,
        baryon_fraction,
        &SolveOptions::default(),
    )
}

/// The general R113 solver: either radiation representation and optional
/// collisionless neutrinos, with every R109-R112 option.
pub fn solve_general(
    cfg: &Settings<'_>,
    mat: &Material,
    lie: Option<&LieInitial>,
    ionization: Option<&Ionization>,
    expansion: ExpansionEquation,
    baryon_fraction: f64,
    opts: &SolveOptions,
) -> Result<Solution, String> {
    solve_general_inner(
        cfg,
        mat,
        lie,
        ionization,
        expansion,
        baryon_fraction,
        opts,
        None,
    )
}

/// Source-owned species and thermal correction. The generated ionization
/// curve comes from the same reference; a second xe table is not accepted.
/// Chemistry is BE at accepted endpoint, with lagged opacity for this cell.
/// Heat is a tracer ledger, not an active photon/baryon energy source.
pub fn solve_general_species_thermal(
    cfg: &Settings<'_>,
    mat: &Material,
    lie: Option<&LieInitial>,
    expansion: ExpansionEquation,
    baryon_fraction: f64,
    opts: &SolveOptions,
    reference: &ReferenceHistory,
) -> Result<Solution, String> {
    if opts.recombination.is_some()
        || !cfg.recoil
        || mat.has_scattering()
        || mat.has_prescribed_motion()
    {
        return Err(
            "species thermochemistry requires exclusive reference ownership and recoil".into(),
        );
    }
    reference
        .at(cfg.duration)
        .map_err(|e| format!("species reference coverage: {e:?}"))?;
    let ion = Ionization::from_species_reference(reference)?;
    solve_general_inner(
        cfg,
        mat,
        lie,
        Some(&ion),
        expansion,
        baryon_fraction,
        opts,
        Some(reference),
    )
}

#[allow(clippy::too_many_arguments)]
fn solve_general_inner(
    cfg: &Settings<'_>,
    mat: &Material,
    lie: Option<&LieInitial>,
    ionization: Option<&Ionization>,
    expansion: ExpansionEquation,
    baryon_fraction: f64,
    opts: &SolveOptions,
    species_ref: Option<&ReferenceHistory>,
) -> Result<Solution, String> {
    if !(0.0 < baryon_fraction && baryon_fraction < 1.0)
        || (cfg.dust_fraction == 0. && baryon_fraction != 0.5)
    {
        return Err("unequal species fraction requires massive matter and 0 < f_b < 1".into());
    }
    if !cfg.active && expansion != ExpansionEquation::Raychaudhuri {
        return Err("Gauss-reduced expansion is available only for active feedback".into());
    }
    if ionization.is_some() && (!cfg.recoil || mat.has_scattering() || mat.has_prescribed_motion())
    {
        return Err(
            "dynamic ionization requires recoil feedback and replaces the prescribed optical input"
                .into(),
        );
    }
    if !cfg.duration.is_finite()
        || cfg.duration <= 0.
        || cfg.steps == 0
        || !(0.0..1.0).contains(&cfg.dust_fraction)
        || !cfg.shear.is_finite()
        || !cfg.dust_beta.iter().all(|v| v.is_finite())
        || cfg.dust_beta.iter().map(|v| v * v).sum::<f64>() >= 1.
    {
        return Err("invalid history, dust fraction or tilt".into());
    }
    if cfg.recoil && (!cfg.active || cfg.dust_fraction <= 0. || mat.has_prescribed_motion()) {
        return Err("recoil uses an active massive electron host and its own evolving velocity; input must supply the bare rate only".into());
    }
    if cfg.active && !cfg.recoil && mat.has_scattering() {
        return Err("active collisionless feedback requires zero optical rate: a prescribed scattering medium supplies no dynamical recoil".into());
    }
    if !cfg.active && cfg.dust_fraction != 0. {
        return Err("two dust streams require active geometry".into());
    }
    if !cfg.omega_lambda.is_finite() || cfg.omega_lambda < 0. {
        return Err("Omega_Lambda must be finite and nonnegative".into());
    }
    if !cfg.active && cfg.lie_update != LieUpdate::Additive {
        return Err("the congruence Lie update applies to active geometry; the tracer background uses its native QState step".into());
    }
    if !cfg.active && cfg.omega_lambda != 0. {
        return Err("a cosmological constant requires active geometry (the tracer background is radiation-only)".into());
    }
    if cfg.dust_fraction == 0. && cfg.dust_beta.iter().any(|b| *b != 0.) {
        return Err("dust tilt requires nonzero dust fraction".into());
    }
    let f_nu = opts.neutrino_fraction;
    if !(0.0..1.0).contains(&f_nu) {
        return Err("neutrino fraction must lie in [0, 1)".into());
    }
    if f_nu > 0. && !cfg.active {
        return Err("collisionless neutrinos require active geometry (the tracer background is photon-only)".into());
    }
    if let Some(rec) = &opts.recombination {
        if ionization.is_none() {
            return Err("matched recombination corrects an ionization table: supply one".into());
        }
        if cfg.omega_lambda >= 1.0 {
            return Err(
                "matched recombination uses a flat FLRW reference, requiring omega_lambda < 1.0"
                    .into(),
            );
        }
        rec.validate()?;
    }
    // Material coverage must match the full evolution even for an optically empty segment.
    if let Some(ion) = ionization {
        ion.cells(0., cfg.duration, 1., 1.)?;
    } else {
        mat.cells(0., cfg.duration)?;
    }
    let dt = cfg.duration / (cfg.steps as f64);
    let profile = match (lie, cfg.active) {
        (Some(ic), true) => vec![initial_lie_node(ic)?],
        (Some(ic), false) => {
            radiation_history_from_lie(ic, cfg.duration, cfg.steps, cfg.nmu, cfg.nphi)?
        }
        (None, true) => radiation_history(cfg.family, cfg.shear, dt, 1, cfg.nmu, cfg.nphi)?,
        (None, false) => radiation_history(
            cfg.family,
            cfg.shear,
            cfg.duration,
            cfg.steps,
            cfg.nmu,
            cfg.nphi,
        )?,
    };
    let mut node = profile.first().ok_or("empty native geometry")?.clone();
    // Gauss fixes Omega_matter + Omega_Lambda; Lambda carries no flux or stress.
    node.omega_lambda = cfg.omega_lambda;
    let mut sky = Field::isotropic(&opts.route, cfg.nmu, cfg.nphi, true)?;
    let initial = sky.moments()?;
    let mut nu = if f_nu > 0. {
        Some(Field::isotropic(&opts.route, cfg.nmu, cfg.nphi, false)?)
    } else {
        None
    };
    let nu_initial = field_moments(&nu)?;
    let total0 = node.omega_radiation - node.omega_lambda;
    if !total0.is_finite() || total0 <= 0. {
        return Err(
            "Omega_Lambda leaves no positive matter density on the initial Gauss slice".into(),
        );
    }
    let (scale, nu_scale) = match &nu_initial {
        None => (total0 * (1. - cfg.dust_fraction) / initial.energy, 0.),
        Some(m) => (
            total0 * (1. - cfg.dust_fraction) * (1. - f_nu) / initial.energy,
            total0 * (1. - cfg.dust_fraction) * f_nu / m.energy,
        ),
    };
    let required = required_flux(&node);
    let coflow = lie.is_some() && required.iter().map(|v| v * v).sum::<f64>().sqrt() > 1e-12;
    let (mut dust, initial_dust_mode) = if coflow {
        if !cfg.active || cfg.dust_fraction <= 0. {
            return Err("nonzero initial Codazzi flux with isotropic photons requires active massive matter".into());
        }
        if cfg.dust_beta.iter().any(|v| *v != 0.) {
            return Err("Codazzi determines the coflow velocity on this Lie initial slice".into());
        }
        let beta = std::array::from_fn(|i| {
            (required[i] - (1. - cfg.dust_fraction) * initial.flux[i]) / cfg.dust_fraction
        });
        (
            Some(
                Dust::coflow_species(total0 * cfg.dust_fraction, baryon_fraction, beta)
                    .map_err(|s| format!("Codazzi coflow: {s}"))?,
            ),
            "codazzi_coflow",
        )
    } else if cfg.dust_fraction == 0. {
        (None, "none")
    } else {
        (
            Some(Dust::opposed_species(
                total0 * cfg.dust_fraction,
                baryon_fraction,
                cfg.dust_beta,
            )?),
            "opposed",
        )
    };
    let mut opacity = Opacity {
        material: mat,
        ionization: match ionization {
            Some(ion) => Some((ion, host_proper_mass(&dust)?)),
            None => None,
        },
        delta_xe: 0.,
        strict_species_offset: species_ref.is_some(),
    };
    let mut thermochemistry = Vec::new();
    if let Some(r) = species_ref {
        let first = r.nodes()[0];
        let b = host_beta(&dust)?;
        thermochemistry.push(ThermochemistrySnapshot {
            eta: 0.,
            state: first.state,
            reference: first.state,
            n_h_m3: first.n_h_m3,
            h_s: first.h_s,
            gamma: 1. / (1. - b.iter().map(|x| x * x).sum::<f64>()).sqrt(),
            expansion_ratio: None,
            endpoint_expansion_ratio: None,
            compton_temperature_k: None,
            diagnostics: ThermalDiagnostics::default(),
        });
    }
    let mut src = source(
        &initial,
        scale,
        nu_initial.as_ref().map(|m| (m, nu_scale)),
        &dust,
        &node,
    )?;
    if cfg.active {
        refresh_mixture(&mut node, src.rad + src.nu + src.dust, src.flux)?;
        node.omega_radiation = src.rad;
    }
    let mut history = vec![Snapshot {
        node: node.clone(),
        radiation: initial,
        omega_dust: src.dust,
        proper_depth: 0.,
        collision_energy_defect: 0.,
        host_beta: host_beta(&dust)?,
        neutrino: nu_initial,
        omega_neutrino: src.nu,
        delta_xe: 0.,
    }];
    let mut cumulative = 0.;
    let mut collision_defect = 0.;
    let mut records = Vec::with_capacity(cfg.steps);
    for step in 0..cfg.steps {
        let mut next = if cfg.active {
            let half = advance_mixture_with_options(
                &node,
                &node,
                dt * 0.5,
                src.rad + src.nu + src.dust,
                src.pressure,
                src.flux,
                expansion,
                cfg.lie_update,
            )?;
            let predictor = evolve_cell(
                &sky,
                nu.as_ref(),
                &dust,
                &node,
                &half,
                &opacity,
                scale,
                cfg.recoil,
                cfg.collision,
            )?;
            let predictor_nu = field_moments(&predictor.nu)?;
            let hm = source(
                &predictor.sky.moments()?,
                scale,
                predictor_nu.as_ref().map(|m| (m, nu_scale)),
                &predictor.dust,
                &half,
            )?;
            advance_mixture_with_options(
                &node,
                &half,
                dt,
                hm.rad + hm.nu + hm.dust,
                hm.pressure,
                hm.flux,
                expansion,
                cfg.lie_update,
            )?
        } else {
            profile[step + 1].clone()
        };
        // Set the independent clock by grid index; avoid a drift of a few ulps
        // beyond a material table's final endpoint on long integrations.
        next.eta = (step + 1) as f64 * dt;
        let step = evolve_cell(
            &sky,
            nu.as_ref(),
            &dust,
            &node,
            &next,
            &opacity,
            scale,
            cfg.recoil,
            cfg.collision,
        )?;
        records.push(StepRecord {
            left: node.clone(),
            right: next.clone(),
            first: step.first,
            second: step.second,
        });
        let rad = step.sky.moments()?;
        let nu_moments = field_moments(&step.nu)?;
        cumulative += step.depth;
        collision_defect += step.energy_defect;
        let beta_before = host_beta(&dust)?;
        let proper_before = if species_ref.is_some() {
            Some(host_proper_mass(&dust)?)
        } else {
            None
        };
        dust = step.dust;
        src = source(
            &rad,
            scale,
            nu_moments.as_ref().map(|m| (m, nu_scale)),
            &dust,
            &next,
        )?;
        if cfg.active {
            refresh_mixture(&mut next, src.rad + src.nu + src.dust, src.flux)?;
            next.omega_radiation = src.rad;
        }
        if let (Some(rec), Some((ion, initial_proper))) = (
            opts.recombination.as_ref().filter(|r| r.active(next.eta)),
            opacity.ionization,
        ) {
            let x_ref_next = ion.xe_at(next.eta)?.min(X_MAX);
            opacity.delta_xe = if x_ref_next >= X_MAX {
                // Hydrogen fully ionized in the reference (Saha-locked, x_e,table >= 1
                // with helium electrons): the matched hydrogen response vanishes.
                0.
            } else {
                let x_ref_prev = ion.xe_at(node.eta)?.min(X_MAX);
                let (_, rate_ref, hubble_ref) =
                    rec.reference(ion, next.eta, cfg.omega_lambda, cfg.dust_fraction)?;
                let beta = host_beta(&dust)?;
                let beta_prime = std::array::from_fn(|i| (beta[i] - beta_before[i]) / dt);
                let photons = step.sky.photons()?;
                let msky =
                    material_directional_sky(&photons, &next, beta, beta_prime, rec.t_unit_k)?;
                let rsky = DirectionalSky {
                    weights: &msky.weights,
                    temperature_k: &msky.temperature_k,
                    expansion_factor: &msky.expansion_factor,
                };
                let tm = compton_temperature_k(&rsky)
                    .map_err(|e| format!("matched recombination at eta {}: {e:?}", next.eta))?;
                let n_h = rec.n_h_emit_m3 * host_proper_mass(&dust)? / initial_proper;
                let hubble = rec.h_emit_s * next.hubble_ratio;
                let gamma = 1. / (1. - beta.iter().map(|b| b * b).sum::<f64>()).sqrt();
                let matched = MatchedStep {
                    x_prev: (x_ref_prev + opacity.delta_xe).clamp(0., X_MAX),
                    x_ref_prev,
                    x_ref_next,
                    d_eta: next.eta - node.eta,
                    gamma,
                    hubble_s: hubble,
                    reference_rate_s: rate_ref,
                    reference_hubble_s: hubble_ref,
                };
                let x = implicit_matched_step(&matched, |x| {
                    anisotropic_peebles_rate(&rsky, n_h, hubble, x, Some(tm))
                })
                .map_err(|e| format!("matched recombination at eta {}: {e:?}", next.eta))?;
                x - x_ref_next
            };
        }
        if let Some(r) = species_ref {
            let first = r.nodes()[0];
            let ref_prev = r
                .at(node.eta)
                .map_err(|e| format!("species reference start: {e:?}"))?;
            let ref_next = r
                .at(next.eta)
                .map_err(|e| format!("species reference end: {e:?}"))?;
            let prev = thermochemistry.last().ok_or("missing species state")?.state;
            let h = next.eta - node.eta;
            let beta = host_beta(&dust)?;
            let beta_prime = std::array::from_fn(|i| (beta[i] - beta_before[i]) / h);
            let b2 = beta.iter().map(|x| x * x).sum::<f64>();
            let gamma = 1. / (1. - b2).sqrt();
            let endpoint_ratio = 3.
                + gamma * gamma * beta.iter().zip(beta_prime).map(|(x, y)| x * y).sum::<f64>()
                - 2. * next.a.iter().zip(beta).map(|(a, b)| a * b).sum::<f64>();
            // Exact average of discrete proper-density continuity for this
            // accepted dust step. Endpoint expression is a diagnostic.
            let proper = host_proper_mass(&dust)?;
            let expansion_ratio =
                -(proper / proper_before.ok_or("missing initial host density")?).ln() / h;
            let n_h =
                first.n_h_m3 * proper / opacity.ionization.ok_or("missing species opacity")?.1;
            let hubble = first.h_s * next.hubble_ratio;
            let photons = step.sky.photons()?;
            let msky = material_directional_sky(&photons, &next, beta, beta_prime, first.tr_k)?;
            let ds = DirectionalSky {
                weights: &msky.weights,
                temperature_k: &msky.temperature_k,
                expansion_factor: &msky.expansion_factor,
            };
            let actual =
                ThermalPoint::new(&ds, n_h, hubble, gamma, expansion_ratio, 0., r.helium())
                    .map_err(|e| format!("species source at eta {}: {e:?}", next.eta))?;
            let reference = r
                .point(ref_next)
                .map_err(|e| format!("species reference source: {e:?}"))?;
            let (state, diagnostics) = thermal_step(
                prev,
                ref_prev.state,
                ref_next.state,
                h,
                r.f_he(),
                &actual,
                &reference,
            )
            .map_err(|e| format!("species matched step at eta {}: {e:?}", next.eta))?;
            opacity.delta_xe = state.xe() - ref_next.state.xe();
            thermochemistry.push(ThermochemistrySnapshot {
                eta: next.eta,
                state,
                reference: ref_next.state,
                n_h_m3: n_h,
                h_s: hubble,
                gamma,
                expansion_ratio: Some(expansion_ratio),
                endpoint_expansion_ratio: Some(endpoint_ratio),
                compton_temperature_k: Some(actual.compton_temperature_k()),
                diagnostics,
            });
        }
        sky = step.sky;
        nu = step.nu;
        node = next;
        history.push(Snapshot {
            node: node.clone(),
            radiation: rad,
            omega_dust: src.dust,
            proper_depth: cumulative,
            collision_energy_defect: collision_defect,
            host_beta: host_beta(&dust)?,
            neutrino: nu_moments,
            omega_neutrino: src.nu,
            delta_xe: opacity.delta_xe,
        });
    }
    let neutrinos = nu.as_ref().map(Field::photons).transpose()?;
    Ok(Solution {
        thermochemistry,
        photons: sky.photons()?,
        history,
        initial_dust_mode,
        records,
        neutrinos,
        route: opts.route.clone(),
        photon_scale: scale,
        neutrino_scale: nu_scale,
        final_dust: dust,
    })
}
